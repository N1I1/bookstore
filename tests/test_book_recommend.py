# import pytest
# from app.models import Book, BookTag, UserBrowse, UserCart, UserFavorite
# from app import db


# def test_recommend_normal(client):
#     # 测试正常推荐
#     response = client.post('/api/recommend_books/', json={"user_id": 40})

#     data = response.get_json()
#     print("Response JSON content:", data)  # 输出 JSON 内容
#     assert response.status_code == 200

#     assert data["message"] == "Books recommended"
#     assert "recommendations" in data
#     assert len(data["recommendations"]) > 1
#     # 输出data的内容、
#     print("Response JSON content:", data)  # 输出 JSON 内容

# def test_recommend_missing_user_id(client):
#     # 测试缺少用户 ID
#     response = client.post('/api/recommend_books/', json={})
#     assert response.status_code == 400
#     data = response.get_json()
#     assert data["error"] == "Missing user ID"

# def test_recommend_no_results(client):
#     # 测试无推荐结果
#     response = client.post('/api/recommend_books/', json={"user_id": 28})
#     assert response.status_code == 404
#     data = response.get_json()
#     assert data["message"] == "No recommendations found"

    