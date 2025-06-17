import pytest
from app.models.tag import Tag
from app import db
from app.models.book import Book

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
def test_tag(app):
    tag = Tag(name='测试标签')
    db.session.add(tag)
    db.session.commit()
    yield tag
    tag_in_db = Tag.query.filter_by(name='测试标签').first()
    if tag_in_db:
        db.session.delete(tag_in_db)
        db.session.commit()

def test_get_all_tags(client, test_tag):
    response = client.get('/api/tags/')
    assert response.status_code == 200
    data = response.get_json()
    assert any(t['name'] == '测试标签' for t in data)

def test_get_single_tag(client, test_tag):
    response = client.get(f'/api/tags/{test_tag.tag_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == '测试标签'

def test_get_tag_not_found(client):
    response = client.get('/api/tags/99999')
    assert response.status_code == 404

def test_create_tag_success(client, login_admin):
    response = client.post('/api/tags/', json={'name': '新标签'})
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == '新标签'
    # 清理
    tag = Tag.query.filter_by(name='新标签').first()
    if tag:
        db.session.delete(tag)
        db.session.commit()

def test_create_tag_missing_name(client, login_admin):
    response = client.post('/api/tags/', json={})
    assert response.status_code == 400
    assert b"Missing required field" in response.data

def test_create_tag_duplicate(client, login_admin, test_tag):
    response = client.post('/api/tags/', json={'name': test_tag.name})
    assert response.status_code == 400
    assert b"already exists" in response.data

def test_create_tag_unauthorized(client):
    response = client.post('/api/tags/', json={'name': '未授权标签'})
    assert response.status_code == 401

def test_update_tag_success(client, login_admin, test_tag):
    response = client.put(f'/api/tags/{test_tag.tag_id}', json={'name': '更新标签'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == '更新标签'
    # 恢复原名
    test_tag.name = '测试标签'
    db.session.commit()

def test_update_tag_not_found(client, login_admin):
    response = client.put('/api/tags/99999', json={'name': '不存在'})
    assert response.status_code == 404

def test_update_tag_missing_name(client, login_admin, test_tag):
    response = client.put(f'/api/tags/{test_tag.tag_id}', json={})
    assert response.status_code == 400
    assert b"Missing required field" in response.data

def test_update_tag_duplicate_name(client, login_admin, test_tag):
    # 新建一个标签
    tag2 = Tag(name='另一个标签')
    db.session.add(tag2)
    db.session.commit()
    response = client.put(f'/api/tags/{test_tag.tag_id}', json={'name': tag2.name})
    assert response.status_code == 400
    assert b"already exists" in response.data
    db.session.delete(tag2)
    db.session.commit()

def test_update_tag_unauthorized(client, test_tag):
    response = client.put(f'/api/tags/{test_tag.tag_id}', json={'name': '未授权'})
    assert response.status_code == 401

def test_delete_tag_success(client, login_admin):
    tag = Tag(name='待删除标签')
    db.session.add(tag)
    db.session.commit()
    response = client.delete(f'/api/tags/{tag.tag_id}')
    assert response.status_code == 204
    assert db.session.get(Tag, tag.tag_id) is None

def test_delete_tag_not_found(client, login_admin):
    response = client.delete('/api/tags/99999')
    assert response.status_code == 404

def test_delete_tag_unauthorized(client, test_tag):
    response = client.delete(f'/api/tags/{test_tag.tag_id}')
    assert response.status_code == 401

@pytest.fixture
def tag_with_books(app):
    tag = Tag(name='有书标签')
    db.session.add(tag)
    db.session.commit()
    book1 = Book(
        title='书1',
        author='作者1',
        isbn='isbn1',
        publisher='出版社1',
        price=10.0,
        discount=1.0,
        stock=5,
        description='desc1'
    )
    book2 = Book(
        title='书2',
        author='作者2',
        isbn='isbn2',
        publisher='出版社2',
        price=20.0,
        discount=0.8,
        stock=3,
        description='desc2'
    )
    db.session.add(book1)
    db.session.add(book2)
    db.session.commit()
    # 关联
    tag.books.append(book1)
    tag.books.append(book2)
    db.session.commit()
    yield tag, [book1, book2]
    # 清理
    tag.books.clear()
    db.session.delete(book1)
    db.session.delete(book2)
    db.session.delete(tag)
    db.session.commit()

def test_get_books_by_tag(client, tag_with_books):
    tag, books = tag_with_books
    response = client.get(f'/api/tags/{tag.tag_id}/books')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 2
    book_ids = [b['book_id'] for b in data]
    assert books[0].book_id in book_ids
    assert books[1].book_id in book_ids

def test_get_books_by_tag_not_found(client):
    response = client.get('/api/tags/99999/books')
    assert response.status_code == 404
    assert b"Tag not found" in response.data
