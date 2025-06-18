<template>
  <div class="complaint-page">
    <el-card>
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
          <el-select v-model="statusFilter" placeholder="筛选状态" style="width:140px;" @change="fetchComplaints">
            <el-option label="全部" value="" />
            <el-option label="待处理" value="待处理" />
            <el-option label="已受理" value="已受理" />
            <el-option label="已解决" value="已解决" />
          </el-select>
        </div>
        <el-button type="primary" @click="showCreateDialog = true">我要投诉</el-button>
      </div>
      <el-table :data="complaints" style="margin-top:20px;" v-loading="loading" empty-text="暂无投诉">
        <el-table-column prop="content" label="投诉内容" />
        <el-table-column prop="complaint_time" label="投诉时间" width="170" />
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column prop="result" label="处理结果" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button
              v-if="row.status === '已受理'"
              size="small"
              type="success"
              @click="markResolved(row.complaint_id)"
            >已解决</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建投诉弹窗 -->
    <el-dialog v-model="showCreateDialog" title="我要投诉" width="400px">
      <el-input
        v-model="newComplaint"
        type="textarea"
        :rows="5"
        placeholder="请输入投诉内容"
        maxlength="200"
        show-word-limit
      />
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="createLoading" @click="createComplaint">提交</el-button>
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
const showCreateDialog = ref(false)
const newComplaint = ref('')
const createLoading = ref(false)
const router = useRouter()

onMounted(fetchComplaints)

async function fetchComplaints() {
  loading.value = true
  try {
    const params = {}
    if (statusFilter.value) params.status = statusFilter.value
    const res = await axios.get('/api/complaint_manage/user_get', {
      params,
      withCredentials: true
    })
    complaints.value = res.data.complaints || []
  } catch (err) {
    if (err.response?.status === 401) {
      ElMessage.warning('请先登录')
      router.push({ name: 'UserLogin' })
    } else if (err.response?.status === 404) {
      complaints.value = []
    } else {
      ElMessage.error('获取投诉信息失败')
    }
  } finally {
    loading.value = false
  }
}

async function createComplaint() {
  if (!newComplaint.value.trim()) {
    ElMessage.warning('投诉内容不能为空')
    return
  }
  createLoading.value = true
  try {
    await axios.post('/api/complaint_manage/user_create', {
      content: newComplaint.value
    }, { withCredentials: true })
    ElMessage.success('投诉已提交')
    showCreateDialog.value = false
    newComplaint.value = ''
    fetchComplaints()
  } catch (err) {
    if (err.response?.status === 401) {
      ElMessage.warning('请先登录')
      router.push({ name: 'UserLogin' })
    } else {
      ElMessage.error(err.response?.data?.error || '提交失败')
    }
  } finally {
    createLoading.value = false
  }
}

async function markResolved(complaint_id) {
  try {
    await axios.post('/api/complaint_manage/user_change_status', {
      complaint_id
    }, { withCredentials: true })
    ElMessage.success('状态已更新为已解决')
    fetchComplaints()
  } catch (err) {
    if (err.response?.status === 401) {
      ElMessage.warning('请先登录')
      router.push({ name: 'UserLogin' })
    } else {
      ElMessage.error(err.response?.data?.error || '操作失败')
    }
  }
}
</script>

<style scoped>
.complaint-page {
  max-width: 900px;
  margin: 40px auto;
  padding: 24px 0;
}
</style>