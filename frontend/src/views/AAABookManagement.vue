<template>
  <div class="admin-book-management">
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
    <el-row :gutter="24">
      <!-- 标签管理区 -->
      <el-col :span="6">
        <el-card>
          <div class="section-title">标签管理</div>
          <el-form :model="newTag" :rules="tagRules" ref="tagFormRef" inline>
            <el-form-item prop="name">
              <el-input v-model="newTag.name" placeholder="新标签名" size="small" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" size="small" @click="createTag" :loading="tagLoading">添加</el-button>
            </el-form-item>
          </el-form>
          <el-table :data="pagedTags" size="small" style="margin-top:10px;">
            <el-table-column prop="tag_id" label="ID" width="50" />
            <el-table-column prop="name" label="标签名" />
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button size="small" @click="editTag(row)">编辑</el-button>
                <el-button size="small" type="danger" @click="deleteTag(row.tag_id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            v-model:current-page="tagPage"
            :page-size="tagPageSize"
            :total="allTags.length"
            layout="prev, pager, next"
            style="margin-top:12px; text-align:right;"
          />
          <!-- 编辑标签弹窗 -->
          <el-dialog v-model="editTagDialog" title="编辑标签" width="300px">
            <el-input v-model="editTagForm.name" placeholder="新标签名" />
            <template #footer>
              <el-button @click="editTagDialog = false">取消</el-button>
              <el-button type="primary" @click="submitEditTag">保存</el-button>
            </template>
          </el-dialog>
        </el-card>
      </el-col>

      <!-- 书籍管理区 -->
      <el-col :span="18">
        <el-card>
          <div class="section-title-bar">
            <span class="section-title">书籍管理</span>
            <el-button
              type="success"
              icon="el-icon-star-on"
              class="recommend-btn"
              @click="notifyNewBooks"
              :disabled="selectedBookIds.length === 0"
            >推荐图书</el-button>
          </div>
          <el-button type="primary" @click="showCreateBookDialog = true" style="margin-bottom:16px;">创建新书籍</el-button>
          <el-table
            :data="pagedBooks"
            :row-key="row => row.book_id"
            style="width:100%;"
            v-loading="bookLoading"
            @selection-change="handleSelectionChange"
            ref="bookTable"
          >
            <el-table-column type="selection" width="50" />
            <el-table-column prop="book_id" label="ID" width="60" />
            <el-table-column prop="title" label="书名" />
            <el-table-column prop="author" label="作者" width="120" />
            <el-table-column prop="isbn" label="ISBN" width="120" />
            <el-table-column prop="price" label="价格" width="80">
              <template #default="{ row }">￥{{ row.price }}</template>
            </el-table-column>
            <el-table-column prop="stock" label="库存" width="80" />
            <el-table-column label="操作" width="180">
              <template #default="{ row }">
                <el-button size="small" @click="viewBook(row)">详情</el-button>
                <el-button size="small" type="danger" @click="deleteBook(row.book_id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            v-model:current-page="bookPage"
            :page-size="bookPageSize"
            :total="allBooks.length"
            layout="prev, pager, next"
            style="margin-top:16px; text-align:right;"
          />
        </el-card>
      </el-col>
    </el-row>
    <!-- 推荐结果弹窗 -->
    <el-dialog v-model="showRecommendDialog" title="推荐结果" width="700px">
      <el-empty v-if="recommendList.length === 0" description="暂无推荐结果" />
      <el-empty v-else :description="recommendList.value" />
      <template #footer>
        <el-button @click="showRecommendDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 创建书籍弹窗 -->
    <el-dialog v-model="showCreateBookDialog" title="创建新书籍" width="500px">
      <el-form :model="newBook" :rules="bookRules" ref="bookFormRef" label-width="90px">
        <el-form-item label="书名" prop="title">
          <el-input v-model="newBook.title" />
        </el-form-item>
        <el-form-item label="作者" prop="author">
          <el-input v-model="newBook.author" />
        </el-form-item>
        <el-form-item label="ISBN" prop="isbn">
          <el-input v-model="newBook.isbn" />
        </el-form-item>
        <el-form-item label="出版社" prop="publisher">
          <el-input v-model="newBook.publisher" />
        </el-form-item>
        <el-form-item label="价格" prop="price">
          <el-input-number v-model="newBook.price" :min="0" :step="0.01" />
        </el-form-item>
        <el-form-item label="折扣" prop="discount">
          <el-input-number v-model="newBook.discount" :min="0" :max="1" :step="0.01" />
        </el-form-item>
        <el-form-item label="库存" prop="stock">
          <el-input-number v-model="newBook.stock" :min="0" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="newBook.description" type="textarea" />
        </el-form-item>
        <el-form-item label="图片URL" prop="image_url">
          <el-input v-model="newBook.image_url" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateBookDialog = false">取消</el-button>
        <el-button type="primary" :loading="bookCreateLoading" @click="createBook">创建</el-button>
      </template>
    </el-dialog>

    <!-- 书籍详情弹窗 -->
    <el-dialog v-model="showBookDetailDialog" :title="bookDetail.title || '书籍详情'" width="600px">
      <el-form :model="bookDetail" :rules="bookRules" ref="bookDetailFormRef" label-width="90px">
        <el-form-item label="书名" prop="title">
          <el-input v-model="bookDetail.title" />
        </el-form-item>
        <el-form-item label="作者" prop="author">
          <el-input v-model="bookDetail.author" />
        </el-form-item>
        <el-form-item label="ISBN" prop="isbn">
          <el-input v-model="bookDetail.isbn" />
        </el-form-item>
        <el-form-item label="出版社" prop="publisher">
          <el-input v-model="bookDetail.publisher" />
        </el-form-item>
        <el-form-item label="价格" prop="price">
          <el-input-number v-model="bookDetail.price" :min="0" :step="0.01" />
        </el-form-item>
        <el-form-item label="折扣" prop="discount">
          <el-input-number v-model="bookDetail.discount" :min="0" :max="1" :step="0.01" />
        </el-form-item>
        <el-form-item label="库存" prop="stock">
          <el-input-number v-model="bookDetail.stock" :min="0" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="bookDetail.description" type="textarea" />
        </el-form-item>
        <el-form-item label="图片URL" prop="image_url">
          <el-input v-model="bookDetail.image_url" />
        </el-form-item>
        <!-- 图书标签管理 -->
        <el-form-item label="标签">
          <el-select v-model="selectedTagId" placeholder="选择标签" style="width:200px;">
            <el-option v-for="tag in allTags" :key="tag.tag_id" :label="tag.name" :value="tag.tag_id" />
          </el-select>
          <el-button size="small" @click="addBookTag" :disabled="!selectedTagId">添加</el-button>
        </el-form-item>
        <el-form-item label="已关联标签">
          <el-tag
            v-for="tag in bookDetail.tags"
            :key="tag.tag_id"
            closable
            @close="removeBookTag(tag.tag_id)"
            style="margin-right:8px;"
          >{{ tag.name }}</el-tag>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBookDetailDialog = false">关闭</el-button>
        <el-button type="primary" :loading="bookUpdateLoading" @click="updateBook">保存修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const router = useRouter()
