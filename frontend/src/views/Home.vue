<!-- filepath: c:\Users\22905\Desktop\database\bookstore\frontend\src\views\Home.vue -->
<template>
  <div class="home-container">
    <el-header class="header">
      <div class="logo">网上书店</div>
      <div class="header-actions">
        <!-- 新增：浏览记录按钮 -->
        <el-button type="text" class="history-btn" @click="goBrowse">
          <el-icon><i class="el-icon-view"></i></el-icon>
          <span style="margin-left:4px;">浏览记录</span>
        </el-button>
        <!-- 新增：收藏夹按钮 -->
        <el-button type="text" class="favorite-btn" @click="goFavorite">
          <el-icon><i class="el-icon-star-on"></i></el-icon>
          <span style="margin-left:4px;">收藏夹</span>
        </el-button>
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
      <el-card class="forum-posts-card">
        <h3 class="forum-title">论坛推荐帖子</h3>
        <el-skeleton v-if="loading" rows="5" animated />
        <el-empty v-else-if="posts.length === 0" description="暂无帖子" />
        <div v-else class="forum-posts-list">
          <div v-for="post in posts" :key="post.id" class="forum-post-item">
            <div class="post-title">{{ post.title }}</div>
            <div class="post-content">{{ post.content }}</div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const router = useRouter()
const username = ref('用户')
const search = ref('')
const tags = ref(['科幻小说', '文学', '历史', '经济', '青春', '推理'])
const activeTag = ref('全部')

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

const posts = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await axios.get('/api/forum_posts/get_posts?limit=5', { params: { limit: 5 } })
    posts.value = res.data
  } catch (err) {
    posts.value = []
  } finally {
    loading.value = false
  }
})

function handleTagSelect(tag) {
  activeTag.value = tag
}

function goBrowse() {
  router.push('/browse')
}
function goFavorite() {
  router.push('/favorite')
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
async function logout() {
  try {
    const res = await axios.post('/api/login/logout', {}, { withCredentials: true })
    if (res.status === 200) {
      ElMessage.success('退出登录成功')
      router.push('/home')
    }
  } catch (err) {
    ElMessage.error('退出登录失败')
  }
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
.cart-btn, .history-btn, .favorite-btn {
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
.forum-posts-card {
  width: 350px;
  margin-left: 24px;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
}
.forum-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 16px;
  color: #409eff;
}
.forum-posts-list {
  padding: 0;
}
.forum-post-item {
  margin-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 8px;
}
.post-title {
  font-weight: bold;
  color: #333;
}
.post-content {
  color: #666;
  font-size: 14px;
  margin-top: 4px;
}
</style>