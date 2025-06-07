from flask import Blueprint, request, jsonify
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from backend.app.models.user import User
from app import db

# 创建蓝图
user_bp = Blueprint('user', __name__, url_prefix='/api/users')


class UserView(MethodView):
    def get(self, user_id=None):
        """处理 GET 请求，获取用户信息"""
        if user_id is None:
            # 获取所有用户
            users = User.query.all()
            return jsonify([{
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "register_time": user.register_time.isoformat(),
                "last_login_time": user.last_login_time.isoformat() if user.last_login_time else None,
                "default_address": user.default_address
            } for user in users])
        else:
            # 获取单个用户
            user = User.query.get(user_id)
            if user:
                return jsonify({
                    "user_id": user.user_id,
                    "username": user.username,
                    "email": user.email,
                    "phone": user.phone,
                    "register_time": user.register_time.isoformat(),
                    "last_login_time": user.last_login_time.isoformat() if user.last_login_time else None,
                    "default_address": user.default_address
                })
            else:
                return jsonify({"error": "User not found"}), 404

    def post(self):
        """处理 POST 请求，创建新用户"""
        data = request.json
        try:
            new_user = User(
                username=data['username'],
                password=data['password'],
                email=data['email'],
                phone=data['phone']
            )
            db.session.add(new_user)
            db.session.commit()
            return jsonify({
                "user_id": new_user.user_id,
                "username": new_user.username,
                "email": new_user.email,
                "phone": new_user.phone,
                "register_time": new_user.register_time.isoformat(),
                "last_login_time": new_user.last_login_time.isoformat() if new_user.last_login_time else None,
                "default_address": new_user.default_address
            }), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Username or Email already exists"}), 400
        except KeyError as e:
            return jsonify({"error": f"Missing required field: {e.args[0]}"}), 400

    def put(self, user_id):
        """处理 PUT 请求，更新用户信息"""
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        data = request.json
        try:
            user.username = data.get('username', user.username)
            user.email = data.get('email', user.email)
            user.phone = data.get('phone', user.phone)
            user.default_address = data.get('default_address', user.default_address)
            db.session.commit()
            return jsonify({
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "register_time": user.register_time.isoformat(),
                "last_login_time": user.last_login_time.isoformat() if user.last_login_time else None,
                "default_address": user.default_address
            })
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Username or Email already exists"}), 400

    def delete(self, user_id):
        """处理 DELETE 请求，删除用户"""
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return jsonify({"message": "User deleted"}), 204
        else:
            return jsonify({"error": "User not found"}), 404


# 将 UserView 注册到蓝图
user_api = UserView.as_view('user_api')
user_bp.add_url_rule('/', view_func=user_api, methods=['GET', 'POST'], defaults={'user_id': None})
user_bp.add_url_rule('/<int:user_id>', view_func=user_api, methods=['GET', 'PUT', 'DELETE'])