import pytest
from werkzeug.security import generate_password_hash
from app.models import User
from app import db

@pytest.fixture
def test_user(app):
    """创建一个测试用户"""
    user = User(
        username='testuser',
        password=generate_password_hash('testpassword'),
        email='test@example.com',
        phone='1234567890'
    )
    db.session.add(user)
    db.session.commit()
    yield user
    db.session.delete(user)
    db.session.commit()

def test_login_success(client, test_user):
    """测试登录成功"""
    response = client.post('/api/login/', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    assert response.status_code == 200
    assert b'Login successful' in response.data

def test_login_wrong_password(client, test_user):
    """测试密码错误"""
    response = client.post('/api/login/', json={
        'username': 'testuser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert b'Invalid username or password' in response.data

def test_login_user_not_exist(client):
    """测试用户不存在"""
    response = client.post('/api/login/', json={
        'username': 'nouser',
        'password': 'nopassword'
    })
    assert response.status_code == 401
    assert b'Invalid username or password' in response.data

def test_login_missing_fields(client):
    """测试缺少字段"""
    response = client.post('/api/login/', json={
        'username': 'testuser'
    })
    assert response.status_code == 400
    assert b'Missing username or password' in response.data

def test_log_out(client, test_user):
    """测试登出"""
    # 首先登录
    client.post('/api/login/', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    
    # 然后登出
    response = client.post('/api/login/logout')
    assert response.status_code == 200
    assert b'Logout successful' in response.data

    # 确认会话已清除
    with client.session_transaction() as session:
        assert 'user_id' not in session
        assert 'username' not in session


def test_login_server_error(client, test_user, monkeypatch):
    def fake_commit():
        raise Exception("DB error!")
    monkeypatch.setattr("app.routes.auth.login.db.session.commit", fake_commit)

    response = client.post('/api/login/', json={
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 500
    assert b"Server error" in response.data