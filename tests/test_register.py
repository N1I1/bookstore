import pytest
from app.models import User
from app import db
from werkzeug.security import check_password_hash

def test_register_success(client):
    response = client.post('/api/register/', json={
        "username": "newuser",
        "password": "newpassword",
        "email": "newuser@example.com",
        "phone": "12345678901"
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "User registered successfully"
    assert "user_id" in data

    # 检查数据库
    user = User.query.filter_by(username="newuser").first()
    assert user is not None
    assert user.email == "newuser@example.com"
    assert check_password_hash(user.password, "newpassword")
    db.session.delete(user)
    db.session.commit()

def test_register_missing_fields(client):
    response = client.post('/api/register/', json={
        "username": "user2",
        "password": "pass2"
        # 缺少 email 和 phone
    })
    assert response.status_code == 400
    assert b"Missing required fields" in response.data

def test_register_duplicate_username(client):
    # 先注册一个用户
    client.post('/api/register/', json={
        "username": "dupuser",
        "password": "pass",
        "email": "dupuser@example.com",
        "phone": "12345678901"
    })
    # 再用相同用户名注册
    response = client.post('/api/register/', json={
        "username": "dupuser",
        "password": "pass2",
        "email": "dupuser2@example.com",
        "phone": "12345678902"
    })
    assert response.status_code == 400
    assert b"Username or email already exists" in response.data
    db.session.query(User).filter_by(username="dupuser").delete()
    db.session.commit()

def test_register_duplicate_email(client):
    # 先注册一个用户
    client.post('/api/register/', json={
        "username": "user3",
        "password": "pass",
        "email": "same@example.com",
        "phone": "12345678901"
    })
    # 再用相同邮箱注册
    response = client.post('/api/register/', json={
        "username": "user4",
        "password": "pass2",
        "email": "same@example.com",
        "phone": "12345678902"
    })
    assert response.status_code == 400
    assert b"Username or email already exists" in response.data
    db.session.query(User).filter_by(username="user3").delete()
    db.session.commit()
