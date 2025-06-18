from app import db
from datetime import datetime

# 评论表
class Comment(db.Model):
    __tablename__ = 'comment'
    comment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('forum_post.post_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete="SET NULL"), nullable=True)
    content = db.Column(db.Text, default=None)
    comment_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    parent_comment_id = db.Column(db.Integer, db.ForeignKey('comment.comment_id', ondelete='CASCADE'), default=None, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)

    # Relationships
    forum_post = db.relationship('ForumPost', back_populates='comments')
    user = db.relationship('User', back_populates='comments')
    parent_comment = db.relationship('Comment', remote_side=[comment_id], back_populates='replies')
    replies = db.relationship(
        'Comment',
        back_populates='parent_comment',
        cascade="all, delete-orphan"
    )
