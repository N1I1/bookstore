import pytest
from app import db
from app.models.book import Book
from app.models.order import Order
from app.models.orderdetail import OrderDetail
from app.models.admin import Admin
from app.models.user import User

@pytest.fixture
def user(app):
    import uuid
    unique_str = uuid.uuid4().hex
    user = User(
        username=f'user_{unique_str}',
        password='userpass',
        email=f'user_{unique_str}@example.com',
        phone='1234567890',
    )
    db.session.add(user)
    db.session.commit()
    yield user
    db.session.delete(user)
    db.session.commit()

@pytest.fixture
def admin_user(app):
    import uuid
    unique_str = uuid.uuid4().hex
    admin = Admin(
        username=f'admin_{unique_str}',
        password='adminpass',
        email=f'admin_{unique_str}@example.com',
        phone='1234567890',
    )
    db.session.add(admin)
    db.session.commit()
    yield admin
    db.session.delete(admin)
    db.session.commit()

@pytest.fixture
def login_user(client, user):
    with client.session_transaction() as sess:
        sess['user_id'] = user.user_id
        sess['username'] = user.username

@pytest.fixture
def login_admin(client, admin_user):
    with client.session_transaction() as sess:
        sess['admin_id'] = admin_user.admin_id
        sess['username'] = admin_user.username

@pytest.fixture
def test_book(app):
    book = Book(
        title='OrderDetail测试书',
        author='作者',
        isbn='9999999999999',
        publisher='出版社',
        price=10.0,
        discount=1.0,
        stock=5,
        description='desc'
    )
    db.session.add(book)
    db.session.commit()
    yield book
    db.session.delete(book)
    db.session.commit()

@pytest.fixture
def test_order_and_detail(app, user, admin_user, test_book):
    order = Order(
        user_id=user.user_id,
        admin_id=admin_user.admin_id,
        order_status='未支付',
        order_time=db.func.now(),
        ship_address='addr',
        bill_address='addr',
        current_address='addr',
        shipper_phone='123',
        biller_phone='456',
        remark='',
        total_amount=10.0
    )
    db.session.add(order)
    db.session.commit()
    detail = OrderDetail(
        order_id=order.order_id,
        book_id=test_book.book_id,
        quantity=2,
        unit_price=10.0
    )
    db.session.add(detail)
    db.session.commit()
    yield order, detail
    order.order_status = '已完成'  # 模拟订单完成
    db.session.commit()
    db.session.delete(order)
    db.session.commit()

def test_get_order_detail_user(client, login_user, test_order_and_detail, user):
    order, detail = test_order_and_detail
    response = client.get(f'/api/order_details/{detail.detail_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['detail_id'] == detail.detail_id
    assert data['order_id'] == order.order_id
    assert data['book_id'] == detail.book_id

def test_get_order_detail_admin(client, login_admin, test_order_and_detail, admin_user):
    order, detail = test_order_and_detail
    response = client.get(f'/api/order_details/{detail.detail_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['detail_id'] == detail.detail_id
    assert data['order_id'] == order.order_id
    assert data['book_id'] == detail.book_id

def test_get_order_detail_unauthorized(client, test_order_and_detail):
    order, detail = test_order_and_detail
    response = client.get(f'/api/order_details/{detail.detail_id}')
    assert response.status_code == 401

def test_get_order_detail_forbidden_user(client, user, test_order_and_detail):
    # 新建另一个用户
    from app.models.user import User
    import uuid
    unique_str = uuid.uuid4().hex
    other_user = User(
        username=f'other_{unique_str}',
        password='pass',
        email=f'other_{unique_str}@example.com',
        phone='11111111111',
    )
    db.session.add(other_user)
    db.session.commit()
    with client.session_transaction() as sess:
        sess['user_id'] = other_user.user_id
        sess['username'] = other_user.username
    order, detail = test_order_and_detail
    response = client.get(f'/api/order_details/{detail.detail_id}')
    assert response.status_code == 403
    db.session.delete(other_user)
    db.session.commit()

def test_get_order_detail_forbidden_admin(client, admin_user, test_order_and_detail):
    # 新建另一个管理员
    from app.models.admin import Admin
    import uuid
    unique_str = uuid.uuid4().hex
    other_admin = Admin(
        username=f'other_admin_{unique_str}',
        password='pass',
        email=f'other_admin_{unique_str}@example.com',
        phone='22222222222',
    )
    db.session.add(other_admin)
    db.session.commit()
    with client.session_transaction() as sess:
        sess['admin_id'] = other_admin.admin_id
        sess['username'] = other_admin.username
    order, detail = test_order_and_detail
    response = client.get(f'/api/order_details/{detail.detail_id}')
    assert response.status_code == 403
    db.session.delete(other_admin)
    db.session.commit()

def test_get_order_detail_not_found(client, login_user):
    response = client.get('/api/order_details/999999')
    assert response.status_code == 404
