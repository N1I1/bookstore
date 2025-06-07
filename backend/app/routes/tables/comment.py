from flask import Blueprint, request, jsonify
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from backend.app.models.tables.comment import Comment
from app import db

# 创建蓝图
comment_bp = Blueprint('comment', __name__, url_prefix='/api/comments')


class CommentView(MethodView):
    def get(self, comment_id=None):
        """处理 GET 请求，获取评论信息"""
        if comment_id is None:
            # 获取所有评论
            comments = Comment.query.all()
            return jsonify([{
                "comment_id": comment.comment_id,
                "post_id": comment.post_id,
                "user_id": comment.user_id,
                "content": comment.content,
                "comment_time": comment.comment_time.isoformat(),
                "parent_comment_id": comment.parent_comment_id
            } for comment in comments])
        else:
            # 获取单个评论
            comment = Comment.query.get(comment_id)
            if comment:
                return jsonify({
                    "comment_id": comment.comment_id,
                    "post_id": comment.post_id,
                    "user_id": comment.user_id,
                    "content": comment.content,
                    "comment_time": comment.comment_time.isoformat(),
                    "parent_comment_id": comment.parent_comment_id
                })
            else:
                return jsonify({"error": "Comment not found"}), 404

    def post(self):
        """处理 POST 请求，创建新评论"""
        data = request.json
        try:
            new_comment = Comment(
                post_id=data['post_id'],
                user_id=data['user_id'],
                content=data.get('content'),
                parent_comment_id=data.get('parent_comment_id')
            )
            db.session.add(new_comment)
            db.session.commit()
            return jsonify({
                "comment_id": new_comment.comment_id,
                "post_id": new_comment.post_id,
                "user_id": new_comment.user_id,
                "content": new_comment.content,
                "comment_time": new_comment.comment_time.isoformat(),
                "parent_comment_id": new_comment.parent_comment_id
            }), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Invalid post_id or user_id"}), 400
        except KeyError as e:
            return jsonify({"error": f"Missing required field: {e.args[0]}"}), 400

    def put(self, comment_id):
        """处理 PUT 请求，更新评论信息"""
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({"error": "Comment not found"}), 404

        data = request.json
        try:
            comment.content = data.get('content', comment.content)
            comment.parent_comment_id = data.get('parent_comment_id', comment.parent_comment_id)
            db.session.commit()
            return jsonify({
                "comment_id": comment.comment_id,
                "post_id": comment.post_id,
                "user_id": comment.user_id,
                "content": comment.content,
                "comment_time": comment.comment_time.isoformat(),
                "parent_comment_id": comment.parent_comment_id
            })
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Invalid post_id or user_id"}), 400

    def delete(self, comment_id):
        """处理 DELETE 请求，删除评论"""
        comment = Comment.query.get(comment_id)
        if comment:
            db.session.delete(comment)
            db.session.commit()
            return jsonify({"message": "Comment deleted"}), 204
        else:
            return jsonify({"error": "Comment not found"}), 404


# 将 CommentView 注册到蓝图
comment_api = CommentView.as_view('comment_api')
comment_bp.add_url_rule('/', view_func=comment_api, methods=['GET', 'POST'], defaults={'comment_id': None})
comment_bp.add_url_rule('/<int:comment_id>', view_func=comment_api, methods=['GET', 'PUT', 'DELETE'])