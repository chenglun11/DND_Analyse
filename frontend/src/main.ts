import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import i18n from './i18n'

const app = createApp(App)

// 添加全局错误处理
app.config.errorHandler = (err, instance, info) => {
  console.error('Vue错误:', err)
  console.error('错误信息:', info)
  
  // 如果是路由相关错误，重定向到404页面
  if (err && typeof err === 'object' && 'message' in err) {
    const errorMessage = err.message as string
    if (errorMessage.includes('404') || errorMessage.includes('not found')) {
      router.push({ name: 'not-found' })
    }
  }
}

app.use(createPinia())
app.use(router)
app.use(i18n)

app.mount('#app')
