from flask import Blueprint, request, jsonify
from flask.views import MethodView
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from datetime import datetime

from app import db
from app.models.user import User
from app.models.admin import Admin

# 定义蓝图
register_bp = Blueprint('register', __name__, url_prefix='/api/register')

class RegisterView(MethodView):
    def post(self):
        # 获取请求数据
        data = request.json
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        phone = data.get('phone')
        user_type = data.get('user_type')  # 'user' 或 'admin'

        # 验证输入
        if not username or not password or not email or not phone or not user_type:
            return jsonify({"error": "Missing required fields"}), 400

        # 检查用户类型
        if user_type not in ['user', 'admin']:
            return jsonify({"error": "Invalid user type"}), 400

        # 检查用户名或邮箱是否已存在
        if user_type == 'user':
            if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
                return jsonify({"error": "Username or email already exists"}), 400
        elif user_type == 'admin':
            if Admin.query.filter_by(username=username).first() or Admin.query.filter_by(email=email).first():
                return jsonify({"error": "Username or email already exists"}), 400

        # 创建用户或管理员
        try:
            if user_type == 'user':
                new_user = User(
                    username=username,
                    password=generate_password_hash(password),
                    email=email,
                    phone=phone,
                    register_time=datetime.now()
                )
                db.session.add(new_user)
                db.session.commit()
                return jsonify({"message": "User registered successfully", "user_id": new_user.user_id}), 201
            elif user_type == 'admin':
                new_admin = Admin(
                    username=username,
                    password=generate_password_hash(password),
                    email=email,
                    phone=phone,
                    register_time=datetime.now()
                )
                db.session.add(new_admin)
                db.session.commit()
                return jsonify({"message": "Admin registered successfully", "admin_id": new_admin.admin_id}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

# 注册视图
register_bp.add_url_rule('/', view_func=RegisterView.as_view('register'))