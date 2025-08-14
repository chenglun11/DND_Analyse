import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/detail/:name/:filename?',
      name: 'detail',
      component: () => import('../views/DetailView.vue'),
    },
    {
      path: '/detail/:names',
      name: 'detail-multi',
      component: () => import('../views/DetailView.vue'),
    },

    {
      path: '/test',
      name: 'test',
      component: () => import('../views/TestView.vue'),
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/help',
      name: 'help',
      component: () => import('../views/HelpView.vue'),
    },
    // {
    //   path: '/analytics',
    //   name: 'analytics',
    //   component: () => import('../views/CorrelationView.vue'),
    // },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('../views/NotFoundView.vue'),
    },
  ],
})

// 添加路由守卫来处理404错误
router.beforeEach((to, from, next) => {
  // 检查路由是否存在
  if (to.matched.length === 0) {
    // 路由不存在，重定向到404页面
    next({ name: 'not-found' })
  } else {
    next()
  }
})

// 添加错误处理
router.onError((error) => {
  console.error('路由错误:', error)
  // 如果是404错误，重定向到404页面
  if (error.message.includes('404')) {
    router.push({ name: 'not-found' })
  }
})

export default router
