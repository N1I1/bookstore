from app import db
from datetime import datetime

# 订单表
class Order(db.Model):
    __tablename__ = 'order'
    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'), nullable=False)
    order_status = db.Column(db.Enum('未支付', '已支付', '已发货', '运输中', '已完成', '订单取消', name='order_status'), nullable=False, default='未支付')
    order_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    payment_time = db.Column(db.DateTime, default=None)
    ship_time = db.Column(db.DateTime, default=None)
    get_time = db.Column(db.DateTime, default=None)
    ship_address = db.Column(db.String(255), nullable=False)
    bill_address = db.Column(db.String(255), nullable=False)
    current_address = db.Column(db.String(255), nullable=False)
    shipper_phone = db.Column(db.String(20), nullable=False)
    biller_phone = db.Column(db.String(20), nullable=False)
    remark = db.Column(db.Text, default=None)