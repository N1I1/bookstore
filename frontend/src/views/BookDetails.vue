<template>
  <div class="book-details-container">
    <!-- 顶部操作栏：使用更协调的配色和间距 -->
    <div class="action-bar">
      <el-button type="primary" plain class="back-btn" @click="goHome">
        <el-icon><ArrowLeft /></el-icon>
        <span>返回首页</span>
      </el-button>
      
      <div class="action-buttons">
        <el-button type="success" class="cart-btn" @click="goToCart">
          <el-icon><ShoppingCart /></el-icon>
          <span>购物车</span>
        </el-button>
        <el-button type="warning" class="post-btn" @click="goCreatePost">
          <el-icon><Edit /></el-icon>
          <span>发帖</span>
        </el-button>
      </div>
    </div>
    
    <!-- 书籍详情区域 - 使用卡片嵌套提升层次感 -->
    <template v-if="book">
      <el-card shadow="hover" class="book-card">
        <div class="book-content">
          <!-- 图片区域添加边框和阴影 -->
          <div class="image-section">
            <div class="image-wrapper">
              <img :src="book.image_url || defaultImg" class="book-image" alt="书籍封面" />
            </div>
            <el-button 
              type="success" 
              size="large"
              class="cart-action-btn"
              :loading="cartLoading"
              :disabled="book && (book.stock <= 0 || cartLoading)"
              @click="addToCart"
            >
              <el-icon><Plus /></el-icon>
              <span>{{ book.stock > 0 ? '加入购物车' : '已售罄' }}</span>
            </el-button>
          </div>
          
          <!-- 书籍信息区域优化排版 -->
          <div class="info-section">
            <h1 class="book-title">{{ book.title }}</h1>
            <div class="book-meta">
              <div class="meta-item">
                <el-icon><User /></el-icon>
                <span>作者：{{ book.author }}</span>
              </div>
              <div class="meta-item">
                <el-icon><Document /></el-icon>
                <span>ISBN：{{ book.isbn }}</span>
              </div>
              <div class="meta-item">
                <el-icon><OfficeBuilding /></el-icon>
                <span>出版社：{{ book.publisher }}</span>
              </div>
            </div>
            
            <div class="price-section">
              <div class="original-price" v-if="book.discount < 1">
                ￥{{ (book.price / book.discount).toFixed(2) }}
              </div>
              <div class="current-price">
                ￥{{ book.price }}
                <span class="discount-tag" v-if="book.discount < 1">
                  {{ (book.discount * 10).toFixed(1) }}折
                </span>
              </div>
            </div>
            
            <div class="stock-section">
              <el-tag :type="book.stock > 10 ? 'success' : book.stock > 0 ? 'warning' : 'danger'">
                <el-icon><Box /></el-icon>
                <span>{{ book.stock > 0 ? `库存 ${book.stock} 件` : '已售罄' }}</span>
              </el-tag>
            </div>
            
            <div class="description-section">
              <h3 class="section-title">内容简介</h3>
              <p class="book-description">{{ book.description || '暂无内容简介' }}</p>
            </div>
            
            <el-button 
              type="danger" 
              plain 
              class="favorite-btn"
              :loading="favLoading"
              @click="addFavorite"
            >
              <el-icon><Star /></el-icon>
              收藏本书
            </el-button>
          </div>
        </div>
      </el-card>
      
      <!-- 相关帖子区块 - 使用更现代化的卡片设计 -->
      <el-card shadow="hover" class="posts-card">
        <template #header>
          <div class="card-header">
            <h3 class="posts-title">相关讨论</h3>
            <div class="posts-count">共 {{ relatedPosts.length }} 个帖子</div>
          </div>
        </template>
        
        <el-skeleton v-if="postsLoading" :rows="4" animated />
        <el-empty v-else-if="relatedPosts.length === 0" description="暂无相关帖子" />
        
        <div v-else class="posts-list">
          <div 
            v-for="post in relatedPosts"
            :key="post.post_id"
            class="post-item"
            @click="goPostDetail(post.post_id)"
          >
            <div class="post-content">
              <h4 class="post-title">{{ post.title || '未命名帖子' }}</h4>
              <p class="post-preview">{{ post.content || '无内容' }}</p>
              
              <div class="post-meta">
                <div class="meta-item">
                  <el-icon><View /></el-icon>
                  <span>{{ post.browse_count || 0 }}</span>
                </div>
                <div class="meta-item">
                  <el-icon><Clock /></el-icon>
                  <span>{{ formatPostTime(post.post_time) }}</span>
                </div>
              </div>
            </div>
            
            <el-button
              v-if="isMine(post)"
              type="danger"
              size="small"
              circle
              @click.stop="deletePost(post.post_id)"
              class="delete-btn"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </el-card>
    </template>
    
    <el-empty v-else description="未找到该书籍信息" />
  </div>
