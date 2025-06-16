import pytest
from datetime import datetime
from app.models import User, Book, UserFavorite
from app import db

@pytest.fixture
def test_user(app):
    """创建测试用户"""
    user = User(
        username='favuser',
        password='hashedpassword',
        email='fav@example.com',
        phone='1234567890'
    )
    db.session.add(user)
    db.session.commit()
    yield user
    favorites = UserFavorite.query.filter_by(user_id=user.user_id).all()
    for favorite in favorites:
        db.session.delete(favorite)
    db.session.commit()
    db.session.delete(user)
    db.session.commit()

@pytest.fixture
def test_book(app):
    """创建测试图书"""
    book = Book(
        title='Test Book',
        author='Author',
        isbn='1234567890123',
        publisher='Test Publisher',
        discount=0.1,
        price=10.0,
        stock=5,
        description='This is a test book.'
    )
    db.session.add(book)
    db.session.commit()
    yield book
    favorites = UserFavorite.query.filter_by(book_id=book.book_id).all()
    for favorite in favorites:
        db.session.delete(favorite)
    db.session.commit()
    db.session.delete(book)
    db.session.commit()

@pytest.fixture
def login_user(client, test_user):
    """模拟登录"""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.user_id
        sess['username'] = test_user.username

def test_get_favorites_empty(client, login_user):
    """测试获取空收藏列表"""
    response = client.get('/api/user_favorites/')
    assert response.status_code == 200
    assert response.json == []

def test_add_favorite_success(client, login_user, test_book):
    """测试成功收藏图书"""
    response = client.post('/api/user_favorites/', json={'book_id': test_book.book_id})
    assert response.status_code == 201
    assert response.json['book_id'] == test_book.book_id

def test_add_favorite_duplicate(client, login_user, test_book):
    """测试重复收藏"""
    client.post('/api/user_favorites/', json={'book_id': test_book.book_id})
    response = client.post('/api/user_favorites/', json={'book_id': test_book.book_id})
    assert response.status_code == 400
    assert b'already favorited' in response.data

def test_add_favorite_book_not_found(client, login_user):
    """测试收藏不存在的图书"""
    response = client.post('/api/user_favorites/', json={'book_id': 99999})
    assert response.status_code == 404
    assert b'Book not found' in response.data

def test_add_favorite_missing_book_id(client, login_user):
    """测试收藏缺少book_id"""
    response = client.post('/api/user_favorites/', json={})
    assert response.status_code == 400
    assert b'Missing required field' in response.data

def test_get_favorites_with_data(client, login_user, test_book):
    """测试获取有收藏的列表"""
    client.post('/api/user_favorites/', json={'book_id': test_book.book_id})
    response = client.get('/api/user_favorites/')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert response.json[0]['book_id'] == test_book.book_id

def test_delete_favorite_success(client, login_user, test_book):
    """测试取消收藏成功"""
    client.post('/api/user_favorites/', json={'book_id': test_book.book_id})
    response = client.delete(f'/api/user_favorites/{test_book.book_id}')
    assert response.status_code == 204

def test_delete_favorite_not_found(client, login_user):
    """测试取消不存在的收藏"""
    response = client.delete('/api/user_favorites/99999')
    assert response.status_code == 404
    assert b'Favorite record not found' in response.data

def test_favorite_unauthenticated(client, test_book):
    """未登录用户操作"""
    response = client.get('/api/user_favorites/')
    assert response.status_code == 401
    response = client.post('/api/user_favorites/', json={'book_id': test_book.book_id})
    assert response.status_code == 401
    response = client.delete(f'/api/user_favorites/{test_book.book_id}')
    assert response.status_code == 401
