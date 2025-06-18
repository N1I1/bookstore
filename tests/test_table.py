import pytest
import sqlalchemy
from app import db
from app.models.user import User
from app.models.admin import Admin
from app.models.book import Book
from app.models.order import Order
from app.models.orderdetail import OrderDetail

@pytest.fixture
def user():
    u = User(username='cascade_user', password='pw', email='cascade@example.com', phone='123')
    db.session.add(u)
    db.session.commit()
    yield u
    user_in_db = db.session.get(User, u.user_id)
    if user_in_db:
        db.session.delete(user_in_db)
        db.session.commit()

@pytest.fixture
def admin_user():
    admin = Admin(username='admin', password='pw', email='admin@example.com', phone='123')
    db.session.add(admin)
    db.session.commit()
    yield admin
    admin_in_db = db.session.get(Admin, admin.admin_id)
    if admin_in_db:
        db.session.delete(admin_in_db)
        db.session.commit()

@pytest.fixture
def book():
    b = Book(title='cascade_book', author='auth', isbn='1234567890123', publisher='pub', price=10, discount=1, stock=1, description='desc')
    db.session.add(b)
    db.session.commit()
    yield b
    b = db.session.get(Book, b.book_id)
    if not b:
        return
    db.session.delete(b)
    db.session.commit()

@pytest.fixture
def order(user):
    o = Order(user_id=user.user_id, order_status='未支付', order_time=db.func.now(), bill_address='addr', biller_phone='123', remark='', total_amount=10)
    db.session.add(o)
    db.session.commit()
    yield o
    o = db.session.get(Order, o.order_id)
    if not o:
        return
    order.order_status = '已完成'
    db.session.commit()
    db.session.delete(o)
    db.session.commit()

@pytest.fixture
def order_detail(order, book):
    od = OrderDetail(order_id=order.order_id, book_id=book.book_id, quantity=1, unit_price=10)
    db.session.add(od)
    db.session.commit()
    yield od
    od = db.session.get(OrderDetail, od.detail_id)
    if not od:
        return
    db.session.delete(od)
    db.session.commit()

def test_cascade_delete_user_deletes_order(user):
    o = Order(user_id=user.user_id, order_status='已完成', order_time=db.func.now(), bill_address='addr', biller_phone='123', remark='', total_amount=10)
    db.session.add(o)
    db.session.commit()
    order_id = o.order_id

    db.session.delete(user)
    db.session.commit()
    assert db.session.get(Order, order_id).user_id is None
    db.session.delete(o)
    db.session.commit()

def test_cascade_delete_order_deletes_orderdetail(order, book):
    od = OrderDetail(order_id=order.order_id, book_id=book.book_id, quantity=1, unit_price=10)
    db.session.add(od)
    db.session.commit()
    detail_id = od.detail_id

    order.order_status = '已完成'
    db.session.commit()
    db.session.delete(order)
    db.session.commit()
    assert db.session.get(OrderDetail, detail_id) is None

def test_cascade_delete_book_deletes_orderdetail(user, book):
    o = Order(user_id=user.user_id, order_status='已完成', order_time=db.func.now(), bill_address='addr', biller_phone='123', remark='', total_amount=10)
    db.session.add(o)
    db.session.commit()
    od = OrderDetail(order_id=o.order_id, book_id=book.book_id, quantity=1, unit_price=10)
    db.session.add(od)
    db.session.commit()
    detail_id = od.detail_id

    db.session.delete(book)
    db.session.commit()
    assert db.session.get(OrderDetail, detail_id).book_id is None
    db.session.delete(o)
    db.session.commit()

def test_set_null_on_delete_admin(user, admin_user):
    o = Order(user_id=user.user_id, order_status='未支付', order_time=db.func.now(), bill_address='addr', biller_phone='123', remark='', total_amount=10, admin_id=admin_user.admin_id)
    db.session.add(o)
    db.session.commit()

    db.session.delete(admin_user)
    db.session.commit()
    db.session.refresh(o)
    assert o.admin_id is None
    o.order_status = '已完成'
    db.session.commit()
    db.session.delete(o)
    db.session.commit()

def test_raw_sql_cannot_delete_user_with_unfinished_order(user):
    # 创建未完成订单
    o = Order(user_id=user.user_id, order_status='未支付', order_time=db.func.now(), bill_address='addr', biller_phone='123', remark='', total_amount=10)
    db.session.add(o)
    db.session.commit()
    
    # Use raw SQL to attempt deletion
    with pytest.raises(Exception) as excinfo:
        with db.engine.connect() as conn:
            conn.execute(sqlalchemy.text(f"DELETE FROM user WHERE user_id = {user.user_id}"))
            conn.commit()
    
    db.session.delete(user)
    db.session.commit()
    assert '不能删除' in str(excinfo.value) or '未完成订单' in str(excinfo.value)
    o.order_status = '已完成'
    db.session.commit()
    db.session.delete(o)
    db.session.commit()

def test_cannot_delete_book_with_unfinished_orderdetail(user, book):
    # 创建未完成订单和订单明细
    o = Order(user_id=user.user_id, order_status='未支付', order_time=db.func.now(), bill_address='addr', biller_phone='123', remark='', total_amount=10)
    db.session.add(o)
    db.session.commit()
    od = OrderDetail(order_id=o.order_id, book_id=book.book_id, quantity=1, unit_price=10)
    db.session.add(od)
    db.session.commit()
    
    # Use raw SQL to attempt deletion
    with pytest.raises(Exception) as excinfo:
        with db.engine.connect() as conn:
            conn.execute(sqlalchemy.text(f"DELETE FROM book WHERE book_id = {book.book_id}"))
            conn.commit()
    
    # Optional: Verify error message
    assert '不能删除' in str(excinfo.value) or '未完成订单' in str(excinfo.value)
    
    # Clean up
    o.order_status = '已完成'
    db.session.commit()
    db.session.delete(o)
    db.session.commit()

def test_cannot_delete_orderdetail_with_unfinished_order(user, book):
    # 创建未完成订单和订单明细
    o = Order(user_id=user.user_id, order_status='未支付', order_time=db.func.now(), bill_address='addr', biller_phone='123', remark='', total_amount=10)
    db.session.add(o)
    db.session.commit()
    od = OrderDetail(order_id=o.order_id, book_id=book.book_id, quantity=1, unit_price=10)
    db.session.add(od)
    db.session.commit()
    
    # Use raw SQL to attempt deletion
    with pytest.raises(Exception) as excinfo:
        with db.engine.connect() as conn:
            conn.execute(sqlalchemy.text(f"DELETE FROM order_detail WHERE detail_id = {od.detail_id}"))
            conn.commit()
    
    # Optional: Verify error message
    assert '不能删除' in str(excinfo.value) or '未完成订单' in str(excinfo.value)
    
    # Clean up
    o.order_status = '已完成'
    db.session.commit()
    db.session.delete(o)
    db.session.commit()
