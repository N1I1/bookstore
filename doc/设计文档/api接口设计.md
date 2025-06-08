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

 

好的，以下是按照你提供的格式编写的用户注册功能的 API 文档，使用 Markdown 语法的代码块表示：

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







### 3. 信息管理