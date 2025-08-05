<script setup lang="ts">
import { ref, onMounted } from 'vue'
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
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const analyzeAllFiles = async () => {
  if (uploadedFiles.value.length === 0) return

  isAnalyzing.value = true
  analysisResults.value = []

  try {
    console.log(`开始分析 ${uploadedFiles.value.length} 个文件`)

    for (let i = 0; i < uploadedFiles.value.length; i++) {
      const file = uploadedFiles.value[i]
      console.log(`分析文件 ${i + 1}/${uploadedFiles.value.length}: ${file.name}`)

      try {
        const result = await DungeonAPI.analyzeDungeon(file)

        if (result.success && result.result) {
          const analysisResult = {
            id: result.file_id || `file_${i}`,
            name: file.name.replace('.json', ''),
            filename: file.name,
            overallScore: result.result.overall_score || 0,
            grade: result.result.grade || '未知',
            detailedScores: result.result.scores || {},
            unifiedData: result.result.unified_data,
            fileId: result.file_id
          }

          analysisResults.value.push(analysisResult)
          console.log(`✅ ${file.name} 分析完成，评分: ${analysisResult.overallScore.toFixed(2)}`)
        } else {
          console.error(`❌ ${file.name} 分析失败:`, result.error)
          errorMessage.value = `${file.name} 分析失败: ${result.error}`
          showErrorDialog.value = true
        }
      } catch (error) {
        console.error(`❌ ${file.name} 分析出错:`, error)
        errorMessage.value = `${file.name} 分析出错: ${error}`
        showErrorDialog.value = true
      }
    }

    // 保存所有结果到localStorage
    localStorage.setItem('analysisResults', JSON.stringify(analysisResults.value))
    console.log(`✅ 批量分析完成，共处理 ${analysisResults.value.length} 个文件`)
  } catch (error) {
    console.error('❌ 批量分析失败:', error)
    errorMessage.value = `批量分析失败: ${error}`
    showErrorDialog.value = true
  } finally {
    isAnalyzing.value = false
  }
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

const handleMetricChange = (metrics: string[]) => {
  selectedMetrics.value = metrics
  console.log('选中的指标:', metrics)
  console.log('指标数量:', metrics.length)

  // 保存选中的指标到localStorage
  localStorage.setItem('selectedMetrics', JSON.stringify(metrics))
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
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 py-4 px-4">
    <div class="w-full max-w-full mx-auto space-y-4">
      <!-- 页面标题 - 增强视觉效果 -->
      <div class="text-center mb-6">
        <div class="inline-flex items-center gap-3 mb-3">
          <div class="w-10 h-10 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full flex items-center justify-center shadow-lg">
            <span class="text-white text-xl">🏰</span>
          </div>
          <h1 class="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
            {{ t('app.title') }}
          </h1>
        </div>
        <p class="text-slate-600 text-base max-w-2xl mx-auto leading-relaxed">{{ t('app.subtitle') }}</p>
        <div class="mt-4 flex flex-wrap justify-center gap-2">
          <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 whitespace-nowrap">
            🔍 智能分析
          </span>
          <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 whitespace-nowrap">
            📊 可视化报告
          </span>
          <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800 whitespace-nowrap">
            🎮 游戏优化
          </span>
        </div>
      </div>
      
      <!-- 主要内容区域 - 动态布局 -->
      <div v-if="analysisResults.length === 0" class="flex justify-center items-start">
        <!-- 居中显示的文件上传区域 -->
        <div class="w-full max-w-2xl space-y-4">
          <!-- 文件上传区域 - 增强视觉效果 -->
          <div class="bg-white/90 backdrop-blur-sm rounded-xl shadow-lg border border-slate-200/60 p-4 hover:shadow-xl transition-all duration-300">
            <div class="mb-3">
              <h3 class="text-sm font-semibold text-slate-800 mb-2 flex items-center gap-2">
                <span class="w-4 h-4 bg-blue-500 rounded-full flex items-center justify-center">
                  <span class="text-white text-xs">📁</span>
                </span>
                文件上传
              </h3>
              <div 
                class="border-2 border-dashed border-slate-300 rounded-xl p-6 text-center transition-all duration-300 bg-gradient-to-br from-slate-50 to-blue-50/30 hover:border-blue-400 hover:bg-gradient-to-br hover:from-blue-50 hover:to-indigo-50/40 relative group cursor-pointer"
                @drop="handleDrop" 
                @dragover.prevent 
                @dragenter.prevent
                @click="fileInput?.click()"
              >
                <div class="flex flex-col items-center gap-3">
                  <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center group-hover:bg-blue-200 transition-colors">
                    <span class="text-blue-600 text-2xl">📁</span>
                  </div>
                  <div>
                    <p class="text-slate-700 text-sm font-medium">{{ t('home.dragAndDrop') }}</p>
                    <p class="text-slate-500 text-xs mt-1">{{ t('home.supportedFormats') }}</p>
                  </div>
                  <div class="flex items-center gap-2 mt-2">
                    <input
                      ref="fileInput"
                      type="file"
                      accept=".json"
                      multiple
                      @change="handleFileSelect"
                      class="hidden"
                    />
                    <button 
                      class="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 hover:from-blue-700 hover:to-indigo-700 hover:shadow-lg transform hover:-translate-y-0.5"
                      @click.stop="fileInput?.click()"
                    >
                      {{ t('home.selectFiles') }}
                    </button>
                    <Popover class="relative">
                      <PopoverButton class="text-slate-400 hover:text-slate-600 p-1 rounded-full hover:bg-slate-100 transition-all duration-300">
                        <InformationCircleIcon class="h-3 w-3" />
                      </PopoverButton>
                      <transition
                        enter-active-class="transition ease-out duration-200"
                        enter-from-class="opacity-0 translate-y-1"
                        enter-to-class="opacity-100 translate-y-0"
                        leave-active-class="transition ease-in duration-150"
                        leave-from-class="opacity-100 translate-y-0"
                        leave-to-class="opacity-0 translate-y-1"
                      >
                        <PopoverPanel class="absolute z-50 w-56 px-3 mt-1 transform -translate-x-1/2 left-1/2 sm:px-0">
                          <div class="overflow-hidden rounded-lg shadow-lg ring-1 ring-slate-200 bg-white">
                            <div class="relative p-2">
                              <h3 class="text-xs font-semibold text-slate-900 mb-1">{{ t('help.fileUpload.title') }}</h3>
                              <ul class="text-xs text-slate-600 space-y-0.5">
                                <li class="flex items-center gap-1">• {{ t('help.fileUpload.content.0') }}</li>
                                <li class="flex items-center gap-1">• {{ t('help.fileUpload.content.1') }}</li>
                                <li class="flex items-center gap-1">• {{ t('help.fileUpload.content.2') }}</li>
                                <li class="flex items-center gap-1">• {{ t('help.fileUpload.content.3') }}</li>
                              </ul>
                            </div>
                          </div>
                        </PopoverPanel>
                      </transition>
                    </Popover>
                  </div>
                </div>
              </div>
              <div v-if="uploadedFiles.length === 0" class="text-center">
                <p class="text-slate-500 text-xs">{{ t('home.uploadPrompt') }}</p>
              </div>
            </div>
          </div>
          
          <!-- 已上传文件列表 - 增强设计 -->
          <div v-if="uploadedFiles.length > 0" class="bg-white/90 backdrop-blur-sm rounded-xl shadow-lg border border-slate-200/60 p-4 hover:shadow-xl transition-all duration-300">
            <div class="flex justify-between items-center mb-3">
              <h3 class="text-sm font-semibold text-slate-800 flex items-center gap-2">
                <span class="w-4 h-4 bg-green-500 rounded-full flex items-center justify-center">
                  <span class="text-white text-xs">✓</span>
                </span>
                {{ t('home.uploadedFiles') }}
              </h3>
              <div class="flex items-center gap-2">
                <span class="bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-700 px-3 py-1 rounded-full text-xs font-medium border border-blue-200">
                  {{ uploadedFiles.length }} {{ t('common.items') }}
                </span>
                <button 
                  @click="uploadedFiles = []" 
                  class="text-red-500 hover:text-red-700 text-xs font-medium transition-all duration-300 hover:bg-red-50 px-2 py-1 rounded-lg"
                  :disabled="isAnalyzing"
                >
                  {{ t('common.clear') }}
                </button>
              </div>
            </div>
            <div class="max-h-40 overflow-y-auto space-y-2 scrollbar-thin scrollbar-thumb-slate-300 scrollbar-track-slate-100">
              <div v-for="(file, index) in uploadedFiles" :key="file.name" 
                   class="flex justify-between items-center p-3 bg-gradient-to-r from-slate-50 to-blue-50/30 rounded-lg border border-slate-200/50 transition-all duration-300 hover:from-blue-50 hover:to-indigo-50/40 hover:shadow-md hover:-translate-y-0.5">
                <div class="flex items-center gap-3 flex-1 min-w-0">
                  <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <DocumentIcon class="w-4 h-4 text-blue-600" />
                  </div>
                  <div class="flex flex-col gap-1 flex-1 min-w-0">
                    <span class="font-medium text-slate-800 truncate text-sm">{{ file.name }}</span>
                    <span class="text-slate-500 text-xs">{{ formatFileSize(file.size) }}</span>
                  </div>
                </div>
                <button 
                  @click="removeFile(index)" 
                  :disabled="isAnalyzing"
                  class="w-7 h-7 bg-red-100 hover:bg-red-200 text-red-600 rounded-lg transition-all duration-300 hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  <XMarkIcon class="w-3 h-3" />
                </button>
              </div>
            </div>
          </div>
          
          <!-- 分析配置 - 增强设计 -->
          <div v-if="uploadedFiles.length > 0" class="bg-white/90 backdrop-blur-sm rounded-xl shadow-lg border border-slate-200/60 p-4 hover:shadow-xl transition-all duration-300">
            <div class="flex justify-between items-center mb-3">
              <h3 class="text-sm font-semibold text-slate-800 flex items-center gap-2">
                <span class="w-4 h-4 bg-purple-500 rounded-full flex items-center justify-center">
                  <span class="text-white text-xs">⚙️</span>
                </span>
                {{ t('home.analysisConfig') }}
              </h3>
              <span class="text-xs text-slate-500 bg-slate-100 px-2 py-1 rounded-full">
                {{ t('home.analysisConfigDescription') }}
              </span>
            </div>
            <!-- 指标选择器 -->
            <div class="p-3 bg-gradient-to-r from-slate-50 to-purple-50/30 rounded-lg border border-slate-200/50 mb-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-slate-900">{{ t('metricSelector.title') }}</span>
                <button 
                  @click="showMetricSelector = !showMetricSelector"
                  class="px-3 py-1 text-xs bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-all duration-300 hover:shadow-sm"
                >
                  {{ showMetricSelector ? t('common.close') : t('common.view') }}
                </button>
              </div>
              <p class="text-xs text-slate-600 mb-2 flex items-center gap-2">
                <span class="w-2 h-2 bg-purple-400 rounded-full"></span>
                {{ t('metricSelector.selectedCount', { count: selectedMetrics.length, total: availableMetricsCount }) }}
              </p>
              <div v-if="showMetricSelector" class="mt-2">
                <MetricSelector
                  :initial-selection="selectedMetrics"
                  @change="handleMetricChange"
                />
              </div>
            </div>
            <!-- 主要分析按钮 -->
            <div class="text-center">
              <button 
                @click="analyzeAllFiles" 
                :disabled="uploadedFiles.length === 0 || isAnalyzing"
                class="relative bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-3 rounded-xl text-sm font-semibold transition-all duration-300 hover:from-green-700 hover:to-emerald-700 hover:shadow-lg hover:-translate-y-0.5 disabled:from-slate-400 disabled:to-slate-500 disabled:cursor-not-allowed disabled:transform-none w-full"
              >
                <div class="flex items-center justify-center gap-2">
                  <span v-if="isAnalyzing" class="w-4 h-4 border-2 border-transparent border-t-white rounded-full animate-spin"></span>
                  <span v-else class="text-lg">🔍</span>
                  <span>{{ isAnalyzing ? t('home.analyzing', { current: analysisResults.length, total: uploadedFiles.length }) : t('home.startAnalysis', { count: uploadedFiles.length }) }}</span>
                </div>
              </button>
              <!-- 分析进度条 -->
              <div v-if="isAnalyzing" class="mt-3">
                <div class="bg-slate-200 rounded-full h-2 overflow-hidden shadow-inner">
                  <div 
                    class="bg-gradient-to-r from-green-500 to-emerald-500 h-full transition-all duration-500 ease-out rounded-full"
                    :style="{ width: `${(analysisResults.length / uploadedFiles.length) * 100}%` }"
                  ></div>
                </div>
                <p class="text-sm text-slate-600 mt-2 font-medium">
                  {{ t('home.progress', { completed: analysisResults.length, total: uploadedFiles.length, percentage: Math.round((analysisResults.length / uploadedFiles.length) * 100) }) }}
                </p>
              </div>
              <p v-if="!isAnalyzing" class="text-slate-500 text-sm mt-2 flex items-center justify-center gap-2">
                <span class="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></span>
                {{ uploadedFiles.length > 0 ? t('home.clickToAnalyze') : t('home.pleaseUploadFirst') }}
              </p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 有分析结果时的左右布局 -->
      <div v-else class="grid grid-cols-1 xl:grid-cols-5 gap-6">
        <!-- 左侧：文件上传和配置 - 增强设计 -->
        <div class="xl:col-span-2 space-y-4">
          <!-- 文件上传区域 - 增强视觉效果 -->
          <div class="bg-white/90 backdrop-blur-sm rounded-xl shadow-lg border border-slate-200/60 p-4 hover:shadow-xl transition-all duration-300">
            <div class="mb-3">
              <h3 class="text-sm font-semibold text-slate-800 mb-2 flex items-center gap-2">
                <span class="w-4 h-4 bg-blue-500 rounded-full flex items-center justify-center">
                  <span class="text-white text-xs">📁</span>
                </span>
                文件上传
              </h3>
              <div 
                class="border-2 border-dashed border-slate-300 rounded-xl p-6 text-center transition-all duration-300 bg-gradient-to-br from-slate-50 to-blue-50/30 hover:border-blue-400 hover:bg-gradient-to-br hover:from-blue-50 hover:to-indigo-50/40 relative group cursor-pointer"
                @drop="handleDrop" 
                @dragover.prevent 
                @dragenter.prevent
                @click="fileInput?.click()"
              >
                <div class="flex flex-col items-center gap-3">
                  <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center group-hover:bg-blue-200 transition-colors">
                    <span class="text-blue-600 text-2xl">📁</span>
                  </div>
                  <div>
                    <p class="text-slate-700 text-sm font-medium">{{ t('home.dragAndDrop') }}</p>
                    <p class="text-slate-500 text-xs mt-1">{{ t('home.supportedFormats') }}</p>
                  </div>
                  <div class="flex items-center gap-2 mt-2">
                    <input
                      ref="fileInput"
                      type="file"
                      accept=".json"
                      multiple
                      @change="handleFileSelect"
                      class="hidden"
                    />
                    <button 
                      class="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 hover:from-blue-700 hover:to-indigo-700 hover:shadow-lg transform hover:-translate-y-0.5"
                      @click.stop="fileInput?.click()"
                    >
                      {{ t('home.selectFiles') }}
                    </button>
                    <Popover class="relative">
                      <PopoverButton class="text-slate-400 hover:text-slate-600 p-1 rounded-full hover:bg-slate-100 transition-all duration-300">
                        <InformationCircleIcon class="h-3 w-3" />
                      </PopoverButton>
                      <transition
                        enter-active-class="transition ease-out duration-200"
                        enter-from-class="opacity-0 translate-y-1"
                        enter-to-class="opacity-100 translate-y-0"
                        leave-active-class="transition ease-in duration-150"
                        leave-from-class="opacity-100 translate-y-0"
                        leave-to-class="opacity-0 translate-y-1"
                      >
                        <PopoverPanel class="absolute z-50 w-56 px-3 mt-1 transform -translate-x-1/2 left-1/2 sm:px-0">
                          <div class="overflow-hidden rounded-lg shadow-lg ring-1 ring-slate-200 bg-white">
                            <div class="relative p-2">
                              <h3 class="text-xs font-semibold text-slate-900 mb-1">{{ t('help.fileUpload.title') }}</h3>
                              <ul class="text-xs text-slate-600 space-y-0.5">
                                <li class="flex items-center gap-1">• {{ t('help.fileUpload.content.0') }}</li>
                                <li class="flex items-center gap-1">• {{ t('help.fileUpload.content.1') }}</li>
                                <li class="flex items-center gap-1">• {{ t('help.fileUpload.content.2') }}</li>
                                <li class="flex items-center gap-1">• {{ t('help.fileUpload.content.3') }}</li>
                              </ul>
                            </div>
                          </div>
                        </PopoverPanel>
                      </transition>
                    </Popover>
                  </div>
                </div>
              </div>
              <div v-if="uploadedFiles.length === 0" class="text-center">
                <p class="text-slate-500 text-xs">{{ t('home.uploadPrompt') }}</p>
              </div>
            </div>
          </div>
          
          <!-- 已上传文件列表 - 增强设计 -->
          <div v-if="uploadedFiles.length > 0" class="bg-white/90 backdrop-blur-sm rounded-xl shadow-lg border border-slate-200/60 p-4 hover:shadow-xl transition-all duration-300">
            <div class="flex justify-between items-center mb-3">
              <h3 class="text-sm font-semibold text-slate-800 flex items-center gap-2">
                <span class="w-4 h-4 bg-green-500 rounded-full flex items-center justify-center">
                  <span class="text-white text-xs">✓</span>
                </span>
                {{ t('home.uploadedFiles') }}
              </h3>
              <div class="flex items-center gap-2">
                <span class="bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-700 px-3 py-1 rounded-full text-xs font-medium border border-blue-200">
                  {{ uploadedFiles.length }} {{ t('common.items') }}
                </span>
                <button 
                  @click="uploadedFiles = []" 
                  class="text-red-500 hover:text-red-700 text-xs font-medium transition-all duration-300 hover:bg-red-50 px-2 py-1 rounded-lg"
                  :disabled="isAnalyzing"
                >
                  {{ t('common.clear') }}
                </button>
              </div>
            </div>
            <div class="max-h-40 overflow-y-auto space-y-2 scrollbar-thin scrollbar-thumb-slate-300 scrollbar-track-slate-100">
              <div v-for="(file, index) in uploadedFiles" :key="file.name" 
                   class="flex justify-between items-center p-3 bg-gradient-to-r from-slate-50 to-blue-50/30 rounded-lg border border-slate-200/50 transition-all duration-300 hover:from-blue-50 hover:to-indigo-50/40 hover:shadow-md hover:-translate-y-0.5">
                <div class="flex items-center gap-3 flex-1 min-w-0">
                  <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <DocumentIcon class="w-4 h-4 text-blue-600" />
                  </div>
                  <div class="flex flex-col gap-1 flex-1 min-w-0">
                    <span class="font-medium text-slate-800 truncate text-sm">{{ file.name }}</span>
                    <span class="text-slate-500 text-xs">{{ formatFileSize(file.size) }}</span>
                  </div>
                </div>
                <button 
                  @click="removeFile(index)" 
                  :disabled="isAnalyzing"
                  class="w-7 h-7 bg-red-100 hover:bg-red-200 text-red-600 rounded-lg transition-all duration-300 hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  <XMarkIcon class="w-3 h-3" />
                </button>
              </div>
            </div>
          </div>
          
          <!-- 分析配置 - 增强设计 -->
          <div v-if="uploadedFiles.length > 0" class="bg-white/90 backdrop-blur-sm rounded-xl shadow-lg border border-slate-200/60 p-4 hover:shadow-xl transition-all duration-300">
            <div class="flex justify-between items-center mb-3">
              <h3 class="text-sm font-semibold text-slate-800 flex items-center gap-2">
                <span class="w-4 h-4 bg-purple-500 rounded-full flex items-center justify-center">
                  <span class="text-white text-xs">⚙️</span>
                </span>
                {{ t('home.analysisConfig') }}
              </h3>
              <span class="text-xs text-slate-500 bg-slate-100 px-2 py-1 rounded-full">
                {{ t('home.analysisConfigDescription') }}
              </span>
            </div>
            <!-- 指标选择器 -->
            <div class="p-3 bg-gradient-to-r from-slate-50 to-purple-50/30 rounded-lg border border-slate-200/50 mb-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-slate-900">{{ t('metricSelector.title') }}</span>
                <button 
                  @click="showMetricSelector = !showMetricSelector"
                  class="px-3 py-1 text-xs bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-all duration-300 hover:shadow-sm"
                >
                  {{ showMetricSelector ? t('common.close') : t('common.view') }}
                </button>
              </div>
              <p class="text-xs text-slate-600 mb-2 flex items-center gap-2">
                <span class="w-2 h-2 bg-purple-400 rounded-full"></span>
                {{ t('metricSelector.selectedCount', { count: selectedMetrics.length, total: availableMetricsCount }) }}
              </p>
              <div v-if="showMetricSelector" class="mt-2">
                <MetricSelector
                  :initial-selection="selectedMetrics"
                  @change="handleMetricChange"
                />
              </div>
            </div>
            <!-- 主要分析按钮 -->
            <div class="text-center">
              <button 
                @click="analyzeAllFiles" 
                :disabled="uploadedFiles.length === 0 || isAnalyzing"
                class="relative bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-3 rounded-xl text-sm font-semibold transition-all duration-300 hover:from-green-700 hover:to-emerald-700 hover:shadow-lg hover:-translate-y-0.5 disabled:from-slate-400 disabled:to-slate-500 disabled:cursor-not-allowed disabled:transform-none w-full"
              >
                <div class="flex items-center justify-center gap-2">
                  <span v-if="isAnalyzing" class="w-4 h-4 border-2 border-transparent border-t-white rounded-full animate-spin"></span>
                  <span v-else class="text-lg">🔍</span>
                  <span>{{ isAnalyzing ? t('home.analyzing', { current: analysisResults.length, total: uploadedFiles.length }) : t('home.startAnalysis', { count: uploadedFiles.length }) }}</span>
                </div>
              </button>
              <!-- 分析进度条 -->
              <div v-if="isAnalyzing" class="mt-3">
                <div class="bg-slate-200 rounded-full h-2 overflow-hidden shadow-inner">
                  <div 
                    class="bg-gradient-to-r from-green-500 to-emerald-500 h-full transition-all duration-500 ease-out rounded-full"
                    :style="{ width: `${(analysisResults.length / uploadedFiles.length) * 100}%` }"
                  ></div>
                </div>
                <p class="text-sm text-slate-600 mt-2 font-medium">
                  {{ t('home.progress', { completed: analysisResults.length, total: uploadedFiles.length, percentage: Math.round((analysisResults.length / uploadedFiles.length) * 100) }) }}
                </p>
              </div>
              <p v-if="!isAnalyzing" class="text-slate-500 text-sm mt-2 flex items-center justify-center gap-2">
                <span class="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></span>
                {{ uploadedFiles.length > 0 ? t('home.clickToAnalyze') : t('home.pleaseUploadFirst') }}
              </p>
            </div>
          </div>
        </div>
        
        <!-- 右侧：分析结果 - 增强设计 -->
        <div class="xl:col-span-3">
          <!-- 分析结果区域 -->
          <div v-if="analysisResults.length > 0" class="bg-white/90 backdrop-blur-xl rounded-xl shadow-xl border border-white/30 p-6">
            <div class="flex justify-between items-start mb-6">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full flex items-center justify-center shadow-lg">
                  <span class="text-white text-sm">📊</span>
                </div>
                <div>
                  <h2 class="text-xl font-bold text-gray-800">
                    {{ t('home.analysisResults') }}
                  </h2>
                  <p class="text-sm text-gray-600">共 {{ analysisResults.length }} 个分析结果</p>
                </div>
              </div>
              <!-- 快速导航区域 - 现代化设计 -->
              <div class="flex flex-wrap gap-3">
                <button
                  @click="viewMultipleDetails"
                  class="group relative inline-flex items-center gap-3 px-5 py-3 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-xl hover:from-blue-600 hover:to-indigo-700 transition-all duration-300 text-sm font-semibold shadow-lg hover:shadow-xl hover:-translate-y-1 transform overflow-hidden"
                >
                  <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700"></div>
                  <span class="text-base relative z-10">👁️</span>
                  <span class="relative z-10">查看细节</span>
                </button>
                <button
                  @click="exportAllResults"
                  class="group relative inline-flex items-center gap-3 px-5 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl hover:from-green-600 hover:to-emerald-700 transition-all duration-300 text-sm font-semibold shadow-lg hover:shadow-xl hover:-translate-y-1 transform overflow-hidden"
                >
                  <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700"></div>
                  <span class="text-base relative z-10">📄</span>
                  <span class="relative z-10">导出报告</span>
                </button>
                <button
                  @click="clearResults"
                  class="group relative inline-flex items-center gap-3 px-5 py-3 bg-gradient-to-r from-red-500 to-pink-600 text-white rounded-xl hover:from-red-600 hover:to-pink-700 transition-all duration-300 text-sm font-semibold shadow-lg hover:shadow-xl hover:-translate-y-1 transform overflow-hidden"
                >
                  <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700"></div>
                  <span class="text-base relative z-10">🗑️</span>
                  <span class="relative z-10">清空结果</span>
                </button>
              </div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div v-for="(result, index) in analysisResults" :key="result.id" 
                   class="bg-white/80 backdrop-blur-sm rounded-xl p-4 shadow-lg border border-gray-200/50 transition-all duration-300 hover:shadow-xl hover:-translate-y-1 transform hover:bg-white/90 group">
                <div class="flex justify-between items-start mb-3">
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 mb-2">
                      <div class="w-6 h-6 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                        <span class="text-blue-600 text-xs">📄</span>
                      </div>
                      <h3 class="text-gray-900 text-sm font-semibold truncate" :title="result.filename">
                        {{ result.filename }}
                      </h3>
                    </div>
                    <p class="text-gray-500 text-xs flex items-center gap-1">
                      <span class="w-1.5 h-1.5 bg-gray-400 rounded-full"></span>
                      {{ t('home.fileNumber', { current: index + 1, total: analysisResults.length }) }}
                    </p>
                  </div>
                  <div class="flex items-end ml-3">
                    <div class="text-center">
                      <div 
                        :class="[
                          'text-lg font-bold py-2 px-3 rounded-xl text-white flex-shrink-0 min-w-12 text-center shadow-lg transform transition-all duration-300 group-hover:scale-105',
                          getScoreClass(result.overallScore) === 'excellent' ? 'bg-gradient-to-r from-green-500 to-emerald-500' : '',
                          getScoreClass(result.overallScore) === 'good' ? 'bg-gradient-to-r from-blue-500 to-indigo-500' : '',
                          getScoreClass(result.overallScore) === 'average' ? 'bg-gradient-to-r from-yellow-500 to-orange-500 text-white' : '',
                          getScoreClass(result.overallScore) === 'poor' ? 'bg-gradient-to-r from-red-500 to-pink-500' : '',
                          getScoreClass(result.overallScore) === 'very-poor' ? 'bg-gradient-to-r from-gray-500 to-slate-500' : ''
                        ]"
                      >
                        {{ result.overallScore.toFixed(2) }}
                      </div>
                      <p class="text-xs text-gray-500 mt-1 font-medium">{{ result.grade }}</p>
                    </div>
                  </div>
                </div>
                
                <!-- 快速操作按钮 -->
                <div class="flex gap-2 mt-3 pt-3 border-t border-gray-100">
                  <button
                    @click="viewDetails(result)"
                    class="flex-1 group/btn relative inline-flex items-center justify-center gap-2 px-3 py-2 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-lg hover:from-blue-600 hover:to-indigo-700 transition-all duration-300 text-xs font-medium shadow-md hover:shadow-lg hover:-translate-y-0.5 transform overflow-hidden"
                  >
                    <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover/btn:translate-x-full transition-transform duration-500"></div>
                    <span class="text-xs relative z-10">👁️</span>
                    <span class="relative z-10">详情</span>
                  </button>
                  <button
                    @click="exportResult(result)"
                    class="flex-1 group/btn relative inline-flex items-center justify-center gap-2 px-3 py-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg hover:from-green-600 hover:to-emerald-700 transition-all duration-300 text-xs font-medium shadow-md hover:shadow-lg hover:-translate-y-0.5 transform overflow-hidden"
                  >
                    <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover/btn:translate-x-full transition-transform duration-500"></div>
                    <span class="text-xs relative z-10">📄</span>
                    <span class="relative z-10">导出</span>
                  </button>
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
                    <div class="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
                      <ExclamationTriangleIcon class="h-6 w-6 text-red-600" aria-hidden="true" />
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
                      class="inline-flex w-full justify-center rounded-xl bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 sm:ml-3 sm:w-auto transition-all duration-300"
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
                    <div class="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
                      <ExclamationTriangleIcon class="h-6 w-6 text-red-600" aria-hidden="true" />
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
  
  .grid.grid-cols-1.md\:grid-cols-2.lg\:grid-cols-3 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 1024px) {
  .text-5xl {
    font-size: 2.25rem;
    line-height: 2.5rem;
  }

  .text-8xl {
    font-size: 6rem;
    line-height: 1;
  }

  .px-12 {
    padding-left: 2rem;
    padding-right: 2rem;
  }

  .py-5 {
    padding-top: 1rem;
    padding-bottom: 1rem;
  }
}

