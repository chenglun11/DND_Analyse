<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { computed } from 'vue'

const router = useRouter()
const { t } = useI18n()

const goBack = () => {
  router.push('/')
}

const helpSections = computed(() => [
  {
    title: t('help.fileUpload.title'),
    icon: '📁',
    content: [
      t('help.fileUpload.content.0'),
      t('help.fileUpload.content.1'),
      t('help.fileUpload.content.2'),
      t('help.fileUpload.content.3'),
      t('help.fileUpload.content.4')
    ]
  },
  {
    title: t('help.analysis.title'),
    icon: '📊',
    content: [
      t('help.analysis.content.0'),
      t('help.analysis.content.1'),
      t('help.analysis.content.2'),
      t('help.analysis.content.3'),
      t('help.analysis.content.4')
    ]
  },
  {
    title: t('help.results.title'),
    icon: '📈',
    content: [
      t('help.results.content.0'),
      t('help.results.content.1'),
      t('help.results.content.2'),
      t('help.results.content.3'),
      t('help.results.content.4')
    ]
  },
  {
    title: t('help.export.title'),
    icon: '💾',
    content: [
      t('help.export.content.0'),
      t('help.export.content.1'),
      t('help.export.content.2'),
      t('help.export.content.3'),
      t('help.export.content.4')
    ]
  }
])

const faqs = [
  {
    question: '支持哪些地下城文件格式？',
    answer: '目前支持Watabou、Donjon、DungeonDraft等多种格式的JSON文件。每种格式都有专门的适配器进行转换。'
  },
  {
    question: '分析需要多长时间？',
    answer: '单个文件分析通常在几秒到几十秒之间，取决于地下城的复杂程度。批量分析时间会相应增加。'
  },
  {
    question: '如何理解质量评分？',
    answer: '评分范围是0-100，分数越高表示地下城质量越好。系统会从可达性、美学平衡、环路比例等多个维度进行评估。'
  },
  {
    question: '可以分析多大的地下城？',
    answer: '理论上没有大小限制，但建议单个地下城房间数量不超过1000个，以确保最佳性能。'
  },
  {
    question: '分析结果会保存吗？',
    answer: '当前会话的分析结果会保存在浏览器中，刷新页面后会丢失。建议及时导出重要结果。'
  },
  {
    question: '如何获得更好的分析结果？',
    answer: '确保地下城文件格式正确，房间和走廊信息完整。系统会自动处理常见的数据问题。'
  }
]

const quickSteps = computed(() => [
  {
    step: 1,
    title: t('help.quickSteps.0.title'),
    description: t('help.quickSteps.0.description'),
    icon: '📁'
  },
  {
    step: 2,
    title: t('help.quickSteps.1.title'),
    description: t('help.quickSteps.1.description'),
    icon: '⚡'
  },
  {
    step: 3,
    title: t('help.quickSteps.2.title'),
    description: t('help.quickSteps.2.description'),
    icon: '📊'
  },
  {
    step: 4,
    title: t('help.quickSteps.3.title'),
    description: t('help.quickSteps.3.description'),
    icon: '💾'
  }
])

const helpFaqs = computed(() => [
  {
    question: t('help.faqs.0.question'),
    answer: t('help.faqs.0.answer')
  },
  {
    question: t('help.faqs.1.question'),
    answer: t('help.faqs.1.answer')
  },
  {
    question: t('help.faqs.2.question'),
    answer: t('help.faqs.2.answer')
  },
  {
    question: t('help.faqs.3.question'),
    answer: t('help.faqs.3.answer')
  },
  {
    question: t('help.faqs.4.question'),
    answer: t('help.faqs.4.answer')
  },
  {
    question: t('help.faqs.5.question'),
    answer: t('help.faqs.5.answer')
  }
])

const helpTips = computed(() => [
  t('help.usageTips.tip1'),
  t('help.usageTips.tip2'),
  t('help.usageTips.tip3'),
  t('help.usageTips.tip4'),
  t('help.usageTips.tip5'),
  t('help.usageTips.tip6'),
  t('help.usageTips.tip7')
])

const helpMetrics = computed(() => [
  {
    name: 'accessibility',
    title: t('help.metricsExplanation.accessibility.title'),
    description: t('help.metricsExplanation.accessibility.description')
  },
  {
            name: 'geometric_balance',
        title: t('help.metricsExplanation.geometric_balance.title'),
        description: t('help.metricsExplanation.geometric_balance.description')
  },
  {
    name: 'loop_ratio',
    title: t('help.metricsExplanation.loop_ratio.title'),
    description: t('help.metricsExplanation.loop_ratio.description')
  },
  {
    name: 'dead_end_ratio',
    title: t('help.metricsExplanation.dead_end_ratio.title'),
    description: t('help.metricsExplanation.dead_end_ratio.description')
  },
  {
    name: 'treasure_distribution',
    title: t('help.metricsExplanation.treasure_distribution.title'),
    description: t('help.metricsExplanation.treasure_distribution.description')
  },
  {
    name: 'monster_distribution',
    title: t('help.metricsExplanation.monster_distribution.title'),
    description: t('help.metricsExplanation.monster_distribution.description')
  }
])
</script>

