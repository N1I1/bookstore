<template>
  <div class="cart-container">
    <el-card class="cart-card">
      <h2>购物车</h2>
      <el-table :data="cart" v-if="cart.length" style="width: 100%">
        <el-table-column prop="book_title" label="书名" />
        <el-table-column prop="quantity" label="数量">
          <template #default="scope">
            <el-input-number
              v-model="scope.row.quantity"
              :min="1"
              @change="updateQuantity(scope.row)"
              size="small"
            />
          </template>
        </el-table-column>
        <el-table-column prop="add_time" label="添加时间" width="180">
          <template #default="scope">
            {{ formatTime(scope.row.add_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button type="danger" size="small" @click="removeFromCart(scope.row)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div v-else class="empty-tip">
        购物车为空
      </div>
      <div class="cart-footer" v-if="cart.length">
        <el-button 
          type="primary" 
          @click="checkout"
          :loading="isCheckingOut"
          :disabled="isCheckingOut"
        >
          结算
          <el-icon v-if="isCheckingOut"><i class="el-icon-loading"></i></el-icon>
        </el-button>
      </div>
      <el-button class="back-btn" @click="goHome">返回首页</el-button>
    </el-card>
  </div>
  <el-dialog
    v-model="showLoginDialog"
    title="提示"
    width="340px"
    :close-on-click-modal="false"
    :show-close="false"
  >
    <div style="text-align:center;">
      <p style="margin-bottom:18px;">请先登录后再进行操作</p>
      <el-button @click="goUserHome" style="margin-right:16px;">暂不登录</el-button>
      <el-button type="primary" @click="goUserLogin">去登录</el-button>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// 购物车数据
const cart = ref([])
const isCheckingOut = ref(false)
const router = useRouter()

// 登录弹窗控制
const showLoginDialog = ref(false)
function handleLoginRequired() {
  showLoginDialog.value = true
}
function goUserHome() {
  showLoginDialog.value = false
  router.push('/home')
}
function goUserLogin() {
  showLoginDialog.value = false
  router.push('/userlogin')
}
// 登录弹窗控制

// 从API获取购物车数据
async function fetchCart() {
  try {
    const res = await axios.get('/api/user_cart/', { withCredentials: true })
    cart.value = res.data
  } catch (err) {
    if (err.response && err.response.status === 401) {
      ElMessage.warning('请先登录')
      handleLoginRequired()
    } else {
      ElMessage.error('获取购物车失败')
    }
    cart.value = []
  }
}

onMounted(() => {
  fetchCart()
})

// 格式化时间显示
function formatTime(timeStr) {
  if (!timeStr) return ''
  return timeStr.replace('T', ' ').slice(0, 19)
}

// 更新商品数量
async function updateQuantity(row) {
  try {
    await axios.put('/api/user_cart/', {
      cart_id: row.cart_id,
      quantity: row.quantity
    }, { withCredentials: true })
    ElMessage.success('数量已更新')
  } catch (err) {
    ElMessage.error('更新数量失败')
    // 更新失败后刷新数据还原状态
    fetchCart()
  }
}

// 从购物车移除商品
async function removeFromCart(row) {
  try {
    await axios.delete('/api/user_cart/', {
      data: { cart_id: row.cart_id },
      withCredentials: true
    })
    ElMessage.success('已移除')
    // 重新获取购物车数据
    fetchCart()
  } catch (err) {
    ElMessage.error('移除失败')
  }
}

async function checkout() {
  if (cart.value.length === 0) return;
  
  // 跳转到订单创建页面，携带购物车数据
  router.push({
    name: 'OrderCreate',
    state: {
      cartItems: cart.value.map(item => ({
        book_id: item.book_id,
        quantity: item.quantity,
        book_title: item.book_title,
        unit_price: item.unit_price
      }))
    }
  });
}

// 返回首页
function goHome() {
  router.push('/home')
}
</script>

<style scoped>
.cart-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 80vh;
  background: #f5f5f5;
  padding-top: 40px;
}
.cart-card {
  width: 700px;
  padding: 30px 20px;
}
.cart-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
.back-btn {
  margin-top: 20px;
  width: 100%;
}
.empty-tip {
  text-align: center;
  color: #888;
  margin: 40px 0;
}
</style>