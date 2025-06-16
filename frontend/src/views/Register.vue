<!-- filepath: c:\Users\22905\Desktop\database\bookstore\frontend\src\views\Register.vue -->
<template>
  <div class="register-wrapper">
    <el-card class="register-card">
      <!-- 左上角返回登录按钮 -->
      <el-button class="back-login-btn" type="text" @click="goLogin" icon="el-icon-arrow-left">
        返回登录
      </el-button>
      <h2 class="register-title">用户注册</h2>
      <el-form :model="form" ref="registerForm" label-width="80px" class="register-form">
        <el-form-item label="用户名" prop="username" required>
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="密码" prop="password" required>
          <el-input v-model="form.password" type="password" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email" required>
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone" required>
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="register">注册</el-button>
        </el-form-item>
      </el-form>
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
  password: '',
  email: '',
  phone: ''
})

async function register() {
  try {
    const res = await axios.post('/api/register/', form.value)
    if (res.status === 201) {
      ElMessage.success('注册成功')
      router.push('/home')
    }
  } catch (err) {
    if (err.response && err.response.status === 400) {
      ElMessage.error(err.response.data.message || '注册失败')
    } else {
      ElMessage.error('网络错误')
    }
  }
}

function goLogin() {
  router.push('/login')
}
</script>

<style scoped>
.register-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}
.register-card {
  width: 400px;
  padding: 32px 24px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  background: #fff;
  position: relative;
}
.back-login-btn {
  position: absolute;
  top: 16px;
  left: 16px;
  color: #409eff;
  font-size: 15px;
}
.register-title {
  text-align: center;
  margin-bottom: 24px;
  font-weight: bold;
  font-size: 24px;
  color: #409eff;
  letter-spacing: 2px;
}
.register-form {
  margin-top: 0;
}
</style>