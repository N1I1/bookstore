from flask import Blueprint, request, jsonify
from flask_mail import Message
from app import mail, db
from app.models.user import User
from app.models.book import Book

notify_bp = Blueprint('notify', __name__, url_prefix='/api/notify')

def send_new_book_email(to_email, book_title, book_url=None):
    subject = f"新书上架通知：《{book_title}》"
    body = f"""您好，

您关注的类型有新书《{book_title}》上架啦！

{f"点击这里查看详情：{book_url}\n" if book_url else ""}
感谢您对我们的支持！

—— 网上书店团队
"""
    msg = Message(
        subject=subject,
        recipients=[to_email],
        body=body
    )
    mail.send(msg)

def dummy_send_email(to_email, book_title):
    """
    模拟发送邮件的函数
    实际应用中应使用 Flask-Mail 或其他邮件服务
    """
    print(f"Sending email to {to_email} about new book: {book_title}")

@notify_bp.route('/new_book', methods=['POST'])
def notify_new_book():
    """
    主动触发新书通知（如管理员添加新书后调用，后续可改为触发器？）
    请求体: { "book_id": 123 }
    """
    data = request.json
    book_id = data.get('book_id')
    if not book_id:
        return jsonify({"error": "Missing book_id"}), 400

    book = db.session.get(Book, book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    # 这里筛选用户
    users = User.query.all()  # 通知所有用户！！

    for user in users:
        dummy_send_email(user.email, "test book title")

    return jsonify({"message": f"已向{len(users)}位用户发送新书通知"}), 200
