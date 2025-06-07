from flask import Blueprint, request, jsonify
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from backend.app.models.suggestionagree import SuggestionAgree
from app import db

# 创建蓝图
suggestion_agree_bp = Blueprint('suggestion_agree', __name__, url_prefix='/api/suggestion_agrees')


class SuggestionAgreeView(MethodView):
    def get(self, agree_id=None):
        """处理 GET 请求，获取赞同信息"""
        if agree_id is None:
            # 获取所有赞同记录
            agrees = SuggestionAgree.query.all()
            return jsonify([{
                "agree_id": agree.agree_id,
                "suggestion_id": agree.suggestion_id,
                "user_id": agree.user_id
            } for agree in agrees])
        else:
            # 获取单个赞同记录
            agree = SuggestionAgree.query.get(agree_id)
            if agree:
                return jsonify({
                    "agree_id": agree.agree_id,
                    "suggestion_id": agree.suggestion_id,
                    "user_id": agree.user_id
                })
            else:
                return jsonify({"error": "Agree not found"}), 404

    def post(self):
        """处理 POST 请求，创建新的赞同记录"""
        data = request.json
        try:
            new_agree = SuggestionAgree(
                suggestion_id=data['suggestion_id'],
                user_id=data['user_id']
            )
            db.session.add(new_agree)
            db.session.commit()
            return jsonify({
                "agree_id": new_agree.agree_id,
                "suggestion_id": new_agree.suggestion_id,
                "user_id": new_agree.user_id
            }), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Duplicate agree entry"}), 400
        except KeyError as e:
            return jsonify({"error": f"Missing required field: {e.args[0]}"}), 400

    def delete(self, agree_id):
        """处理 DELETE 请求，删除赞同记录"""
        agree = SuggestionAgree.query.get(agree_id)
        if agree:
            db.session.delete(agree)
            db.session.commit()
            return jsonify({"message": "Agree deleted"}), 204
        else:
            return jsonify({"error": "Agree not found"}), 404

    def put(self, agree_id):
        """处理 PUT 请求，更新赞同记录（例如：取消赞同）"""
        agree = SuggestionAgree.query.get(agree_id)
        if not agree:
            return jsonify({"error": "Agree not found"}), 404

        data = request.json
        try:
            agree.suggestion_id = data.get('suggestion_id', agree.suggestion_id)
            agree.user_id = data.get('user_id', agree.user_id)
            db.session.commit()
            return jsonify({
                "agree_id": agree.agree_id,
                "suggestion_id": agree.suggestion_id,
                "user_id": agree.user_id
            })
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Duplicate agree entry"}), 400


# 将 SuggestionAgreeView 注册到蓝图
suggestion_agree_api = SuggestionAgreeView.as_view('suggestion_agree_api')
suggestion_agree_bp.add_url_rule('/', view_func=suggestion_agree_api, methods=['GET', 'POST'], defaults={'agree_id': None})
suggestion_agree_bp.add_url_rule('/<int:agree_id>', view_func=suggestion_agree_api, methods=['GET', 'PUT', 'DELETE'])