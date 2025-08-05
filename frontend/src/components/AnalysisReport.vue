<template>
  <div class="analysis-report bg-white rounded-xl shadow-lg border border-gray-200 p-6">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-bold text-gray-900 flex items-center gap-2">
        <span class="w-2 h-2 bg-blue-500 rounded-full"></span>
        📊 详细分析报告
      </h3>
      <div class="flex items-center gap-2">
        <button @click="exportReport" class="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition-colors">
          导出报告
        </button>
        <button @click="toggleView" class="px-3 py-1 bg-gray-100 text-gray-700 rounded text-sm hover:bg-gray-200 transition-colors">
          {{ viewMode === 'detailed' ? '简化视图' : '详细视图' }}
        </button>
      </div>
    </div>

    <!-- 总体评分卡片 -->
    <div class="overall-score-card mb-6 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div>
          <h4 class="text-lg font-semibold text-gray-900 mb-1">总体评分</h4>
          <p class="text-sm text-gray-600">基于 {{ Object.keys(scores).length }} 项指标的综合评估</p>
        </div>
        <div class="text-right">
          <div :class="[
            'text-3xl font-bold mb-1',
            getScoreColor(overallScore)
          ]">
            {{ (overallScore * 100).toFixed(1) }}
          </div>
          <div :class="[
            'px-3 py-1 rounded-full text-sm font-medium',
            getGradeBadgeClass(grade)
          ]">
            {{ grade }}
          </div>
        </div>
      </div>
    </div>

    <!-- 指标详情 -->
    <div class="metrics-grid grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
      <div v-for="metric in allMetrics" :key="metric.key" 
           :class="[
             'metric-card border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow',
             isMetricSelected(metric.key) ? 'bg-gray-50' : 'bg-gray-50/50 opacity-60'
           ]">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-2">
            <span class="text-lg">{{ getMetricIcon(metric.key) }}</span>
            <h5 class="font-semibold text-gray-900">{{ metric.name }}</h5>
            <span v-if="!isMetricSelected(metric.key)" class="text-xs text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded">禁用</span>
          </div>
          <div class="text-right">
            <div :class="[
              'text-xl font-bold',
              isMetricSelected(metric.key) ? getScoreColor(getMetricScore(metric.key)) : 'text-gray-400'
            ]">
              {{ isMetricSelected(metric.key) ? (getMetricScore(metric.key) * 100).toFixed(0) + '%' : 'N/A' }}
            </div>
          </div>
        </div>
        
        <!-- 进度条 -->
        <div class="mb-3">
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div :class="[
              'h-2 rounded-full transition-all duration-500',
              isMetricSelected(metric.key) ? getProgressBarColor(getMetricScore(metric.key)) : 'bg-gray-400'
            ]"
            :style="{ width: isMetricSelected(metric.key) ? `${getMetricScore(metric.key) * 100}%` : '0%' }"></div>
          </div>
        </div>

        <p :class="[
          'text-sm mb-2',
          isMetricSelected(metric.key) ? 'text-gray-600' : 'text-gray-400'
        ]">{{ metric.description }}</p>

        <!-- 详细视图 -->
        <div v-if="viewMode === 'detailed' && isMetricSelected(metric.key) && getMetricDetail(metric.key)" class="detailed-info bg-white border border-gray-100 rounded p-3 mt-3">
          <h6 class="text-xs font-semibold text-gray-800 mb-2">详细信息</h6>
          <div class="text-xs text-gray-600 space-y-1">
            <div v-for="(value, key) in getDetailInfo(getMetricDetail(metric.key))" :key="key" class="flex justify-between">
              <span>{{ key }}:</span>
              <span class="font-medium">{{ value }}</span>
            </div>
          </div>
        </div>

        <!-- 评估等级 -->
        <div class="mt-3 flex items-center justify-between">
          <span :class="[
            'px-2 py-1 rounded-full text-xs font-medium',
            isMetricSelected(metric.key) ? getScoreBadgeClass(getMetricScore(metric.key)) : 'bg-gray-100 text-gray-400'
          ]">
            {{ isMetricSelected(metric.key) ? getScoreGrade(getMetricScore(metric.key)) : '未启用' }}
          </span>
          <span :class="[
            'text-xs',
            isMetricSelected(metric.key) ? 'text-gray-500' : 'text-gray-400'
          ]">
            {{ isMetricSelected(metric.key) ? getImprovementTip(metric.key, getMetricScore(metric.key)) : '指标未启用' }}
          </span>
        </div>
      </div>
    </div>

    <!-- 雷达图 -->
    <div v-if="viewMode === 'detailed'" class="radar-chart-container mb-6">
      <h4 class="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
        <span>📈</span>
        指标雷达图
      </h4>
      <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <canvas ref="radarCanvas" width="400" height="300"></canvas>
      </div>
    </div>

    <!-- 分析总结 -->
    <div class="analysis-summary bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-lg p-4">
      <h4 class="font-semibold text-gray-900 mb-3 flex items-center gap-2">
        <span>📝</span>
        分析总结
      </h4>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="strength-areas">
          <h5 class="text-sm font-semibold text-green-800 mb-2">优势领域</h5>
          <ul class="space-y-1">
            <li v-for="strength in getStrengths()" :key="strength" 
                class="text-sm text-green-700 flex items-center gap-1">
              <span class="text-green-500">✓</span>
              {{ strength }}
            </li>
          </ul>
        </div>
        <div class="improvement-areas">
          <h5 class="text-sm font-semibold text-orange-800 mb-2">改进空间</h5>
          <ul class="space-y-1">
            <li v-for="weakness in getWeaknesses()" :key="weakness" 
                class="text-sm text-orange-700 flex items-center gap-1">
              <span class="text-orange-500">⚠</span>
              {{ weakness }}
            </li>
          </ul>
        </div>
        <div class="overall-assessment">
          <h5 class="text-sm font-semibold text-blue-800 mb-2">总体评价</h5>
          <p class="text-sm text-blue-700">{{ getOverallAssessment() }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'

interface Props {
  scores: Record<string, { score: number; detail?: any }>
  overallScore: number
  grade: string
  dungeonName?: string
}

const props = defineProps<Props>()

const viewMode = ref<'simple' | 'detailed'>('simple')
const radarCanvas = ref<HTMLCanvasElement>()

// 从localStorage获取选中的指标
const selectedMetrics = ref<string[]>([])

// 加载选中的指标
const loadSelectedMetrics = () => {
  const saved = localStorage.getItem('selectedMetrics')
  if (saved) {
    try {
      selectedMetrics.value = JSON.parse(saved)
    } catch (error) {
      console.error('Failed to load selected metrics:', error)
      selectedMetrics.value = []
    }
  } else {
    // 如果没有保存的配置，默认选择所有9个指标
    selectedMetrics.value = [
      'dead_end_ratio',
      'geometric_balance',
      'treasure_monster_distribution',
      'accessibility',
      'path_diversity',
      'loop_ratio',
      'degree_variance',
      'door_distribution',
      'key_path_length'
    ]
  }
}

// 检查指标是否被选中
const isMetricSelected = (metric: string): boolean => {
  if (selectedMetrics.value.length === 0) {
    return true // 如果没有选择任何指标，默认显示所有指标为启用状态
  }
  if (selectedMetrics.value.length === 9) {
    return true // 如果选择了所有9个指标，也显示为启用状态
  }
  return selectedMetrics.value.includes(metric)
}

// 获取指标分数
const getMetricScore = (metric: string): number => {
  return props.scores[metric]?.score || 0
}

// 获取指标详细信息
const getMetricDetail = (metric: string): any => {
  return props.scores[metric]?.detail || null
}

// 定义所有指标
const allMetrics = [
  { key: 'dead_end_ratio', name: '死胡同比例', description: '评估地牢中死胡同的比例，影响探索流畅性' },
  { key: 'geometric_balance', name: '几何平衡', description: '分析空间布局的几何平衡性和美观度' },
  { key: 'treasure_monster_distribution', name: '奖励分布', description: '评估奖励和挑战的分布合理性' },
  { key: 'accessibility', name: '可达性', description: '检查所有区域的可达性和连通性' },
  { key: 'path_diversity', name: '路径多样性', description: '分析到达目标的路径多样性' },
  { key: 'loop_ratio', name: '环路比例', description: '评估环路设计对探索体验的影响' },
  { key: 'degree_variance', name: '连接度方差', description: '分析房间连接度的变化和复杂性' },
  { key: 'door_distribution', name: '门分布', description: '评估门的位置分布合理性' },
  { key: 'key_path_length', name: '关键路径长度', description: '分析关键路径的长度和设计' }
]

const toggleView = () => {
  viewMode.value = viewMode.value === 'simple' ? 'detailed' : 'simple'
  if (viewMode.value === 'detailed') {
    nextTick(() => {
      drawRadarChart()
    })
  }
}

const getMetricIcon = (metric: string): string => {
  const icons = {
    dead_end_ratio: '🛑',
    geometric_balance: '⚖️',
    treasure_monster_distribution: '💰',
    accessibility: '🚪',
    path_diversity: '🗺️',
    loop_ratio: '🔄',
    degree_variance: '🔗',
    door_distribution: '🚪',
    key_path_length: '🗝️'
  }
  return icons[metric as keyof typeof icons] || '📊'
}

const getMetricName = (metric: string): string => {
  const names = {
    dead_end_ratio: '死胡同比例',
    geometric_balance: '几何平衡',
    treasure_monster_distribution: '奖励分布',
    accessibility: '可达性',
    path_diversity: '路径多样性',
    loop_ratio: '环路比例',
    degree_variance: '连接度方差',
    door_distribution: '门分布',
    key_path_length: '关键路径长度'
  }
  return names[metric as keyof typeof names] || metric
}

const getMetricDescription = (metric: string): string => {
  const descriptions = {
    dead_end_ratio: '评估地牢中死胡同的比例，影响探索流畅性',
    geometric_balance: '分析空间布局的几何平衡性和美观度',
    treasure_monster_distribution: '评估奖励和挑战的分布合理性',
    accessibility: '检查所有区域的可达性和连通性',
    path_diversity: '分析到达目标的路径多样性',
    loop_ratio: '评估环路设计对探索体验的影响',
    degree_variance: '分析房间连接度的变化和复杂性',
    door_distribution: '评估门的位置分布合理性',
    key_path_length: '分析关键路径的长度和设计'
  }
  return descriptions[metric as keyof typeof descriptions] || '暂无描述'
}

const getScoreColor = (score: number): string => {
  if (score >= 0.8) return 'text-green-600'
  if (score >= 0.65) return 'text-blue-600'
  if (score >= 0.5) return 'text-yellow-600'
  if (score >= 0.35) return 'text-orange-600'
  return 'text-red-600'
}

const getProgressBarColor = (score: number): string => {
  if (score >= 0.8) return 'bg-green-500'
  if (score >= 0.65) return 'bg-blue-500'
  if (score >= 0.5) return 'bg-yellow-500'
  if (score >= 0.35) return 'bg-orange-500'
  return 'bg-red-500'
}

const getScoreBadgeClass = (score: number): string => {
  if (score >= 0.8) return 'bg-green-100 text-green-800'
  if (score >= 0.65) return 'bg-blue-100 text-blue-800'
  if (score >= 0.5) return 'bg-yellow-100 text-yellow-800'
  if (score >= 0.35) return 'bg-orange-100 text-orange-800'
  return 'bg-red-100 text-red-800'
}

const getGradeBadgeClass = (grade: string): string => {
  const classes = {
    '优秀': 'bg-green-100 text-green-800',
    '良好': 'bg-blue-100 text-blue-800',
    '一般': 'bg-yellow-100 text-yellow-800',
    '较差': 'bg-orange-100 text-orange-800',
    '未知': 'bg-gray-100 text-gray-800'
  }
  return classes[grade as keyof typeof classes] || 'bg-gray-100 text-gray-800'
}

const getScoreGrade = (score: number): string => {
  if (score >= 0.8) return '优秀'
  if (score >= 0.65) return '良好'
  if (score >= 0.5) return '一般'
  if (score >= 0.35) return '较差'
  return '需改进'
}

const getDetailInfo = (detail: any): Record<string, any> => {
  if (!detail || typeof detail !== 'object') return {}
  
  const info: Record<string, any> = {}
  for (const [key, value] of Object.entries(detail)) {
    if (typeof value === 'number') {
      info[key] = Number(value).toFixed(2)
    } else if (typeof value === 'boolean') {
      info[key] = value ? '是' : '否'
    } else {
      info[key] = String(value)
    }
  }
  return info
}

const getImprovementTip = (metric: string, score: number): string => {
  if (score >= 0.8) return '表现优秀'
  
  const tips = {
    dead_end_ratio: '考虑增加环路连接',
    geometric_balance: '调整房间布局比例',
    treasure_monster_distribution: '平衡奖励与挑战',
    accessibility: '检查连通性问题',
    path_diversity: '增加替代路径',
    loop_ratio: '添加循环设计',
    degree_variance: '丰富连接模式',
    door_distribution: '优化门的位置',
    key_path_length: '调整关键路径'
  }
  return tips[metric as keyof typeof tips] || '需要改进'
}

const getStrengths = (): string[] => {
  return Object.entries(props.scores)
    .filter(([metric, data]) => isMetricSelected(metric) && data.score >= 0.7)
    .map(([metric, _]) => getMetricName(metric))
}

const getWeaknesses = (): string[] => {
  return Object.entries(props.scores)
    .filter(([metric, data]) => isMetricSelected(metric) && data.score < 0.5)
    .map(([metric, _]) => getMetricName(metric))
}

const getOverallAssessment = (): string => {
  const score = props.overallScore
  if (score >= 0.8) {
    return '该地牢设计优秀，各项指标表现良好，能够提供优质的游戏体验。'
  } else if (score >= 0.65) {
    return '该地牢设计良好，大部分指标达标，稍作调整即可进一步提升。'
  } else if (score >= 0.5) {
    return '该地牢设计中等，存在一些需要改进的地方，建议重点关注低分指标。'
  } else if (score >= 0.35) {
    return '该地牢设计有较大改进空间，建议优先解决关键问题。'
  } else {
    return '该地牢设计需要大幅调整，建议重新考虑整体布局和设计方案。'
  }
}

const drawRadarChart = () => {
  if (!radarCanvas.value) return
  
  const canvas = radarCanvas.value
  const ctx = canvas.getContext('2d')!
  const centerX = canvas.width / 2
  const centerY = canvas.height / 2
  const radius = Math.min(canvas.width, canvas.height) / 2 - 40
  
  // 清除画布
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  
  // 获取被选中的指标数据
  const selectedMetricsData = Object.entries(props.scores).filter(([metric, _]) => isMetricSelected(metric))
  const metrics = selectedMetricsData
  const angleStep = metrics.length > 0 ? (2 * Math.PI) / metrics.length : 0
  
  // 绘制背景网格
  ctx.strokeStyle = '#e5e7eb'
  ctx.lineWidth = 1
  
  for (let i = 1; i <= 5; i++) {
    const gridRadius = (radius * i) / 5
    ctx.beginPath()
    ctx.arc(centerX, centerY, gridRadius, 0, 2 * Math.PI)
    ctx.stroke()
  }
  
  // 绘制轴线
  for (let i = 0; i < metrics.length; i++) {
    const angle = i * angleStep - Math.PI / 2
    const x = centerX + Math.cos(angle) * radius
    const y = centerY + Math.sin(angle) * radius
    
    ctx.beginPath()
    ctx.moveTo(centerX, centerY)
    ctx.lineTo(x, y)
    ctx.stroke()
  }
  
  // 绘制数据多边形
  if (metrics.length > 0) {
    ctx.fillStyle = 'rgba(59, 130, 246, 0.3)'
    ctx.strokeStyle = '#3b82f6'
    ctx.lineWidth = 2
    
    ctx.beginPath()
    for (let i = 0; i < metrics.length; i++) {
      const [_, data] = metrics[i]
      const angle = i * angleStep - Math.PI / 2
      const distance = (data.score * radius)
      const x = centerX + Math.cos(angle) * distance
      const y = centerY + Math.sin(angle) * distance
      
      if (i === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }
    }
    ctx.closePath()
    ctx.fill()
    ctx.stroke()
    
    // 绘制数据点
    ctx.fillStyle = '#3b82f6'
    for (let i = 0; i < metrics.length; i++) {
      const [_, data] = metrics[i]
      const angle = i * angleStep - Math.PI / 2
      const distance = (data.score * radius)
      const x = centerX + Math.cos(angle) * distance
      const y = centerY + Math.sin(angle) * distance
      
      ctx.beginPath()
      ctx.arc(x, y, 4, 0, 2 * Math.PI)
      ctx.fill()
    }
    
    // 绘制标签
    ctx.fillStyle = '#374151'
    ctx.font = '12px Arial'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    
    for (let i = 0; i < metrics.length; i++) {
      const [metric, _] = metrics[i]
      const angle = i * angleStep - Math.PI / 2
      const labelDistance = radius + 25
      const x = centerX + Math.cos(angle) * labelDistance
      const y = centerY + Math.sin(angle) * labelDistance
      
      ctx.fillText(getMetricName(metric), x, y)
    }
  }
}

const exportReport = () => {
  const reportData = {
    dungeon_name: props.dungeonName || '未命名地牢',
    analysis_date: new Date().toISOString(),
    overall_score: props.overallScore,
    grade: props.grade,
    detailed_scores: props.scores,
    summary: {
      strengths: getStrengths(),
      weaknesses: getWeaknesses(),
      assessment: getOverallAssessment()
    }
  }
  
  const dataStr = JSON.stringify(reportData, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${props.dungeonName || 'dungeon'}_analysis_report_${new Date().toISOString().slice(0, 10)}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

onMounted(() => {
  loadSelectedMetrics() // 在组件挂载时加载选中的指标
  if (viewMode.value === 'detailed') {
    nextTick(() => {
      drawRadarChart()
    })
  }
})
</script>

<style scoped>
.analysis-report {
  max-height: 800px;
  overflow-y: auto;
}

.metric-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.metric-card:hover {
  transform: translateY(-2px);
}

.overall-score-card {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(99, 102, 241, 0.1) 100%);
}

/* 自定义滚动条 */
.analysis-report::-webkit-scrollbar {
  width: 6px;
}

.analysis-report::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}

.analysis-report::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 3px;
}

.analysis-report::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.5);
}
</style>