<!-- filepath: c:\Users\22905\Desktop\database\bookstore\frontend\src\views\BookDetails.vue -->
<template>
  <div class="details-container">
    <el-card class="details-card">
      <!-- 左上角返回首页按钮 -->
      <el-button class="back-btn" type="primary" @click="goHome" icon="el-icon-arrow-left" plain>
        返回首页
      </el-button>
      <!-- 右上角购物车图标按钮 -->
      <el-button class="cart-btn" type="text" @click="goCart">
        <el-icon><i class="el-icon-shopping-cart-full"></i></el-icon>
        <span style="margin-left:4px;">购物车</span>
      </el-button>
      <el-row>
        <el-col :span="8">
          <img :src="book.cover" class="book-cover" alt="封面" />
        </el-col>
        <el-col :span="16">
          <h2>{{ book.title }}</h2>
          <p><b>作者：</b>{{ book.author }}</p>
          <p><b>ISBN：</b>{{ book.isbn }}</p>
          <p><b>出版社：</b>{{ book.publisher }}</p>
          <p><b>定价：</b>￥{{ book.price }}</p>
          <p><b>折扣：</b>{{ book.discount * 100 }}%</p>
          <p><b>目录：</b>{{ book.catalog }}</p>
          <p><b>库存状态：</b>{{ book.stock > 0 ? '有货' : '无货' }}</p>
          <el-button type="primary" :disabled="book.stock === 0" @click="addToCart(book)">
            添加至购物车
          </el-button>
        </el-col>
      </el-row>
      <el-divider />
      <!-- <div class="comments-section">
        <h3>评论区</h3>
        <el-form :model="commentForm" class="comment-form" @submit.prevent="submitComment">
          <el-form-item>
            <el-input
              v-model="commentForm.content"
              type="textarea"
              placeholder="写下你的评论"
              rows="2"
              maxlength="200"
              show-word-limit
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="submitComment">发表评论</el-button>
          </el-form-item>
        </el-form>
        <el-divider />
        <div v-if="comments.length">
          <el-card v-for="(item, idx) in comments" :key="idx" class="comment-item">
            <b>{{ item.user }}</b>：{{ item.content }}
          </el-card>
        </div>
        <div v-else class="no-comment">暂无评论</div>
      </div> -->
      <div class="post-area">
        <el-card v-for="post in posts" :key="post.post_id" class="post-item">
          <div>{{ post.content }}</div>
          <div class="post-meta">
            <el-button
              type="text"
              :icon="post.liked ? 'el-icon-star-on' : 'el-icon-star-off'"
              @click="toggleLike(post)"
            >
              {{ post.like_count }}
            </el-button>
            <span class="post-time">{{ formatTime(post.post_time) }}</span>
          </div>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

// 模拟图书数据，实际应从后端获取
const books = [
  {
    id: '1',
    title: '三体',
    author: '刘慈欣',
    isbn: '9787536692930',
    publisher: '重庆出版社',
    price: 49.9,
    discount: 0.8,
    catalog: '科幻小说',
    stock: 20,
    cover: 'https://img1.doubanio.com/view/subject/l/public/s33445566.jpg'
  },
  // ...更多图书
]

const route = useRoute()
const router = useRouter()
const bookId = route.params.id
const book = ref(books.find(b => String(b.id) === String(bookId)) || {})

// 示例数据，实际应通过API获取
const posts = ref([
  {
    post_id: 1,
    content: '三体真的很震撼！',
    post_time: '2024-06-16 15:00',
    like_count: 5,
    liked: false // 当前用户是否已点赞
  },
  {
    post_id: 2,
    content: '活着让我感动落泪。',
    post_time: '2024-06-15 10:00',
    like_count: 3,
    liked: true
  }
])
const commentForm = ref({ content: '' })

function formatTime(time) {
  return time.replace('T', ' ').slice(0, 16)
}

function toggleLike(post) {
  // 实际应调用后端API，传递 post_id 和 user_id
  if (post.liked) {
    post.like_count--
    post.liked = false
    // await api.delete('/post/like', { post_id: post.post_id, user_id: ... })
    ElMessage.info('已取消点赞')
  } else {
    post.like_count++
    post.liked = true
    // await api.post('/post/like', { post_id: post.post_id, user_id: ... })
    ElMessage.success('点赞成功')
  }
}

function submitComment() {
  if (!commentForm.value.content) {
    ElMessage.warning('评论不能为空')
    return
  }
  comments.value.unshift({
    user: '当前用户', // 实际应取当前登录用户
    content: commentForm.value.content
  })
  commentForm.value.content = ''
  ElMessage.success('评论成功')
}

// 添加至购物车（这里用window.cart模拟，实际建议用pinia/vuex或localStorage）
function addToCart(book) {
  window.cart = window.cart || []
  if (!window.cart.find(item => item.id === book.id)) {
    window.cart.push(book)
    ElMessage.success('已添加至购物车')
  } else {
    ElMessage.info('该书已在购物车中')
  }
}

function goHome() {
  router.push('/home')
}
function goCart() {
  router.push('/cart')
}
</script>

<style scoped>
.details-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 80vh;
  background: #f5f5f5;
  padding-top: 40px;
}
.details-card {
  width: 800px;
  padding: 30px 20px;
  position: relative;
}
.back-btn {
  position: absolute;
  top: 16px;
  left: 16px;
  z-index: 10;
}
.cart-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 10;
  color: #409eff;
  font-size: 18px;
}
.book-cover {
  width: 180px;
  height: 240px;
  object-fit: cover;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.comments-section {
  margin-top: 30px;
}
.comment-form {
  margin-bottom: 10px;
}
.comment-item {
  margin-bottom: 10px;
}
.no-comment {
  color: #888;
  text-align: center;
  margin: 20px 0;
}
.post-item {
  margin-bottom: 16px;
}
.post-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 8px;
}
.post-time {
  color: #888;
  font-size: 12px;
}
</style>