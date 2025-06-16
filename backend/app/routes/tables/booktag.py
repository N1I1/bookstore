from flask import Blueprint, request, jsonify, session
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from app.models.booktag import book_tag
from app import db

booktag_bp = Blueprint('booktag', __name__, url_prefix='/api/booktags')


class BookTagView(MethodView):
    def post(self):
        """处理 POST 请求，创建新的图书标签关联"""
        admin_id = session.get('admin_id', None)
        if not admin_id:
            return jsonify({"error": "Unauthorized"}), 401
        book_id = request.json.get('book_id')
        tag_id = request.json.get('tag_id')
        if not book_id or not tag_id:
            return jsonify({"error": "Missing required fields: book_id and tag_id"}), 400
        try:
            # 检查是否已存在该关联
            exists = db.session.execute(
                db.select(book_tag).where(
                    book_tag.c.book_id == book_id,
                    book_tag.c.tag_id == tag_id
                )
            ).first()
            if exists:
                return jsonify({"error": "Duplicate book tag"}), 400

            # 插入新关联
            db.session.execute(
                book_tag.insert().values(book_id=book_id, tag_id=tag_id)
            )
            db.session.commit()
            return jsonify({
                "book_id": book_id,
                "tag_id": tag_id
            }), 201
        except Exception:
            db.session.rollback()
            return jsonify({"error": "Server error"}), 500

    def put(self):
        """处理 PUT 请求，更新图书标签信息"""
        admin_id = session.get('admin_id', None)
        if not admin_id:
            return jsonify({"error": "Unauthorized"}), 401
        data = request.json
        book_id = data.get('book_id')
        tag_id = data.get('tag_id')
        new_tag_id = data.get('new_tag_id')
        if not book_id or not tag_id or not new_tag_id:
            return jsonify({"error": "Missing required fields: book_id, tag_id, new_tag_id"}), 400

        # 检查原关联是否存在
        exists = db.session.execute(
            db.select(book_tag).where(
                book_tag.c.book_id == book_id,
                book_tag.c.tag_id == tag_id
            )
        ).first()
        if not exists:
            return jsonify({"error": "Book tag relation not found"}), 404

        # 检查新关联是否已存在
        duplicate = db.session.execute(
            db.select(book_tag).where(
                book_tag.c.book_id == book_id,
                book_tag.c.tag_id == new_tag_id
            )
        ).first()
        if duplicate:
            return jsonify({"error": "Duplicate book tag"}), 400

        try:
            # 先删除原关联
            db.session.execute(
                book_tag.delete().where(
                    book_tag.c.book_id == book_id,
                    book_tag.c.tag_id == tag_id
                )
            )
            # 再插入新关联
            db.session.execute(
                book_tag.insert().values(book_id=book_id, tag_id=new_tag_id)
            )
            db.session.commit()
            return jsonify({
                "book_id": book_id,
                "tag_id": new_tag_id
            }), 200
        except Exception:
            db.session.rollback()
            return jsonify({"error": "Server error"}), 500

    def delete(self):
        """处理 DELETE 请求，删除图书标签"""
        admin_id = session.get('admin_id', None)
        if not admin_id:
            return jsonify({"error": "Unauthorized"}), 401
        data = request.json
        book_id = data.get('book_id')
        tag_id = data.get('tag_id')
        if not book_id or not tag_id:
            return jsonify({"error": "Missing required fields: book_id and tag_id"}), 400

        exists = db.session.execute(
            db.select(book_tag).where(
                book_tag.c.book_id == book_id,
                book_tag.c.tag_id == tag_id
            )
        ).first()
        if not exists:
            return jsonify({"error": "Book tag relation not found"}), 404

        try:
            db.session.execute(
                book_tag.delete().where(
                    book_tag.c.book_id == book_id,
                    book_tag.c.tag_id == tag_id
                )
            )
            db.session.commit()
            return '', 204
        except Exception:
            db.session.rollback()
            return jsonify({"error": "Server error"}), 500

# 将 BookTagView 注册到蓝图
booktag_api = BookTagView.as_view('booktag_api')
booktag_bp.add_url_rule('/', view_func=booktag_api, methods=['POST', 'PUT', 'DELETE'])
