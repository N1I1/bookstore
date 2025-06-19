import pytest
from app import db
from app.models.forumpost import ForumPost
from app.models.user import User
from app.models.book import Book

import uuid

@pytest.fixture
def test_user(app):
    unique_str = uuid.uuid4().hex
    unique_email = f"test_{unique_str}@example.com"
    unique_username = f"testuser_{unique_str}"
    user = User(username=unique_username, password='123456', email=unique_email, 
                phone='1234567890')
    db.session.add(user)
    db.session.commit()
    yield user
    ForumPost.query.filter_by(user_id=user.user_id).delete()
    db.session.commit()
    db.session.delete(user)
    db.session.commit()

@pytest.fixture
def login_user(client, test_user):
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.user_id

@pytest.fixture
def test_book(app):
    book = Book(title='Test Book', 
                author='Author', 
                isbn='1234567890', 
                publisher='Test Publisher', 
                price=9.99, 
                discount=0.1,
                stock=100,
                description='Test Description')
    db.session.add(book)
    db.session.commit()
    yield book
    posts = ForumPost.query.filter_by(book_id=book.book_id).all()
    for post in posts:
        db.session.delete(post)
    db.session.commit()
    db.session.delete(book)
    db.session.commit()

@pytest.fixture
def test_post(app, test_user):
    post = ForumPost(user_id=test_user.user_id, title='Test Title', content='Test Content')
    db.session.add(post)
    db.session.commit()
    yield post
    post_in_db = db.session.get(ForumPost, post.post_id)
    if post_in_db:
        db.session.delete(post_in_db)
        db.session.commit()

def test_create_post(client, login_user, test_book):
    response = client.post('/api/forum_posts/', json={
        'title': 'New Post',
        'content': 'Post Content',
        'book_id': test_book.book_id
    })
    assert response.status_code == 201
    assert b"Post created successfully" in response.data

def test_create_post_no_content(client, login_user):
    response = client.post('/api/forum_posts/', json={
        'title': 'No Content'
    })
    assert response.status_code == 400
    assert b"Content is empty" in response.data

