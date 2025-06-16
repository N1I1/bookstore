<!-- filepath: c:\Users\22905\Desktop\database\bookstore\frontend\src\views\Login.vue -->
<template>
  <div class="login-wrapper">
    <el-card class="login-card">
      <h2 class="login-title">用户登录</h2>
      <el-form :model="form" ref="loginForm" label-width="80px" class="login-form">
        <el-form-item label="用户名" prop="username" required>
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="密码" prop="password" required>
          <el-input v-model="form.password" type="password" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="login">登录</el-button>
        </el-form-item>
      </el-form>
      <div class="register-link">
        还没有账号？
        <el-link type="primary" @click="goRegister">注册账号</el-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const router = useRouter()
const form = ref({
  username: '',
  password: ''
})

async function login() {
  try {
    const res = await axios.post('/api/login/', form.value, { withCredentials: true })
    if (res.status === 200) {
      ElMessage.success('登录成功')
      router.push('/home')
    }
  } catch (err) {
    if (err.response && err.response.status === 401) {
      ElMessage.error('用户名或密码错误')
    } else if (err.response && err.response.status === 400) {
      ElMessage.error('请填写完整信息')
    } else {
      ElMessage.error('网络错误')
    }
  }
}

function goRegister() {
  router.push('/register')
}
</script>

<style scoped>
.login-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}
.login-card {
  width: 400px;
  padding: 32px 24px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  background: #fff;
}
.login-title {
  text-align: center;
  margin-bottom: 24px;
  font-weight: bold;
  font-size: 24px;
  color: #409eff;
  letter-spacing: 2px;
}
.login-form {
  margin-top: 0;
}
.register-link {
  text-align: center;
  margin-top: 16px;
  font-size: 15px;
}
</style>