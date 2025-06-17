import pytest
import uuid
from app import db
from app.models.user import User
from app.models.book import Book
from app.models.usercart import UserCart

def random_str():
    return str(uuid.uuid4())

@pytest.fixture
def test_user(app):
    user = User(username=f"user_{random_str()}", 
                password="testpass",
                email=f"user_{random_str()}@example.com",
                phone="1234567890")
    db.session.add(user)
    db.session.commit()
    yield user
    user_cart_items = UserCart.query.filter_by(user_id=user.user_id).all()
    for item in user_cart_items:
        db.session.delete(item)
    db.session.commit()
    db.session.delete(user)
    db.session.commit()

@pytest.fixture
def login_user(client, test_user):
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.user_id

@pytest.fixture
def test_book(app):
    book = Book(
        title=f"Book_{random_str()}",
        author="Author",
        price=10.0,
        isbn=random_str()[:13],
        stock=100,
        publisher="Publisher",
        description="This is a test book.",
        discount=0.1,
        image_url="http://example.com/image.jpg"
    )
    db.session.add(book)
    db.session.commit()
    yield book
    user_cart_items = UserCart.query.filter_by(book_id=book.book_id).all()
    for item in user_cart_items:
        db.session.delete(item)
    db.session.commit()
    db.session.delete(book)
    db.session.commit()

@pytest.fixture
def cart_item(app, test_user, test_book):
    item = UserCart(user_id=test_user.user_id, book_id=test_book.book_id, quantity=2)
    db.session.add(item)
    db.session.commit()
    yield item
    item_in_db = db.session.get(UserCart, item.cart_id)
    if item_in_db:
        db.session.delete(item)
        db.session.commit()

def test_add_to_cart(client, login_user, test_book):
    response = client.post('/api/user_cart/', json={
        "book_id": test_book.book_id,
        "quantity": 3
    })
    assert response.status_code == 201
    assert b"Added to cart" in response.data

def test_get_cart(client, login_user, cart_item):
    response = client.get('/api/user_cart/')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert any(item['book_id'] == cart_item.book_id for item in data)

def test_update_cart_quantity(client, login_user, cart_item):
    response = client.put('/api/user_cart/', json={
        "cart_id": cart_item.cart_id,
        "quantity": 5
    })
    assert response.status_code == 200
    assert b"Cart updated" in response.data
    db.session.refresh(cart_item)
    assert cart_item.quantity == 5

def test_delete_cart_item(client, login_user, cart_item):
    response = client.delete('/api/user_cart/', json={
        "cart_id": cart_item.cart_id
    })
    assert response.status_code == 204
    assert db.session.get(UserCart, cart_item.cart_id) is None

def test_add_cart_invalid_book(client, login_user):
    response = client.post('/api/user_cart/', json={
        "book_id": 99999999,
        "quantity": 1
    })
    assert response.status_code == 404

def test_cart_requires_login(client, test_book):
    response = client.post('/api/user_cart/', json={
        "book_id": test_book.book_id,
        "quantity": 1
    })
    assert response.status_code == 401

def test_cart_requires_login(client, test_book):
    response = client.post('/api/user_cart/', json={
        "book_id": test_book.book_id,
        "quantity": 1
    })
    assert response.status_code == 401
    response = client.get('/api/user_cart/')
    assert response.status_code == 401
    response = client.put('/api/user_cart/', json={"cart_id": 1, "quantity": 1})
    assert response.status_code == 401
    response = client.delete('/api/user_cart/', json={"cart_id": 1})
    assert response.status_code == 401

def test_add_cart_invalid_bookid_or_quantity(client, login_user):
    response = client.post('/api/user_cart/', json={
        "book_id": None,
        "quantity": 1
    })
    assert response.status_code == 400
    response = client.post('/api/user_cart/', json={
        "book_id": 1,
        "quantity": 0
    })
    assert response.status_code == 400

def test_add_cart_book_not_found(client, login_user):
    response = client.post('/api/user_cart/', json={
        "book_id": 99999999,
        "quantity": 1
    })
    assert response.status_code == 404

def test_update_cart_invalid_cartid_or_quantity(client, login_user):
    response = client.put('/api/user_cart/', json={
        "cart_id": None,
        "quantity": 1
    })
    assert response.status_code == 400
    response = client.put('/api/user_cart/', json={
        "cart_id": 1,
        "quantity": 0
    })
    assert response.status_code == 400

def test_delete_cart_invalid_cartid(client, login_user):
    response = client.delete('/api/user_cart/', json={
        "cart_id": None
    })
    assert response.status_code == 400

def test_update_cart_item_not_found(client, login_user):
    response = client.put('/api/user_cart/', json={
        "cart_id": 99999999,
        "quantity": 1
    })
    assert response.status_code == 404

def test_delete_cart_item_not_found(client, login_user):
    response = client.delete('/api/user_cart/', json={
        "cart_id": 99999999
    })
    assert response.status_code == 404

def test_add_cart_book_already_in_cart(client, login_user, cart_item):
    response = client.post('/api/user_cart/', json={
        "book_id": cart_item.book_id,
        "quantity": 1
    })
    assert response.status_code == 400
    assert b"Book already in cart" in response.data
