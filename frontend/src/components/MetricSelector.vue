<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h3 class="text-lg font-semibold text-gray-800">{{ t('metricSelector.title') }}</h3>
      <div class="flex gap-2">
        <button 
          @click="selectAll"
          class="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-all duration-300 hover:shadow-sm transform hover:-translate-y-0.5"
        >
          {{ t('metricSelector.selectAll') }}
        </button>
      </div>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
      <div 
        v-for="(metric, index) in availableMetrics" 
        :key="metric.key"
        class="relative animate-fade-in"
        :style="{ animationDelay: `${index * 0.05}s` }"
      >
        <label 
          :for="`metric-${metric.key}`"
          class="flex items-start gap-3 p-3 border border-gray-200 rounded-lg cursor-pointer transition-all duration-300 hover:border-blue-300 hover:bg-blue-50 hover:shadow-md hover:-translate-y-0.5"
          :class="{ 
            'border-blue-500 bg-blue-50 shadow-md': selectedMetrics.includes(metric.key) && !isMetricDisabled(metric.key),
            'border-gray-300 bg-gray-100 cursor-not-allowed opacity-60': isMetricDisabled(metric.key)
          }"
        >
          <input
            :id="`metric-${metric.key}`"
            v-model="selectedMetrics"
            :value="metric.key"
            type="checkbox"
            :disabled="isMetricDisabled(metric.key)"
            class="mt-1 w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            @click.stop="handleCheckboxClick(metric.key, $event)"
          />
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span class="font-medium text-gray-900 text-sm" :class="{ 'text-gray-500': isMetricDisabled(metric.key) }">{{ metric.name }}</span>
              <span 
                v-if="metric.category"
                class="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded-full transition-all duration-200"
                :class="{ 'bg-gray-200 text-gray-400': isMetricDisabled(metric.key) }"
              >
                {{ metric.category }}
              </span>
              <span v-if="isMetricDisabled(metric.key)" class="px-2 py-0.5 text-xs bg-red-100 text-red-600 rounded-full">
                已禁用
              </span>
            </div>
            <p class="text-xs text-gray-600 mt-1" :class="{ 'text-gray-400': isMetricDisabled(metric.key) }">{{ metric.description }}</p>
            <p v-if="!isMetricDisabled(metric.key)" class="text-xs text-gray-500 mt-1">Ctrl+点击禁用</p>
          </div>
          <!-- 选中状态指示器 -->
          <div v-if="selectedMetrics.includes(metric.key) && !isMetricDisabled(metric.key)" 
               class="absolute top-2 right-2 w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center animate-scale-in">
            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
          </div>
          <!-- 禁用状态指示器 -->
          <div v-if="isMetricDisabled(metric.key)" 
               class="absolute top-2 right-2 w-6 h-6 bg-gray-400 rounded-full flex items-center justify-center">
            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </div>
        </label>
      </div>
    </div>
    
    <div class="flex items-center justify-between pt-2 border-t border-gray-200">
      <span class="text-sm text-gray-600">
        {{ t('metricSelector.selectedCount', { count: selectedMetrics.length, total: availableMetrics.length }) }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'

interface MetricConfig {
  key: string
  name: string
  description: string
  category?: string
  defaultEnabled: boolean
}

interface Props {
  initialSelection?: string[]
  disabled?: boolean
  disabledMetrics?: string[]
}

interface Emits {
  (e: 'update:modelValue', value: string[]): void
  (e: 'change', value: string[]): void
  (e: 'toggleDisabled', metricKey: string): void
}

const props = withDefaults(defineProps<Props>(), {
  initialSelection: () => [],
  disabled: false,
  disabledMetrics: () => []
})

const emit = defineEmits<Emits>()
const { t } = useI18n()

// 可用的评估指标配置
const availableMetrics: MetricConfig[] = [
  {
    key: 'dead_end_ratio',
    name: t('metrics.dead_end_ratio'),
    description: t('metricDescriptions.dead_end_ratio.description'),
    category: t('metricCategories.layout'),
    defaultEnabled: true
  },
  {
    key: 'geometric_balance',
    name: t('metrics.geometric_balance'),
    description: t('metricDescriptions.geometric_balance.description'),
    category: t('metricCategories.layout'),
    defaultEnabled: true
  },
  {
    key: 'treasure_monster_distribution',
    name: t('metrics.treasure_monster_distribution'),
    description: t('metricDescriptions.treasure_monster_distribution.description'),
    category: t('metricCategories.gameplay'),
    defaultEnabled: true
  },
  {
    key: 'accessibility',
    name: t('metrics.accessibility'),
    description: t('metricDescriptions.accessibility.description'),
    category: t('metricCategories.navigation'),
    defaultEnabled: true
  },
  {
    key: 'path_diversity',
    name: t('metrics.path_diversity'),
    description: t('metricDescriptions.path_diversity.description'),
    category: t('metricCategories.navigation'),
    defaultEnabled: true
  },
  {
    key: 'loop_ratio',
    name: t('metrics.loop_ratio'),
    description: t('metricDescriptions.loop_ratio.description'),
    category: t('metricCategories.layout'),
    defaultEnabled: true
  },

  {
    key: 'degree_variance',
    name: t('metrics.degree_variance'),
    description: t('metricDescriptions.degree_variance.description'),
    category: t('metricCategories.layout'),
    defaultEnabled: true
  },
  {
    key: 'door_distribution',
    name: t('metrics.door_distribution'),
    description: t('metricDescriptions.door_distribution.description'),
    category: t('metricCategories.layout'),
    defaultEnabled: true
  },
  {
    key: 'key_path_length',
    name: t('metrics.key_path_length'),
    description: t('metricDescriptions.key_path_length.description'),
    category: t('metricCategories.navigation'),
    defaultEnabled: true
  }
]

const selectedMetrics = ref<string[]>([])

// 初始化选中状态
const initializeSelection = () => {
  if (props.initialSelection.length > 0) {
    selectedMetrics.value = [...props.initialSelection]
    console.log('使用外部传入的指标选择:', selectedMetrics.value)
  } else {
    // 默认选择所有9个指标
    const defaultMetrics = availableMetrics.map(metric => metric.key)
    selectedMetrics.value = defaultMetrics
    console.log('使用默认指标选择（全部9个）:', selectedMetrics.value)
  }
}

// 全选
const selectAll = () => {
  selectedMetrics.value = availableMetrics.map(metric => metric.key)
  applySelection()
}

// 全不选(保留一个默认指标)
const deselectAll = () => {
  // 至少保留一个默认指标用于分析
  selectedMetrics.value = ['accessibility'] // 保留可达性指标作为默认
  applySelection()
}

// 检查指标是否被禁用
const isMetricDisabled = (metricKey: string): boolean => {
  return props.disabledMetrics.includes(metricKey)
}

// 切换指标禁用状态
const toggleMetricDisabled = (metricKey: string) => {
  emit('toggleDisabled', metricKey)
}

// 处理复选框点击
const handleCheckboxClick = (metricKey: string, event: MouseEvent) => {
  // 如果指标已禁用，则启用它
  if (isMetricDisabled(metricKey)) {
    toggleMetricDisabled(metricKey)
    return
  }

  // 如果按住 Ctrl 键点击，则禁用指标
  if (event.ctrlKey) {
    toggleMetricDisabled(metricKey)
    return
  }

  // 正常的选择/取消选择逻辑
  const checkbox = event.target as HTMLInputElement
  if (checkbox.checked) {
    // 选中时，如果已选中，则不重复选中
    if (!selectedMetrics.value.includes(metricKey)) {
      selectedMetrics.value.push(metricKey)
    }
  } else {
    // 取消选中时，从选中列表中移除
    selectedMetrics.value = selectedMetrics.value.filter(key => key !== metricKey)
  }
  applySelection()
}

// 应用选择
const applySelection = () => {
  emit('update:modelValue', selectedMetrics.value)
  emit('change', selectedMetrics.value)
}

// 重置选择
const resetSelection = () => {
  initializeSelection()
}

// 监听选中状态变化
watch(selectedMetrics, (newValue) => {
  emit('update:modelValue', newValue)
}, { deep: true })

// 监听外部props变化
watch(() => props.initialSelection, (newValue) => {
  if (newValue && newValue.length > 0) {
    selectedMetrics.value = [...newValue]
  } else {
    // 如果外部传入空数组，使用默认配置
    initializeSelection()
  }
}, { deep: true, immediate: true })

onMounted(() => {
  // 确保初始化
  if (selectedMetrics.value.length === 0) {
    initializeSelection()
  }
  

})
</script>

<style scoped>
/* 复选框样式优化 */
input[type="checkbox"]:checked {
  background-color: #3b82f6;
  border-color: #3b82f6;
}

input[type="checkbox"]:focus {
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
}

/* 标签悬停效果 */
label:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 选中状态动画 */
label {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 禁用状态 */
label.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

label.disabled:hover {
  transform: none;
  box-shadow: none;
}

/* 淡入动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fadeIn 0.5s ease-out;
}

/* 缩放动画 */
@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.animate-scale-in {
  animation: scaleIn 0.3s ease-out;
}

/* 按钮点击效果 */
button:active {
  transform: scale(0.98);
}

/* 选中状态指示器动画 */
.animate-scale-in {
  animation: scaleIn 0.2s ease-out;
}

/* 复选框选中动画 */
input[type="checkbox"]:checked {
  animation: scaleIn 0.2s ease-out;
}

/* 标签选中状态增强 */
label:has(input:checked) {
  border-color: #3b82f6;
  background-color: #eff6ff;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .grid.grid-cols-1.md\:grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .flex.items-center.justify-between {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .flex.gap-2 {
    justify-content: center;
  }
}
</style>