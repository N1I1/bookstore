from flask import Blueprint, request, jsonify
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from app.models.booktag import BookTag
from app import db

booktag_bp = Blueprint('booktag', __name__, url_prefix='/api/booktags')


class BookTagView(MethodView):
    def get(self, book_tag_id=None):
        """处理 GET 请求，获取图书标签信息"""
        if book_tag_id is None:
            # 获取所有图书标签
            book_tags = BookTag.query.all()
            print(f"Retrieved {len(book_tags)} book tags from the database.")
            return jsonify([{
                "book_tag_id": tag.book_tag_id,
                "book_id": tag.book_id,
                "tag": tag.tag
            } for tag in book_tags])
        else:
            # 获取单个图书标签
            book_tag = BookTag.query.get(book_tag_id)
            if book_tag:
                return jsonify({
                    "book_tag_id": book_tag.book_tag_id,
                    "book_id": book_tag.book_id,
                    "tag": book_tag.tag
                })
            else:
                return jsonify({"error": "Book tag not found"}), 404

    def post(self):
        """处理 POST 请求，创建新的图书标签"""
        data = request.json
        try:
            new_book_tag = BookTag(
                book_id=data['book_id'],
                tag=data['tag']
            )
            db.session.add(new_book_tag)
            db.session.commit()
            return jsonify({
                "book_tag_id": new_book_tag.book_tag_id,
                "book_id": new_book_tag.book_id,
                "tag": new_book_tag.tag
            }), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Duplicate book tag"}), 400
        except KeyError as e:
            return jsonify({"error": f"Missing required field: {e.args[0]}"}), 400

    def put(self, book_tag_id):
        """处理 PUT 请求，更新图书标签信息"""
        book_tag = BookTag.query.get(book_tag_id)
        if not book_tag:
            return jsonify({"error": "Book tag not found"}), 404

        data = request.json
        try:
            book_tag.book_id = data.get('book_id', book_tag.book_id)
            book_tag.tag = data.get('tag', book_tag.tag)
            db.session.commit()
            return jsonify({
                "book_tag_id": book_tag.book_tag_id,
                "book_id": book_tag.book_id,
                "tag": book_tag.tag
            })
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Duplicate book tag"}), 400

    def delete(self, book_tag_id):
        """处理 DELETE 请求，删除图书标签"""
        book_tag = BookTag.query.get(book_tag_id)
        if book_tag:
            db.session.delete(book_tag)
            db.session.commit()
            return jsonify({"message": "Book tag deleted"}), 204
        else:
            return jsonify({"error": "Book tag not found"}), 404

# 将 BookTagView 注册到蓝图
booktag_api = BookTagView.as_view('booktag_api')
booktag_bp.add_url_rule('/', view_func=booktag_api, methods=['GET', ], defaults={'book_tag_id': None})
booktag_bp.add_url_rule('/', view_func=booktag_api, methods=['POST', ])
booktag_bp.add_url_rule('/<int:book_tag_id>', view_func=booktag_api, methods=['GET', 'PUT', 'DELETE'])
