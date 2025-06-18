from app import db
from datetime import datetime

# 订单表
class Order(db.Model):
    __tablename__ = 'order'
    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete="SET NULL"), nullable=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id', ondelete='SET NULL'), nullable=True)
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
"""
DELIMITER $$

CREATE TRIGGER before_delete_order_detail
BEFORE DELETE ON order_detail
FOR EACH ROW
BEGIN
    DECLARE v_order_status VARCHAR(20);

    SELECT o.order_status INTO v_order_status
    FROM `order` o
    WHERE o.order_id = OLD.order_id;

    IF v_order_status IS NOT NULL AND v_order_status NOT IN ('已完成', '订单取消') THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = '订单未完成或未取消，不能删除订单明细';
    END IF;
END$$

DELIMITER ;
"""

"""
DELIMITER $$

CREATE TRIGGER before_delete_order
BEFORE DELETE ON `order`
FOR EACH ROW
BEGIN
    IF OLD.order_status NOT IN ('已完成', '订单取消') THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = '只能删除已完成或已取消的订单';
    END IF;
END$$

DELIMITER ;
"""