@media (max-width: 768px) {
  .py-4.px-4 {
    padding: 0.75rem;
  }
  
  .text-3xl {
    font-size: 1.25rem;
    line-height: 1.75rem;
  }
  
  .text-base {
    font-size: 0.875rem;
    line-height: 1.25rem;
  }
  
  .gap-6 {
    gap: 1rem;
  }
  
  .gap-4 {
    gap: 0.75rem;
  }
  
  .p-6 {
    padding: 1rem;
  }
  
  .p-4 {
    padding: 0.75rem;
  }
  
  .mb-6 {
    margin-bottom: 1rem;
  }
  
  .w-10.h-10 {
    width: 2rem;
    height: 2rem;
  }
  
  .w-8.h-8 {
    width: 1.5rem;
    height: 1.5rem;
  }
  
  .grid.grid-cols-1.md\:grid-cols-2.lg\:grid-cols-3 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .max-h-40 {
    max-height: 8rem;
  }
  
  /* 最小高度在移动端的调整 */
  .min-h-\[600px\] {
    min-height: 400px;
  }
  
  /* 文件上传区域在移动端的优化 */
  .p-6.text-center {
    padding: 1rem;
  }
  
  /* 分析结果卡片在移动端的优化 */
  .hover\:-translate-y-1:hover {
    transform: translateY(0);
  }
  
  .transform.hover\:-translate-y-0\.5:hover {
    transform: translateY(0);
  }
}

@media (max-width: 640px) {
  .text-5xl {
    font-size: 1.5rem;
    line-height: 2rem;
  }

  .text-xl {
    font-size: 1.125rem;
    line-height: 1.75rem;
  }

  .px-6 {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .p-6 {
    padding: 1rem;
  }

  .gap-6 {
    gap: 1rem;
  }

  .grid.grid-cols-1.md\:grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
