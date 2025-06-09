from flask import Blueprint, request, jsonify
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.models.userbrowse import UserBrowse
from app import db

# 创建蓝图
user_browse_bp = Blueprint('user_browse', __name__, url_prefix='/api/user_browse')


class UserBrowseView(MethodView):
    def get(self, browse_id=None):
        """处理 GET 请求，获取浏览记录"""
        if browse_id is None:
            # 获取所有浏览记录
            browses = UserBrowse.query.all()
            return jsonify([{
                "browse_id": browse.browse_id,
                "user_id": browse.user_id,
                "book_id": browse.book_id,
                "browse_time": browse.browse_time.isoformat()
            } for browse in browses])
        else:
            # 获取单个浏览记录
            browse = UserBrowse.query.get(browse_id)
            if browse:
                return jsonify({
                    "browse_id": browse.browse_id,
                    "user_id": browse.user_id,
                    "book_id": browse.book_id,
                    "browse_time": browse.browse_time.isoformat()
                })
            else:
                return jsonify({"error": "Browse record not found"}), 404

    def post(self):
        """处理 POST 请求，创建新的浏览记录"""
        data = request.json
        try:
            new_browse = UserBrowse(
                user_id=data['user_id'],
                book_id=data['book_id']
            )
            db.session.add(new_browse)
            db.session.commit()
            return jsonify({
                "browse_id": new_browse.browse_id,
                "user_id": new_browse.user_id,
                "book_id": new_browse.book_id,
                "browse_time": new_browse.browse_time.isoformat()
            }), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Duplicate browse entry"}), 400
        except KeyError as e:
            return jsonify({"error": f"Missing required field: {e.args[0]}"}), 400

    def delete(self, browse_id):
        """处理 DELETE 请求，删除浏览记录"""
        browse = UserBrowse.query.get(browse_id)
        if browse:
            db.session.delete(browse)
            db.session.commit()
            return jsonify({"message": "Browse record deleted"}), 204
        else:
            return jsonify({"error": "Browse record not found"}), 404

    def put(self, browse_id):
        """处理 PUT 请求，更新浏览记录（例如：更新浏览时间）"""
        browse = UserBrowse.query.get(browse_id)
        if not browse:
            return jsonify({"error": "Browse record not found"}), 404

        data = request.json
        try:
            browse.user_id = data.get('user_id', browse.user_id)
            browse.book_id = data.get('book_id', browse.book_id)
            browse.browse_time = datetime.now()  # 更新浏览时间
            db.session.commit()
            return jsonify({
                "browse_id": browse.browse_id,
                "user_id": browse.user_id,
                "book_id": browse.book_id,
                "browse_time": browse.browse_time.isoformat()
            })
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Duplicate browse entry"}), 400


# 将 UserBrowseView 注册到蓝图
user_browse_api = UserBrowseView.as_view('user_browse_api')
user_browse_bp.add_url_rule('/', view_func=user_browse_api, methods=['GET', 'POST'], defaults={'browse_id': None})
user_browse_bp.add_url_rule('/<int:browse_id>', view_func=user_browse_api, methods=['GET', 'PUT', 'DELETE'])