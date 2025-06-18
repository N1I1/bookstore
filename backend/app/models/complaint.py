from app import db
from datetime import datetime

# 投诉表
class Complaint(db.Model):
    __tablename__ = 'complaint'
    complaint_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    complaint_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    status = db.Column(db.Enum('待处理', '已受理', '已解决', name='complaint_status'), nullable=False, default='待处理')
    result = db.Column(db.Text, default=None)
