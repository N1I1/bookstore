from flask import Blueprint, request, jsonify
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from app.models.book import Book
from app import db

book_bp = Blueprint('book', __name__, url_prefix='/api/books')


class BookView(MethodView):
    def get(self, book_id=None):
        """处理 GET 请求，获取书籍信息"""
        if book_id is None:
            # 获取所有书籍
            books = Book.query.all()
            print(f"Retrieved {len(books)} books from the database.")
            return jsonify([{
                "book_id": book.book_id,
                "title": book.title,
                "author": book.author,
                "isbn": book.isbn,
                "publisher": book.publisher,
                "price": str(book.price),
                "discount": str(book.discount),
                "stock": book.stock,
                "description": book.description
            } for book in books])
        else:
            # 获取单个书籍
            book = Book.query.get(book_id)
            if book:
                return jsonify({
                    "book_id": book.book_id,
                    "title": book.title,
                    "author": book.author,
                    "isbn": book.isbn,
                    "publisher": book.publisher,
                    "price": str(book.price),
                    "discount": str(book.discount),
                    "stock": book.stock,
                    "description": book.description
                })
            else:
                return jsonify({"error": "Book not found"}), 404

    def post(self):
        """处理 POST 请求，创建新书籍"""
        data = request.json
        try:
            new_book = Book(
                title=data['title'],
                author=data['author'],
                isbn=data['isbn'],
                publisher=data['publisher'],
                price=data['price'],
                discount=data['discount'],
                stock=data['stock'],
                description=data.get('description')
            )
            db.session.add(new_book)
            db.session.commit()
            return jsonify({
                "book_id": new_book.book_id,
                "title": new_book.title,
                "author": new_book.author,
                "isbn": new_book.isbn,
                "publisher": new_book.publisher,
                "price": str(new_book.price),
                "discount": str(new_book.discount),
                "stock": new_book.stock,
                "description": new_book.description
            }), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "ISBN already exists"}), 400
        except KeyError as e:
            return jsonify({"error": f"Missing required field: {e.args[0]}"}), 400

    def put(self, book_id):
        """处理 PUT 请求，更新书籍信息"""
        book = Book.query.get(book_id)
        if not book:
            return jsonify({"error": "Book not found"}), 404

        data = request.json
        try:
            book.title = data.get('title', book.title)
            book.author = data.get('author', book.author)
            book.isbn = data.get('isbn', book.isbn)
            book.publisher = data.get('publisher', book.publisher)
            book.price = data.get('price', book.price)
            book.discount = data.get('discount', book.discount)
            book.stock = data.get('stock', book.stock)
            book.description = data.get('description', book.description)
            db.session.commit()
            return jsonify({
                "book_id": book.book_id,
                "title": book.title,
                "author": book.author,
                "isbn": book.isbn,
                "publisher": book.publisher,
                "price": str(book.price),
                "discount": str(book.discount),
                "stock": book.stock,
                "description": book.description
            })
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "ISBN already exists"}), 400

    def delete(self, book_id):
        """处理 DELETE 请求，删除书籍"""
        book = Book.query.get(book_id)
        if book:
            db.session.delete(book)
            db.session.commit()
            return jsonify({"message": "Book deleted"}), 204
        else:
            return jsonify({"error": "Book not found"}), 404

# 将 BookView 注册到蓝图
book_api = BookView.as_view('book_api')
book_bp.add_url_rule('/', view_func=book_api, methods=['GET', ], defaults={'book_id': None})
book_bp.add_url_rule('/', view_func=book_api, methods=['POST', ])
book_bp.add_url_rule('/<int:book_id>', view_func=book_api, methods=['GET', 'PUT', 'DELETE'])

