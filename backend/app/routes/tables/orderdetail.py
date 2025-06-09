from flask import Blueprint, request, jsonify
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from app.models.orderdetail import OrderDetail
from app import db

# 创建蓝图
order_detail_bp = Blueprint('order_detail', __name__, url_prefix='/api/order_details')


class OrderDetailView(MethodView):
    def get(self, detail_id=None):
        """处理 GET 请求，获取订单明细信息"""
        if detail_id is None:
            # 获取所有订单明细
            details = OrderDetail.query.all()
            return jsonify([{
                "detail_id": detail.detail_id,
                "order_id": detail.order_id,
                "book_id": detail.book_id,
                "quantity": detail.quantity,
                "unit_price": str(detail.unit_price)
            } for detail in details])
        else:
            # 获取单个订单明细
            detail = OrderDetail.query.get(detail_id)
            if detail:
                return jsonify({
                    "detail_id": detail.detail_id,
                    "order_id": detail.order_id,
                    "book_id": detail.book_id,
                    "quantity": detail.quantity,
                    "unit_price": str(detail.unit_price)
                })
            else:
                return jsonify({"error": "Order detail not found"}), 404

    def post(self):
        """处理 POST 请求，创建新订单明细"""
        data = request.json
        try:
            new_detail = OrderDetail(
                order_id=data['order_id'],
                book_id=data['book_id'],
                quantity=data['quantity'],
                unit_price=data['unit_price']
            )
            db.session.add(new_detail)
            db.session.commit()
            return jsonify({
                "detail_id": new_detail.detail_id,
                "order_id": new_detail.order_id,
                "book_id": new_detail.book_id,
                "quantity": new_detail.quantity,
                "unit_price": str(new_detail.unit_price)
            }), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Invalid order_id or book_id"}), 400
        except KeyError as e:
            return jsonify({"error": f"Missing required field: {e.args[0]}"}), 400

    def put(self, detail_id):
        """处理 PUT 请求，更新订单明细信息"""
        detail = OrderDetail.query.get(detail_id)
        if not detail:
            return jsonify({"error": "Order detail not found"}), 404

        data = request.json
        try:
            detail.order_id = data.get('order_id', detail.order_id)
            detail.book_id = data.get('book_id', detail.book_id)
            detail.quantity = data.get('quantity', detail.quantity)
            detail.unit_price = data.get('unit_price', detail.unit_price)
            db.session.commit()
            return jsonify({
                "detail_id": detail.detail_id,
                "order_id": detail.order_id,
                "book_id": detail.book_id,
                "quantity": detail.quantity,
                "unit_price": str(detail.unit_price)
            })
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Invalid order_id or book_id"}), 400

    def delete(self, detail_id):
        """处理 DELETE 请求，删除订单明细"""
        detail = OrderDetail.query.get(detail_id)
        if detail:
            db.session.delete(detail)
            db.session.commit()
            return jsonify({"message": "Order detail deleted"}), 204
        else:
            return jsonify({"error": "Order detail not found"}), 404


# 将 OrderDetailView 注册到蓝图
order_detail_api = OrderDetailView.as_view('order_detail_api')
order_detail_bp.add_url_rule('/', view_func=order_detail_api, methods=['GET', 'POST'], defaults={'detail_id': None})
order_detail_bp.add_url_rule('/<int:detail_id>', view_func=order_detail_api, methods=['GET', 'PUT', 'DELETE'])