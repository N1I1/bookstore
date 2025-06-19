<template>
  <div class="browse-container">
    <div class="action-bar">
      <el-button class="back-btn" @click="goHome">
        <i class="el-icon-back"></i>
        <span>返回首页</span>
      </el-button>
    </div>
    
    <el-card class="browse-card">
      <div class="card-header">
        <h2><i class="el-icon-notebook-2"></i> 浏览记录</h2>
        <p class="subtitle">您最近浏览过的书籍</p>
      </div>
      
      <div class="content-wrapper">
        <el-table :data="browseList" v-if="browseList.length" style="width: 100%" class="custom-table">
          <el-table-column label="书名" min-width="300">
            <template #default="scope">
              <div class="book-info" @click="goBookDetails(scope.row.book_id)">
                <div class="book-title">
                  {{ scope.row.book_title || '未知书名' }}
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="浏览时间" width="220">
            <template #default="scope">
              <div class="browse-time">
                <i class="el-icon-time"></i>
                {{ formatTime(scope.row.browse_time) }}
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="scope">
              <el-button
                type="danger"
                size="small"
                icon="el-icon-delete"
                @click="deleteBrowse(scope.row.browse_id)"
              >删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <div v-else class="empty-state">
          <div class="empty-icon">
            <i class="el-icon-notebook-1"></i>
          </div>
          <div class="empty-text">
            <h3>暂无浏览记录</h3>
            <p>您最近还没有浏览过任何书籍</p>
          </div>
          <el-button type="primary" class="explore-btn" @click="goHome">
            <i class="el-icon-reading"></i>
            浏览书籍
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
  <el-dialog
    v-model="showLoginDialog"
    title="提示"
    width="340px"
    :close-on-click-modal="false"
    :show-close="false"
  >
    <div style="text-align:center;">
      <p style="margin-bottom:18px;">请先登录后再进行操作</p>
      <el-button @click="goUserHome" style="margin-right:16px;">暂不登录</el-button>
      <el-button type="primary" @click="goUserLogin">去登录</el-button>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()
const browseList = ref([])
const defaultCover = "https://via.placeholder.com/60x80?text=No+Cover"

// 登录弹窗控制
const showLoginDialog = ref(false)
function handleLoginRequired() {
  showLoginDialog.value = true
}
function goUserHome() {
  showLoginDialog.value = false
  router.push('/home')
}
function goUserLogin() {
  showLoginDialog.value = false
  router.push('/userlogin')
}
// 登录弹窗控制

onMounted(async () => {
  try {
    const res = await axios.get('/api/user_browse/user/', { withCredentials: true })
    browseList.value = res.data
  } catch (err) {
    browseList.value = []
    if (err.response && err.response.status === 401) {
      ElMessage.warning('请先登录')
      handleLoginRequired()
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
      handleLoginRequired()
    } else {
      ElMessage.error('删除失败')
    }
  }
}

function formatTime(timeStr) {
  if (!timeStr) return '';
  const date = new Date(timeStr);
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

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
  flex-direction: column;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4edf5 100%);
  padding: 20px;
}

.action-bar {
  display: flex;
  margin-bottom: 20px;
}

.back-btn {
  background: linear-gradient(90deg, #4361ee, #3a0ca3);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  box-shadow: 0 4px 10px rgba(67, 97, 238, 0.3);
  transition: all 0.3s ease;
}

.back-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(67, 97, 238, 0.4);
}

.back-btn i {
  margin-right: 8px;
}

.browse-card {
  flex: 1;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
  border: none;
  background: white;
  padding: 25px;
}

.card-header {
  text-align: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.card-header h2 {
  font-size: 28px;
  font-weight: 600;
  color: #2c3e50;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.card-header .subtitle {
  color: #7f8c8d;
  font-size: 16px;
  margin-top: 10px;
}

.content-wrapper {
  padding: 0 15px;
}

.custom-table {
  border-radius: 10px;
  overflow: hidden;
}

.custom-table :deep(.el-table__header) th {
  background-color: #f8f9fa;
  color: #2c3e50;
  font-weight: 600;
  font-size: 16px;
}

.custom-table :deep(.el-table__row) td {
  padding: 15px 0;
  border-bottom: 1px solid #edf2f7;
}

.book-info {
  display: flex;
  align-items: center;
  gap: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 10px;
  border-radius: 8px;
}

.book-info:hover {
  background-color: #f8f9ff;
  transform: translateX(5px);
}

.book-title {
  font-weight: 600;
  color: #2c3e50;
  font-size: 16px;
}

.browse-time {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #7f8c8d;
  font-size: 14px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
}

.empty-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.empty-icon i {
  font-size: 40px;
  color: #bdc3c7;
}

.empty-text h3 {
  font-size: 22px;
  color: #2c3e50;
  margin-bottom: 10px;
  font-weight: 600;
}

.empty-text p {
  color: #95a5a6;
  font-size: 16px;
  max-width: 400px;
  line-height: 1.6;
  margin-bottom: 25px;
}

.explore-btn {
  width: 180px;
  height: 45px;
  font-size: 16px;
  border-radius: 8px;
  background: linear-gradient(90deg, #4361ee, #3a0ca3);
  border: none;
}

.explore-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(67, 97, 238, 0.3);
}

@media (max-width: 768px) {
  .browse-card {
    padding: 15px;
  }
  
  .card-header h2 {
    font-size: 24px;
  }
  
  .book-title {
    font-size: 14px;
  }
  
  .browse-time {
    font-size: 12px;
  }
}
</style>