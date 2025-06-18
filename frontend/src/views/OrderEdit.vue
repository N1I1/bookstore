<template>
  <div class="order-edit-container" v-if="order">
    <el-card>
      <h2>修改订单</h2>
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
      <div style="margin-top:20px;">
        <el-button type="primary" @click="submitEdit" :loading="loading">保存</el-button>
        <el-button @click="goBack">返回</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const order = ref(null)
const form = ref({
  bill_address: '',
  biller_phone: '',
  remark: ''
})
const loading = ref(false)

onMounted(async () => {
  try {
    const res = await axios.get(`/api/orders/${route.params.order_id}`, { withCredentials: true })
    order.value = res.data
    form.value.bill_address = order.value.bill_address
    form.value.biller_phone = order.value.biller_phone
    form.value.remark = order.value.remark
  } catch {
    ElMessage.error('获取订单失败')
  }
})

async function submitEdit() {
  // 确保订单状态是未支付
  if (order.value?.order_status !== '未支付') {
    ElMessage.warning('只有未支付订单可修改');
    return;
  }
  
  if (!form.value.bill_address || !form.value.biller_phone) {
    ElMessage.warning('请填写完整信息');
    return;
  }
  
  loading.value = true;
  try {
    await axios.put(`/api/orders/${route.params.order_id}`, {
      bill_address: form.value.bill_address,
      biller_phone: form.value.biller_phone,
      remark: form.value.remark || ""
    }, { withCredentials: true });
    
    ElMessage.success('修改成功');
    router.push({ 
      name: 'OrderDetail', 
      params: { order_id: route.params.order_id } 
    });
  } catch (err) {
    if (err.response?.status === 400) {
      ElMessage.error(err.response.data.error || '修改失败');
    } else if (err.response?.status === 403) {
      ElMessage.error('无权修改此订单');
    } else {
      ElMessage.error('修改失败');
    }
  } finally {
    loading.value = false;
  }
}
function goBack() {
  router.push({ name: 'OrderDetail', params: { order_id: route.params.order_id } })
}
</script>

<style scoped>
.order-edit-container {
  max-width: 700px;
  margin: 40px auto;
  padding: 20px;
}
</style>