from app import db
from datetime import datetime

# 评论表
class Comment(db.Model):
    __tablename__ = 'comment'
    comment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('forum_post.post_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    content = db.Column(db.Text, default=None)
    comment_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    parent_comment_id = db.Column(db.Integer, db.ForeignKey('comment.comment_id'), default=None)