def test_get_post(client, login_user, test_post):
    response = client.get(f'/api/forum_posts/{test_post.post_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['title'] == 'Test Title'
    assert data['content'] == 'Test Content'

def test_update_post(client, login_user, test_post, test_book):
    response = client.put(f'/api/forum_posts/{test_post.post_id}', json={
        'title': 'Updated Title',
        'content': 'Updated Content',
        'book_id': test_book.book_id
    })
    assert response.status_code == 200
    assert b"Post updated successfully" in response.data

@pytest.fixture
def another_user(app):
    unique_str = uuid.uuid4().hex
    user = User(username=f"other_{unique_str}", password='123456', email=f"other_{unique_str}@example.com", phone='1234567890')
    db.session.add(user)
    db.session.commit()
    yield user
    db.session.delete(user)
    db.session.commit()

def test_update_post_not_owner(client, test_post, another_user):
    with client.session_transaction() as sess:
        sess['user_id'] = another_user.user_id
    response = client.put(f'/api/forum_posts/{test_post.post_id}', json={
        'title': 'Hack',
        'content': 'Hack'
    })
    assert response.status_code == 403

def test_get_nonexistent_post(client, login_user):
    response = client.get('/api/forum_posts/999999')
    assert response.status_code == 404
    assert b"Post not found" in response.data


def test_delete_post(client, login_user, test_post):
    response = client.delete(f'/api/forum_posts/{test_post.post_id}')
    assert response.status_code == 204
    # 检查逻辑删除
    post = db.session.get(ForumPost, test_post.post_id)
    assert post.is_deleted is True

def test_delete_post_not_owner(client, test_post, another_user):
    with client.session_transaction() as sess:
        sess['user_id'] = another_user.user_id
    response = client.delete(f'/api/forum_posts/{test_post.post_id}')
    assert response.status_code == 403

def test_get_random_posts(client, login_user, test_post):
    response = client.get('/api/forum_posts/get_posts')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert any(post['title'] == 'Test Title' for post in data)

def test_post_with_nonexistent_book(client, login_user):
    response = client.post('/api/forum_posts/', json={
        'title': 'Test',
        'content': 'Test Content',
        'book_id': 999999  # 假设不存在
    })
    assert response.status_code == 404
    assert b"Book not found" in response.data

def test_post_without_logged_in_user(client):
    response = client.post('/api/forum_posts/', json={
        'title': 'Test',
        'content': 'Test Content'
    })
    assert response.status_code == 401
    assert b"User not logged in" in response.data

def test_post_empty_title(client, login_user):
    response = client.post('/api/forum_posts/', json={
        'title': '',
        'content': 'Test Content'
    })
    assert response.status_code == 201
    post_id = response.get_json().get('post_id')
    post_title = db.session.get(ForumPost, post_id).title
    assert post_title == 'Untitled Post'
    assert b"Post created successfully" in response.data

def test_put_without_logged_in_user(client, test_post):
    response = client.put(f'/api/forum_posts/{test_post.post_id}', json={
        'title': 'Updated Title',
        'content': 'Updated Content'
    })
    assert response.status_code == 401
    assert b"User not logged in" in response.data

def test_put_post_not_found(client, login_user):
    response = client.put('/api/forum_posts/999999', json={
        'title': 'Test',
        'content': 'Test'
    })
    assert response.status_code == 404
 
def test_put_post_empty_title(client, login_user, test_post):
    response = client.put(f'/api/forum_posts/{test_post.post_id}', json={
        'title': '',
        'content': 'Test'
    })
    assert response.status_code == 400

def test_put_post_empty_content(client, login_user, test_post):
    response = client.put(f'/api/forum_posts/{test_post.post_id}', json={
        'title': 'Test',
        'content': ''
    })
    assert response.status_code == 400

def test_put_post_nonexistent_book(client, login_user, test_post):
    response = client.put(f'/api/forum_posts/{test_post.post_id}', json={
        'title': 'Test',
        'content': 'Test',
        'book_id': 999999
    })
    assert response.status_code == 404

def test_delete_post_not_found(client, login_user):
    response = client.delete('/api/forum_posts/999999')
    assert response.status_code == 404

# def test_delete_post_not_owner(client, test_post, another_user):
#     with client.session_transaction() as sess:
#         sess['user_id'] = another_user.user_id
#     response = client.delete(f'/api/forum_posts/{test_post.post_id}')
#     assert response.status_code == 403

def test_delete_post_not_logged_in(client, test_post):
    response = client.delete(f'/api/forum_posts/{test_post.post_id}')
    assert response.status_code == 401

def test_get_random_posts_no_posts(client):
    # 先确保没有帖子
    ForumPost.query.delete()
    db.session.commit()
    response = client.get('/api/forum_posts/get_posts')
    assert response.status_code == 404

def test_get_posts_by_book(client, login_user, test_book, test_user):
    # 创建两个帖子，均关联到 test_book
    post1 = ForumPost(user_id=test_user.user_id, book_id=test_book.book_id, title='Book Post 1', content='Content 1')
    post2 = ForumPost(user_id=test_user.user_id, book_id=test_book.book_id, title='Book Post 2', content='Content 2')
    db.session.add_all([post1, post2])
    db.session.commit()

    response = client.get(f'/api/forum_posts/by_book/{test_book.book_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    titles = [post['title'] for post in data]
    assert 'Book Post 1' in titles
    assert 'Book Post 2' in titles

    # 清理
    db.session.delete(post1)
    db.session.delete(post2)
    db.session.commit()

def test_get_random_posts_no_posts(client):
    # 先确保没有帖子
    ForumPost.query.delete()
    db.session.commit()
    response = client.get('/api/forum_posts/by_book/999999')
    assert response.status_code == 404

def test_get_posts_by_user(client, login_user, test_user, test_book):
    # 创建两个帖子，均关联到 test_user
    post1 = ForumPost(user_id=test_user.user_id, book_id=test_book.book_id, title='User Post 1', content='Content 1')
    post2 = ForumPost(user_id=test_user.user_id, book_id=test_book.book_id, title='User Post 2', content='Content 2')
    db.session.add_all([post1, post2])
    db.session.commit()

    # 只获取当前登录用户的帖子
    response = client.get(f'/api/forum_posts/by_user/')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    # 只包含当前用户的帖子
    titles = [post['title'] for post in data]
    assert 'User Post 1' in titles
    assert 'User Post 2' in titles

    # 清理
    db.session.delete(post1)
    db.session.delete(post2)
    db.session.commit()

def test_get_posts_by_user_no_posts(client, login_user, another_user):
    response = client.get(f'/api/forum_posts/by_user/')
    assert response.status_code == 404
    assert b"No posts found for this user" in response.data
