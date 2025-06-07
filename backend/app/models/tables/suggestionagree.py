from app import db
from datetime import datetime

# 建议赞同关系表
class SuggestionAgree(db.Model):
    __tablename__ = 'suggestion_agree'
    agree_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    suggestion_id = db.Column(db.Integer, db.ForeignKey('suggestion.suggestion_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
