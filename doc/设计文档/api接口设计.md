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

## 用户浏览记录（UserBrowse）

### 创建浏览记录

- **URL**：`POST /api/user_browse/`
- **请求体**（JSON）：
  ```json
  {
    "book_id": 1
  }
  ```
- **响应**：
  - 200 成功
    ```json
    {
      "browse_id": 1,
      "user_id": 1,
      "book_id": 1,
      "browse_time": "2025-06-15T12:34:56"
    }
    ```
  - 401 未登录
  - 400 缺少 book_id 或重复浏览记录

---

### 获取单条浏览记录

- **URL**：`GET /api/user_browse/<browse_id>`
- **响应**：
  - 200 成功
    ```json
    {
      "browse_id": 1,
      "user_id": 1,
      "book_id": 1,
      "browse_time": "2025-06-15T12:34:56"
    }
    ```
  - 401 未登录
  - 403 非本人
  - 404 记录不存在

---

### 删除浏览记录

- **URL**：`DELETE /api/user_browse/<browse_id>`
- **响应**：
  - 204 成功，无内容
  - 401 未登录
  - 404 记录不存在

---

### 获取用户所有浏览记录

- **URL**：`GET /api/user_browse/user/<user_id>`
- **说明**：仅本人可查
- **响应**：
  - 200 成功，返回浏览记录列表
    ```json
    [
      {
        "browse_id": 1,
        "user_id": 1,
        "book_id": 1,
        "browse_time": "2025-06-15T12:34:56"
      }
    ]
    ```
  - 401 未登录
  - 403 非本人

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

---

## 通知相关

### 主动触发新书通知

- **URL**：`POST /api/notify/new_book`
- **请求体**（JSON）：
  ```json
  {
    "book_id": 123
  }
  ```
- **响应**：
  - 200 成功：`{"message": "已向N位用户发送新书通知"}`
  - 400 缺少 book_id
  - 404 图书不存在

- **说明**：管理员添加新书后可调用此接口，向所有用户发送新书上架通知邮件，后续需要个性化服务，设置触发器等。

---

## 用户收藏（UserFavorite）

### 获取当前用户所有收藏

- **URL**：`GET /api/user_favorites/`
- **说明**：需登录，仅返回当前登录用户的收藏列表
- **响应**：
  - 200 成功，返回收藏列表
    ```json
    [
      {
        "book_id": 1,
        "favorite_time": "2025-06-16T12:34:56"
      }
    ]
    ```
  - 401 未登录：`{"error": "User not logged in"}`

---

### 添加收藏

- **URL**：`POST /api/user_favorites/`
- **请求体**（JSON）：
  ```json
  {
    "book_id": 1
  }
  ```
- **响应**：
  - 201 成功
    ```json
    {
      "book_id": 1,
      "favorite_time": "2025-06-16T12:34:56"
    }
    ```
  - 400 缺少字段：`{"error": "Missing required field: book_id"}`
  - 400 已收藏：`{"error": "Book already favorited"}`
  - 404 图书不存在：`{"error": "Book not found"}`
  - 401 未登录：`{"error": "User not logged in"}`

---

### 取消收藏

- **URL**：`DELETE /api/user_favorites/<book_id>` 
- **说明**：需登录，仅能取消自己的收藏
- **响应**：
  - 204 成功，无内容
  - 404 收藏不存在：`{"error": "Favorite record not found"}`
  - 401 未登录：`{"error": "User not logged in"}`
> 注意是 **book_id**

---

> 所有收藏相关接口均需先登录，登录后自动识别当前用户，无需传 user_id。

## 图书（Book）

### 获取所有书籍

- **URL**：`GET /api/books/`
- **说明**：获取所有书籍信息
- **响应**：
  - 200 成功，返回书籍列表
    ```json
    [
      {
        "book_id": 1,
        "title": "string",
        "author": "string",
        "isbn": "string",
        "publisher": "string",
        "price": 10.0,
        "discount": 0.9,
        "stock": 100,
        "description": "string",
        "image_url": "string"
      }
    ]
    ```

---

### 获取单本书籍

- **URL**：`GET /api/books/<book_id>`
- **说明**：获取指定书籍信息
- **响应**：
  - 200 成功
    ```json
    {
      "book_id": 1,
      "title": "string",
      "author": "string",
      "isbn": "string",
      "publisher": "string",
      "price": 10.0,
      "discount": 0.9,
      "stock": 100,
      "description": "string",
      "image_url": "string"
    }
    ```
  - 404 书籍不存在：`{"error": "Book not found"}`

---

### 创建新书籍

- **URL**：`POST /api/books/`
- **权限**：仅管理员（需登录，session 中有 `admin_id`）
- **请求体**（JSON）：
  ```json
  {
    "title": "string",
    "author": "string",
    "isbn": "string",
    "publisher": "string",
    "price": 10.0,
    "discount": 0.9,
    "stock": 100,
    "description": "string",
    "image_url": "string"
  }
  ```
- **响应**：
  - 201 成功：`{"message": "Book created", "book_id": 1}`
  - 400 缺少字段：`{"error": "Missing required field: 字段名"}`
  - 400 类型错误：`{"error": "Invalid data type"}`
  - 400 唯一性约束冲突：`{"error": "Book already exists or unique constraint failed"}`
  - 401 未授权：`{"error": "Unauthorized"}`
  - 500 服务器错误：`{"error": "Server error"}`

---

### 更新书籍信息

- **URL**：`PUT /api/books/<book_id>`
- **权限**：仅管理员
- **请求体**（JSON，可选字段）：
  ```json
  {
    "title": "string",
    "author": "string",
    "isbn": "string",
    "publisher": "string",
    "price": 10.0,
    "discount": 0.9,
    "stock": 100,
    "description": "string"
  }
  ```
- **响应**：
  - 200 成功，返回更新后的书籍信息
    ```json
    {
      "book_id": 1,
      "title": "string",
      "author": "string",
      "isbn": "string",
      "publisher": "string",
      "price": 10.0,
      "discount": 0.9,
      "stock": 100,
      "description": "string"
    }
    ```
  - 400 类型错误：`{"error": "Invalid data type"}`
  - 400 唯一性约束冲突：`{"error": "Unique constraint failed"}`
  - 401 未授权：`{"error": "Unauthorized"}`
  - 404 书籍不存在：`{"error": "Book not found"}`
  - 500 服务器错误：`{"error": "Server error"}`

---

### 删除书籍

- **URL**：`DELETE /api/books/<book_id>`
- **权限**：仅管理员
- **响应**：
  - 204 成功，无内容
  - 401 未授权：`{"error": "Unauthorized"}`
  - 404 书籍不存在：`{"error": "Book not found"}`

---

> 所有涉及书籍管理（新增、修改、删除）的接口均需管理员权限（session 中有 `admin_id`）。
