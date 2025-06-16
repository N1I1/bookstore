from app.models.booktag import book_tag
from app import db

class Tag(db.Model):
    __tablename__ = 'tag'
    tag_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    books = db.relationship('Book', secondary=book_tag, backref=db.backref('tags', lazy='dynamic'))

    def __repr__(self):
        return f'<Tag {self.name}>'
