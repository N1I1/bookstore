from flask import Blueprint, request, jsonify
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.models.userfavorite import UserFavorite
from app import db

# 创建蓝图
user_favorite_bp = Blueprint('user_favorite', __name__, url_prefix='/api/user_favorites')


class UserFavoriteView(MethodView):
    def get(self, favorite_id=None):
        """处理 GET 请求，获取收藏记录"""
        if favorite_id is None:
            # 获取所有收藏记录
            favorites = UserFavorite.query.all()
            return jsonify([{
                "favorite_id": favorite.favorite_id,
                "user_id": favorite.user_id,
                "book_id": favorite.book_id,
                "favorite_time": favorite.favorite_time.isoformat()
            } for favorite in favorites])
        else:
            # 获取单个收藏记录
            favorite = UserFavorite.query.get(favorite_id)
            if favorite:
                return jsonify({
                    "favorite_id": favorite.favorite_id,
                    "user_id": favorite.user_id,
                    "book_id": favorite.book_id,
                    "favorite_time": favorite.favorite_time.isoformat()
                })
            else:
                return jsonify({"error": "Favorite record not found"}), 404

    def post(self):
        """处理 POST 请求，创建新的收藏记录"""
        data = request.json
        try:
            new_favorite = UserFavorite(
                user_id=data['user_id'],
                book_id=data['book_id']
            )
            db.session.add(new_favorite)
            db.session.commit()
            return jsonify({
                "favorite_id": new_favorite.favorite_id,
                "user_id": new_favorite.user_id,
                "book_id": new_favorite.book_id,
                "favorite_time": new_favorite.favorite_time.isoformat()
            }), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Duplicate favorite entry"}), 400
        except KeyError as e:
            return jsonify({"error": f"Missing required field: {e.args[0]}"}), 400

    def delete(self, favorite_id):
        """处理 DELETE 请求，删除收藏记录"""
        favorite = UserFavorite.query.get(favorite_id)
        if favorite:
            db.session.delete(favorite)
            db.session.commit()
            return jsonify({"message": "Favorite record deleted"}), 204
        else:
            return jsonify({"error": "Favorite record not found"}), 404

    def put(self, favorite_id):
        """处理 PUT 请求，更新收藏记录（例如：取消收藏）"""
        favorite = UserFavorite.query.get(favorite_id)
        if not favorite:
            return jsonify({"error": "Favorite record not found"}), 404

        data = request.json
        try:
            favorite.user_id = data.get('user_id', favorite.user_id)
            favorite.book_id = data.get('book_id', favorite.book_id)
            db.session.commit()
            return jsonify({
                "favorite_id": favorite.favorite_id,
                "user_id": favorite.user_id,
                "book_id": favorite.book_id,
                "favorite_time": favorite.favorite_time.isoformat()
            })
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Duplicate favorite entry"}), 400


# 将 UserFavoriteView 注册到蓝图
user_favorite_api = UserFavoriteView.as_view('user_favorite_api')
user_favorite_bp.add_url_rule('/', view_func=user_favorite_api, methods=['GET', 'POST'], defaults={'favorite_id': None})
user_favorite_bp.add_url_rule('/<int:favorite_id>', view_func=user_favorite_api, methods=['GET', 'PUT', 'DELETE'])