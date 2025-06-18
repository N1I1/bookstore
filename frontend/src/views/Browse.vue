<!-- filepath: c:\Users\22905\Desktop\database\bookstore\frontend\src\views\Browse.vue -->
<template>
  <div class="browse-container">
    <el-card class="browse-card">
      <h2>浏览记录</h2>
      <el-table :data="browseList" v-if="browseList.length" style="width: 100%">
        <el-table-column label="书名">
          <template #default="scope">
            <el-link type="primary" @click="goBookDetails(scope.row.book_id)">
              {{ scope.row.book_title || '未知书名' }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="browse_time" label="浏览时间" />
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button
              type="danger"
              size="small"
              @click="deleteBrowse(scope.row.browse_id)"
            >删除</el-button>
          </template>
        </el-table-column>
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
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()
const browseList = ref([])

onMounted(async () => {
  try {
    const res = await axios.get('/api/user_browse/user/', { withCredentials: true })
    browseList.value = res.data
  } catch (err) {
    browseList.value = []
    if (err.response && err.response.status === 401) {
      ElMessage.warning('请先登录')
      router.push('/login')
    } else {
      ElMessage.error('获取浏览记录失败')
    }
  }
})

// 删除浏览记录
async function deleteBrowse(browseId) {
  try {
    await axios.delete(`/api/user_browse/${browseId}`, { withCredentials: true })
    ElMessage.success('删除成功')
    browseList.value = browseList.value.filter(item => item.browse_id !== browseId)
  } catch (err) {
    if (err.response && err.response.status === 404) {
      ElMessage.warning('记录不存在')
    } else if (err.response && err.response.status === 401) {
      ElMessage.warning('请先登录')
      router.push('/login')
    } else {
      ElMessage.error('删除失败')
    }
  }
}
// 

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
