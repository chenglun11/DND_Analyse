<script setup lang="ts">
import { RouterView, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import LanguageSwitcher from './components/LanguageSwitcher.vue'
import { onMounted } from 'vue'

const router = useRouter()
const { t } = useI18n()

// 更新页头功能，链接到新页面
const goToAbout = () => {
  router.push('/about')
}

const goToHelp = () => {
  router.push('/help')
}

// 初始化语言设置
onMounted(() => {
  const savedLanguage = localStorage.getItem('preferred-language')
  if (savedLanguage) {
    // 这里需要访问i18n实例来设置语言
    // 由于在setup中无法直接访问，我们将在组件中处理
  }
})
</script>

<template>
  <div id="app">
    <!-- 全局页头 -->
    <header class="global-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="app-title">{{ t('app.title') }}</h1>
          <p class="app-subtitle">{{ t('app.subtitle') }}</p>
        </div>
        <div class="header-right">
          <nav class="nav-menu">
            <router-link to="/" class="nav-link">{{ t('nav.home') }}</router-link>
            <router-link to="/test" class="nav-link">{{ t('nav.test') }}</router-link>
          </nav>
          <LanguageSwitcher />
          <div class="header-actions">
            <button class="action-btn" @click="goToAbout">{{ t('nav.about') }}</button>
            <button class="action-btn" @click="goToHelp">{{ t('nav.help') }}</button>
          </div>
        </div>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="main-content">
      <RouterView />
    </main>

    <!-- 页脚 -->
    <footer class="global-footer">
      <div class="footer-content">
        <div class="footer-section">
          <h3>Dungeon Analyzer</h3>
          <p>专业的D&D地下城质量评估工具</p>
          <div class="footer-links">
            <a href="#" class="footer-link">使用指南</a>
            <a href="#" class="footer-link">API文档</a>
            <a href="#" class="footer-link">更新日志</a>
          </div>
        </div>
        
        <div class="footer-section">
          <h4>功能特性</h4>
          <ul class="footer-list">
            <li>多格式支持</li>
            <li>质量评估</li>
            <li>可视化分析</li>
            <li>批量处理</li>
          </ul>
        </div>
        
        <div class="footer-section">
          <h4>技术支持</h4>
          <ul class="footer-list">
            <li>问题反馈</li>
            <li>功能建议</li>
            <li>Bug报告</li>
            <li>联系我们</li>
          </ul>
        </div>
        
        <div class="footer-section">
          <h4>版本信息</h4>
          <p>当前版本: v1.0.0</p>
          <p>最后更新: 2024年12月</p>
          <div class="footer-social">
            <span class="social-icon">📧</span>
            <span class="social-icon">🐙</span>
            <span class="social-icon">💬</span>
          </div>
        </div>
      </div>
      
      <div class="footer-bottom">
        <p>&copy; 2024 Dungeon Analyzer. 保留所有权利。</p>
        <p>专为D&D地下城设计师打造</p>
      </div>
    </footer>
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
  background: var(--color-background);
}

#app {
  min-height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  background: var(--color-background);
}

/* 全局页头样式 */
.global-header {
  background: #4a4a4a;
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
  background: var(--color-background);
}

/* 页脚样式 */
.global-footer {
  background: #2d3748;
  color: white;
  padding: 40px 20px 20px;
  margin-top: auto;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 40px;
  margin-bottom: 30px;
}

.footer-section h3 {
  font-size: 1.5rem;
  margin-bottom: 15px;
  color: #e2e8f0;
}

.footer-section h4 {
  font-size: 1.2rem;
  margin-bottom: 15px;
  color: #e2e8f0;
}

.footer-section p {
  color: #a0aec0;
  line-height: 1.6;
  margin-bottom: 10px;
}

.footer-links {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.footer-link {
  color: #a0aec0;
  text-decoration: none;
  transition: color 0.3s ease;
}

.footer-link:hover {
  color: #e2e8f0;
}

.footer-list {
  list-style: none;
  padding: 0;
}

.footer-list li {
  color: #a0aec0;
  margin-bottom: 8px;
  transition: color 0.3s ease;
}

.footer-list li:hover {
  color: #e2e8f0;
}

.footer-social {
  display: flex;
  gap: 15px;
  margin-top: 15px;
}

.social-icon {
  font-size: 1.5rem;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.social-icon:hover {
  transform: scale(1.2);
}

.footer-bottom {
  max-width: 1400px;
  margin: 0 auto;
  padding-top: 20px;
  border-top: 1px solid #4a5568;
  text-align: center;
}

.footer-bottom p {
  color: #718096;
  margin: 5px 0;
  font-size: 0.9rem;
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
  
  .global-footer {
    padding: 30px 15px 15px;
  }
  
  .footer-content {
    grid-template-columns: 1fr;
    gap: 30px;
  }
  
  .footer-section {
    text-align: center;
  }
  
  .footer-social {
    justify-content: center;
  }
}
</style>
