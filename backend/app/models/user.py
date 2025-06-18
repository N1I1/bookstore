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

"""
DELIMITER $$

CREATE TRIGGER before_delete_user
BEFORE DELETE ON user
FOR EACH ROW
BEGIN
    -- 检查该用户是否有未完成或未取消的订单
    IF EXISTS (
        SELECT 1
        FROM `order`
        WHERE user_id = OLD.user_id
          AND order_status NOT IN ('已完成', '订单取消')
    ) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = '该用户有关联的未完成订单，不能删除';
    END IF;
END$$

DELIMITER ;
"""
