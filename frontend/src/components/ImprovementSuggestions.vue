<template>
  <div :class="[
    'improvement-suggestions bg-white rounded-xl border border-gray-200',
    compact ? 'p-2 shadow-sm' : 'p-6 shadow-lg'
  ]">
    <div v-if="!compact" class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-bold text-gray-900 flex items-center gap-2">
        <span class="w-2 h-2 bg-yellow-500 rounded-full"></span>
        {{ t('fullyreport.suggestions') }}
      </h3>
      <span class="text-sm text-gray-500">{{ suggestions.length }} {{ t('fullyreport.suggestions') }}</span>
    </div>

    <div v-if="suggestions.length === 0" :class="compact ? 'text-center py-4' : 'text-center py-8'">
      <div v-if="!compact" class="text-6xl mb-4"></div>
      <p :class="compact ? 'text-sm text-gray-600' : 'text-gray-600'">{{ t('fullyreport.noSuggestions') }}</p>
    </div>

    <div v-else :class="compact ? 'space-y-2' : 'space-y-4'">
      <div v-for="(suggestion, index) in suggestions" :key="index" 
           :class="[
             'improvement-item bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 rounded-lg transition-all duration-300 hover:shadow-md',
             compact ? 'p-2' : 'p-4'
           ]">
        <div :class="compact ? 'flex items-start gap-2' : 'flex items-start gap-3'">
          <div class="flex-shrink-0">
            <div :class="[
              'rounded-full flex items-center justify-center text-white font-bold',
              compact ? 'w-6 h-6 text-xs' : 'w-8 h-8 text-sm',
              getPriorityColor(suggestion.priority)
            ]">
              {{ index + 1 }}
            </div>
          </div>
          <div class="flex-1">
            <div :class="[
              'flex items-center justify-between',
              compact ? 'mb-1' : 'mb-2'
            ]">
              <h4 :class="[
                'font-semibold text-gray-900',
                compact ? 'text-sm' : 'text-base'
              ]">{{ suggestion.title }}</h4>
              <span v-if="!compact" :class="[
                'px-2 py-1 rounded-full text-xs font-medium',
                getPriorityBadgeClass(suggestion.priority)
              ]">
                {{ getPriorityText(suggestion.priority) }}
              </span>
            </div>
            <p :class="[
              'text-gray-700',
              compact ? 'text-xs mb-1' : 'text-sm mb-3'
            ]">{{ suggestion.description }}</p>
            
            <!-- 具体改进措施 -->
            <div v-if="!compact && suggestion.actions && suggestion.actions.length > 0" class="mb-3">
              <p class="text-xs font-medium text-gray-800 mb-1">{{ t('fullyreport.suggestionsActions') }}</p>
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
                <span class="font-medium">{{ t('fullyreport.expectedImprovement') }}</span>
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
        <h4 class="font-semibold text-blue-900 mb-2">{{ t('fullyreport.suggestionsSummaryOverall') }}</h4>
        <p class="text-blue-800 text-sm mb-2">
          {{ t('fullyreport.suggestionsSummary', { totalCategories: getTotalCategories(), highPrioritySuggestions: getHighPrioritySuggestions().length }) }}
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
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

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
  compact?: boolean
}

const props = defineProps<Props>()

