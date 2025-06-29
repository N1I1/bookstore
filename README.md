## Bookstore Management System

网上书店管理系统。

## 功能需求

1. **系统管理**
   - 用户注册、注销、登录、修改密码

2. **图书查询**
   - 图书信息包括：书名、作者、编号（ISBN）、出版社、定价、折扣、目录、库存状态等
   - 支持按书名、作者、出版社等信息模糊查询

3. **订单管理**
   - 用户可下订单，系统检查订单有效性后发送到用户邮箱
   - 用户付款后，通过邮局发货，并对订单流程进行跟踪管理

4. **信息服务**
   - 跟踪用户购买或浏览习惯，有相关新书时通过电子邮件通知用户

5. **用户论坛**
   - 用户可发表书评或进行投诉

6. **数据备份与恢复**
   - 支持系统数据的备份与恢复

## 技术栈

TODO

## 项目结构

```
   
├─backend  
│  ├─app  
│  │  ├─models  
│  │  ├─routes  
│  │  │  ├─auth  
│  │  │  ├─services  
│  │  │  ├─tables  
│  │  │  └─views  
│  ├─data  
│  │  └─test  
│  ├─migrations  
│  │  ├─versions  
│  ├─static  
│  ├─templates  
├─doc  
│  ├─数据库部署  
│  └─设计文档  
├─frontend  
│  └─src  
│      ├─components  
│      ├─router  
│      └─views  
└─tests  
  
  
```
## E-R图

![image](https://github.com/user-attachments/assets/0ab8185b-b178-407e-bb12-e31873d7d4b9)

