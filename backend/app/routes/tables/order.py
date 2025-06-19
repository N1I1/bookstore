from flask import Blueprint, request, jsonify, session
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.models.order import Order
from app.models.orderdetail import OrderDetail
from app.models.book import Book
from app.models.admin import Admin
from app import db

order_bp = Blueprint('order', __name__, url_prefix='/api/orders')

class OrderView(MethodView):
    def get(self, order_id=None):
        """获取订单或订单列表"""
        user_id = session.get('user_id')
        admin_id = session.get('admin_id')

        if order_id is None:
            # 查询订单列表
            if not admin_id and not user_id:
                return jsonify({"error": "Unauthorized"}), 401
            elif admin_id and user_id:
                orders = Order.query.filter_by(admin_id=admin_id, user_id=user_id, is_deleted=False).all()
            elif admin_id:
                orders = Order.query.filter_by(admin_id=admin_id).all()
            elif user_id:
                orders = Order.query.filter_by(user_id=user_id, is_deleted=False).all()
            return jsonify([
                {
                    "order_id": o.order_id,
                    "order_status": o.order_status,
                    "order_time": o.order_time.isoformat(),
                    "total_amount": float(o.total_amount),
                } for o in orders
            ])
        else:
            # 查询单个订单
            order = db.session.query(Order).filter_by(order_id=order_id, is_deleted=False).first()
            if not order:
                return jsonify({"error": "Order not found"}), 404
            if user_id and not admin_id:
                if order.user_id != user_id:
                    print("User ID mismatch:", user_id, order.user_id)
                    return jsonify({"error": "Forbidden"}), 403
                    
            if admin_id:
                if order.admin_id and order.admin_id != admin_id:
                    print("Admin ID mismatch:", admin_id, order.admin_id)
                    return jsonify({"error": "Forbidden"}), 403
        
            return jsonify({
                "order_id": order.order_id,
                "order_status": order.order_status,
                "order_time": order.order_time.isoformat(),
                "payment_time": order.payment_time.isoformat() if order.payment_time else None,
                "ship_time": order.ship_time.isoformat() if order.ship_time else None,
                "get_time": order.get_time.isoformat() if order.get_time else None,
                "ship_address": order.ship_address,
                "bill_address": order.bill_address,
                "current_address": order.current_address,
                "shipper_phone": order.shipper_phone,
                "biller_phone": order.biller_phone,
                "remark": order.remark,
                "total_amount": float(order.total_amount),
                "details": [
                    {
                        "detail_id": d.detail_id,
                        "book_id": d.book_id,
                        "book_title": d.book.title if d.book else None,
                        "quantity": d.quantity,
                        "unit_price": float(d.unit_price)
                    } for d in order.order_details
                ]
            })

    def post(self):
        """创建新订单（用户）"""
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401
        data = request.json
        try:
            details = data.get('details')
            if not details or not isinstance(details, list):
                return jsonify({"error": "Order details required"}), 400

            total_amount = 0
            order_details = []
            for item in details:
                book_id = item.get('book_id')
                if not book_id:
                    return jsonify({"error": "book_id is required"}), 400
                book = db.session.get(Book, book_id)
                if not book:
                    return jsonify({"error": f"Book {book_id} not found"}), 400
                quantity = item.get('quantity')
                if not isinstance(quantity, int) or quantity <= 0:
                    return jsonify({"error": "Quantity must be positive"}), 400
                unit_price = float(book.price) * float(book.discount)
                total_amount += unit_price * quantity
                order_details.append({
                    "book_id": book.book_id,
                    "quantity": quantity,
                    "unit_price": unit_price
                })

            bill_address = data.get('bill_address', '')
            biller_phone = data.get('biller_phone', '')
            remark = data.get('remark', '')

            # 创建订单
            order = Order(
                user_id=user_id,
                order_status='未支付',
                order_time=datetime.now(),
                bill_address=bill_address,
                biller_phone=biller_phone,
                remark=remark,
                total_amount=total_amount
            )
            db.session.add(order)
            db.session.flush()  # 获取order_id

            # 创建订单明细
            for d in order_details:
                detail = OrderDetail(
                    order_id=order.order_id,
                    book_id=d['book_id'],
                    quantity=d['quantity'],
                    unit_price=d['unit_price']
                )
                db.session.add(detail)
            db.session.commit()
            return jsonify({"order_id": order.order_id, "total_amount": float(order.total_amount)}), 201

        except KeyError as e:
            return jsonify({"error": f"Missing required field: {e.args[0]}"}), 400
        except Exception as e:
            print(e)
            db.session.rollback()
            return jsonify({"error": "Server error"}), 400

    def put(self, order_id):
        """用户修改订单地址、备注等信息"""
        order = db.session.query(Order).filter_by(order_id=order_id, is_deleted=False).first()
        if not order:
            return jsonify({"error": "Order not found"}), 404

        user_id = session.get('user_id')
        data = request.json

        if user_id:
            if order.user_id != user_id:
                return jsonify({"error": "Forbidden"}), 403
            # 用户只能改地址、备注、电话等信息
            if order.order_status != '未支付':
                return jsonify({"error": "Only unpaid orders can be updated"}), 400
            updated = False
            for field in ['bill_address', 'biller_phone', 'remark']:
                if field in data:
                    setattr(order, field, data[field])
                    updated = True
            if not updated:
                return jsonify({"error": "No updatable field provided"}), 400
            db.session.commit()
            return jsonify({"message": "Order updated successfully"})
        else:
            return jsonify({"error": "Unauthorized"}), 401

    def delete(self, order_id):
        """删除订单（仅用户可删已完成或已取消订单）"""
        order = db.session.query(Order).filter_by(order_id=order_id, is_deleted=False).first()
        if not order:
            return jsonify({"error": "Order not found"}), 404
        user_id = session.get('user_id')
        if not user_id or order.user_id != user_id:
            return jsonify({"error": "Forbidden"}), 403
        if order.order_status not in ['已完成', '订单取消']:
                return jsonify({"error": "Only complete orders can be deleted"}), 400

        order.is_deleted = True  # 软删除
        db.session.commit()
        return '', 204

