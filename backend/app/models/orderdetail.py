from app import db

# 订单明细表
class OrderDetail(db.Model):
    __tablename__ = 'order_detail'
    __table_args__ = (
        db.UniqueConstraint('order_id', 'book_id', name='uix_order_book'),
    )
    detail_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)

    book = db.relationship('Book', backref='order_details', lazy='joined')
