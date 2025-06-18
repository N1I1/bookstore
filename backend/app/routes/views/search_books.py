from flask import Blueprint, request, jsonify
from flask.views import MethodView

from app.models import Book
from app import db

# 定义蓝图
book_search_bp = Blueprint('search_books', __name__, url_prefix='/api/search_books')

class BookSearchView(MethodView):
    def post(self):
        # 获取请求数据
        data = request.json
        search_query = data.get('query')  # 查询字符串

        # 验证输入
        if not search_query:
            return jsonify({"error": "Missing search query"}), 400

        try:
            # 查询相关的图书
            books = Book.query.filter(
                (Book.title.ilike(f"%{search_query}%")) |
                (Book.author.ilike(f"%{search_query}%")) |
                (Book.isbn.ilike(f"%{search_query}%")) |
                (Book.publisher.ilike(f"%{search_query}%"))
            ).all()

            # 提取图书的详细信息
            book_info = [
                {
                    "book_id": book.book_id,
                    "title": book.title,
                    "author": book.author,
                    "isbn": book.isbn,
                    "publisher": book.publisher,
                    "price": str(book.price),  # 将 Numeric 转换为字符串
                    "discount": str(book.discount),  #  Numeric 转换为字符串
                    "stock": book.stock,
                    "description": book.description,
                    "image_url": book.image_url
                } for book in books
            ]

            # 返回结果
            if book_info:
                return jsonify({"message": "Books found", "books": book_info}), 200
            else:
                return jsonify({"message": "No books found"}), 404

        except Exception as e:
            return jsonify({"error": str(e)}), 500

# 注册视图
book_search_bp.add_url_rule('/', view_func=BookSearchView.as_view('search_books'))

