<!-- filepath: c:\Users\22905\Desktop\database\bookstore\frontend\src\views\UserInfo.vue -->
<template>
  <div class="user-info-wrapper">
    <el-card class="user-info-card">
      <h2 class="user-info-title">个人信息</h2>
      <el-form :model="user" :rules="rules" ref="userForm" label-width="100px" class="user-info-form">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="user.username" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="user.email" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="user.phone" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="user.password" type="password" placeholder="如需修改请填写" show-password />
        </el-form-item>
        <el-form-item label="默认地址" prop="default_address">
          <el-input v-model="user.default_address" />
        </el-form-item>
        <el-form-item label="注册时间">
          <el-input v-model="user.register_time" disabled />
        </el-form-item>
        <el-form-item label="上次登录">
          <el-input v-model="user.last_login_time" disabled />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="updateUser">保存修改</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const user = ref({
  username: '',
  email: '',
  phone: '',
  default_address: '',
  register_time: '',
  last_login_time: ''
})

onMounted(async () => {
  try {
    const res = await axios.get('/api/users/<user_id>', { withCredentials: true })
    if (res.status === 200) {
      Object.assign(user.value, res.data)
    }
  } catch (err) {
    if (err.response && err.response.status === 401) {
      ElMessage.error('请先登录')
    } else if (err.response && err.response.status === 403) {
      ElMessage.error('无权访问')
    } else if (err.response && err.response.status === 404) {
      ElMessage.error('用户不存在')
    } else {
      ElMessage.error('获取信息失败')
    }
  }
})

async function updateUser() {
  try {
    // 只提交有变动的字段
    const updateData = {
      username: user.value.username,
      email: user.value.email,
      phone: user.value.phone,
      default_address: user.value.default_address
    }
    if (user.value.password) updateData.password = user.value.password

    const res = await axios.put(`/api/users/${userId}`, updateData, { withCredentials: true })
    if (res.status === 200) {
      ElMessage.success('信息修改成功')
      user.value.password = ''
    }
  } catch (err) {
    if (err.response && err.response.status === 401) {
      ElMessage.error('请先登录')
    } else if (err.response && err.response.status === 403) {
      ElMessage.error('无权修改他人信息')
    } else if (err.response && err.response.status === 404) {
      ElMessage.error('用户不存在')
    } else if (err.response && err.response.status === 400) {
      ElMessage.error(err.response.data.message || '用户名或邮箱已存在')
    } else {
      ElMessage.error('修改失败')
    }
  }
}
</script>

<style scoped>
.user-info-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}
.user-info-card {
  width: 500px;
  padding: 32px 24px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  background: #fff;
}
.user-info-title {
  text-align: center;
  margin-bottom: 24px;
  font-weight: bold;
  font-size: 24px;
  color: #409eff;
  letter-spacing: 2px;
}
.user-info-form {
  margin-top: 0;
}
</style>