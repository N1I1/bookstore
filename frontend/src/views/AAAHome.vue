<!-- 管理员首页 -->
 <template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 p-4">
    <div class="w-full max-w-md">
      <div class="text-center mb-10">
        <h1 class="text-3xl font-bold text-gray-800 mb-2">图书管理系统</h1>
        <p class="text-gray-600">管理员控制面板</p>
      </div>
      
      <div class="space-y-6">
        <!-- 订单管理按钮 -->
        <router-link to="/aaaordermanagement">
          <button class="w-full flex items-center justify-center py-4 px-6 bg-blue-600 hover:bg-blue-700 rounded-lg shadow text-white font-medium text-lg transition-all duration-200 transform hover:scale-[1.02]">
            <i class="fas fa-receipt mr-3 text-xl"></i>
            订单管理
          </button>
        </router-link>
        
        <!-- 书籍管理按钮 -->
        <router-link to="/aaabookmanagement">
          <button class="w-full flex items-center justify-center py-4 px-6 bg-green-600 hover:bg-green-700 rounded-lg shadow text-white font-medium text-lg transition-all duration-200 transform hover:scale-[1.02]">
            <i class="fas fa-book mr-3 text-xl"></i>
            书籍管理
          </button>
        </router-link>
      </div>
      
      <div class="mt-12 text-center text-gray-500 text-sm">
        <p>当前登录：管理员账号</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AAAHome',
  // 组件逻辑可以在这里添加
}
</script>

<style scoped>
/* 添加简单的动画效果 */
button {
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

button:hover {
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}
</style>