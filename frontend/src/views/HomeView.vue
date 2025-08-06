<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { DungeonAPI } from '../services/api'
import {
  Dialog,
  DialogPanel,
  DialogTitle,
  TransitionChild,
  TransitionRoot
} from '@headlessui/vue'
import {
  Listbox,
  ListboxButton,
  ListboxOptions,
  ListboxOption
} from '@headlessui/vue'

import {
  Popover,
  PopoverButton,
  PopoverPanel
} from '@headlessui/vue'
import {
  CheckIcon,
  ChevronUpDownIcon,
  XMarkIcon,
  DocumentIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon
} from '@heroicons/vue/24/outline'
import MetricSelector from '../components/MetricSelector.vue'
import { FileIcon, ChartIcon, LightningIcon, SaveIcon, TargetIcon, RefreshIcon } from '../components/icons'

interface AnalysisResult {
  id: string
  name: string
  filename: string
  overallScore: number
  grade: string
  detailedScores: Record<string, { score: number; detail?: any }>
  unifiedData?: any
  fileId?: string
}

const router = useRouter()
const { t } = useI18n()
// TODO: Remove unused t constant later
const fileInput = ref<HTMLInputElement>()
const uploadedFiles = ref<File[]>([])
const isAnalyzing = ref(false)
const analysisResults = ref<AnalysisResult[]>([])

// Headless UI 状态
const showConfirmDialog = ref(false)
const showErrorDialog = ref(false)
const errorMessage = ref('')
const selectedFiles = ref<File[]>([])
const showFileList = ref(false)

const selectedMetrics = ref<string[]>([
  'dead_end_ratio',
  'geometric_balance',
  'treasure_monster_distribution',
  'accessibility',
  'path_diversity',
  'loop_ratio',
  'degree_variance',
  'door_distribution',
  'key_path_length'
])
const showMetricSelector = ref(false)
const availableMetricsCount = 9 // 总可用指标数量

const disabledMetrics = ref<string[]>([])

const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  const files = event.dataTransfer?.files
  if (files) {
    addFiles(Array.from(files))
  }
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files) {
    addFiles(Array.from(target.files))
  }
}

const addFiles = (files: File[]) => {
  const jsonFiles = files.filter(file => file.name.endsWith('.json'))
  const newFiles = jsonFiles.filter(newFile =>
    !uploadedFiles.value.some(existingFile => existingFile.name === newFile.name)
  )
  uploadedFiles.value.push(...newFiles)

  if (newFiles.length !== jsonFiles.length) {
    console.log(`跳过 ${jsonFiles.length - newFiles.length} 个重复文件`)
  }
}

