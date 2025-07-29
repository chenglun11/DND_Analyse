<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  router.push('/')
}

const features = [
  {
    icon: '🎯',
    title: '智能质量评估',
    description: '基于9个核心指标的地下城质量评估系统'
  },
  {
    icon: '📊',
    title: '可视化分析',
    description: '生成详细的可视化图表和路径分析'
  },
  {
    icon: '🔄',
    title: '多格式支持',
    description: '支持Watabou、Donjon、DungeonDraft等多种格式'
  },
  {
    icon: '⚡',
    title: '批量处理',
    description: '支持批量上传和分析多个地下城文件'
  },
  {
    icon: '📈',
    title: '详细报告',
    description: '生成包含改进建议的详细分析报告'
  },
  {
    icon: '💾',
    title: '结果导出',
    description: '支持导出分析结果和可视化图像'
  }
]

const qualityMetrics = [
  { name: '可达性评估', description: '评估地下城各区域的连通性和可达性' },
  { name: '美学平衡', description: '分析房间布局的美观性和平衡性' },
  { name: '环路比例', description: '计算地下城中的环路结构比例' },
  { name: '死胡同比例', description: '评估死胡同和无效路径的比例' },
  { name: '宝藏分布', description: '分析宝藏和战利品的分布合理性' },
  { name: '怪物分布', description: '评估怪物和敌人的分布策略' },
  { name: '关键路径长度', description: '分析主要路径的长度和复杂度' },
  { name: '度数方差', description: '评估房间连接度的分布情况' },
  { name: '空间推理', description: '分析空间布局的逻辑性和合理性' }
]

const techStack = [
  { category: '前端', items: ['Vue 3', 'TypeScript', 'Vite', 'Tailwind CSS'] },
  { category: '后端', items: ['Python', 'Flask', 'NumPy', 'Pandas'] },
  { category: '算法', items: ['A*路径算法', 'BFS搜索', '图论分析'] },
  { category: '可视化', items: ['Canvas API', 'SVG', 'Chart.js'] }
]
</script>

<template>
  <div class="about-page">
    <div class="about-header">
      <button class="back-btn" @click="goBack">
        ← 返回首页
      </button>
      <h1>关于地下城分析器</h1>
      <p class="subtitle">专业的D&D地下城质量评估工具</p>
    </div>

    <div class="about-content">
      <!-- 项目介绍 -->
      <section class="section">
        <h2>🎯 项目简介</h2>
        <div class="intro-card">
          <p>
            地下城分析器是一个专门为D&D（龙与地下城）游戏设计的智能工具，
            旨在帮助游戏设计师和地下城制作者创建高质量的地下城。
          </p>
          <p>
            通过先进的算法和9个核心评估指标，我们能够自动分析地下城的结构、
            布局和游戏性，提供详细的质量评估和改进建议。
          </p>
        </div>
      </section>

      <!-- 核心功能 -->
      <section class="section">
        <h2>🚀 核心功能</h2>
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
        <h2>📊 质量评估指标</h2>
        <div class="metrics-grid">
          <div v-for="metric in qualityMetrics" :key="metric.name" class="metric-card">
            <h4>{{ metric.name }}</h4>
            <p>{{ metric.description }}</p>
          </div>
        </div>
      </section>

      <!-- 技术栈 -->
      <section class="section">
        <h2>🛠️ 技术栈</h2>
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
        <h2>📋 版本信息</h2>
        <div class="version-info">
          <div class="info-item">
            <strong>当前版本：</strong>
            <span>v1.0.0</span>
          </div>
          <div class="info-item">
            <strong>最后更新：</strong>
            <span>2024年12月</span>
          </div>
          <div class="info-item">
            <strong>开发团队：</strong>
            <span>地下城分析器开发组</span>
          </div>
          <div class="info-item">
            <strong>许可证：</strong>
            <span>MIT License</span>
          </div>
        </div>
      </section>

      <!-- 快速操作 -->
      <section class="section">
        <h2>⚡ 快速操作</h2>
        <div class="quick-actions">
          <button class="action-btn primary" @click="router.push('/')">
            开始分析
          </button>
          <button class="action-btn" @click="router.push('/help')">
            查看帮助
          </button>
          <button class="action-btn" @click="router.push('/test')">
            功能测试
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
  background: #667eea;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.3s ease;
}

.back-btn:hover {
  background: #5a6fd8;
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
  background: #667eea;
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
  background: #667eea;
}

.action-btn.primary:hover {
  background: #5a6fd8;
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