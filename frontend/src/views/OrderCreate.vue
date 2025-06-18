<template>
  <div class="order-create-container">
    <el-card>
      <h2>创建订单</h2>
      <el-form :model="form" label-width="90px" ref="formRef">
        <el-form-item label="账单地址" prop="bill_address" required>
          <el-input v-model="form.bill_address"/>
        </el-form-item>
        <el-form-item label="账单电话" prop="biller_phone" required>
          <el-input v-model="form.biller_phone"/>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark"/>
        </el-form-item>
      </el-form>
      <h3 style="margin-top:20px;">订单明细</h3>
      <el-table :data="cartBooks" style="width:100%">
        <el-table-column prop="title" label="书名"/>
        <el-table-column prop="quantity" label="数量"/>
      </el-table>
      <div style="margin-top:20px;">
        <el-button type="primary" @click="submitOrder" :loading="loading">提交订单</el-button>
        <el-button @click="goBack">返回</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const router = useRouter()
const form = ref({
  bill_address: '',
  biller_phone: '',
  remark: ''
})
const cartBooks = ref([])
const loading = ref(false)

onMounted(async () => {
  try {
    const res = await axios.get('/api/user_cart/', { withCredentials: true })
    cartBooks.value = res.data.map(item => ({
      book_id: item.book_id,
      title: item.book_title,
      quantity: item.quantity
    }))
  } catch {
    ElMessage.error('获取购物车失败')
  }
})

async function submitOrder() {
  if (!form.value.bill_address || !form.value.biller_phone) {
    ElMessage.warning('请填写完整信息')
    return
  }
  if (!cartBooks.value.length) {
    ElMessage.warning('购物车为空')
    return
  }
  const details = cartBooks.value.map(item => ({
    book_id: item.book_id,
    quantity: item.quantity
  }))


  loading.value = true
  try {
    const res = await axios.post('/api/orders/', {
      details,
      bill_address: form.value.bill_address,
      biller_phone: form.value.biller_phone,
      remark: form.value.remark
    }, { withCredentials: true })
    ElMessage.success('订单创建成功')
    router.push({ name: 'OrderDetail', params: { order_id: res.data.order_id } })
  } catch (err) {
    if (err.response?.data?.error) {
      ElMessage.error('创建订单失败1: ' + err.response.data.error)
    } else {
      ElMessage.error('创建订单失败2')
    }
  } finally {
    loading.value = false
  }
}
function goBack() {
  router.push({ name: 'OrderList' })
}
</script>

<style scoped>
.order-create-container {
  max-width: 700px;
  margin: 40px auto;
  padding: 20px;
}
</style>