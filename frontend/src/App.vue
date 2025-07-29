<script setup lang="ts">
import { RouterView, useRouter } from 'vue-router'

const router = useRouter()

// 更新页头功能，链接到新页面
const goToAbout = () => {
  router.push('/about')
}

const goToHelp = () => {
  router.push('/help')
}
</script>

<template>
  <div id="app">
    <!-- 全局页头 -->
    <header class="global-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="app-title">地下城分析器</h1>
          <p class="app-subtitle">专业的D&D地下城质量评估工具</p>
        </div>
        <div class="header-right">
          <nav class="nav-menu">
            <router-link to="/" class="nav-link">首页</router-link>
            <router-link to="/test" class="nav-link">测试</router-link>
          </nav>
          <div class="header-actions">
            <button class="action-btn" @click="goToAbout">关于</button>
            <button class="action-btn" @click="goToHelp">帮助</button>
          </div>
        </div>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  width: 100%;
  /* 移除 overflow: hidden，允许页面滚动 */
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  line-height: 1.6;
  color: #333;
}

#app {
  min-height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
}

/* 全局页头样式 */
.global-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 15px 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.app-title {
  font-size: 1.8rem;
  font-weight: bold;
  margin: 0;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.app-subtitle {
  font-size: 0.9rem;
  opacity: 0.9;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.nav-menu {
  display: flex;
  gap: 20px;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 6px;
  transition: background 0.3s ease;
  font-weight: 500;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.2);
}

.nav-link.router-link-active {
  background: rgba(255, 255, 255, 0.3);
}

.header-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.3s ease;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .global-header {
    padding: 10px 15px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 15px;
  }
  
  .header-right {
    flex-direction: column;
    gap: 15px;
  }
  
  .nav-menu {
    gap: 10px;
  }
  
  .nav-link {
    padding: 6px 12px;
    font-size: 0.9rem;
  }
  
  .app-title {
    font-size: 1.5rem;
  }
  
  .app-subtitle {
    font-size: 0.8rem;
  }
}
</style>
