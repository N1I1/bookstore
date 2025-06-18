<template>
  <div class="admin-order-management">
    <el-card>
      <h2>分配给我的订单</h2>
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
            <el-button size="small" @click="viewOrder(row.order_id)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && orders.length === 0" description="暂无订单" />
    </el-card>

    <!-- 订单详情弹窗 -->
    <el-dialog v-model="showDetailDialog" title="订单详情" width="600px">
      <el-form v-if="orderDetail" label-width="100px">
        <el-form-item label="订单号">{{ orderDetail.order_id }}</el-form-item>
        <el-form-item label="状态">{{ orderDetail.order_status }}</el-form-item>
        <el-form-item label="下单时间">{{ orderDetail.order_time }}</el-form-item>
        <el-form-item label="支付时间" v-if="orderDetail.payment_time">{{ orderDetail.payment_time }}</el-form-item>
        <el-form-item label="发货时间" v-if="orderDetail.ship_time">{{ orderDetail.ship_time }}</el-form-item>
        <el-form-item label="收货时间" v-if="orderDetail.get_time">{{ orderDetail.get_time }}</el-form-item>
        <el-form-item label="收货地址">{{ orderDetail.ship_address }}</el-form-item>
        <el-form-item label="账单地址">{{ orderDetail.bill_address }}</el-form-item>
        <el-form-item label="当前运输地址">
          <el-input v-model="shipForm.current_address" :disabled="!canEditShip" />
        </el-form-item>
        <el-form-item label="发货人电话">
          <el-input v-model="shipForm.shipper_phone" :disabled="!canEditShip" />
        </el-form-item>
        <el-form-item label="备注">{{ orderDetail.remark }}</el-form-item>
        <el-form-item label="总金额">￥{{ orderDetail.total_amount }}</el-form-item>
        <el-form-item label="订单明细">
          <el-table :data="orderDetail.details" size="small" style="width:100%;">
            <el-table-column prop="book_title" label="书名"/>
            <el-table-column prop="quantity" label="数量"/>
            <el-table-column prop="unit_price" label="单价"/>
          </el-table>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button
          v-if="canShip"
          type="primary"
          :loading="shipLoading"
          @click="shipOrder"
        >发货</el-button>
        <el-button
          v-if="canEditShip"
          type="success"
          :loading="editShipLoading"
          @click="updateShipAddress"
        >修改运输地址</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const orders = ref([])
const loading = ref(true)
const showDetailDialog = ref(false)
const orderDetail = ref(null)
const shipForm = reactive({
  current_address: '',
  shipper_phone: ''
})
const shipLoading = ref(false)
const editShipLoading = ref(false)

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

function formatTime(timeStr) {
  return timeStr ? timeStr.replace('T', ' ').slice(0, 19) : ''
}

async function viewOrder(orderId) {
  try {
    const res = await axios.get(`/api/orders/${orderId}`, { withCredentials: true })
    orderDetail.value = {
      ...res.data,
      order_time: formatTime(res.data.order_time),
      payment_time: formatTime(res.data.payment_time),
      ship_time: formatTime(res.data.ship_time),
      get_time: formatTime(res.data.get_time)
    }
    shipForm.current_address = res.data.current_address || ''
    shipForm.shipper_phone = res.data.shipper_phone || ''
    showDetailDialog.value = true
  } catch (err) {
    ElMessage.error('获取订单详情失败')
  }
}

// 仅已支付未发货订单可发货
const canShip = computed(() =>
  orderDetail.value &&
  orderDetail.value.order_status === '已支付' &&
  !orderDetail.value.ship_time
)
// 仅已发货未收货订单可修改运输地址
const canEditShip = computed(() =>
  orderDetail.value &&
  orderDetail.value.order_status === '已发货'
)

async function shipOrder() {
  shipLoading.value = true
  try {
    await axios.post(`/api/orders/${orderDetail.value.order_id}/ship`, {
      ship_address: orderDetail.value.ship_address,
      current_address: shipForm.current_address,
      shipper_phone: shipForm.shipper_phone
    }, { withCredentials: true })
    ElMessage.success('发货成功')
    showDetailDialog.value = false
    fetchOrders()
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '发货失败')
  } finally {
    shipLoading.value = false
  }
}

async function updateShipAddress() {
  editShipLoading.value = true
  try {
    await axios.put(`/api/orders/${orderDetail.value.order_id}/ship_address`, {
      current_address: shipForm.current_address,
      // ship_address 可选，如需修改可加上
    }, { withCredentials: true })
    ElMessage.success('运输地址已更新')
    showDetailDialog.value = false
    fetchOrders()
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '修改失败')
  } finally {
    editShipLoading.value = false
  }
}
</script>

<style scoped>
.admin-order-management {
  padding: 32px 24px;
}
</style>