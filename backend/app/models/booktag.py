from app import db

book_tag = db.Table(
    'book_tag',
    # 书被删除时，书与标签的关联关系 也会被删除
    db.Column('book_id', db.Integer, db.ForeignKey('book.book_id', ondelete='CASCADE'), primary_key=True),
    # 标签被删除时，书与标签的关联关系 也会被删除
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.tag_id', ondelete='CASCADE'), primary_key=True)
)
