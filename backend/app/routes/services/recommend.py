from flask import  Blueprint, request, jsonify, session

from app import db, app
from app.models.book import Book
from app.models.userbrowse import UserBrowse

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401
    # 1. 获取用户最近浏览/购买的类别
    recent_browses = UserBrowse.query.filter_by(user_id=user_id).order_by(UserBrowse.browse_time.desc()).limit(10).all()
    categories = [browse.book.category for browse in recent_browses if browse.book]
    # 2. 统计最常出现的类别
    from collections import Counter
    if not categories:
        # 没有浏览历史，推荐全站热门新书
        books = Book.query.order_by(Book.publish_time.desc()).limit(10).all()
    else:
        top_category = Counter(categories).most_common(1)[0][0]
        # 3. 推荐该类别下最新的书
        books = Book.query.filter_by(category=top_category).order_by(Book.publish_time.desc()).limit(10).all()
    # 4. 返回推荐书籍
    result = [{
        "book_id": b.book_id,
        "title": b.title,
        "author": b.author,
        "category": b.category,
        "publish_time": b.publish_time.isoformat()
    } for b in books]
    return jsonify(result)
