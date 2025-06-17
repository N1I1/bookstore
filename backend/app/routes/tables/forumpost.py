from flask import Blueprint, request, jsonify, session
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.models.forumpost import ForumPost
from app.models.comment import Comment
from app.models.book import Book
from app import db

# 创建蓝图
forum_post_bp = Blueprint('forum_post', __name__, url_prefix='/api/forum_posts')


class ForumPostView(MethodView):
    def get(self, post_id):
        """处理 GET 请求，获取帖子信息"""
        # 获取单个帖子
        post = db.session.get(ForumPost, post_id)
        if post and not post.is_deleted:
            return jsonify({
                "post_id": post.post_id,
                "book_id": post.book_id,
                "title": post.title,
                "content": post.content,
                "post_time": post.post_time.isoformat(),
                "browse_count": post.browse_count
            })
        else:
            return jsonify({"error": "Post not found"}), 404

    def post(self):
        """处理 POST 请求，创建新帖子"""
        user_id = session.get('user_id', None)
        if not user_id:
            return jsonify({"error": "User not logged in"}), 401
        
        data = request.json
        title = data.get('title', None)
        book_id = data.get('book_id', None)
        content = data.get('content', None)
        post_time = datetime.now()
        if not title:
            title = "Untitled Post"
        if not content:
            return jsonify({"error": "Content is empty"}), 400
        
        try:
            if book_id is not None:
                # 检查 book_id 是否存在
                book = db.session.get(Book, book_id)
                if not book:
                    return jsonify({"error": "Book not found"}), 404
            new_post = ForumPost(
                user_id=user_id,
                book_id=book_id,
                title=title,
                content=content,
                post_time=post_time
            )
            db.session.add(new_post)
            db.session.commit()
            return jsonify({
                "Message": "Post created successfully",
                "post_id": new_post.post_id,
            }), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Invalid user_id or book_id"}), 400

    def put(self, post_id):
        """处理 PUT 请求，更新帖子信息"""
        user_id = session.get('user_id', None)
        if not user_id:
            return jsonify({"error": "User not logged in"}), 401
        post = db.session.get(ForumPost, post_id)
        if not post:
            return jsonify({"error": "Post not found"}), 404
        if  post.user_id != user_id:
            return jsonify({"error": "You can only edit your own posts"}), 403

        data = request.json
        new_title = data.get('title', None)
        new_content = data.get('content', None)
        new_book_id = data.get('book_id', None)
        if not new_title:
            return jsonify({"error": "Title is empty"}), 400
        if not new_content:
            return jsonify({"error": "Content is empty"}), 400
        if new_book_id:
            newbook = db.session.get(Book, new_book_id)
            if not newbook:
                return jsonify({"error": "Book not found"}), 404
        try:
            post.title = new_title
            post.book_id = new_book_id
            post.content = new_content
            db.session.commit()
            return jsonify({
                "message": "Post updated successfully",
            }), 200
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Invalid user_id or book_id"}), 400

    def delete(self, post_id):
        """处理 DELETE 请求，删除帖子"""
        user_id = session.get('user_id', None)
        if not user_id:
            return jsonify({"error": "User not logged in"}), 401
        post = db.session.get(ForumPost, post_id)
        if not post:
            return jsonify({"error": "Post not found"}), 404
        if post.user_id != user_id:
            return jsonify({"error": "You can only delete your own posts"}), 403
        
        # 将帖子标记为已删除而不是直接删除
        post.is_deleted = True
        db.session.commit()
        return '', 204

# 随机获取几个帖子
# 后期可添加分页参数
@forum_post_bp.route('/get_posts', methods=['GET'])
def get_random_posts():
    limit = request.args.get('limit', 5, type=int)
    """获取随机帖子"""
    posts = ForumPost.query.filter_by(is_deleted=False).order_by(db.func.random()).limit(limit).all()
    if not posts:
        return jsonify({"error": "No posts found"}), 404
    return jsonify([{
        "post_id": post.post_id,
        "book_id": post.book_id,
        "title": post.title,
        "content": post.content,
        "post_time": post.post_time.isoformat(),
        "browse_count": post.browse_count
    } for post in posts]),  200

# 将 ForumPostView 注册到蓝图
forum_post_api = ForumPostView.as_view('forum_post_api')
forum_post_bp.add_url_rule('/', view_func=forum_post_api, methods=['POST'])
forum_post_bp.add_url_rule('/<int:post_id>', view_func=forum_post_api, methods=['GET', 'PUT', 'DELETE'])


@forum_post_bp.route('/by_book/<int:book_id>', methods=['GET'])
def get_posts_by_book(book_id):
    posts = ForumPost.query.filter_by(book_id=book_id, is_deleted=False).all()
    return jsonify([{
        'post_id': post.post_id,
        'title': post.title,
        'content': post.content,
        'post_time': post.post_time.isoformat(),
        'browse_count': post.browse_count,
        'user_id': post.user_id
    } for post in posts])
