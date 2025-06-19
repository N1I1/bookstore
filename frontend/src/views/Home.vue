<template>
  <div class="home-container">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="logo">
        <el-icon><Reading /></el-icon>
        <span>网上书店</span>
      </div>
      
      <div class="header-actions">
        <!-- 搜索框 -->
        <div class="search-container">
          <el-input
            v-model="searchQuery"
            placeholder="搜索书名、作者、内容..."
            clearable
            @keyup.enter="searchBooks"
            @clear="resetSearch"
          >
            <template #append>
              <el-button type="primary" icon="Search" @click="searchBooks" />
            </template>
          </el-input>
        </div>

        <!-- 功能按钮组 -->
        <div class="action-buttons">
          <el-tooltip content="投诉建议" placement="bottom">
            <el-button type="warning" circle @click="goComplaint">
              <el-icon><Warning /></el-icon>
            </el-button>
          </el-tooltip>
          
          <el-tooltip content="我的订单" placement="bottom">
            <el-button type="primary" circle @click="goOrderList">
              <el-icon><Tickets /></el-icon>
            </el-button>
          </el-tooltip>
          
          <el-tooltip content="发布帖子" placement="bottom">
            <el-button type="success" circle @click="goCreatePost">
              <el-icon><Edit /></el-icon>
            </el-button>
          </el-tooltip>
          
          <el-tooltip content="浏览记录" placement="bottom">
            <el-button type="info" circle @click="goBrowse">
              <el-icon><Clock /></el-icon>
            </el-button>
          </el-tooltip>
          
          <el-tooltip content="我的收藏" placement="bottom">
            <el-button type="danger" circle @click="goFavorite">
              <el-icon><Star /></el-icon>
            </el-button>
          </el-tooltip>
          
          <el-tooltip content="购物车" placement="bottom">
            <el-button type="primary" circle @click="goCart">
              <el-icon><ShoppingCart /></el-icon>
            </el-button>
          </el-tooltip>
        </div>
        
        <!-- 用户信息 -->
        <div class="user-section">
          <el-avatar :size="36" :src="userAvatar" @click="goUserInfo" />
          <span class="username">欢迎，{{ username }}</span>
          <el-button type="text" @click="logout">
            <el-icon><SwitchButton /></el-icon>
            <span>退出</span>
          </el-button>
        </div>
      </div>
    </el-header>
    
    <!-- 搜索状态提示 -->
    <div v-if="searchStatus" class="search-status">
      <el-tag :type="searchStatus.type" size="large" round>
        {{ searchStatus.message }}
      </el-tag>
      <el-button v-if="isSearching" type="text" @click="resetSearch">
        <el-icon><Back /></el-icon>
        <span>返回全部书籍</span>
      </el-button>
    </div>
    
    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧标签导航 - 独立滚动 -->
      <div class="tag-menu">
        <div class="tag-header">
          <el-icon><CollectionTag /></el-icon>
          <span>图书分类</span>
        </div>
        
        <div class="tag-groups">
          <div 
            v-for="initial in initials" 
            :key="initial"
            class="tag-group"
          >
            <div class="group-title" @click="toggleTagGroup(initial)">
              {{ initial }}
              <el-icon :class="{ 'rotate-icon': activeInitial === initial }">
                <ArrowRight />
              </el-icon>
            </div>
            
            <el-collapse-transition>
              <div v-show="activeInitial === initial" class="tag-items">
                <div
                  v-for="tag in tagGroups[initial]"
                  :key="tag.tag_id"
                  class="tag-item"
                  :class="{ 'active-tag': activeTagId === tag.tag_id }"
                  @click="handleTagSelect(tag.tag_id, tag.name)"
                >
                  {{ tag.name }}
                </div>
              </div>
            </el-collapse-transition>
          </div>
        </div>
        
        <div 
          class="all-tags"
          :class="{ 'active-tag': activeTagId === 'all' }"
          @click="handleTagSelect('all', '')"
        >
          <el-icon><Menu /></el-icon>
          <span>全部书籍</span>
        </div>
      </div>
      
      <!-- 中间书籍展示区 - 独立滚动 -->
      <div class="book-section">
        <div class="section-header">
          <h2>
            <el-icon><Notebook /></el-icon>
            {{ isSearching ? `搜索结果 (${filteredBooks.length}本)` : '精选好书推荐' }}
          </h2>
          <el-divider />
        </div>
        
        <div class="book-list-container">
          <div v-if="filteredBooks.length > 0" class="book-list">
            <el-row :gutter="24">
              <el-col
                v-for="book in pagedBooks"
                :key="book.book_id"
                :xs="12" :sm="8" :md="6"
                class="book-col"
              >
                <el-card 
                  class="book-card" 
                  shadow="hover"
                  @click="goBookDetail(book.book_id)"
                >
                  <div class="book-image">
                    <el-image 
                      :src="book.image_url || defaultImg" 
                      fit="cover"
                      class="book-img"
                    />
                    <div v-if="book.discount < 1" class="discount-badge">
                      {{ (book.discount * 10).toFixed(1) }}折
                    </div>
                  </div>
                  
                  <div class="book-info">
                    <!-- 书名固定高度 -->
                    <div class="book-title" :title="book.title">
                      {{ book.title }}
                    </div>
                    <!-- 作者固定位置 -->
                    <div class="book-author">
                      <el-icon><User /></el-icon>
                      {{ book.author }}
                    </div>
                    <div class="book-meta">
                      <!-- 价格固定位置 -->
                      <div class="book-price">
                        <span class="price">¥{{ book.price }}</span>
                        <span v-if="book.original_price" class="original-price">
                          ¥{{ book.original_price }}
                        </span>
                      </div>
                      <!-- 库存固定位置 -->
                      <div class="book-stock">
                        <el-icon><Box /></el-icon>
                        库存: {{ book.stock }}
                      </div>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
          
          <!-- 无数据提示 -->
          <el-empty 
            v-if="isSearching && filteredBooks.length === 0" 
            description="未找到相关书籍"
            :image-size="200"
          />
          <el-empty 
            v-if="!isSearching && books.length === 0" 
            description="暂无书籍数据"
            :image-size="200"
          />
        </div>
        
        <!-- 分页器 -->
        <div v-if="filteredBooks.length > pageSize" class="pagination-bar">
          <el-pagination
            background
            layout="prev, pager, next, jumper"
            :page-size="pageSize"
            :total="filteredBooks.length"
            v-model:current-page="currentPage"
          />
        </div>
      </div>
      
      <!-- 右侧论坛推荐区 - 独立滚动 -->
      <div class="forum-section">
        <div class="section-header">
          <h3>
            <el-icon><ChatLineRound /></el-icon>
            热门书友讨论
          </h3>
          <el-button type="text" @click="goCreatePost">
            <el-icon><Plus /></el-icon>
            发帖
          </el-button>
        </div>
        
        <el-card shadow="never" class="forum-card">
          <el-skeleton v-if="loading" :rows="5" animated />
          
          <el-empty 
            v-else-if="posts.length === 0" 
            description="暂无帖子"
            :image-size="100"
          />
          
          <div v-else class="post-list">
            <div 
              v-for="post in posts" 
              :key="post.post_id" 
              class="post-item"
              @click="goPostDetail(post.post_id)"
            >
              <div class="post-header">
                <el-avatar :size="32" :src="post.avatar" />
                <div class="post-author">{{ post.author }}</div>
                <div class="post-time">{{ formatTime(post.create_time) }}</div>
              </div>
              
              <div class="post-title">{{ post.title }}</div>
              <div class="post-content">{{ post.content }}</div>
              
              <div class="post-footer">
                <div class="post-stats">
                  <span>
                    <el-icon><View /></el-icon>
                    {{ post.views }}
                  </span>
                  <span>
                    <el-icon><ChatDotRound /></el-icon>
                    {{ post.comments }}
                  </span>
                  <span>
                    <el-icon><Star /></el-icon>
                    {{ post.likes }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>
    
    <!-- 登录提示弹窗 -->
    <el-dialog
      v-model="showLoginDialog"
      title="提示"
      width="380px"
      :close-on-click-modal="false"
      align-center
    >
      <div class="login-dialog-content">
        <el-icon :size="48" color="#409EFF"><WarningFilled /></el-icon>
        <p>请先登录后再进行操作</p>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="goHome">暂不登录</el-button>
          <el-button type="primary" @click="goUserLogin">立即登录</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
  <el-dialog
    v-model="showRecommendDialog"
    title="为你推荐的书籍"
    width="700px"
    @close="handleDialogClose"
  >
    <el-table :data="recommendList" v-if="recommendList.length">
      <el-table-column prop="title" label="书名" />
      <el-table-column prop="author" label="作者" />
      <el-table-column prop="publisher" label="出版社" />
      <el-table-column prop="recommend_type" label="推荐类型" />
      <el-table-column prop="recommend_reason" label="推荐理由" />
    </el-table>
    <el-empty v-else description="暂无推荐结果" />
    <template #footer>
      <el-checkbox v-model="dontShowAgain" style="margin-right:16px;">
        15分钟内不再弹出
      </el-checkbox>
      <el-button @click="handleDialogClose">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { 
  ElMessage, ElLoading 
} from 'element-plus'
import {
  Reading, Search, Warning, Tickets, Edit, Clock,
  Star, ShoppingCart, SwitchButton, Back, CollectionTag,
  ArrowRight, Menu, Notebook, User, Box, ChatLineRound,
  Plus, View, ChatDotRound, WarningFilled
} from '@element-plus/icons-vue'

const router = useRouter()
const username = ref('书友')
const userAvatar = ref('https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png')

// 标签相关
const tags = ref([])
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
const activeInitial = ref('')
const activeTagId = ref('all')

// 书籍相关
const books = ref([])
const filteredBooks = ref([])
const searchQuery = ref('')
const searchStatus = ref(null)
const isSearching = ref(false)
const currentPage = ref(1)
const pageSize = 20
const defaultImg = 'https://img1.baidu.com/it/u=1609036816,3547813773&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=750'

// 论坛帖子
const posts = ref([])
const loading = ref(true)

// 推荐书籍弹窗
const showRecommendDialog = ref(false)
const recommendList = ref([])
const dontShowAgain = ref(false)

// 登录弹窗
const showLoginDialog = ref(false)

// 推荐书籍
function fetchRecommendBooks() {
  axios.get('/api/recommend_books/recommend', { withCredentials: true })
    .then(res => {
      if (res.data && res.data.recommendations && res.data.recommendations.length > 0) {
        recommendList.value = res.data.recommendations
        showRecommendDialog.value = true
      } else {
        recommendList.value = []
      }
    })
    .catch(err => {
      if (err.response?.status === 400) {
        ElMessage.error('缺少用户ID')
      } else if (err.response?.status === 404) {
        ElMessage.warning('没有推荐书籍')
      } else {
        ElMessage.error('推荐失败')
      }
    })
}

function handleDialogClose() {
  if (dontShowAgain.value) {
    localStorage.setItem('recommendDialogHideUntil', Date.now() + 3 * 60 * 1000)
  }
  showRecommendDialog.value = false
}

// 计算当前页显示的书籍
const pagedBooks = computed(() => {
  if (filteredBooks.value.length <= pageSize) {
    return filteredBooks.value
  }
  const start = (currentPage.value - 1) * pageSize
  return filteredBooks.value.slice(start, start + pageSize)
})

onMounted(async () => {
  const loadingInstance = ElLoading.service({ 
    target: '.book-section',
    text: '正在加载数据...'
  })
  
  try {
    // 获取标签数据
    const tagRes = await axios.get('/api/tags/')
    tags.value = tagRes.data
    
    // 获取书籍数据
    const bookRes = await axios.get('/api/books/')
    books.value = bookRes.data
    filteredBooks.value = [...bookRes.data]
    
    // 获取论坛帖子
    const postRes = await axios.get('/api/forum_posts/get_posts', { 
      params: { limit: 5 } 
    })
    posts.value = postRes.data
  } catch (err) {
    ElMessage.error('数据加载失败')
  } finally {
    loading.value = false
    loadingInstance.close()
  }
  const hideUntil = Number(localStorage.getItem('recommendDialogHideUntil') || 0)
  if (Date.now() < hideUntil) return
  fetchRecommendBooks()
})

// 搜索书籍
const searchBooks = async () => {
  if (!searchQuery.value.trim()) {
    ElMessage.warning('请输入搜索内容')
    return
  }
  
  searchStatus.value = {
    type: 'info',
    message: `正在搜索: "${searchQuery.value}"...`
  }
  isSearching.value = true
  
  try {
    const response = await axios.post('/api/search_books', {
      query: searchQuery.value
    }, { timeout: 5000 })

    if (response.data.message === "Books found" && response.data.books) {
      const foundBookIds = response.data.books.map(book => Number(book.book_id))
      const foundBooks = books.value.filter(book => 
        foundBookIds.includes(Number(book.book_id))
      )
      filteredBooks.value = foundBooks
      currentPage.value = 1
      
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
    ElMessage.error('搜索失败，请稍后重试')
    searchStatus.value = {
      type: 'danger',
      message: '搜索请求失败'
    }
  }
}

// 重置搜索
const resetSearch = () => {
  searchQuery.value = ''
  searchStatus.value = null
  isSearching.value = false
  filteredBooks.value = [...books.value]
  activeTagId.value = 'all'
  currentPage.value = 1
}

// 标签选择
async function handleTagSelect(tagId, tagName) {
  activeTagId.value = tagId
  activeInitial.value = ''
  
  if (tagId === 'all') {
    filteredBooks.value = books.value
    return
  }
  
  const loadingInstance = ElLoading.service({ 
    target: '.book-section',
    text: '正在加载分类书籍...'
  })
  
  try {
    const res = await axios.get(`/api/tags/${tagId}/books`)
    filteredBooks.value = res.data
    
    if (tagName) {
      isSearching.value = true
      searchStatus.value = {
        type: 'info',
        message: `标签: "${tagName}"`
      }
    }
  } catch (err) {
    ElMessage.error('获取分类书籍失败')
  } finally {
    loadingInstance.close()
  }
}

// 切换标签组
function toggleTagGroup(initial) {
  activeInitial.value = activeInitial.value === initial ? '' : initial
}

// 导航方法
function goBookDetail(bookId) {
  try {
    axios.post('/api/user_browse/', { book_id: bookId }, { withCredentials: true })
    router.push(`/book/${bookId}`)
  } catch (err) {
    if (err.response?.status === 401) {
      showLoginDialog.value = true
    } else {
      router.push(`/book/${bookId}`)
    }
  }
}

function goComplaint() {
  router.push({ name: 'UserComplaint' })
}

function goCreatePost() {
  router.push({ name: 'CreatePost', query: { book_id: '' } })
}

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
  showLoginDialog.value = false
  router.push('/user')
}

function goOrderList() {
  router.push({ name: 'OrderList' })
}

function goPostDetail(postId) {
  router.push({ name: 'PostDetail', params: { post_id: postId } })
}

async function logout() {
  try {
    await axios.post('/api/login/logout', {}, { withCredentials: true })
    ElMessage.success('退出登录成功')
    router.push('/home')
  } catch (err) {
    ElMessage.error('退出登录失败')
  }
}

function goHome() {
  showLoginDialog.value = false
}

function goUserLogin() {
  router.push('/login')
}

// 格式化时间
function formatTime(timeString) {
  return new Date(timeString).toLocaleDateString()
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background-color: #f8fafc;
  display: flex;
  flex-direction: column;
}

/* 头部样式 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #1e40af, #3b82f6);
  color: white;
  padding: 0 30px;
  height: 70px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
  flex-shrink: 0; /* 防止头部被压缩 */
}

