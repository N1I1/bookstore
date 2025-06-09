from flask import Blueprint, request, jsonify
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.models.complaint import Complaint
from app import db

# 创建蓝图
complaint_bp = Blueprint('complaint', __name__, url_prefix='/api/complaints')


class ComplaintView(MethodView):
    def get(self, complaint_id=None):
        """处理 GET 请求，获取投诉信息"""
        if complaint_id is None:
            # 获取所有投诉
            complaints = Complaint.query.all()
            return jsonify([{
                "complaint_id": complaint.complaint_id,
                "user_id": complaint.user_id,
                "content": complaint.content,
                "complaint_time": complaint.complaint_time.isoformat(),
                "status": complaint.status,
                "result": complaint.result
            } for complaint in complaints])
        else:
            # 获取单个投诉
            complaint = Complaint.query.get(complaint_id)
            if complaint:
                return jsonify({
                    "complaint_id": complaint.complaint_id,
                    "user_id": complaint.user_id,
                    "content": complaint.content,
                    "complaint_time": complaint.complaint_time.isoformat(),
                    "status": complaint.status,
                    "result": complaint.result
                })
            else:
                return jsonify({"error": "Complaint not found"}), 404

    def post(self):
        """处理 POST 请求，创建新投诉"""
        data = request.json
        try:
            new_complaint = Complaint(
                user_id=data['user_id'],
                content=data['content'],
                status=data.get('status', '待处理'),
                result=data.get('result')
            )
            db.session.add(new_complaint)
            db.session.commit()
            return jsonify({
                "complaint_id": new_complaint.complaint_id,
                "user_id": new_complaint.user_id,
                "content": new_complaint.content,
                "complaint_time": new_complaint.complaint_time.isoformat(),
                "status": new_complaint.status,
                "result": new_complaint.result
            }), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Invalid user_id"}), 400
        except KeyError as e:
            return jsonify({"error": f"Missing required field: {e.args[0]}"}), 400

    def put(self, complaint_id):
        """处理 PUT 请求，更新投诉信息"""
        complaint = Complaint.query.get(complaint_id)
        if not complaint:
            return jsonify({"error": "Complaint not found"}), 404

        data = request.json
        try:
            complaint.content = data.get('content', complaint.content)
            complaint.status = data.get('status', complaint.status)
            complaint.result = data.get('result', complaint.result)
            db.session.commit()
            return jsonify({
                "complaint_id": complaint.complaint_id,
                "user_id": complaint.user_id,
                "content": complaint.content,
                "complaint_time": complaint.complaint_time.isoformat(),
                "status": complaint.status,
                "result": complaint.result
            })
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Invalid user_id"}), 400

    def delete(self, complaint_id):
        """处理 DELETE 请求，删除投诉"""
        complaint = Complaint.query.get(complaint_id)
        if complaint:
            db.session.delete(complaint)
            db.session.commit()
            return jsonify({"message": "Complaint deleted"}), 204
        else:
            return jsonify({"error": "Complaint not found"}), 404


# 将 ComplaintView 注册到蓝图
complaint_api = ComplaintView.as_view('complaint_api')
complaint_bp.add_url_rule('/', view_func=complaint_api, methods=['GET', 'POST'], defaults={'complaint_id': None})
complaint_bp.add_url_rule('/<int:complaint_id>', view_func=complaint_api, methods=['GET', 'PUT', 'DELETE'])