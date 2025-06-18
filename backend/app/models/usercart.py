from app import db
from datetime import datetime

# 用户购物车表
class UserCart(db.Model):
    __tablename__ = 'user_cart'
    cart_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    #  用户被删除时，级联删除用户购物车
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete="CASCADE"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id', ondelete='SET NULL'), nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    add_time = db.Column(db.DateTime, nullable=False, default=datetime.now)

    book = db.relationship('Book', backref='cart_items')
