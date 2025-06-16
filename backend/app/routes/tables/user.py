from flask import Blueprint, request, jsonify, session
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from werkzeug.security import generate_password_hash

from app.models.user import User
from app import db

# 创建蓝图
user_bp = Blueprint('user', __name__, url_prefix='/api/users')


class UserView(MethodView):
    def get(self, user_id):
        """处理 GET 请求，获取用户信息"""
        current_user_id = session.get('user_id')
        if current_user_id is None:
            return jsonify({"error": "User not logged in"}), 401
        if current_user_id != user_id:
            return jsonify({"error": "Forbidden"}), 403
        user = db.session.get(User, user_id)
        if user:
            return jsonify({
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "register_time": user.register_time.isoformat(),
                "last_login_time": user.last_login_time.isoformat() if user.last_login_time else None,
                "default_address": user.default_address
            })
        else:
            return jsonify({"error": "User not found"}), 404

    def put(self, user_id):
        """处理 PUT 请求，更新用户信息"""
        current_user_id = session.get('user_id')
        if current_user_id is None:
            return jsonify({"error": "User not logged in"}), 401
        if current_user_id != user_id:
            return jsonify({"error": "Forbidden"}), 403
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        data = request.json
        try:
            user.username = data.get('username', user.username)
            user.email = data.get('email', user.email)
            user.phone = data.get('phone', user.phone)
            if 'password' in data and data['password']:
                user.password = generate_password_hash(data['password'])
            user.default_address = data.get('default_address', user.default_address)
            db.session.commit()
            return jsonify({"message": "User updated successfully"}), 200
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Username or Email already exists"}), 400

    def delete(self, user_id):
        """处理 DELETE 请求，删除用户"""
        current_user_id = session.get('user_id')
        if current_user_id is None:
            return jsonify({"error": "User not logged in"}), 401
        if current_user_id != user_id:
            return jsonify({"error": "Forbidden"}), 403
        user = db.session.get(User, user_id)
        if user:
            # 此处可能会出现问题，因 comment forum_post都有一个外键指向user，之后再考虑
            db.session.delete(user)
            db.session.commit()
            return '', 204
        else:
            return jsonify({"error": "User not found"}), 404


# 将 UserView 注册到蓝图
user_api = UserView.as_view('user_api')
user_bp.add_url_rule('/<int:user_id>', view_func=user_api, methods=['GET', 'PUT', 'DELETE'])
