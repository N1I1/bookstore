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
        <el-form-item>
          <el-button type="primary" @click="updateUser">保存修改</el-button>
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
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
const router = useRouter()

const user = ref({
  username: '',
  email: '',
  phone: '',
  default_address: '',
  register_time: '',
  last_login_time: '',
  user_id: ''
})

const userPosts = ref([])
const postsLoading = ref(true)

onMounted(async () => {
  try {
    const res = await axios.get('/api/users/', { withCredentials: true })
    console.log('用户信息响应:', res.data) // 调试日志
    if (res.status === 200) {
      Object.assign(user.value, res.data)
      // 确保user_id存在
        fetchUserPosts()
      }
    }
  } catch (err) {
    postsLoading.value = false
    if (err.response && err.response.status === 401) {
      ElMessage.error('请先登录')
    } else if (err.response && err.response.status === 403) {
      ElMessage.error('无权访问')
    } else if (err.response && err.response.status === 404) {
      ElMessage.error('用户不存在')
    } else {
      ElMessage.error('获取信息失败')
    }
  }
})

async function fetchUserPosts() {
  postsLoading.value = true
  try {
    const res = await axios.get(`/api/forum_posts/by_user/`, {
      withCredentials: true
    })
    console.log('用户帖子响应:', res.data) // 调试日志
    userPosts.value = res.data
  } catch (err) {
    console.error('获取用户帖子失败:', err)
    if (err.response?.status === 404) {
      // 用户没有帖子，返回空数组
      userPosts.value = []
    } else {
      ElMessage.error('获取帖子失败')
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
  if (user.value.password) updateData.password = user.value.password

  try {
    const res = await axios.put('/api/users/', updateData, { withCredentials: true })
    if (res.status === 200) {
      ElMessage.success('信息修改成功')
      user.value.password = ''
    }
  } catch (err) {
    if (err.response && err.response.status === 401) {
      ElMessage.error('请先登录')
    } else if (err.response && err.response.status === 403) {
      ElMessage.error('无权修改他人信息')
    } else if (err.response && err.response.status === 404) {
      ElMessage.error('用户不存在')
    } else if (err.response && err.response.status === 400) {
      ElMessage.error(err.response.data.message || '用户名或邮箱已存在')
    } else {
      ElMessage.error('修改失败')
    }
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
  background: #f5f7fa;
}
.user-info-card {
  width: 500px;
  padding: 32px 24px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  background: #fff;
  position: relative;
}
.user-info-title {
  text-align: center;
  margin-bottom: 24px;
  font-weight: bold;
  font-size: 24px;
  color: #409eff;
  letter-spacing: 2px;
}
.user-info-form {
  margin-top: 0;
}
.back-home-btn {
  position: absolute;
  top: 16px;
  left: 16px;
  color: #409eff;
  font-size: 15px;
}
.user-posts-section {
  margin-top: 40px;
}
.user-post-item {
  cursor: pointer;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.2s;
}
.user-post-item:hover {
  background: #f9f9f9;
}
.post-title {
  font-weight: bold;
  color: #333;
  font-size: 15px;
  margin-bottom: 4px;
}
.post-content {
  color: #666;
  font-size: 13px;
  margin-bottom: 4px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.5em;
}
.post-meta {
  color: #aaa;
  font-size: 12px;
}
</style>
