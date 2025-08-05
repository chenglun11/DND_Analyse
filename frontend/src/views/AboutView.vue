<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { computed } from 'vue'

const router = useRouter()
const { t } = useI18n()

const goBack = () => {
  router.push('/')
}

const features = [
  {
    icon: '🎯',
    title: t('about.features.0.title'),
    description: t('about.features.0.description')
  },
  {
    icon: '📊',
    title: t('about.features.1.title'),
    description: t('about.features.1.description')
  },
  {
    icon: '🔄',
    title: t('about.features.2.title'),
    description: t('about.features.2.description')
  },
  {
    icon: '⚡',
    title: t('about.features.3.title'),
    description: t('about.features.3.description')
  },
  {
    icon: '📈',
    title: t('about.features.4.title'),
    description: t('about.features.4.description')
  },
  {
    icon: '💾',
    title: t('about.features.5.title'),
    description: t('about.features.5.description')
  }
]

const qualityMetrics = [
  { name: t('about.qualityMetrics.0.name'), description: t('about.qualityMetrics.0.description') },
  { name: t('about.qualityMetrics.1.name'), description: t('about.qualityMetrics.1.description') },
  { name: t('about.qualityMetrics.2.name'), description: t('about.qualityMetrics.2.description') },
  { name: t('about.qualityMetrics.3.name'), description: t('about.qualityMetrics.3.description') },
  { name: t('about.qualityMetrics.4.name'), description: t('about.qualityMetrics.4.description') },
  { name: t('about.qualityMetrics.5.name'), description: t('about.qualityMetrics.5.description') },
  { name: t('about.qualityMetrics.6.name'), description: t('about.qualityMetrics.6.description') },
  { name: t('about.qualityMetrics.7.name'), description: t('about.qualityMetrics.7.description') },
  { name: t('about.qualityMetrics.8.name'), description: t('about.qualityMetrics.8.description') }
]

const techStack = computed(() => [
  { 
    category: t('about.techStackCategories.0'), 
    items: ['Vue 3', 'TypeScript', 'Vite', 'Tailwind CSS']
  },
  { 
    category: t('about.techStackCategories.1'), 
    items: ['Python', 'Flask', 'NumPy', 'Pandas']
  },
  { 
    category: t('about.techStackCategories.2'), 
    items: ['A* Path Algorithm', 'BFS Search', 'Graph Theory Analysis']
  },
  { 
    category: t('about.techStackCategories.3'), 
    items: ['Canvas API', 'SVG', 'Chart.js']
  }
])
</script>

