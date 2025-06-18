from app import db
from datetime import datetime

# 订单表
class Order(db.Model):
    __tablename__ = 'order'
    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 管理员被删除时，设置为NULL
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete='SET NULL'), nullable=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'), nullable=True)
    order_status = db.Column(db.Enum('未支付', '已支付', '已发货', '已完成', '订单取消', name='order_status'), nullable=False, default='未支付')
    order_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    payment_time = db.Column(db.DateTime, default=None)
    ship_time = db.Column(db.DateTime, default=None)
    get_time = db.Column(db.DateTime, default=None)
    ship_address = db.Column(db.String(255), nullable=True)
    bill_address = db.Column(db.String(255), nullable=False)
    current_address = db.Column(db.String(255), nullable=True)
    shipper_phone = db.Column(db.String(20), nullable=True)
    biller_phone = db.Column(db.String(20), nullable=False)
    remark = db.Column(db.Text, default=None)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00) # Total amount of the order
    is_deleted = db.Column(db.Boolean, default=False)  # 软删除

    # 删除订单时，级联删除订单详情
    order_details = db.relationship('OrderDetail', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    user = db.relationship('User', backref='orders', lazy='joined')
