from app import db

# 图书表
class Book(db.Model):
    __tablename__ = 'book'
    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(20), nullable=False, unique=True)
    publisher = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    discount = db.Column(db.Numeric(5, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, default=None)
    image_url = db.Column(db.String(255), default=None)
"""
DELIMITER $$

CREATE TRIGGER before_delete_book
BEFORE DELETE ON book
FOR EACH ROW
BEGIN
    -- 检查是否存在与该书相关的订单明细，且这些订单明细的订单状态不是“已完成”或“订单取消”
    IF EXISTS (
        SELECT 1
        FROM order_detail od
        JOIN `order` o ON od.order_id = o.order_id
        WHERE od.book_id = OLD.book_id
          AND o.order_status NOT IN ('已完成', '订单取消')
    ) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = '该书有关联的未完成订单，不能删除';
    END IF;
END$$

DELIMITER ;
"""
