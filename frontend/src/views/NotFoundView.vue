<template>
  <div class="not-found">
    <div class="not-found-content">
      <div class="error-code">404</div>
      <h1>页面未找到</h1>
      <p>抱歉，您访问的页面不存在或已被移除。</p>
      <div class="actions">
        <router-link to="/" class="home-btn">返回首页</router-link>
        <button @click="goBack" class="back-btn">返回上一页</button>
      </div>
      <div class="suggestions">
        <h3>您可能想要访问：</h3>
        <ul>
          <li><router-link to="/">首页</router-link></li>
          <li><router-link to="/about">关于我们</router-link></li>
          <li><router-link to="/help">帮助文档</router-link></li>
          <li><router-link to="/test">测试页面</router-link></li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    router.push('/')
  }
}
</script>

<style scoped>
.not-found {
  min-height: calc(100vh - 80px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: var(--color-background);
}

.not-found-content {
  max-width: 600px;
  text-align: center;
  background: white;
  padding: 60px 40px;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.error-code {
  font-size: 8rem;
  font-weight: bold;
  color: #e53e3e;
  margin-bottom: 20px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

.not-found-content h1 {
  font-size: 2.5rem;
  color: #333;
  margin-bottom: 15px;
}

.not-found-content p {
  font-size: 1.2rem;
  color: #666;
  margin-bottom: 40px;
  line-height: 1.6;
}

.actions {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-bottom: 40px;
}

.home-btn,
.back-btn {
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 1rem;
  text-decoration: none;
  transition: all 0.3s ease;
  cursor: pointer;
  border: none;
}

.home-btn {
  background: #3182ce;
  color: white;
}

.home-btn:hover {
  background: #2c5aa0;
  transform: translateY(-2px);
}

.back-btn {
  background: #718096;
  color: white;
}

.back-btn:hover {
  background: #4a5568;
  transform: translateY(-2px);
}

.suggestions {
  text-align: left;
  max-width: 400px;
  margin: 0 auto;
}

.suggestions h3 {
  color: #333;
  margin-bottom: 15px;
  font-size: 1.2rem;
}

.suggestions ul {
  list-style: none;
  padding: 0;
}

.suggestions li {
  margin-bottom: 10px;
}

.suggestions a {
  color: #3182ce;
  text-decoration: none;
  font-size: 1rem;
  transition: color 0.3s ease;
}

.suggestions a:hover {
  color: #2c5aa0;
  text-decoration: underline;
}

@media (max-width: 768px) {
  .not-found-content {
    padding: 40px 20px;
  }
  
  .error-code {
    font-size: 6rem;
  }
  
  .not-found-content h1 {
    font-size: 2rem;
  }
  
  .actions {
    flex-direction: column;
    gap: 15px;
  }
  
  .home-btn,
  .back-btn {
    width: 100%;
  }
}
</style> 