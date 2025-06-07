from flask import Blueprint, request, jsonify
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from backend.app.models.tables.postlike import PostLike
from app import db

# 创建蓝图
post_like_bp = Blueprint('post_like', __name__, url_prefix='/api/post_likes')


class PostLikeView(MethodView):
    def get(self, like_id=None):
        """处理 GET 请求，获取点赞信息"""
        if like_id is None:
            # 获取所有点赞记录
            likes = PostLike.query.all()
            return jsonify([{
                "like_id": like.like_id,
                "post_id": like.post_id,
                "user_id": like.user_id
            } for like in likes])
        else:
            # 获取单个点赞记录
            like = PostLike.query.get(like_id)
            if like:
                return jsonify({
                    "like_id": like.like_id,
                    "post_id": like.post_id,
                    "user_id": like.user_id
                })
            else:
                return jsonify({"error": "Like not found"}), 404

    def post(self):
        """处理 POST 请求，创建新的点赞记录"""
        data = request.json
        try:
            new_like = PostLike(
                post_id=data['post_id'],
                user_id=data['user_id']
            )
            db.session.add(new_like)
            db.session.commit()
            return jsonify({
                "like_id": new_like.like_id,
                "post_id": new_like.post_id,
                "user_id": new_like.user_id
            }), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Duplicate like entry"}), 400
        except KeyError as e:
            return jsonify({"error": f"Missing required field: {e.args[0]}"}), 400

    def delete(self, like_id):
        """处理 DELETE 请求，删除点赞记录"""
        like = PostLike.query.get(like_id)
        if like:
            db.session.delete(like)
            db.session.commit()
            return jsonify({"message": "Like deleted"}), 204
        else:
            return jsonify({"error": "Like not found"}), 404

    def put(self, like_id):
        """处理 PUT 请求，更新点赞记录（例如：取消点赞）"""
        like = PostLike.query.get(like_id)
        if not like:
            return jsonify({"error": "Like not found"}), 404

        data = request.json
        try:
            like.post_id = data.get('post_id', like.post_id)
            like.user_id = data.get('user_id', like.user_id)
            db.session.commit()
            return jsonify({
                "like_id": like.like_id,
                "post_id": like.post_id,
                "user_id": like.user_id
            })
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Duplicate like entry"}), 400


# 将 PostLikeView 注册到蓝图
post_like_api = PostLikeView.as_view('post_like_api')
post_like_bp.add_url_rule('/', view_func=post_like_api, methods=['GET', 'POST'], defaults={'like_id': None})
post_like_bp.add_url_rule('/<int:like_id>', view_func=post_like_api, methods=['GET', 'PUT', 'DELETE'])