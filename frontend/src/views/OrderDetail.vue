<template>
  <div class="order-detail-container" v-if="order">
    <el-card>
      <h2>订单详情</h2>
      <div>订单号：{{ order.order_id }}</div>
      <div>状态：{{ order.order_status }}</div>
      <div>下单时间：{{ order.order_time }}</div>
      <div v-if="order.payment_time">支付时间：{{ order.payment_time }}</div>
      <div v-if="order.ship_time">发货时间：{{ order.ship_time }}</div>
      <div v-if="order.get_time">收货时间：{{ order.get_time }}</div>
      <div>账单地址：{{ order.bill_address }}</div>
      <div>账单电话：{{ order.biller_phone }}</div>
      <div>备注：{{ order.remark }}</div>
      <div>总金额：￥{{ order.total_amount }}</div>
      <el-table :data="order.details" style="width:100%;margin-top:20px;">
        <el-table-column prop="book_title" label="书名"/>
        <el-table-column prop="quantity" label="数量"/>
        <el-table-column prop="unit_price" label="单价"/>
      </el-table>
      <div style="margin-top:20px;">
        <el-button v-if="order.order_status==='未支付'" type="primary" @click="payOrder">支付</el-button>
        <el-button v-if="order.order_status==='未支付'" @click="editOrder">修改</el-button>
        <el-button v-if="order.order_status==='未支付'" type="danger" @click="deleteOrder">删除</el-button>
        <el-button v-if="order.order_status==='未支付'" @click="cancelOrder">取消</el-button>
        <el-button v-if="order.order_status==='已发货'" type="success" @click="confirmOrder">确认收货</el-button>
        <el-button @click="goBack">返回</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const order = ref(null)

async function fetchOrder() {
  try {
    const res = await axios.get(`/api/orders/${route.params.order_id}`, {
      withCredentials: true
    });
    
    // 映射API字段到前端
    order.value = {
      ...res.data,
      // 添加时间格式化
      order_time: formatTime(res.data.order_time),
      payment_time: formatTime(res.data.payment_time),
      ship_time: formatTime(res.data.ship_time),
      get_time: formatTime(res.data.get_time)
    };
  } catch (err) {
    if (err.response?.status === 403) {
      ElMessage.error('无权查看此订单');
    } else if (err.response?.status === 404) {
      ElMessage.error('订单不存在');
    } else {
      ElMessage.error('获取订单详情失败');
    }
  }
}

// 添加时间格式化函数
function formatTime(timeStr) {
  return timeStr ? timeStr.replace('T', ' ').slice(0, 19) : '';
}

function goBack() {
  router.push({ name: 'OrderList' })
}
function editOrder() {
  router.push({ name: 'OrderEdit', params: { order_id: order.value.order_id } })
}
async function deleteOrder() {
  ElMessageBox.confirm('确定要删除该订单吗？', '提示', { type: 'warning' })
    .then(async () => {
      try {
        await axios.delete(`/api/orders/${order.value.order_id}`, { withCredentials: true })
        ElMessage.success('删除成功')
        goBack()
      } catch {
        ElMessage.error('删除失败')
      }
    })
}
async function payOrder() {
  try {
    await axios.post(`/api/orders/${order.value.order_id}/pay`, {}, { withCredentials: true })
    ElMessage.success('支付成功')
    fetchOrder()
  } catch {
    ElMessage.error('支付失败')
  }
}
async function cancelOrder() {
  try {
    await axios.post(`/api/orders/${order.value.order_id}/cancel`, {}, { withCredentials: true })
    ElMessage.success('已取消')
    fetchOrder()
  } catch {
    ElMessage.error('取消失败')
  }
}
async function confirmOrder() {
  try {
    await axios.post(`/api/orders/${order.value.order_id}/confirm`, {}, { withCredentials: true })
    ElMessage.success('已确认收货')
    fetchOrder()
  } catch {
    ElMessage.error('确认收货失败')
  }
}
</script>

<style scoped>
.order-detail-container {
  max-width: 800px;
  margin: 40px auto;
  padding: 20px;
}
</style>