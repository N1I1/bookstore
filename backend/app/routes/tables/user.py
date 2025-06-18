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
    def get(self):
        """处理 GET 请求，获取用户信息"""
        user_id = session.get('user_id')
        if user_id is None:
            return jsonify({"error": "User not logged in"}), 401
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

    def put(self):
        """处理 PUT 请求，更新用户信息"""
        user_id = session.get('user_id')
        if user_id is None:
            return jsonify({"error": "User not logged in"}), 401
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

    def delete(self):
        """处理 DELETE 请求，删除用户"""
        user_id = session.get('user_id')
        if user_id is None:
            return jsonify({"error": "User not logged in"}), 401
            
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        from app.models.order import Order
        
        active_orders = db.session.query(Order).filter(
            Order.user_id == user_id,
            Order.order_status.not_in(['已完成', '订单取消']),
            Order.is_deleted == False
        ).all()
        
        # 如果有未完成订单，拒绝删除
        if active_orders:
            # 准备详细的错误信息
            order_ids = [str(order.order_id) for order in active_orders]
            order_str = ", ".join(order_ids)
            
            print(f"拒绝删除用户 {user_id}：发现未完成订单 {order_str}")
            return jsonify({
                "error": "您有未完成的订单，不能注销账号",
                "order_ids": order_ids
            }), 400
        
        # 如果没有未完成订单，继续删除操作
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"error": "用户不存在"}), 404
            
        try:
            db.session.delete(user)
            db.session.commit()
            print(f"成功删除用户 {user_id}")
            return '', 204
        except Exception as e:
            db.session.rollback()
            print(f"删除用户出错: {str(e)}")
            return jsonify({"error": "删除账号时发生错误"}), 500


# 将 UserView 注册到蓝图
user_api = UserView.as_view('user_api')
user_bp.add_url_rule('/', view_func=user_api, methods=['GET', 'PUT', 'DELETE'])
