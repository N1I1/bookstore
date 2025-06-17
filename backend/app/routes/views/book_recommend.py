from flask import Blueprint, request, jsonify
from flask.views import MethodView

from app.models import Book, BookTag, UserBrowse, UserCart, UserFavorite
from app import db
from collections import Counter

# 定义蓝图
book_recommend_bp = Blueprint('recommend_books', __name__, url_prefix='/api/recommend_books')

class BookRecommendView(MethodView):
    def post(self):
        # 获取请求参数
        data = request.json
        user_id = data.get('user_id')

        # 验证输入
        if not user_id:
            return jsonify({"error": "Missing user ID"}), 400

        try:
            # Step 1: 获取用户最近浏览、购物车、收藏的书籍
            recent_browses = UserBrowse.query.filter_by(user_id=user_id).order_by(UserBrowse.browse_time.desc()).limit(5).all()
            recent_carts = UserCart.query.filter_by(user_id=user_id).order_by(UserCart.add_time.desc()).limit(5).all()
            recent_favorites = UserFavorite.query.filter_by(user_id=user_id).order_by(UserFavorite.favorite_time.desc()).limit(5).all()

            # 提取书籍 ID
            book_ids = [browse.book_id for browse in recent_browses] + \
                       [cart.book_id for cart in recent_carts] + \
                       [favorite.book_id for favorite in recent_favorites]

            # Step 2: 统计作者出现次数
            authors = [db.session.get(Book, book_id).author for book_id in book_ids]
            most_common_author = Counter(authors).most_common(1)[0][0] if authors else None

            # Step 3: 统计标签出现次数
            tags = []
            for book_id in book_ids:
                tags.extend([tag.tag for tag in BookTag.query.filter_by(book_id=book_id).all()])
            most_common_tags = [tag for tag, _ in Counter(tags).most_common(3)] if tags else []

            # Step 4: 推荐书籍
            recommendations = []

            # 推荐相同作者的书籍
            if most_common_author:
                author_book = Book.query.filter(
                    Book.author == most_common_author,
                    Book.book_id.notin_(book_ids)
                ).first()
                if author_book:
                    recommendations.append({
                        'book_id': author_book.book_id,
                        'recommend_type': '作者推荐',
                        'recommend_reason': f'作者：{most_common_author}'
                    })

            # 推荐标签相关的书籍
            for tag in most_common_tags:
                tag_book = Book.query.join(BookTag, Book.book_id == BookTag.book_id).filter(
                    BookTag.tag == tag,
                    Book.book_id.notin_(book_ids)
                ).first()
                if tag_book:
                    recommendations.append({
                        'book_id': tag_book.book_id,
                        'recommend_type': '标签推荐',
                        'recommend_reason': f'标签：{tag}'
                    })

            # 返回结果
            if recommendations:
                return jsonify({"message": "Books recommended", "recommendations": recommendations}), 200
            else:
                return jsonify({"message": "No recommendations found"}), 404

        except Exception as e:
            return jsonify({"error": str(e)}), 500

# 注册视图
book_recommend_bp.add_url_rule('/', view_func=BookRecommendView.as_view('recommend_books'))
