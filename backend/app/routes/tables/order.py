from flask import Blueprint, request, jsonify
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from backend.app.models.tables.order import Order
from app import db

# 创建蓝图
order_bp = Blueprint('order', __name__, url_prefix='/api/orders')


class OrderView(MethodView):
    def get(self, order_id=None):
        """处理 GET 请求，获取订单信息"""
        if order_id is None:
            # 获取所有订单
            orders = Order.query.all()
            return jsonify([{
                "order_id": order.order_id,
                "user_id": order.user_id,
                "admin_id": order.admin_id,
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
                "remark": order.remark
            } for order in orders])
        else:
            # 获取单个订单
            order = Order.query.get(order_id)
            if order:
                return jsonify({
                    "order_id": order.order_id,
                    "user_id": order.user_id,
                    "admin_id": order.admin_id,
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
                    "remark": order.remark
                })
            else:
                return jsonify({"error": "Order not found"}), 404

    def post(self):
        """处理 POST 请求，创建新订单"""
        data = request.json
        try:
            new_order = Order(
                user_id=data['user_id'],
                admin_id=data['admin_id'],
                order_status=data.get('order_status', '未支付'),
                ship_address=data['ship_address'],
                bill_address=data['bill_address'],
                current_address=data['current_address'],
                shipper_phone=data['shipper_phone'],
                biller_phone=data['biller_phone'],
                remark=data.get('remark')
            )
            db.session.add(new_order)
            db.session.commit()
            return jsonify({
                "order_id": new_order.order_id,
                "user_id": new_order.user_id,
                "admin_id": new_order.admin_id,
                "order_status": new_order.order_status,
                "order_time": new_order.order_time.isoformat(),
                "payment_time": new_order.payment_time.isoformat() if new_order.payment_time else None,
                "ship_time": new_order.ship_time.isoformat() if new_order.ship_time else None,
                "get_time": new_order.get_time.isoformat() if new_order.get_time else None,
                "ship_address": new_order.ship_address,
                "bill_address": new_order.bill_address,
                "current_address": new_order.current_address,
                "shipper_phone": new_order.shipper_phone,
                "biller_phone": new_order.biller_phone,
                "remark": new_order.remark
            }), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Invalid user_id or admin_id"}), 400
        except KeyError as e:
            return jsonify({"error": f"Missing required field: {e.args[0]}"}), 400

    def put(self, order_id):
        """处理 PUT 请求，更新订单信息"""
        order = Order.query.get(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404

        data = request.json
        try:
            order.order_status = data.get('order_status', order.order_status)
            order.ship_address = data.get('ship_address', order.ship_address)
            order.bill_address = data.get('bill_address', order.bill_address)
            order.current_address = data.get('current_address', order.current_address)
            order.shipper_phone = data.get('shipper_phone', order.shipper_phone)
            order.biller_phone = data.get('biller_phone', order.biller_phone)
            order.remark = data.get('remark', order.remark)
            order.payment_time = data.get('payment_time', order.payment_time)
            order.ship_time = data.get('ship_time', order.ship_time)
            order.get_time = data.get('get_time', order.get_time)
            db.session.commit()
            return jsonify({
                "order_id": order.order_id,
                "user_id": order.user_id,
                "admin_id": order.admin_id,
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
                "remark": order.remark
            })
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Invalid user_id or admin_id"}), 400

    def delete(self, order_id):
        """处理 DELETE 请求，删除订单"""
        order = Order.query.get(order_id)
        if order:
            db.session.delete(order)
            db.session.commit()
            return jsonify({"message": "Order deleted"}), 204
        else:
            return jsonify({"error": "Order not found"}), 404


# 将 OrderView 注册到蓝图
order_api = OrderView.as_view('order_api')
order_bp.add_url_rule('/', view_func=order_api, methods=['GET', 'POST'], defaults={'order_id': None})
order_bp.add_url_rule('/<int:order_id>', view_func=order_api, methods=['GET', 'PUT', 'DELETE'])