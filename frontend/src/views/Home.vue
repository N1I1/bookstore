<!-- filepath: c:\Users\22905\Desktop\database\bookstore\frontend\src\views\Home.vue -->
<template>
  <div class="home-container">
    <el-header class="header">
      <div class="logo">网上书店</div>
      <div class="header-actions">
        <el-button type="text" class="cart-btn" @click="goCart">
          <el-icon><i class="el-icon-shopping-cart-full"></i></el-icon>
          <span style="margin-left:4px;">购物车</span>
        </el-button>
        <el-avatar icon="el-icon-user" @click="goUserInfo" style="cursor:pointer;" />
        <span class="username">欢迎，{{ username }}</span>
        <el-button type="text" @click="logout">退出登录</el-button>
      </div>
    </el-header>
    <div class="main-content">
      <!-- 左侧标签栏 -->
      <el-menu
        class="tag-menu"
        :default-active="activeTag"
        @select="handleTagSelect"
      >
        <el-menu-item index="全部">全部</el-menu-item>
        <el-menu-item
          v-for="tag in tags"
          :key="tag"
          :index="tag"
        >{{ tag }}</el-menu-item>
      </el-menu>
      <!-- 右侧内容 -->
      <div class="content-area">
        <el-input
          v-model="search"
          placeholder="搜索书名、作者、出版社"
          prefix-icon="el-icon-search"
          class="search-bar"
          clearable
        />
        <el-row :gutter="20" class="book-list">
          <el-col :span="6" v-for="book in filteredBooks" :key="book.id">
            <el-card
              :body-style="{ padding: '20px', cursor: 'pointer' }"
              class="book-card"
              @click="goBookDetails(book.id)"
            >
              <img :src="book.cover" class="book-cover" alt="封面" />
              <div class="book-info">
                <h3>{{ book.title }}</h3>
                <el-tag size="small" style="margin-bottom: 5px;">{{ book.tag }}</el-tag>
                <p class="author">作者：{{ book.author }}</p>
                <p class="price">￥{{ book.price }}</p>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
      <!-- 右侧论坛热门帖子区 -->
      <div class="forum-sidebar">
        <el-card class="forum-card">
          <h3 style="margin-bottom: 16px;">热门帖子</h3>
          <el-scrollbar height="500px">
            <div
              v-for="post in topPosts"
              :key="post.post_id"
              class="forum-post-item"
              @click="goPost(post.post_id)"
            >
              <div class="forum-content">{{ post.content }}</div>
              <div class="forum-meta">
                <span class="forum-time">{{ formatTime(post.post_time) }}</span>
                <span class="forum-browse">浏览：{{ post.browse_count }}</span>
              </div>
            </div>
            <div v-if="!topPosts.length" class="no-post">暂无热门帖子</div>
          </el-scrollbar>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const username = ref('用户')
const search = ref('')
const tags = ref(['科幻小说', '文学', '历史', '经济', '青春', '推理'])
const activeTag = ref('全部')

// 模拟后端获取帖子数据，实际应通过API获取
const forumPosts = ref([
  {
    post_id: 1,
    user_id: 2,
    book_id: 1,
    content: '三体真的很震撼，强烈推荐！',
    post_time: '2024-06-01 12:30:00',
    browse_count: 120
  },
  {
    post_id: 2,
    user_id: 3,
    book_id: 2,
    content: '活着让我感动落泪。',
    post_time: '2024-06-10 09:15:00',
    browse_count: 98
  },
  // ...更多帖子
])

// 取浏览量前十的帖子
const topPosts = computed(() =>
  forumPosts.value
    .slice()
    .sort((a, b) => b.browse_count - a.browse_count)
    .slice(0, 10)
)

