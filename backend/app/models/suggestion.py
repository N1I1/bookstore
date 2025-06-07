from app import db
from datetime import datetime

# 建议表
class Suggestion(db.Model):
    __tablename__ = 'suggestion'
    suggestion_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    suggestion_time = db.Column(db.DateTime, nullable=False, default=datetime.now)