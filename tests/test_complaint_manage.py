import pytest
from app import db
from app.models import User, Admin, Complaint

@pytest.fixture
def test_user(app):
    user = User(username='testuser', password='123456', email='testuser@example.com', phone='1234567890')
    db.session.add(user)
    db.session.commit()
    yield user
    db.session.delete(user)
    db.session.commit()

@pytest.fixture
def test_admin(app):
    admin = Admin(username='admin', password='admin123', email='testadmin@example.com', phone='9876543210')
    db.session.add(admin)
    db.session.commit()
    yield admin
    db.session.delete(admin)
    db.session.commit()

@pytest.fixture
def login_user(client, test_user):
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.user_id

@pytest.fixture
def login_admin(client, test_admin):
    with client.session_transaction() as sess:
        sess['admin_id'] = test_admin.admin_id

def test_user_create_and_get_complaint(client, login_user, test_user):
    # 用户创建投诉
    response = client.post('/api/complaint_manage/user_create', json={
        "content": "投诉内容测试"
    })
    assert response.status_code == 201
    assert b"Complaint created successfully" in response.data

    # 用户获取自己的投诉
    response = client.get('/api/complaint_manage/user_get')
    assert response.status_code == 200
    data = response.get_json()
    assert "complaints" in data
    assert any(c["content"] == "投诉内容测试" for c in data["complaints"])

def test_user_create_complaint_no_content(client, login_user):
    response = client.post('/api/complaint_manage/user_create', json={})
    assert response.status_code == 400
    assert b"Complaint content cannot be empty" in response.data

def test_user_get_complaint_not_logged_in(client):
    response = client.get('/api/complaint_manage/user_get')
    assert response.status_code == 401

def test_user_change_status(client, login_user, test_user):
    # 创建投诉
    complaint = Complaint(user_id=test_user.user_id, content="test", status="已受理")
    db.session.add(complaint)
    db.session.commit()

    # 用户变更投诉状态
    response = client.post('/api/complaint_manage/user_change_status', json={
        "complaint_id": complaint.complaint_id
    })
    assert response.status_code == 200
    assert b"Complaint status updated successfully" in response.data

    db.session.delete(complaint)
    db.session.commit()

def test_user_change_status_wrong_status(client, login_user, test_user):
    complaint = Complaint(user_id=test_user.user_id, content="test", status="待处理")
    db.session.add(complaint)
    db.session.commit()

    response = client.post('/api/complaint_manage/user_change_status', json={
        "complaint_id": complaint.complaint_id
    })
    assert response.status_code == 400
    assert b"Complaint status is not" in response.data

    db.session.delete(complaint)
    db.session.commit()

def test_admin_get_complaints(client, login_admin, test_user):
    # 创建投诉
    complaint = Complaint(user_id=test_user.user_id, content="admin test", status="待处理")
    db.session.add(complaint)
    db.session.commit()

    response = client.get('/api/complaint_manage/admin_get')
    assert response.status_code == 200
    data = response.get_json()
    assert "complaints" in data
    assert any(c["content"] == "admin test" for c in data["complaints"])

    db.session.delete(complaint)
    db.session.commit()

def test_admin_get_complaints_with_status(client, login_admin, test_user):
    complaint = Complaint(user_id=test_user.user_id, content="admin test2", status="已解决")
    db.session.add(complaint)
    db.session.commit()

    response = client.get('/api/complaint_manage/admin_get?status=已解决')
    assert response.status_code == 200
    data = response.get_json()
    assert any(c["status"] == "已解决" for c in data["complaints"])

    db.session.delete(complaint)
    db.session.commit()

def test_deal_with_complaint(client, login_admin, test_user):
    complaint = Complaint(user_id=test_user.user_id, content="to deal", status="待处理")
    db.session.add(complaint)
    db.session.commit()

    response = client.post('/api/complaint_manage/deal_with_complaint', json={
        "complaint_id": complaint.complaint_id,
        "result": "处理结果"
    })
    assert response.status_code == 200
    assert b"Complaint processed successfully" in response.data

    db.session.delete(complaint)
    db.session.commit()

def test_deal_with_complaint_wrong_status(client, login_admin, test_user):
    complaint = Complaint(user_id=test_user.user_id, content="to deal", status="已受理")
    db.session.add(complaint)
    db.session.commit()

    response = client.post('/api/complaint_manage/deal_with_complaint', json={
        "complaint_id": complaint.complaint_id,
        "result": "处理结果"
    })
    assert response.status_code == 400

    db.session.delete(complaint)
    db.session.commit()

def test_deal_with_complaint_not_found(client, login_admin):
    response = client.post('/api/complaint_manage/deal_with_complaint', json={
        "complaint_id": 999999,
        "result": "处理结果"
    })
    assert response.status_code == 404

def test_deal_with_complaint_not_logged_in(client):
    response = client.post('/api/complaint_manage/deal_with_complaint', json={
        "complaint_id": 1,
        "result": "处理结果"
    })
    assert response.status_code == 401
