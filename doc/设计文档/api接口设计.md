# Bookstore API 接口文档

## 认证相关

### 用户注册

- **URL**：`POST /api/register/`
- **请求体**（JSON）：
  ```json
  {
    "username": "string",
    "password": "string",
    "email": "string",
    "phone": "string"
  }
  ```
- **响应**：
  - 201 成功：`{"message": "User registered successfully", "user_id": 1}`
  - 400 缺少字段或用户名/邮箱已存在

---

### 用户登录

- **URL**：`POST /api/login/`
- **请求体**（JSON）：
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **响应**：
  - 200 成功：`{"message": "Login successful"}`
  - 401 用户名或密码错误
  - 400 缺少字段

- **说明**：登录成功后，`session` 自动保存用户信息。

---

### 用户登出

- **URL**：`POST /api/login/logout`
- **响应**：
  - 200 成功：`{"message": "Logout successful"}`

---

## 用户信息

### 获取用户信息

- **URL**：`GET /api/users/<user_id>`
- **说明**：仅本人可查
- **响应**：
  - 200 成功
    ```json
    {
      "username": "string",
      "email": "string",
      "phone": "string",
      "register_time": "2025-06-15T12:34:56",
      "last_login_time": "2025-06-15T12:34:56",
      "default_address": "string"
    }
    ```
  - 401 未登录
  - 403 非本人
  - 404 用户不存在

---

### 更新用户信息

- **URL**：`PUT /api/users/<user_id>`
- **请求体**（JSON，可选字段）：
  ```json
  {
    "username": "string",
    "email": "string",
    "phone": "string",
    "password": "string",
    "default_address": "string"
  }
  ```
- **响应**：
  - 200 成功：`{"message": "User updated successfully"}`
  - 401 未登录
  - 403 非本人
  - 404 用户不存在
  - 400 用户名或邮箱已存在

---

### 删除用户

- **URL**：`DELETE /api/users/<user_id>`
- **响应**：
  - 204 成功，无内容
  - 401 未登录
  - 403 非本人
  - 404 用户不存在

> 此处可能会有问题，与 comment forum_post 表之间的关系需要再考虑一下

---

## 帖子（ForumPost）

### 创建帖子

- **URL**：`POST /api/forum_posts/`
- **请求体**（JSON）：
  ```json
  {
    "title": "string",          // 可为空，为空则设置为 Untitled Post
    "content": "string",        // 必填
    "book_id": 1                // 可选
  }
  ```
- **响应**：
  - 201 成功：`{"Message": "Post created successfully", "post_id": 1}`
  - 401 未登录
  - 400 缺少内容或 book_id 不存在

---

### 获取单个帖子

- **URL**：`GET /api/forum_posts/<post_id>`
- **响应**：
  - 200 成功
    ```json
    {
      "post_id": 1,
      "book_id": 1,
      "title": "string",
      "content": "string",
      "post_time": "2025-06-15T12:34:56",
      "browse_count": 10
    }
    ```
  - 404 帖子不存在

---

### 更新帖子

- **URL**：`PUT /api/forum_posts/<post_id>`
- **请求体**（JSON）：
  ```json
  {
    "title": "string",
    "content": "string",
    "book_id": 1
  }
  ```
- **响应**：
  - 200 成功：`{"message": "Post updated successfully"}`
  - 401 未登录
  - 403 非本人
  - 404 帖子不存在
  - 400 缺少标题/内容或 book_id 不存在

---

### 删除帖子

- **URL**：`DELETE /api/forum_posts/<post_id>`
- **响应**：
  - 204 成功，无内容
  - 401 未登录
  - 403 非本人
  - 404 帖子不存在

---

### 获取随机帖子

- **URL**：`GET /api/forum_posts/get_posts?limit=5`
- **响应**：
  - 200 成功，返回帖子列表
  - 404 没有帖子

---

## 评论（Comment）

### 创建评论

- **URL**：`POST /api/comments/`
- **请求体**（JSON）：
  ```json
  {
    "post_id": 1,
    "content": "string",
    "parent_comment_id": 2   // 可选，回复某条评论
  }
  ```
- **响应**：
  - 201 成功：`{"message": "Comment created successfully"}`
  - 400 缺少字段或 post_id/user_id 不合法

---

### 获取单条评论

- **URL**：`GET /api/comments/<comment_id>`
- **响应**：
  - 200 成功
    ```json
    {
      "comment_id": 1,
      "username": "string",
      "content": "string",
      "comment_time": "2025-06-15T12:34:56"
    }
    ```
  - 404 评论不存在

---

### 更新评论

- **URL**：`PUT /api/comments/<comment_id>`
- **请求体**（JSON）：
  ```json
  {
    "content": "string",
    "parent_comment_id": 2   // 可选
  }
  ```
- **响应**：
  - 200 成功：`{"message": "Comment updated successfully"}`
  - 403 非本人
  - 404 评论不存在
  - 400 post_id/user_id 不合法

---

### 删除评论

- **URL**：`DELETE /api/comments/<comment_id>`
- **响应**：
  - 204 成功：`{"message": "Comment deleted"}`
  - 403 非本人
  - 404 评论不存在

---

### 获取评论树

- **URL**：`GET /api/comments/tree/<post_id>`
- **响应**：
  - 200 成功，返回该帖子的评论树（嵌套结构）
    ```json
    [
      {
        "comment_id": 1,
        "username": "string",
        "content": "string",
        "comment_time": "2025-06-15T12:34:56",
        "replies": [
          {
            "comment_id": 2,
            "username": "string",
            "content": "string",
            "comment_time": "2025-06-15T12:35:00",
            "replies": [ ... ]
          }
        ]
      }
    ]
    ```

---

## 说明

- 所有需要登录的接口，需先调用 `/api/login/` 登录，后续请求自动带 session。
- 所有接口均返回标准 JSON。


### 4. 图书查询

API：`/api/search_books`

方法：`POST`

输入：


```python
{
    query:                  # 查询字符串，必填
}
```


输出：


```python
# 数据不全
jsonify({"error": "Missing search query"}), 400

# 查询成功，找到相关图书
jsonify({"message": "Books found", "book_ids": [list_of_book_ids]}), 200

# 查询成功，但未找到相关图书
jsonify({"message": "No books found"}), 404

# 服务器内部错误
jsonify({"error": "Internal server error"}), 500
```