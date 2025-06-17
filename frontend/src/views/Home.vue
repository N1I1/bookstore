<!-- filepath: c:\Users\22905\Desktop\database\bookstore\frontend\src\views\Home.vue -->
<template>
  <div class="home-container">
    <el-header class="header">
      <div class="logo">网上书店</div>
      <div class="header-actions">
        <!-- 添加搜索框 -->
        <div class="search-container">
          <el-input
            v-model="searchQuery"
            placeholder="搜索书名、作者、内容..."
            clearable
            @keyup.enter="searchBooks"
            @clear="resetSearch"
          >
            <template #append>
              <el-button icon="el-icon-search" @click="searchBooks" />
            </template>
          </el-input>
        </div>
        
        <!-- 浏览记录按钮 -->
        <el-button type="text" class="history-btn" @click="goBrowse">
          <el-icon><i class="el-icon-view"></i></el-icon>
          <span style="margin-left:4px;">浏览记录</span>
        </el-button>
        
        <!-- 收藏夹按钮 -->
        <el-button type="text" class="favorite-btn" @click="goFavorite">
          <el-icon><i class="el-icon-star-on"></i></el-icon>
          <span style="margin-left:4px;">收藏夹</span>
        </el-button>
        
        <!-- 购物车按钮 -->
        <el-button type="text" class="cart-btn" @click="goCart">
          <el-icon><i class="el-icon-shopping-cart-full"></i></el-icon>
          <span style="margin-left:4px;">购物车</span>
        </el-button>
        
        <!-- 用户头像和名字 -->
        <el-avatar icon="el-icon-user" @click="goUserInfo" style="cursor:pointer;" />
        <span class="username">欢迎，{{ username }}</span>
        <el-button type="text" @click="logout">退出登录</el-button>
      </div>
    </el-header>
    
    <!-- 搜索状态提示 -->
    <div v-if="searchStatus" class="search-status">
      <el-tag :type="searchStatus.type">{{ searchStatus.message }}</el-tag>
      <el-button v-if="isSearching" type="text" @click="resetSearch">返回全部书籍</el-button>
    </div>
    
    <div class="main-content">
      <!-- 左侧标签栏 -->
      <div class="tag-menu-fixed">
        <div
          v-for="initial in initials"
          :key="initial"
          class="tag-initial"
          :class="{ 'active-initial': activeInitial === initial }"
          @click="toggleTagGroup(initial)"
        >
          {{ initial }}
          <transition name="fade">
            <div
              v-if="activeInitial === initial"
              class="tag-popover"
            >
              <div
                v-for="tag in tagGroups[initial]"
                :key="tag.tag_id"
                class="tag-item"
                :class="{ 'active-tag': activeTagId === tag.tag_id }"
                @click.stop="handleTagSelect(tag.tag_id, tag.name)"
              >
                {{ tag.name }}
              </div>
            </div>
          </transition>
        </div>
        <div 
          class="tag-initial all-tags" 
          :class="{ 'active-initial': activeTagId === 'all' }"
          @click="handleTagSelect('all', '')"
        >
          全部
        </div>
      </div>
      <!-- 中间书籍部分（确保5行4列布局不变） -->
      <div class="home-wrapper">
        <h2 class="home-title">
          {{ isSearching ? `搜索结果 (${filteredBooks.length}本)` : '全部书籍' }}
        </h2>
        
        <el-row v-if="filteredBooks.length > 0" :gutter="24" class="book-list">
          <!-- 保持4列布局（每个占6个span单位） -->
          <el-col
            v-for="book in pagedBooks"
            :key="book.book_id"
            :span="6"
            class="book-col"
          >
            <el-card class="book-card" shadow="hover" @click="goBookDetail(book.book_id)">
              <img :src="book.image_url || defaultImg" class="book-img" alt="封面" />
              <div class="book-info">
                <div class="book-title" :title="book.title">{{ book.title }}</div>
                <div class="book-author">{{ book.author }}</div>
                <div class="book-price">
                  <span class="price">￥{{ book.price }}</span>
                  <span class="discount" v-if="book.discount < 1">
                    ({{ (book.discount * 10).toFixed(1) }}折)
                  </span>
                </div>
                <div class="book-stock">库存：{{ book.stock }}</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
        
        <!-- 无搜索结果时显示 -->
        <el-empty v-if="isSearching && filteredBooks.length === 0" description="未找到相关书籍" />
        <el-empty v-if="!isSearching && books.length === 0" description="暂无书籍数据" />
        
        <!-- 分页器 -->
        <div v-if="filteredBooks.length > pageSize" class="pagination-bar">
          <el-pagination
            background
            layout="prev, pager, next"
            :page-size="pageSize"
            :total="filteredBooks.length"
            v-model:current-page="currentPage"
          />
        </div>
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
const tags = ref([])
// 分组后的标签对象，如 { K: [{tag_id:1, name:'科幻'}], W: [...] }
const tagGroups = computed(() => {
  const groups = {}
  tags.value.forEach(tag => {
    const first = tag.name[0].toUpperCase()
    if (!groups[first]) groups[first] = []
    groups[first].push(tag)
  })
  return groups
})
const initials = computed(() => Object.keys(tagGroups.value).sort())

