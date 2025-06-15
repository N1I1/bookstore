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
    response = client.get(f'/api/users/{login_user.user_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['username'].startswith('testuser_')
    assert data['email'].startswith('test_')

def test_get_user_info_unauthorized(client, test_user, another_user):
    with client.session_transaction() as sess:
        sess['user_id'] = another_user.user_id
    response = client.get(f'/api/users/{test_user.user_id}')
    assert response.status_code == 403

def test_get_user_info_not_logged_in(client, test_user):
    response = client.get(f'/api/users/{test_user.user_id}')
    assert response.status_code == 401

def test_update_user_info(client, login_user):
    response = client.put(f'/api/users/{login_user.user_id}', json={
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

def test_update_user_info_unauthorized(client, test_user, another_user):
    with client.session_transaction() as sess:
        sess['user_id'] = another_user.user_id
    response = client.put(f'/api/users/{test_user.user_id}', json={
        'username': 'hack'
    })
    assert response.status_code == 403

def test_update_user_info_not_logged_in(client, test_user):
    response = client.put(f'/api/users/{test_user.user_id}', json={
        'username': 'hack'
    })
    assert response.status_code == 401

def test_update_user_info_duplicate_email(client, login_user, another_user):
    response = client.put(f'/api/users/{login_user.user_id}', json={
        'email': another_user.email
    })
    assert response.status_code == 400
    assert b"already exists" in response.data

def test_delete_user(client, login_user):
    response = client.delete(f'/api/users/{login_user.user_id}')
    assert response.status_code == 204
    # 检查数据库中用户已被删除
    user = db.session.get(User, login_user.user_id)
    assert user is None

def test_delete_user_unauthorized(client, test_user, another_user):
    with client.session_transaction() as sess:
        sess['user_id'] = another_user.user_id
    response = client.delete(f'/api/users/{test_user.user_id}')
    assert response.status_code == 403

def test_delete_user_not_logged_in(client, test_user):
    response = client.delete(f'/api/users/{test_user.user_id}')
    assert response.status_code == 401

def test_get_user_not_found(client, login_user):
    response = client.get('/api/users/999999')
    assert response.status_code == 403 or response.status_code == 404

def test_update_user_not_found(client, login_user):
    response = client.put('/api/users/999999', json={'username': 'ghost'})
    assert response.status_code == 404 or response.status_code == 403

def test_update_user_integrity_error(client, login_user, another_user):
    # 尝试把自己的邮箱改成另一个用户的邮箱，触发唯一性约束
    response = client.put(f'/api/users/{login_user.user_id}', json={'email': another_user.email})
    assert response.status_code == 400

def test_delete_user_not_found(client, login_user):
    response = client.delete('/api/users/999999')
    assert response.status_code == 404 or response.status_code == 403

def test_get_user_not_found_logged_in(client, login_user):
    response = client.get('/api/users/999999')
    # 如果你的实现先判断权限再查找用户，可能返回403，否则404
    assert response.status_code in (403, 404)

def test_update_user_password(client, login_user):
    new_password = 'newpassword123'
    response = client.put(f'/api/users/{login_user.user_id}', json={
        'password': new_password
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == "User updated successfully"
    # 检查数据库中密码已被更新（加密后不等于原始密码）
    user = db.session.get(User, login_user.user_id)
    assert user.password != 'newpassword123'
