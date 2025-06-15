<!-- filepath: c:\Users\22905\Desktop\database\bookstore\frontend\src\views\Cart.vue -->
<template>
  <div class="cart-container">
    <el-card class="cart-card">
      <h2>购物车</h2>
      <el-table :data="cart" v-if="cart.length" style="width: 100%">
        <el-table-column prop="title" label="书名" />
        <el-table-column prop="author" label="作者" />
        <el-table-column prop="price" label="单价" />
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
        <span>总价：<b>￥{{ totalPrice }}</b></span>
        <el-button type="primary" @click="checkout">结算</el-button>
      </div>
      <el-button class="back-btn" @click="goHome">返回首页</el-button>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

// 假设通过API获取购物车数据
const cart = ref([])

const router = useRouter()

// 模拟API请求，实际应替换为后端接口
function fetchCart() {
  // 这里用静态数据模拟
  cart.value = [
    {
      id: 1,
      title: '三体',
      author: '刘慈欣',
      price: 49.9,
      quantity: 2
    },
    {
      id: 2,
      title: '活着',
      author: '余华',
      price: 39.9,
      quantity: 1
    }
  ]
}

onMounted(() => {
  fetchCart()
})

const totalPrice = computed(() =>
  cart.value.reduce((sum, book) => sum + Number(book.price) * Number(book.quantity), 0).toFixed(2)
)

function updateQuantity(row) {
  // 实际应调用后端API更新数量
  ElMessage.success('数量已更新')
}

function removeFromCart(row) {
  // 实际应调用后端API删除
  cart.value = cart.value.filter(item => item.id !== row.id)
  ElMessage.success('已移除')
}

function checkout() {
  // 实际应调用后端API结算
  ElMessage.success('结算成功！')
  cart.value = []
}

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
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  font-size: 18px;
}
.back-btn {
  margin-top: 20px;
}
.empty-tip {
  text-align: center;
  color: #888;
  margin: 40px 0;
}
</style>