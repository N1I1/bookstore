from app import db
from datetime import datetime

# 用户收藏表
class UserFavorite(db.Model):
    __tablename__ = 'user_favorite'
    favorite_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 用户被删除时，级联删除用户收藏
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete="CASCADE"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id', ondelete='SET NULL'), nullable=True)
    favorite_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