function goAdminHome() {
  router.push('/AAAHome') // 请确保路由名为 AAAHome
}

/* 标签管理相关 */
const allTags = ref([])
const tagLoading = ref(false)
const newTag = reactive({ name: '' })
const tagFormRef = ref(null)
const tagRules = { name: [{ required: true, message: '请输入标签名', trigger: 'blur' }] }
const editTagDialog = ref(false)
const editTagForm = reactive({ tag_id: null, name: '' })
const tagPage = ref(1)
const tagPageSize = 25

const pagedTags = computed(() => {
  const start = (tagPage.value - 1) * tagPageSize
  return allTags.value.slice(start, start + tagPageSize)
})

/* 书籍管理相关 */
const allBooks = ref([])
const bookLoading = ref(false)
const bookPage = ref(1)
const bookPageSize = ref(25)
const showCreateBookDialog = ref(false)
const showBookDetailDialog = ref(false)
const bookFormRef = ref(null)
const bookDetailFormRef = ref(null)
const bookCreateLoading = ref(false)
const bookUpdateLoading = ref(false)
const newBook = reactive({
  title: '', author: '', isbn: '', publisher: '', price: 0, discount: 1, stock: 0, description: '', image_url: ''
})
const bookDetail = reactive({
  book_id: null, title: '', author: '', isbn: '', publisher: '', price: 0, discount: 1, stock: 0, description: '', image_url: '', tags: []
})
const selectedTagId = ref(null)

