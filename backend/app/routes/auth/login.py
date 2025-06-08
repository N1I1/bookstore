from flask import Blueprint, request, jsonify, session
from flask.views import MethodView
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from datetime import datetime

from app import db
from app.models.user import User
from app.models.admin import Admin


# 定义蓝图
login_bp = Blueprint('login', __name__, url_prefix='/api/login')

class LoginView(MethodView):
    def post(self):
        # 获取表单数据
        data = request.json
        username = data.get('username')
        password = data.get('password')
        user_type = data.get('user_type')  # 'user' 或 'admin'

        if not username or not password or not user_type:
            return jsonify({"error": "Missing username, password, or user_type"}), 400

        if user_type == 'user':
            # 用户登录逻辑
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                # 登录成功，更新最后登录时间
                user.last_login_time = datetime.now()
                db.session.commit()
                session['user_id'] = user.user_id
                session['username'] = user.username
                session['user_type'] = 'user'
                return jsonify({"message": "Login successful", "user_id": user.user_id, "user_type": "user"}), 200
            else:
                return jsonify({"error": "Invalid username or password"}), 401
        elif user_type == 'admin':
            # 管理员登录逻辑
            admin = Admin.query.filter_by(username=username).first()
            if admin and check_password_hash(admin.password, password):
                # 登录成功，更新最后登录时间
                admin.last_login_time = datetime.now()
                db.session.commit()
                session['user_id'] = admin.admin_id
                session['username'] = admin.username
                session['user_type'] = 'admin'
                return jsonify({"message": "Login successful", "user_id": admin.admin_id, "user_type": "admin"}), 200
            else:
                return jsonify({"error": "Invalid username or password"}), 401
        else:
            return jsonify({"error": "Unknown user type"}), 400

# 注册视图
login_bp.add_url_rule('/', view_func=LoginView.as_view('login'))

@login_bp.route('/logout', methods=['POST'])
def logout():
    # 清除会话信息
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('user_type', None)
    return jsonify({"message": "Logout successful"}), 200