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

```json
session = {
	"user_id":int,
	"username":"string"
}
```

---

### 用户登出

- **URL**：`POST /api/login/logout`
- **响应**：
  - 200 成功：`{"message": "Logout successful"}`，`user_id`，`username`会自动删除

---

### 管理员登录

- **URL**：`POST /api/admin/login/`

- **请求体**（JSON）：

  ```json
  {
    "adminname": "string",
    "password": "string"
  }
  ```

- **响应**：

  - 200 成功：`{"message": "Login successful"}`
  - 401 用户名或密码错误 `{"error": "Invalid adminname or password"}`
  - 400 缺少字段 `{"error": "Missing adminname or password"}`

- **说明**：登录成功后，`session` 自动保存用户信息。

  ```json
  session = {
  	"admin_id":int,
  	"admin_username":"string"
  }
  ```

  


---

### 管理员登出

- **URL**：`POST /api/admin/login/logout`
- **响应**：
  - 200 成功：`{"message": "Logout successful"}`
- **说明**：登出时，`admin_id`，`admin_username`会自动删除

-----



## 用户信息

### 获取当前用户信息

- **URL**：`GET /api/users/`
- **说明**：需登录，仅返回当前登录用户的信息
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
  - 401 未登录：`{"error": "User not logged in"}`
  - 404 用户不存在

---

### 更新当前用户信息

- **URL**：`PUT /api/users/`
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
  - 401 未登录：`{"error": "User not logged in"}`
  - 404 用户不存在
  - 400 用户名或邮箱已存在

---

### 删除当前用户

- **URL**：`DELETE /api/users/`
- **说明**：需登录，仅能删除当前登录用户
- **响应**：
  - 204 成功，无内容
  - 401 未登录：`{"error": "User not logged in"}`
  - 404 用户不存在

> 此处可能会有问题，与 comment forum_post 表之间的关系需要再考虑一下

> 所有用户信息相关接口均需先登录，登录后使用 session 识别当前用户，无需传 user_id。

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

### 通过 book_id 获取相关帖子

- **URL**：`GET /api/forum_posts/by_book/<book_id>`
- **说明**：获取指定图书下的所有帖子
- **响应**：
  - 200 成功，返回该图书的帖子列表
    ```json
    [
      {
        "post_id": 1,
        "title": "帖子标题",
        "content": "帖子内容",
        "post_time": "2025-06-17T12:34:56",
        "browse_count": 10,
        "user_id": 1
      }
    ]
    ```
  - 404 未找到帖子：`{"error": "No posts found for this book"}`

### 通过 user_id 获取用户所有帖子

- **URL**：`GET /api/forum_posts/by_user/<user_id>`
- **说明**：获取指定用户发布的所有帖子
- **响应**：
  - 200 成功，返回该用户的帖子列表
    ```json
    [
      {
        "post_id": 1,
        "book_id": 1,
        "title": "string",
        "content": "string",
        "post_time": "2025-06-15T12:34:56",
        "browse_count": 10
      }
    ]
    ```
  - 404 未找到帖子：`{"error": "No posts found for this user"}`

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
      "book_title": "book_title",
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

- **URL**：`GET /api/user_browse/user/`
- **说明**：仅本人可查
- **响应**：
  - 200 成功，返回浏览记录列表
    ```json
    [
      {
        "browse_id": 1,
        "user_id": 1,
        "book_id": 1,
        "book_title": "book_title",
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

API：`/api/search_books/`

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
jsonify({"message": "Books found", "books": [list_of_books]}), 200

# 查询成功，但未找到相关图书
jsonify({"message": "No books found"}), 404

# 服务器内部错误
jsonify({"error": "Internal server error"}), 500
```

