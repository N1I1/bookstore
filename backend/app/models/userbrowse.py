from app import db
from datetime import datetime

# 用户浏览表
class UserBrowse(db.Model):
    __tablename__ = 'user_browse'
    browse_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 用户被删除时，级联删除用户浏览记录
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete="CASCADE"), nullable=False)
    # 书被删除时，浏览记录中的书籍ID设置为NULL
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id', ondelete='SET NULL'), nullable=True)
    browse_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
