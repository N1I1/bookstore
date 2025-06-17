import pytest
import uuid
from app import db
from app.models.user import User
from app.models.admin import Admin
from app.models.book import Book
from app.models.order import Order
from app.models.orderdetail import OrderDetail

@pytest.fixture
def user(app):
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

    # 删除该用户的所有订单明细和订单
    orders = Order.query.filter_by(user_id=user.user_id).all()
    for order in orders:
        # 先删明细
        for detail in order.order_details:
            db.session.delete(detail)
        db.session.delete(order)
    db.session.commit()
    for order in orders:
        # 确保订单被删除
        db.session.delete(order)
        db.session.commit()

    user_in_db = db.session.get(User, user.user_id)
    if user_in_db:
        # Ensure the user exists before trying to delete
        db.session.delete(user_in_db)
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
    admin_in_db = db.session.get(Admin, admin.admin_id)
    if admin_in_db:
        db.session.delete(admin_in_db)
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
    isbn = str(uuid.uuid4()).replace('-', '')[:13]
    book = Book(
        title='订单测试书',
        author='作者',
        isbn=isbn,
        publisher='出版社',
        price=20.0,
        discount=1.0,
        stock=10,
        description='desc'
    )
    db.session.add(book)
    db.session.commit()
    yield book
    order_details = OrderDetail.query.filter_by(book_id=book.book_id).all()
    for detail in order_details:
        # 先删明细
        db.session.delete(detail)
        db.session.commit()
        # 再删订单（如果没有其它明细）
        order = db.session.get(Order, detail.order_id)
        if order and not order.order_details.count():
            db.session.delete(order)
            db.session.commit()
    # 最后删 Book
    book_in_db = db.session.get(Book, book.book_id)
    if book_in_db:
        db.session.delete(book_in_db)
        db.session.commit()

@pytest.fixture
def test_order(app, user, admin_user, test_book):
    order = Order(
        user_id=user.user_id,
        admin_id=admin_user.admin_id,
        order_status='未支付',
        order_time=db.func.now(),
        bill_address='addr',
        biller_phone='123',
        remark='',
        total_amount=40.0
    )
    db.session.add(order)
    db.session.commit()
    detail = OrderDetail(
        order_id=order.order_id,
        book_id=test_book.book_id,
        quantity=2,
        unit_price=20.0
    )
    db.session.add(detail)
    db.session.commit()
    yield order, detail
    order_detail_in_db = db.session.get(OrderDetail, detail.detail_id)
    if order_detail_in_db:
        db.session.delete(order_detail_in_db)
        db.session.commit()
    order_in_db = db.session.get(Order, order.order_id)
    if order_in_db:

        db.session.delete(order_in_db)
        db.session.commit()

def test_create_order(client, login_user, test_book):
    print("++++++++++++++++++++++++++++++")
    print(test_book.book_id)
    print("++++++++++++++++++++++++++++++")
    data = {
        "bill_address": "test_addr",
        "biller_phone": "1234567890",
        "remark": "test",
        "details": [
            {"book_id": test_book.book_id, "quantity": 2}
        ]
    }
    response = client.post('/api/orders/', json=data)
    assert response.status_code == 201
    resp = response.get_json()
    assert "order_id" in resp
    assert resp["total_amount"] == 40.0

def test_get_order_list_user(client, login_user, test_order):
    response = client.get('/api/orders/')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert any(o["order_id"] == test_order[0].order_id for o in data)

def test_get_order_list_admin(client, login_admin, test_order):
    response = client.get('/api/orders/')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert any(o["order_id"] == test_order[0].order_id for o in data)

