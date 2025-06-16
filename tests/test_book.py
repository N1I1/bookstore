import pytest
from app.models import Book, Admin
from app import db

@pytest.fixture
def admin_user(app):
    """创建管理员用户"""
    admin = Admin(
        username='adminuser',
        password='hashedpassword',
        email='admin@example.com',
        phone='1234567890',
    )
    db.session.add(admin)
    db.session.commit()
    yield admin
    admin_in_db = Admin.query.filter_by(username='adminuser').first()
    if admin_in_db:
        # 删除管理员用户
        db.session.delete(admin_in_db)
        db.session.commit()

@pytest.fixture
def login_admin(client, admin_user):
    """模拟管理员登录"""
    with client.session_transaction() as sess:
        sess['admin_id'] = admin_user.admin_id
        sess['username'] = admin_user.username

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
    book_in_db = Book.query.filter_by(isbn='1234567890123').first()
    if book_in_db:
        # 删除测试图书
        db.session.delete(book_in_db)
        db.session.commit()

def test_get_books_empty(client):
    """测试获取所有书籍（空）"""
    response = client.get('/api/books/')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_create_book_success(client, login_admin):
    """测试成功创建书籍"""
    response = client.post('/api/books/', json={
        "title": "Book1",
        "author": "Author1",
        "isbn": "1111111111111",
        "publisher": "Publisher1",
        "price": 20.0,
        "discount": 0.9,
        "stock": 10,
        "description": "desc"
    })
    assert response.status_code == 201
    assert "book_id" in response.json
    db.session.delete(Book.query.filter_by(isbn="1111111111111").first())
    db.session.commit()

def test_create_book_missing_field(client, login_admin):
    """测试缺少字段"""
    response = client.post('/api/books/', json={
        "title": "Book2"
    })
    assert response.status_code == 400
    assert b"Missing required field" in response.data

def test_create_book_invalid_type(client, login_admin):
    """测试字段类型错误"""
    response = client.post('/api/books/', json={
        "title": "Book3",
        "author": "Author3",
        "isbn": "2222222222222",
        "publisher": "Publisher3",
        "price": "not_a_number",
        "discount": 0.8,
        "stock": 5,
        "description": "desc"
    })
    assert response.status_code == 400
    assert b"Invalid data type" in response.data

def test_create_book_duplicate_isbn(client, login_admin, test_book):
    """测试ISBN重复"""
    response = client.post('/api/books/', json={
        "title": "Book4",
        "author": "Author4",
        "isbn": test_book.isbn,
        "publisher": "Publisher4",
        "price": 30.0,
        "discount": 0.7,
        "stock": 8,
        "description": "desc"
    })
    assert response.status_code == 400
    assert b"unique constraint" in response.data or b"already exists" in response.data

def test_get_single_book(client, test_book):
    """测试获取单本书籍"""
    response = client.get(f'/api/books/{test_book.book_id}')
    assert response.status_code == 200
    assert response.json['book_id'] == test_book.book_id

def test_get_single_book_not_found(client):
    """测试获取不存在的书籍"""
    response = client.get('/api/books/99999')
    assert response.status_code == 404
    assert b"Book not found" in response.data

def test_update_book_success(client, login_admin, test_book):
    """测试成功更新书籍"""
    response = client.put(f'/api/books/{test_book.book_id}', json={
        "title": "Updated Title",
        "price": 99.9
    })
    assert response.status_code == 200
    assert response.json['title'] == "Updated Title"
    assert response.json['price'] == 99.9

def test_update_book_invalid_type(client, login_admin, test_book):
    """测试更新时类型错误"""
    response = client.put(f'/api/books/{test_book.book_id}', json={
        "price": "not_a_number"
    })
    assert response.status_code == 400
    assert b"Invalid data type" in response.data

def test_update_book_not_found(client, login_admin):
    """测试更新不存在的书籍"""
    response = client.put('/api/books/99999', json={
        "title": "No Book"
    })
    assert response.status_code == 404
    assert b"Book not found" in response.data

def test_update_book_duplicate_isbn(client, login_admin, test_book):
    """测试更新ISBN为已存在的ISBN"""
    # 先创建另一本书
    book2 = Book(
        title='Book5',
        author='Author5',
        isbn='5555555555555',
        publisher='Publisher5',
        discount=0.5,
        price=50.0,
        stock=2,
        description='desc'
    )
    db.session.add(book2)
    db.session.commit()
    response = client.put(f'/api/books/{test_book.book_id}', json={
        "isbn": book2.isbn
    })
    assert response.status_code == 400
    assert b"Unique constraint" in response.data or b"already exists" in response.data
    db.session.delete(book2)
    db.session.commit()

def test_delete_book_success(client, login_admin, test_book):
    """测试删除书籍"""
    response = client.delete(f'/api/books/{test_book.book_id}')
    assert response.status_code == 204

def test_delete_book_not_found(client, login_admin):
    """测试删除不存在的书籍"""
    response = client.delete('/api/books/99999')
    assert response.status_code == 404
    assert b"Book not found" in response.data

def test_book_unauthorized(client, test_book):
    """未登录管理员不能增删改"""
    response = client.post('/api/books/', json={
        "title": "Book6",
        "author": "Author6",
        "isbn": "6666666666666",
        "publisher": "Publisher6",
        "price": 60.0,
        "discount": 0.6,
        "stock": 6,
        "description": "desc"
    })
    assert response.status_code == 401
    response = client.put(f'/api/books/{test_book.book_id}', json={
        "title": "Should not update"
    })
    assert response.status_code == 401
    response = client.delete(f'/api/books/{test_book.book_id}')
    assert response.status_code == 401
