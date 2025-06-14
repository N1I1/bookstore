# 一、用户信息管理模块

### 1. 用户登录

**API：** `/api/login`

**方法：** `POST`

**输入：** 

```python
{
	username:				# 用户名
	password:				# 密码
	user_type:				# 用户类型（user 或 admin）
}
```

**输出：**

```python
# 数据不全
jsonify({"error": "Missing username, password, or user_type"}), 400

#登录成功
jsonify({
    "message": "Login successful", 
    "user_id": user.user_id, 
    "user_type": "user"
}), 200

jsonify({
    "message": "Login successful", 
    "user_id": admin.admin_id, 
    "user_type": "admin"
}), 200

#密码或账户或用户类型错误
jsonify({"error": "Invalid username or password"}), 401
jsonify({"error": "Unknown user type"}), 400
```



### 2. 用户注册

**API：** `/api/register`

**方法：** `POST`

**输入：**

```python
{
    username:               # 用户名
    password:               # 密码
    email:                  # 邮箱
    phone:                  # 手机号
    user_type:              # 用户类型（user 或 admin）
}
```

**输出：**

```python
# 数据不全
jsonify({"error": "Missing required fields"}), 400

# 用户名或邮箱已存在
jsonify({"error": "Username or email already exists"}), 400

# 用户类型无效
jsonify({"error": "Invalid user type"}), 400

# 注册成功（普通用户）
jsonify({
    "message": "User registered successfully", 
    "user_id": new_user.user_id
}), 201

# 注册成功（管理员）
jsonify({
    "message": "Admin registered successfully", 
    "admin_id": new_admin.admin_id
}), 201

# 服务器内部错误
jsonify({"error": "Internal server error"}), 500
```

好的，以下是按照你提供的格式重新编写的 **信息管理模块** 的 API 接口说明，不包含示例部分：

### 3. 用户信息更新

**API：** `/api/update_info`

**方法：** `POST`

**输入：**

```python
{
    user_id:                # 用户或管理员的ID，必填
    username:               # 新用户名（可选）
    password:               # 新密码（可选）
    email:                  # 新邮箱（可选）
    phone:                  # 新手机号（可选）
    default_address:        # 用户的默认地址（可选，仅对用户有效）
    user_type:              # 用户类型（"user" 或 "admin"），必填
}
```

**输出：**

```python
# 数据不全
jsonify({"error": "Missing user_id or user_type"}), 400

# 用户或管理员未找到
jsonify({"error": "User not found"}), 404
jsonify({"error": "Admin not found"}), 404

# 用户类型无效
jsonify({"error": "Invalid user type"}), 400

# 更新成功（用户）
jsonify({"message": "User information updated successfully"}), 200

# 更新成功（管理员）
jsonify({"message": "Admin information updated successfully"}), 200

# 服务器内部错误
jsonify({"error": "Internal server error"}), 500
```

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