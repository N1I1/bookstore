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
      <div>收货地址：{{ order.ship_address }}</div>
      <div>
        账单地址：
        <span v-if="!editMode">{{ order.bill_address }}</span>
        <el-input v-else v-model="editForm.bill_address" size="small" style="width: 300px;" />
      </div>
      <div>
        账单电话：
        <span v-if="!editMode">{{ order.biller_phone }}</span>
        <el-input v-else v-model="editForm.biller_phone" size="small" style="width: 200px;" />
      </div>
      <div>当前运输地址：{{ order.current_address }}</div>
      <div>发货人电话：{{ order.shipper_phone }}</div>
      <div>
        备注：
        <span v-if="!editMode">{{ order.remark }}</span>
        <el-input v-else v-model="editForm.remark" size="small" style="width: 400px;" />
      </div>
      <div>总金额：￥{{ order.total_amount }}</div>
      <el-table :data="order.details" style="width:100%;margin-top:20px;">
        <el-table-column prop="book_title" label="书名"/>
        <el-table-column prop="quantity" label="数量"/>
        <el-table-column prop="unit_price" label="单价"/>
      </el-table>
      <div style="margin-top:20px;">
        <el-button @click="goBack">返回</el-button>
        <el-button
          v-if="order.order_status === '未支付' && !editMode"
          type="primary"
          @click="editMode = true"
        >修改订单</el-button>
        <el-button
          v-if="order.order_status === '未支付' && editMode"
          type="success"
          @click="submitEdit"
          :loading="editLoading"
        >保存</el-button>
        <el-button
          v-if="order.order_status === '未支付' && editMode"
          @click="cancelEdit"
        >取消</el-button>
        <el-button
          v-if="order.order_status === '未支付' && !editMode"
          type="warning"
          @click="payOrder"
          :loading="payLoading"
        >支付订单</el-button>
        <el-button
          v-if="order.order_status === '未支付' && !editMode"
          type="danger"
          @click="cancelOrder"
          :loading="cancelLoading"
        >取消订单</el-button>
      </div>
    </el-card>
  </div>
  <el-empty v-else description="未找到订单" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const order = ref(null)
const editMode = ref(false)
const editForm = ref({
  bill_address: '',
  biller_phone: '',
  remark: ''
})
const editLoading = ref(false)
const payLoading = ref(false)
const cancelLoading = ref(false)

onMounted(fetchOrder)

async function fetchOrder() {
  try {
    const res = await axios.get(`/api/orders/${route.params.order_id}`, {
      withCredentials: true
    })
    order.value = {
      ...res.data,
      order_time: formatTime(res.data.order_time),
      payment_time: formatTime(res.data.payment_time),
      ship_time: formatTime(res.data.ship_time),
      get_time: formatTime(res.data.get_time)
    }
    // 初始化编辑表单
    editForm.value = {
      bill_address: res.data.bill_address || '',
      biller_phone: res.data.biller_phone || '',
      remark: res.data.remark || ''
    }
  } catch (err) {
    if (err.response?.status === 401) {
      ElMessage.error('请先登录')
      router.push('/userlogin')
    } else if (err.response?.status === 403) {
      ElMessage.error('无权查看此订单')
      router.push({ name: 'OrderList' })
    } else if (err.response?.status === 404) {
      ElMessage.error('订单不存在')
      router.push({ name: 'OrderList' })
    } else {
      ElMessage.error('获取订单详情失败')
    }
  }
}

function formatTime(timeStr) {
  return timeStr ? timeStr.replace('T', ' ').slice(0, 19) : ''
}

function goBack() {
  router.push({ name: 'OrderList' })
}

function cancelEdit() {
  editMode.value = false
  // 恢复原始数据
  editForm.value = {
    bill_address: order.value.bill_address || '',
    biller_phone: order.value.biller_phone || '',
    remark: order.value.remark || ''
  }
}

async function submitEdit() {
  editLoading.value = true
  try {
    const payload = {
      bill_address: editForm.value.bill_address,
      biller_phone: editForm.value.biller_phone,
      remark: editForm.value.remark
    }
    const res = await axios.put(`/api/orders/${order.value.order_id}`, payload, {
      withCredentials: true
    })
    ElMessage.success('订单修改成功')
    editMode.value = false
    await fetchOrder()
  } catch (err) {
    if (err.response?.status === 400) {
      ElMessage.error('订单状态不允许或无可更新字段')
    } else if (err.response?.status === 401) {
      ElMessage.error('请先登录')
      router.push('/userlogin')
    } else if (err.response?.status === 403) {
      ElMessage.error('无权修改此订单')
    } else if (err.response?.status === 404) {
      ElMessage.error('订单不存在')
      router.push({ name: 'OrderList' })
    } else {
      ElMessage.error('修改订单失败')
    }
  } finally {
    editLoading.value = false
  }
}

async function payOrder() {
  payLoading.value = true
  try {
    const res = await axios.post(`/api/orders/${order.value.order_id}/pay`, {}, {
      withCredentials: true
    })
    ElMessage.success('支付成功')
    await fetchOrder()
  } catch (err) {
    if (err.response?.status === 400) {
      ElMessage.error('订单状态不允许支付')
    } else if (err.response?.status === 401) {
      ElMessage.error('请先登录')
      router.push('/userlogin')
    } else if (err.response?.status === 403) {
      ElMessage.error('无权支付此订单')
    } else if (err.response?.status === 404) {
      ElMessage.error('订单不存在')
      router.push({ name: 'OrderList' })
    } else {
      ElMessage.error('支付失败')
    }
  } finally {
    payLoading.value = false
  }
}

async function cancelOrder() {
  cancelLoading.value = true
  try {
    const res = await axios.post(`/api/orders/${order.value.order_id}/cancel`, {}, {
      withCredentials: true
    })
    ElMessage.success('订单已取消')
    await fetchOrder()
  } catch (err) {
    if (err.response?.status === 400) {
      ElMessage.error('订单状态不允许取消')
    } else if (err.response?.status === 401) {
      ElMessage.error('请先登录')
      router.push('/userlogin')
    } else if (err.response?.status === 403) {
      ElMessage.error('无权取消此订单')
    } else if (err.response?.status === 404) {
      ElMessage.error('订单不存在')
      router.push({ name: 'OrderList' })
    } else {
      ElMessage.error('取消订单失败')
    }
  } finally {
    cancelLoading.value = false
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