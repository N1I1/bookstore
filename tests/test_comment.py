import pytest
from app import db
from app.models.comment import Comment
from app.models.forumpost import ForumPost
from app.models.user import User

@pytest.fixture
def user(app):
    """创建一个测试用户"""
    user = User(username="testuser", 
                password="testpass",
                email="example@example.com",
                phone="1234567890")
    db.session.add(user)
    db.session.commit()
    yield user
    db.session.delete(user)
    db.session.commit()

@pytest.fixture
def forum_post(app, user):
    """创建一个测试帖子"""
    post = ForumPost(user_id=user.user_id, content="test post")
    db.session.add(post)
    db.session.commit()
    yield post
    # 清理相关评论
    comments = Comment.query.filter_by(post_id=post.post_id).all()
    for comment in comments:
        db.session.delete(comment)
    db.session.delete(post)
    db.session.commit()

@pytest.fixture
def login_user(client, user):
    """模拟登录，设置 session"""
    with client.session_transaction() as sess:
        sess['user_id'] = user.user_id

@pytest.fixture
def sample_comment(app, forum_post, user):
    """创建一个测试评论"""
    comment = Comment(post_id=forum_post.post_id, user_id=user.user_id, content="test comment")
    db.session.add(comment)
    db.session.commit()
    yield comment
    db.session.delete(comment)
    db.session.commit()

def test_get_nonexistent_comment(client, login_user):
    """测试获取不存在的评论"""
    response = client.get('/api/comments/99999')
    assert response.status_code == 404
    assert b"Comment not found" in response.data

def test_create_comment(client, login_user, forum_post):
    """测试创建评论"""
    response = client.post('/api/comments/', json={
        "post_id": forum_post.post_id,
        "content": "This is a test comment"
    })
    assert response.status_code == 201
    assert b"Comment created successfully" in response.data

def test_create_comment_missing_fields(client, login_user):
    """测试缺少字段"""
    response = client.post('/api/comments/', json={
        "post_id": 1
    })
    assert response.status_code == 400
    assert b"Missing required fields" in response.data

def test_get_single_comment(client, login_user, sample_comment):
    """测试获取单条评论"""
    response = client.get(f'/api/comments/{sample_comment.comment_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data["comment_id"] == sample_comment.comment_id
    assert data["username"] == "testuser"
    assert data["content"] == "test comment"

def test_update_comment(client, login_user, sample_comment):
    """测试更新评论"""
    response = client.put(f'/api/comments/{sample_comment.comment_id}', json={
        "content": "updated comment"
    })
    assert response.status_code == 200
    assert b"Comment updated successfully" in response.data

def test_delete_comment(client, login_user, sample_comment):
    """测试删除评论（逻辑删除）"""
    response = client.delete(f'/api/comments/{sample_comment.comment_id}')
    assert response.status_code == 204
    # 检查数据库中is_deleted为True
    comment = db.session.get(Comment, sample_comment.comment_id)
    assert comment.is_deleted is True

def test_unauthorized_update(client, sample_comment):
    """测试未登录或非本人不能修改评论"""
    response = client.put(f'/api/comments/{sample_comment.comment_id}', json={
        "content": "hack"
    })
    assert response.status_code == 403

def test_unauthorized_delete(client, sample_comment):
    """测试未登录或非本人不能删除评论"""
    response = client.delete(f'/api/comments/{sample_comment.comment_id}')
    assert response.status_code == 403

def test_update_nonexistent_comment(client, login_user):
    """测试修改不存在的评论"""
    response = client.put('/api/comments/99999', json={
        "content": "should not work"
    })
    assert response.status_code == 404
    assert b"Comment not found" in response.data

def test_delete_nonexistent_comment(client, login_user):
    """测试删除不存在的评论"""
    response = client.delete('/api/comments/99999')
    assert response.status_code == 404
    assert b"Comment not found" in response.data

def test_get_comment_tree(client, login_user, forum_post, user):
    """测试获取评论树结构"""
    # 创建父评论
    parent = Comment(post_id=forum_post.post_id, user_id=user.user_id, content="parent comment")
    db.session.add(parent)
    db.session.commit()
    # 创建子评论
    child = Comment(post_id=forum_post.post_id, user_id=user.user_id, content="child comment", parent_comment_id=parent.comment_id)
    db.session.add(child)
    db.session.commit()

    response = client.get(f'/api/comments/tree/{forum_post.post_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert any(c["content"] == "parent comment" for c in data)
    # 检查子评论在replies中
    parent_node = next(c for c in data if c["content"] == "parent comment")
    assert any(r["content"] == "child comment" for r in parent_node["replies"])

    # 清理
    db.session.delete(child)
    db.session.delete(parent)
    db.session.commit()
