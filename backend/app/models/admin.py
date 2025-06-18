from app import db
from datetime import datetime

# 管理员信息表
class Admin(db.Model):
    __tablename__ = 'admin'
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)
    register_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    last_login_time = db.Column(db.DateTime, default=None)
