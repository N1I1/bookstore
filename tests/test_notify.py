import pytest
import json
from app import create_app, db
from app.models import Book, Tag, UserBrowse, UserCart, UserFavorite, User, book_tag


@pytest.fixture
def app():
    app = create_app()
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

# def test_register_user(client):
#     # 注册用户
#     register_data = {
#         "username": "test_user",
#         "password": "test_password",
#         "email": "2022212153@mail.hfut.edu.cn",
#         "phone": "1234567890"
#     }
#     response = client.post('/api/register/', json=register_data)
#     assert response.status_code == 201, "Failed to register user"

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

# def test_setup_data(client, login_user):
#     # 设置测试数据
#     user_id = login_user
    
#     # 添加测试书籍
#     book1 = Book(title="Book 1", author="Author A", isbn="1234567890", publisher="Publisher A", price=10.0, discount=0.8, stock=10, description="Description 1", image_url="url1")
#     book2 = Book(title="Book 2", author="Author A", isbn="0987654321", publisher="Publisher B", price=20.0, discount=0.9, stock=5, description="Description 2", image_url="url2")
#     book3 = Book(title="Book 3", author="Author B", isbn="1122334455", publisher="Publisher C", price=15.0, discount=0.85, stock=8, description="Description 3", image_url="url3")
#     book4 = Book(title="Book 4", author="Author A", isbn="1122334456", publisher="Publisher C", price=15.0, discount=0.85, stock=8, description="Description 4", image_url="url4")
#     book5 = Book(title="Book 5", author="Author B", isbn="1122334457", publisher="Publisher D", price=15.0, discount=0.85, stock=8, description="Description 5", image_url="url5")
#     book6 = Book(title="Book 6", author="Author B", isbn="1122334458", publisher="Publisher C", price=15.0, discount=0.85, stock=8, description="Description 6", image_url="url6")
#     db.session.add_all([book1, book2, book3, book4, book5, book6])
#     db.session.commit()

#     # 添加测试标签
#     tag1 = Tag(name="Tag 1")
#     tag2 = Tag(name="Tag 2")
#     db.session.add_all([tag1, tag2])
#     db.session.commit()

#     # 关联书籍和标签
#     book1.tags.append(tag1)
#     book2.tags.append(tag2)
#     book4.tags.append(tag1)
#     book5.tags.append(tag2)
#     book6.tags.append(tag1)
#     db.session.commit()

#     # 添加用户浏览、购物车、收藏记录
#     browse1 = UserBrowse(user_id=user_id, book_id=book1.book_id)
#     browse2 = UserBrowse(user_id=user_id, book_id=book2.book_id)
#     cart1 = UserCart(user_id=user_id, book_id=book3.book_id, quantity=1)
#     favorite1 = UserFavorite(user_id=user_id, book_id=book1.book_id)
#     db.session.add_all([browse1, browse2, cart1, favorite1])
#     db.session.commit()

#     # 断言数据库中书的数量为6
#     assert db.session.query(Book).count() == 6, "Failed to add books to database"

def test_notify(client):
    # 通过isbn号查询
    data = {'book_id':db.session.query(Book).filter_by(isbn='1122334458').first().book_id}
    response = client.post('/api/notify/new_book', json=data)
    print(response.json)
    assert response.status_code == 200, "Failed to notify user"





# def test_delete_data(client):
#     db.session.query(UserFavorite).delete()
#     db.session.query(UserCart).delete()
#     db.session.query(UserBrowse).delete()
#     db.session.query(book_tag).delete()  # 删除 book_tag 关联表中的记录
#     db.session.query(Book).delete()
#     db.session.query(Tag).delete()
#     db.session.query(User).delete()
#     db.session.commit()


