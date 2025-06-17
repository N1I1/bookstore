from flask import Blueprint, request, jsonify, session
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.models.userfavorite import UserFavorite
from app.models.book import Book
from app import db

# 创建蓝图
user_favorite_bp = Blueprint('user_favorite', __name__, url_prefix='/api/user_favorites')

class UserFavoriteView(MethodView):
    def get(self):
        """处理 GET 请求，获取当前用户所有收藏记录"""
        session_user_id = session.get('user_id')
        if not session_user_id:
            return jsonify({"error": "User not logged in"}), 401

        favorites = UserFavorite.query.filter_by(user_id=session_user_id).all()
        result = []
        for favorite in favorites:
            book = db.session.get(Book, favorite.book_id)
            result.append({
                "book_id": favorite.book_id,
                "book_title": book.title if book else None,
                "favorite_time": favorite.favorite_time.isoformat()
            })
        return jsonify(result), 200

    def post(self):
        """处理 POST 请求，创建新的收藏记录"""
        user_id = session.get('user_id', None)
        if not user_id:
            return jsonify({"error": "User not logged in"}), 401
        data = request.json
        book_id = data.get('book_id', None)
        if not book_id:
            return jsonify({"error": "Missing required field: book_id"}), 400
        
        # 检查书是否存在
        book = db.session.get(Book, book_id)
        if not book:
            return jsonify({"error": "Book not found"}), 404
        # 检查是否已收藏
        existing_favorite = UserFavorite.query.filter_by(user_id=user_id, book_id=book_id).first()
        if existing_favorite:
            return jsonify({"error": "Book already favorited"}), 400
        try:
            new_favorite = UserFavorite(
                user_id=user_id,
                book_id=book_id,
                favorite_time=datetime.now()
            )
            db.session.add(new_favorite)
            db.session.commit()
            return jsonify({
                "book_id": new_favorite.book_id,
                "book_title": book.title,
                "favorite_time": new_favorite.favorite_time.isoformat()
            }), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Duplicate favorite entry"}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Server error"}), 500

    def delete(self, book_id):
        """处理 DELETE 请求，取消收藏"""
        user_id = session.get('user_id', None)
        if not user_id:
            return jsonify({"error": "User not logged in"}), 401
        # 检查收藏记录是否存在
        favorite = UserFavorite.query.filter_by(user_id=user_id, book_id=book_id).first()
        if favorite:
            db.session.delete(favorite)
            db.session.commit()
            return "", 204
        else:
            return jsonify({"error": "Favorite record not found"}), 404

# 将 UserFavoriteView 注册到蓝图
user_favorite_api = UserFavoriteView.as_view('user_favorite_api')
user_favorite_bp.add_url_rule('/', view_func=user_favorite_api, methods=['GET', 'POST'])
user_favorite_bp.add_url_rule('/<int:book_id>', view_func=user_favorite_api, methods=['DELETE'])
