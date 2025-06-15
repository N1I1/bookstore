<!-- filepath: c:\Users\22905\Desktop\database\bookstore\frontend\src\views\BookDetails.vue -->
<template>
  <div class="details-container">
    <el-card>
      <el-button class="back-btn" type="primary" @click="goHome" icon="el-icon-arrow-left" plain>
        返回首页
      </el-button>
      <h2>图书详情</h2>
      <p>图书ID：{{ bookId }}</p>
      <!-- 这里可以展示更多图书详细信息 -->
    </el-card>
  </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
const route = useRoute()
const router = useRouter()
const bookId = route.params.id

function goHome() {
  router.push('/home')
}
</script>

<style scoped>
.details-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 80vh;
}
.el-card {
  position: relative;
  min-width: 400px;
  min-height: 200px;
  padding-top: 40px;
}
.back-btn {
  position: absolute;
  top: 16px;
  left: 16px;
  z-index: 10;
}
</style>