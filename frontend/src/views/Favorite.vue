<!-- filepath: c:\Users\22905\Desktop\database\bookstore\frontend\src\views\Favorite.vue -->
<template>
  <div class="favorite-container">
    <el-card class="favorite-card">
      <h2>收藏夹</h2>
      <el-table :data="favoriteList" v-if="favoriteList.length" style="width: 100%">
        <el-table-column label="书名">
          <template #default="scope">
            <el-link type="primary" @click="goBookDetails(scope.row.book_id)">
              {{ scope.row.book_title }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="favorite_time" label="收藏时间" />
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button type="danger" size="small" @click="removeFavorite(scope.row)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div v-else class="empty-tip">
        暂无收藏
      </div>
      <el-button class="back-btn" @click="goHome">返回首页</el-button>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const favoriteList = ref([])

onMounted(() => {
  // 实际应通过API获取
  favoriteList.value = [
    { book_id: 1, book_title: '三体', favorite_time: '2024-06-10 12:00' },
    { book_id: 2, book_title: '活着', favorite_time: '2024-06-12 09:30' }
  ]
})

function goBookDetails(bookId) {
  router.push(`/book/${bookId}`)
}
function removeFavorite(row) {
  // 实际应调用后端API移除
  favoriteList.value = favoriteList.value.filter(item => item.book_id !== row.book_id)
  ElMessage.success('已移除收藏')
}
function goHome() {
  router.push('/home')
}
</script>

<style scoped>
.favorite-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 80vh;
  background: #f5f5f5;
  padding-top: 40px;
}
.favorite-card {
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