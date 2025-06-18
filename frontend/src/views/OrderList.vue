<!-- filepath: c:\Users\22905\Desktop\database\bookstore\frontend\src\views\OrderList.vue -->
<template>
  <div class="order-list-container">
    <el-card>
      <h2>我的订单</h2>
      <el-table :data="orders" v-loading="loading" style="width:100%;margin-top:20px;">
        <el-table-column prop="order_id" label="订单号" width="100" />
        <el-table-column prop="order_status" label="状态" width="100" />
        <el-table-column prop="order_time" label="下单时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.order_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="总金额" width="100">
          <template #default="{ row }">
            ￥{{ row.total_amount.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button size="small" @click="goDetail(row.order_id)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && orders.length === 0" description="暂无订单" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const orders = ref([])
const loading = ref(true)
const router = useRouter()

onMounted(async () => {
  try {
    const res = await axios.get('/api/orders/', { withCredentials: true })
    orders.value = res.data
  } catch (err) {
    if (err.response?.status === 401) {
      ElMessage.error('请先登录')
      router.push('/userlogin')
    } else {
      ElMessage.error('获取订单失败')
    }
  } finally {
    loading.value = false
  }
})

function goDetail(orderId) {
  router.push({ name: 'OrderDetail', params: { order_id: orderId } })
}

function formatTime(timeStr) {
  return timeStr ? timeStr.replace('T', ' ').slice(0, 19) : ''
}
</script>

<style scoped>
.order-list-container {
  max-width: 900px;
  margin: 40px auto;
  padding: 20px;
}
</style>