// 搜索相关状态
const searchQuery = ref('')
const searchStatus = ref(null)
const isSearching = ref(false) // 当前是否在搜索状态

const books = ref([]) // 存储所有书籍数据
const filteredBooks = ref([]) // 存储过滤后的书籍数据
const currentPage = ref(1)
const pageSize = 20 // 5行 * 4列 = 20本/页
const defaultImg = 'https://img1.baidu.com/it/u=1609036816,3547813773&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=750'

// 计算当前页显示的书籍
const pagedBooks = computed(() => {
  // 当数量不足一页时显示所有
  if (filteredBooks.value.length <= pageSize) {
    return filteredBooks.value
  }
  const start = (currentPage.value - 1) * pageSize
  return filteredBooks.value.slice(start, start + pageSize)
})

// 添加标签相关状态变量
const activeInitial = ref('') // 当前激活的首字母
const activeTagId = ref('all') // 当前选中的标签ID

onMounted(async () => {
  // 1. 获取所有标签
  try {
    const tagRes = await axios.get('/api/tags/')
    tags.value = tagRes.data
  } catch (err) {
    tags.value = []
    ElMessage.error('获取标签失败')
  }
  
  // 2. 获取书籍数据
  try {
    const res = await axios.get('/api/books/')
    books.value = res.data
    filteredBooks.value = res.data
    // 重置当前页
    currentPage.value = 1
  } catch (err) {
    books.value = []
    filteredBooks.value = []
    ElMessage.error('获取书籍列表失败')
  }
  
  // 3. 加载论坛热门帖子
  try {
    const res = await axios.get('/api/forum_posts/get_posts', { params: { limit: 5 } })
    posts.value = res.data
  } catch (err) {
    console.error('获取论坛帖子失败:', err)
    posts.value = []
  } finally {
    loading.value = false
  }
})

// 搜索书籍
const searchBooks = async () => {
  if (!searchQuery.value.trim()) {
    ElMessage.warning('请输入搜索内容')
    return
  }
  
  // 显示搜索状态
  searchStatus.value = {
    type: 'info',
    message: `正在搜索: "${searchQuery.value}"...`
  }
  isSearching.value = true
  
  try {
    // 发送搜索请求
    const response = await axios.post('/api/search_books', {
      query: searchQuery.value
    }, {
      timeout: 5000 // 设置超时时间
    })

    // 处理搜索结果
    if (response.data.message === "Books found" && response.data.book_ids) {
      const foundBookIds = response.data.book_ids
      
      // 从全部书籍中过滤出匹配的书籍
      const foundBooks = books.value.filter(book => 
        foundBookIds.includes(book.book_id.toString())
      )
      
      filteredBooks.value = foundBooks
      currentPage.value = 1 // 搜索后重置到第一页
      
      searchStatus.value = {
        type: 'success',
        message: `找到 ${foundBooks.length} 本相关书籍`
      }
    } else if (response.data.message === "No books found") {
      filteredBooks.value = []
      searchStatus.value = {
        type: 'warning',
        message: '未找到相关书籍'
      }
    }
  } catch (error) {
    console.error('搜索失败:', error)
    let errorMessage = '搜索过程中出现错误'
    
    if (error.response) {
      if (error.response.status === 400) {
        errorMessage = error.response.data.error || '缺少搜索查询'
      } else if (error.response.status === 500) {
        errorMessage = '服务器内部错误'
      }
    } else if (error.code === 'ECONNABORTED') {
      errorMessage = '搜索请求超时'
    }
    
    ElMessage.error(errorMessage)
    searchStatus.value = {
      type: 'danger',
      message: errorMessage
    }
  }
}

// 重置搜索，显示全部书籍
const resetSearch = () => {
  searchQuery.value = ''
  searchStatus.value = null
  isSearching.value = false
  filteredBooks.value = [...books.value] // 恢复显示全部书籍
  activeTagId.value = 'all'
  currentPage.value = 1
}

// 点击标签进行筛选
async function handleTagSelect(tagId, tagName) {
  activeTagId.value = tagId
  activeInitial.value = '' // 选择标签后关闭弹出层
  
  // 如果是全部标签
  if (tagId === 'all') {
    filteredBooks.value = books.value
    return
  }
  
  // 添加加载状态
  loading.value = true
  try {
    const res = await axios.get(`/api/tags/${tagId}/books`)
    filteredBooks.value = res.data
    
    // 更新页面标题显示当前标签
    if (tagName) {
      isSearching.value = true
      searchStatus.value = {
        type: 'info',
        message: `标签: "${tagName}"`
      }
    }
  } catch (err) {
    ElMessage.error('获取标签书籍失败')
    filteredBooks.value = []
  } finally {
    loading.value = false
  }
}