const pagedBooks = computed(() => {
  const start = (bookPage.value - 1) * bookPageSize.value
  return allBooks.value.slice(start, start + bookPageSize.value)
})

/* 书籍表单校验 */
const bookRules = {
  title: [{ required: true, message: '请输入书名', trigger: 'blur' }],
  author: [{ required: true, message: '请输入作者', trigger: 'blur' }],
  isbn: [{ required: true, message: '请输入ISBN', trigger: 'blur' }],
  publisher: [{ required: true, message: '请输入出版社', trigger: 'blur' }],
  price: [{ required: true, type: 'number', message: '请输入价格', trigger: 'blur' }],
  discount: [{ required: true, type: 'number', message: '请输入折扣', trigger: 'blur' }],
  stock: [{ required: true, type: 'number', message: '请输入库存', trigger: 'blur' }],
  description: [{ required: true, message: '请输入描述', trigger: 'blur' }],
  image_url: [{ required: true, message: '请输入图片URL', trigger: 'blur' }]
}

/* 标签管理方法 */
async function fetchAllTags() {
  tagLoading.value = true
  try {
    const res = await axios.get('/api/tags/', { withCredentials: true })
    allTags.value = res.data.tags || res.data
  } catch (err) {
    allTags.value = []
  } finally {
    tagLoading.value = false
  }
}
async function createTag() {
  tagFormRef.value.validate(async (valid) => {
    if (!valid) return
    tagLoading.value = true
    try {
      await axios.post('/api/tags/', { name: newTag.name }, { withCredentials: true })
      ElMessage.success('标签创建成功')
      newTag.name = ''
      fetchAllTags()
    } catch (err) {
      ElMessage.error(err.response?.data?.error || '创建失败')
    } finally {
      tagLoading.value = false
    }
  })
}
function editTag(row) {
  editTagForm.tag_id = row.tag_id
  editTagForm.name = row.name
  editTagDialog.value = true
}
async function submitEditTag() {
  if (!editTagForm.name) {
    ElMessage.warning('请输入新标签名')
    return
  }
  try {
    await axios.put(`/api/tags/${editTagForm.tag_id}`, { name: editTagForm.name }, { withCredentials: true })
    ElMessage.success('修改成功')
    editTagDialog.value = false
    fetchAllTags()
  } catch (err) {
    ElMessage.error(err.response?.data?.error || '修改失败')
  }
}
async function deleteTag(tag_id) {
  try {
    await axios.delete(`/api/tags/${tag_id}`, { withCredentials: true })
    ElMessage.success('删除成功')
    fetchAllTags()
  } catch (err) {
    ElMessage.error(err.response?.data?.error || '删除失败')
  }
}