def test_get_order_detail_user(client, login_user, test_order):
    order, _ = test_order
    response = client.get(f'/api/orders/{order.order_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data["order_id"] == order.order_id

def test_get_order_detail_admin(client, login_admin, test_order):
    order, _ = test_order
    response = client.get(f'/api/orders/{order.order_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data["order_id"] == order.order_id

def test_update_order_user(client, login_user, test_order):
    order, _ = test_order
    # 只允许未支付订单修改
    response = client.put(f'/api/orders/{order.order_id}', json={
        "bill_address": "new_addr",
        "remark": "new_remark"
    })
    assert response.status_code == 200
    assert b"updated" in response.data

def test_update_order_user_paid_forbidden(client, login_user, test_order):
    order, _ = test_order
    order.order_status = '已支付'
    db.session.commit()
    response = client.put(f'/api/orders/{order.order_id}', json={
        "bill_address": "new_addr"
    })
    assert response.status_code == 400

def test_delete_order_user(client, login_user, test_order):
    order, _ = test_order
    response = client.delete(f'/api/orders/{order.order_id}')
    assert response.status_code == 204
    assert db.session.get(Order, order.order_id) is None

def test_delete_order_user_paid_forbidden(client, login_user, test_order):
    order, _ = test_order
    order.order_status = '已支付'
    db.session.commit()
    response = client.delete(f'/api/orders/{order.order_id}')
    assert response.status_code == 400

def test_pay_order(client, login_user, test_order):
    order, _ = test_order
    response = client.post(f'/api/orders/{order.order_id}/pay')
    assert response.status_code == 200
    db.session.refresh(order)
    assert order.order_status == '已支付'

def test_cancel_order(client, login_user, test_order):
    order, _ = test_order
    response = client.post(f'/api/orders/{order.order_id}/cancel')
    assert response.status_code == 200
    db.session.refresh(order)
    assert order.order_status == '订单取消'

def test_confirm_order(client, login_user, test_order):
    order, _ = test_order
    order.order_status = '已发货'
    db.session.commit()
    response = client.post(f'/api/orders/{order.order_id}/confirm')
    assert response.status_code == 200
    db.session.refresh(order)
    assert order.order_status == '已完成'

def test_admin_ship_order(client, login_admin, test_order):
    order, _ = test_order
    order.order_status = '已支付'
    db.session.commit()
    response = client.post(f'/api/orders/{order.order_id}/ship', json={
        "ship_address": "ship_addr",
        "current_address": "now_addr",
        "shipper_phone": "99999999999"
    })
    assert response.status_code == 200
    db.session.refresh(order)
    assert order.order_status == '已发货'
    assert order.ship_address == "ship_addr"

def test_admin_update_ship_address(client, login_admin, test_order):
    order, _ = test_order
    response = client.put(f'/api/orders/{order.order_id}/ship_address', json={
        "ship_address": "new_ship_addr"
    })
    assert response.status_code == 200
    db.session.refresh(order)
    assert order.ship_address == "new_ship_addr"

def test_order_permission_forbidden(client, test_order, user, admin_user):
    order, _ = test_order
    # 另一个用户
    other_user = User(
        username='other_user',
        password='pass',
        email='other_user@example.com',
        phone='11111111111',
    )
    db.session.add(other_user)
    db.session.commit()
    with client.session_transaction() as sess:
        sess['user_id'] = other_user.user_id
    response = client.get(f'/api/orders/{order.order_id}')
    assert response.status_code == 403
    db.session.delete(other_user)
    db.session.commit()
    # 另一个管理员
    other_admin = Admin(
        username='other_admin',
        password='pass',
        email='other_admin@example.com',
        phone='22222222222',
    )
    db.session.add(other_admin)
    db.session.commit()
    with client.session_transaction() as sess:
        sess['admin_id'] = other_admin.admin_id
    response = client.get(f'/api/orders/{order.order_id}')
    assert response.status_code == 403
    db.session.delete(other_admin)
    db.session.commit()

def test_get_order_list_unauthorized(client):
    """1. 查询订单列表，未登录应返回401"""
    response = client.get('/api/orders/')
    assert response.status_code == 401
    assert b"Unauthorized" in response.data

def test_get_single_order_not_found(client, login_user):
    """2. 查询单个订单，订单不存在应返回404"""
    response = client.get('/api/orders/999999')
    assert response.status_code == 404
    assert b"Order not found" in response.data

def test_create_order_unauthorized(client, test_book):
    """3. 创建新订单，未登录应返回401"""
    data = {
        "bill_address": "test_addr",
        "biller_phone": "1234567890",
        "remark": "test",
        "details": [
            {"book_id": test_book.book_id, "quantity": 2}
        ]
    }
    response = client.post('/api/orders/', json=data)
    assert response.status_code == 401
    assert b"Unauthorized" in response.data

def test_create_order_details_required(client, login_user):
    """4. 创建订单时未传details，触发order details required"""
    data = {
        "bill_address": "test_addr",
        "biller_phone": "1234567890",
        "remark": "test"
        # 缺少details字段
    }
    response = client.post('/api/orders/', json=data)
    assert response.status_code == 400
    assert b"Order details required" in response.data

def test_create_order_book_id_required(client, login_user):
    """5. 创建新订单时details缺book_id，触发book_id is required"""
    data = {
        "bill_address": "test_addr",
        "biller_phone": "1234567890",
        "remark": "test",
        "details": [
            {"quantity": 2}
        ]
    }
    response = client.post('/api/orders/', json=data)
    assert response.status_code == 400
    assert b"book_id is required" in response.data

def test_create_order_book_not_found(client, login_user):
    """6. 创建新订单时book_id不存在，触发book xxx not found"""
    data = {
        "bill_address": "test_addr",
        "biller_phone": "1234567890",
        "remark": "test",
        "details": [
            {"book_id": 999999, "quantity": 2}
        ]
    }
    response = client.post('/api/orders/', json=data)
    assert response.status_code == 400
    assert b"Book 999999 not found" in response.data

def test_create_order_quantity_must_be_positive(client, login_user, test_book):
    """7. 创建新订单时quantity为0或负数，触发quantity must be positive"""
    data = {
        "bill_address": "test_addr",
        "biller_phone": "1234567890",
        "remark": "test",
        "details": [
            {"book_id": test_book.book_id, "quantity": 0}
        ]
    }
    response = client.post('/api/orders/', json=data)
    assert response.status_code == 400
    assert b"Quantity must be positive" in response.data

def test_update_order_user_id_mismatch(client, user, test_order):
    """1. 用户修改订单时，session中的user_id与订单user_id不符"""
    order, _ = test_order
    # 新建另一个用户
    other_user = User(
        username='other_user',
        password='pass',
        email='other_user@example.com',
        phone='11111111111',
    )
    db.session.add(other_user)
    db.session.commit()
    with client.session_transaction() as sess:
        sess['user_id'] = other_user.user_id
    response = client.put(f'/api/orders/{order.order_id}', json={
        "bill_address": "new_addr"
    })
    assert response.status_code == 403
    assert b"Forbidden" in response.data
    db.session.delete(other_user)
    db.session.commit()

def test_update_order_nothing_updated(client, login_user, test_order):
    """2. 用户更新订单信息时，实际上什么也没更新"""
    order, _ = test_order
    response = client.put(f'/api/orders/{order.order_id}', json={})
    assert response.status_code == 400
    assert b"No updatable field provided" in response.data

def test_update_order_not_logged_in(client, test_order):
    """3. 用户更新订单信息时没有登录"""
    order, _ = test_order
    response = client.put(f'/api/orders/{order.order_id}', json={
        "bill_address": "new_addr"
    })
    assert response.status_code == 401
    assert b"Unauthorized" in response.data

def test_delete_order_not_found(client, login_user):
    """4. 用户删除订单时，找不到相应订单"""
    response = client.delete('/api/orders/999999')
    assert response.status_code == 404
    assert b"Order not found" in response.data

def test_delete_order_not_owner(client, user, test_order):
    """5. 用户想要删除不是自己的订单"""
    order, _ = test_order
    # 新建另一个用户
    other_user = User(
        username='other_user2',
        password='pass',
        email='other_user2@example.com',
        phone='11111111112',
    )
    db.session.add(other_user)
    db.session.commit()
    with client.session_transaction() as sess:
        sess['user_id'] = other_user.user_id
    response = client.delete(f'/api/orders/{order.order_id}')
    assert response.status_code == 403
    assert b"Forbidden" in response.data
    db.session.delete(other_user)
    db.session.commit()

def test_pay_order_not_logged_in(client, test_order):
    """6. 用户支付时未登录"""
    order, _ = test_order
    response = client.post(f'/api/orders/{order.order_id}/pay')
    assert response.status_code == 401
    assert b"Unauthorized" in response.data

def test_pay_order_user_id_mismatch(client, user, test_order):
    """7. 用户支付时session中的user_id与订单user_id不符"""
    order, _ = test_order
    # 新建另一个用户
    other_user = User(
        username='other_user3',
        password='pass',
        email='other_user3@example.com',
        phone='11111111113',
    )
    db.session.add(other_user)
    db.session.commit()
    with client.session_transaction() as sess:
        sess['user_id'] = other_user.user_id
    response = client.post(f'/api/orders/{order.order_id}/pay')
    assert response.status_code == 403
    assert b"Forbidden" in response.data
    db.session.delete(other_user)
    db.session.commit()

def test_pay_order_status_not_unpaid(client, login_user, test_order):
    """用户支付时，状态不是未支付"""
    order, _ = test_order
    order.order_status = '已支付'
    db.session.commit()
    response = client.post(f'/api/orders/{order.order_id}/pay')
    assert response.status_code == 400
    assert b"Order status not allowed for payment" in response.data

def test_cancel_order_not_logged_in(client, test_order):
    """用户取消订单时未登录"""
    order, _ = test_order
    response = client.post(f'/api/orders/{order.order_id}/cancel')
    assert response.status_code == 401
    assert b"Unauthorized" in response.data

def test_cancel_order_not_found(client, login_user):
    """取消未找到的订单"""
    response = client.post('/api/orders/999999/cancel')
    assert response.status_code == 404
    assert b"Order not found" in response.data

def test_cancel_order_not_owner(client, user, test_order):
    """取消的订单不是自己的账户"""
    order, _ = test_order
    other_user = User(
        username='other_user_cancel',
        password='pass',
        email='other_user_cancel@example.com',
        phone='11111111114',
    )
    db.session.add(other_user)
    db.session.commit()
    with client.session_transaction() as sess:
        sess['user_id'] = other_user.user_id
    response = client.post(f'/api/orders/{order.order_id}/cancel')
    assert response.status_code == 403
    assert b"Forbidden" in response.data
    db.session.delete(other_user)
    db.session.commit()

def test_cancel_order_status_not_allowed(client, login_user, test_order):
    """订单不是在未支付或已支付状态下"""
    order, _ = test_order
    order.order_status = '已发货'
    db.session.commit()
    response = client.post(f'/api/orders/{order.order_id}/cancel')
    assert response.status_code == 400
    assert b"Only unpaid or paid-but-unshipped orders can be cancelled" in response.data

def test_confirm_order_not_logged_in(client, test_order):
    """用户确认收货时没有登陆"""
    order, _ = test_order
    response = client.post(f'/api/orders/{order.order_id}/confirm')
    assert response.status_code == 401
    assert b"Unauthorized" in response.data

def test_confirm_order_user_id_mismatch(client, user, test_order):
    """确认收货与自己账户不符"""
    order, _ = test_order
    other_user = User(
        username='other_user_confirm',
        password='pass',
        email='other_user_confirm@example.com',
        phone='11111111115',
    )
    db.session.add(other_user)
    db.session.commit()
    with client.session_transaction() as sess:
        sess['user_id'] = other_user.user_id
    response = client.post(f'/api/orders/{order.order_id}/confirm')
    assert response.status_code == 403
    assert b"Forbidden" in response.data
    db.session.delete(other_user)
    db.session.commit()

def test_confirm_order_status_not_shipped(client, login_user, test_order):
    """订单不在已发货状态下就确认收货"""
    order, _ = test_order
    order.order_status = '未支付'
    db.session.commit()
    response = client.post(f'/api/orders/{order.order_id}/confirm')
    assert response.status_code == 400
    assert b"Order status not allowed for confirmation" in response.data

def test_admin_ship_order_not_logged_in(client, test_order):
    """管理员发货时未登录"""
    order, _ = test_order
    response = client.post(f'/api/orders/{order.order_id}/ship', json={
        "ship_address": "ship_addr"
    })
    assert response.status_code == 401
    assert b"Unauthorized" in response.data

def test_admin_ship_order_not_found(client, login_admin):
    """管理员确认发货时找不到订单"""
    response = client.post('/api/orders/999999/ship', json={
        "ship_address": "ship_addr"
    })
    assert response.status_code == 404
    assert b"Order not found" in response.data

def test_admin_ship_order_not_owner(client, admin_user, test_order):
    """管理员对自己不管理的订单确认发货"""
    order, _ = test_order
    other_admin = Admin(
        username='other_admin_ship',
        password='pass',
        email='other_admin_ship@example.com',
        phone='11111111116',
    )
    db.session.add(other_admin)
    db.session.commit()
    with client.session_transaction() as sess:
        sess['admin_id'] = other_admin.admin_id
    response = client.post(f'/api/orders/{order.order_id}/ship', json={
        "ship_address": "ship_addr"
    })
    assert response.status_code == 403
    assert b"Forbidden" in response.data
    db.session.delete(other_admin)
    db.session.commit()

def test_admin_ship_order_status_not_paid(client, login_admin, test_order):
    """订单不在已支付状态下管理员就发货"""
    order, _ = test_order
    order.order_status = '未支付'
    db.session.commit()
    response = client.post(f'/api/orders/{order.order_id}/ship', json={
        "ship_address": "ship_addr"
    })
    assert response.status_code == 400
    assert b"Order status not allowed for shipping" in response.data

def test_admin_update_ship_address_not_logged_in(client, test_order):
    """管理员更新订单状态时未登录"""
    order, _ = test_order
    response = client.put(f'/api/orders/{order.order_id}/ship_address', json={
        "ship_address": "new_ship_addr"
    })
    assert response.status_code == 401
    assert b"Unauthorized" in response.data

def test_admin_update_ship_address_not_found(client, login_admin):
    """管理员更新订单状态时，更新找不到的订单"""
    response = client.put('/api/orders/999999/ship_address', json={
        "ship_address": "new_ship_addr"
    })
    assert response.status_code == 404
    assert b"Order not found" in response.data

def test_admin_update_ship_address_not_owner(client, admin_user, test_order):
    """管理员更新不属于自己管理的订单"""
    order, _ = test_order
    other_admin = Admin(
        username='other_admin_update',
        password='pass',
        email='other_admin_update@example.com',
        phone='11111111117',
    )
    db.session.add(other_admin)
    db.session.commit()
    with client.session_transaction() as sess:
        sess['admin_id'] = other_admin.admin_id
    response = client.put(f'/api/orders/{order.order_id}/ship_address', json={
        "ship_address": "new_ship_addr"
    })
    assert response.status_code == 403
    assert b"Forbidden" in response.data
    db.session.delete(other_admin)
    db.session.commit()

def test_admin_update_ship_address_nothing_updated(client, login_admin, test_order):
    """更新订单信息时没有更新地址"""
    order, _ = test_order
    response = client.put(f'/api/orders/{order.order_id}/ship_address', json={})
    assert response.status_code == 400
    assert b"No address field provided" in response.data

def test_get_order_detail_admin_not_owner(client, login_admin, test_order, admin_user):
    """管理员查询单个订单时，获取不属于自己的订单"""
    order, _ = test_order
    # 新建另一个管理员
    other_admin = Admin(
        username='other_admin_get',
        password='pass',
        email='other_admin_get@example.com',
        phone='11111111118',
    )
    db.session.add(other_admin)
    db.session.commit()
    with client.session_transaction() as sess:
        sess['admin_id'] = other_admin.admin_id
    response = client.get(f'/api/orders/{order.order_id}')
    assert response.status_code == 403
    assert b"Forbidden" in response.data
    db.session.delete(other_admin)
    db.session.commit()

def test_update_order_user_not_found(client, login_user):
    """用户更新找不到的订单"""
    response = client.put('/api/orders/999999', json={"bill_address": "new_addr"})
    assert response.status_code == 404
    assert b"Order not found" in response.data

def test_pay_order_not_found(client, login_user):
    """用户支付找不到的订单"""
    response = client.post('/api/orders/999999/pay')
    assert response.status_code == 404
    assert b"Order not found" in response.data

def test_confirm_order_not_found(client, login_user):
    """用户确认收货找不到的订单"""
    response = client.post('/api/orders/999999/confirm')
    assert response.status_code == 404
    assert b"Order not found" in response.data
