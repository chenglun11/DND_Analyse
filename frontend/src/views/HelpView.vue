<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  router.push('/')
}

const helpSections = [
  {
    title: '📁 文件上传',
    icon: '📁',
    content: [
      '支持拖拽文件到上传区域',
      '支持点击选择文件按钮',
      '支持多种JSON格式的地下城文件',
      '支持批量上传多个文件',
      '支持的文件格式：Watabou、Donjon、DungeonDraft等'
    ]
  },
  {
    title: '📊 分析功能',
    icon: '📊',
    content: [
      '自动评估地下城质量',
      '生成可视化图像',
      '提供详细的分析报告',
      '计算9个核心质量指标',
      '生成改进建议'
    ]
  },
  {
    title: '📈 结果查看',
    icon: '📈',
    content: [
      '点击"查看详情"查看完整报告',
      '支持导出分析结果',
      '提供改进建议',
      '可视化路径分析',
      '质量评分详情'
    ]
  },
  {
    title: '💾 数据导出',
    icon: '💾',
    content: [
      '导出JSON格式的分析结果',
      '导出可视化图像',
      '批量导出多个文件结果',
      '自定义导出选项',
      '支持多种导出格式'
    ]
  }
]

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

const quickSteps = [
  {
    step: 1,
    title: '上传文件',
    description: '拖拽或选择地下城JSON文件',
    icon: '📁'
  },
  {
    step: 2,
    title: '开始分析',
    description: '点击"开始分析"按钮',
    icon: '⚡'
  },
  {
    step: 3,
    title: '查看结果',
    description: '等待分析完成，查看评分',
    icon: '📊'
  },
  {
    step: 4,
    title: '详细报告',
    description: '点击"查看详情"查看完整报告',
    icon: '📋'
  },
  {
    step: 5,
    title: '导出结果',
    description: '导出分析结果和可视化图像',
    icon: '💾'
  }
]

const tips = [
  '建议使用Chrome或Firefox浏览器获得最佳体验',
  '支持批量分析多个文件，提高工作效率',
  '分析结果会自动保存，刷新页面后会丢失',
  '可以随时导出分析结果，避免数据丢失',
  '系统会自动处理常见的数据格式问题',
  '可视化图像支持缩放和交互操作',
  '质量评分基于9个核心指标，全面评估地下城质量'
]
</script>

<template>
  <div class="help-page">
    <div class="help-header">
      <button class="back-btn" @click="goBack">
        ← 返回首页
      </button>
      <h1>使用帮助</h1>
      <p class="subtitle">详细的使用指南和常见问题解答</p>
    </div>

    <div class="help-content">
      <!-- 快速开始 -->
      <section class="section">
        <h2>🚀 快速开始</h2>
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
        <h2>📖 功能指南</h2>
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
        <h2>❓ 常见问题</h2>
        <div class="faq-list">
          <div v-for="faq in faqs" :key="faq.question" class="faq-item">
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
        <h2>💡 使用提示</h2>
        <div class="tips-grid">
          <div v-for="tip in tips" :key="tip" class="tip-item">
            <span class="tip-icon">💡</span>
            <span>{{ tip }}</span>
          </div>
        </div>
      </section>

      <!-- 质量评估指标说明 -->
      <section class="section">
        <h2>📊 质量评估指标说明</h2>
        <div class="metrics-explanation">
          <div class="metric-item">
            <h4>可达性评估 (Accessibility)</h4>
            <p>评估地下城各区域的连通性和可达性，确保玩家能够到达所有重要区域。</p>
          </div>
          <div class="metric-item">
            <h4>美学平衡 (Aesthetic Balance)</h4>
            <p>分析房间布局的美观性和平衡性，评估视觉设计的合理性。</p>
          </div>
          <div class="metric-item">
            <h4>环路比例 (Loop Ratio)</h4>
            <p>计算地下城中的环路结构比例，适当的环路可以增加探索的趣味性。</p>
          </div>
          <div class="metric-item">
            <h4>死胡同比例 (Dead End Ratio)</h4>
            <p>评估死胡同和无效路径的比例，过多的死胡同会影响游戏体验。</p>
          </div>
          <div class="metric-item">
            <h4>宝藏分布 (Treasure Distribution)</h4>
            <p>分析宝藏和战利品的分布合理性，确保奖励的公平性。</p>
          </div>
          <div class="metric-item">
            <h4>怪物分布 (Monster Distribution)</h4>
            <p>评估怪物和敌人的分布策略，平衡挑战性和可玩性。</p>
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
          <button class="action-btn" @click="router.push('/about')">
            关于我们
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
.help-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
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
  background: #667eea;
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
  background: #667eea;
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
  background: #667eea;
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