const removeFile = (index: number) => {
  uploadedFiles.value.splice(index, 1)
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Number((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const analyzeAllFiles = async () => {
  if (uploadedFiles.value.length === 0) return

  isAnalyzing.value = true
  analysisResults.value = []

  try {
    console.log(`开始分析 ${uploadedFiles.value.length} 个文件`)
    console.log('选中的指标:', selectedMetrics.value)

    for (let i = 0; i < uploadedFiles.value.length; i++) {
      const file = uploadedFiles.value[i]
      console.log(`分析文件 ${i + 1}/${uploadedFiles.value.length}: ${file.name}`)

      try {
        // 直接调用API，不传递选项参数
        const result = await DungeonAPI.analyzeDungeon(file)

        if (result.success && result.result) {
          // 根据选中的指标过滤详细分数
          const filteredScores: Record<string, { score: number; detail?: any }> = {}
          const originalScores = result.result.scores || {}
          
          // 只保留选中的指标
          for (const metric of selectedMetrics.value) {
            if (originalScores[metric]) {
              filteredScores[metric] = originalScores[metric]
            }
          }
          
          // 重新计算总体分数（基于选中的指标）
          let totalScore = 0
          let validMetricsCount = 0
          
          for (const metric of selectedMetrics.value) {
            if (filteredScores[metric]) {
              totalScore += filteredScores[metric].score
              validMetricsCount += 1
            }
          }
          
          const overallScore = validMetricsCount > 0 ? totalScore / validMetricsCount : 0
          
          // 根据新分数确定等级
          let grade = '未知'
          if (overallScore >= 0.8) grade = '优秀'
          else if (overallScore >= 0.65) grade = '良好'
          else if (overallScore >= 0.5) grade = '一般'
          else if (overallScore >= 0.35) grade = '较差'
          else grade = '很差'

          const analysisResult = {
            id: result.file_id || `file_${i}`,
            name: file.name.replace('.json', ''),
            filename: file.name,
            overallScore: overallScore,
            grade: grade,
            detailedScores: filteredScores,
            unifiedData: result.result.unified_data,
            fileId: result.file_id
          }

          analysisResults.value.push(analysisResult)
          console.log(`${file.name} 分析完成，评分: ${formatScore(analysisResult.overallScore)}`)
          console.log(`使用的指标: ${Object.keys(filteredScores).join(', ')}`)
        } else {
          console.error(`${file.name} 分析失败:`, result.error)
          errorMessage.value = `${file.name} 分析失败: ${result.error}`
          showErrorDialog.value = true
        }
      } catch (error) {
        console.error(`${file.name} 分析出错:`, error)
        errorMessage.value = `${file.name} 分析出错: ${error}`
        showErrorDialog.value = true
      }
    }

    // 保存所有结果到localStorage
    localStorage.setItem('analysisResults', JSON.stringify(analysisResults.value))
    console.log(`批量分析完成，共处理 ${analysisResults.value.length} 个文件`)
    
    // 分析完成后滚动到顶部并添加动画
    await nextTick()
    scrollToTopWithAnimation()
  } catch (error) {
    console.error('批量分析失败:', error)
    errorMessage.value = `批量分析失败: ${error}`
    showErrorDialog.value = true
  } finally {
    isAnalyzing.value = false
  }
}

// 添加滚动到顶部的动画函数
const scrollToTopWithAnimation = () => {
  const scrollContainer = document.querySelector('.min-h-screen')
  if (scrollContainer) {
    scrollContainer.scrollTo({
      top: 0,
      behavior: 'smooth'
    })
  }
}

// 添加指标选择器的交互状态
const metricSelectorState = ref({
  isApplying: false,
  isResetting: false,
  showSuccessMessage: false
})

// 增强的指标选择处理函数
const handleMetricChange = (metrics: string[]) => {
  selectedMetrics.value = metrics
  console.log('选中的指标:', metrics)
  console.log('指标数量:', metrics.length)

  // 保存选中的指标到localStorage
  localStorage.setItem('selectedMetrics', JSON.stringify(metrics))
  
  // 显示成功消息
  metricSelectorState.value.showSuccessMessage = true
  setTimeout(() => {
    metricSelectorState.value.showSuccessMessage = false
  }, 2000)
}

// 应用指标选择的函数
const applyMetricSelection = () => {
  metricSelectorState.value.isApplying = true
  setTimeout(() => {
    metricSelectorState.value.isApplying = false
    // 这里可以添加其他应用逻辑
  }, 1000)
}

// 重置指标选择的函数
const resetMetricSelection = () => {
  metricSelectorState.value.isResetting = true
  setTimeout(() => {
    metricSelectorState.value.isResetting = false
    // 重置为默认选择
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
    localStorage.setItem('selectedMetrics', JSON.stringify(selectedMetrics.value))
  }, 1000)
}

const toggleMetricDisabled = (metricKey: string) => {
  const index = disabledMetrics.value.indexOf(metricKey)
  if (index > -1) {
    // 启用指标
    disabledMetrics.value.splice(index, 1)
    console.log(`已启用指标: ${metricKey}`)
  } else {
    // 禁用指标
    disabledMetrics.value.push(metricKey)
    console.log(`已禁用指标: ${metricKey}`)
  }
  
  // 从选中列表中移除已禁用的指标
  selectedMetrics.value = selectedMetrics.value.filter(metric => 
    !disabledMetrics.value.includes(metric)
  )
  
  // 保存禁用状态到localStorage
  localStorage.setItem('disabledMetrics', JSON.stringify(disabledMetrics.value))
}

const getScoreClass = (score: number): string => {
  if (score >= 0.8) return 'excellent'
  if (score >= 0.65) return 'good'
  if (score >= 0.5) return 'average'
  if (score >= 0.35) return 'poor'
  return 'very-poor'
}

const getGradeClass = (grade: string): string => {
  const gradeMap: Record<string, string> = {
    '优秀': 'excellent',
    '良好': 'good',
    '一般': 'average',
    '较差': 'poor',
    '未知': 'unknown'
  }
  return gradeMap[grade] || 'unknown'
}

const viewDetails = (result: AnalysisResult) => {
  console.log('查看详情:', result)

  // 保存当前结果到localStorage
  localStorage.setItem('currentAnalysisResult', JSON.stringify(result))

  // 检查文件ID是否存在
  if (!result.fileId) {
    console.warn('文件ID不存在，尝试使用ID字段:', result.id)
  }

  // 导航到详情页面
  router.push({
    name: 'detail',
    params: {
      name: result.name,
      fileId: result.fileId || result.id,
      filename: result.filename || result.name
    }
  }).then(() => {
    console.log('路由跳转成功')
  }).catch((error) => {
    console.error('路由跳转失败:', error)
  })
}

const viewMultipleDetails = () => {
  console.log('查看多个详情')
  console.log('分析结果数量:', analysisResults.value.length)
  console.log('分析结果:', analysisResults.value)

  // 保存所有结果到localStorage
  localStorage.setItem('analysisResults', JSON.stringify(analysisResults.value))

  // 构建路由参数
  const names = analysisResults.value.map(r => r.name).join(',')
  console.log('路由参数 names:', names)

  // 跳转到DetailView的多详情模式
  router.push({
    name: 'detail-multi',
    params: {
      names: names
    }
  }).then(() => {
    console.log('路由跳转成功')
  }).catch((error) => {
    console.error('路由跳转失败:', error)
  })
}

const clearResults = () => {
  showConfirmDialog.value = true
}

const confirmClearResults = () => {
  analysisResults.value = []
  localStorage.removeItem('analysisResults')
  console.log('已清除所有分析结果')
  showConfirmDialog.value = false
}

const exportResult = (result: AnalysisResult) => {
  console.log('导出报告:', result)

  // 创建详细的报告数据
  const reportData = {
    dungeon_name: result.name,
    analysis_date: new Date().toISOString(),
    overall_score: result.overallScore,
    grade: result.grade,
    detailed_scores: result.detailedScores,
    unified_data: result.unifiedData,
    recommendations: generateRecommendations(result.detailedScores),
    summary: generateSummary(result)
  }

  // 转换为JSON格式
  const data = JSON.stringify(reportData, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${result.name}_analysis_report_${new Date().toISOString().slice(0, 10)}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  console.log('已导出分析报告:', result.name)
}

const exportAllResults = () => {
  console.log('导出所有分析结果')

  // 创建批量报告数据
  const batchReportData = {
    analysis_date: new Date().toISOString(),
    total_files: analysisResults.value.length,
    results: analysisResults.value.map(result => ({
      dungeon_name: result.name,
      filename: result.filename,
      overall_score: result.overallScore,
      grade: result.grade,
      detailed_scores: result.detailedScores,
      recommendations: generateRecommendations(result.detailedScores),
      summary: generateSummary(result)
    })),
    summary: {
      average_score: analysisResults.value.reduce((sum, r) => sum + r.overallScore, 0) / analysisResults.value.length,
      total_files: analysisResults.value.length,
      excellent_count: analysisResults.value.filter(r => r.overallScore >= 0.8).length,
      needs_improvement_count: analysisResults.value.filter(r => r.overallScore < 0.5).length
    }
  }

  // 转换为JSON格式
  const data = JSON.stringify(batchReportData, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `batch_analysis_report_${new Date().toISOString().slice(0, 10)}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  console.log('已导出批量分析报告')
}

// 生成改进建议
const generateRecommendations = (scores: Record<string, { score: number; detail?: any }>) => {
  const recommendations: string[] = []

  if (scores.dead_end_ratio?.score < 0.5) {
    recommendations.push('减少死胡同比例，增加环路连接以提高探索体验')
  }

  if (scores.geometric_balance?.score < 0.7) {
    recommendations.push('优化几何平衡，改善空间布局')
  }

  if (scores.treasure_monster_distribution?.score < 0.5) {
    recommendations.push('优化宝藏和怪物分布，提供更好的游戏体验')
  }

  if (scores.accessibility?.score < 0.7) {
    recommendations.push('改善可达性，优化路径设计')
  }

  if (scores.path_diversity?.score < 0.5) {
    recommendations.push('增加路径多样性，提供不同的探索路径')
  }

  if (scores.loop_ratio?.score < 0.3) {
    recommendations.push('增加环路比例，提高地图的探索性')
  }

  return recommendations
}

// 格式化分数显示
const formatScore = (score: number): string => {
  if (score === 0) return '0.00'
  if (score < 0.01) return '< 0.01'
  if (score >= 1) return '1.00'
  // 限制小数位数为3位，避免超长小数
  return Number(score.toFixed(3)).toString()
}

// 生成总结
const generateSummary = (result: AnalysisResult) => {
  const score = result.overallScore
  let grade = 'F'
  let description = '需要大幅改进'

  if (score >= 0.8) {
    grade = 'A'
    description = '优秀的地下城设计'
  } else if (score >= 0.65) {
    grade = 'B'
    description = '良好的地下城设计'
  } else if (score >= 0.5) {
    grade = 'C'
    description = '一般的地下城设计'
  } else if (score >= 0.35) {
    grade = 'D'
    description = '需要改进的地下城设计'
  }

  return {
    grade,
    description,
    overall_score: score
  }
}

onMounted(async () => {
  console.log('HomeView mounted')
  console.log('Headless UI components loaded:', {
    Dialog: !!Dialog,
    Listbox: !!Listbox,
    Popover: !!Popover
  })

  // 不自动恢复分析结果，只有在用户上传文件并分析后才显示
  // 这样可以避免打开页面就看到旧的分析结果
  console.log('不自动恢复分析结果，等待用户上传文件')

  // 尝试从localStorage恢复选中的指标
  const savedMetrics = localStorage.getItem('selectedMetrics')
  if (savedMetrics) {
    try {
      const parsedMetrics = JSON.parse(savedMetrics)
      if (parsedMetrics && parsedMetrics.length > 0) {
        selectedMetrics.value = parsedMetrics
        console.log(`从localStorage恢复了选中的指标:`, selectedMetrics.value)
      }
    } catch (error) {
      console.error('恢复指标选择失败:', error)
    }
  }

  // 确保至少有默认指标被选中
  if (selectedMetrics.value.length === 0) {
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
    console.log('使用默认指标配置（全部9个）:', selectedMetrics.value)
  } else {
    console.log('使用已保存的指标配置:', selectedMetrics.value)
  }

  console.log('HomeView最终指标配置:', selectedMetrics.value)
  console.log('HomeView最终指标数量:', selectedMetrics.value.length)
})
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-[#f0f8ff] py-4 sm:py-6 lg:py-8 px-3 sm:px-4 lg:px-6">
    <div class="w-full max-w-full mx-auto space-y-4 sm:space-y-6 lg:space-y-8">
      <!-- 页面标题 - 统一间距 -->
      <div class="text-center mb-6 sm:mb-8">
        <div class="inline-flex items-center gap-3 sm:gap-4 mb-3 sm:mb-4">
          <div class="w-10 h-10 sm:w-12 sm:h-12 bg-[#2892D7] rounded-full flex items-center justify-center shadow-lg">
            <span class="text-white text-xl sm:text-2xl">🏰</span>
          </div>
          <h1 class="text-2xl sm:text-3xl lg:text-4xl font-bold text-[#173753]">
            {{ t('app.title') }}
          </h1>
        </div>
        <p class="text-slate-600 text-sm sm:text-base lg:text-lg max-w-2xl sm:max-w-3xl mx-auto leading-relaxed">{{ t('app.subtitle') }}</p>
      </div>
      
      <!-- 主要内容区域 - 统一高度和间距 -->
      <div v-if="analysisResults.length === 0" class="flex justify-center items-start">
        <!-- 居中显示的文件上传区域 -->
        <div class="w-full max-w-4xl space-y-4 sm:space-y-6 lg:space-y-8">
          <!-- 文件上传区域 - 统一高度 -->
          <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-4 sm:p-8 min-h-[300px] sm:min-h-[400px] flex flex-col justify-center">
            <div 
              class="border-2 border-dashed border-slate-300 bg-slate-50 rounded-lg p-6 sm:p-12 text-center hover:border-[#2892D7] hover:bg-slate-100 transition-all duration-200 cursor-pointer flex-1 flex flex-col justify-center"
              @drop="handleDrop" 
              @dragover.prevent 
              @dragenter.prevent
              @click="fileInput?.click()"
            >
              <input
                ref="fileInput"
                type="file"
                accept=".json"
                multiple
                @change="handleFileSelect"
                class="hidden"
              />
              
              <div class="flex flex-col items-center gap-4 sm:gap-6">
                <div class="w-16 h-16 sm:w-20 sm:h-20 bg-[#2892D7] rounded-full flex items-center justify-center">
                  <span class="text-white text-2xl sm:text-3xl">📁</span>
                </div>
                
                <div class="space-y-2 sm:space-y-3">
                  <h3 class="text-lg sm:text-xl font-semibold text-slate-800">{{ t('home.dragAndDrop') }}</h3>
                  <p class="text-slate-600 text-sm sm:text-base">{{ t('home.supportedFormats') }}</p>
                </div>
                
                <button 
                  class="bg-[#2892D7] text-white px-6 sm:px-8 py-3 sm:py-4 rounded-lg font-medium hover:bg-[#1D70A2] transition-colors text-base sm:text-lg"
                  @click.stop="fileInput?.click()"
                >
                  {{ t('home.selectFiles') }}
                </button>
              </div>
            </div>
          </div>
          
          <!-- 已上传文件列表 - 统一高度 -->
          <div v-if="uploadedFiles.length > 0" class="bg-white rounded-xl shadow-sm border border-slate-200 p-4 sm:p-6 min-h-[120px] sm:min-h-[160px] lg:min-h-[200px]">
            <div class="flex justify-between items-center mb-3 sm:mb-4">
              <h3 class="text-sm sm:text-base font-semibold text-slate-800">{{ t('home.uploadedFiles') }} ({{ uploadedFiles.length }})</h3>
              <button 
                @click="uploadedFiles = []" 
                class="text-red-500 hover:text-red-700 text-xs sm:text-sm font-medium"
                :disabled="isAnalyzing"
              >
                {{ t('common.clear') }}
              </button>
            </div>
            <div class="space-y-2 sm:space-y-3 max-h-24 sm:max-h-32 lg:max-h-48 overflow-y-auto">
              <div v-for="(file, index) in uploadedFiles" :key="file.name" 
                   class="flex justify-between items-center p-2 sm:p-3 lg:p-4 bg-slate-50 rounded-lg border border-slate-200">
                <div class="flex items-center gap-2 sm:gap-3 lg:gap-4 flex-1 min-w-0">
                  <DocumentIcon class="w-4 h-4 sm:w-5 sm:h-5 text-[#2892D7]" />
                  <div class="flex flex-col gap-1 flex-1 min-w-0">
                    <span class="font-medium text-slate-800 truncate text-xs sm:text-sm lg:text-base">{{ file.name }}</span>
                    <span class="text-slate-500 text-xs sm:text-sm">{{ formatFileSize(file.size) }}</span>
                  </div>
                </div>
                <button 
                  @click="removeFile(index)" 
                  :disabled="isAnalyzing"
                  class="text-slate-400 hover:text-red-500 transition-colors"
                >
                  <XMarkIcon class="w-4 h-4 sm:w-5 sm:h-5" />
                </button>
              </div>
            </div>
          </div>
          
          <!-- 分析配置 - 统一高度 -->
          <div v-if="uploadedFiles.length > 0" class="bg-white rounded-xl shadow-sm border border-slate-200 p-4 sm:p-6 min-h-[240px] sm:min-h-[280px] lg:min-h-[300px]">
            <div class="mb-3 sm:mb-4">
              <h3 class="text-sm sm:text-base font-semibold text-slate-800">{{ t('home.analysisConfig') }}</h3>
            </div>
            <!-- 指标选择器 -->
            <div class="relative p-3 sm:p-4 bg-slate-50 rounded-lg border border-slate-200 mb-4 sm:mb-6">
              <div class="flex items-center justify-between mb-2 sm:mb-3">
                <span class="text-sm sm:text-base font-medium text-slate-900">{{ t('metricSelector.title') }}</span>
                <button 
                  @click="showMetricSelector = !showMetricSelector"
                  class="px-3 sm:px-4 py-1 sm:py-2 text-xs sm:text-sm bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-colors"
                >
                  {{ showMetricSelector ? t('common.close') : t('common.view') }}
                </button>
              </div>
              <p class="text-xs sm:text-sm text-slate-600 mb-2 sm:mb-3">
                {{ t('metricSelector.selectedCount', { count: selectedMetrics.length, total: availableMetricsCount }) }}
              </p>
              
              <!-- 轻量保存提示(不影响布局) -->
              <div v-if="metricSelectorState.showSuccessMessage" 
                   class="absolute top-2 right-2 px-2 py-1 bg-green-500 text-white text-xs rounded-md shadow-lg animate-fade-in z-10">
                ✓ 已保存
              </div>
              
              <div v-if="showMetricSelector" class="mt-2 sm:mt-3">
                <MetricSelector
                  :initial-selection="selectedMetrics"
                  :disabled-metrics="disabledMetrics"
                  @change="handleMetricChange"
                  @toggle-disabled="toggleMetricDisabled"
                />
              </div>
            </div>
            <!-- 主要分析按钮 -->
            <div class="text-center">
              <button 
                @click="analyzeAllFiles" 
                :disabled="uploadedFiles.length === 0 || isAnalyzing"
                class="relative bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 sm:px-8 py-3 sm:py-4 rounded-xl text-sm sm:text-base font-semibold transition-all duration-300 hover:from-green-700 hover:to-emerald-700 hover:shadow-lg hover:-translate-y-0.5 disabled:from-slate-400 disabled:to-slate-500 disabled:cursor-not-allowed disabled:transform-none w-full"
              >
                <div class="flex items-center justify-center gap-2 sm:gap-3">
                  <span v-if="isAnalyzing" class="w-4 h-4 sm:w-5 sm:h-5 border-2 border-transparent border-t-white rounded-full animate-spin"></span>
                  <span v-else class="text-lg sm:text-xl"></span>
                  <span>{{ isAnalyzing ? t('home.analyzing', { current: analysisResults.length, total: uploadedFiles.length }) : t('home.startAnalysis', { count: uploadedFiles.length }) }}</span>
                </div>
              </button>
              <!-- 分析进度条 -->
              <div v-if="isAnalyzing" class="mt-3 sm:mt-4">
                <div class="bg-slate-200 rounded-full h-2 sm:h-3 overflow-hidden shadow-inner">
                  <div 
                    class="bg-gradient-to-r from-green-500 to-emerald-500 h-full transition-all duration-500 ease-out rounded-full"
                    :style="{ width: `${(analysisResults.length / uploadedFiles.length) * 100}%` }"
                  ></div>
                </div>
                <p class="text-sm sm:text-base text-slate-600 mt-2 sm:mt-3 font-medium">
                  {{ t('home.progress', { completed: analysisResults.length, total: uploadedFiles.length, percentage: Math.round((analysisResults.length / uploadedFiles.length) * 100) }) }}
                </p>
              </div>
              <p v-if="!isAnalyzing" class="text-slate-500 text-sm sm:text-base mt-2 sm:mt-3 flex items-center justify-center gap-2 sm:gap-3">
                <span class="w-2 h-2 sm:w-3 sm:h-3 bg-[#6DAEDB] rounded-full animate-pulse"></span>
                {{ uploadedFiles.length > 0 ? t('home.clickToAnalyze') : t('home.pleaseUploadFirst') }}
              </p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 有分析结果时的左右布局 - 统一高度 -->
      <div v-else class="grid grid-cols-1 xl:grid-cols-5 gap-4 sm:gap-6 lg:gap-8">
        <!-- 左侧：文件上传和配置 - 统一高度 -->
        <div class="xl:col-span-2 space-y-4 sm:space-y-6">
          <!-- 文件上传区域 - 统一高度 -->
          <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-4 sm:p-6 min-h-[200px] sm:min-h-[250px] lg:min-h-[300px]">
            <div class="mb-3 sm:mb-4">
              <h3 class="text-sm sm:text-base font-semibold text-slate-800 mb-2 sm:mb-3">文件上传</h3>
              <div 
                class="border-2 border-dashed border-slate-300 bg-slate-50 rounded-lg p-3 sm:p-4 lg:p-8 text-center hover:border-[#2892D7] hover:bg-slate-100 transition-all duration-200 cursor-pointer flex-1 flex flex-col justify-center"
                @drop="handleDrop" 
                @dragover.prevent 
                @dragenter.prevent
                @click="fileInput?.click()"
              >
                <input
                  ref="fileInput"
                  type="file"
                  accept=".json"
                  multiple
                  @change="handleFileSelect"
                  class="hidden"
                />
                
                <div class="flex flex-col items-center gap-2 sm:gap-3 lg:gap-4">
                  <div class="w-10 h-10 sm:w-12 sm:h-12 lg:w-16 lg:h-16 bg-[#2892D7] rounded-full flex items-center justify-center">
                    <span class="text-white text-lg sm:text-xl lg:text-2xl">📁</span>
                  </div>
                  
                  <div class="space-y-1 sm:space-y-2">
                    <p class="text-slate-700 text-xs sm:text-sm lg:text-base font-medium">{{ t('home.dragAndDrop') }}</p>
                    <p class="text-slate-500 text-xs sm:text-sm">{{ t('home.supportedFormats') }}</p>
                  </div>
                  
                  <button 
                    class="bg-[#2892D7] text-white px-3 sm:px-4 lg:px-6 py-2 sm:py-3 rounded-lg text-xs sm:text-sm lg:text-base font-medium hover:bg-[#1D70A2] transition-colors"
                    @click.stop="fileInput?.click()"
                  >
                    {{ t('home.selectFiles') }}
                  </button>
                </div>
              </div>
              <div v-if="uploadedFiles.length === 0" class="text-center mt-2 sm:mt-3">
                <p class="text-slate-500 text-xs sm:text-sm">{{ t('home.uploadPrompt') }}</p>
              </div>
            </div>
          </div>
          
          <!-- 已上传文件列表 - 统一高度 -->
          <div v-if="uploadedFiles.length > 0" class="bg-white rounded-xl shadow-sm border border-slate-200 p-4 sm:p-6 min-h-[120px] sm:min-h-[160px] lg:min-h-[200px]">
            <div class="flex justify-between items-center mb-3 sm:mb-4">
              <h3 class="text-sm sm:text-base font-semibold text-slate-800">{{ t('home.uploadedFiles') }} ({{ uploadedFiles.length }})</h3>
              <button 
                @click="uploadedFiles = []" 
                class="text-red-500 hover:text-red-700 text-xs sm:text-sm font-medium"
                :disabled="isAnalyzing"
              >
                {{ t('common.clear') }}
              </button>
            </div>
            <div class="space-y-2 sm:space-y-3 max-h-24 sm:max-h-32 lg:max-h-48 overflow-y-auto">
              <div v-for="(file, index) in uploadedFiles" :key="file.name" 
                   class="flex justify-between items-center p-2 sm:p-3 lg:p-4 bg-slate-50 rounded-lg border border-slate-200">
                <div class="flex items-center gap-2 sm:gap-3 lg:gap-4 flex-1 min-w-0">
                  <DocumentIcon class="w-4 h-4 sm:w-5 sm:h-5 text-[#2892D7]" />
                  <div class="flex flex-col gap-1 flex-1 min-w-0">
                    <span class="font-medium text-slate-800 truncate text-xs sm:text-sm lg:text-base">{{ file.name }}</span>
                    <span class="text-slate-500 text-xs sm:text-sm">{{ formatFileSize(file.size) }}</span>
                  </div>
                </div>
                <button 
                  @click="removeFile(index)" 
                  :disabled="isAnalyzing"
                  class="text-slate-400 hover:text-red-500 transition-colors"
                >
                  <XMarkIcon class="w-4 h-4 sm:w-5 sm:h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 右侧：分析结果 - 统一高度 -->
        <div class="xl:col-span-3">
          <!-- 分析结果区域 -->
          <div v-if="analysisResults.length > 0" 
               class="bg-white/90 backdrop-blur-xl rounded-xl shadow-xl border border-white/30 p-4 sm:p-6 lg:p-8 min-h-[300px] sm:min-h-[400px] lg:min-h-[500px] animate-slide-in-from-top">
            <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-3 sm:gap-4 mb-4 sm:mb-6 lg:mb-8">
              <div class="flex items-center gap-2 sm:gap-3 lg:gap-4">
                <div class="w-6 h-6 sm:w-8 sm:h-8 lg:w-10 lg:h-10 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full flex items-center justify-center shadow-lg">
                  <span class="text-white text-xs sm:text-sm lg:text-lg"></span>
                </div>
                <div>
                  <h2 class="text-base sm:text-lg lg:text-xl font-bold text-gray-800">
                    {{ t('home.analysisResults') }}
                  </h2>
                  <p class="text-xs sm:text-sm lg:text-base text-gray-600">共 {{ analysisResults.length }} 个分析结果</p>
                </div>
              </div>
              <!-- 快速导航区域 - 响应式布局 -->
              <div class="flex flex-col sm:flex-row gap-1 sm:gap-2 lg:gap-3 w-full lg:w-auto">
                <button
                  @click="viewMultipleDetails"
                  class="group relative inline-flex items-center justify-center gap-1 sm:gap-2 px-2 sm:px-3 lg:px-6 py-1.5 sm:py-2 lg:py-3 bg-gradient-to-r from-[#2892D7] to-[#1D70A2] text-white rounded-md sm:rounded-lg lg:rounded-xl hover:from-[#1D70A2] hover:to-[#173753] transition-all duration-300 text-xs sm:text-sm lg:text-base font-semibold shadow-md hover:shadow-lg hover:-translate-y-0.5 transform overflow-hidden"
                >
                  <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700"></div>
                  <span class="relative z-10">查看细节</span>
                </button>
                <button
                  @click="exportAllResults"
                  class="group relative inline-flex items-center justify-center gap-1 sm:gap-2 px-2 sm:px-3 lg:px-6 py-1.5 sm:py-2 lg:py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-md sm:rounded-lg lg:rounded-xl hover:from-green-600 hover:to-emerald-700 transition-all duration-300 text-xs sm:text-sm lg:text-base font-semibold shadow-md hover:shadow-lg hover:-translate-y-0.5 transform overflow-hidden"
                >
                  <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700"></div>
                  <span class="relative z-10">导出报告</span>
                </button>
                <button
                  @click="clearResults"
                  class="group relative inline-flex items-center justify-center gap-1 sm:gap-2 px-2 sm:px-3 lg:px-6 py-1.5 sm:py-2 lg:py-3 bg-gradient-to-r from-[#2892D7] to-[#1D70A2] text-white rounded-md sm:rounded-lg lg:rounded-xl hover:from-[#1D70A2] hover:to-[#173753] transition-all duration-300 text-xs sm:text-sm lg:text-base font-semibold shadow-md hover:shadow-lg hover:-translate-y-0.5 transform overflow-hidden"
                >
                  <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700"></div>
                  <span class="relative z-10">清空结果</span>
                </button>
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 lg:gap-6">
              <div v-for="(result, index) in analysisResults" :key="result.id" 
                   class="bg-white/95 backdrop-blur-sm rounded-lg sm:rounded-xl p-3 sm:p-4 lg:p-6 shadow-lg border border-gray-200/60 transition-all duration-300 hover:shadow-md group animate-scale-in"
                   :style="{ animationDelay: `${index * 0.1}s` }">
                <!-- 文件图标和分数布局 -->
                <div class="flex items-start justify-between mb-3">
                  <div class="w-8 h-8 sm:w-10 sm:h-10 lg:w-12 lg:h-12 bg-gradient-to-br from-[#2892D7] to-[#1D70A2] rounded-lg lg:rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg">
                    <svg class="w-4 h-4 sm:w-5 sm:h-5 lg:w-6 lg:h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                  </div>
                  <div class="text-center">
                    <div 
                      :class="[
                        'text-lg sm:text-xl lg:text-2xl font-bold py-2 px-3 lg:px-4 rounded-lg text-white shadow-lg transform transition-all duration-300 group-hover:scale-105',
                        getScoreClass(result.overallScore) === 'excellent' ? 'bg-gradient-to-r from-green-500 to-emerald-500' : '',
                        getScoreClass(result.overallScore) === 'good' ? 'bg-gradient-to-r from-[#2892D7] to-[#1D70A2]' : '',
                        getScoreClass(result.overallScore) === 'average' ? 'bg-gradient-to-r from-[#6DAEDB] to-[#2892D7]' : '',
                        getScoreClass(result.overallScore) === 'poor' ? 'bg-gradient-to-r from-[#1D70A2] to-[#173753]' : '',
                        getScoreClass(result.overallScore) === 'very-poor' ? 'bg-gradient-to-r from-[#173753] to-[#1B4353]' : ''
                      ]"
                    >
                      {{ formatScore(result.overallScore) }}
                    </div>
                    <p class="text-xs sm:text-sm text-gray-600 mt-2 font-medium">{{ result.grade }}</p>
                  </div>
                </div>
                
                <!-- 文件名和信息 -->
                <div>
                  <h3 class="text-gray-900 text-sm sm:text-base font-semibold mb-2 truncate" :title="result.filename">
                    {{ result.filename }}
                  </h3>
                  <div class="flex items-center gap-2 text-xs sm:text-sm text-gray-500">
                    <span class="w-1.5 h-1.5 bg-[#6DAEDB] rounded-full"></span>
                    {{ t('home.fileNumber', { current: index + 1, total: analysisResults.length }) }}
                  </div>
                  <div class="text-xs text-gray-400 mt-1">
                    使用上方“查看细节”按钮来查看所有结果
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 弹窗部分保持不变 -->
      <TransitionRoot as="template" :show="showConfirmDialog">
        <Dialog as="div" class="relative z-50" @close="showConfirmDialog = false">
          <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100" leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
            <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity backdrop-blur-sm" />
          </TransitionChild>
          <div class="fixed inset-0 z-10 overflow-y-auto">
            <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
              <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95" enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200" leave-from="opacity-100 translate-y-0 sm:scale-100" leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
                <DialogPanel class="relative transform overflow-hidden rounded-2xl bg-white px-4 pb-4 pt-5 text-left shadow-2xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
                  <div class="sm:flex sm:items-start">
                    <div class="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-blue-100 sm:mx-0 sm:h-10 sm:w-10">
                      <ExclamationTriangleIcon class="h-6 w-6 text-[#2892D7]" aria-hidden="true" />
                    </div>
                    <div class="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left">
                      <DialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900">
                        {{ t('confirm.clearResults') }}
                      </DialogTitle>
                      <div class="mt-2">
                        <p class="text-sm text-gray-500">
                          {{ t('confirm.clearResultsConfirm', { count: analysisResults.length }) }}
                        </p>
                      </div>
                    </div>
                  </div>
                  <div class="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
                    <button
                      type="button"
                      class="inline-flex w-full justify-center rounded-xl bg-[#2892D7] px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-[#1D70A2] sm:ml-3 sm:w-auto transition-all duration-300"
                      @click="confirmClearResults"
                    >
                      {{ t('confirm.clearResults') }}
                    </button>
                    <button
                      type="button"
                      class="mt-3 inline-flex w-full justify-center rounded-xl bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto transition-all duration-300"
                      @click="showConfirmDialog = false"
                    >
                      {{ t('common.cancel') }}
                    </button>
                  </div>
                </DialogPanel>
              </TransitionChild>
            </div>
          </div>
        </Dialog>
      </TransitionRoot>
      <TransitionRoot as="template" :show="showErrorDialog">
        <Dialog as="div" class="relative z-50" @close="showErrorDialog = false">
          <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100" leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
            <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity backdrop-blur-sm" />
          </TransitionChild>
          <div class="fixed inset-0 z-10 overflow-y-auto">
            <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
              <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95" enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200" leave-from="opacity-100 translate-y-0 sm:scale-100" leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
                <DialogPanel class="relative transform overflow-hidden rounded-2xl bg-white px-4 pb-4 pt-5 text-left shadow-2xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
                  <div class="sm:flex sm:items-start">
                    <div class="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-blue-100 sm:mx-0 sm:h-10 sm:w-10">
                      <ExclamationTriangleIcon class="h-6 w-6 text-[#2892D7]" aria-hidden="true" />
                    </div>
                    <div class="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left">
                      <DialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900">
                        {{ t('errors.analysisError') }}
                      </DialogTitle>
                      <div class="mt-2">
                        <p class="text-sm text-gray-500">
                          {{ errorMessage }}
                        </p>
                      </div>
                    </div>
                  </div>
                  <div class="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
                    <button
                      type="button"
                      class="inline-flex w-full justify-center rounded-xl bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 sm:ml-3 sm:w-auto transition-all duration-300"
                      @click="showErrorDialog = false"
                    >
                      确定
                    </button>
                  </div>
                </DialogPanel>
              </TransitionChild>
            </div>
          </div>
        </Dialog>
      </TransitionRoot>
    </div>
  </div>
</template>

<style scoped>
/* 自定义样式 */
.bg-radial-gradient {
  background: radial-gradient(circle at center, rgba(59, 130, 246, 0.1) 0%, transparent 70%);
}

/* 动画效果 */
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
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

/* 滑动动画 */
@keyframes slideInFromTop {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-slide-in-from-top {
  animation: slideInFromTop 0.6s ease-out;
}

/* 缩放动画 */
@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.animate-scale-in {
  animation: scaleIn 0.4s ease-out;
}

/* 悬停效果 */
.group:hover .group-hover\:scale-110 {
  transform: scale(1.1);
}

/* 渐变背景动画 */
@keyframes gradient-shift {
  0% {
    background-position: 0% 50%;
  }

  50% {
    background-position: 100% 50%;
  }

  100% {
    background-position: 0% 50%;
  }
}

.bg-gradient-animated {
  background-size: 200% 200%;
  animation: gradient-shift 3s ease infinite;
}

/* 玻璃态效果 */
.backdrop-blur-xl {
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}

/* 阴影效果 */
.shadow-2xl {
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

/* 按钮点击效果 */
button:active {
  transform: scale(0.98);
}

/* 卡片悬停效果增强 */
.card-hover {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.card-hover:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

/* 渐变文字效果 */
.gradient-text {
  background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 脉冲动画 */
@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }

  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* 淡入动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in {
  animation: fadeIn 0.6s ease-out;
}

/* 滑动动画 */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }

  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.slide-in {
  animation: slideIn 0.5s ease-out;
}

/* 成功消息动画 */
@keyframes successPop {
  0% {
    opacity: 0;
    transform: scale(0.8) translateY(-10px);
  }
  50% {
    transform: scale(1.05) translateY(0);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.success-pop {
  animation: successPop 0.4s ease-out;
}

/* 滚动到顶部动画 */
@keyframes scrollToTop {
  from {
    transform: translateY(0);
  }
  to {
    transform: translateY(-100vh);
  }
}

.scroll-to-top {
  animation: scrollToTop 0.8s ease-in-out;
}

/* 响应式设计优化 */
@media (max-width: 1280px) {
  .grid.grid-cols-1.xl\:grid-cols-5 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
    gap: 1rem;
  }
  
  .xl\:col-span-2 {
    grid-column: span 1 / span 1;
  }
  
  .xl\:col-span-3 {
    grid-column: span 1 / span 1;
  }
  
  .grid.grid-cols-1.sm\:grid-cols-2.lg\:grid-cols-3 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  /* 统一最小高度 */
  .min-h-\[400px\] {
    min-height: 300px;
  }
  
  .min-h-\[500px\] {
    min-height: 350px;
  }
  
  .min-h-\[600px\] {
    min-height: 400px;
  }
  
  .min-h-\[300px\] {
    min-height: 250px;
  }
  
  .min-h-\[250px\] {
    min-height: 200px;
  }
  
  .min-h-\[200px\] {
    min-height: 150px;
  }
  
  .min-h-\[160px\] {
    min-height: 120px;
  }
  
  .min-h-\[280px\] {
    min-height: 220px;
  }
  
  .min-h-\[180px\] {
    min-height: 140px;
  }
}

@media (max-width: 1024px) {
  .text-4xl {
    font-size: 2rem;
    line-height: 2.25rem;
  }

  .text-2xl {
    font-size: 1.5rem;
    line-height: 2rem;
  }

  .text-xl {
    font-size: 1.125rem;
    line-height: 1.5rem;
  }

  .text-lg {
    font-size: 1rem;
    line-height: 1.5rem;
  }

  .px-6 {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }

  .py-4 {
    padding-top: 0.75rem;
    padding-bottom: 0.75rem;
  }
  
  .p-8 {
    padding: 1.5rem;
  }
  
  .p-6 {
    padding: 1rem;
  }
  
  .p-4 {
    padding: 0.75rem;
  }
  
  .gap-8 {
    gap: 1.5rem;
  }
  
  .gap-6 {
    gap: 1rem;
  }
  
  .gap-4 {
    gap: 0.75rem;
  }
  
  .gap-3 {
    gap: 0.5rem;
  }
  
  .space-y-6 {
    margin-top: 1rem;
  }
  
  .space-y-6 > * + * {
    margin-top: 1rem;
  }
  
  .mb-8 {
    margin-bottom: 1.5rem;
  }
  
  .mb-6 {
    margin-bottom: 1rem;
  }
  
  .mb-4 {
    margin-bottom: 0.75rem;
  }
  
  .w-12.h-12 {
    width: 2.5rem;
    height: 2.5rem;
  }
  
  .w-10.h-10 {
    width: 2rem;
    height: 2rem;
  }
  
  .w-8.h-8 {
    width: 1.5rem;
    height: 1.5rem;
  }
  
  .grid.grid-cols-1.sm\:grid-cols-2.lg\:grid-cols-3 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  /* 调整最小高度 */
  .min-h-\[400px\] {
    min-height: 250px;
  }
  
  .min-h-\[500px\] {
    min-height: 300px;
  }
  
  .min-h-\[600px\] {
    min-height: 350px;
  }
  
  .min-h-\[300px\] {
    min-height: 200px;
  }
  
  .min-h-\[250px\] {
    min-height: 180px;
  }
  
  .min-h-\[200px\] {
    min-height: 140px;
  }
  
  .min-h-\[160px\] {
    min-height: 100px;
  }
  
  .min-h-\[280px\] {
    min-height: 200px;
  }
  
  .min-h-\[180px\] {
    min-height: 120px;
  }
}

@media (max-width: 768px) {
  .px-6 {
    padding-left: 0.75rem;
    padding-right: 0.75rem;
  }
  
  .py-4 {
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
  }
  
  .text-xl {
    font-size: 1rem;
    line-height: 1.5rem;
  }
  
  .text-lg {
    font-size: 0.875rem;
    line-height: 1.25rem;
  }
  
  .text-base {
    font-size: 0.75rem;
    line-height: 1.125rem;
  }
  
  .text-sm {
    font-size: 0.75rem;
    line-height: 1.125rem;
  }
  
  .gap-8 {
    gap: 1rem;
  }
  
  .gap-6 {
    gap: 0.75rem;
  }
  
  .gap-4 {
    gap: 0.5rem;
  }
  
  .gap-3 {
    gap: 0.375rem;
  }
  
  .p-8 {
    padding: 1rem;
  }
  
  .p-6 {
    padding: 0.75rem;
  }
  
  .p-4 {
    padding: 0.5rem;
  }
  
  .p-3 {
    padding: 0.375rem;
  }
  
  .mb-8 {
    margin-bottom: 1rem;
  }
  
  .mb-6 {
    margin-bottom: 0.75rem;
  }
  
  .mb-4 {
    margin-bottom: 0.5rem;
  }
  
  .mb-3 {
    margin-bottom: 0.375rem;
  }
  
  .w-12.h-12 {
    width: 2rem;
    height: 2rem;
  }
  
  .w-10.h-10 {
    width: 1.5rem;
    height: 1.5rem;
  }
  
  .w-8.h-8 {
    width: 1.25rem;
    height: 1.25rem;
  }
  
  .grid.grid-cols-1.sm\:grid-cols-2.lg\:grid-cols-3 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .max-h-48 {
    max-height: 8rem;
  }
  
  .max-h-40 {
    max-height: 6rem;
  }
  
  .max-h-32 {
    max-height: 4rem;
  }
  
  /* 调整最小高度 */
  .min-h-\[400px\] {
    min-height: 200px;
  }
  
  .min-h-\[500px\] {
    min-height: 250px;
  }
  
  .min-h-\[600px\] {
    min-height: 300px;
  }
  
  .min-h-\[300px\] {
    min-height: 150px;
  }
  
  .min-h-\[250px\] {
    min-height: 120px;
  }
  
  .min-h-\[200px\] {
    min-height: 100px;
  }
  
  .min-h-\[160px\] {
    min-height: 80px;
  }
  
  .min-h-\[280px\] {
    min-height: 150px;
  }
  
  .min-h-\[180px\] {
    min-height: 100px;
  }
  
  /* 文件上传区域在移动端的优化 */
  .p-12.text-center {
    padding: 1rem;
  }
  
  .p-8.text-center {
    padding: 0.75rem;
  }
  
  .p-6.text-center {
    padding: 0.5rem;
  }
  
  .p-4.text-center {
    padding: 0.375rem;
  }
  
  /* 分析结果卡片在移动端的优化 */
  .hover\:-translate-y-1:hover {
    transform: translateY(0);
  }
  
  .transform.hover\:-translate-y-0\.5:hover {
    transform: translateY(0);
  }
  
  /* 按钮在移动端的优化 */
  .px-8.py-4 {
    padding-left: 1rem;
    padding-right: 1rem;
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
  }
  
  .px-6.py-3 {
    padding-left: 0.75rem;
    padding-right: 0.75rem;
    padding-top: 0.375rem;
    padding-bottom: 0.375rem;
  }
  
  .px-4.py-3 {
    padding-left: 0.5rem;
    padding-right: 0.5rem;
    padding-top: 0.375rem;
    padding-bottom: 0.375rem;
  }
  
  .px-4.py-2 {
    padding-left: 0.5rem;
    padding-right: 0.5rem;
    padding-top: 0.25rem;
    padding-bottom: 0.25rem;
  }
}

@media (max-width: 640px) {
  .text-4xl {
    font-size: 1.5rem;
    line-height: 1.75rem;
  }

  .text-2xl {
    font-size: 1.125rem;
    line-height: 1.5rem;
  }

  .text-xl {
    font-size: 0.875rem;
    line-height: 1.25rem;
  }

  .text-lg {
    font-size: 0.75rem;
    line-height: 1.125rem;
  }

  .px-8 {
    padding-left: 0.75rem;
    padding-right: 0.75rem;
  }

  .p-8 {
    padding: 0.75rem;
  }

  .p-6 {
    padding: 0.5rem;
  }

  .p-4 {
    padding: 0.375rem;
  }

  .p-3 {
    padding: 0.25rem;
  }

  .gap-8 {
    gap: 0.75rem;
  }

  .gap-6 {
    gap: 0.5rem;
  }

  .gap-4 {
    gap: 0.375rem;
  }

  .gap-3 {
    gap: 0.25rem;
  }

  .grid.grid-cols-1.sm\:grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  /* 进一步调整最小高度 */
  .min-h-\[400px\] {
    min-height: 150px;
  }
  
  .min-h-\[500px\] {
    min-height: 200px;
  }
  
  .min-h-\[600px\] {
    min-height: 250px;
  }
  
  .min-h-\[300px\] {
    min-height: 120px;
  }
  
  .min-h-\[250px\] {
    min-height: 100px;
  }
  
  .min-h-\[200px\] {
    min-height: 80px;
  }
  
  .min-h-\[160px\] {
    min-height: 60px;
  }
  
  .min-h-\[280px\] {
    min-height: 120px;
  }
  
  .min-h-\[180px\] {
    min-height: 80px;
  }
  
  /* 图标大小调整 */
  .w-12.h-12 {
    width: 1.5rem;
    height: 1.5rem;
  }
  
  .w-10.h-10 {
    width: 1.25rem;
    height: 1.25rem;
  }
  
  .w-8.h-8 {
    width: 1rem;
    height: 1rem;
  }
  
  /* 按钮内边距调整 */
  .px-8.py-4 {
    padding-left: 0.75rem;
    padding-right: 0.75rem;
    padding-top: 0.375rem;
    padding-bottom: 0.375rem;
  }
  
  .px-6.py-3 {
    padding-left: 0.5rem;
    padding-right: 0.5rem;
    padding-top: 0.25rem;
    padding-bottom: 0.25rem;
  }
  
  .px-4.py-3 {
    padding-left: 0.375rem;
    padding-right: 0.375rem;
    padding-top: 0.25rem;
    padding-bottom: 0.25rem;
  }
  
  .px-4.py-2 {
    padding-left: 0.375rem;
    padding-right: 0.375rem;
    padding-top: 0.125rem;
    padding-bottom: 0.125rem;
  }
}

/* 自定义滚动条 */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.5);
}

/* 按钮悬停效果 */
button:hover {
  transform: translateY(-2px);
}

button:active {
  transform: translateY(0);
}

/* 卡片悬停效果 */
.card-hover {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.card-hover:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

/* 渐变文字效果 */
.gradient-text {
  background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 脉冲动画 */
@keyframes pulse {

  0%,
  100% {
    opacity: 1;
  }

  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* 淡入动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in {
  animation: fadeIn 0.6s ease-out;
}

/* 滑动动画 */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }

  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.slide-in {
  animation: slideIn 0.5s ease-out;
}
</style>

