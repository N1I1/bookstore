from flask import Blueprint, request, jsonify, session
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.models.usercart import UserCart
from app.models.book import Book
from app import db

# 创建蓝图
user_cart_bp = Blueprint('user_cart', __name__, url_prefix='/api/user_cart')


class UserCartView(MethodView):
    def get(self):
        """获取当前用户的购物车列表"""
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "Not logged in"}), 401
        cart_items = UserCart.query.filter_by(user_id=user_id).all()
        result = []
        for item in cart_items:
            result.append({
                "cart_id": item.cart_id,
                "book_id": item.book_id,
                "book_title": item.book.title if item.book else None,
                "book_price": item.book.price if item.book else None,
                "book_image": item.book.image_url if item.book else None,
                "quantity": item.quantity,
                "add_time": item.add_time.isoformat()
            })
        return jsonify(result), 200

    def post(self):
        """添加图书到购物车（已存在则数量累加）"""
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "Not logged in"}), 401
        data = request.json
        book_id = data.get('book_id')
        quantity = data.get('quantity', 1)
        if not book_id or quantity < 1:
            return jsonify({"error": "Invalid book_id or quantity"}), 400
        # 检查书是否存在
        book = db.session.get(Book, book_id)
        if not book:
            return jsonify({"error": "Book not found"}), 404
        # 查找是否已存在
        cart_item = UserCart.query.filter_by(user_id=user_id, book_id=book_id).first()
        if cart_item:
            return  jsonify({"error": "Book already in cart"}), 400
        else:
            cart_item = UserCart(user_id=user_id, book_id=book_id, quantity=quantity)
            db.session.add(cart_item)
        db.session.commit()
        return jsonify({"message": "Added to cart", "cart_id": cart_item.cart_id}), 201

    def put(self):
        """更新购物车中某项的数量"""
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "Not logged in"}), 401
        data = request.json
        cart_id = data.get('cart_id')
        quantity = data.get('quantity')
        if not cart_id or quantity is None or quantity < 1:
            return jsonify({"error": "Invalid cart_id or quantity"}), 400
        cart_item = UserCart.query.filter_by(cart_id=cart_id, user_id=user_id).first()
        if not cart_item:
            return jsonify({"error": "Cart item not found"}), 404
        cart_item.quantity = quantity
        cart_item.add_time = datetime.now()
        db.session.commit()
        return jsonify({"message": "Cart updated"}), 200

    def delete(self):
        """删除购物车中的某项"""
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "Not logged in"}), 401
        data = request.json
        cart_id = data.get('cart_id')
        if not cart_id:
            return jsonify({"error": "Invalid cart_id"}), 400
        cart_item = UserCart.query.filter_by(cart_id=cart_id, user_id=user_id).first()
        if not cart_item:
            return jsonify({"error": "Cart item not found"}), 404
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({"message": "Cart item deleted"}), 204

# 将 UserCartView 注册到蓝图
user_cart_api = UserCartView.as_view('user_cart_api')
user_cart_bp.add_url_rule('/', view_func=user_cart_api, methods=['GET', 'POST', 'PUT', 'DELETE'])