```json
[
    {
        "book_id": 1,
        "title": "The Hunger Games",
        "author": "Suzanne Collins",
        "isbn": "9780439023481",
        "publisher": "Scholastic",
        "price": "12.99",
        "discount": "1.00",
        "stock": 100,
        "description": "Book 1 of the Hunger Games series.",
        "image_url": "http://example.com/hunger_games.jpg"
    },
    {
        "book_id": 2,
        "title": "Catching Fire",
        "author": "Suzanne Collins",
        "isbn": "9780439023482",
        "publisher": "Scholastic",
        "price": "14.99",
        "discount": "1.00",
        "stock": 100,
        "description": "Book 2 of the Hunger Games series.",
        "image_url": "http://example.com/catching_fire.jpg"
    }
]

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
        "book_title": "book_title",
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
      "book_title": "book_title",
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

---

## 标签（Tag）

### 获取所有标签

- **URL**：`GET /api/tags/`
- **说明**：获取所有标签
- **响应**：
  - 200 成功，返回标签列表
    ```json
    [
      {
        "tag_id": 1,
        "name": "科幻"
      }
    ]
    ```

---

### 获取单个标签

- **URL**：`GET /api/tags/<tag_id>`
- **说明**：获取指定标签信息
- **响应**：
  - 200 成功
    ```json
    {
      "tag_id": 1,
      "name": "科幻"
    }
    ```
  - 404 标签不存在：`{"error": "Tag not found"}`

---

### 创建新标签

- **URL**：`POST /api/tags/`
- **权限**：仅管理员（需登录，session 中有 `admin_id`）
- **请求体**（JSON）：
  ```json
  {
    "name": "科幻"
  }
  ```
- **响应**：
  - 201 成功：`{"tag_id": 1, "name": "科幻"}`
  - 400 缺少字段：`{"error": "Missing required field: name"}`
  - 400 标签名已存在：`{"error": "Tag name already exists"}`
  - 401 未授权：`{"error": "Unauthorized"}`

---

### 修改标签

- **URL**：`PUT /api/tags/<tag_id>`
- **权限**：仅管理员
- **请求体**（JSON）：
  ```json
  {
    "name": "新标签名"
  }
  ```
- **响应**：
  - 200 成功：`{"tag_id": 1, "name": "新标签名"}`
  - 400 缺少字段：`{"error": "Missing required field: name"}`
  - 400 标签名已存在：`{"error": "Tag name already exists"}`
  - 401 未授权：`{"error": "Unauthorized"}`
  - 404 标签不存在：`{"error": "Tag not found"}`

---

### 删除标签

- **URL**：`DELETE /api/tags/<tag_id>`
- **权限**：仅管理员
- **响应**：
  - 204 成功，无内容
  - 401 未授权：`{"error": "Unauthorized"}`
  - 404 标签不存在：`{"error": "Tag not found"}`

---

### 获取标签下的所有书籍

- **URL**：`GET /api/tags/<tag_id>/books`
- **说明**：获取该标签下所有关联的书籍
- **响应**：
  - 200 成功，返回书籍列表
    ```json
    [
      {
        "book_id": 1,
        "title": "三体",
        "author": "刘慈欣",
        "isbn": "1234567890",
        "publisher": "出版社",
        "price": 39.9,
        "discount": 0.9,
        "stock": 100,
        "description": "科幻小说",
        "image_url": "http://example.com/cover.jpg"
      }
    ]
    ```
  - 404 标签不存在：`{"error": "Tag not found"}`

---

## 图书标签关联（BookTag）

### 添加图书标签关联

- **URL**：`POST /api/booktags/`
- **权限**：仅管理员
- **请求体**（JSON）：
  ```json
  {
    "book_id": 1,
    "tag_id": 2
  }
  ```
- **响应**：
  - 201 成功：`{"book_id": 1, "tag_id": 2}`
  - 400 缺少字段：`{"error": "Missing required fields: book_id and tag_id"}`
  - 400 已存在：`{"error": "Duplicate book tag"}`
  - 401 未授权：`{"error": "Unauthorized"}`
  - 500 服务器错误：`{"error": "Server error"}`

---

### 修改图书标签关联

- **URL**：`PUT /api/booktags/`
- **权限**：仅管理员
- **请求体**（JSON）：
  ```json
  {
    "book_id": 1,
    "tag_id": 2,
    "new_tag_id": 3
  }
  ```
- **响应**：
  - 200 成功：`{"book_id": 1, "tag_id": 3}`
  - 400 缺少字段：`{"error": "Missing required fields: book_id, tag_id, new_tag_id"}`
  - 400 已存在：`{"error": "Duplicate book tag"}`
  - 401 未授权：`{"error": "Unauthorized"}`
  - 404 原关联不存在：`{"error": "Book tag relation not found"}`
  - 500 服务器错误：`{"error": "Server error"}`

---

### 删除图书标签关联

- **URL**：`DELETE /api/booktags/`
- **权限**：仅管理员
- **请求体**（JSON）：
  ```json
  {
    "book_id": 1,
    "tag_id": 2
  }
  ```
- **响应**：
  - 204 成功，无内容
  - 400 缺少字段：`{"error": "Missing required fields: book_id and tag_id"}`
  - 401 未授权：`{"error": "Unauthorized"}`
  - 404 关联不存在：`{"error": "Book tag relation not found"}`
  - 500 服务器错误：`{"error": "Server error"}`

---

> 所有标签和图书标签关联相关接口的管理操作均需管理员权限（session 中有 `admin_id`）。

---



### 推荐书籍


​	• URL：`GET /api/recommend_books/recommend`


​	• 权限：仅用户（需要登录状态，通过`session`获取`user_id`）


​	• 请求参数（URL 参数，必选字段）：

​		• `user_id`：用户的唯一标识符（通过`session`自动获取，无需手动传递）


​	• 响应：


​		• 200 成功：返回推荐的书籍列表	


```json
    {
      "message": "Books recommended",
      "recommendations": [
        {
          "title": "string",
          "author": "string",
          "isbn": "string",
          "publisher": "string",
          "price": "string",
          "discount": "string",
          "stock": "integer",
          "description": "string",
          "image_url": "string",
          "recommend_type": "string",
          "recommend_reason": "string"
        }
      ]
    }
