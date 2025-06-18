import { createRouter, createWebHistory } from 'vue-router'
import AAALogin from '../views/AAALogin.vue'
import AAAHome from '../views/AAAHome.vue'
import AAAOrderManagement from '../views/AAAOrderManagement.vue'
import AAABookManagement from '../views/AAABookManagement.vue'
import AAAComplaintManage from '../views/AAAComplaintManage.vue'
import UserLogin from '../views/UserLogin.vue'
import Register from '../views/Register.vue'
import Home from '../views/Home.vue'
import BookDetails from '../views/BookDetails.vue'
import UserInfo from '../views/UserInfo.vue'
import Cart from '../views/Cart.vue'
import Browse from '../views/Browse.vue'
import Favorite from '../views/Favorite.vue'
import CreatePost from '../views/CreatePost.vue'
import OrderList from '../views/OrderList.vue'
import OrderDetail from '../views/OrderDetail.vue'
import OrderEdit from '../views/OrderEdit.vue'
import PostDetail from '../views/PostDetail.vue'
import UserComplaint from '../views/UserComplaint.vue'

const routes = [
  { path: '/aaalogin', component: AAALogin },
  { path: '/aaahome', component: AAAHome },
  { path: '/aaaordermanagement', component: AAAOrderManagement },
  { path: '/aaabookmanagement', component: AAABookManagement },
  { path: '/aaacomplaintmanage', component: AAAComplaintManage },
  { path: '/userlogin', component: UserLogin },
  { path: '/register', component: Register },
  { path: '/home', component: Home },
  { path: '/book/:id', component: BookDetails },
  { path: '/user', component: UserInfo },
  { path: '/cart', component: Cart },
  { path: '/favorite', component: Favorite },
  { path: '/browse', component: Browse },
  { path: '/createpost', name: 'CreatePost', component: CreatePost },
  { path: '/orders', name: 'OrderList', component: OrderList },
  { path: '/orders/:order_id', name: 'OrderDetail', component: OrderDetail },
  { path: '/orders/:order_id/edit', name: 'OrderEdit', component: OrderEdit },
  {
    path: '/order/create',
    name: 'OrderCreate',
    component: () => import('../views/OrderCreate.vue')
  },
  { path: '/post/:post_id', name: 'PostDetail', component: PostDetail },
  { path: '/user/complaint', name: 'UserComplaint', component: UserComplaint },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router