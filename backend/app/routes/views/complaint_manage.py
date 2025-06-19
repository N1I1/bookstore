from flask import Blueprint, request, jsonify, session
from flask.views import MethodView
from datetime import datetime
from app.models import Complaint, User
from app import db

# 定义蓝图
complaint_manage_bp = Blueprint('complaint_manage', __name__, url_prefix='/api/complaint_manage')

class ComplaintAPI(MethodView):
    def dispatch_request(self, *args, **kwargs):
        # 获取请求的 HTTP 方法
        method = request.method.lower()
        # 获取请求路径
        path = request.path

        # 根据 HTTP 方法和请求路径调用对应的自定义方法
        if method == 'get':
            if path.endswith('/user_get'):
                return self.user_get()
            elif path.endswith('/admin_get'):
                return self.admin_get()
            else:
                return jsonify({"error": "Invalid path for GET request"}), 400
        elif method == 'post':
            if path.endswith('/user_create'):
                return self.user_create()
            elif path.endswith('/user_change_status'):
                return self.user_change_status()
            elif path.endswith('/deal_with_complaint'):
                return self.deal_with_complaint()
            else:
                return jsonify({"error": "Invalid path for POST request"}), 400
        else:
            return jsonify({"error": "Method not allowed"}), 405
    def user_get(self):
        user_id = session.get('user_id')
        print(user_id)
        if not user_id:
            return jsonify({"error": "User not logged in"}), 401

        try:
            complaints = Complaint.query.filter_by(user_id=user_id).all()
            user = db.session.get(User, user_id)
            username = user.username if user else ""

            complaint_info = [
                {
                    "complaint_id": complaint.complaint_id,
                    "content": complaint.content,
                    "complaint_time": complaint.complaint_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "status": complaint.status,
                    "result": complaint.result,
                    "username": username
                } for complaint in complaints
            ]

            return jsonify({
                "message": "Complaints found" if complaint_info else "No complaints found",
                "complaints": complaint_info
            }), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def user_create(self):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "User not logged in"}), 401

        data = request.json
        content = data.get('content')
        if not content:
            return jsonify({"error": "Complaint content cannot be empty"}), 400

        try:
            new_complaint = Complaint(
                user_id=user_id,
                content=content,
                complaint_time=datetime.now(),
                status='待处理'
            )
            db.session.add(new_complaint)
            db.session.commit()
            return jsonify({"message": "Complaint created successfully"}), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    def user_change_status(self):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "User not logged in"}), 401

        complaint_id = request.json.get('complaint_id')
        try:
            complaint = db.session.get(Complaint, complaint_id)
            if not complaint or complaint.user_id != user_id:
                print(f"Complaint not found or user_id mismatch: {complaint_id}, {user_id}")
                return jsonify({"error": "Complaint not found or you do not have permission to modify it"}), 404

            if complaint.status != '已受理':
                return jsonify({"error": "Complaint status is not '已受理'", 'cur_status': complaint.status}), 400

            complaint.status = '已解决'
            db.session.commit()
            return jsonify({"message": "Complaint status updated successfully"}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def admin_get(self):
        status = request.args.get('status')
        try:
            query = Complaint.query
            if status:
                query = query.filter_by(status=status)
            complaints = query.all()
            
            complaint_info = []
            for complaint in complaints:
                if complaint.user_id:
                    user = db.session.get(User, complaint.user_id)
                    username = user.username
                else:
                    username = ""
                complaint_info.append({
                    "complaint_id": complaint.complaint_id,
                    "user_id": complaint.user_id,
                    "username": username,
                    "content": complaint.content,
                    "complaint_time": complaint.complaint_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "status": complaint.status,
                    "result": complaint.result
                    })

            if complaint_info:
                return jsonify({"message": "Complaints found", "complaints": complaint_info}), 200
            else:
                return jsonify({"message": "No complaints found"}), 404

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def deal_with_complaint(self):
        admin_id = session.get('admin_id')
        if not admin_id:
            return jsonify({"error": "Admin not logged in"}), 401

        data = request.json
        print(data)
        complaint_id = data.get('complaint_id')
        result = data.get('result')
        if not complaint_id or not result:
            return jsonify({"error": "Missing complaint_id or result"}), 400

        try:
            complaint = db.session.get(Complaint, complaint_id)
            if not complaint:
                return jsonify({"error": "Complaint not found"}), 404

            if complaint.status != '待处理':
                return jsonify({"error": "Complaint status is not 'Pending'"}), 400

            complaint.status = '已受理'
            complaint.result = result
            db.session.commit()
            return jsonify({"message": "Complaint processed successfully"}), 200

        except Exception as e:
            db.session.rollback()
            print(f"Error processing complaint: {str(e)}")
            return jsonify({"error": str(e)}), 500

# 注册路由
complaint_manage_bp.add_url_rule('/user_get', view_func=ComplaintAPI.as_view('user_get'), methods=['GET'])
complaint_manage_bp.add_url_rule('/admin_get', view_func=ComplaintAPI.as_view('admin_get'), methods=['GET'])
complaint_manage_bp.add_url_rule('/user_create', view_func=ComplaintAPI.as_view('user_create'), methods=['POST'])
complaint_manage_bp.add_url_rule('/user_change_status', view_func=ComplaintAPI.as_view('user_change_status'), methods=['POST'])
complaint_manage_bp.add_url_rule('/deal_with_complaint', view_func=ComplaintAPI.as_view('deal_with_complaint'), methods=['POST'])
