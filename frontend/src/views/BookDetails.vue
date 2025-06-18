<!-- filepath: c:\Users\22905\Desktop\database\bookstore\frontend\src\views\BookDetails.vue -->
<template>
  <div class="book-details-wrapper" v-if="book">
    <!-- 顶部操作栏：返回首页 + 购物车按钮 -->
    <div class="book-details-header">
      <el-button type="text" class="back-btn" @click="goHome">
        <el-icon><i class="el-icon-back"></i></el-icon>
        <span>返回首页</span>
      </el-button>
      
      <el-button type="primary" class="cart-btn" @click="goToCart">
        <el-icon><i class="el-icon-shopping-cart-full"></i></el-icon>
        <span>购物车</span>
      </el-button>
      <el-button
        type="warning"
        class="post-btn"
        style="margin-top: 12px; width: 120px;"
        @click="goCreatePost"
      >
        <el-icon><i class="el-icon-edit"></i></el-icon>
        <span>发帖</span>
      </el-button>
    </div>
    
    <el-card class="book-details-card">
      <div class="book-details-main">
        <div class="img-and-cart">
          <img :src="book.image_url || defaultImg" class="book-img" alt="封面" />
          
          <!-- 图片下方添加加入购物车按钮 -->
          <el-button 
            type="success" 
            class="add-to-cart-btn"
            :loading="cartLoading"
            :disabled="book && (book.stock <= 0 || cartLoading)"
            @click="addToCart"
          >
            <el-icon><i class="el-icon-plus"></i></el-icon>
            <span>加入购物车</span>
          </el-button>
        </div>
        
        <div class="book-info">
          <h2 class="book-title">{{ book.title }}</h2>
          <div class="book-author">作者：{{ book.author }}</div>
          <div class="book-isbn">ISBN：{{ book.isbn }}</div>
          <div class="book-publisher">出版社：{{ book.publisher }}</div>
          <div class="book-price">
            价格：<span class="price">￥{{ book.price }}</span>
            <span class="discount" v-if="book.discount < 1">({{ (book.discount * 10).toFixed(1) }}折)</span>
          </div>
          <div class="book-stock">
            库存：{{ book.stock > 0 ? book.stock : '无货' }}
            <el-tag v-if="book.stock <= 0" type="danger" size="small" style="margin-left:8px;">售罄</el-tag>
          </div>
          <div class="book-desc">简介：{{ book.description || '暂无简介' }}</div>
          <el-button
            type="primary"
            class="favorite-btn"
            :loading="favLoading"
            @click="addFavorite"
          >
            <el-icon><i class="el-icon-star-on"></i></el-icon>
            收藏
          </el-button>
        </div>
      </div>
    </el-card>
    <!-- 相关帖子区块 -->
    <el-card class="related-posts-card" style="margin-top: 32px;">
      <h3 class="related-title">相关帖子</h3>
      <el-skeleton v-if="postsLoading" rows="4" animated />
      <el-empty v-else-if="relatedPosts.length === 0" description="暂无相关帖子" />
      <div v-else>
        <div
          v-for="post in relatedPosts"
          :key="post.post_id"
          class="related-post-item"
          @click="goPostDetail(post.post_id)"
        >
          <div class="post-title">{{ post.title || 'Untitled Post' }}</div>
          <div class="post-content">{{ post.content }}</div>
          <div class="post-meta">
            <span>浏览：{{ post.browse_count }}</span>
            <span style="margin-left:16px;">时间：{{ post.post_time?.slice(0,16).replace('T',' ') }}</span>
          </div>
        </div>
      </div>
    </el-card>
  </div>
  
  <el-empty v-else description="未找到该书籍" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const book = ref(null)
const defaultImg = 'https://img1.baidu.com/it/u=1609036816,3547813773&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=750'
const favLoading = ref(false)
const cartLoading = ref(false)
const relatedPosts = ref([])
const postsLoading = ref(true)

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
})

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
.book-details-wrapper {
  max-width: 800px;
  margin: 40px auto;
  padding: 24px;
}

/* 顶部操作栏样式 */
.book-details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.back-btn {
  color: #606266;
  font-size: 16px;
}

.back-btn:hover {
  color: #409eff;
}

.cart-btn {
  background-color: #e6a23c;
  border-color: #e6a23c;
}

.cart-btn:hover {
  background-color: #e6bc5c;
  border-color: #e6bc5c;
}

/* 书籍详情卡片 */
.book-details-card {
  padding: 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.book-details-main {
  display: flex;
  gap: 32px;
}

.img-and-cart {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 200px;
}

.book-img {
  width: 180px;
  height: 260px;
  object-fit: cover;
  border-radius: 6px;
  background: #f5f5f5;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* 加入购物车按钮样式 */
.add-to-cart-btn {
  margin-top: 20px;
  width: 100%;
  background-color: #67c23a;
  border-color: #67c23a;
}

.add-to-cart-btn:hover {
  background-color: #85ce61;
  border-color: #85ce61;
}

.add-to-cart-btn:disabled {
  background-color: #ccc;
  border-color: #bbb;
  cursor: not-allowed;
}

.book-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.book-title {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
  line-height: 1.4;
}

.book-author,
.book-isbn,
.book-publisher,
.book-price,
.book-stock,
.book-desc {
  font-size: 16px;
  color: #444;
}

.price {
  color: #e67e22;
  font-weight: bold;
  font-size: 20px;
}

.discount {
  color: #67c23a;
  margin-left: 8px;
  font-size: 16px;
}

.book-stock {
  margin-top: 10px;
  font-size: 16px;
  color: #333;
  font-weight: 500;
}

.book-desc {
  margin-top: 20px;
  color: #666;
  font-size: 15px;
  line-height: 1.8;
  background: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
}
/* 收藏键 */
.favorite-btn {
  margin-top: 18px;
  width: 120px;
  align-self: flex-start;
}
/* ...existing code... */
.related-posts-card {
  margin-top: 32px;
  padding: 24px;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.related-title {
  font-size: 18px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 18px;
  border-bottom: 1px solid #eee;
  padding-bottom: 8px;
}
.related-post-item {
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background 0.2s;
}
.related-post-item:last-child {
  border-bottom: none;
}
.related-post-item:hover {
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
/* ...existing code... */
</style>