# 注册路由
order_api = OrderView.as_view('order_api')
order_bp.add_url_rule('/', view_func=order_api, methods=['GET'], defaults={'order_id': None})
order_bp.add_url_rule('/', view_func=order_api, methods=['POST'])
order_bp.add_url_rule('/<int:order_id>', view_func=order_api, methods=['GET', 'PUT', 'DELETE'])


@order_bp.route('/<int:order_id>/pay', methods=['POST'])
def user_pay_order(order_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    order = db.session.query(Order).filter_by(order_id=order_id, is_deleted=False).first()
    if not order:
        return jsonify({"error": "Order not found"}), 404
    if order.user_id != user_id:
        return jsonify({"error": "Forbidden"}), 403
    if order.order_status != '未支付':
        return jsonify({"error": "Order status not allowed for payment"}), 400

    order.order_status = '已支付'
    order.payment_time = datetime.now()
    db.session.commit()
    return jsonify({"message": "Order paid successfully"})

@order_bp.route('/<int:order_id>/cancel', methods=['POST'])
def user_cancel_order(order_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    order = db.session.query(Order).filter_by(order_id=order_id, is_deleted=False).first()
    if not order:
        return jsonify({"error": "Order not found"}), 404
    if order.user_id != user_id:
        return jsonify({"error": "Forbidden"}), 403
    if order.order_status not in ['未支付', '已支付']:
        return jsonify({"error": "Only unpaid or paid-but-unshipped orders can be cancelled"}), 400

    order.order_status = '订单取消'
    db.session.commit()
    return jsonify({"message": "Order cancelled successfully"})

@order_bp.route('/<int:order_id>/confirm', methods=['POST'])
def user_confirm_order(order_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    order = db.session.query(Order).filter_by(order_id=order_id, is_deleted=False).first()
    if not order:
        return jsonify({"error": "Order not found"}), 404
    if order.user_id != user_id:
        return jsonify({"error": "Forbidden"}), 403
    if order.order_status != '已发货':
        return jsonify({"error": "Order status not allowed for confirmation"}), 400

    order.get_time = datetime.now()
    order.order_status = '已完成'
    db.session.commit()
    return jsonify({"message": "Order confirmed successfully"})

@order_bp.route('/<int:order_id>/ship', methods=['POST'])
def admin_ship_order(order_id):
    admin_id = session.get('admin_id')
    if not admin_id:
        return jsonify({"error": "Unauthorized"}), 401
    order = db.session.query(Order).filter_by(order_id=order_id, is_deleted=False).first()
    if not order:
        return jsonify({"error": "Order not found"}), 404
    if order.admin_id != admin_id:
        return jsonify({"error": "Forbidden"}), 403
    if order.order_status != '已支付':
        return jsonify({"error": "Order status not allowed for shipping"}), 400

    data = request.json or {}
    if 'ship_address' in data:
        order.ship_address = data['ship_address']
    if 'current_address' in data:
        order.current_address = data['current_address']
    if 'shipper_phone' in data:
        order.shipper_phone = data['shipper_phone']

    order.ship_time = datetime.now()
    order.order_status = '已发货'
    db.session.commit()
    return jsonify({"message": "Order shipped successfully"})

@order_bp.route('/<int:order_id>/ship_address', methods=['PUT'])
def admin_update_ship_address(order_id):
    admin_id = session.get('admin_id')
    if not admin_id:
        return jsonify({"error": "Unauthorized"}), 401
    order = db.session.query(Order).filter_by(order_id=order_id).first()
    if not order:
        return jsonify({"error": "Order not found"}), 404
    if order.admin_id != admin_id:
        return jsonify({"error": "Forbidden"}), 403

    data = request.json or {}
    # 只允许管理员修改运输相关地址
    updated = False
    for field in ['ship_address', 'current_address']:
        if field in data:
            setattr(order, field, data[field])
            updated = True

    if not updated:
        return jsonify({"error": "No address field provided"}), 400

    db.session.commit()
    return jsonify({"message": "Shipping address updated successfully"})

@order_bp.route('/assign_admin', methods=['POST'])
def assign_admin_to_orders():
    # 查询所有未分配管理员的订单
    admin_id = session.get('admin_id')
    if not admin_id:
        return jsonify({"error": "Unauthorized"}), 401
    unassigned_orders = Order.query.filter_by(admin_id=None, order_status='已支付').all()
    if not unassigned_orders:
        print("没有需要分配的订单")
        return jsonify({"error": "No orders to assign"}), 404

    # 查询所有管理员及其当前订单数
    admins = Admin.query.all()
    if not admins:
        print("没有可用的管理员")
        return jsonify({"error": "No available admins"}), 404

    # 统计每个管理员当前已分配的订单数
    admin_order_counts = {
        admin.admin_id: Order.query.filter_by(admin_id=admin.admin_id).count()
        for admin in admins
    }

    for order in unassigned_orders:
        # 找到订单数最少的管理员
        min_admin_id = min(admin_order_counts, key=admin_order_counts.get)
        order.admin_id = min_admin_id
        admin_order_counts[min_admin_id] += 1  # 该管理员订单数+1

    db.session.commit()
    return jsonify({"message": f"已为{len(unassigned_orders)}个订单分配管理员"}), 200
