from datetime import datetime

from flask import Blueprint, request, jsonify, session
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from app.models.comment import Comment
from app import db

# 创建蓝图
comment_bp = Blueprint('comment', __name__, url_prefix='/api/comments')


class CommentView(MethodView):
    def get(self, comment_id):
        """处理 GET 请求，获取评论信息"""
        # 获取单个评论
        comment = db.session.get(Comment, comment_id)
        if comment and not comment.is_deleted:
            return jsonify({
                "comment_id": comment.comment_id,
                # "post_id": comment.post_id,
                "username": comment.user.username if comment.user else "Unknown",
                "content": comment.content,
                "comment_time": comment.comment_time.isoformat(),
                # "parent_comment_id": comment.parent_comment_id
            })
        else:
            return jsonify({"error": "Comment not found"}), 404

    def post(self):
        """处理 POST 请求，创建新评论"""
        data = request.json
        post_id = data.get('post_id', None)
        content = data.get('content', None)
        parent_comment_id = data.get('parent_comment_id', None)
        user_id = session.get('user_id')
        if not post_id or not content or not user_id:
            return jsonify({"error": "Missing required fields"}), 400
        try:
            new_comment = Comment(
                post_id=post_id,
                user_id=user_id,
                content=content,
                parent_comment_id=parent_comment_id
            )
            db.session.add(new_comment)
            db.session.commit()
            return jsonify({
                "message": "Comment created successfully",
            }), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Invalid post_id or user_id"}), 400

    def put(self, comment_id):
        """处理 PUT 请求，更新评论信息"""
        comment = db.session.get(Comment, comment_id)
        if not comment:
            return jsonify({"error": "Comment not found"}), 404
        if comment.user_id != session.get('user_id'):
            return jsonify({"error": "Unauthorized"}), 403

        data = request.json
        try:
            comment.content = data.get('content', comment.content)
            comment.parent_comment_id = data.get('parent_comment_id', comment.parent_comment_id)
            db.session.commit()
            return jsonify({
                "message": "Comment updated successfully",
            })
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Invalid post_id or user_id"}), 400

    def delete(self, comment_id):
        """处理 DELETE 请求，删除评论"""
        comment = db.session.get(Comment, comment_id)
        if not comment:
            return jsonify({"error": "Comment not found"}), 404
        if comment.user_id != session.get('user_id'):
            return jsonify({"error": "Unauthorized"}), 403
        if comment:
            # 修改状态为已删除
            # 不会级联删除子评论
            comment.is_deleted = True
            db.session.commit()
            return jsonify({"message": "Comment deleted"}), 204

def get_comments_tree(post_id):
    parent_comments = db.session.query(Comment).filter_by(post_id=post_id, parent_comment_id=None).all()
    if not parent_comments:
        return []

    def serialize(comment):
        return {
            "comment_id": comment.comment_id,
            "username": comment.user.username,
            "content": comment.content if not comment.is_deleted else "",
            "comment_time": comment.comment_time.isoformat(),
            "replies": [serialize(child) for child in comment.replies]
        }

    return [serialize(c) for c in parent_comments]

# 用法
@comment_bp.route('/tree/<int:post_id>')
def get_comment_tree(post_id):
    return jsonify(get_comments_tree(post_id))

# 将 CommentView 注册到蓝图
comment_api = CommentView.as_view('comment_api')
comment_bp.add_url_rule('/', view_func=comment_api, methods=['POST'])
comment_bp.add_url_rule('/<int:comment_id>', view_func=comment_api, methods=['GET', 'PUT', 'DELETE'])
