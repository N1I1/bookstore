<template>
  <div class="admin-home">
    <!-- 顶部栏 -->
    <header class="admin-header">
      <div class="admin-header-left">
        <img src="https://cdn.jsdelivr.net/gh/element-plus/element-plus@2.3.13/docs/public/logo-small.svg" class="logo" />
        <span class="admin-title">图书管理后台</span>
      </div>
      <el-button
        type="danger"
        icon="el-icon-switch-button"
        @click="logout"
        class="logout-btn"
      >退出登录</el-button>
    </header>

    <!-- 主内容区 -->
    <main class="admin-main">
      <el-card class="welcome-card">
        <h2>欢迎来到管理员首页</h2>
        <p>请选择下方功能进行管理操作。</p>
        <div class="admin-btn-group">
          <el-button
            type="primary"
            size="large"
            icon="el-icon-s-order"
            @click="goOrderManagement"
          >订单管理</el-button>
          <el-button
            type="success"
            size="large"
            icon="el-icon-s-management"
            @click="goBookManagement"
          >图书管理</el-button>
        </div>
      </el-card>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const router = useRouter()

function goOrderManagement() {
  router.push('/AAAOrderManagement' ) // 请确保路由名正确
}
function goBookManagement() {
  router.push('/AAABookManagement') // 请确保路由名正确
}

async function logout() {
  try {
    await axios.post('/api/admin/login/logout', {}, { withCredentials: true })
    ElMessage.success('已退出登录')
    router.push('/AAALogin' )
  } catch (err) {
    ElMessage.error('退出失败')
  }
}
</script>

<style scoped>
.admin-home {
  min-height: 100vh;
  background: #f5f7fa;
}
.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
  background: #fff;
  padding: 0 40px;
  border-bottom: 1px solid #ebeef5;
  box-shadow: 0 2px 8px #0000000a;
}
.admin-header-left {
  display: flex;
  align-items: center;
}
.logo {
  height: 36px;
  margin-right: 12px;
}
.admin-title {
  font-size: 22px;
  font-weight: bold;
  color: #409eff;
  letter-spacing: 2px;
}
.logout-btn {
  font-size: 16px;
  letter-spacing: 2px;
}
.admin-main {
  padding: 48px 24px;
  min-height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #f5f7fa;
}
.welcome-card {
  max-width: 500px;
  width: 100%;
  margin-top: 80px;
  text-align: center;
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 2px 12px #0000000d;
  padding: 40px 0 32px 0;
}
.welcome-card h2 {
  margin-bottom: 16px;
  color: #409eff;
  font-size: 26px;
  font-weight: 600;
}
.welcome-card p {
  color: #666;
  font-size: 17px;
  margin-bottom: 24px;
}
.admin-btn-group {
  display: flex;
  justify-content: center;
  gap: 32px;
  margin-top: 24px;
}
</style>