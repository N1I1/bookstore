import pytest
from app.models import Book
from app.routes.views.search_books import book_search_bp

def test_search_books_success(client):
    # 测试成功查询
    # 查询 "Hunger Games"
    response = client.post('/api/search_books/search_books', json={'query': 'Hunger Games'})
    assert response.status_code == 200
    data = response.json
    assert 'message' in data
    assert 'book_ids' in data
    assert len(data['book_ids']) == 3 
    assert data['book_ids'][0] == 1

    # 查询 "Harry Potter"
    response = client.post('/api/search_books/search_books', json={'query': 'Harry Potter'})
    assert response.status_code == 200
    data = response.json
    assert 'message' in data
    assert 'book_ids' in data
    assert len(data['book_ids']) == 7  
    assert data['book_ids'][0] == 2

    # 查找 isbn 439023483
    response = client.post('/api/search_books/search_books', json={'query': '439023483'})
    assert response.status_code == 200
    data = response.json
    assert 'message' in data
    assert 'book_ids' in data
    assert len(data['book_ids']) == 1
    assert data['book_ids'][0] == 1

    # 查找 作者 J.K. Rowling
    response = client.post('/api/search_books/search_books', json={'query': 'J.K. Rowling'})
    assert response.status_code == 200
    data = response.json
    assert 'message' in data
    assert 'book_ids' in data
    assert len(data['book_ids']) == 7
    assert data['book_ids'][0] == 2

    # 查找出版社 Wiley
    response = client.post('/api/search_books/search_books', json={'query': 'Wiley'})
    assert response.status_code == 200
    data = response.json
    assert 'message' in data
    assert 'book_ids' in data
    assert len(data['book_ids']) == 4
    assert data['book_ids'][0] == 4


def test_search_books_empty_result(client):
    # 测试查询结果为空
    response = client.post('/api/search_books/search_books', json={'query': 'Nonexistent Book'})
    assert response.status_code == 404
    data = response.json
    assert 'message' in data
    assert data['message'] == 'No books found'

def test_search_books_missing_query(client):
    # 测试缺失查询参数
    response = client.post('/api/search_books/search_books', json={})
    assert response.status_code == 400
    data = response.json
    assert 'error' in data
    assert data['error'] == 'Missing search query'