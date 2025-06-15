from app import db
from datetime import datetime

# 帖子表
class ForumPost(db.Model):
    __tablename__ = 'forum_post'
    post_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'), default=None)
    content = db.Column(db.Text, default=None)
    post_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    browse_count = db.Column(db.Integer, nullable=False, default=0)

    comments = db.relationship('Comment', back_populates='forum_post')