async function goBookDetail(bookId) {
  try {
    // 先记录浏览
    await axios.post('/api/user_browse/', { book_id: bookId }, { withCredentials: true })
  } catch (err) {
    // 可以忽略错误，或者提示未登录
    if (err.response && err.response.status === 401) {
      ElMessage.warning('请先登录以记录浏览')
    }
  }
  // 跳转到详情页
  router.push(`/book/${bookId}`)
}

// 切换标签组显示
function toggleTagGroup(initial) {
  // 如果点击的是当前已展开的首字母，则关闭
  if (activeInitial.value === initial) {
    activeInitial.value = ''
  } else {
    activeInitial.value = initial
  }
}
// 导航方法保持不变

function goBrowse() {
  router.push('/browse')
}

function goFavorite() {
  router.push('/favorite')
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

// 论坛帖子相关状态
const posts = ref([])
const loading = ref(true)
</script>

<style scoped>
.home-wrapper {
  flex: 1; /* 占据剩余空间 */
  max-width: 1000px;
  min-width: 800px;
}
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

/* 搜索框容器样式 */
.search-container {
  margin-right: 20px;
  width: 300px;
}

.search-container .el-input-group {
  transition: all 0.3s ease;
}

.search-container .el-input-group:hover {
  transform: scale(1.02);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 搜索状态提示 */
.search-status {
  display: flex;
  align-items: center;
  margin: 10px auto;
  padding: 8px 16px;
  background-color: #f5f5f5;
  border-radius: 4px;
  max-width: 1200px;
}

.search-status .el-tag {
  margin-right: 10px;
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
  justify-content: center; /* 居中显示 */
  padding: 0 20px;
}
/* tag */
.tag-menu-fixed {
  width: 60px;
  margin-right: 20px; /* 增加右边距 */
  align-self: flex-start; /* 顶部对齐 */
}
.tag-initial {
  width: 40px;
  height: 40px;
  line-height: 40px;
  text-align: center;
  margin: 4px 0;
  background: #f5f7fa;
  border-radius: 50%;
  cursor: pointer;
  font-weight: bold;
  position: relative;
}
.tag-popover {
  position: absolute;
  left: 50px;
  top: 0;
  min-width: 100px;
  background: #fff;
  border: 1px solid #eee;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.12);
  z-index: 10;
  padding: 8px 0;
}
.tag-item {
  padding: 6px 18px;
  cursor: pointer;
  white-space: nowrap;
}
.tag-item:hover {
  background: #f0f7ff;
  color: #409eff;
}
/* tag */
.search-bar {
  margin: 0 auto 20px;
  max-width: 500px;
  display: block;
}
/* 中间书籍展示部分 - 保持布局不变 */
.home-wrapper {
  max-width: 1000px;
  margin: 32px auto;
  padding: 24px;
  background: #fff;
  border-radius: 10px;
  min-height: 80vh;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.home-title {
  font-size: 26px;
  font-weight: bold;
  margin-bottom: 24px;
  color: #409eff;
  text-align: left;
  border-bottom: 1px solid #eee;
  padding-bottom: 12px;
}

.book-list {
  margin-bottom: 32px;
}

.book-col {
  margin-bottom: 24px;
}

/* 书籍卡片样式 */
.book-card {
  cursor: pointer;
  transition: all 0.3s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
}

.book-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.book-img {
  width: 120px;
  height: 180px; /* 固定高度确保对齐 */
  object-fit: cover;
  margin: 15px auto 10px;
  border-radius: 4px;
  background: #f8f8f8;
}

.book-info {
  width: 100%;
  text-align: center;
  padding: 0 10px;
}

.book-title {
  font-weight: bold;
  font-size: 15px;
  margin-bottom: 6px;
  display: -webkit-box;
  -webkit-line-clamp: 2; /* 限制标题为两行 */
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  height: 2.6em; /* 2行高度 */
  line-height: 1.3em;
}

.book-author {
  color: #666;
  font-size: 13px;
  margin-bottom: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.book-price {
  color: #e67e22;
  font-size: 15px;
  margin-bottom: 6px;
  font-weight: bold;
}

.price {
  font-weight: bold;
}

.discount {
  color: #67c23a;
  margin-left: 6px;
  font-size: 13px;
}

.book-stock {
  color: #999;
  font-size: 12px;
  margin-bottom: 10px;
}

.pagination-bar {
  display: flex;
  justify-content: center;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}
/* 中间书籍展示部分 */

/* 右侧推荐帖子内容 */
.forum-posts-card {
  width: 350px;
  min-width: 300px;
  margin-left: 24px;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  height: fit-content;
  position: sticky;
  top: 90px;
  align-self: flex-start; /* 顶部对齐 */
}

.forum-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 16px;
  color: #409eff;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.forum-posts-list {
  padding: 0;
}

.forum-post-item {
  margin-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 12px;
  transition: all 0.2s ease;
  cursor: pointer;
}

.forum-post-item:hover {
  background-color: #f9f9f9;
}

.post-title {
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
  font-size: 15px;
}

.post-content {
  color: #666;
  font-size: 13px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.5em;
}
/* 右侧推荐帖子内容 */
</style>