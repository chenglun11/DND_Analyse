<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h3 class="text-lg font-semibold text-gray-800">{{ t('metricSelector.title') }}</h3>
      <div class="flex gap-2">
        <button 
          @click="selectAll"
          class="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors"
        >
          {{ t('metricSelector.selectAll') }}
        </button>
        <button 
          @click="deselectAll"
          class="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
        >
          {{ t('metricSelector.deselectAll') }}
        </button>
      </div>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
      <div 
        v-for="metric in availableMetrics" 
        :key="metric.key"
        class="relative"
      >
        <label 
          :for="`metric-${metric.key}`"
          class="flex items-start gap-3 p-3 border border-gray-200 rounded-lg cursor-pointer transition-all duration-200 hover:border-blue-300 hover:bg-blue-50"
          :class="{ 'border-blue-500 bg-blue-50': selectedMetrics.includes(metric.key) }"
        >
          <input
            :id="`metric-${metric.key}`"
            v-model="selectedMetrics"
            :value="metric.key"
            type="checkbox"
            class="mt-1 w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2"
          />
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span class="font-medium text-gray-900 text-sm">{{ metric.name }}</span>
              <span 
                v-if="metric.category"
                class="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded-full"
              >
                {{ metric.category }}
              </span>
            </div>
            <p class="text-xs text-gray-600 mt-1">{{ metric.description }}</p>
          </div>
        </label>
      </div>
    </div>
    
    <div class="flex items-center justify-between pt-2 border-t border-gray-200">
      <span class="text-sm text-gray-600">
        {{ t('metricSelector.selectedCount', { count: selectedMetrics.length, total: availableMetrics.length }) }}
      </span>
      <div class="flex gap-2">
        <button 
          @click="applySelection"
          :disabled="selectedMetrics.length === 0"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors text-sm font-medium"
        >
          {{ t('metricSelector.apply') }}
        </button>
        <button 
          @click="resetSelection"
          class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors text-sm font-medium"
        >
          {{ t('metricSelector.reset') }}
        </button>
      </div>
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
}

interface Emits {
  (e: 'update:modelValue', value: string[]): void
  (e: 'change', value: string[]): void
}

const props = withDefaults(defineProps<Props>(), {
  initialSelection: () => [],
  disabled: false
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
}

// 全不选
const deselectAll = () => {
  selectedMetrics.value = []
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
</style>