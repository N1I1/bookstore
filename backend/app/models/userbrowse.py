from app import db
from datetime import datetime

# 用户浏览表
class UserBrowse(db.Model):
    __tablename__ = 'user_browse'
    browse_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'), nullable=False)
    browse_time = db.Column(db.DateTime, nullable=False, default=datetime.now)