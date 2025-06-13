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
        username = data.get('username', None)
        password = data.get('password', None)

        if not username or not password:
            return jsonify({"error": "Missing username, password"}), 400

        try:
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                user.last_login_time = datetime.now()
                db.session.commit()
                set_user_session(user)
                return jsonify({"message": "Login successful"}), 200
            else:
                return jsonify({"error": "Invalid username or password"}), 401
        except Exception as e:
            db.session.rollback()
            ################
            # 处理异常，返回错误信息 注意详细信息不应该在生产环境中直接返回给用户
            ################
            return jsonify({"error": "Server error", "details": str(e)}), 500

# 注册视图
login_bp.add_url_rule('/', view_func=LoginView.as_view('login'))

@login_bp.route('/logout', methods=['POST'])
def logout():
    # 清除会话信息
    clear_user_session()
    return jsonify({"message": "Logout successful"}), 200

def set_user_session(user):
    session['user_id'] = user.user_id
    session['username'] = user.username

def clear_user_session():
    session.pop('user_id', None)
    session.pop('username', None)