<template>
  <div class="user-info-wrapper">
    <el-card class="user-info-card">
      <el-button
        class="back-home-btn"
        type="text"
        icon="el-icon-arrow-left"
        @click="goHome"
      >
        返回首页
      </el-button>
      <h2 class="user-info-title">个人信息</h2>
      
      <!-- 用户操作按钮组 -->
      <div class="user-actions">
        <el-button type="primary" @click="updateUser">保存修改</el-button>
        <el-button type="danger" @click="deleteUser">删除账户</el-button>
      </div>
      
      <el-form :model="user" :rules="rules" ref="userForm" label-width="100px" class="user-info-form">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="user.username" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="user.email" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="user.phone" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="user.password" type="password" placeholder="如需修改请填写" show-password />
          <div class="password-hint">留空则不修改密码</div>
        </el-form-item>
        <el-form-item label="默认地址" prop="default_address">
          <el-input v-model="user.default_address" />
        </el-form-item>
        <el-form-item label="注册时间">
          <el-input v-model="user.register_time" disabled />
        </el-form-item>
        <el-form-item label="上次登录">
          <el-input v-model="user.last_login_time" disabled />
        </el-form-item>
      </el-form>
      
      <!-- 用户帖子展示区块 -->
      <div class="user-posts-section">
        <h3 style="margin:32px 0 16px 0;color:#409eff;">我的帖子</h3>
        <el-skeleton v-if="postsLoading" rows="4" animated />
        <el-empty v-else-if="userPosts.length === 0" description="暂无帖子" />
        <el-timeline v-else>
          <el-timeline-item
            v-for="post in userPosts"
            :key="post.post_id"
            :timestamp="formatTime(post.post_time)"
            placement="top"
          >
            <div class="user-post-item" @click="goPostDetail(post.post_id)">
              <div class="post-title">{{ post.title || 'Untitled Post' }}</div>
              <div class="post-content">{{ post.content }}</div>
              <div class="post-meta">
                <span>浏览：{{ post.browse_count }}</span>
                <span v-if="post.book_id" style="margin-left:12px;">关联书籍ID：{{ post.book_id }}</span>
              </div>
            </div>
          </el-timeline-item>
        </el-timeline>
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
const router = useRouter()

const user = ref({
  username: '',
  email: '',
  phone: '',
  password: '',
  default_address: '',
  register_time: '',
  last_login_time: '',
  user_id: ''
})

const userPosts = ref([])
const postsLoading = ref(true)

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

onMounted(async () => {
  try {
    // 获取用户信息
    const userRes = await axios.get('/api/users/', { withCredentials: true })
    
    // 调试日志
    console.log('用户信息响应:', userRes.data)
    
    if (userRes.status === 200) {
      // 将API返回的数据映射到user对象
      user.value = {
        username: userRes.data.username,
        email: userRes.data.email,
        phone: userRes.data.phone || '',
        password: '',
        default_address: userRes.data.default_address || '',
        register_time: userRes.data.register_time,
        last_login_time: userRes.data.last_login_time,
        user_id: userRes.data.user_id // 确保user_id存在
      }
      
      // 获取用户帖子
      if (user.value.user_id) {
        console.log('获取用户帖子，用户ID:', user.value.user_id)
        await fetchUserPosts(user.value.user_id)
      } else {
        postsLoading.value = false
        console.error('用户信息中缺少user_id字段')
      }
    }
  } catch (err) {
    postsLoading.value = false
    handleApiError(err, '获取用户信息')
  }
})

async function fetchUserPosts(userId) {
  postsLoading.value = true
  try {
    const res = await axios.get(`/api/forum_posts/by_user/${userId}`, {
      withCredentials: true
    })
    
    // 调试日志
    console.log('用户帖子响应:', res.data)
    
    userPosts.value = res.data
  } catch (err) {
    console.error('获取用户帖子失败:', err)
    if (err.response?.status === 404) {
      // 用户没有帖子，返回空数组
      userPosts.value = []
      ElMessage.warning('您还没有发布过帖子')
    } else {
      handleApiError(err, '获取用户帖子')
      userPosts.value = []
    }
  } finally {
    postsLoading.value = false
  }
}

