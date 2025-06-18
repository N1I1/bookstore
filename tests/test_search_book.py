import pytest
from app.models import Book
from app.routes.views.search_books import book_search_bp
from app import db

from app import create_app

@pytest.fixture
def app():
    app = create_app()
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture()
def test_books():
    # 创建测试数据
    books = [
        Book(title="The Hunger Games", author="Suzanne Collins", isbn="9780439023481", publisher="Scholastic", price=12.99, discount=1.00, stock=100, description="Book 1 of the Hunger Games series.", image_url="http://example.com/hunger_games.jpg"),
        Book(title="Catching Fire", author="Suzanne Collins", isbn="9780439023482", publisher="Scholastic", price=14.99, discount=1.00, stock=100, description="Book 2 of the Hunger Games series.", image_url="http://example.com/catching_fire.jpg"),
        Book(title="Mockingjay", author="Suzanne Collins", isbn="9780439023483", publisher="Scholastic", price=16.99, discount=1.00, stock=100, description="Book 3 of the Hunger Games series.", image_url="http://example.com/mockingjay.jpg"),
        Book(title="Harry Potter and the Sorcerer's Stone", author="J.K. Rowling", isbn="9780439554930", publisher="Bloomsbury", price=10.99, discount=1.00, stock=150, description="Book 1 of the Harry Potter series.", image_url="http://example.com/hp1.jpg"),
        Book(title="Harry Potter and the Chamber of Secrets", author="J.K. Rowling", isbn="9780439064866", publisher="Bloomsbury", price=11.99, discount=1.00, stock=150, description="Book 2 of the Harry Potter series.", image_url="http://example.com/hp2.jpg"),
        Book(title="Harry Potter and the Prisoner of Azkaban", author="J.K. Rowling", isbn="9780439136365", publisher="Bloomsbury", price=12.99, discount=1.00, stock=150, description="Book 3 of the Harry Potter series.", image_url="http://example.com/hp3.jpg"),
        Book(title="Python Programming", author="John Doe", isbn="9781234567890", publisher="Wiley", price=29.99, discount=0.90, stock=50, description="A book about Python programming.", image_url="http://example.com/python.jpg"),
        Book(title="Flask Web Development", author="Jane Doe", isbn="9780987654321", publisher="Wiley", price=24.99, discount=0.85, stock=30, description="A book about Flask web development.", image_url="http://example.com/flask.jpg"),
        Book(title="Hunger Games: The Final Chapter", author="Suzanne Collins", isbn="9780439023484", publisher="Scholastic", price=18.99, discount=1.00, stock=100, description="A new book in the Hunger Games series.", image_url="http://example.com/hunger_games_final.jpg")
    ]
    return books

def test_search_books_success(client, test_books):
    # 插入测试数据
    with client.application.app_context():
        db.session.add_all(test_books)
        db.session.commit()

    # 测试成功查询
    # 查询 "Hunger Games"
    response = client.post('/api/search_books/', json={'query': 'Hunger Games'})
    assert response.status_code == 200
    data = response.json
    assert 'message' in data
    assert 'books' in data
    assert len(data['books']) == 2

    # 查询 "Harry Potter"
    response = client.post('/api/search_books/', json={'query': 'Harry Potter'})
    assert response.status_code == 200
    data = response.json
    assert 'message' in data
    assert 'books' in data
    assert len(data['books']) == 3

    # 查找 isbn 439023483
    response = client.post('/api/search_books/', json={'query': '439023483'})
    assert response.status_code == 200
    data = response.json
    assert 'message' in data
    assert 'books' in data
    assert len(data['books']) == 1

    # 查找 作者 J.K. Rowling
    response = client.post('/api/search_books/', json={'query': 'J.K. Rowling'})
    assert response.status_code == 200
    data = response.json
    assert 'message' in data
    assert 'books' in data
    assert len(data['books']) == 3

    # 查找出版社 Wiley
    response = client.post('/api/search_books/', json={'query': 'Wiley'})
    assert response.status_code == 200
    data = response.json
    assert 'message' in data
    assert 'books' in data
    assert len(data['books']) == 2

    # 删除测试数据
    with client.application.app_context():
        db.session.query(Book).delete()
        db.session.commit()

def test_search_books_empty_result(client, test_books):
    # 插入测试数据
    with client.application.app_context():
        db.session.query(Book).delete()
        db.session.add_all(test_books)
        db.session.commit()

    # 测试查询结果为空
    response = client.post('/api/search_books/', json={'query': 'Nonexistent Book'})
    assert response.status_code == 404
    data = response.json
    assert 'message' in data
    assert data['message'] == 'No books found'

    # 删除测试数据
    with client.application.app_context():
        db.session.query(Book).delete()
        db.session.commit()

def test_search_books_missing_query(client, test_books):
    # 插入测试数据
    with client.application.app_context():
        db.session.add_all(test_books)
        db.session.commit()

    # 测试缺失查询参数
    response = client.post('/api/search_books/', json={})
    assert response.status_code == 400
    data = response.json
    assert 'error' in data
    assert data['error'] == 'Missing search query'

    # 删除测试数据
    with client.application.app_context():
        db.session.query(Book).delete()
        db.session.commit()
