from flask import Blueprint, request, jsonify, session
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.models.userbrowse import UserBrowse
from app import db

# 创建蓝图
user_browse_bp = Blueprint('user_browse', __name__, url_prefix='/api/user_browse')


class UserBrowseView(MethodView):
    def get(self, browse_id):
        """处理 GET 请求，获取浏览记录"""
        user_id = session.get('user_id', None)
        if not user_id:
            return jsonify({"error": "User not logged in"}), 401
        browse = db.session.get(UserBrowse, browse_id)
        if not browse or browse.user_id != user_id:
            return jsonify({"error": "Forbidden"}), 403
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
        user_id = session.get('user_id')
        book_id = request.json.get('book_id')
        if not user_id:
            return jsonify({"error": "User not logged in"}), 401
        if not book_id:
            return jsonify({"error": "Book ID is required"}), 400
        browse = db.session.query(UserBrowse).filter_by(user_id=user_id, book_id=book_id).first()
        if browse:
            # 如果记录已存在，更新浏览时间
            browse.browse_time = datetime.now()
        else:
            browse = UserBrowse(
                user_id=user_id,
                book_id=book_id,
                browse_time=datetime.now()
            )
            db.session.add(browse)

        try:
            db.session.commit()
            return jsonify({
                "browse_id": browse.browse_id,
                "user_id": browse.user_id,
                "book_id": browse.book_id,
                "browse_time": browse.browse_time.isoformat()
            }), 200
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Duplicate browse entry"}), 400

    def delete(self, browse_id):
        """处理 DELETE 请求，删除浏览记录"""
        user_id = session.get('user_id', None)
        if not user_id:
            return jsonify({"error": "User not logged in"}), 401
        browse = db.session.query(UserBrowse).filter_by(browse_id=browse_id, user_id=user_id).first()
        if not browse:
            return jsonify({"error": "Browse record not found"}), 404
        try:
            db.session.delete(browse)
            db.session.commit()
            return '', 204
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Failed to delete browse record"}), 400
@user_browse_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_browses(user_id):
    """获取指定用户的所有浏览记录（仅本人可查）"""
    current_user_id = session.get('user_id')
    if current_user_id is None:
        return jsonify({"error": "User not logged in"}), 401
    if current_user_id != user_id:
        return jsonify({"error": "Forbidden"}), 403

    browses = UserBrowse.query.filter_by(user_id=user_id).order_by(UserBrowse.browse_time.desc()).all()
    result = [
        {
            "browse_id": b.browse_id,
            "user_id": b.user_id,
            "book_id": b.book_id,
            "browse_time": b.browse_time.isoformat()
        }
        for b in browses
    ]
    return jsonify(result), 200

# 将 UserBrowseView 注册到蓝图
user_browse_api = UserBrowseView.as_view('user_browse_api')
user_browse_bp.add_url_rule('/', view_func=user_browse_api, methods=['POST'])
user_browse_bp.add_url_rule('/<int:browse_id>', view_func=user_browse_api, methods=['GET', 'DELETE'])
