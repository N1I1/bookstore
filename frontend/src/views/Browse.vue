<!-- filepath: c:\Users\22905\Desktop\database\bookstore\frontend\src\views\Browse.vue -->
<template>
  <div class="browse-container">
    <el-card class="browse-card">
      <h2>浏览记录</h2>
      <el-table :data="browseList" v-if="browseList.length" style="width: 100%">
        <el-table-column label="书名">
          <template #default="scope">
            <el-link type="primary" @click="goBookDetails(scope.row.book_id)">
              {{ scope.row.book_title }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="browse_time" label="浏览时间" />
      </el-table>
      <div v-else class="empty-tip">
        暂无浏览记录
      </div>
      <el-button class="back-btn" @click="goHome">返回首页</el-button>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const browseList = ref([])

onMounted(() => {
  // 实际应通过API获取
  browseList.value = [
    { book_id: 1, book_title: '三体', browse_time: '2024-06-16 15:00' },
    { book_id: 2, book_title: '活着', browse_time: '2024-06-15 10:00' }
  ]
})

function goBookDetails(bookId) {
  router.push(`/book/${bookId}`)
}
function goHome() {
  router.push('/home')
}
</script>

<style scoped>
.browse-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 80vh;
  background: #f5f5f5;
  padding-top: 40px;
}
.browse-card {
  width: 700px;
  padding: 30px 20px;
}
.back-btn {
  margin-top: 20px;
}
.empty-tip {
  text-align: center;
  color: #888;
  margin: 40px 0;
}
</style>