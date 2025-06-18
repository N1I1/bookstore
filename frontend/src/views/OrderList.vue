<template>
  <div class="order-list-container">
    <el-card>
      <h2>我的订单</h2>
      <el-table :data="orders" v-loading="loading" style="width:100%">
        <el-table-column prop="order_id" label="订单号" width="100"/>
        <el-table-column prop="order_status" label="状态" width="100"/>
        <el-table-column prop="order_time" label="下单时间" width="180"/>
        <el-table-column prop="total_amount" label="总金额" width="100"/>
        <el-table-column label="操作" width="260">
          <template #default="scope">
            <el-button size="small" @click="viewDetail(scope.row)">详情</el-button>
            <el-button v-if="scope.row.order_status==='未支付'" size="small" type="primary" @click="payOrder(scope.row)">支付</el-button>
            <el-button v-if="scope.row.order_status==='未支付'" size="small" @click="editOrder(scope.row)">修改</el-button>
            <el-button v-if="scope.row.order_status==='未支付'" size="small" type="danger" @click="deleteOrder(scope.row)">删除</el-button>
            <el-button v-if="scope.row.order_status==='未支付'" size="small" @click="cancelOrder(scope.row)">取消</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const orders = ref([])
const loading = ref(false)
const router = useRouter()

async function fetchOrders() {
  loading.value = true;
  try {
    const res = await axios.get('/api/orders/', { 
      withCredentials: true 
    });
    
    orders.value = res.data.map(order => ({
      ...order,
      // 添加时间格式化
      order_time: order.order_time.replace('T', ' ').slice(0, 19)
    }));
  } catch (err) {
    ElMessage.error('获取订单失败');
  } finally {
    loading.value = false;
  }
}

// 在所有操作函数中添加错误处理
async function deleteOrder(row) {
  try {
    await axios.delete(`/api/orders/${row.order_id}`, { 
      withCredentials: true 
    });
    ElMessage.success('删除成功');
    fetchOrders();
  } catch (err) {
    if (err.response?.status === 400) {
      ElMessage.error(err.response.data.error || '删除失败');
    } else if (err.response?.status === 403) {
      ElMessage.error('无权删除此订单');
    } else {
      ElMessage.error('删除失败');
    }
  }
}

function viewDetail(row) {
  router.push({ name: 'OrderDetail', params: { order_id: row.order_id } })
}
function editOrder(row) {
  router.push({ name: 'OrderEdit', params: { order_id: row.order_id } })
}
async function payOrder(row) {
  try {
    await axios.post(`/api/orders/${row.order_id}/pay`, {}, { withCredentials: true })
    ElMessage.success('支付成功')
    fetchOrders()
  } catch {
    ElMessage.error('支付失败')
  }
}
async function cancelOrder(row) {
  try {
    await axios.post(`/api/orders/${row.order_id}/cancel`, {}, { withCredentials: true })
    ElMessage.success('已取消')
    fetchOrders()
  } catch {
    ElMessage.error('取消失败')
  }
}
</script>

<style scoped>
.order-list-container {
  max-width: 900px;
  margin: 40px auto;
  padding: 20px;
}
</style>