/* 书籍管理方法 */
async function fetchAllBooks() {
  bookLoading.value = true
  try {
    const res = await axios.get('/api/books/', { withCredentials: true })
    allBooks.value = res.data.books || res.data
  } catch (err) {
    allBooks.value = []
  } finally {
    bookLoading.value = false
  }
}
async function createBook() {
  bookFormRef.value.validate(async (valid) => {
    if (!valid) return
    bookCreateLoading.value = true
    try {
      await axios.post('/api/books/', newBook, { withCredentials: true })
      ElMessage.success('书籍创建成功')
      showCreateBookDialog.value = false
      fetchAllBooks()
      // 重置表单
      Object.assign(newBook, { title: '', author: '', isbn: '', publisher: '', price: 0, discount: 1, stock: 0, description: '', image_url: '' })
    } catch (err) {
      ElMessage.error(err.response?.data?.error || '创建失败')
    } finally {
      bookCreateLoading.value = false
    }
  })
}
function viewBook(row) {
  Object.assign(bookDetail, row)
  // 获取书籍标签
  fetchBookTags(row.book_id)
  showBookDetailDialog.value = true
}
async function updateBook() {
  bookUpdateLoading.value = true
  try {
    const payload = { ...bookDetail }
    delete payload.book_id
    delete payload.tags
    await axios.put(`/api/books/${bookDetail.book_id}`, payload, { withCredentials: true })
    ElMessage.success('修改成功')
    showBookDetailDialog.value = false
    fetchAllBooks()
  } catch (err) {
    ElMessage.error(err.response?.data?.error || '修改失败')
  } finally {
    bookUpdateLoading.value = false
  }
}
async function deleteBook(book_id) {
  try {
    await axios.delete(`/api/books/${book_id}`, { withCredentials: true })
    ElMessage.success('删除成功')
    fetchAllBooks()
  } catch (err) {
    ElMessage.error(err.response?.data?.error || '删除失败')
  }
}

/* 图书标签关联管理 */
async function fetchBookTags(book_id) {
  try {
    const res = await axios.get(`/api/books/${book_id}/tags`, { withCredentials: true })
    bookDetail.tags = res.data
  } catch {
    bookDetail.tags = []
  }
}
async function addBookTag() {
  if (!selectedTagId.value) return
  try {
    await axios.post('/api/booktags/', { book_id: bookDetail.book_id, tag_id: selectedTagId.value }, { withCredentials: true })
    ElMessage.success('标签关联成功')
    fetchBookTags(bookDetail.book_id)
  } catch (err) {
    ElMessage.error(err.response?.data?.error || '关联失败')
  }
}
async function removeBookTag(tag_id) {
  try {
    await axios.delete('/api/booktags/', {
      data: { book_id: bookDetail.book_id, tag_id },
      withCredentials: true
    })
    ElMessage.success('标签已移除')
    fetchBookTags(bookDetail.book_id)
  } catch (err) {
    ElMessage.error(err.response?.data?.error || '移除失败')
  }
}

onMounted(() => {
  fetchAllTags()
  fetchAllBooks()
})

/* 多选相关，分页记忆 */
const selectedBookIds = ref([])
const bookTable = ref(null)
function handleSelectionChange(selection) {
  const currentPageIds = pagedBooks.value.map(b => b.book_id)
  // 先移除当前页的所有id
  selectedBookIds.value = selectedBookIds.value.filter(id => !currentPageIds.includes(id))
  // 再合并新选中的id，并去重
  const newIds = selection.map(item => item.book_id)
  selectedBookIds.value = Array.from(new Set([...selectedBookIds.value, ...newIds]))
}

// 分页切换时同步高亮
function syncSelection() {
  nextTick(() => {
    if (!bookTable.value) return
    bookTable.value.clearSelection()
    pagedBooks.value.forEach(row => {
      // 类型一致很重要
      if (selectedBookIds.value.includes(row.book_id)) {
        bookTable.value.toggleRowSelection(row, true)
      }
    })
  })
}
watch(pagedBooks, syncSelection, { immediate: true })

/* 推荐图书功能 */
const showRecommendDialog = ref(false)
const recommendList = ref([])

async function notifyNewBooks() {
  if (selectedBookIds.value.length === 0) {
    ElMessage.warning('请先勾选要推荐的图书')
    return
  }
  try {
    // 传递book_ids给后端
    const res = await axios.post('/api/notify/new_book', { book_ids: selectedBookIds.value }, { withCredentials: true })
    ElMessage.success(res.data.message || '推荐成功')
    showRecommendDialog.value = false
  } catch (err) {
    ElMessage.error(err.response?.data?.error || '推荐失败')
    recommendList.value = []
    showRecommendDialog.value = true
  }
}
</script>

<style scoped>
.back-admin-btn {
  margin-bottom: 12px;
}
.section-title-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.section-title {
  font-size: 20px;
  font-weight: bold;
  color: #409eff;
}
.recommend-btn {
  margin-left: auto;
}
</style>