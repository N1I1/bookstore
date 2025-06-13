<!-- filepath: frontend/src/views/Login.vue -->
<template>
  <div class="login-container">
    <el-card class="login-card">
      <div class="login-title">用户登录</div>
      <el-form :model="form" :rules="rules" ref="loginForm" label-width="0">
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名/邮箱"
            prefix-icon="el-icon-user"
            clearable
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            prefix-icon="el-icon-lock"
            show-password
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" style="width:100%;" @click="onLogin" :loading="loading">
            登录
          </el-button>
        </el-form-item>
        <div class="login-links">
          <el-link href="/register" type="primary">注册账号</el-link>
          <el-link href="#" type="info" style="float:right;">忘记密码？</el-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const form = ref({
  username: '',
  password: ''
})
const rules = {
  username: [{ required: true, message: '请输入用户名或邮箱', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}
const loading = ref(false)
const loginForm = ref(null)

const onLogin = () => {
  loginForm.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      // 这里预留与后端 Flask 的接口
      // 假设后端接口为 POST /api/login
      const res = await axios.post('/api/login', {
        username: form.value.username,
        password: form.value.password
      })
      if (res.data.success) {
        ElMessage.success('登录成功')
        // 登录成功后的跳转或处理
        window.location.href = '/'
      } else {
        ElMessage.error(res.data.message || '登录失败')
      }
    } catch (e) {
      ElMessage.error('网络错误或服务器异常')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #e0e7ff 0%, #f9fafb 100%);
}
.login-card {
  width: 350px;
  padding: 30px 20px 20px 20px;
  box-shadow: 0 2px 12px #00000010;
  border-radius: 12px;
}
.login-title {
  text-align: center;
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 25px;
  color: #409eff;
  letter-spacing: 2px;
}
.login-links {
  margin-top: 10px;
  display: flex;
  justify-content: space-between;
}
</style>