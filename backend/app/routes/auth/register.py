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

        # 验证输入
        if not username or not password or not email or not phone:
            return jsonify({"error": "Missing required fields"}), 400

        # 检查用户名或邮箱是否已存在
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            return jsonify({"error": "Username or email already exists"}), 400

        # 创建用户
        try:
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
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

# 注册视图
register_bp.add_url_rule('/', view_func=RegisterView.as_view('register'))