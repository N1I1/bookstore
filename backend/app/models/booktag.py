from app import db
from datetime import datetime

# 图书标签表
class BookTag(db.Model):
    __tablename__ = 'book_tag'
    book_tag_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'), nullable=False)
    tag = db.Column(db.String(50), nullable=False)