```

​		• 400 缺少用户ID：`{"error": "Missing user ID"}`


​		• 404 无推荐结果：`{"message": "No recommendations found"}`


​		• 500 服务器错误：`{"error": "Server error"}`

​	示例响应

​		成功（200）

```json
{
  "message": "Books recommended",
  "recommendations": [
    {
      "title": "The Hunger Games",
      "author": "Suzanne Collins",
      "isbn": "9780439023481",
      "publisher": "Scholastic",
      "price": "12.99",
      "discount": "1.00",
      "stock": 100,
      "description": "Book 1 of the Hunger Games series.",
      "image_url": "http://example.com/hunger_games.jpg",
      "recommend_type": "作者推荐",
      "recommend_reason": "作者：Suzanne Collins"
    },
    {
      "title": "Catching Fire",
      "author": "Suzanne Collins",
      "isbn": "9780439023482",
      "publisher": "Scholastic",
      "price": "14.99",
      "discount": "1.00",
      "stock": 100,
      "description": "Book 2 of the Hunger Games series.",
      "image_url": "http://example.com/catching_fire.jpg",
      "recommend_type": "标签推荐",
      "recommend_reason": "标签：Adventure"
    }
  ]
}
```



---

## 订单（Order）

### 获取订单列表

- **URL**：`GET /api/orders/`
- **说明**：用户获取自己的订单列表，管理员获取自己分配的订单列表
- **权限**：需登录
- **响应**：
  - 200 成功，返回订单列表
    ```json
    [
      {
        "order_id": 1,
        "order_status": "未支付",
        "order_time": "2025-06-16T12:34:56",
        "total_amount": 99.9
      }
    ]
    ```
  - 401 未授权：`{"error": "Unauthorized"}`

---

### 获取单个订单

- **URL**：`GET /api/orders/<order_id>`
- **说明**：用户或管理员获取自己相关的订单详情
- **权限**：需登录
- **响应**：
  - 200 成功
    ```json
    {
      "order_id": 1,
      "order_status": "已支付",
      "order_time": "2025-06-16T12:34:56",
      "payment_time": "2025-06-16T13:00:00",
      "ship_time": "2025-06-17T09:00:00",
      "get_time": "2025-06-18T10:00:00",
      "ship_address": "收货地址",
      "bill_address": "账单地址",
      "current_address": "当前运输地址",
      "shipper_phone": "12345678901",
      "biller_phone": "12345678901",
      "remark": "备注信息",
      "total_amount": 99.9,
      "details": [
        {
          "detail_id": 1,
          "book_id": 1,
          "book_title": "三体",
          "quantity": 2,
          "unit_price": 49.95
        }
      ]
    }
    ```
  - 401 未授权：`{"error": "Unauthorized"}`
  - 403 非本人/非分配管理员：`{"error": "Forbidden"}`
  - 404 订单不存在：`{"error": "Order not found"}`

---

### 创建订单

- **URL**：`POST /api/orders/`
- **权限**：仅用户
- **请求体**（JSON）：
  ```json
  {
    "details": [
      {
        "book_id": 1,
        "quantity": 2
      }
    ],
    "bill_address": "账单地址",
    "biller_phone": "12345678901",
    "remark": "备注"
  }
  ```
- **响应**：
  - 201 成功：`{"order_id": 1, "total_amount": 99.9}`
  - 400 缺少字段/参数错误/书籍不存在
  - 401 未授权

---

### 修改订单（仅未支付，用户可改账单地址、电话、备注）

- **URL**：`PUT /api/orders/<order_id>`
- **权限**：仅用户
- **请求体**（JSON，可选字段）：
  ```json
  {
    "bill_address": "新账单地址",
    "biller_phone": "新电话",
    "remark": "新备注"
  }
  ```
- **响应**：
  - 200 成功：`{"message": "Order updated successfully"}`
  - 400 订单状态不允许/无可更新字段
  - 401 未授权
  - 403 非本人
  - 404 订单不存在

---

### 删除订单（仅已完成，或订单取消）

- **URL**：`DELETE /api/orders/<order_id>`
- **权限**：仅用户
- **响应**：
  - 204 成功，无内容
  - 400 订单状态不允许
  - 401 未授权
  - 403 非本人
  - 404 订单不存在

---

### 用户支付订单

- **URL**：`POST /api/orders/<order_id>/pay`
- **权限**：仅用户
- **响应**：
  - 200 成功：`{"message": "Order paid successfully"}`
  - 400 订单状态不允许
  - 401 未授权
  - 403 非本人
  - 404 订单不存在

---

### 用户取消订单

- **URL**：`POST /api/orders/<order_id>/cancel`
- **权限**：仅用户
- **响应**：
  - 200 成功：`{"message": "Order cancelled successfully"}`
  - 400 订单状态不允许
  - 401 未授权
  - 403 非本人
  - 404 订单不存在

---

### 用户确认收货

- **URL**：`POST /api/orders/<order_id>/confirm`
- **权限**：仅用户
- **响应**：
  - 200 成功：`{"message": "Order confirmed successfully"}`
  - 400 订单状态不允许
  - 401 未授权
  - 403 非本人
  - 404 订单不存在

---

### 分配订单给管理员

- **URL**：`POST /api/orders/assign_admin`
- **权限**：仅管理员（需登录，`session`中有`admin_id`）
- **说明**：为所有“已支付且未分配管理员”的订单，自动分配给当前订单数最少的管理员。
- **请求体**：无
- **响应**：
  - 200 成功：`{"message": "已为N个订单分配管理员"}`
  - 401 未授权：`{"error": "Unauthorized"}`
  - 404 没有需要分配的订单：`{"error": "No orders to assign"}`
  - 404 没有可用管理员：`{"error": "No available admins"}`

> 后续可考虑设置每有新订单即更新或定时更新。

---

### 管理员发货

- **URL**：`POST /api/orders/<order_id>/ship`
- **权限**：仅管理员
- **请求体**（JSON，可选字段）：
  ```json
  {
    "ship_address": "收货地址",
    "current_address": "当前运输地址",
    "shipper_phone": "快递员电话"
  }
  ```
- **响应**：
  - 200 成功：`{"message": "Order shipped successfully"}`
  - 400 订单状态不允许
  - 401 未授权
  - 403 非分配管理员
  - 404 订单不存在

---

### 管理员修改运输地址

- **URL**：`PUT /api/orders/<order_id>/ship_address`
- **权限**：仅管理员
- **请求体**（JSON，至少一个字段）：
  ```json
  {
    "ship_address": "新收货地址",
    "current_address": "新运输地址"
  }
  ```
- **响应**：
  - 200 成功：`{"message": "Shipping address updated successfully"}`
  - 400 缺少字段
  - 401 未授权
  - 403 非分配管理员
  - 404 订单不存在

---

## 订单明细（OrderDetail）

### 获取订单明细

- **URL**：`GET /api/order_details/<detail_id>`
- **说明**：仅允许用户/管理员获取自己相关订单的明细
- **权限**：需登录
- **响应**：
  - 200 成功
    ```json
    {
      "detail_id": 1,
      "order_id": 1,
      "book_id": 1,
      "quantity": 2,
      "unit_price": 49.95,
      "book_title": "三体"
    }
    ```
  - 401 未授权
  - 403 非本人/非分配管理员
  - 404 明细不存在

---

> 订单相关接口均需登录，用户只能操作自己的订单，管理员只能操作分配给自己的订单。
> 分配订单给管理员的功能还需要完善。

## 用户购物车（UserCart）

### 获取当前用户购物车

- **URL**：`GET /api/user_cart/`
- **说明**：需登录，仅返回当前登录用户的购物车项列表
- **响应**：
  - 200 成功，返回购物车项列表
    ```json
    [
      {
        "cart_id": 1,
        "book_id": 1,
        "book_title": "书名",
        "book_price": 39.9,
        "book_image": "http://example.com/cover.jpg",
        "quantity": 2,
        "add_time": "2025-06-17T12:34:56"
      }
    ]
    ```
  - 401 未登录：`{"error": "Not logged in"}`

---

### 添加图书到购物车

- **URL**：`POST /api/user_cart/`
- **请求体**（JSON）：
  ```json
  {
    "book_id": 1,
    "quantity": 2   // 可选，默认为1
  }
  ```
- **响应**：
  - 201 成功：`{"message": "Added to cart", "cart_id": 1}`
  - 400 book_id/quantity 非法：`{"error": "Invalid book_id or quantity"}`
  - 400 已存在：`{"error": "Book already in cart"}`
  - 404 图书不存在：`{"error": "Book not found"}`
  - 401 未登录：`{"error": "Not logged in"}`

---

### 更新购物车项数量

- **URL**：`PUT /api/user_cart/`
- **请求体**（JSON）：
  ```json
  {
    "cart_id": 1,
    "quantity": 3
  }
  ```
- **响应**：
  - 200 成功：`{"message": "Cart updated"}`
  - 400 cart_id/quantity 非法：`{"error": "Invalid cart_id or quantity"}`
  - 404 购物车项不存在：`{"error": "Cart item not found"}`
  - 401 未登录：`{"error": "Not logged in"}`

---

### 删除购物车项

- **URL**：`DELETE /api/user_cart/`
- **请求体**（JSON）：
  ```json
  {
    "cart_id": 1
  }
  ```
- **响应**：
  - 204 成功：`{"message": "Cart item deleted"}`
  - 400 cart_id 非法：`{"error": "Invalid cart_id"}`
  - 404 购物车项不存在：`{"error": "Cart item not found"}`
  - 401 未登录：`{"error": "Not logged in"}`

---

> 所有购物车相关接口均需先登录，登录后自动识别当前用户，无需传 user_id。
