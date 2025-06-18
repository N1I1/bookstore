import pytest
import json
from app import create_app, db
from app.models import User, Admin ,Complaint

test_complaint_2_id = 0
test_complaint_3_id = 0

@pytest.fixture
def app():
    app = create_app()
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    return app.test_client()


def test_register_user(client):
    # 注册用户
    register_data = {
        "username": "test_user",
        "password": "test_password",
        "email": "test@example.com",
        "phone": "1234567890"
    }
    response = client.post('/api/register/', json=register_data)
    assert response.status_code == 201, "Failed to register user"

def test_register_admin(client):
    # 注册管理员
    register_data = {
        "username": "test_admin",
        "password": "test_password",
        "email": "test@example.com",
        "phone": "1234567890"
    }
    response = client.post('/api/admins/', json=register_data)
    assert response.status_code == 201, "Failed to register admin"


@pytest.fixture(scope='function')
def login_user(client):
    # 模拟用户登录
    login_data = {
        "username": "test_user",
        "password": "test_password"
    }
    response = client.post('/api/login/', json=login_data)
    assert response.status_code == 200, "Failed to login user"

    # 获取 session 中的 user_id
    with client.session_transaction() as sess:
        user_id = sess.get('user_id')

    assert user_id is not None, "User ID not found in session"
    return user_id

@pytest.fixture(scope='function')
def login_admin(client):
    # 模拟管理员登录
    login_data = {
        "adminname": "test_admin",
        "password": "test_password"
    }
    response = client.post('/api/admin/login/', json=login_data)
    assert response.status_code == 200, "Failed to login admin"

    # 获取 session 中的 admin_id
    with client.session_transaction() as sess:
        admin_id = sess.get('admin_id')
    
    # 验证是否成功获取 admin_id
    assert admin_id is not None, "User ID not found in session after login"
    
    return admin_id

def test_setup_data(client, login_user):
    user_id = login_user

    # 创建投诉数据
    complaint_1 = Complaint(user_id=user_id, content="投诉内容1", status="待处理")
    complaint_2 = Complaint(user_id=user_id, content="投诉内容2", status="已受理", result="处理结果2")
    db.session.add_all([complaint_1, complaint_2])
    db.session.commit()

    global test_complaint_2_id
    test_complaint_2_id = complaint_2.complaint_id

def test_complaint_manage_user_get_success(client, login_user):
    user_id = login_user

    # 验证获取所有投诉数据
    data = {'status': None}
    response = client.get('/api/complaint_manage/user_get', json=data)
    assert response.status_code == 200, "Failed to get complaint data"
    data = json.loads(response.data)
    complaint = data['complaints']
    assert len(complaint) > 1, "Incorrect number of complaints returned"

    # 验证获取 待处理 投诉数据
    data = {'status': '待处理'}
    response = client.get('/api/complaint_manage/user_get', json=data)
    assert response.status_code == 200, "Failed to get complaint data"
    data = json.loads(response.data)
    complaint = data['complaints']
    assert len(complaint) == 1, "Incorrect number of complaints returned"

    # 验证获取 已受理 投诉数据
    data = {'status': '已受理'}
    response = client.get('/api/complaint_manage/user_get', json=data)
    assert response.status_code == 200, "Failed to get complaint data"
    data = json.loads(response.data)
    complaint = data['complaints']
    assert len(complaint) == 1, "Incorrect number of complaints returned"

    # 验证获取 已解决 投诉数据
    data = {'status': '已解决'}
    response = client.get('/api/complaint_manage/user_get', json=data)
    assert response.status_code == 404, "Failed to get complaint data"
    data = json.loads(response.data)
    message= data['message']
    assert message == 'No complaints found'

def test_complaint_manage_user_create_success(client, login_user):
    user_id = login_user

    # 创建投诉数据
    data = {
        "content": "投诉内容3",
    }
    response = client.post('/api/complaint_manage/user_create', json=data)
    assert response.status_code == 201, "Failed to create complaint data"
    data = json.loads(response.data)
    message = data['message']
    assert message == "Complaint created successfully"

    global test_complaint_3_id
    test_complaint_3_id = db.session.query(Complaint).filter_by(content="投诉内容3").first().complaint_id

def test_complaint_manage_user_change_status_success(client, login_user):
    user_id = login_user

    # 更新投诉状态
    data = {"complaint_id": test_complaint_2_id}
    response = client.post('/api/complaint_manage/user_change_status', json=data)
    assert response.status_code == 200, "Failed to update complaint status"
    data = json.loads(response.data)
    message = data['message']
    assert message == "Complaint status updated successfully"

def test_complaint_manage_admin_get_success(client, login_admin):
    admin_id = login_admin

    # 验证获取所有投诉数据
    data = {'status': None}
    response = client.get('/api/complaint_manage/admin_get', json=data)
    assert response.status_code == 200, "Failed to get complaint data"
    data = json.loads(response.data)
    complaint = data['complaints']
    assert len(complaint) == 3, "Incorrect number of complaints returned"
    
def test_complaint_manage_deal_with_complaint_success(client, login_admin):
    admin_id = login_admin

    # 处理投诉
    data = {"complaint_id": test_complaint_3_id, "result": "处理结果3"}
    response = client.post('/api/complaint_manage/deal_with_complaint', json=data)
    assert response.status_code == 200, "Failed to deal with complaint"
    data = json.loads(response.data)
    message = data['message']
    assert message == "Complaint processed successfully"


def test_delete_test_data():
    db.session.query(Complaint).delete()
    db.session.query(User).delete()
    db.session.query(Admin).delete()
    db.session.commit()