const books = ref([
  {
    id: 1,
    title: '三体',
    author: '刘慈欣',
    publisher: '重庆出版社',
    price: 49.9,
    cover: 'https://img1.doubanio.com/view/subject/l/public/s33445566.jpg',
    tag: '科幻小说'
  },
  {
    id: 2,
    title: '活着',
    author: '余华',
    publisher: '作家出版社',
    price: 39.9,
    cover: 'https://img1.doubanio.com/view/subject/l/public/s29796444.jpg',
    tag: '文学'
  },
  {
    id: 3,
    title: '解忧杂货店',
    author: '东野圭吾',
    publisher: '南海出版公司',
    price: 45.0,
    cover: 'https://img1.doubanio.com/view/subject/l/public/s27264181.jpg',
    tag: '推理'
  },
  {
    id: 4,
    title: '百年孤独',
    author: '加西亚·马尔克斯',
    publisher: '南海出版公司',
    price: 59.0,
    cover: 'https://img1.doubanio.com/view/subject/l/public/s6384944.jpg',
    tag: '文学'
  }
  // ...更多图书
])

const filteredBooks = computed(() => {
  let result = books.value
  if (activeTag.value !== '全部') {
    result = result.filter(book => book.tag === activeTag.value)
  }
  if (search.value) {
    result = result.filter(
      book =>
        book.title.includes(search.value) ||
        book.author.includes(search.value) ||
        book.publisher.includes(search.value)
    )
  }
  return result
})

function handleTagSelect(tag) {
  activeTag.value = tag
}

function goBookDetails(id) {
  router.push(`/book/${id}`)
}
function goCart() {
  router.push('/cart')
}
function goUserInfo() {
  router.push('/user')
}
function logout() {
  router.push('/login')
}
function goPost(postId) {
  router.push(`/forum/${postId}`)
}

function formatTime(time) {
  // 简单格式化，实际可用dayjs等库
  return time.replace('T', ' ').slice(0, 16)
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: #f5f5f5;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #409eff;
  color: #fff;
  padding: 0 40px;
  height: 64px;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}
.cart-btn {
  color: #fff;
  font-size: 18px;
}
.username {
  margin: 0 10px;
}
.main-content {
  display: flex;
  margin-top: 20px;
}
.tag-menu {
  width: 160px;
  min-height: 400px;
  margin-right: 30px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  padding-top: 20px;
}
.content-area {
  flex: 1;
}
.search-bar {
  margin: 0 auto 20px;
  max-width: 500px;
  display: block;
}
.book-list {
  margin-top: 20px;
}
.book-card {
  margin-bottom: 20px;
  min-height: 350px;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: box-shadow 0.3s, transform 0.3s;
  cursor: pointer;
}
.book-card:hover {
  box-shadow: 0 8px 24px rgba(64, 158, 255, 0.3), 0 1.5px 8px rgba(0,0,0,0.08);
  transform: translateY(-6px) scale(1.03);
  border: 1.5px solid #409eff;
  z-index: 2;
}
.book-cover {
  width: 120px;
  height: 160px;
  object-fit: cover;
  margin-bottom: 15px;
}
.book-info {
  text-align: center;
}
.author {
  color: #888;
  font-size: 14px;
  margin: 5px 0;
}
.price {
  color: #e4393c;
  font-size: 16px;
  margin: 5px 0 10px 0;
}
.main-content {
  display: flex;
  margin-top: 20px;
}
.forum-sidebar {
  width: 320px;
  margin-left: 30px;
}
.forum-card {
  min-height: 200px;
  max-height: 600px;
  overflow: hidden;
}
.forum-post-item {
  padding: 12px 8px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background 0.2s;
}
.forum-post-item:hover {
  background: #f5faff;
}
.forum-content {
  font-size: 15px;
  color: #333;
  margin-bottom: 6px;
  word-break: break-all;
}
.forum-meta {
  font-size: 12px;
  color: #888;
  display: flex;
  justify-content: space-between;
}
.no-post {
  text-align: center;
  color: #aaa;
  margin: 20px 0;
}
</style>