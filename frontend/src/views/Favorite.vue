<!-- filepath: c:\Users\22905\Desktop\database\bookstore\frontend\src\views\Favorite.vue -->
<template>
  <div class="favorite-wrapper">
    <el-card class="favorite-card">
      <div class="header-container">
        <el-button 
          type="primary" 
          plain 
          icon="el-icon-s-home" 
          @click="goHome"
          class="home-button"
        >
          返回主页
        </el-button>
        <h2 class="favorite-title">我的收藏夹</h2>
      </div>
      <el-empty v-if="favorites.length === 0 && !loading" description="暂无收藏" />
      <el-table
        v-else
        :data="favorites"
        style="width: 100%;"
        :loading="loading"
        border
      >
        <el-table-column prop="book_id" label="书籍ID" width="100" />
        <el-table-column label="收藏时间" width="180">
          <template #default="scope">
            {{ formatTime(scope.row.favorite_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              @click="goBookDetail(scope.row.book_id)"
              plain
            >查看</el-button>
          </template>
        </el-table-column>
        <el-table-column label="取消收藏" width="215">
          <template #default="scope">
            <el-button
              type="danger"
              size="small"
              @click="removeFavorite(scope.row.book_id)"
              :loading="removingId === scope.row.book_id"
            >取消收藏</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const favorites = ref([])
const loading = ref(true)
const removingId = ref(null)
const router = useRouter()

onMounted(async () => {
  await fetchFavorites()
})

async function fetchFavorites() {
  loading.value = true
  try {
    const res = await axios.get('/api/user_favorites/', { withCredentials: true })
    favorites.value = res.data
  } catch (err) {
    favorites.value = []
    if (err.response && err.response.status === 401) {
      ElMessage.warning('请先登录')
    } else {
      ElMessage.error('获取收藏失败')
    }
  } finally {
    loading.value = false
  }
}

async function removeFavorite(bookId) {
  removingId.value = bookId
  try {
    await axios.delete(`/api/user_favorites/${bookId}`, { withCredentials: true })
    ElMessage.success('已取消收藏')
    favorites.value = favorites.value.filter(fav => fav.book_id !== bookId)
  } catch (err) {
    if (err.response && err.response.status === 404) {
      ElMessage.warning('收藏记录不存在')
    } else if (err.response && err.response.status === 401) {
      ElMessage.warning('请先登录')
    } else {
      ElMessage.error('取消收藏失败')
    }
  } finally {
    removingId.value = null
  }
}
function goHome() {
  router.push('/home')
}
function goBookDetail(bookId) {
  router.push(`/book/${bookId}`)
}

function formatTime(timeStr) {
  if (!timeStr) return ''
  return timeStr.replace('T', ' ').slice(0, 19)
}
</script>

<style scoped>
.favorite-wrapper {
  max-width: 800px;
  margin: 40px auto;
  padding: 24px;
}
.favorite-card {
  padding: 32px;
}

/* 添加顶部容器样式 */
.header-container {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
  position: relative; /* 相对定位 */
}

.home-button {
  position: absolute; /* 绝对定位在标题左侧 */
  left: 0;
  top: 50%;
  transform: translateY(-50%);
}

.favorite-title {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  text-align: center;
  flex: 1; /* 占据剩余空间以居中标题 */
}

/* 添加一些响应式设计 */
@media (max-width: 600px) {
  .favorite-card {
    padding: 16px;
  }
  
  .home-button {
    position: static;
    transform: none;
    margin-bottom: 10px;
  }
  
  .header-container {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .favorite-title {
    align-self: center;
    margin-top: 10px;
  }
}
</style>