<template>
  <div class="about-page">
    <div class="about-header">
      <button class="back-btn" @click="goBack">
        {{ t('about.backButton') }}
      </button>
      <h1>{{ t('about.title') }}</h1>
      <p class="subtitle">{{ t('about.subtitle') }}</p>
    </div>

    <div class="about-content">
      <!-- 项目介绍 -->
      <section class="section">
        <h2>{{ t('about.intro.title') }}</h2>
        <div class="intro-card">
          <p>
            {{ t('about.intro.description1') }}
          </p>
          <p>
            {{ t('about.intro.description2') }}
          </p>
        </div>
      </section>

      <!-- 核心功能 -->
      <section class="section">
        <h2>🚀 {{ t('common.coreFeatures') }}</h2>
        <div class="features-grid">
          <div v-for="feature in features" :key="feature.title" class="feature-card">
            <div class="feature-icon">{{ feature.icon }}</div>
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
          </div>
        </div>
      </section>

      <!-- 质量评估指标 -->
      <section class="section">
        <h2>📊 {{ t('about.qualityMetricsTitle') }}</h2>
        <div class="metrics-grid">
          <div v-for="metric in qualityMetrics" :key="metric.name" class="metric-card">
            <h4>{{ metric.name }}</h4>
            <p>{{ metric.description }}</p>
          </div>
        </div>
      </section>

      <!-- 技术栈 -->
      <section class="section">
        <h2>🛠️ {{ t('about.techStackTitle') }}</h2>
        <div class="tech-grid">
          <div v-for="tech in techStack" :key="tech.category" class="tech-category">
            <h4>{{ tech.category }}</h4>
            <div class="tech-items">
              <span v-for="item in tech.items" :key="item" class="tech-item">
                {{ item }}
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- 版本信息 -->
      <section class="section">
        <h2>📋 {{ t('about.versionInfoTitle') }}</h2>
        <div class="version-info">
          <div class="info-item">
            <strong>{{ t('about.versionInfo.currentVersion') }}：</strong>
            <span>v1.0.3</span>
          </div>
          <div class="info-item">
            <strong>{{ t('about.versionInfo.lastUpdate') }}：</strong>
            <span>{{ t('about.versionInfo.lastUpdateDate') }}</span>
          </div>
          <div class="info-item">
            <strong>{{ t('about.versionInfo.developmentTeam') }}：</strong>
            <span>{{ t('about.versionInfo.teamName') }}</span>
          </div>
          <div class="info-item">
            <strong>{{ t('about.versionInfo.license') }}：</strong>
            <span>MIT License</span>
          </div>
        </div>
      </section>

      <!-- 快速操作 -->
      <section class="section">
        <h2>⚡ {{ t('about.quickActionsTitle') }}</h2>
        <div class="quick-actions">
          <button class="action-btn primary" @click="router.push('/')">
            {{ t('about.quickActions.startAnalysis') }}
          </button>
          <button class="action-btn" @click="router.push('/help')">
            {{ t('about.quickActions.viewHelp') }}
          </button>
          <button class="action-btn" @click="router.push('/test')">
            {{ t('about.quickActions.featureTest') }}
          </button>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.about-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background: var(--color-background);
  min-height: calc(100vh - 80px);
}

.about-header {
  text-align: center;
  margin-bottom: 40px;
  position: relative;
}

.back-btn {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  background: #2d3748;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.3s ease;
}

.back-btn:hover {
  background: #1a202c;
}

.about-header h1 {
  font-size: 2.5rem;
  color: #333;
  margin-bottom: 10px;
}

.subtitle {
  font-size: 1.2rem;
  color: #666;
}

.about-content {
  display: flex;
  flex-direction: column;
  gap: 40px;
}

.section {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.section h2 {
  font-size: 1.8rem;
  color: #333;
  margin-bottom: 20px;
  border-bottom: 2px solid #667eea;
  padding-bottom: 10px;
}

.intro-card {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.intro-card p {
  margin-bottom: 15px;
  line-height: 1.6;
  color: #555;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.feature-card {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  transition: transform 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-icon {
  font-size: 2.5rem;
  margin-bottom: 15px;
}

.feature-card h3 {
  color: #333;
  margin-bottom: 10px;
}

.feature-card p {
  color: #666;
  line-height: 1.5;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.metric-card {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  border-left: 3px solid #28a745;
}

.metric-card h4 {
  color: #333;
  margin-bottom: 8px;
}

.metric-card p {
  color: #666;
  font-size: 0.9rem;
  line-height: 1.4;
}

.tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.tech-category {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}

.tech-category h4 {
  color: #333;
  margin-bottom: 15px;
  font-size: 1.1rem;
}

.tech-items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.tech-item {
  background: #4a5568;
  color: white;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
}

.version-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 6px;
}

.info-item strong {
  color: #333;
}

.quick-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
}

.action-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: #6c757d;
  color: white;
}

.action-btn:hover {
  transform: translateY(-2px);
}

.action-btn.primary {
  background: #4a5568;
}

.action-btn.primary:hover {
  background: #2d3748;
}

@media (max-width: 768px) {
  .about-page {
    padding: 15px;
  }
  
  .about-header h1 {
    font-size: 2rem;
  }
  
  .back-btn {
    position: static;
    transform: none;
    margin-bottom: 20px;
    padding: 10px 20px;
    font-size: 16px;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .tech-grid {
    grid-template-columns: 1fr;
  }
  
  .quick-actions {
    flex-direction: column;
  }
}
</style> 