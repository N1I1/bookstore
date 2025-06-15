<!-- filepath: c:\Users\22905\Desktop\database\bookstore\frontend\src\views\Register.vue -->
<template>
  <div class="register-container">
    <el-card class="register-card">
      <h2>注册账号</h2>
      <el-form :model="form" :rules="rules" ref="registerFormRef" label-width="70px">
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            prefix-icon="el-icon-user"
            clearable
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
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
          <el-button type="primary" @click="onRegister">注册</el-button>
          <el-button @click="goLogin" type="text">返回登录</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const registerFormRef = ref(null)
const form = ref({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

function onRegister() {
  registerFormRef.value.validate((valid) => {
    if (valid) {
      ElMessage.success('注册成功！')
      router.push('/login')
    }
  })
}

function goLogin() {
  router.push('/login')
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: #f5f5f5;
}
.register-card {
  width: 350px;
  padding: 30px 20px;
}
</style>