function formatTime(timeStr) {
  return timeStr ? timeStr.replace('T', ' ').slice(0, 19) : ''
}

function goPostDetail(postId) {
  router.push({ name: 'PostDetail', params: { post_id: postId } })
}

async function updateUser() {
  // 只提交有变动的字段
  const updateData = {
    username: user.value.username,
    email: user.value.email,
    phone: user.value.phone,
    default_address: user.value.default_address
  }
  
  // 只有在密码字段有值时才更新密码
  if (user.value.password) {
    updateData.password = user.value.password
  }

  try {
    const res = await axios.put('/api/users/', updateData, { withCredentials: true })
    if (res.status === 200) {
      ElMessage.success('信息修改成功')
      // 清空密码字段但不重置表单绑定
      user.value.password = ''
    }
  } catch (err) {
    handleApiError(err, '更新用户信息')
  }
}

async function deleteUser() {
  try {
    await ElMessageBox.confirm(
      '确定要删除您的账户吗？此操作不可撤销！',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        center: true
      }
    )
    
    // 用户确认删除
    const res = await axios.delete('/api/users/', { withCredentials: true })
    if (res.status === 204) {
      ElMessage.success('账户已成功删除')
      // 退出登录状态并跳转到首页
      setTimeout(() => {
        router.push('/login')
      }, 1500)
    }
  } catch (err) {
    ElMessage.error('删除账户失败，请请检查是否有未完成的订单')
  }
}

function handleApiError(err, action = '操作') {
  if (err.response) {
    switch (err.response.status) {
      case 400:
        ElMessage.error(err.response.data.message || '请求参数错误')
        break
      case 401:
        ElMessage.error('请先登录')
        handleLoginRequired()
        break
      case 403:
        ElMessage.error('无权执行此操作')
        break
      case 404:
        ElMessage.error('资源不存在')
        break
      default:
        ElMessage.error(`${action}失败，服务器错误`)
    }
  } else {
    ElMessage.error(`${action}失败，网络错误`)
  }
}

function goHome() {
  router.push('/home')
}
</script>

<style scoped>
.user-info-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4edf5 100%);
  padding: 20px;
}

.user-info-card {
  width: 700px;
  padding: 40px 30px;
  border-radius: 12px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  background: #fff;
  position: relative;
}

.user-info-title {
  text-align: center;
  margin-bottom: 30px;
  font-weight: bold;
  font-size: 26px;
  color: #4361ee;
  letter-spacing: 1px;
}

.user-info-form {
  margin-top: 20px;
}

.back-home-btn {
  position: absolute;
  top: 20px;
  left: 20px;
  color: #4361ee;
  font-size: 16px;
  font-weight: 500;
}

.user-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 20px;
}

.password-hint {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.user-posts-section {
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.user-post-item {
  cursor: pointer;
  padding: 12px 15px;
  border-radius: 8px;
  background: #f9fafb;
  transition: all 0.3s ease;
  border: 1px solid #eee;
}

.user-post-item:hover {
  background: #f0f7ff;
  border-color: #cce5ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.post-title {
  font-weight: bold;
  color: #2c3e50;
  font-size: 16px;
  margin-bottom: 8px;
}

.post-content {
  color: #4a5568;
  font-size: 14px;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.6em;
}

.post-meta {
  color: #718096;
  font-size: 13px;
  display: flex;
}

@media (max-width: 768px) {
  .user-info-card {
    width: 100%;
    padding: 30px 15px;
  }
  
  .user-info-title {
    font-size: 22px;
  }
  
  .user-actions {
    flex-direction: column;
    gap: 10px;
  }
}
</style>
