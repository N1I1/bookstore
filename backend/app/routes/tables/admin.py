from flask import Blueprint, request, jsonify
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.models.admin import Admin
from app import db

# 创建蓝图
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admins')


class AdminView(MethodView):
    def get(self, admin_id=None):
        """处理 GET 请求，获取管理员信息"""
        if admin_id is None:
            # 获取所有管理员
            admins = Admin.query.all()
            return jsonify([{
                "admin_id": admin.admin_id,
                "username": admin.username,
                "email": admin.email,
                "phone": admin.phone,
                "register_time": admin.register_time.isoformat(),
                "last_login_time": admin.last_login_time.isoformat() if admin.last_login_time else None
            } for admin in admins])
        else:
            # 获取单个管理员
            admin = Admin.query.get(admin_id)
            if admin:
                return jsonify({
                    "admin_id": admin.admin_id,
                    "username": admin.username,
                    "email": admin.email,
                    "phone": admin.phone,
                    "register_time": admin.register_time.isoformat(),
                    "last_login_time": admin.last_login_time.isoformat() if admin.last_login_time else None
                })
            else:
                return jsonify({"error": "Admin not found"}), 404

    def post(self):
        """处理 POST 请求，创建新管理员"""
        data = request.json
        try:
            new_admin = Admin(
                username=data['username'],
                password=data['password'],
                email=data['email'],
                phone=data['phone']
            )
            db.session.add(new_admin)
            db.session.commit()
            return jsonify({
                "admin_id": new_admin.admin_id,
                "username": new_admin.username,
                "email": new_admin.email,
                "phone": new_admin.phone,
                "register_time": new_admin.register_time.isoformat(),
                "last_login_time": new_admin.last_login_time.isoformat() if new_admin.last_login_time else None
            }), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Username or Email already exists"}), 400
        except KeyError as e:
            return jsonify({"error": f"Missing required field: {e.args[0]}"}), 400

    def put(self, admin_id):
        """处理 PUT 请求，更新管理员信息"""
        admin = Admin.query.get(admin_id)
        if not admin:
            return jsonify({"error": "Admin not found"}), 404

        data = request.json
        try:
            admin.username = data.get('username', admin.username)
            admin.password = data.get('password', admin.password)
            admin.email = data.get('email', admin.email)
            admin.phone = data.get('phone', admin.phone)
            admin.last_login_time = datetime.now()  # 更新最后登录时间
            db.session.commit()
            return jsonify({
                "admin_id": admin.admin_id,
                "username": admin.username,
                "email": admin.email,
                "phone": admin.phone,
                "register_time": admin.register_time.isoformat(),
                "last_login_time": admin.last_login_time.isoformat()
            })
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Username or Email already exists"}), 400

    def delete(self, admin_id):
        """处理 DELETE 请求，删除管理员"""
        admin = Admin.query.get(admin_id)
        if admin:
            db.session.delete(admin)
            db.session.commit()
            return jsonify({"message": "Admin deleted"}), 204
        else:
            return jsonify({"error": "Admin not found"}), 404


# 将 AdminView 注册到蓝图
admin_api = AdminView.as_view('admin_api')
admin_bp.add_url_rule('/', view_func=admin_api, methods=['GET', 'POST'], defaults={'admin_id': None})
admin_bp.add_url_rule('/<int:admin_id>', view_func=admin_api, methods=['GET', 'PUT', 'DELETE'])