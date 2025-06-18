<template>
  <div class="post-detail-container" v-if="post">
    <el-card>
      <h2>{{ post.title || 'Untitled Post' }}</h2>
      <div style="color:#888;font-size:13px;">
        发布时间：{{ post.post_time }}　浏览：{{ post.browse_count }}
      </div>
      <div v-if="post.book_id" style="margin:10px 0;">
        关联书籍ID：<router-link :to="`/book/${post.book_id}`">{{ post.book_id }}</router-link>
      </div>
      <div class="post-content" style="margin:20px 0;">{{ post.content }}</div>
      <el-divider />
      <!-- 评论区 -->
      <div class="comment-section">
        <h3 style="margin-bottom:16px;">评论</h3>
        <!-- 新评论输入框 -->
        <el-input
          v-model="newComment"
          type="textarea"
          :rows="2"
          maxlength="300"
          show-word-limit
          placeholder="发表你的评论..."
          style="margin-bottom:8px;"
        />
        <el-button type="primary" @click="submitComment" :loading="commentLoading" size="small">发表评论</el-button>
        <el-divider />
        <!-- 评论树 -->
        <CommentTree
          v-if="comments.length"
          :comments="comments"
          :post-id="post.post_id"
          :current-user-id="currentUserId"
          @refresh="fetchComments"
        />
        <el-empty v-else description="暂无评论" />
      </div>
      <el-button style="margin-top:24px;" @click="goBack">返回</el-button>
    </el-card>
  </div>
  <el-empty v-else description="未找到帖子" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import CommentTree from '../components/CommentTree.vue'

const route = useRoute()
const router = useRouter()
const post = ref(null)
const comments = ref([])
const newComment = ref('')
const commentLoading = ref(false)
const currentUserId = ref(null) // 你可以从用户信息接口获取

onMounted(() => {
  fetchPost()
  fetchCurrentUser()
})

async function fetchPost() {
  try {
    const res = await axios.get(`/api/forum_posts/${route.params.post_id}`)
    post.value = {
      ...res.data,
      post_time: formatTime(res.data.post_time)
    }
    fetchComments()
  } catch (err) {
    ElMessage.error('帖子不存在')
    setTimeout(() => router.back(), 1200)
  }
}

async function fetchComments() {
  if (!post.value) return
  try {
    const res = await axios.get(`/api/comments/tree/${post.value.post_id}`)
    comments.value = res.data
  } catch (err) {
    comments.value = []
  }
}

async function submitComment() {
  if (!newComment.value.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }
  commentLoading.value = true
  try {
    await axios.post('/api/comments/', {
      post_id: post.value.post_id,
      content: newComment.value
    }, { withCredentials: true })
    ElMessage.success('评论成功')
    newComment.value = ''
    fetchComments()
  } catch (err) {
    ElMessage.error('评论失败')
  } finally {
    commentLoading.value = false
  }
}

function formatTime(timeStr) {
  return timeStr ? timeStr.replace('T', ' ').slice(0, 19) : ''
}

function goBack() {
  router.back()
}

// 获取当前用户id（如有需要）
async function fetchCurrentUser() {
  try {
    const res = await axios.get('/api/users/', { withCredentials: true })
    currentUserId.value = res.data.user_id
  } catch {}
}
</script>

<style scoped>
.post-detail-container {
  max-width: 800px;
  margin: 40px auto;
  padding: 20px;
}
.post-content {
  font-size: 16px;
  line-height: 1.8;
  color: #333;
  white-space: pre-wrap;
}
.comment-section {
  margin-top: 32px;
}
</style>