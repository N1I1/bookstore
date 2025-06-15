from app import db
from datetime import datetime

# 用户信息表
class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)
    register_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    last_login_time = db.Column(db.DateTime, default=None)
    default_address = db.Column(db.String(255), default=None)

    comments = db.relationship('Comment', back_populates='user')
    posts = db.relationship('ForumPost', back_populates='poster')
