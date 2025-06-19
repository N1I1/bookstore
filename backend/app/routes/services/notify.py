from flask import Blueprint, request, jsonify
from flask_mail import Message
from app import mail, db
from app.models.user import User
from app.models.book import Book
from app.models.userbrowse import UserBrowse
from app.models.userfavorite import UserFavorite
from app.models.usercart import UserCart
from app.models.booktag import book_tag
from datetime import datetime


notify_bp = Blueprint('notify', __name__, url_prefix='/api/notify')

def send_email(book_title, send_infos):
    # 初始化成功发送邮件的计数器
    success_count = 0

    # 遍历 send_infos 列表
    for info in send_infos:
        user_id = info['user_id']
        recommend_type = info['recommend_type']
        recommend_reason = info['recommend_reason']

        # 查询用户表获取邮箱地址
        user = db.session.query(User).filter(User.user_id == user_id).first()
        username = user.username
        # print(username, user.email)s
        if user and user.email:  # 如果用户存在且有邮箱地址
            # 构造邮件内容
            subject = "Your Personalized Recommendation"
            body = f"""
            Dear {username},

            We have a personalized recommendation for you based on your interests.

            Book Title: {book_title}
            Recommendation Type: {recommend_type}
            Recommendation Reason: {recommend_reason}

            Thank you for using our service!

            Best regards,
            Your Team
            """
            # 创建邮件对象
            msg = Message(subject=subject,
                          recipients=[user.email],
                          body=body)
            print(msg.body)
            try:
                # 发送邮件
                mail.send(msg)
                success_count += 1  # 成功发送计数加1
            except Exception as e:
                print(f"Failed to send email to user {user_id}: {e}")
                # 如果发送失败，记录日志（这里使用 Flask 的日志记录功能）
                pass
                

    return success_count

@notify_bp.route('/new_book', methods=['POST'])
def notify_new_book():
    """
    主动触发新书通知（如管理员添加新书后调用，后续可改为触发器？）
    请求体: { "book_id": 123 }
    """
    data = request.json
    book_ids = data.get('book_ids')
    if not book_ids:
        return jsonify({"error": "Missing book_id"}), 400
    
    count = 0
    for book_id in book_ids:

        book = db.session.get(Book, book_id)
    
        if not book:
            return jsonify({"error": "Book not found"}), 404

        # 这里筛选用户
        filter_results = filter_users_by_interests(book_id)

        if not filter_results:
            return jsonify({"error": "There are no eligible users"}), 404
        
        book_title = book.title
        count = count + send_email(book_title, filter_results)
    # print(filter_results)
    return jsonify({"message": f"检测目标用户{len(filter_results)}位，已向{count}位用户发送新书通知"}), 200


def filter_users_by_interests(book_id):

    session = db.session
    # 获取书籍的作者和标签
    book = session.query(Book).filter(Book.book_id == book_id).first()
    if not book:
        return "书籍不存在", None, None

    author = book.author
    tags = book.tags

    # 根据作者筛选用户
    users_by_author = (
        session.query(UserBrowse.user_id)
        .filter(UserBrowse.book_id == book.book_id)
        .union(
            session.query(UserFavorite.user_id)
            .filter(UserFavorite.book_id == book.book_id),
            session.query(UserCart.user_id)
            .filter(UserCart.book_id == book.book_id)
        )
        .distinct()
        .all()
    )

    # 根据标签筛选用户
    users_by_tags = []
    for tag in tags:
        users_by_tag = (
            session.query(UserBrowse.user_id)
            .join(Book, UserBrowse.book_id == Book.book_id)
            .join(book_tag, Book.book_id == book_tag.c.book_id)
            .filter(book_tag.c.tag_id == tag.tag_id)
            .union(
                session.query(UserFavorite.user_id)
                .join(Book, UserFavorite.book_id == Book.book_id)
                .join(book_tag, Book.book_id == book_tag.c.book_id)
                .filter(book_tag.c.tag_id == tag.tag_id),
                session.query(UserCart.user_id)
                .join(Book, UserCart.book_id == Book.book_id)
                .join(book_tag, Book.book_id == book_tag.c.book_id)
                .filter(book_tag.c.tag_id == tag.tag_id)
            )
            .distinct()
            .all()
        )
        users_by_tags.extend(users_by_tag)

    # 合并用户列表并去重
    users_by_author = [user[0] for user in users_by_author]
    users_by_tags = [user[0] for user in users_by_tags]
    all_users = list(set(users_by_author + users_by_tags))

    # 构造返回结果
    result = []
    for user_id in all_users:
        if user_id in users_by_author and user_id in users_by_tags:
            result.append({
                "user_id": user_id,
                "recommend_type": "作者和标签",
                "recommend_reason": f"作者：{author}，标签：{', '.join([tag.name for tag in tags])}"
            })
        elif user_id in users_by_author:
            result.append({
                "user_id": user_id,
                "recommend_type": "作者",
                "recommend_reason": f"作者：{author}"
            })
        elif user_id in users_by_tags:
            result.append({
                "user_id": user_id,
                "recommend_type": "标签",
                "recommend_reason": f"标签：{', '.join([tag.name for tag in tags])}"
            })

    return result
