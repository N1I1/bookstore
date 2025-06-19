<template>
  <div class="post-detail-page">
    <el-row align="middle" class="header-row">
      <el-col :span="24" style="display: flex; align-items: center; justify-content: space-between;">
        <el-button
          type="primary"
          icon="el-icon-arrow-left"
          class="back-btn"
          @click="goBack"
        >返回</el-button>
        <el-button
          type="danger"
          icon="el-icon-delete"
          @click="deletePost"
        >删除帖子</el-button>
      </el-col>
    </el-row>
    <el-card class="post-main-card" v-if="post">
      <h2 class="post-title">{{ post.title || 'Untitled Post' }}</h2>
      <div class="post-meta">
        发布时间：{{ post.post_time }}　浏览：{{ post.browse_count }}
      </div>
      <div v-if="post.book_id && book" class="book-brief">
        <img
          :src="book.image_url || 'https://img1.baidu.com/it/u=1609036816,3547813773&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=750'"
          alt="封面"
          class="book-brief-cover"
        >
        <div class="book-brief-info">
          <router-link :to="`/book/${book.book_id}`" class="book-brief-title">{{ book.title }}</router-link>
          <div>作者：{{ book.author }}</div>
          <div>出版社：{{ book.publisher }}</div>
          <div>ISBN：{{ book.isbn }}</div>
          <div>
            价格：<span style="color:#e4393c;">￥{{ book.price }}</span>
            <span v-if="book.discount < 1" style="color:#409eff;">（{{ (book.discount * 10).toFixed(1) }}折）</span>
          </div>
          <div>库存：{{ book.stock }}</div>
        </div>
      </div>
      <div v-if="post.book_id && book" class="book-brief-desc">{{ book.description }}</div>
      <div class="post-content">{{ post.content }}</div>
      <el-divider />
      <!-- 评论区 -->
      <div class="comment-section">
        <h3 class="comment-title">评论</h3>
        <!-- 新评论输入框 -->
        <el-input
          v-model="newComment"
          type="textarea"
          :rows="2"
          maxlength="300"
          show-word-limit
          placeholder="发表你的评论..."
          class="comment-input"
        />
        <el-button type="primary" @click="submitComment" :loading="commentLoading" size="small" style="margin-top:8px;">发表评论</el-button>
        <el-divider />
        <!-- 评论树 -->
        <CommentTree
          v-if="comments.length"
          :comments="comments"
          :post-id="post.post_id"
          :current-user-id="currentUserId"
          @refresh="fetchComments"
          @delete-comment="deleteComment"
        />
        <el-empty v-else description="暂无评论" />
      </div>
    </el-card>
    <el-empty v-else description="未找到帖子" />
  </div>
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
const currentUserId = ref(null)
const book = ref(null)

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
    if (post.value.book_id) {
      fetchBookDetail(post.value.book_id)
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

async function fetchBookDetail(bookId) {
  try {
    const res = await axios.get(`/api/books/${bookId}`)
    book.value = res.data
  } catch (err) {
    book.value = null
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

async function deleteComment(commentId) {
  try {
    await axios.delete(`/api/comments/${commentId}`, { withCredentials: true })
    ElMessage.success('评论已删除')
    fetchComments()
  } catch (err) {
    if (err.response && err.response.status === 403) {
      ElMessage.error('只能删除自己的评论')
    } else if (err.response && err.response.status === 404) {
      ElMessage.error('评论不存在')
    } else {
      ElMessage.error('删除失败')
    }
  }
}

async function deletePost() {
  try {
    await axios.delete(`/api/forum_posts/${post.value.post_id}`, { withCredentials: true })
    ElMessage.success('帖子已删除')
    router.push('/home')
  } catch (err) {
    if (err.response?.status === 401) {
      ElMessage.error('请先登录')
      router.push('/userlogin')
    } else if (err.response?.status === 403) {
      ElMessage.error('只能删除自己的帖子')
    } else if (err.response?.status === 404) {
      ElMessage.error('帖子不存在')
      router.push('/home')
    } else {
      ElMessage.error('删除失败')
    }
  }
}

function formatTime(timeStr) {
  return timeStr ? timeStr.replace('T', ' ').slice(0, 19) : ''
}

function goBack() {
  router.back()
}

async function fetchCurrentUser() {
  try {
    const res = await axios.get('/api/users/', { withCredentials: true })
    currentUserId.value = res.data.user_id
  } catch {}
}
</script>

<style scoped>
.post-detail-page {
  max-width: 900px;
  margin: 40px auto 0 auto;
  padding: 0 0 32px 0;
  background: #f7f9fb;
  min-height: 90vh;
}
.header-row {
  margin-bottom: 18px;
}
.back-btn {
  font-size: 15px;
  letter-spacing: 1px;
  margin-bottom: 8px;
}
.post-main-card {
  border-radius: 16px;
  box-shadow: 0 2px 12px #0000000d;
  margin-bottom: 32px;
  padding: 32px 32px 24px 32px;
  background: #fff;
}
.post-title {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 12px;
  color: #222;
}
.post-meta {
  color: #888;
  font-size: 13px;
  margin-bottom: 12px;
}
.book-brief {
  display: flex;
  align-items: flex-start;
  gap: 18px;
  margin-bottom: 8px;
}
.book-brief-cover {
  width: 80px;
  height: 110px;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 2px 8px #00000014;
  background: #fafbfc;
}
.book-brief-info {
  flex: 1;
  font-size: 15px;
  color: #444;
}
.book-brief-title {
  font-weight: bold;
  font-size: 16px;
  color: #409eff;
  text-decoration: none;
}
.book-brief-title:hover {
  text-decoration: underline;
}
.book-brief-desc {
  color: #666;
  margin-bottom: 12px;
  margin-left: 98px;
  font-size: 14px;
}
.post-content {
  font-size: 16px;
  line-height: 1.8;
  color: #333;
  white-space: pre-wrap;
  margin: 20px 0;
}
.comment-section {
  margin-top: 32px;
}
.comment-title {
  margin-bottom: 16px;
  font-size: 20px;
  color: #409eff;
  font-weight: bold;
}
.comment-input {
  margin-bottom: 8px;
}
</style>