import pytest
from app import db
from app.models.user import User

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
    user_in_db = db.session.get(User, user.user_id)
    if user_in_db:
        db.session.delete(user_in_db)
        db.session.commit()

def test_get_user_info(client, login_user):
    response = client.get('/api/users/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['username'].startswith('testuser_')
    assert data['email'].startswith('test_')

def test_get_user_info_not_logged_in(client, test_user):
    response = client.get('/api/users/')
    assert response.status_code == 401

def test_update_user_info(client, login_user):
    response = client.put('/api/users/', json={
        'username': 'updateduser',
        'email': 'updated@example.com',
        'phone': '1112223333',
        'default_address': 'New Address'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == "User updated successfully"
    user = db.session.get(User, login_user.user_id)
    assert user.username == 'updateduser'
    assert user.email == 'updated@example.com'
    assert user.phone == '1112223333'
    assert user.default_address == 'New Address'

def test_update_user_info_not_logged_in(client, test_user):
    response = client.put('/api/users/', json={
        'username': 'hack'
    })
    assert response.status_code == 401

def test_update_user_info_duplicate_email(client, login_user, another_user):
    response = client.put('/api/users/', json={
        'email': another_user.email
    })
    assert response.status_code == 400
    assert b"already exists" in response.data

def test_delete_user(client, login_user):
    response = client.delete('/api/users/')
    assert response.status_code == 204
    # 检查数据库中用户已被删除
    user = db.session.get(User, login_user.user_id)
    assert user is None

def test_delete_user_not_logged_in(client, test_user):
    response = client.delete('/api/users/')
    assert response.status_code == 401

def test_update_user_password(client, login_user):
    new_password = 'newpassword123'
    response = client.put('/api/users/', json={
        'password': new_password
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == "User updated successfully"
    # 检查数据库中密码已被更新（加密后不等于原始密码）
    user = db.session.get(User, login_user.user_id)
    assert user.password != 'newpassword123'