</template>

<script setup>
// 优化导入方式，使用具名导入
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  ShoppingCart,
  Edit,
  Plus,
  User,
  Document,
  OfficeBuilding,
  Box,
  Star,
  View,
  Clock,
  Delete
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const book = ref(null)
const defaultImg = 'https://img1.baidu.com/it/u=1609036816,3547813773&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=750'
const favLoading = ref(false)
const cartLoading = ref(false)
const relatedPosts = ref([])
const postsLoading = ref(true)
const currentUserId = ref(null)

onMounted(async () => {
  const bookId = route.params.id
  try {
    // 获取书籍详情
    const res = await axios.get(`/api/books/${bookId}`)
    book.value = res.data
    // 记录浏览
    try {
      await axios.post('/api/user_browse/', { book_id: bookId }, { withCredentials: true })
    } catch (err) {
      console.warn('记录浏览失败:', err)
    }
  } catch (err) {
    book.value = null
    if (err.response && err.response.status === 404) {
      ElMessage.warning('未找到该书籍')
    } else {
      ElMessage.error('获取书籍信息失败')
    }
  }

  // 获取相关帖子
  try {
    const res = await axios.get(`/api/forum_posts/by_book/${bookId}`)
    relatedPosts.value = res.data
  } catch (err) {
    relatedPosts.value = []
  } finally {
    postsLoading.value = false
  }
  
  // 获取当前用户ID
  try {
    const res = await axios.get('/api/users/', { withCredentials: true })
    currentUserId.value = res.data.user_id
  } catch (err) {
    console.warn('获取用户信息失败:', err)
  }
})

function formatPostTime(timeStr) {
  if (!timeStr) return ''
  return timeStr.slice(0, 16).replace('T', ' ')
}

async function deletePost(postId) {
  try {
    await axios.delete(`/api/forum_posts/${postId}`, { withCredentials: true })
    ElMessage.success('帖子已删除')
    // 刷新帖子列表
    relatedPosts.value = relatedPosts.value.filter(p => p.post_id !== postId)
  } catch (err) {
    if (err.response?.status === 403) {
      ElMessage.error('只能删除自己的帖子')
    } else if (err.response?.status === 404) {
      ElMessage.error('帖子不存在')
    } else if (err.response?.status === 401) {
      ElMessage.error('请先登录')
      router.push('/userlogin')
    } else {
      ElMessage.error('删除失败')
    }
  }
}

function isMine(post) {
  return currentUserId.value && post.user_id == currentUserId.value
}

// 返回首页
function goHome() {
  router.push('/home')
}

// 跳转购物车
function goToCart() {
  router.push('/cart')
}

// 加入购物车
async function addToCart() {
  if (!book.value) return
  cartLoading.value = true
  try {
    const res = await axios.post('/api/user_cart/', {
      book_id: book.value.book_id,
      quantity: 1
    }, { withCredentials: true })
    if (res.status === 201) {
      ElMessage.success('已加入购物车')
    } else {
      ElMessage.warning(res.data.error || '加入购物车失败')
    }
  } catch (error) {
    if (error.response?.status === 400 && error.response.data.error === 'Book already in cart') {
      ElMessage.warning('该书已在购物车')
    } else if (error.response?.status === 401) {
      ElMessage.warning('请先登录')
      router.push('/login')
    } else {
      ElMessage.error(error.response?.data?.error || '操作失败')
    }
  } finally {
    cartLoading.value = false
  }
}

// 添加收藏 
async function addFavorite() {
  if (!book.value) return
  favLoading.value = true
  try {
    const res = await axios.post('/api/user_favorites/', { book_id: book.value.book_id }, { withCredentials: true })
    if (res.status === 201) {
      ElMessage.success('收藏成功')
    }
  } catch (err) {
    if (err.response) {
      if (err.response.status === 400 && err.response.data.error === 'Book already favorited') {
        ElMessage.warning('该书已收藏')
      } else if (err.response.status === 400) {
        ElMessage.error('缺少必要字段')
      } else if (err.response.status === 404) {
        ElMessage.error('图书不存在')
      } else if (err.response.status === 401) {
        ElMessage.warning('请先登录')
      } else {
        ElMessage.error('收藏失败')
      }
    } else {
      ElMessage.error('网络错误')
    }
  } finally {
    favLoading.value = false
  }
}

