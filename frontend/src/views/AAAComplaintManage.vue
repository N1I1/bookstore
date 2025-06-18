<template>
  <div class="admin-complaint-page">
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
        <el-select v-model="statusFilter" placeholder="筛选状态" style="width:140px;" @change="fetchComplaints">
          <el-option label="全部" value="" />
          <el-option label="待处理" value="待处理" />
          <el-option label="已受理" value="已受理" />
          <el-option label="已解决" value="已解决" />
        </el-select>
      </div>
      <el-table :data="complaints" style="margin-top:20px;" v-loading="loading" empty-text="暂无投诉">
        <el-table-column prop="complaint_id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="content" label="投诉内容" />
        <el-table-column prop="complaint_time" label="投诉时间" width="170" />
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column prop="result" label="处理结果" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button
              v-if="row.status === '待处理'"
              size="small"
              type="primary"
              @click="openDealDialog(row)"
            >处理</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 处理投诉弹窗 -->
    <el-dialog v-model="showDealDialog" title="处理投诉" width="400px">
      <div style="margin-bottom:12px;">
        <strong>投诉内容：</strong>
        <div style="margin:8px 0 12px 0;">{{ dealComplaint?.content }}</div>
      </div>
      <el-input
        v-model="dealResult"
        type="textarea"
        :rows="4"
        placeholder="请输入处理结果"
        maxlength="200"
        show-word-limit
      />
      <template #footer>
        <el-button @click="showDealDialog = false">取消</el-button>
        <el-button type="primary" :loading="dealLoading" @click="dealWithComplaint">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const complaints = ref([])
const loading = ref(false)
const statusFilter = ref('')
const showDealDialog = ref(false)
const dealComplaint = ref(null)
const dealResult = ref('')
const dealLoading = ref(false)
const router = useRouter()

function goAdminHome() {
  router.push('/AAAHome') // 请确保路由名为 AdminHome
}

onMounted(fetchComplaints)

async function fetchComplaints() {
  loading.value = true
  try {
    const params = {}
    if (statusFilter.value) params.status = statusFilter.value
    const res = await axios.get('/api/complaint_manage/admin_get', {
      params,
      withCredentials: true
    })
    complaints.value = res.data.complaints || []
  } catch (err) {
    if (err.response?.status === 401) {
      ElMessage.warning('请先登录')
      router.push({ name: 'AdminLogin' })
    } else if (err.response?.status === 404) {
      complaints.value = []
    } else {
      ElMessage.error('获取投诉信息失败')
    }
  } finally {
    loading.value = false
  }
}

function openDealDialog(row) {
  dealComplaint.value = row
  dealResult.value = ''
  showDealDialog.value = true
}

async function dealWithComplaint() {
  if (!dealResult.value.trim()) {
    ElMessage.warning('处理结果不能为空')
    return
  }
  dealLoading.value = true
  try {
    await axios.post('/api/complaint_manage/deal_with_complaint', {
      complaint_id: dealComplaint.value.complaint_id,
      result: dealResult.value
    }, { withCredentials: true })
    ElMessage.success('投诉已处理')
    showDealDialog.value = false
    fetchComplaints()
  } catch (err) {
    if (err.response?.status === 401) {
      ElMessage.warning('请先登录')
      router.push({ name: 'AdminLogin' })
    } else {
      ElMessage.error(err.response?.data?.error || '处理失败')
    }
  } finally {
    dealLoading.value = false
  }
}
</script>

<style scoped>
.admin-complaint-page {
  max-width: 1000px;
  margin: 40px auto;
  padding: 24px 0;
}
</style>