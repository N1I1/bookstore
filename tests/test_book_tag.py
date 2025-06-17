import pytest
from app import db
from app.models.book import Book
from app.models.tag import Tag

@pytest.fixture
def admin_user(app):
    from app.models.admin import Admin
    import uuid
    unique_str = uuid.uuid4().hex
    admin = Admin(
        username=f'admin_{unique_str}',
        password='adminpass',
        email=f'admin_{unique_str}@example.com',
        phone='1234567890',
    )
    db.session.add(admin)
    db.session.commit()
    yield admin
    admin_in_db = Admin.query.filter_by(username=admin.username).first()
    if admin_in_db:
        db.session.delete(admin_in_db)
        db.session.commit()

@pytest.fixture
def login_admin(client, admin_user):
    with client.session_transaction() as sess:
        sess['admin_id'] = admin_user.admin_id
        sess['username'] = admin_user.username

@pytest.fixture
def test_book(app):
    book = Book(
        title='BookTag测试书',
        author='作者',
        isbn='9999999999999',
        publisher='出版社',
        price=10.0,
        discount=1.0,
        stock=5,
        description='desc'
    )
    db.session.add(book)
    db.session.commit()
    yield book
    db.session.delete(book)
    db.session.commit()

@pytest.fixture
def test_tag(app):
    tag = Tag(name='BookTag测试标签')
    db.session.add(tag)
    db.session.commit()
    yield tag
    db.session.delete(tag)
    db.session.commit()

def test_create_booktag_success(client, login_admin, test_book, test_tag):
    response = client.post('/api/booktags/', json={
        'book_id': test_book.book_id,
        'tag_id': test_tag.tag_id
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['book_id'] == test_book.book_id
    assert data['tag_id'] == test_tag.tag_id

def test_create_booktag_duplicate(client, login_admin, test_book, test_tag):
    # 先插入一次
    client.post('/api/booktags/', json={
        'book_id': test_book.book_id,
        'tag_id': test_tag.tag_id
    })
    # 再插入一次
    response = client.post('/api/booktags/', json={
        'book_id': test_book.book_id,
        'tag_id': test_tag.tag_id
    })
    assert response.status_code == 400
    assert b"Duplicate book tag" in response.data

def test_create_booktag_missing_fields(client, login_admin):
    response = client.post('/api/booktags/', json={})
    assert response.status_code == 400
    assert b"Missing required fields" in response.data

def test_create_booktag_unauthorized(client, test_book, test_tag):
    response = client.post('/api/booktags/', json={
        'book_id': test_book.book_id,
        'tag_id': test_tag.tag_id
    })
    assert response.status_code == 401

def test_update_booktag_success(client, login_admin, test_book, test_tag, app):
    # 新建一个标签
    tag2 = Tag(name='BookTag新标签')
    db.session.add(tag2)
    db.session.commit()
    # 先插入原关联
    client.post('/api/booktags/', json={
        'book_id': test_book.book_id,
        'tag_id': test_tag.tag_id
    })
    # 更新为新标签
    response = client.put('/api/booktags/', json={
        'book_id': test_book.book_id,
        'tag_id': test_tag.tag_id,
        'new_tag_id': tag2.tag_id
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['tag_id'] == tag2.tag_id
    # 清理
    db.session.delete(tag2)
    db.session.commit()

def test_update_booktag_not_found(client, login_admin, test_book, test_tag):
    response = client.put('/api/booktags/', json={
        'book_id': test_book.book_id,
        'tag_id': 99999,
        'new_tag_id': test_tag.tag_id
    })
    assert response.status_code == 404
    assert b"Book tag relation not found" in response.data

def test_update_booktag_duplicate(client, login_admin, test_book, test_tag, app):
    # 新建两个标签
    tag2 = Tag(name='BookTag新标签2')
    db.session.add(tag2)
    db.session.commit()
    # 插入两个关联
    client.post('/api/booktags/', json={
        'book_id': test_book.book_id,
        'tag_id': test_tag.tag_id
    })
    client.post('/api/booktags/', json={
        'book_id': test_book.book_id,
        'tag_id': tag2.tag_id
    })
    # 尝试把 test_tag 改为 tag2（已存在）
    response = client.put('/api/booktags/', json={
        'book_id': test_book.book_id,
        'tag_id': test_tag.tag_id,
        'new_tag_id': tag2.tag_id
    })
    assert response.status_code == 400
    assert b"Duplicate book tag" in response.data
    db.session.delete(tag2)
    db.session.commit()

def test_update_booktag_missing_fields(client, login_admin):
    response = client.put('/api/booktags/', json={})
    assert response.status_code == 400
    assert b"Missing required fields" in response.data

def test_update_booktag_unauthorized(client, test_book, test_tag):
    response = client.put('/api/booktags/', json={
        'book_id': test_book.book_id,
        'tag_id': test_tag.tag_id,
        'new_tag_id': test_tag.tag_id
    })
    assert response.status_code == 401

def test_delete_booktag_success(client, login_admin, test_book, test_tag):
    # 先插入
    client.post('/api/booktags/', json={
        'book_id': test_book.book_id,
        'tag_id': test_tag.tag_id
    })
    response = client.delete('/api/booktags/', json={
        'book_id': test_book.book_id,
        'tag_id': test_tag.tag_id
    })
    assert response.status_code == 204

def test_delete_booktag_not_found(client, login_admin, test_book, test_tag):
    response = client.delete('/api/booktags/', json={
        'book_id': test_book.book_id,
        'tag_id': 99999
    })
    assert response.status_code == 404

def test_delete_booktag_missing_fields(client, login_admin):
    response = client.delete('/api/booktags/', json={})
    assert response.status_code == 400
    assert b"Missing required fields" in response.data

def test_delete_booktag_unauthorized(client, test_book, test_tag):
    response = client.delete('/api/booktags/', json={
        'book_id': test_book.book_id,
        'tag_id': test_tag.tag_id
    })
    assert response.status_code == 401