// 根据评分生成改进建议
const suggestions = computed<ImprovementSuggestion[]>(() => {
  const suggestions: ImprovementSuggestion[] = []
  
  if (!props.scores) return suggestions

  // 获取当前语言的 actions
  const getActions = (metric: string): string[] => {
    const actionsMap: { [key: string]: string[] } = {
      dead_end_ratio: [
        t('forSuggesstions.dead_end_ratio.actions.0'),
        t('forSuggesstions.dead_end_ratio.actions.1'),
        t('forSuggesstions.dead_end_ratio.actions.2'),
        t('forSuggesstions.dead_end_ratio.actions.3')
      ],
      geometric_balance: [
        t('forSuggesstions.geometric_balance.actions.0'),
        t('forSuggesstions.geometric_balance.actions.1'),
        t('forSuggesstions.geometric_balance.actions.2'),
        t('forSuggesstions.geometric_balance.actions.3')
      ],
      treasure_monster_distribution: [
        t('forSuggesstions.treasure_monster_distribution.actions.0'),
        t('forSuggesstions.treasure_monster_distribution.actions.1'),
        t('forSuggesstions.treasure_monster_distribution.actions.2'),
        t('forSuggesstions.treasure_monster_distribution.actions.3')
      ],
      accessibility: [
        t('forSuggesstions.accessibility.actions.0'),
        t('forSuggesstions.accessibility.actions.1'),
        t('forSuggesstions.accessibility.actions.2'),
        t('forSuggesstions.accessibility.actions.3')
      ],
      path_diversity: [
        t('forSuggesstions.path_diversity.actions.0'),
        t('forSuggesstions.path_diversity.actions.1'),
        t('forSuggesstions.path_diversity.actions.2'),
        t('forSuggesstions.path_diversity.actions.3')
      ],
      loop_ratio: [
        t('forSuggesstions.loop_ratio.actions.0'),
        t('forSuggesstions.loop_ratio.actions.1'),
        t('forSuggesstions.loop_ratio.actions.2'),
        t('forSuggesstions.loop_ratio.actions.3')
      ],
      degree_variance: [
        t('forSuggesstions.degree_variance.actions.0'),
        t('forSuggesstions.degree_variance.actions.1'),
        t('forSuggesstions.degree_variance.actions.2'),
        t('forSuggesstions.degree_variance.actions.3')
      ]
    }
    return actionsMap[metric] || []
  }

  // 死胡同比例建议
  if (props.scores.dead_end_ratio?.score < 0.6) {
    suggestions.push({
      title: t('forSuggesstions.dead_end_ratio.title'),
      description: t('forSuggesstions.dead_end_ratio.description'),
      priority: props.scores.dead_end_ratio.score < 0.3 ? 'high' : 'medium',
      category: t('forSuggesstions.dead_end_ratio.category'),
      metric: 'dead_end_ratio',
      currentScore: props.scores.dead_end_ratio.score,
      targetScore: 0.7,
      actions: getActions('dead_end_ratio'),
      expectedImprovement: t('forSuggesstions.dead_end_ratio.expected')
    })
  }

  // 几何平衡建议
  if (props.scores.geometric_balance?.score < 0.65) {
    suggestions.push({
      title: t('forSuggesstions.geometric_balance.title'),
      description: t('forSuggesstions.geometric_balance.description'),
      priority: props.scores.geometric_balance.score < 0.4 ? 'high' : 'medium',
      category: t('forSuggesstions.geometric_balance.category'),
      metric: 'geometric_balance',
      currentScore: props.scores.geometric_balance.score,
      targetScore: 0.75,
      actions: getActions('geometric_balance'),
      expectedImprovement: t('forSuggesstions.geometric_balance.expected')
    })
  }

  // 宝藏怪物分布建议
  if (props.scores.treasure_monster_distribution?.score < 0.6) {
    suggestions.push({
      title: t('forSuggesstions.treasure_monster_distribution.title'),
      description: t('forSuggesstions.treasure_monster_distribution.description'),
      priority: 'high',
      category: t('forSuggesstions.treasure_monster_distribution.category'),
      metric: 'treasure_monster_distribution',
      currentScore: props.scores.treasure_monster_distribution.score,
      targetScore: 0.8,
      actions: getActions('treasure_monster_distribution'),
      expectedImprovement: t('forSuggesstions.treasure_monster_distribution.expected')
    })
  }

  // 可达性建议
  if (props.scores.accessibility?.score < 0.7) {
    suggestions.push({
      title: t('forSuggesstions.accessibility.title'),
      description: t('forSuggesstions.accessibility.description'),
      priority: 'high',
      category: t('forSuggesstions.accessibility.category'),
      metric: 'accessibility',
      currentScore: props.scores.accessibility.score,
      targetScore: 0.85,
      actions: getActions('accessibility'),
      expectedImprovement: t('forSuggesstions.accessibility.expected')
    })
  }

  // 路径多样性建议
  if (props.scores.path_diversity?.score < 0.5) {
    suggestions.push({
      title: t('forSuggesstions.path_diversity.title'),
      description: t('forSuggesstions.path_diversity.description'),
      priority: 'medium',
      category: t('forSuggesstions.path_diversity.category'),
      metric: 'path_diversity',
      currentScore: props.scores.path_diversity.score,
      targetScore: 0.7,
      actions: getActions('path_diversity'),
      expectedImprovement: t('forSuggesstions.path_diversity.expected')
    })
  }

  // 环路比例建议
  if (props.scores.loop_ratio?.score < 0.4) {
    suggestions.push({
      title: t('forSuggesstions.loop_ratio.title'),
      description: t('forSuggesstions.loop_ratio.description'),
      priority: 'medium',
      category: t('forSuggesstions.loop_ratio.category'),
      metric: 'loop_ratio',
      currentScore: props.scores.loop_ratio.score,
      targetScore: 0.6,
      actions: getActions('loop_ratio'),
      expectedImprovement: t('forSuggesstions.loop_ratio.expected')
    })
  }

  // 度方差建议
  if (props.scores.degree_variance?.score < 0.6) {
    suggestions.push({
      title: t('forSuggesstions.degree_variance.title'),
      description: t('forSuggesstions.degree_variance.description'),
      priority: 'low',
      category: t('forSuggesstions.degree_variance.category'),
      metric: 'degree_variance',
      currentScore: props.scores.degree_variance.score,
      targetScore: 0.7,
      actions: getActions('degree_variance'),
      expectedImprovement: t('forSuggesstions.degree_variance.expected')
    })
  }

  // 按优先级排序
  return suggestions.sort((a, b) => {
    const priorityOrder = { high: 3, medium: 2, low: 1 }
    return priorityOrder[b.priority] - priorityOrder[a.priority]
  })
})

const getPriorityColor = (priority: string): string => {
  const colors: { [key: string]: string } = {
    high: 'bg-red-500',
    medium: 'bg-yellow-500', 
    low: 'bg-blue-500'
  }
  return colors[priority] || 'bg-gray-500'
}

const getPriorityBadgeClass = (priority: string): string => {
  const classes: { [key: string]: string } = {
    high: 'bg-red-100 text-red-800',
    medium: 'bg-yellow-100 text-yellow-800',
    low: 'bg-blue-100 text-blue-800'
  }
  return classes[priority] || 'bg-gray-100 text-gray-800'
}

const getPriorityText = (priority: string): string => {
  const texts: { [key: string]: string } = {
    high: t('forSuggesstions.high'),
    medium: t('forSuggesstions.medium'),
    low: t('forSuggesstions.low')
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