from app import db
from datetime import datetime

# 帖子表
class ForumPost(db.Model):
    __tablename__ = 'forum_post'
    post_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 用户被删除时，帖子仍然保留，但用户会被设置为NULL
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete="SET NULL"), nullable=True)
    # 书被删除时，帖子仍然保留，但书籍信息会被设置为NULL
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id', ondelete='SET NULL'), nullable=True)
    title = db.Column(db.String(255), nullable=False, default="Untitled Post")
    content = db.Column(db.Text, default=None)
    post_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    browse_count = db.Column(db.Integer, nullable=False, default=0)
    is_deleted = db.Column(db.Boolean, default=False)

    comments = db.relationship('Comment', back_populates='forum_post')
    poster = db.relationship('User', back_populates='posts')
