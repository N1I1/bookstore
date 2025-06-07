from flask import Blueprint, request, jsonify
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from backend.app.models.tables.suggestion import Suggestion
from app import db

# 创建蓝图
suggestion_bp = Blueprint('suggestion', __name__, url_prefix='/api/suggestions')


class SuggestionView(MethodView):
    def get(self, suggestion_id=None):
        """处理 GET 请求，获取建议信息"""
        if suggestion_id is None:
            # 获取所有建议
            suggestions = Suggestion.query.all()
            return jsonify([{
                "suggestion_id": suggestion.suggestion_id,
                "user_id": suggestion.user_id,
                "content": suggestion.content,
                "suggestion_time": suggestion.suggestion_time.isoformat()
            } for suggestion in suggestions])
        else:
            # 获取单个建议
            suggestion = Suggestion.query.get(suggestion_id)
            if suggestion:
                return jsonify({
                    "suggestion_id": suggestion.suggestion_id,
                    "user_id": suggestion.user_id,
                    "content": suggestion.content,
                    "suggestion_time": suggestion.suggestion_time.isoformat()
                })
            else:
                return jsonify({"error": "Suggestion not found"}), 404

    def post(self):
        """处理 POST 请求，创建新建议"""
        data = request.json
        try:
            new_suggestion = Suggestion(
                user_id=data['user_id'],
                content=data['content']
            )
            db.session.add(new_suggestion)
            db.session.commit()
            return jsonify({
                "suggestion_id": new_suggestion.suggestion_id,
                "user_id": new_suggestion.user_id,
                "content": new_suggestion.content,
                "suggestion_time": new_suggestion.suggestion_time.isoformat()
            }), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Invalid user_id"}), 400
        except KeyError as e:
            return jsonify({"error": f"Missing required field: {e.args[0]}"}), 400

    def put(self, suggestion_id):
        """处理 PUT 请求，更新建议信息"""
        suggestion = Suggestion.query.get(suggestion_id)
        if not suggestion:
            return jsonify({"error": "Suggestion not found"}), 404

        data = request.json
        try:
            suggestion.content = data.get('content', suggestion.content)
            db.session.commit()
            return jsonify({
                "suggestion_id": suggestion.suggestion_id,
                "user_id": suggestion.user_id,
                "content": suggestion.content,
                "suggestion_time": suggestion.suggestion_time.isoformat()
            })
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Invalid user_id"}), 400

    def delete(self, suggestion_id):
        """处理 DELETE 请求，删除建议"""
        suggestion = Suggestion.query.get(suggestion_id)
        if suggestion:
            db.session.delete(suggestion)
            db.session.commit()
            return jsonify({"message": "Suggestion deleted"}), 204
        else:
            return jsonify({"error": "Suggestion not found"}), 404


# 将 SuggestionView 注册到蓝图
suggestion_api = SuggestionView.as_view('suggestion_api')
suggestion_bp.add_url_rule('/', view_func=suggestion_api, methods=['GET', 'POST'], defaults={'suggestion_id': None})
suggestion_bp.add_url_rule('/<int:suggestion_id>', view_func=suggestion_api, methods=['GET', 'PUT', 'DELETE'])