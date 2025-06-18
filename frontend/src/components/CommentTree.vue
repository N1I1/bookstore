<template>
  <div>
    <div
      v-for="comment in comments"
      :key="comment.comment_id"
      class="comment-item"
    >
      <div class="comment-header">
        <b>{{ comment.username }}</b>
        <span class="comment-time">（{{ formatTime(comment.comment_time) }}）</span>
      </div>
      <div class="comment-body">
        <template v-if="editingId === comment.comment_id">
          <el-input
            v-model="editContent"
            size="small"
            style="width: 400px; margin-bottom: 4px;"
          />
          <el-button
            size="small"
            type="success"
            :loading="editLoading"
            @click="submitEdit(comment)"
          >保存</el-button>
          <el-button
            size="small"
            @click="editingId = null"
          >取消</el-button>
        </template>
        <template v-else>
          {{ comment.content }}
        </template>
      </div>
      <div class="comment-actions">
        <el-button size="small" link @click="showReply(comment.comment_id)">回复</el-button>
        <el-button
          v-if="isMine(comment)"
          size="small"
          link
          @click="showEdit(comment)"
        >编辑</el-button>
        <el-button
          v-if="isMine(comment)"
          size="small"
          link
          type="danger"
          @click="deleteComment(comment)"
        >删除</el-button>
      </div>
      <div v-if="replyToId === comment.comment_id" class="reply-box">
        <el-input
          v-model="replyContent"
          size="small"
          style="width: 400px; margin-bottom: 4px;"
          placeholder="回复内容..."
        />
        <el-button
          size="small"
          type="primary"
          :loading="replyLoading"
          @click="submitReply(comment.comment_id)"
        >提交</el-button>
        <el-button
          size="small"
          @click="replyToId = null"
        >取消</el-button>
      </div>
      <!-- 递归渲染子评论 -->
      <div v-if="comment.replies && comment.replies.length" class="comment-replies">
        <CommentTree
          :comments="comment.replies"
          :post-id="postId"
          @refresh="emitRefresh"
          :current-user-id="currentUserId"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const props = defineProps({
  comments: { type: Array, required: true },
  postId: { type: Number, required: true },
  currentUserId: { type: [Number, String], default: null }
})
const emit = defineEmits(['refresh'])

const replyContent = ref('')
const replyToId = ref(null)
const replyLoading = ref(false)
const editingId = ref(null)
const editContent = ref('')
const editLoading = ref(false)

function isMine(comment) {
  // 确保后端返回的评论数据中包含 user_id
  return props.currentUserId && comment.user_id == props.currentUserId
}

function showReply(commentId) {
  replyToId.value = commentId
  replyContent.value = ''
}

async function submitReply(parentId) {
  if (!replyContent.value.trim()) {
    ElMessage.warning('请输入回复内容')
    return
  }
  
  replyLoading.value = true
  try {
    await axios.post('/api/comments/', {
      post_id: props.postId,
      content: replyContent.value,
      parent_comment_id: parentId
    }, {
      withCredentials: true // 添加认证信息
    })
    
    ElMessage.success('回复成功')
    replyContent.value = ''
    replyToId.value = null
    emit('refresh')
  } catch (err) {
    console.error('回复失败:', err)
    
    // 更详细的错误处理
    let errorMsg = '回复失败'
    if (err.response?.data?.error) {
      errorMsg += `: ${err.response.data.error}`
    } else if (err.response?.status === 401) {
      errorMsg = '请先登录'
    }
    
    ElMessage.error(errorMsg)
  } finally {
    replyLoading.value = false
  }
}

function showEdit(comment) {
  editingId.value = comment.comment_id
  editContent.value = comment.content
}

async function submitEdit(comment) {
  if (!editContent.value.trim()) {
    ElMessage.warning('内容不能为空')
    return
  }
  
  editLoading.value = true
  try {
    await axios.put(`/api/comments/${comment.comment_id}`, {
      content: editContent.value
    }, {
      withCredentials: true // 添加认证信息
    })
    
    ElMessage.success('修改成功')
    editingId.value = null
    emit('refresh')
  } catch (err) {
    console.error('修改失败:', err)
    
    // 更详细的错误处理
    let errorMsg = '修改失败'
    if (err.response?.data?.error) {
      errorMsg += `: ${err.response.data.error}`
    } else if (err.response?.status === 401) {
      errorMsg = '请先登录'
    } else if (err.response?.status === 403) {
      errorMsg = '无权修改此评论'
    }
    
    ElMessage.error(errorMsg)
  } finally {
    editLoading.value = false
  }
}

async function deleteComment(comment) {
  try {
    await axios.delete(`/api/comments/${comment.comment_id}`, {
      withCredentials: true // 添加认证信息
    })
    
    ElMessage.success('删除成功')
    emit('refresh')
  } catch (err) {
    console.error('删除失败:', err)
    
    // 更详细的错误处理
    let errorMsg = '删除失败'
    if (err.response?.data?.error) {
      errorMsg += `: ${err.response.data.error}`
    } else if (err.response?.status === 401) {
      errorMsg = '请先登录'
    } else if (err.response?.status === 403) {
      errorMsg = '无权删除此评论'
    }
    
    ElMessage.error(errorMsg)
  }
}

function formatTime(timeStr) {
  if (!timeStr) return ''
  
  // 更好的时间格式化
  try {
    const date = new Date(timeStr)
    if (isNaN(date.getTime())) throw new Error('Invalid date')
    
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    // 如果无法解析，返回原始格式
    return timeStr.replace('T', ' ').slice(0, 16)
  }
}

function emitRefresh() {
  emit('refresh')
}
</script>

<style scoped>
.comment-item {
  border-bottom: 1px solid #f0f0f0;
  padding: 12px 0 8px 0;
  margin-left: 0;
}
.comment-header {
  font-size: 14px;
  color: #409eff;
}
.comment-time {
  color: #aaa;
  font-size: 12px;
  margin-left: 8px;
}
.comment-body {
  margin: 4px 0 4px 0;
  font-size: 15px;
  color: #333;
  word-break: break-word; /* 添加换行处理 */
}
.comment-actions {
  margin-bottom: 4px;
}
.comment-replies {
  margin-left: 32px;
  margin-top: 4px;
  border-left: 2px solid #eee; /* 添加视觉层次 */
  padding-left: 12px;
}
.reply-box {
  margin: 8px 0 8px 0;
  background: #f9f9f9;
  padding: 8px;
  border-radius: 4px;
}
</style>