from flask import Blueprint, request, jsonify, session
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from app.models.orderdetail import OrderDetail
from app import db

order_detail_bp = Blueprint('order_detail', __name__, url_prefix='/api/order_details')

class OrderDetailView(MethodView):
    def get(self, detail_id):
        """仅允许通过明细ID获取单条明细，并校验权限"""
        detail = db.session.get(OrderDetail, detail_id)
        if not detail:
            return jsonify({"error": "Order detail not found"}), 404

        # 权限校验
        user_id = session.get('user_id')
        admin_id = session.get('admin_id')
        if user_id:
            if detail.order.user_id != user_id:
                return jsonify({"error": "Forbidden"}), 403
        elif admin_id:
            if detail.order.admin_id != admin_id:
                return jsonify({"error": "Forbidden"}), 403
        else:
            return jsonify({"error": "Unauthorized"}), 401

        return jsonify({
            "detail_id": detail.detail_id,
            "order_id": detail.order_id,
            "book_id": detail.book_id,
            "quantity": detail.quantity,
            "unit_price": float(detail.unit_price),
            "book_title": detail.book.title if detail.book else None
        })


# 注册路由
order_detail_api = OrderDetailView.as_view('order_detail_api')
order_detail_bp.add_url_rule('/<int:detail_id>', view_func=order_detail_api, methods=['GET'])