function goCreatePost() {
  router.push({ name: 'CreatePost', query: { book_id: book.value?.book_id || '' } })
}

function goPostDetail(postId) {
  router.push({ name: 'PostDetail', params: { post_id: postId } })
}
</script>

<style scoped>
.book-details-container {
  max-width: 1200px;
  margin: 30px auto;
  padding: 0 20px;
}

/* 顶部操作栏样式 */
.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 15px 20px;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.action-buttons {
  display: flex;
  gap: 15px;
}

.back-btn span,
.cart-btn span,
.post-btn span {
  margin-left: 6px;
}

/* 书籍卡片样式 */
.book-card {
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 30px;
  border: none;
}

.book-content {
  display: flex;
  padding: 25px;
  gap: 40px;
}

@media (max-width: 768px) {
  .book-content {
    flex-direction: column;
    gap: 25px;
  }
}

.image-section {
  flex: 0 0 300px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.image-wrapper {
  width: 100%;
  height: 380px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f9f9f9;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.book-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.cart-action-btn {
  width: 100%;
  height: 50px;
  font-size: 16px;
}

.info-section {
  flex: 1;
}

.book-title {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 20px;
  line-height: 1.3;
  position: relative;
  padding-bottom: 15px;
}

.book-title::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  width: 60px;
  height: 4px;
  background: linear-gradient(90deg, #409eff, #67c23a);
  border-radius: 2px;
}

.book-meta {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
  margin-bottom: 25px;
}

.meta-item {
  display: flex;
  align-items: center;
  font-size: 16px;
  color: #555;
}

.meta-item .el-icon {
  margin-right: 8px;
  color: #409eff;
}

.price-section {
  display: flex;
  align-items: center;
  gap: 15px;
  margin: 25px 0;
  padding: 15px;
  background: linear-gradient(to right, #f8fafc, #f1f8ff);
  border-radius: 10px;
}

.original-price {
  font-size: 18px;
  color: #999;
  text-decoration: line-through;
}

.current-price {
  font-size: 32px;
  font-weight: 700;
  color: #e74c3c;
}

.discount-tag {
  display: inline-block;
  background: #f56c6c;
  color: white;
  font-size: 14px;
  padding: 3px 10px;
  border-radius: 20px;
  margin-left: 10px;
  vertical-align: super;
}

.stock-section {
  margin-bottom: 25px;
}

.stock-section .el-tag {
  font-size: 16px;
  padding: 10px 20px;
  border-radius: 8px;
}

.description-section {
  margin: 30px 0;
}

.section-title {
  font-size: 20px;
  color: #333;
  margin-bottom: 15px;
  position: relative;
  padding-left: 15px;
}

.section-title::before {
  content: "";
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 18px;
  background: #409eff;
  border-radius: 2px;
}

.book-description {
  font-size: 16px;
  line-height: 1.8;
  color: #555;
  padding: 15px;
  background: #f9fafb;
  border-radius: 8px;
  border-left: 3px solid #409eff;
}

.favorite-btn {
  width: 150px;
  height: 45px;
  font-size: 16px;
  margin-top: 10px;
}

/* 帖子卡片样式 */
.posts-card {
  border-radius: 16px;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.posts-title {
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
}

.posts-count {
  font-size: 14px;
  color: #666;
}

.posts-list {
  display: grid;
  gap: 20px;
}

.post-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-radius: 12px;
  background: #fafbfc;
  transition: all 0.3s ease;
  cursor: pointer;
  border: 1px solid #eee;
}

.post-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
  border-color: #dcdfe6;
}

.post-content {
  flex: 1;
}

.post-title {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 10px;
}

.post-preview {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 15px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-meta {
  display: flex;
  gap: 20px;
}

.post-meta .meta-item {
  display: flex;
  align-items: center;
  font-size: 13px;
  color: #909399;
}

.post-meta .el-icon {
  margin-right: 5px;
}

.delete-btn {
  flex-shrink: 0;
  margin-left: 15px;
}
</style>