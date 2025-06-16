from flask import Blueprint, request, jsonify, session
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from app.models.tag import Tag
from app import db

tag_bp = Blueprint('tag', __name__, url_prefix='/api/tags')

class TagView(MethodView):
    def get(self, tag_id=None):
        """获取所有标签或单个标签"""
        if tag_id is None:
            tags = Tag.query.all()
            return jsonify([{"tag_id": t.tag_id, "name": t.name} for t in tags]), 200
        tag = db.session.get(Tag, tag_id)
        if tag:
            return jsonify({"tag_id": tag.tag_id, "name": tag.name}), 200
        return jsonify({"error": "Tag not found"}), 404

    def post(self):
        """创建新标签（需管理员权限）"""
        admin_id = session.get('admin_id')
        if not admin_id:
            return jsonify({"error": "Unauthorized"}), 401
        data = request.json
        name = data.get('name')
        if not name:
            return jsonify({"error": "Missing required field: name"}), 400
        try:
            tag = Tag(name=name)
            db.session.add(tag)
            db.session.commit()
            return jsonify({"tag_id": tag.tag_id, "name": tag.name}), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Tag name already exists"}), 400

    def put(self, tag_id):
        """修改标签名称（需管理员权限）"""
        admin_id = session.get('admin_id')
        if not admin_id:
            return jsonify({"error": "Unauthorized"}), 401
        tag = db.session.get(Tag, tag_id)
        if not tag:
            return jsonify({"error": "Tag not found"}), 404
        data = request.json
        name = data.get('name')
        if not name:
            return jsonify({"error": "Missing required field: name"}), 400
        try:
            tag.name = name
            db.session.commit()
            return jsonify({"tag_id": tag.tag_id, "name": tag.name}), 200
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Tag name already exists"}), 400

    def delete(self, tag_id):
        """删除标签（需管理员权限）"""
        admin_id = session.get('admin_id')
        if not admin_id:
            return jsonify({"error": "Unauthorized"}), 401
        tag = db.session.get(Tag, tag_id)
        if not tag:
            return jsonify({"error": "Tag not found"}), 404
        db.session.delete(tag)
        db.session.commit()
        return '', 204


# 路由注册
tag_api = TagView.as_view('tag_api')
tag_bp.add_url_rule('/', view_func=tag_api, methods=['GET'], defaults={'tag_id': None})
tag_bp.add_url_rule('/', view_func=tag_api, methods=['POST'])
tag_bp.add_url_rule('/<int:tag_id>', view_func=tag_api, methods=['GET', 'PUT', 'DELETE'])
