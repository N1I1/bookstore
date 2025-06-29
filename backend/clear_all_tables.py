from app import db, create_app
from app.models.user import User
from app.models.admin import Admin
from app.models.book import Book
from app.models.order import Order
from app.models.orderdetail import OrderDetail
from app.models.forumpost import ForumPost
from app.models.comment import Comment
from app.models.booktag import book_tag
from app.models.userbrowse import UserBrowse
from app.models.userfavorite import UserFavorite
from app.models.usercart import UserCart
from app.models.tag import Tag
from app.models.complaint import Complaint

def clear_all_tables():
    # 注意顺序，先清子表再清父表，避免外键约束错误
    orders = db.session.query(Order).all()
    for order in orders:
        order.order_status = '已完成'
    db.session.commit()
    db.session.query(UserCart).delete()
    db.session.query(UserBrowse).delete()
    db.session.query(UserFavorite).delete()
    db.session.query(Complaint).delete()
    book_tag.delete()
    db.session.query(OrderDetail).delete()
    db.session.query(Comment).delete()
    db.session.query(ForumPost).delete()
    db.session.query(Order).delete()
    db.session.query(Admin).delete()
    db.session.query(Tag).delete()
    db.session.query(Book).delete()
    db.session.query(User).delete()
    db.session.commit()
    print("All specified tables have been cleared.")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        clear_all_tables()
        print("Database tables cleared successfully.")
