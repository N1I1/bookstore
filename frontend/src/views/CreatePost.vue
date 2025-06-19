<template>
  <div class="create-post-container">
    <el-row align="middle" style="margin-bottom: 24px;">
      <el-col :span="24">
        <el-button
          type="primary"
          icon="el-icon-arrow-left"
          class="back-btn"
          @click="goUserHome"
        >返回首页</el-button>
      </el-col>
    </el-row>
    <el-card class="post-form">
      <h2>创建新帖子</h2>
      <el-form 
        :model="postForm" 
        label-width="80px"
        :rules="rules"
        ref="postFormRef"
      >
        <el-form-item label="标题" prop="title">
          <el-input 
            v-model="postForm.title" 
            placeholder="请输入帖子标题"
          ></el-input>
        </el-form-item>
        
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="postForm.content"
            type="textarea"
            :rows="6"
            placeholder="请输入帖子内容"
            resize="none"
          ></el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="submitForm"
            :loading="submitting"
          >
            提交
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
  <el-dialog
      v-model="showLoginDialog"
      title="提示"
      width="340px"
      :close-on-click-modal="false"
      :show-close="false"
    >
      <div style="text-align:center;">
        <p style="margin-bottom:18px;">请先登录后再进行操作</p>
        <el-button @click="goUserHome" style="margin-right:16px;">暂不登录</el-button>
        <el-button type="primary" @click="goUserLogin">去登录</el-button>
      </div>
    </el-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 登录弹窗控制
const showLoginDialog = ref(false)
function handleLoginRequired() {
  showLoginDialog.value = true
}
function goUserHome() {
  showLoginDialog.value = false
  router.push('/home')
}
function goUserLogin() {
  showLoginDialog.value = false
  router.push('/userlogin')
}
// 登录弹窗控制

// 获取 book_id 参数
const bookId = ref('')
onMounted(() => {
  bookId.value = route.query.book_id || ''
})

// 表单数据
const postForm = ref({
  title: '',
  content: ''
})

// 表单验证规则
const rules = {
  title: [
    { min: 0, max: 50, message: '标题最长 50 个字符', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入内容', trigger: 'blur' },
    { min: 10, message: '内容至少 10 个字符', trigger: 'blur' }
  ]
}

// 表单引用
const postFormRef = ref(null)
// 提交状态
const submitting = ref(false)

// 提交表单
const submitForm = () => {
  postFormRef.value.validate(async (valid) => {
    if (!valid) {
      ElMessage.warning('请填写完整的表单信息')
      return
    }

    submitting.value = true
    try {
      // 构造请求体
      const payload = {
        title: postForm.value.title?.trim() ? postForm.value.title : 'Untitled Post',
        content: postForm.value.content,
      }
      if (bookId.value) {
        payload.book_id = Number(bookId.value)
      }

      const response = await axios.post(
        '/api/forum_posts/',
        payload,
        { withCredentials: true }
      )

      if (response.status === 201) {
        ElMessage.success('帖子创建成功')
        // 跳转回书籍详情页（如有 book_id）
        if (bookId.value) {
          router.push(`/book/${bookId.value}`)
        } else {
          router.push('/home')
        }
      } else {
        ElMessage.error(response.data.Message || '创建失败')
      }
    } catch (error) {
      if (error.response?.status === 401) {
        ElMessage.warning('请先登录')
        handleLoginRequired()
      } else {
        ElMessage.error('创建帖子失败: ' + (error.response?.data?.Message || error.message))
      }
    } finally {
      submitting.value = false
    }
  })
}

// 重置表单
const resetForm = () => {
  postFormRef.value.resetFields()
}
</script>

<style scoped>
.page-container {
  max-width: 900px;
  margin: 40px auto 0 auto;
  padding: 32px 24px 24px 24px;
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 2px 12px #0000000d;
  min-height: 70vh;
}
.back-btn {
  margin-bottom: 12px;
  font-size: 15px;
  letter-spacing: 1px;
}
.main-content {
  padding: 24px 0 0 0;
}
</style>