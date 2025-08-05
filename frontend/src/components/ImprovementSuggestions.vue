<template>
  <div class="improvement-suggestions bg-white rounded-xl shadow-lg border border-gray-200 p-6">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-bold text-gray-900 flex items-center gap-2">
        <span class="w-2 h-2 bg-yellow-500 rounded-full"></span>
        💡 改进建议
      </h3>
      <span class="text-sm text-gray-500">{{ suggestions.length }} 条建议</span>
    </div>

    <div v-if="suggestions.length === 0" class="text-center py-8">
      <div class="text-6xl mb-4">🎉</div>
      <p class="text-gray-600">恭喜！暂无改进建议，地牢设计已经非常优秀！</p>
    </div>

    <div v-else class="space-y-4">
      <div v-for="(suggestion, index) in suggestions" :key="index" 
           class="improvement-item bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 rounded-lg p-4 transition-all duration-300 hover:shadow-md">
        <div class="flex items-start gap-3">
          <div class="flex-shrink-0">
            <div :class="[
              'w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm',
              getPriorityColor(suggestion.priority)
            ]">
              {{ index + 1 }}
            </div>
          </div>
          <div class="flex-1">
            <div class="flex items-center justify-between mb-2">
              <h4 class="font-semibold text-gray-900">{{ suggestion.title }}</h4>
              <span :class="[
                'px-2 py-1 rounded-full text-xs font-medium',
                getPriorityBadgeClass(suggestion.priority)
              ]">
                {{ getPriorityText(suggestion.priority) }}
              </span>
            </div>
            <p class="text-gray-700 text-sm mb-3">{{ suggestion.description }}</p>
            
            <!-- 具体改进措施 -->
            <div v-if="suggestion.actions && suggestion.actions.length > 0" class="mb-3">
              <p class="text-xs font-medium text-gray-800 mb-1">建议措施：</p>
              <ul class="space-y-1">
                <li v-for="(action, actionIndex) in suggestion.actions" :key="actionIndex" 
                    class="text-xs text-gray-600 flex items-start gap-1">
                  <span class="text-green-500 font-bold">•</span>
                  <span>{{ action }}</span>
                </li>
              </ul>
            </div>

            <!-- 预期效果 -->
            <div v-if="suggestion.expectedImprovement" class="bg-green-50 border border-green-200 rounded p-2">
              <p class="text-xs text-green-800">
                <span class="font-medium">预期效果：</span>
                {{ suggestion.expectedImprovement }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 总结和额外建议 -->
    <div v-if="suggestions.length > 0" class="mt-6 pt-6 border-t border-gray-200">
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 class="font-semibold text-blue-900 mb-2">📊 总体建议</h4>
        <p class="text-blue-800 text-sm mb-2">
          根据分析结果，该地牢在 {{ getTotalCategories() }} 个方面需要改进。
          建议优先处理 <span class="font-semibold">{{ getHighPrioritySuggestions().length }}</span> 个高优先级问题。
        </p>
        <div class="flex flex-wrap gap-2 mt-3">
          <span v-for="category in getCategories()" :key="category" 
                class="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
            {{ category }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface ImprovementSuggestion {
  title: string
  description: string
  priority: 'high' | 'medium' | 'low'
  category: string
  metric?: string
  currentScore?: number
  targetScore?: number
  actions?: string[]
  expectedImprovement?: string
}

interface Props {
  scores: Record<string, { score: number; detail?: any }>
  overallScore?: number
}

const props = defineProps<Props>()

// 根据评分生成改进建议
const suggestions = computed<ImprovementSuggestion[]>(() => {
  const suggestions: ImprovementSuggestion[] = []
  
  if (!props.scores) return suggestions

  // 死胡同比例建议
  if (props.scores.dead_end_ratio?.score < 0.6) {
    suggestions.push({
      title: '减少死胡同设计',
      description: '当前地牢存在过多死胡同，可能导致玩家感到挫败或探索体验单调。',
      priority: props.scores.dead_end_ratio.score < 0.3 ? 'high' : 'medium',
      category: '布局优化',
      metric: 'dead_end_ratio',
      currentScore: props.scores.dead_end_ratio.score,
      targetScore: 0.7,
      actions: [
        '将部分死胡同连接到其他区域',
        '在死胡同末端放置有价值的奖励',
        '创建循环路径替代直线通道',
        '增加隐藏通道或秘密房间'
      ],
      expectedImprovement: '提升探索流畅性，减少玩家挫败感'
    })
  }

  // 几何平衡建议
  if (props.scores.geometric_balance?.score < 0.65) {
    suggestions.push({
      title: '优化空间布局平衡',
      description: '地牢的几何布局不够平衡，可能影响视觉美感和游戏体验。',
      priority: props.scores.geometric_balance.score < 0.4 ? 'high' : 'medium',
      category: '视觉设计',
      metric: 'geometric_balance',
      currentScore: props.scores.geometric_balance.score,
      targetScore: 0.75,
      actions: [
        '调整房间大小比例，避免过大或过小的房间',
        '优化房间分布，创造更好的视觉平衡',
        '确保主要区域的对称性或有序性',
        '合理安排重要房间的位置'
      ],
      expectedImprovement: '提升地牢美观度和空间感'
    })
  }

  // 宝藏怪物分布建议
  if (props.scores.treasure_monster_distribution?.score < 0.6) {
    suggestions.push({
      title: '优化奖励分布策略',
      description: '宝藏和怪物的分布可能不够合理，影响游戏平衡性和探索动机。',
      priority: 'high',
      category: '游戏平衡',
      metric: 'treasure_monster_distribution',
      currentScore: props.scores.treasure_monster_distribution.score,
      targetScore: 0.8,
      actions: [
        '确保高价值奖励伴随相应的挑战',
        '在探索路径上合理分布小奖励',
        '避免奖励过于集中或分散',
        '根据地牢深度调整奖励价值'
      ],
      expectedImprovement: '提升游戏平衡性和探索动机'
    })
  }

  // 可达性建议
  if (props.scores.accessibility?.score < 0.7) {
    suggestions.push({
      title: '改善区域连通性',
      description: '部分区域的可达性存在问题，可能导致玩家无法到达某些重要位置。',
      priority: 'high',
      category: '连通性',
      metric: 'accessibility',
      currentScore: props.scores.accessibility.score,
      targetScore: 0.85,
      actions: [
        '检查并修复断开的连接',
        '增加备用路径到达重要区域',
        '确保所有房间都可以从入口到达',
        '考虑添加快捷通道或传送点'
      ],
      expectedImprovement: '确保完整的探索体验'
    })
  }

  // 路径多样性建议
  if (props.scores.path_diversity?.score < 0.5) {
    suggestions.push({
      title: '增加路径选择多样性',
      description: '当前地牢的路径选择较为单一，缺乏探索的策略性和趣味性。',
      priority: 'medium',
      category: '探索体验',
      metric: 'path_diversity',
      currentScore: props.scores.path_diversity.score,
      targetScore: 0.7,
      actions: [
        '创建多条通往目标的路径',
        '设计分支路径和可选区域',
        '增加需要特殊钥匙或技能的路径',
        '平衡不同路径的风险和奖励'
      ],
      expectedImprovement: '提升探索策略性和重玩价值'
    })
  }

  // 环路比例建议
  if (props.scores.loop_ratio?.score < 0.4) {
    suggestions.push({
      title: '增加循环路径设计',
      description: '地牢缺乏足够的环路设计，可能导致线性化的探索体验。',
      priority: 'medium',
      category: '布局优化',
      metric: 'loop_ratio',
      currentScore: props.scores.loop_ratio.score,
      targetScore: 0.6,
      actions: [
        '连接现有的死胡同形成环路',
        '设计大型循环区域',
        '创建多层次的环路结构',
        '确保环路有明确的游戏目的'
      ],
      expectedImprovement: '提升探索流畅性和导航便利性'
    })
  }

  // 度方差建议
  if (props.scores.degree_variance?.score < 0.6) {
    suggestions.push({
      title: '优化连接度分布',
      description: '房间连接度的变化不够丰富，可能影响地牢的复杂性和探索体验。',
      priority: 'low',
      category: '结构优化',
      metric: 'degree_variance',
      currentScore: props.scores.degree_variance.score,
      targetScore: 0.7,
      actions: [
        '创建具有不同连接数的房间',
        '设计中心枢纽房间',
        '平衡简单通道和复杂交叉点',
        '确保重要房间有多个入口'
      ],
      expectedImprovement: '增加地牢结构的复杂性和趣味性'
    })
  }

  // 按优先级排序
  return suggestions.sort((a, b) => {
    const priorityOrder = { high: 3, medium: 2, low: 1 }
    return priorityOrder[b.priority] - priorityOrder[a.priority]
  })
})

const getPriorityColor = (priority: string): string => {
  const colors = {
    high: 'bg-red-500',
    medium: 'bg-yellow-500', 
    low: 'bg-blue-500'
  }
  return colors[priority] || 'bg-gray-500'
}

const getPriorityBadgeClass = (priority: string): string => {
  const classes = {
    high: 'bg-red-100 text-red-800',
    medium: 'bg-yellow-100 text-yellow-800',
    low: 'bg-blue-100 text-blue-800'
  }
  return classes[priority] || 'bg-gray-100 text-gray-800'
}

const getPriorityText = (priority: string): string => {
  const texts = {
    high: '高优先级',
    medium: '中优先级',
    low: '低优先级'
  }
  return texts[priority] || '未知'
}

const getTotalCategories = (): number => {
  const categories = new Set(suggestions.value.map(s => s.category))
  return categories.size
}

const getHighPrioritySuggestions = (): ImprovementSuggestion[] => {
  return suggestions.value.filter(s => s.priority === 'high')
}

const getCategories = (): string[] => {
  const categories = new Set(suggestions.value.map(s => s.category))
  return Array.from(categories)
}
</script>

<style scoped>
.improvement-suggestions {
  max-height: 600px;
  overflow-y: auto;
}

.improvement-item {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.improvement-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px -5px rgba(0, 0, 0, 0.1);
}

/* 自定义滚动条 */
.improvement-suggestions::-webkit-scrollbar {
  width: 6px;
}

.improvement-suggestions::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}

.improvement-suggestions::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 3px;
}

.improvement-suggestions::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.5);
}
</style>