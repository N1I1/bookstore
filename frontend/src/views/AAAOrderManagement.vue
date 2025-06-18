<template>
  <div class="admin-order-management">
    <el-row :gutter="24">
      <el-col :span="24">
        <el-button
          type="primary"
          icon="el-icon-arrow-left"
          class="back-admin-btn"
          @click="goAdminHome"
        >返回管理员首页</el-button>
      </el-col>
    </el-row>
    <el-card>
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <h2>分配给我的订单</h2>
        <el-button
          type="primary"
          :loading="assigning"
          @click="assignOrders"
        >刷新/分配订单</el-button>
      </div>
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
      <div v-if="orderDetail">
        <div>订单编号：{{ orderDetail.order_id }}</div>
        <div>订单状态：{{ orderDetail.order_status }}</div>
        <div>下单时间：{{ orderDetail.order_time }}</div>
        <!-- <div>收货人：{{ orderDetail.biller_name }}</div> -->
        <div>收货人电话：{{ orderDetail.biller_phone }}</div>
        <div>收货地址：{{ orderDetail.bill_address }}</div>
        <div>发货地址：{{ orderDetail.ship_address || '未填写' }}</div>
        <div>当前运输地址：{{ orderDetail.current_address || '未填写' }}</div>
        <div>发货人电话：{{ orderDetail.shipper_phone || '未填写' }}</div>
        <div>发货时间：{{ orderDetail.ship_time || '未发货' }}</div>
        <div>完成时间：{{ orderDetail.get_time || '未完成' }}</div>
        <div style="margin: 16px 0 0 0; font-weight:bold;">操作区：</div>
        <!-- 已支付：可填写发货人电话、发货地址 -->
        <el-form v-if="canShip" label-width="100px" style="margin-top:10px;">
          <el-form-item label="发货人电话">
            <el-input v-model="shipForm.shipper_phone" placeholder="请输入发货人电话" />
          </el-form-item>
          <el-form-item label="发货地址">
            <el-input v-model="shipForm.ship_address" placeholder="请输入发货地址" />
          </el-form-item>
        </el-form>
        <!-- 已发货：仅可修改当前运输地址 -->
        <el-form v-else-if="canEditShip" label-width="100px" style="margin-top:10px;">
          <el-form-item label="当前运输地址">
            <el-input v-model="shipForm.current_address" placeholder="请输入当前运输地址" />
          </el-form-item>
        </el-form>
        <!-- 已完成：只读，无表单 -->
        <div v-else style="margin-top:10px;color:#888;">订单已完成，所有信息只读。</div>
      </div>
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
import { ref, reactive, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const orders = ref([])
const loading = ref(true)
const showDetailDialog = ref(false)
const orderDetail = ref(null)
const shipForm = reactive({
  ship_address: '',
  shipper_phone: '',
  current_address: ''
})
const shipLoading = ref(false)
const editShipLoading = ref(false)
const assigning = ref(false)
const router = useRouter()

function goAdminHome() {
  router.push('/AAAHome') // 请确保路由名为 AdminHome
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
    // 初始化表单
    shipForm.ship_address = res.data.ship_address || ''
    shipForm.shipper_phone = res.data.shipper_phone || ''
    shipForm.current_address = res.data.current_address || ''
    showDetailDialog.value = true
  } catch (err) {
    ElMessage.error('获取订单详情失败')
  }
}

// 已支付未发货订单可发货
const canShip = computed(() =>
  orderDetail.value &&
  orderDetail.value.order_status === '已支付' &&
  !orderDetail.value.ship_time
)
// 已发货未完成订单可修改运输地址
const canEditShip = computed(() =>
  orderDetail.value &&
  orderDetail.value.order_status === '已发货'
)

async function shipOrder() {
  // 校验
  if (!shipForm.ship_address.trim()) {
    ElMessage.warning('请填写发货地址')
    return
  }
  if (!shipForm.shipper_phone.trim()) {
    ElMessage.warning('请填写发货人电话')
    return
  }
  shipLoading.value = true
  try {
    await axios.post(`/api/orders/${orderDetail.value.order_id}/ship`, {
      ship_address: shipForm.ship_address,
      current_address: shipForm.ship_address, // 发货时当前地址=发货地址
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
  if (!shipForm.current_address.trim()) {
    ElMessage.warning('请填写当前运输地址')
    return
  }
  editShipLoading.value = true
  try {
    await axios.put(`/api/orders/${orderDetail.value.order_id}/ship_address`, {
      current_address: shipForm.current_address
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

async function assignOrders() {
  assigning.value = true
  try {
    const res = await axios.post('/api/orders/assign_admin', {}, { withCredentials: true })
    ElMessage.success(res.data.message || '分配成功')
    fetchOrders()
  } catch (err) {
    ElMessage.error(err.response?.data?.error || '分配失败')
  } finally {
    assigning.value = false
  }
}
</script>

<style scoped>
.admin-order-management {
  padding: 32px 24px;
}
</style>
