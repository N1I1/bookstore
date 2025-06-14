import pytest
from app.models import Admin
from werkzeug.security import generate_password_hash

@pytest.fixture
def test_admin(app):
    admin = Admin(
        username='adminuser',
        password=generate_password_hash('adminpass'),
        email='admin@example.com',
        phone='1234567890'
    )
    from app import db
    db.session.add(admin)
    db.session.commit()
    yield admin
    db.session.delete(admin)
    db.session.commit()

def test_admin_login_success(client, test_admin):
    response = client.post('/api/admin/login/', json={
        'username': 'adminuser',
        'password': 'adminpass'
    })
    assert response.status_code == 200
    assert b'Login successful' in response.data

def test_admin_login_wrong_password(client, test_admin):
    response = client.post('/api/admin/login/', json={
        'username': 'adminuser',
        'password': 'wrongpass'
    })
    assert response.status_code == 401
    assert b'Invalid username or password' in response.data

def test_admin_login_user_not_exist(client):
    response = client.post('/api/admin/login/', json={
        'username': 'noadmin',
        'password': 'nopass'
    })
    assert response.status_code == 401
    assert b'Invalid username or password' in response.data

def test_admin_login_missing_fields(client):
    response = client.post('/api/admin/login/', json={
        'username': 'adminuser'
    })
    assert response.status_code == 400
    assert b'Missing username or password' in response.data

def test_admin_logout(client, test_admin):
    # 首先登录
    client.post('/api/admin/login/', json={
        'username': 'adminuser',
        'password': 'adminpass'
    })
    
    # 然后登出
    response = client.post('/api/admin/login/logout')
    assert response.status_code == 200
    assert b'Logout successful' in response.data

    # 检查会话是否清除
    with client.session_transaction() as session:
        assert 'admin_user_id' not in session
        assert 'admin_username' not in session