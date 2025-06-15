import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Home from '../views/Home.vue'
import BookDetails from '../views/BookDetails.vue'
import UserInfo from '../views/UserInfo.vue'

const routes = [
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/home', component: Home },
  { path: '/book/:id', component: BookDetails },
  { path: '/user', component: UserInfo },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router