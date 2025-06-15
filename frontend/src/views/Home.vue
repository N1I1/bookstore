<!-- filepath: c:\Users\22905\Desktop\database\bookstore\frontend\src\views\Home.vue -->
<template>
  <div class="home-container">
    <el-header class="header">
      <div class="logo">网上书店</div>
      <div class="user-info">
        <el-avatar icon="el-icon-user" @click="goUserInfo" style="cursor:pointer;" />
        <span class="username">欢迎，{{ username }}</span>
        <el-button type="text" @click="logout">退出登录</el-button>
      </div>
    </el-header>
    <el-main>
      <el-input
        v-model="search"
        placeholder="搜索图书、作者、ISBN"
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
                <p class="author">作者：{{ book.author }}</p>
                <p class="price">￥{{ book.price }}</p>
                <el-button type="primary" size="small">加入购物车</el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = ref('用户') // 实际项目可从登录信息获取
const search = ref('')

const books = ref([
  {
    id: 1,
    title: '三体',
    author: '刘慈欣',
    price: 49.9,
    cover: 'https://img1.doubanio.com/view/subject/l/public/s33445566.jpg'
  },
  {
    id: 2,
    title: '活着',
    author: '余华',
    price: 39.9,
    cover: 'https://img1.doubanio.com/view/subject/l/public/s29796444.jpg'
  },
  {
    id: 3,
    title: '解忧杂货店',
    author: '东野圭吾',
    price: 45.0,
    cover: 'https://img1.doubanio.com/view/subject/l/public/s27264181.jpg'
  },
  {
    id: 4,
    title: '百年孤独',
    author: '加西亚·马尔克斯',
    price: 59.0,
    cover: 'https://img1.doubanio.com/view/subject/l/public/s6384944.jpg'
  }
  // ...可继续添加
])

const filteredBooks = computed(() => {
  if (!search.value) return books.value
  return books.value.filter(
    book =>
      book.title.includes(search.value) ||
      book.author.includes(search.value) ||
      String(book.id).includes(search.value)
  )
})

function logout() {
  // 清除登录状态，跳转到登录页
  router.push('/login')
}

function goBookDetails(id) {
  router.push(`/book/${id}`)
}

function goUserInfo() {
  router.push('/user')
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
.logo {
  font-size: 24px;
  font-weight: bold;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}
.username {
  margin: 0 10px;
}
.search-bar {
  margin: 30px auto 20px;
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
</style>