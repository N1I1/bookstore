<template>
  <div class="user-order-page">
    <el-row style="margin-bottom: 16px;">
      <el-col :span="24">
        <el-button
          type="primary"
          icon="el-icon-arrow-left"
          @click="goHome"
        >返回首页</el-button>
      </el-col>
    </el-row>
    <el-card>
      <el-table :data="orders" v-loading="loading" style="width:100%;">
        <el-table-column prop="order_id" label="订单号" width="100" />
        <el-table-column prop="order_status" label="状态" width="120" />
        <el-table-column prop="order_time" label="下单时间" width="180" />
        <el-table-column prop="total_amount" label="总金额" width="100">
          <template #default="{ row }">
            ￥{{ row.total_amount.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button size="small" @click="viewOrder(row.order_id)">详情</el-button>
            <el-button
              v-if="row.order_status === '已完成' || row.order_status === '订单取消'"
              size="small"
              type="danger"
              @click="deleteOrder(row.order_id)"
            >删除订单</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 订单详情弹窗等可按需添加 -->
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
import axios from 'axios'
import { ElMessage } from 'element-plus'

const router = useRouter()
const orders = ref([])
const loading = ref(false)

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

function goHome() {
  router.push('/home') // 请确保首页路由名为 Home
}

onMounted(fetchOrders)

async function fetchOrders() {
  loading.value = true
  try {
    const res = await axios.get('/api/orders/', { withCredentials: true })
    orders.value = res.data
  } catch (err) {
    orders.value = []
  } finally {
    loading.value = false
  }
}

async function deleteOrder(orderId) {
  try {
    await axios.delete(`/api/orders/${orderId}`, { withCredentials: true })
    ElMessage.success('订单已删除')
    fetchOrders()
  } catch (err) {
    if (err.response?.status === 400) {
      ElMessage.error('订单状态不允许删除')
    } else if (err.response?.status === 401) {
      ElMessage.error('请先登录')
      handleLoginRequired()
    } else if (err.response?.status === 403) {
      ElMessage.error('只能删除自己的订单')
    } else if (err.response?.status === 404) {
      ElMessage.error('订单不存在')
    } else {
      ElMessage.error('删除失败')
    }
  }
}

function viewOrder(orderId) {
  // 跳转或弹窗显示订单详情
  router.push({ name: 'OrderDetail', params: { order_id: orderId } })
}
</script>

<style scoped>
.user-order-page {
  max-width: 1000px;
  margin: 40px auto;
  padding: 24px;
}
</style>