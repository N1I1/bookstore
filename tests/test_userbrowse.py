import pytest
from app import db
from app.models.user import User
from app.models.book import Book
from app.models.userbrowse import UserBrowse

@pytest.fixture
def test_user(app):
    import uuid
    unique_str = uuid.uuid4().hex
    user = User(
        username=f'testuser_{unique_str}',
        password='123456',
        email=f'test_{unique_str}@example.com',
        phone='1234567890'
    )
    db.session.add(user)
    db.session.commit()
    yield user
    user_in_db = db.session.get(User, user.user_id)
    if user_in_db:
        db.session.delete(user_in_db)
        db.session.commit()

@pytest.fixture
def login_user(client, test_user):
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.user_id
    return test_user

@pytest.fixture
def test_book(app):
    import uuid
    unique_str = uuid.uuid4().hex
    book = Book(
        title=f'Test Book {unique_str}',
        author='Author',
        isbn=f'ISBN{unique_str[:10]}',
        publisher='Publisher',
        price=19.99,
        discount=0.1,
        stock=100,
        description='This is a test book description.'
    )
    db.session.add(book)
    db.session.commit()
    yield book
    book_in_db = db.session.get(Book, book.book_id)
    UserBrowse.query.filter_by(book_id=book.book_id).delete()
    db.session.commit()
    if book_in_db:
        db.session.delete(book_in_db)
        db.session.commit()

@pytest.fixture
def test_browse(app, test_user, test_book):
    browse = UserBrowse(user_id=test_user.user_id, book_id=test_book.book_id)
    db.session.add(browse)
    db.session.commit()
    yield browse
    browse_in_db = db.session.get(UserBrowse, browse.browse_id)
    if browse_in_db:
        db.session.delete(browse_in_db)
        db.session.commit()

def test_create_browse(client, login_user, test_book):
    response = client.post('/api/user_browse/', json={
        'book_id': test_book.book_id
    })
    assert response.status_code == 200 or response.status_code == 201
    data = response.get_json()
    assert data['book_id'] == test_book.book_id
    assert data['user_id'] == login_user.user_id

def test_create_browse_not_logged_in(client, test_book):
    response = client.post('/api/user_browse/', json={
        'book_id': test_book.book_id
    })
    assert response.status_code == 401

def test_create_browse_missing_book_id(client, login_user):
    response = client.post('/api/user_browse/', json={})
    assert response.status_code == 400

def test_get_browse(client, login_user, test_browse):
    response = client.get(f'/api/user_browse/{test_browse.browse_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['browse_id'] == test_browse.browse_id

def test_get_browse_not_found(client, login_user):
    response = client.get('/api/user_browse/999999')
    assert response.status_code == 404 or  response.status_code == 403

def test_delete_browse(client, login_user, test_browse):
    response = client.delete(f'/api/user_browse/{test_browse.browse_id}')
    assert response.status_code == 204
    # 检查数据库中已删除
    browse = db.session.get(UserBrowse, test_browse.browse_id)
    assert browse is None

def test_delete_browse_not_found(client, login_user):
    response = client.delete('/api/user_browse/999999')
    assert response.status_code == 404 or  response.status_code == 403

def test_delete_browse_not_logged_in(client, test_browse):
    response = client.delete(f'/api/user_browse/{test_browse.browse_id}')
    assert response.status_code == 401

@pytest.fixture
def another_user(app):
    import uuid
    unique_str = uuid.uuid4().hex
    user = User(
        username=f'another_{unique_str}',
        password='abcdef',
        email=f'another_{unique_str}@example.com',
        phone='0987654321'
    )
    db.session.add(user)
    db.session.commit()
    yield user
    db.session.delete(user)
    db.session.commit()

def test_delete_browse_forbidden(client, test_browse, another_user):
    with client.session_transaction() as sess:
        sess['user_id'] = another_user.user_id
    response = client.delete(f'/api/user_browse/{test_browse.browse_id}')
    assert response.status_code == 403 or  response.status_code == 404

import time

def test_create_browse_updates_time(client, login_user, test_book):
    # 第一次创建
    response1 = client.post('/api/user_browse/', json={'book_id': test_book.book_id})
    assert response1.status_code in (200, 201)
    data1 = response1.get_json()
    old_time = data1['browse_time']

    # 等待一小会儿，确保时间有差异
    import time
    time.sleep(1)

    # 再次创建同样的记录，应更新时间
    response2 = client.post('/api/user_browse/', json={'book_id': test_book.book_id})
    assert response2.status_code in (200, 201)
    data2 = response2.get_json()
    new_time = data2['browse_time']

    assert new_time > old_time

def test_get_browse_not_logged_in(client, test_browse):
    response = client.get(f'/api/user_browse/{test_browse.browse_id}')
    assert response.status_code == 401
    assert b"User not logged in" in response.data

def test_get_user_browses(client, login_user, test_book):
    # 先创建两条浏览记录
    client.post('/api/user_browse/', json={'book_id': test_book.book_id})
    client.post('/api/user_browse/', json={'book_id': test_book.book_id})  # 再次访问，更新时间

    response = client.get(f'/api/user_browse/user/{login_user.user_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]['user_id'] == login_user.user_id
    assert 'browse_time' in data[0]

def test_get_user_browses_not_logged_in(client, test_user):
    response = client.get(f'/api/user_browse/user/{test_user.user_id}')
    assert response.status_code == 401

def test_get_user_browses_forbidden(client, test_user, another_user):
    with client.session_transaction() as sess:
        sess['user_id'] = another_user.user_id
    response = client.get(f'/api/user_browse/user/{test_user.user_id}')
    assert response.status_code == 403
