from flask import Blueprint, request, jsonify

from app.models.book import Book
from app import db

book_bp = Blueprint('book', __name__, url_prefix='/api/books')

@book_bp.route('/', methods=['GET'])
def get_books():
    """获取所有图书"""
    books = Book.query.all()
    return jsonify([
        {
            'id': b.id,
            'title': b.title,
            'author': b.author,
            'description': b.description,
            'price': b.price,
            'stock': b.stock
        } for b in books
    ])

@book_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """获取单本图书"""
    book = Book.query.get_or_404(book_id)
    return jsonify({
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'description': book.description,
        'price': book.price,
        'stock': book.stock
    })

@book_bp.route('/', methods=['POST'])
def add_book():
    """添加图书"""
    data = request.get_json()
    book = Book(
        title=data['title'],
        author=data['author'],
        description=data.get('description', ''),
        price=data['price'],
        stock=data.get('stock', 0)
    )
    db.session.add(book)
    db.session.commit()
    return jsonify({'message': 'Book added', 'id': book.id}), 201

