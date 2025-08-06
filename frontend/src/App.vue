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
  color: #334155;
  background: #f8fafc;
}

#app {
  min-height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  background: #f8fafc;
  position: relative;
}

/* 全局页头样式 */
.global-header {
  background: #173753;  /* Prussian blue */
  color: white;
  padding: 15px 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 50;
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
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
  color: #6DAEDB;  /* Carolina blue */
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
  background: #f8fafc;
  min-height: calc(100vh - 120px); /* 减去header和footer的高度 */
}

/* 页脚样式 */
.global-footer {
  background: #173753;  /* Prussian blue - 与页头保持一致 */
  color: white;
  padding: 20px;
  margin-top: auto;
  position: sticky;
  bottom: 0;
  z-index: 40;
}

.footer-bottom {
  max-width: 1400px;
  margin: 0 auto;
}

.footer-bottom-content {
  display: flex;
  justify-content: center;
  align-items: center;
}

.footer-bottom-left p {
  color: #64748b;
  margin: 0;
  font-size: 0.9rem;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .header-content {
    gap: 15px;
  }
  
  .nav-menu {
    gap: 15px;
  }
  
  .app-title {
    font-size: 1.4rem;
  }
  
  .app-subtitle {
    font-size: 0.75rem;
  }
}

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

  .footer-bottom-content {
    flex-direction: column;
    gap: 10px;
  }
}
</style>
