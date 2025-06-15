<!-- filepath: c:\Users\22905\Desktop\database\bookstore\frontend\src\views\UserInfo.vue -->
<template>
  <div class="user-info-container">
    <el-card class="user-info-card">
      <div class="user-header">
        <el-avatar icon="el-icon-user" size="large" />
        <div class="user-basic">
          <h2>{{ user.username }}</h2>
          <p>邮箱：{{ user.email }}</p>
        </div>
      </div>
      <el-divider />
      <div class="user-actions">
        <el-button type="primary" @click="showChangePwd = true">修改密码</el-button>
        <el-button type="danger" @click="confirmLogout">注销用户</el-button>
        <el-button @click="goHome">返回首页</el-button>
      </div>
    </el-card>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="showChangePwd" title="修改密码" width="400px">
      <el-form :model="pwdForm" :rules="pwdRules" ref="pwdFormRef" label-width="80px">
        <el-form-item label="原密码" prop="oldPwd">
          <el-input v-model="pwdForm.oldPwd" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="newPwd">
          <el-input v-model="pwdForm.newPwd" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showChangePwd = false">取消</el-button>
        <el-button type="primary" @click="changePwd">确定</el-button>
      </template>
    </el-dialog>

    <!-- 注销确认弹窗 -->
    <el-dialog
      v-model="showLogoutConfirm"
      title="确认注销"
      width="350px"
      :before-close="handleClose"
    >
      <span>确定要注销该用户吗？此操作将删除数据库中的所有相关信息，且无法恢复！</span>
      <template #footer>
        <el-button @click="showLogoutConfirm = false">取消</el-button>
        <el-button type="danger" @click="logout">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

const user = ref({
  username: 'book_user',
  email: 'user@example.com'
})

const showChangePwd = ref(false)
const pwdFormRef = ref(null)
const pwdForm = ref({
  oldPwd: '',
  newPwd: ''
})
const pwdRules = {
  oldPwd: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  newPwd: [{ required: true, message: '请输入新密码', trigger: 'blur' }]
}

const showLogoutConfirm = ref(false)

function changePwd() {
  pwdFormRef.value.validate(valid => {
    if (valid) {
      ElMessage.success('密码修改成功！')
      showChangePwd.value = false
      pwdForm.value.oldPwd = ''
      pwdForm.value.newPwd = ''
    }
  })
}

function confirmLogout() {
  showLogoutConfirm.value = true
}

function handleClose() {
  showLogoutConfirm.value = false
}

function logout() {
  // 这里应调用后端API删除用户及相关数据
  // await api.deleteUser(user.value.id)
  ElMessage.success('注销成功，相关信息已删除！')
  showLogoutConfirm.value = false
  router.push('/login')
}

function goHome() {
  router.push('/home')
}
</script>

<style scoped>
.user-info-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 80vh;
  background: #f5f5f5;
}
.user-info-card {
  width: 400px;
  padding: 30px 20px;
}
.user-header {
  display: flex;
  align-items: center;
  gap: 20px;
}
.user-basic h2 {
  margin: 0;
}
.user-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}
</style>