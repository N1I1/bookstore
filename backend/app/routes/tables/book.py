from flask import Blueprint, request, jsonify, session
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from app.models.book import Book
from app.models.order import Order
from app import db

book_bp = Blueprint('book', __name__, url_prefix='/api/books')


class BookView(MethodView):
    def get(self, book_id=None):
        """处理 GET 请求，获取单本书籍信息"""
        if not book_id:
            """获取所有书籍"""
            books = Book.query.all()
            return jsonify([{
                "book_id": book.book_id,
                "title": book.title,
                "author": book.author,
                "isbn": book.isbn,
                "publisher": book.publisher,
                "price": float(book.price),
                "discount": float(book.discount),
                "stock": int(book.stock),
                "description": book.description,
                "image_url": book.image_url if book.image_url else None
            } for book in books]), 200
        else:
            # 获取单个书籍
            book = db.session.get(Book, book_id)
            if book:
                return jsonify({
                    "book_id": book.book_id,
                    "title": book.title,
                    "author": book.author,
                    "isbn": book.isbn,
                    "publisher": book.publisher,
                    "price": float(book.price),
                    "discount": float(book.discount),
                    "stock": int(book.stock),
                    "description": book.description,
                    "image_url": book.image_url if  book.image_url else None
                })
            else:
                return jsonify({"error": "Book not found"}), 404

    def post(self):
        """处理 POST 请求，创建新书籍"""
        data = request.json
        admin_id = session.get('admin_id', None)
        if not admin_id:
            return jsonify({"error": "Unauthorized"}), 401
        try:
            new_book = Book(
                title=data['title'],
                author=data['author'],
                isbn=data['isbn'],
                publisher=data['publisher'],
                price=float(data['price']),
                discount=float(data['discount']),
                stock=int(data['stock']),
                description=data.get('description', None),
                image_url=data.get('image_url', None)
            )
            db.session.add(new_book)
            db.session.commit()
            return jsonify({"message": "Book created", "book_id": new_book.book_id}), 201
        except KeyError as e:
            return jsonify({"error": f"Missing required field: {e.args[0]}"}), 400
        except ValueError as e:
            return jsonify({"error": "Invalid data type"}), 400
        except IntegrityError as e:
            db.session.rollback()
            return jsonify({"error": "Book already exists or unique constraint failed"}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Server error"}), 500

    def put(self, book_id):
        """处理 PUT 请求，更新书籍信息"""
        admin_id = session.get('admin_id', None)
        if not admin_id:
            return jsonify({"error": "Unauthorized"}), 401
        book = db.session.get(Book, book_id)
        if not book:
            return jsonify({"error": "Book not found"}), 404
        data = request.json
        try:
            book.title = data.get('title', book.title)
            book.author = data.get('author', book.author)
            book.isbn = data.get('isbn', book.isbn)
            book.publisher = data.get('publisher', book.publisher)
            book.price = float(data.get('price', book.price))
            book.discount = float(data.get('discount', book.discount))
            book.stock = int(data.get('stock', book.stock))
            book.description = data.get('description', book.description)
            db.session.commit()
            return jsonify({
                "book_id": book.book_id,
                "title": book.title,
                "author": book.author,
                "isbn": book.isbn,
                "publisher": book.publisher,
                "price": float(book.price),
                "discount": float(book.discount),
                "stock": book.stock,
                "description": book.description
            }), 200
        except ValueError:
            return jsonify({"error": "Invalid data type"}), 400
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Unique constraint failed"}), 400
        except Exception:
            db.session.rollback()
            return jsonify({"error": "Server error"}), 500

    def delete(self, book_id):
        """处理 DELETE 请求，删除书籍"""
        admin_id = session.get('admin_id', None)
        if not admin_id:
            return jsonify({"error": "Unauthorized"}), 401
            
        book = db.session.get(Book, book_id)
        if not book:
            return jsonify({"error": "Book not found"}), 404
        
        from app.models.orderdetail import OrderDetail
        
        active_orders = db.session.query(Order).join(
            OrderDetail, Order.order_id == OrderDetail.order_id
        ).filter(
            OrderDetail.book_id == book_id,
            Order.order_status.not_in(['已完成', '订单取消']),
            Order.is_deleted == False
        ).all()
        
        if active_orders:
            return jsonify({
                "error": "该书有关联的未完成订单，不能删除",
                "order_ids": [order.order_id for order in active_orders]
            }), 400
        
        try:
            db.session.delete(book)
            db.session.commit()
            return jsonify({"message": "Book deleted"}), 204
        except Exception as e:
            db.session.rollback()
            print(f"删除图书出错: {str(e)}")
            return jsonify({"error": f"删除图书失败: {str(e)}"}), 500

# 将 BookView 注册到蓝图
book_api = BookView.as_view('book_api')
book_bp.add_url_rule('/', view_func=book_api, methods=['GET'], defaults={'book_id': None})
book_bp.add_url_rule('/', view_func=book_api, methods=['POST'])
book_bp.add_url_rule('/<int:book_id>', view_func=book_api, methods=['GET', 'PUT', 'DELETE'])

@book_bp.route('/<int:book_id>/tags', methods=['GET'])
def get_tags_by_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    # 假设 Book 有 tags 关系
    tags = getattr(book, 'tags', None)
    if tags is None:
        return jsonify({"error": "Book-tag relationship not defined"}), 500
    return jsonify([
        {"tag_id": tag.tag_id, "name": tag.name}
        for tag in tags
    ]), 200