.logo {
  display: flex;
  align-items: center;
  font-size: 24px;
  font-weight: bold;
  gap: 10px;
}

.logo .el-icon {
  font-size: 28px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.search-container {
  width: 320px;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.user-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.username {
  font-size: 14px;
}

/* 搜索状态 */
.search-status {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 0;
  background-color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  gap: 15px;
  flex-shrink: 0; /* 防止搜索状态栏被压缩 */
}

/* 主内容区 - 设置为弹性布局并允许滚动 */
.main-content {
  display: flex;
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  gap: 20px;
  flex: 1;
  width: 100%;
  overflow: hidden; /* 隐藏外部滚动条 */
  align-items: stretch;
  height: calc(100vh - 110px); /* 减去头部和搜索状态栏高度 */
}

/* 标签导航 - 独立滚动 */
.tag-menu {
  width: 220px;
  background: white;
  border-radius: 12px;
  padding: 20px 0;
  box-shadow: var(--card-shadow);
  display: flex;
  flex-direction: column;
  height: 100%; /* 高度100% */
  overflow: hidden; /* 隐藏内部滚动条 */
}

.tag-header {
  display: flex;
  align-items: center;
  padding: 0 20px 15px;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  border-bottom: 1px solid #f1f5f9;
  gap: 8px;
  flex-shrink: 0; /* 防止头部被压缩 */
}

.tag-groups {
  padding: 10px 0;
  flex: 1; /* 占据剩余空间 */
  overflow-y: auto; /* 添加垂直滚动条 */
}

.tag-group {
  margin-bottom: 8px;
}

.group-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.group-title:hover {
  background-color: #f8fafc;
}

.group-title .el-icon {
  transition: transform 0.3s;
}

.rotate-icon {
  transform: rotate(90deg);
}

.tag-items {
  padding: 5px 0 5px 30px;
}

.tag-item {
  padding: 8px 15px;
  border-radius: 6px;
  margin: 4px 0;
  cursor: pointer;
  transition: all 0.2s;
}

.tag-item:hover {
  background-color: #eff6ff;
  color: #3b82f6;
}

.active-tag {
  background-color: #dbeafe;
  color: #2563eb;
  font-weight: 500;
}

.all-tags {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  margin-top: auto; /* 推到标签区域底部 */
  border-top: 1px solid #f1f5f9;
  font-weight: 500;
  cursor: pointer;
  gap: 8px;
  transition: all 0.3s;
  flex-shrink: 0; /* 防止被压缩 */
}

.all-tags:hover {
  background-color: #f8fafc;
  color: #3b82f6;
}

/* 书籍区域 - 独立滚动 */
.book-section {
  flex: 1;
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: var(--card-shadow);
  display: flex;
  flex-direction: column;
  height: 100%; /* 高度100% */
  overflow: hidden; /* 隐藏内部滚动条 */
}

.section-header {
  margin-bottom: 20px;
  flex-shrink: 0; /* 防止头部被压缩 */
}

.section-header h2 {
  display: flex;
  align-items: center;
  font-size: 20px;
  color: #1e293b;
  gap: 10px;
}

.el-divider {
  margin: 15px 0;
}

/* 书籍列表容器 - 独立滚动 */
.book-list-container {
  flex: 1; /* 占据剩余空间 */
  overflow-y: auto; /* 添加垂直滚动条 */
}

.book-list {
  margin-bottom: 30px;
}

.book-col {
  margin-bottom: 25px;
}

.book-card {
  border-radius: 10px;
  overflow: hidden;
  transition: all 0.3s;
  height: 380px; /* 固定卡片高度 */
  display: flex;
  flex-direction: column;
}

.book-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.book-image {
  position: relative;
  height: 200px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f8fafc;
  overflow: hidden;
  flex-shrink: 0; /* 防止被压缩 */
}

.book-img {
  width: 140px;
  height: 180px;
  object-fit: cover;
  transition: transform 0.3s;
}

.book-card:hover .book-img {
  transform: scale(1.05);
}

.discount-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: #ef4444;
  color: white;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
}

/* 书籍信息区域 - 固定布局 */
.book-info {
  padding: 15px;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 120px; /* 可根据实际调整 */
}

/* 书名固定高度和位置 */
.book-title {
  font-weight: 600;
  font-size: 16px;
  margin-bottom: 10px;
  height: 44px; /* 2行高度 */
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

/* 作者固定位置 */
.book-author {
  display: -webkit-box;
  -webkit-line-clamp: 2;      /* 最多2行 */
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #64748b;
  font-size: 14px;
  margin-bottom: 12px;
  height: 40px;                /* 2行高度，按实际字体大小调整 */
  word-break: break-all;
  gap: 5px;
  align-items: flex-start;
}

.book-meta {
  margin-top: auto; /* 价格和库存推到信息区域底部 */
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 价格位置 */
.book-price {
  display: flex;
  align-items: center;
  gap: 8px;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.price {
  font-size: 18px;
  font-weight: bold;
  color: #ef4444;
}

.original-price {
  font-size: 14px;
  color: #94a3b8;
  text-decoration: line-through;
}

/* 库存位置 */
.book-stock {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #64748b;
  gap: 5px;
  max-width: 90px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pagination-bar {
  display: flex;
  justify-content: center;
  padding-top: 20px;
  border-top: 1px solid #f1f5f9;
  flex-shrink: 0; /* 防止被压缩 */
}

/* 论坛区域 - 独立滚动 */
.forum-section {
  width: 320px;
  display: flex;
  flex-direction: column;
  height: 100%; /* 高度100% */
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  flex-shrink: 0; /* 防止头部被压缩 */
}

.section-header h3 {
  display: flex;
  align-items: center;
  font-size: 18px;
  color: #1e293b;
  gap: 8px;
}

.forum-card {
  border-radius: 12px;
  overflow: hidden;
  flex: 1; /* 占据剩余空间 */
  display: flex;
  flex-direction: column;
}

.post-list {
  flex: 1; /* 占据剩余空间 */
  overflow-y: auto; /* 添加垂直滚动条 */
  padding: 5px;
}

.post-item {
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 15px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid #f1f5f9;
}

.post-item:hover {
  border-color: #dbeafe;
  background-color: #f8fafc;
  transform: translateY(-3px);
}

.post-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  gap: 10px;
}

.post-author {
  font-weight: 500;
  flex: 1;
}

.post-time {
  font-size: 12px;
  color: #94a3b8;
}

.post-title {
  font-weight: 600;
  margin-bottom: 8px;
  font-size: 15px;
}

.post-content {
  color: #64748b;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-footer {
  display: flex;
  justify-content: flex-end;
}

.post-stats {
  display: flex;
  gap: 15px;
  font-size: 13px;
  color: #94a3b8;
}

.post-stats span {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 登录弹窗 */
.login-dialog-content {
  text-align: center;
  padding: 20px 0;
}

.login-dialog-content p {
  margin: 15px 0;
  font-size: 16px;
}

.dialog-footer {
  display: flex;
  justify-content: center;
  gap: 15px;
}
</style>