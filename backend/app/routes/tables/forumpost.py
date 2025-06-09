from flask import Blueprint, request, jsonify
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.models.forumpost import ForumPost
from app import db

# 创建蓝图
forum_post_bp = Blueprint('forum_post', __name__, url_prefix='/api/forum_posts')


class ForumPostView(MethodView):
    def get(self, post_id=None):
        """处理 GET 请求，获取帖子信息"""
        if post_id is None:
            # 获取所有帖子
            posts = ForumPost.query.all()
            return jsonify([{
                "post_id": post.post_id,
                "user_id": post.user_id,
                "book_id": post.book_id,
                "content": post.content,
                "post_time": post.post_time.isoformat(),
                "browse_count": post.browse_count
            } for post in posts])
        else:
            # 获取单个帖子
            post = ForumPost.query.get(post_id)
            if post:
                return jsonify({
                    "post_id": post.post_id,
                    "user_id": post.user_id,
                    "book_id": post.book_id,
                    "content": post.content,
                    "post_time": post.post_time.isoformat(),
                    "browse_count": post.browse_count
                })
            else:
                return jsonify({"error": "Post not found"}), 404

    def post(self):
        """处理 POST 请求，创建新帖子"""
        data = request.json
        try:
            new_post = ForumPost(
                user_id=data['user_id'],
                book_id=data.get('book_id'),
                content=data.get('content'),
                browse_count=data.get('browse_count', 0)
            )
            db.session.add(new_post)
            db.session.commit()
            return jsonify({
                "post_id": new_post.post_id,
                "user_id": new_post.user_id,
                "book_id": new_post.book_id,
                "content": new_post.content,
                "post_time": new_post.post_time.isoformat(),
                "browse_count": new_post.browse_count
            }), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Invalid user_id or book_id"}), 400
        except KeyError as e:
            return jsonify({"error": f"Missing required field: {e.args[0]}"}), 400

    def put(self, post_id):
        """处理 PUT 请求，更新帖子信息"""
        post = ForumPost.query.get(post_id)
        if not post:
            return jsonify({"error": "Post not found"}), 404

        data = request.json
        try:
            post.user_id = data.get('user_id', post.user_id)
            post.book_id = data.get('book_id', post.book_id)
            post.content = data.get('content', post.content)
            post.browse_count = data.get('browse_count', post.browse_count)
            db.session.commit()
            return jsonify({
                "post_id": post.post_id,
                "user_id": post.user_id,
                "book_id": post.book_id,
                "content": post.content,
                "post_time": post.post_time.isoformat(),
                "browse_count": post.browse_count
            })
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Invalid user_id or book_id"}), 400

    def delete(self, post_id):
        """处理 DELETE 请求，删除帖子"""
        post = ForumPost.query.get(post_id)
        if post:
            db.session.delete(post)
            db.session.commit()
            return jsonify({"message": "Post deleted"}), 204
        else:
            return jsonify({"error": "Post not found"}), 404


# 将 ForumPostView 注册到蓝图
forum_post_api = ForumPostView.as_view('forum_post_api')
forum_post_bp.add_url_rule('/', view_func=forum_post_api, methods=['GET', 'POST'], defaults={'post_id': None})
forum_post_bp.add_url_rule('/<int:post_id>', view_func=forum_post_api, methods=['GET', 'PUT', 'DELETE'])