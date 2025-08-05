<template>
  <div class="test-view">
    <div class="container">
      <h1>{{ t('app.title') }}</h1>
      <p>{{ t('app.subtitle') }}</p>
      
      <div class="test-section">
        <h2>语言测试</h2>
        <p>当前语言: {{ currentLocale }}</p>
        
        <div class="test-items">
          <div class="test-item">
            <h3>通用文本</h3>
            <p>{{ t('common.loading') }}</p>
            <p>{{ t('common.error') }}</p>
            <p>{{ t('common.success') }}</p>
          </div>
          
          <div class="test-item">
            <h3>导航文本</h3>
            <p>{{ t('nav.home') }}</p>
            <p>{{ t('nav.about') }}</p>
            <p>{{ t('nav.help') }}</p>
          </div>
          
          <div class="test-item">
            <h3>首页文本</h3>
            <p>{{ t('home.uploadTitle') }}</p>
            <p>{{ t('home.startAnalysis') }}</p>
            <p>{{ t('home.analysisResults') }}</p>
          </div>
          
          <div class="test-item">
            <h3>详情页文本</h3>
            <p>{{ t('detail.backButton') }}</p>
            <p>{{ t('detail.analysisResults') }}</p>
            <p>{{ t('detail.overallScore') }}</p>
          </div>
          
          <div class="test-item">
            <h3>指标名称</h3>
            <p>{{ t('metrics.accessibility') }}</p>
            <p>{{ t('metrics.geometric_balance') }}</p>
            <p>{{ t('metrics.loop_ratio') }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()

const currentLocale = computed(() => locale.value)
</script>

<style scoped>
.test-view {
  padding: 20px;
  background: var(--color-background);
  min-height: calc(100vh - 80px);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

h1 {
  color: #333;
  margin-bottom: 10px;
}

p {
  color: #666;
  margin-bottom: 20px;
}

.test-section {
  margin-top: 40px;
}

.test-section h2 {
  color: #333;
  margin-bottom: 20px;
  border-bottom: 2px solid #4a5568;
  padding-bottom: 10px;
}

.test-items {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.test-item {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 20px;
  border: 1px solid #e9ecef;
}

.test-item h3 {
  color: #333;
  margin-bottom: 15px;
  font-size: 1.1rem;
}

.test-item p {
  color: #555;
  margin-bottom: 8px;
  font-size: 0.9rem;
}

.current-locale {
  background: #4a5568;
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  display: inline-block;
  margin-bottom: 20px;
  font-weight: 500;
}
</style> 