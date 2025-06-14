from flask import Blueprint, request, jsonify
from flask.views import MethodView
from werkzeug.security import generate_password_hash
from datetime import datetime

from app.models import User, Admin
from app import db

# 定义蓝图
info_bp = Blueprint('info', __name__, url_prefix='/api/update_info')

class UpdateInfoView(MethodView):
    def post(self):
        # 获取请求数据
        data = request.json
        user_id = data.get('user_id')  # 用户或管理员的ID
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        phone = data.get('phone')
        user_type = data.get('user_type')  # 'user' 或 'admin'
        default_address = data.get('default_address')  # 用户的默认地址

        # 验证输入
        if not user_id or not user_type:
            return jsonify({"error": "Missing user_id or user_type"}), 400

        try:
            if user_type == 'user':
                # 更新用户信息
                user = User.query.filter_by(user_id=user_id).first()
                if not user:
                    return jsonify({"error": "User not found"}), 404

                if username:
                    user.username = username
                if password:
                    user.password = generate_password_hash(password)
                if email:
                    user.email = email
                if phone:
                    user.phone = phone
                if default_address is not None:
                    user.default_address = default_address  # 更新默认地址
                user.last_login_time = datetime.now()

                db.session.commit()
                return jsonify({"message": "User information updated successfully"}), 200

            elif user_type == 'admin':
                # 更新管理员信息
                admin = Admin.query.filter_by(admin_id=user_id).first()
                if not admin:
                    return jsonify({"error": "Admin not found"}), 404

                if username:
                    admin.username = username
                if password:
                    admin.password = generate_password_hash(password)
                if email:
                    admin.email = email
                if phone:
                    admin.phone = phone
                admin.last_login_time = datetime.now()

                db.session.commit()
                return jsonify({"message": "Admin information updated successfully"}), 200

            else:
                return jsonify({"error": "Invalid user type"}), 400

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

# 注册视图
info_bp.add_url_rule('/', view_func=UpdateInfoView.as_view('update_info'))