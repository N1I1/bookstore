from flask import Blueprint, request, jsonify
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from backend.app.models.tables.usercart import UserCart
from app import db

# 创建蓝图
user_cart_bp = Blueprint('user_cart', __name__, url_prefix='/api/user_cart')


class UserCartView(MethodView):
    def get(self, cart_id=None):
        """处理 GET 请求，获取购物车信息"""
        if cart_id is None:
            # 获取所有购物车记录
            carts = UserCart.query.all()
            return jsonify([{
                "cart_id": cart.cart_id,
                "user_id": cart.user_id,
                "book_id": cart.book_id,
                "quantity": cart.quantity,
                "add_time": cart.add_time.isoformat()
            } for cart in carts])
        else:
            # 获取单个购物车记录
            cart = UserCart.query.get(cart_id)
            if cart:
                return jsonify({
                    "cart_id": cart.cart_id,
                    "user_id": cart.user_id,
                    "book_id": cart.book_id,
                    "quantity": cart.quantity,
                    "add_time": cart.add_time.isoformat()
                })
            else:
                return jsonify({"error": "Cart record not found"}), 404

    def post(self):
        """处理 POST 请求，创建新的购物车记录"""
        data = request.json
        try:
            new_cart = UserCart(
                user_id=data['user_id'],
                book_id=data['book_id'],
                quantity=data['quantity']
            )
            db.session.add(new_cart)
            db.session.commit()
            return jsonify({
                "cart_id": new_cart.cart_id,
                "user_id": new_cart.user_id,
                "book_id": new_cart.book_id,
                "quantity": new_cart.quantity,
                "add_time": new_cart.add_time.isoformat()
            }), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Duplicate cart entry"}), 400
        except KeyError as e:
            return jsonify({"error": f"Missing required field: {e.args[0]}"}), 400

    def put(self, cart_id):
        """处理 PUT 请求，更新购物车记录"""
        cart = UserCart.query.get(cart_id)
        if not cart:
            return jsonify({"error": "Cart record not found"}), 404

        data = request.json
        try:
            cart.quantity = data.get('quantity', cart.quantity)
            db.session.commit()
            return jsonify({
                "cart_id": cart.cart_id,
                "user_id": cart.user_id,
                "book_id": cart.book_id,
                "quantity": cart.quantity,
                "add_time": cart.add_time.isoformat()
            })
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Duplicate cart entry"}), 400

    def delete(self, cart_id):
        """处理 DELETE 请求，删除购物车记录"""
        cart = UserCart.query.get(cart_id)
        if cart:
            db.session.delete(cart)
            db.session.commit()
            return jsonify({"message": "Cart record deleted"}), 204
        else:
            return jsonify({"error": "Cart record not found"}), 404


# 将 UserCartView 注册到蓝图
user_cart_api = UserCartView.as_view('user_cart_api')
user_cart_bp.add_url_rule('/', view_func=user_cart_api, methods=['GET', 'POST'], defaults={'cart_id': None})
user_cart_bp.add_url_rule('/<int:cart_id>', view_func=user_cart_api, methods=['GET', 'PUT', 'DELETE'])