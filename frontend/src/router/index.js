import { createRouter, createWebHistory } from 'vue-router'
import UserLogin from '../views/UserLogin.vue'
import Register from '../views/Register.vue'
import Home from '../views/Home.vue'
import BookDetails from '../views/BookDetails.vue'
import UserInfo from '../views/UserInfo.vue'
import Cart from '../views/Cart.vue'
import Browse from '../views/Browse.vue'
import Favorite from '../views/Favorite.vue'

const routes = [
  { path: '/userlogin', component: UserLogin },
  { path: '/register', component: Register },
  { path: '/home', component: Home },
  { path: '/book/:id', component: BookDetails },
  { path: '/user', component: UserInfo },
  { path: '/cart', component: Cart },
  { path: '/favorite', component: Favorite },
  { path: '/browse', component: Browse },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router