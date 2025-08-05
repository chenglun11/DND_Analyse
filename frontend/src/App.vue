<script setup lang="ts">
import { RouterView, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import LanguageSwitcher from './components/LanguageSwitcher.vue'
import BaseButton from './components/BaseButton.vue'
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
          <div class="logo-section">
            <div class="logo-icon">🏰</div>
            <div class="logo-text">
              <h1 class="app-title">{{ t('app.title') }}</h1>
              <p class="app-subtitle">{{ t('app.subtitle') }}</p>
            </div>
          </div>
        </div>
        
        <div class="header-center">
          <nav class="nav-menu">
            <router-link to="/" class="nav-link" active-class="nav-link-active">
              {{ t('nav.home') }}
            </router-link>
            <router-link to="/test" class="nav-link" active-class="nav-link-active">
              {{ t('nav.test') }}
            </router-link>
          </nav>
        </div>
        
        <div class="header-right">
          <div class="header-actions">
            <BaseButton 
              variant="ghost" 
              size="sm" 
              @click="goToAbout"
              class="header-btn"
            >
              {{ t('nav.about') }}
            </BaseButton>
            <BaseButton 
              variant="ghost" 
              size="sm" 
              @click="goToHelp"
              class="header-btn"
            >
              {{ t('nav.help') }}
            </BaseButton>
          </div>
          <LanguageSwitcher />
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
        <div class="footer-section main-section">
          <div class="footer-logo">
            <div class="footer-logo-icon">🏰</div>
            <div class="footer-logo-text">
              <h3>Dungeon Analyzer</h3>
              <p>专业的D&D地下城质量评估工具</p>
            </div>
          </div>
        </div>
        
        <div class="footer-section">
          <h4 class="footer-section-title">功能特性</h4>
          <ul class="footer-list">
            <li>多格式支持</li>
            <li>质量评估</li>
            <li>可视化分析</li>
            <li>批量处理</li>
          </ul>
        </div>
        
        <div class="footer-section">
          <h4 class="footer-section-title">版本信息</h4>
          <div class="version-info">
            <div class="version-item">
              <span class="version-label">版本:</span>
              <span class="version-value">v1.0.0</span>
            </div>
            <div class="version-item">
              <span class="version-label">更新:</span>
              <span class="version-value">2024年12月</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="footer-bottom">
        <div class="footer-bottom-content">
          <div class="footer-bottom-left">
            <p>&copy; 2024 Dungeon Analyzer. 保留所有权利。</p>
          </div>
        </div>
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
  gap: 20px;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 5px;
  flex-shrink: 0;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  font-size: 2rem;
  color: #ffd700;
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.app-title {
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.app-subtitle {
  font-size: 0.8rem;
  opacity: 0.9;
  margin: 0;
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: flex-start;
}

.nav-menu {
  display: flex;
  gap: 20px;
  justify-content: flex-start;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 6px;
  transition: background 0.3s ease;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.2);
}

.nav-link-active {
  background: rgba(255, 255, 255, 0.3);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-shrink: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.header-btn {
  color: white !important;
  background: transparent !important;
  border: none !important;
  padding: 8px 16px !important;
  font-size: 0.9rem !important;
}

.header-btn:hover {
  background: rgba(255, 255, 255, 0.2) !important;
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

.footer-section.main-section {
  grid-column: span 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.footer-logo-icon {
  font-size: 2rem;
  color: #ffd700;
}

.footer-logo-text h3 {
  font-size: 1.3rem;
  margin-bottom: 5px;
  color: #e2e8f0;
}

.footer-logo-text p {
  font-size: 0.9rem;
  color: #a0aec0;
  margin-bottom: 10px;
}

.footer-description p {
  color: #a0aec0;
  line-height: 1.6;
  margin-bottom: 15px;
  max-width: 400px;
}

.footer-section h4 {
  font-size: 1.1rem;
  margin-bottom: 15px;
  color: #e2e8f0;
}

.footer-section-title {
  font-size: 1.1rem;
  margin-bottom: 15px;
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

.version-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.version-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.version-label {
  font-size: 0.9rem;
  color: #a0aec0;
}

.version-value {
  font-weight: bold;
  color: #e2e8f0;
}

.footer-bottom {
  max-width: 1400px;
  margin: 0 auto;
  padding-top: 20px;
  border-top: 1px solid #4a5568;
}

.footer-bottom-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.footer-bottom-left p {
  color: #718096;
  margin: 5px 0;
  font-size: 0.9rem;
}

.footer-bottom-right {
  display: flex;
  gap: 15px;
}

.footer-bottom-link {
  color: #a0aec0;
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.3s ease;
}

.footer-bottom-link:hover {
  color: #e2e8f0;
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
  
  .header-left, .header-center, .header-right {
    width: 100%;
    text-align: center;
  }

  .logo-section {
    justify-content: center;
  }
  
  .nav-menu {
    justify-content: center;
    gap: 10px;
  }
  
  .nav-link {
    padding: 6px 12px;
    font-size: 0.9rem;
  }
  
  .app-title {
    font-size: 1.3rem;
  }
  
  .app-subtitle {
    font-size: 0.7rem;
  }

  .header-actions {
    justify-content: center;
  }

  .header-btn {
    padding: 6px 12px !important;
    font-size: 0.8rem !important;
  }

  .footer-content {
    grid-template-columns: 1fr;
    gap: 30px;
  }

  .footer-section.main-section {
    grid-column: 1 / -1;
  }

  .footer-section {
    text-align: center;
  }

  .footer-bottom-content {
    flex-direction: column;
    gap: 10px;
  }

  .footer-bottom-right {
    flex-direction: column;
    gap: 10px;
  }
}
</style>
