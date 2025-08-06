<template>
  <div :class="[
    'analysis-report bg-white rounded-xl border border-gray-200',
    compact ? 'p-2 shadow-sm' : 'p-8 shadow-lg'
  ]">
    <div v-if="!compact" class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-bold text-gray-900 flex items-center gap-2">
        <span class="w-2 h-2 bg-[#2892D7] rounded-full"></span>
        {{ t('fullyreport.detailed') }}
      </h3>
      <div class="flex items-center gap-2">
        <button @click="exportReport" class="px-3 py-1 bg-[#2892D7] text-white rounded text-sm hover:bg-[#1D70A2] transition-colors">
          {{ t('common.export') }}
        </button>
        <button @click="toggleView" class="px-3 py-1 bg-gray-100 text-gray-700 rounded text-sm hover:bg-gray-200 transition-colors">
          {{ viewMode === 'detailed' ? t('fullyreport.simple') : t('fullyreport.detailed') }}
        </button>
      </div>
    </div>


    <!-- 指标详情 -->
    <div :class="[
      'metrics-grid gap-3',
      compact ? 'grid grid-cols-1 mb-3' : 'grid grid-cols-2 gap-4 lg:gap-6 mb-8'
    ]">
      <div v-for="metric in allMetrics.filter(m => isMetricSelected(m.key))" :key="metric.key" 
           :class="[
             'metric-card border border-gray-200 rounded-lg hover:shadow-md transition-shadow bg-gray-50',
             compact ? 'p-2' : 'p-6'
           ]">
        <div :class="[
          'flex items-center justify-between',
          compact ? 'mb-1' : 'mb-3'
        ]">
          <div class="flex items-center gap-1">
            <span :class="compact ? 'text-sm' : 'text-lg'">{{ getMetricIcon(metric.key) }}</span>
            <h5 :class="[
              'font-semibold text-gray-900',
              compact ? 'text-xs' : 'text-base'
            ]">{{ metric.name }}</h5>
            <span v-if="!isMetricSelected(metric.key)" class="text-xs text-gray-400 bg-gray-100 px-1 py-0.5 rounded">{{t('common.disabled')}}</span>
          </div>
          <div class="text-right">
            <div :class="[
              'font-bold',
              compact ? 'text-sm' : 'text-xl',
              isMetricSelected(metric.key) ? getScoreColor(getMetricScore(metric.key)) : 'text-gray-400'
            ]">
              {{ isMetricSelected(metric.key) ? formatScore(getMetricScore(metric.key)) : t('common.notAvailable') }}
            </div>
          </div>
        </div>
        
        <!-- 进度条 -->
        <div :class="compact ? 'mb-1' : 'mb-3'">
          <div :class="[
            'w-full bg-gray-200 rounded-full',
            compact ? 'h-1' : 'h-2'
          ]">
            <div :class="[
              'rounded-full transition-all duration-500',
              compact ? 'h-1' : 'h-2',
              isMetricSelected(metric.key) ? getProgressBarColor(getMetricScore(metric.key)) : 'bg-gray-400'
            ]"
            :style="{ width: isMetricSelected(metric.key) ? `${getMetricScore(metric.key) * 100}%` : '0%' }"></div>
          </div>
        </div>

        <p v-if="!compact" :class="[
          'text-sm mb-2',
          isMetricSelected(metric.key) ? 'text-gray-600' : 'text-gray-400'
        ]">{{ metric.description }}</p>

        <!-- 详细视图 -->
        <div v-if="!compact && viewMode === 'detailed' && isMetricSelected(metric.key) && getMetricDetail(metric.key)" class="detailed-info bg-white border border-gray-100 rounded p-4 mt-4">
          <h6 class="text-sm font-semibold text-gray-800 mb-3">{{t('fullyreport.detailedInfo')}}</h6>
          <div class="text-sm text-gray-600 space-y-3">
            <div v-for="(value, key) in getDetailInfo(getMetricDetail(metric.key))" :key="key" class="break-words">
              <div class="flex flex-col sm:flex-row sm:justify-between gap-2">
                <span class="text-gray-700 font-medium min-w-0 flex-shrink-0 text-sm">{{ key }}:</span>
                <span class="text-gray-900 font-mono break-all text-sm">{{ value }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 评估等级 -->
        <div :class="[
          'flex items-center justify-between',
          compact ? 'mt-1' : 'mt-3'
        ]">
            <span :class="[
              'px-2 py-1 rounded-full text-xs font-medium',
              isMetricSelected(metric.key) ? getScoreBadgeClass(getMetricScore(metric.key)) : 'bg-gray-100 text-gray-400'
            ]">
            {{ isMetricSelected(metric.key) ? getScoreGrade(getMetricScore(metric.key)) : t('common.disabled') }}
          </span>
          <span v-if="!compact && viewMode !== 'detailed'" :class="[
            'text-xs',
            isMetricSelected(metric.key) ? 'text-gray-500' : 'text-gray-400'
          ]">
          </span>
        </div>
      </div>
    </div>

    <!-- 雷达图 -->
    <div v-if="!compact && viewMode === 'detailed'" class="radar-chart-container mb-8">
      <h4 class="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
        <span>📈</span>
        {{ t('fullyreport.radarChart') }}
      </h4>
      <div class="bg-gray-50 border border-gray-200 rounded-lg p-6">
        <canvas ref="radarCanvas" width="500" height="400"></canvas>
      </div>
    </div>

    <!-- 分析总结 -->
    <div v-if="!compact" class="analysis-summary bg-gradient-to-r from-white to-gray-50 border  rounded-lg p-6">
      <h4 class="text-xl font-semibold text-gray-800 mb-4">{{t('fullyreport.analysisSummary')}}</h4>
      
      <div class="space-y-4">
        <div>
          <h5 class="text-base font-semibold text-green-800 mb-3">{{t('fullyreport.strength')}}</h5>
          <div class="space-y-2">
                         <div 
               v-for="strength in getStrengths()" 
               :key="strength"
               class="text-base text-green-700 flex items-center gap-2">
               <span class="text-green-500">✓</span>
               {{ strength }}
             </div>
          </div>
        </div>
        
        <div v-if="viewMode !== 'detailed'">
          <h5 class="text-base font-semibold text-orange-800 mb-3">{{t('fullyreport.improvement')}}</h5>
          <div class="space-y-2">
                         <div 
               v-for="weakness in getWeaknesses()" 
               :key="weakness"
               class="text-base text-orange-700 flex items-center gap-2">
               <span class="text-orange-500">⚠</span>
               {{ weakness }}
             </div>
          </div>
        </div>
        
        <div>
          <h5 class="text-base font-semibold text-[#173753] mb-3">{{t('fullyreport.overallAssessment')}}</h5>
          <p class="text-base text-[#1D70A2] leading-relaxed">{{ getOverallAssessment() }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'  

const { t } = useI18n()

interface Props {
  scores: Record<string, { score: number; detail?: any }>
  overallScore: number
  grade: string
  dungeonName?: string
  selectedMetrics?: string[]
  compact?: boolean
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
  // 使用传入的selectedMetrics，如果没有传入则使用内部的selectedMetrics
  const metrics = props.selectedMetrics || selectedMetrics.value
  
  if (metrics.length === 0) {
    return true // 如果没有选择任何指标，默认显示所有指标为启用状态
  }
  if (metrics.length === 9) {
    return true // 如果选择了所有9个指标，也显示为启用状态
  }
  return metrics.includes(metric)
}

// 获取指标分数
const getMetricScore = (metric: string): number => {
  const score = props.scores[metric]?.score || 0
  return Number(score)
}

// 格式化显示分数
const formatScore = (score: number): string => {
  if (score === 0) return '0.00'
  if (score < 0.01) return '< 0.01'
  if (score >= 1) return '1.00'
  // 限制小数位数为3位，避免超长小数
  return Number(score.toFixed(3)).toString() // 使用Number转换去除末尾0
}

// 获取指标详细信息
const getMetricDetail = (metric: string): any => {
  return props.scores[metric]?.detail || null
}

// 定义所有指标
const allMetrics = [
  { key: 'dead_end_ratio', name: t('metrics.dead_end_ratio'), description: t('metricDescriptions.dead_end_ratio.description') },
  { key: 'geometric_balance', name: t('metrics.geometric_balance'), description: t('metricDescriptions.geometric_balance.description') },
  { key: 'treasure_monster_distribution', name: t('metrics.treasure_monster_distribution'), description: t('metricDescriptions.treasure_monster_distribution.description') },
  { key: 'accessibility', name: t('metrics.accessibility'), description: t('metricDescriptions.accessibility.description') },
  { key: 'path_diversity', name: t('metrics.path_diversity'), description: t('metricDescriptions.path_diversity.description') },
  { key: 'loop_ratio', name: t('metrics.loop_ratio'), description: t('metricDescriptions.loop_ratio.description') },
  { key: 'degree_variance', name: t('metrics.degree_variance'), description: t('metricDescriptions.degree_variance.description') },
  { key: 'door_distribution', name: t('metrics.door_distribution'), description: t('metricDescriptions.door_distribution.description') },
  { key: 'key_path_length', name: t('metrics.key_path_length'), description: t('metricDescriptions.key_path_length.description') }
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
  return ''
}

const getMetricName = (metric: string): string => {
  return t(`metrics.${metric}`) || metric
}

const getMetricDescription = (metric: string): string => {
  return t(`metricDescriptions.${metric}.description`) || '暂无描述'
}

const getScoreColor = (score: number): string => {
  if (score >= 0.8) return 'text-[#059669]'  /* 优秀 - 绿色 */
  if (score >= 0.65) return 'text-[#0891b2]' /* 良好 - 青色 */
  if (score >= 0.5) return 'text-[#d97706]'  /* 一般 - 橙色 */
  if (score >= 0.35) return 'text-[#dc2626]' /* 差 - 红色 */
  if (score > 0) return 'text-[#dc2626]'     /* 很差 - 红色 */
  return 'text-[#dc2626]'  /* 0分 - 红色，表示严重问题 */
}

const getProgressBarColor = (score: number): string => {
  if (score >= 0.8) return 'bg-[#059669]'  /* 优秀 - 绿色 */
  if (score >= 0.65) return 'bg-[#0891b2]' /* 良好 - 青色 */
  if (score >= 0.5) return 'bg-[#d97706]'  /* 一般 - 橙色 */
  if (score >= 0.35) return 'bg-[#dc2626]' /* 差 - 红色 */
  if (score > 0) return 'bg-[#dc2626]'     /* 很差 - 红色 */
  return 'bg-[#dc2626]'  /* 0分 - 红色，表示严重问题 */
}

const getScoreBadgeClass = (score: number): string => {
  if (score >= 0.8) return 'bg-[#ecfdf5] text-[#059669]'  /* 优秀 - 绿色背景 */
  if (score >= 0.65) return 'bg-[#ecfeff] text-[#0891b2]' /* 良好 - 青色背景 */
  if (score >= 0.5) return 'bg-[#fffbeb] text-[#d97706]'  /* 一般 - 橙色背景 */
  if (score >= 0.35) return 'bg-[#fef2f2] text-[#dc2626]' /* 差 - 红色背景 */
  if (score > 0) return 'bg-[#fef2f2] text-[#dc2626]'     /* 很差 - 红色背景 */
  return 'bg-[#fef2f2] text-[#dc2626]'  /* 0分 - 红色背景，表示严重问题 */
}

const getGradeBadgeClass = (grade: string): string => {
  const classes = {
    [t('scoreLevels.excellent')]: 'bg-[#ecfdf5] text-[#059669]',  /* 优秀 - 绿色 */
    [t('scoreLevels.good')]: 'bg-[#ecfeff] text-[#0891b2]', /* 良好 - 青色 */
    [t('scoreLevels.average')]: 'bg-[#fffbeb] text-[#d97706]',  /* 一般 - 橙色 */
    [t('scoreLevels.poor')]: 'bg-[#fef2f2] text-[#dc2626]', /* 较差 - 红色 */
    '未知': 'bg-gray-100 text-gray-800'
  }
  return classes[grade as keyof typeof classes] || 'bg-gray-100 text-gray-800'
}

const getScoreGrade = (score: number): string => {
  if (score >= 0.8) return t('scoreLevels.excellent')
  if (score >= 0.65) return t('scoreLevels.good')
  if (score >= 0.5) return t('scoreLevels.average')
  if (score >= 0.35) return t('scoreLevels.poor')
  return t('fullyreport.improvement')
}

const getDetailInfo = (detail: any): Record<string, any> => {
  if (!detail || typeof detail !== 'object') return {}
  
  const info: Record<string, any> = {}
  
  // 定义有意义的字段名称映射 - 保留英文显示
  const fieldMap: Record<string, string> = {
    'total_rooms': 'Total Rooms',
    'dead_end_rooms': 'Dead End Rooms',
    'dead_end_ratio': 'Dead End Ratio',
    'average_distance': 'Average Distance',
    'max_distance': 'Max Distance',
    'connected_components': 'Connected Components',
    'loops_count': 'Loops Count',
    'total_connections': 'Total Connections',
    'treasure_count': 'Treasure Count',
    'monster_count': 'Monster Count',
    'door_count': 'Door Count',
    'key_count': 'Key Count',
    'avg_path_diversity': 'Avg Path Diversity',
    'std_path_diversity': 'Std Path Diversity',
    'max_path_diversity': 'Max Path Diversity',
    'min_path_diversity': 'Min Path Diversity',
    'total_pairs_analyzed': 'Total Pairs Analyzed',
    'rounds_completed': 'Rounds Completed',
    'algorithm': 'Algorithm',
    'fusion_method': 'Fusion Method',
    'normalization': 'Normalization',
    'sampling': 'Sampling',
    'cyclomatic_number': 'Cyclomatic Number',
    'loop_ratio': 'Loop Ratio',
    'sigmoid_loop_ratio': 'Sigmoid Loop Ratio',
    'total_edges': 'Total Edges',
    'note': 'Note',
    'reachability_ratio': 'Reachability Ratio',
    'path_variance': 'Path Variance',
    'avg_path_length': 'Avg Path Length',
    'raw_variance': 'Raw Variance',
    'normalized_variance': 'Normalized Variance',
    'degrees': 'Degrees',
    'max_variance': 'Max Variance',
    'room_count': 'Room Count',
    'mean_degree': 'Mean Degree',
    'cv': 'CV',
    'avg_entropy': 'Avg Entropy',
    'weights': 'Weights',
    'normalized': 'Normalized',
    'dead_end_count': 'Dead End Count',
    'reason': 'Reason',
    'score_breakdown': 'Score Breakdown',
    'raw_loop_ratio': 'Raw Loop Ratio',
    'final_score': 'Final Score',
    'detailed_analysis': 'Detailed Analysis',
    'round_0': 'Round 0',
    'round_1': 'Round 1',
    'round_2': 'Round 2',
    'round_3': 'Round 3',
    'round_4': 'Round 4',
    'round_5': 'Round 5',
    'round_6': 'Round 6',
    'round_7': 'Round 7',
    'round_8': 'Round 8',
    'round_9': 'Round 9',
    'round_10': 'Round 10',
    'round_11': 'Round 11',
    'round_12': 'Round 12',
    'round_13': 'Round 13',
    'round_14': 'Round 14',
    'round_15': 'Round 15',
    'round_16': 'Round 16',
    'round_17': 'Round 17',
    'round_18': 'Round 18',
    'round_19': 'Round 19',
    'round_20': 'Round 20',
    'samplingMulti-round strategy': 'Multi-round Strategy'
  }
  
  // 过滤和清理数据
  for (const [key, value] of Object.entries(detail)) {
    // 过滤无意义的字段和技术性太强的字段
    if (key === 'score' || key === 'detail' || key === 'metric_type' || 
        key === 'debug' || key === 'detailed_analysis' || key === 'score_breakdown' ||
        key.startsWith('round_') || key === 'algorithm' || key === 'note' ||
        value === null || value === undefined || value === '' ||
        (typeof value === 'number' && isNaN(value))) {
      continue
    }
    
    // 优化字段名称显示 - 使用英文并保持简洁
    let displayName = fieldMap[key] || key.replace(/_/g, ' ')
    
    // 如果字段名太长，进行缩写
    if (displayName.length > 20) {
      displayName = displayName.replace(/Average/g, 'Avg')
      displayName = displayName.replace(/Maximum/g, 'Max')
      displayName = displayName.replace(/Minimum/g, 'Min')
      displayName = displayName.replace(/Standard/g, 'Std')
      displayName = displayName.replace(/Normalized/g, 'Norm')
    }
    
    if (typeof value === 'number') {
      // 数字格式化 - 限制小数位数，避免超长小数
      if (value < 0.01 && value > 0) {
        info[displayName] = '< 0.01'
      } else if (value > 1000) {
        info[displayName] = Math.round(value).toLocaleString()
      } else if (value % 1 === 0) {
        info[displayName] = value.toString()
      } else {
        // 限制小数位数为3位，避免超长小数
        const formattedValue = Number(value.toFixed(3)).toString()
        info[displayName] = formattedValue
      }
    } else if (typeof value === 'boolean') {
      info[displayName] = value ? '是' : '否'
    } else if (typeof value === 'string' && value.length < 100) {
      info[displayName] = value
    } else if (Array.isArray(value) && value.length < 20) {
      // 对数组中的数字进行格式化
      const formattedArray = value.map(item => {
        if (typeof item === 'number') {
          if (item < 0.01 && item > 0) {
            return '< 0.01'
          } else if (item > 1000) {
            return Math.round(item).toLocaleString()
          } else if (item % 1 === 0) {
            return item.toString()
          } else {
            // 限制小数位数为3位，避免超长小数
            return Number(item.toFixed(3)).toString()
          }
        }
        return item
      })
      info[displayName] = formattedArray.join(', ')
    }
  }
  
  return info
}

const getImprovementTip = (metric: string, score: number): string => {
  if (score >= 0.8) return t('suggestions.continuousOptimization.description')
  
  const tips = {
    dead_end_ratio: t('suggestions.deadEndRatio.description'),
    geometric_balance: t('suggestions.geometricBalance.description'),
    treasure_monster_distribution: t('suggestions.treasureMonsterDistribution.description'),
    accessibility: t('suggestions.accessibility.description'),
    path_diversity: t('suggestions.pathDiversity.description'),
    loop_ratio: t('suggestions.loopRatio.description'),
    degree_variance: t('suggestions.degreeVariance.description'),
    door_distribution: t('suggestions.doorDistribution.description'),
    key_path_length: t('suggestions.keyPathLength.description')
  }
  return tips[metric as keyof typeof tips] || t('common.noData')
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
    return t('fullyreport.OverallAssessment.excellent')
  } else if (score >= 0.65) {
    return t('fullyreport.OverallAssessment.good')
  } else if (score >= 0.5) {
    return t('fullyreport.OverallAssessment.average')
  } else if (score >= 0.35) {
    return t('fullyreport.OverallAssessment.poor')
  } else {
    return t('fullyreport.OverallAssessment.poor')
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