<template>
  <div class="help-page">
    <div class="help-header">
      <button class="back-btn" @click="goBack">
        {{ t('help.backButton') }}
      </button>
      <h1>{{ t('help.title') }}</h1>
      <p class="subtitle">{{ t('help.subtitle') }}</p>
    </div>

    <div class="help-content">
      <!-- 快速开始 -->
      <section class="section">
        <h2>🚀 {{ t('common.quickStart') }}</h2>
        <div class="steps-grid">
          <div v-for="step in quickSteps" :key="step.step" class="step-card">
            <div class="step-number">{{ step.step }}</div>
            <div class="step-icon">{{ step.icon }}</div>
            <h3>{{ step.title }}</h3>
            <p>{{ step.description }}</p>
          </div>
        </div>
      </section>

      <!-- 功能指南 -->
      <section class="section">
        <h2>📖 {{ t('common.functionGuide') }}</h2>
        <div class="guides-grid">
          <div v-for="guide in helpSections" :key="guide.title" class="guide-card">
            <div class="guide-header">
              <div class="guide-icon">{{ guide.icon }}</div>
              <h3>{{ guide.title }}</h3>
            </div>
            <ul class="guide-list">
              <li v-for="item in guide.content" :key="item">{{ item }}</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- 常见问题 -->
      <section class="section">
        <h2>❓ {{ t('common.faq') }}</h2>
        <div class="faq-list">
          <div v-for="faq in helpFaqs" :key="faq.question" class="faq-item">
            <div class="faq-question">
              <h4>{{ faq.question }}</h4>
            </div>
            <div class="faq-answer">
              <p>{{ faq.answer }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 使用提示 -->
      <section class="section">
        <h2>💡 {{ t('help.usageTips.title') }}</h2>
        <div class="tips-grid">
          <div v-for="tip in helpTips" :key="tip" class="tip-item">
            <span class="tip-icon">💡</span>
            <span>{{ tip }}</span>
          </div>
        </div>
      </section>

      <!-- 质量评估指标说明 -->
      <section class="section">
        <h2>📊 {{ t('help.metricsExplanation.title') }}</h2>
        <div class="metrics-explanation">
          <div v-for="metric in helpMetrics" :key="metric.name" class="metric-item">
            <h4>{{ metric.title }}</h4>
            <p>{{ metric.description }}</p>
          </div>
        </div>
      </section>

      <!-- 快速操作 -->
      <section class="section">
        <h2>⚡ {{ t('help.quickActions.title') }}</h2>
        <div class="quick-actions">
          <button class="action-btn primary" @click="router.push('/')">
            {{ t('help.quickActions.startAnalysis') }}
          </button>
          <button class="action-btn" @click="router.push('/about')">
            {{ t('help.quickActions.about') }}
          </button>
          <button class="action-btn" @click="router.push('/test')">
            {{ t('help.quickActions.test') }}
          </button>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.help-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background: var(--color-background);
  min-height: calc(100vh - 80px);
}

.help-header {
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

.help-header h1 {
  font-size: 2.5rem;
  color: #333;
  margin-bottom: 10px;
}

.subtitle {
  font-size: 1.2rem;
  color: #666;
}

.help-content {
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

.steps-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.step-card {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  position: relative;
  transition: transform 0.3s ease;
}

.step-card:hover {
  transform: translateY(-5px);
}

.step-number {
  position: absolute;
  top: -10px;
  left: 50%;
  transform: translateX(-50%);
  background: #4a5568;
  color: white;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.step-icon {
  font-size: 2rem;
  margin: 15px 0 10px 0;
}

.step-card h3 {
  color: #333;
  margin-bottom: 8px;
}

.step-card p {
  color: #666;
  font-size: 0.9rem;
}

.guides-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.guide-card {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #28a745;
}

.guide-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.guide-icon {
  font-size: 1.5rem;
  margin-right: 10px;
}

.guide-card h3 {
  color: #333;
  margin: 0;
}

.guide-list {
  list-style: none;
  padding: 0;
}

.guide-list li {
  padding: 5px 0;
  color: #666;
  position: relative;
  padding-left: 20px;
}

.guide-list li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #28a745;
  font-weight: bold;
}

.faq-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.faq-item {
  background: #f8f9fa;
  border-radius: 8px;
  overflow: hidden;
}

.faq-question {
  background: #4a5568;
  color: white;
  padding: 15px 20px;
}

.faq-question h4 {
  margin: 0;
  font-size: 1rem;
}

.faq-answer {
  padding: 15px 20px;
}

.faq-answer p {
  margin: 0;
  color: #666;
  line-height: 1.5;
}

.tips-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 15px;
}

.tip-item {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.tip-icon {
  font-size: 1.2rem;
  color: #667eea;
}

.metrics-explanation {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.metric-item {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.metric-item h4 {
  color: #333;
  margin-bottom: 10px;
}

.metric-item p {
  color: #666;
  line-height: 1.5;
  margin: 0;
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
  background: #5a6fd8;
}

@media (max-width: 768px) {
  .help-page {
    padding: 15px;
  }
  
  .help-header h1 {
    font-size: 2rem;
  }
  
  .back-btn {
    position: static;
    transform: none;
    margin-bottom: 20px;
    padding: 10px 20px;
    font-size: 16px;
  }
  
  .steps-grid {
    grid-template-columns: 1fr;
  }
  
  .guides-grid {
    grid-template-columns: 1fr;
  }
  
  .tips-grid {
    grid-template-columns: 1fr;
  }
  
  .metrics-explanation {
    grid-template-columns: 1fr;
  }
  
  .quick-actions {
    flex-direction: column;
  }
}
</style> 