<template>
  <div class="space-y-3">
    <!-- 新的布局：使用更宽的容器和更好的比例分配 -->
    <div class="grid grid-cols-1 2xl:grid-cols-12 gap-6">
      <!-- 可视化区域 - 占据更多空间，提高比例 -->
      <div class="2xl:col-span-8 bg-white/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200/60 shadow-xl">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold text-gray-800 flex items-center gap-3">
            <div class="w-6 h-6 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-lg flex items-center justify-center">
              <span class="text-white text-xs">🎨</span>
            </div>
            地下城可视化
          </h3>
          <div class="flex items-center gap-2">
            <div class="flex bg-gray-100 rounded-lg p-1">
              <button 
                @click="visualizationMode = 'canvas'"
                :class="['px-3 py-1 text-xs font-medium rounded-md transition-all duration-300', 
                  visualizationMode === 'canvas' 
                    ? 'bg-blue-600 text-white shadow-sm' 
                    : 'text-gray-600 hover:text-gray-800 hover:bg-gray-200']"
              >
                交互式
              </button>
              <button 
                @click="visualizationMode = 'image'"
                :class="['px-3 py-1 text-xs font-medium rounded-md transition-all duration-300', 
                  visualizationMode === 'image' 
                    ? 'bg-blue-600 text-white shadow-sm' 
                    : 'text-gray-600 hover:text-gray-800 hover:bg-gray-200']"
              >
                静态图片
              </button>
            </div>
            <button 
              v-if="imageData" 
              @click="downloadImage"
              class="px-3 py-1 bg-green-100 text-green-700 rounded-lg text-xs font-medium hover:bg-green-200 transition-colors"
            >
              下载图片
            </button>
          </div>
        </div>
        
        <div v-if="loading" class="flex items-center justify-center py-16 bg-gradient-to-br from-slate-50 to-blue-50/30 rounded-xl border-2 border-dashed border-slate-300">
          <div class="text-center">
            <div class="w-12 h-12 border-4 border-slate-300 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
            <p class="text-slate-600 font-medium">{{ t('common.loading') }}</p>
            <p class="text-slate-500 text-sm mt-1">正在生成可视化...</p>
          </div>
        </div>
        
        <div v-else-if="error" class="text-center py-16 bg-gradient-to-br from-red-50 to-pink-50/30 rounded-xl border-2 border-dashed border-red-200">
          <div class="text-red-600 mb-4">
            <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <span class="text-red-600 text-xl">⚠️</span>
            </div>
            <p class="font-medium">{{ error }}</p>
          </div>
          <div v-if="error.includes('文件ID已过期')" class="mt-4">
            <button 
              @click="goBackToHome" 
              class="px-6 py-3 bg-gradient-to-r from-red-600 to-pink-600 text-white rounded-lg hover:from-red-700 hover:to-pink-700 transition-all duration-300 font-medium shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
            >
              返回主页重新上传
            </button>
          </div>
        </div>
        
        <!-- 交互式可视化 -->
        <div v-else-if="visualizationMode === 'canvas' && dungeonData" class="space-y-3">
          <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-3 border border-blue-200">
            <h4 class="text-sm font-medium text-blue-800 mb-1 flex items-center gap-2">
              <span class="w-4 h-4 bg-blue-500 rounded-full"></span>
              {{ t('detail.canvasVisualization') }}
            </h4>
            <p class="text-xs text-blue-600">点击房间和通道查看详细信息</p>
          </div>
          <div class="border-2 border-gray-200 rounded-xl overflow-hidden shadow-inner bg-white min-h-[600px]">
            <DungeonVisualizer 
              :dungeon-data="dungeonData"
              @room-click="handleRoomClick"
              @corridor-click="handleCorridorClick"
            />
          </div>
        </div>
        
        <!-- 静态图片可视化 -->
        <div v-else-if="visualizationMode === 'image' && imageData" class="space-y-3">
          <div class="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-3 border border-green-200">
            <h4 class="text-sm font-medium text-green-800 mb-1 flex items-center gap-2">
              <span class="w-4 h-4 bg-green-500 rounded-full"></span>
              {{ t('detail.generatedImage') }}
            </h4>
            <p class="text-xs text-green-600">高质量matplotlib生成的地下城布局图</p>
          </div>
          <div class="border-2 border-gray-200 rounded-xl overflow-hidden shadow-lg bg-white">
            <div class="relative group">
              <img 
                :src="`data:image/png;base64,${imageData}`" 
                alt="Generated visualization" 
                class="w-full h-auto transition-transform duration-300 group-hover:scale-105" 
              />
              <div class="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors duration-300 flex items-center justify-center opacity-0 group-hover:opacity-100">
                <button 
                  @click="openImageFullscreen"
                  class="bg-white/90 backdrop-blur-sm text-gray-800 px-4 py-2 rounded-lg shadow-lg hover:bg-white transition-all duration-300 font-medium"
                >
                  🔍 查看大图
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 自动切换到有效的可视化模式 -->
        <div v-else-if="dungeonData && !imageData" class="space-y-3">
          <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-3 border border-blue-200">
            <h4 class="text-sm font-medium text-blue-800 mb-1 flex items-center gap-2">
              <span class="w-4 h-4 bg-blue-500 rounded-full"></span>
              {{ t('detail.canvasVisualization') }}
            </h4>
            <p class="text-xs text-blue-600">点击房间和通道查看详细信息</p>
          </div>
          <div class="border-2 border-gray-200 rounded-xl overflow-hidden shadow-inner bg-white min-h-[600px]">
            <DungeonVisualizer 
              :dungeon-data="dungeonData"
              @room-click="handleRoomClick"
              @corridor-click="handleCorridorClick"
            />
          </div>
        </div>
        
        <div v-else-if="!dungeonData && imageData" class="space-y-3">
          <div class="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-3 border border-green-200">
            <h4 class="text-sm font-medium text-green-800 mb-1 flex items-center gap-2">
              <span class="w-4 h-4 bg-green-500 rounded-full"></span>
              {{ t('detail.generatedImage') }}
            </h4>
            <p class="text-xs text-green-600">高质量matplotlib生成的地下城布局图</p>
          </div>
          <div class="border-2 border-gray-200 rounded-xl overflow-hidden shadow-lg bg-white">
            <div class="relative group">
              <img 
                :src="`data:image/png;base64,${imageData}`" 
                alt="Generated visualization" 
                class="w-full h-auto transition-transform duration-300 group-hover:scale-105" 
              />
              <div class="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors duration-300 flex items-center justify-center opacity-0 group-hover:opacity-100">
                <button 
                  @click="openImageFullscreen"
                  class="bg-white/90 backdrop-blur-sm text-gray-800 px-4 py-2 rounded-lg shadow-lg hover:bg-white transition-all duration-300 font-medium"
                >
                  🔍 查看大图
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div v-else class="flex items-center justify-center min-h-[500px] bg-gradient-to-br from-slate-50 to-blue-50/30 rounded-xl border-2 border-dashed border-slate-300">
          <div class="text-center">
            <div class="w-16 h-16 bg-slate-200 rounded-full flex items-center justify-center mx-auto mb-4">
              <span class="text-slate-500 text-2xl">🎨</span>
            </div>
            <p class="text-slate-600 font-medium mb-2">{{ t('detail.noVisualizationData') }}</p>
            <p class="text-slate-500 text-sm">请稍等，正在生成可视化数据...</p>
          </div>
        </div>
        
        <!-- 全屏图片查看模态框 -->
        <div v-if="showFullscreenImage" class="fixed inset-0 bg-black/90 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click="closeFullscreenImage">
          <div class="relative max-w-full max-h-full">
            <img 
              :src="`data:image/png;base64,${imageData}`" 
              alt="Fullscreen visualization" 
              class="max-w-full max-h-full object-contain rounded-lg shadow-2xl"
              @click.stop
            />
            <button 
              @click="closeFullscreenImage"
              class="absolute top-4 right-4 w-10 h-10 bg-black/50 hover:bg-black/70 text-white rounded-full flex items-center justify-center transition-colors"
            >
              ✕
            </button>
          </div>
        </div>
      </div>
      
      <!-- 分析结果区域 - 优化布局，占据剩余空间 -->
      <div class="2xl:col-span-4 bg-white/95 backdrop-blur-sm rounded-xl p-5 border border-gray-200/60 shadow-lg">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-6 h-6 bg-gradient-to-r from-green-500 to-blue-600 rounded-lg flex items-center justify-center shadow-sm">
            <span class="text-white text-xs">📊</span>
          </div>
          <h3 class="text-lg font-bold text-gray-800">分析报告</h3>
        </div>
        
        <div class="space-y-5">
          <!-- 总体评分 - 更清晰的设计 -->
          <div class="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-5 border border-blue-200/50">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-sm font-semibold text-gray-700">综合评分</h4>
              <div class="flex items-center gap-2">
                <span class="text-sm text-gray-600">等级:</span>
                <span class="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  {{ grade }}
                </span>
              </div>
            </div>
            <div class="flex items-center gap-4">
              <div class="text-4xl font-bold text-blue-600">
                {{ (overallScore * 100).toFixed(0) }}
                <span class="text-lg text-gray-500">%</span>
              </div>
              <div class="flex-1">
                <div class="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                  <div 
                    class="h-3 rounded-full transition-all duration-500 ease-out"
                    :class="[
                      getScoreClass(overallScore) === 'excellent' ? 'bg-gradient-to-r from-green-500 to-emerald-500' : '',
                      getScoreClass(overallScore) === 'good' ? 'bg-gradient-to-r from-blue-500 to-cyan-500' : '',
                      getScoreClass(overallScore) === 'average' ? 'bg-gradient-to-r from-yellow-500 to-orange-500' : '',
                      getScoreClass(overallScore) === 'poor' ? 'bg-gradient-to-r from-red-500 to-pink-500' : '',
                      getScoreClass(overallScore) === 'very-poor' ? 'bg-gradient-to-r from-gray-500 to-slate-500' : ''
                    ]"
                    :style="{ width: `${overallScore * 100}%` }"
                  ></div>
                </div>
                <p class="text-sm text-gray-600 mt-2">
                  {{ getScoreClass(overallScore) === 'excellent' ? '🎯 设计优秀，达到专业水准' : 
                     getScoreClass(overallScore) === 'good' ? '✅ 设计良好，表现不错' :
                     getScoreClass(overallScore) === 'average' ? '⚠️ 设计一般，有改进空间' :
                     getScoreClass(overallScore) === 'poor' ? '❌ 设计欠佳，需要改进' : '🔧 设计较差，需要大幅改进' }}
                </p>
              </div>
            </div>
          </div>
          
          <!-- 选项卡导航 - 优化设计 -->
          <div class="bg-gray-50 rounded-lg p-1 mb-4">
            <nav class="flex space-x-1">
              <button @click="activeTab = 'overview'" 
                      :class="[
                        'flex-1 py-2 px-3 text-sm font-medium rounded-md transition-all duration-200',
                        activeTab === 'overview' 
                          ? 'bg-white text-blue-700 shadow-sm border border-blue-200' 
                          : 'text-gray-600 hover:text-gray-800 hover:bg-white/50'
                      ]">
                📊 指标概览
              </button>
              <button @click="activeTab = 'detailed'" 
                      :class="[
                        'flex-1 py-2 px-3 text-sm font-medium rounded-md transition-all duration-200',
                        activeTab === 'detailed' 
                          ? 'bg-white text-blue-700 shadow-sm border border-blue-200' 
                          : 'text-gray-600 hover:text-gray-800 hover:bg-white/50'
                      ]">
                📋 详细报告
              </button>
              <button @click="activeTab = 'suggestions'" 
                      :class="[
                        'flex-1 py-2 px-3 text-sm font-medium rounded-md transition-all duration-200',
                        activeTab === 'suggestions' 
                          ? 'bg-white text-blue-700 shadow-sm border border-blue-200' 
                          : 'text-gray-600 hover:text-gray-800 hover:bg-white/50'
                      ]">
                💡 改进建议
              </button>
            </nav>
          </div>

          <!-- 概览选项卡 -->
          <div v-if="activeTab === 'overview'" class="space-y-3">
            <!-- 详细指标 - 现代卡片设计 -->
            <div class="space-y-3">
              <h4 class="text-sm font-semibold text-gray-800 mb-2 flex items-center gap-2">
                <div class="w-2 h-2 bg-gradient-to-r from-purple-400 to-pink-500 rounded-full"></div>
                {{ t('detail.metricDetails') }}
              </h4>
              <div class="space-y-2">
                <!-- 显示所有9个指标，包括未选择的 -->
                <div v-for="metric in allMetrics" :key="metric.key" 
                     :class="[
                       'group p-3 rounded-lg border transition-all duration-300 hover:shadow-lg hover:-translate-y-0.5',
                       !isMetricSelected(metric.key) ? 'opacity-60 bg-gray-50/50 border-gray-200' : [
                         getScoreClass(getMetricScore(metric.key)) === 'excellent' ? 'bg-gradient-to-br from-green-50 to-emerald-50 border-green-200 shadow-sm' : '',
                         getScoreClass(getMetricScore(metric.key)) === 'good' ? 'bg-gradient-to-br from-blue-50 to-cyan-50 border-blue-200 shadow-sm' : '',
                         getScoreClass(getMetricScore(metric.key)) === 'average' ? 'bg-gradient-to-br from-yellow-50 to-orange-50 border-yellow-200 shadow-sm' : '',
                         getScoreClass(getMetricScore(metric.key)) === 'poor' ? 'bg-gradient-to-br from-red-50 to-pink-50 border-red-200 shadow-sm' : '',
                         getScoreClass(getMetricScore(metric.key)) === 'very-poor' ? 'bg-gradient-to-br from-gray-50 to-slate-50 border-gray-200 shadow-sm' : ''
                       ]
                     ]"
                >
                  <div class="flex justify-between items-start mb-2">
                    <h5 :class="[
                      'font-semibold text-sm flex items-center gap-2',
                      isMetricSelected(metric.key) ? 'text-gray-800' : 'text-gray-500'
                    ]">
                      {{ metric.name }}
                      <span v-if="!isMetricSelected(metric.key)" class="text-xs text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded">{{ t('detail.disabled') }}</span>
                    </h5>
                    <span 
                      :class="[
                        'px-2 py-1 rounded-full text-xs font-bold shadow-sm',
                        !isMetricSelected(metric.key) ? 'bg-gray-300 text-gray-600' : [
                          getScoreClass(getMetricScore(metric.key)) === 'excellent' ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white' : '',
                          getScoreClass(getMetricScore(metric.key)) === 'good' ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white' : '',
                          getScoreClass(getMetricScore(metric.key)) === 'average' ? 'bg-gradient-to-r from-yellow-500 to-orange-500 text-gray-800' : '',
                          getScoreClass(getMetricScore(metric.key)) === 'poor' ? 'bg-gradient-to-r from-red-500 to-pink-500 text-white' : '',
                          getScoreClass(getMetricScore(metric.key)) === 'very-poor' ? 'bg-gradient-to-r from-gray-500 to-slate-500 text-white' : ''
                        ]
                      ]"
                    >
                      {{ isMetricSelected(metric.key) ? (getMetricScore(metric.key) * 100).toFixed(0) + '%' : 'N/A' }}
                    </span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-1.5 mb-2 overflow-hidden">
                    <div 
                      :class="[
                        'h-1.5 rounded-full transition-all duration-500 ease-out',
                        !isMetricSelected(metric.key) ? 'bg-gray-400' : [
                          getScoreClass(getMetricScore(metric.key)) === 'excellent' ? 'bg-gradient-to-r from-green-500 to-emerald-500' : '',
                          getScoreClass(getMetricScore(metric.key)) === 'good' ? 'bg-gradient-to-r from-blue-500 to-cyan-500' : '',
                          getScoreClass(getMetricScore(metric.key)) === 'average' ? 'bg-gradient-to-r from-yellow-500 to-orange-500' : '',
                          getScoreClass(getMetricScore(metric.key)) === 'poor' ? 'bg-gradient-to-r from-red-500 to-pink-500' : '',
                          getScoreClass(getMetricScore(metric.key)) === 'very-poor' ? 'bg-gradient-to-r from-gray-500 to-slate-500' : ''
                        ]
                      ]"
                      :style="{ width: isMetricSelected(metric.key) ? `${getMetricScore(metric.key) * 100}%` : '0%' }"
                    ></div>
                  </div>
                  <p :class="[
                    'text-xs leading-relaxed',
                    isMetricSelected(metric.key) ? 'text-gray-600' : 'text-gray-400'
                  ]">
                    {{ isMetricSelected(metric.key) ? getMetricDescription(metric.key, getMetricScore(metric.key)) : metric.description }}
                  </p>
                </div>
              </div>
            </div>
          
          </div>
          
          <!-- 详细分析选项卡 -->
          <div v-if="activeTab === 'detailed'" class="space-y-3">
            <AnalysisReport 
              :scores="detailedScores"
              :overall-score="overallScore"
              :grade="grade || '未知'"
              :dungeon-name="dungeonName"
            />
          </div>
          
          <!-- 改进建议选项卡 -->
          <div v-if="activeTab === 'suggestions'" class="space-y-3">
            <ImprovementSuggestions 
              :scores="detailedScores"
              :overall-score="overallScore"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import DungeonVisualizer from './DungeonVisualizer.vue'
import AnalysisReport from './AnalysisReport.vue'
import ImprovementSuggestions from './ImprovementSuggestions.vue'
import { DungeonAPI } from '../services/api'
import type { DungeonData, Room, Corridor } from '../types/dungeon'
import { Dialog, DialogPanel, DialogTitle } from '@headlessui/vue'


interface ImprovementSuggestion {
  title: string
  description: string
}

interface Props {
  dungeonName: string
  fileId?: string
  filename?: string
  autoLoad?: boolean
}

interface Emits {
  (e: 'export', data: any): void
  (e: 'refresh'): void
  (e: 'error', error: string): void
  (e: 'loaded', data: any): void
}

const props = withDefaults(defineProps<Props>(), {
  autoLoad: true
})

const emit = defineEmits<Emits>()

const { t } = useI18n()

const dungeonData = ref<DungeonData | undefined>(undefined)
const overallScore = ref(0)
const detailedScores = ref<Record<string, { score: number; detail?: any }>>({})
const loading = ref(false)
const error = ref<string | null>(null)
const imageData = ref<string | null>(null)
const selectedRoom = ref<Room | null>(null)
const selectedMetrics = ref<string[]>([])
const activeTab = ref<'overview' | 'detailed' | 'suggestions'>('overview')
const visualizationMode = ref<'canvas' | 'image'>('canvas')
const showFullscreenImage = ref(false)
const grade = ref<string>('未知')

// 从localStorage获取选中的指标
const loadSelectedMetrics = () => {
  const saved = localStorage.getItem('selectedMetrics')
  if (saved) {
    try {
      selectedMetrics.value = JSON.parse(saved)
      console.log('从localStorage加载指标选择:', selectedMetrics.value)
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
    console.log('使用默认指标配置（全部9个）:', selectedMetrics.value)
  }
}

// 检查指标是否被选中
const isMetricSelected = (metric: string): boolean => {
  // 如果没有选择任何指标，默认显示所有指标为启用状态
  if (selectedMetrics.value.length === 0) {
    return true
  }
  // 如果选择了所有9个指标，也显示为启用状态
  if (selectedMetrics.value.length === 9) {
    return true
  }
  // 检查指标是否在选择列表中
  return selectedMetrics.value.includes(metric)
}

// 获取分析结果
const fetchAnalysisResult = async () => {
  try {
    loading.value = true
    error.value = null
    
    console.log('获取分析结果，地下城名称:', props.dungeonName, '文件ID:', props.fileId, '文件名:', props.filename)
    
    // 优先使用文件ID，如果没有则使用文件名
    if (props.fileId) {
      console.log('使用文件ID进行查询:', props.fileId)
      
      // 获取分析结果
      try {
        const analysisResult = await DungeonAPI.analyzeDungeonById(props.fileId)
        console.log('分析结果:', analysisResult)
        
        if (analysisResult.success && analysisResult.result) {
          const assessment = analysisResult.result
          console.log('评估数据:', assessment)
          
          overallScore.value = assessment.overall_score || 0
          grade.value = assessment.grade || '未知'
          console.log('整体分数:', overallScore.value, '等级:', grade.value)
          
          // 处理详细分数 - 保持完整的数据结构
          const scores = assessment.scores || {}
          detailedScores.value = scores
          console.log('处理后的分数:', scores)
          
          // 如果没有整体分数，计算平均分
          if (!assessment.overall_score && Object.keys(scores).length > 0) {
            const totalScore = Object.values(scores).reduce((sum, scoreData) => {
              return sum + (typeof scoreData === 'object' && scoreData.score ? scoreData.score : 0)
            }, 0)
            overallScore.value = (totalScore / Object.keys(scores).length)
            console.log('计算的整体分数:', overallScore.value)
          }
        }
      } catch (analysisErr) {
        console.error('通过文件ID获取分析结果失败:', analysisErr)
        
        // 检查是否是404错误（文件ID过期）
        if (analysisErr instanceof Error && analysisErr.message.includes('404')) {
          error.value = '文件ID已过期，请重新上传文件进行分析'
          emit('error', '文件ID已过期，请重新上传文件进行分析')
        } else {
          error.value = '获取分析结果失败'
          emit('error', '获取分析结果失败')
        }
        return
      }
      
      // 获取可视化数据
      try {
        console.log('正在获取可视化数据，文件ID:', props.fileId)
        const result = await DungeonAPI.getVisualizationDataById(props.fileId)
        console.log('可视化数据结果:', result)
        if (result.success && result.visualization_data) {
          dungeonData.value = result.visualization_data
          console.log('可视化数据设置成功:', dungeonData.value)
        } else {
          console.warn('可视化数据获取失败或为空:', result)
        }
      } catch (dataErr) {
        console.error('通过文件ID获取可视化数据失败:', dataErr)
      }
      
      // 生成图像
      try {
        console.log('正在生成图像，文件ID:', props.fileId)
        const imageResult = await DungeonAPI.visualizeDungeonById(props.fileId, {
          show_connections: true,
          show_room_ids: true,
          show_grid: true,
          show_game_elements: true
        })
        
        console.log('图像生成结果:', imageResult)
        if (imageResult.success && imageResult.image_data) {
          imageData.value = imageResult.image_data
          console.log('图像生成成功，数据长度:', imageResult.image_data.length)
        } else {
          console.warn('图像生成失败或为空:', imageResult)
        }
      } catch (imageErr) {
        console.error('通过文件ID生成图像失败:', imageErr)
      }
      
    } else if (props.filename) {
      console.log('使用文件名进行查询:', props.filename)
      
      // 获取分析结果
      const analysisResult = await DungeonAPI.analyzeDungeonByFilename(props.filename)
      console.log('分析结果:', analysisResult)
      
      if (analysisResult.success && analysisResult.result) {
        const assessment = analysisResult.result
        console.log('评估数据:', assessment)
        
        overallScore.value = assessment.overall_score || 0
        grade.value = assessment.grade || '未知'
        console.log('整体分数:', overallScore.value, '等级:', grade.value)
        
        // 处理详细分数 - 保持完整的数据结构
        const scores = assessment.scores || {}
        detailedScores.value = scores
        console.log('处理后的分数:', scores)
        
        // 如果没有整体分数，计算平均分
        if (!assessment.overall_score && Object.keys(scores).length > 0) {
          const totalScore = Object.values(scores).reduce((sum, scoreData) => {
            return sum + (typeof scoreData === 'object' && scoreData.score ? scoreData.score : 0)
          }, 0)
          overallScore.value = (totalScore / Object.keys(scores).length)
          console.log('计算的整体分数:', overallScore.value)
        }
      }
      
      // 获取可视化数据
      try {
        const result = await DungeonAPI.getVisualizationDataByFilename(props.filename)
        if (result.success && result.visualization_data) {
          dungeonData.value = result.visualization_data
        }
      } catch (dataErr) {
        console.warn('可视化数据获取失败:', dataErr)
        // 不设置错误，因为可视化数据不是必需的
      }
      
      // 生成图像
      try {
        const imageResult = await DungeonAPI.visualizeDungeonByFilename(props.filename, {
          show_connections: true,
          show_room_ids: true,
          show_grid: true,
          show_game_elements: true
        })
        
        if (imageResult.success && imageResult.image_data) {
          imageData.value = imageResult.image_data
          console.log('图像生成成功')
        }
      } catch (imageErr) {
        console.warn('图像生成失败:', imageErr)
      }
    } else {
      error.value = '缺少文件ID或文件名'
      emit('error', '缺少文件ID或文件名')
      return
    }
    
    // 自动设置可视化模式
    if (imageData.value && !dungeonData.value) {
      visualizationMode.value = 'image'
    } else if (dungeonData.value && !imageData.value) {
      visualizationMode.value = 'canvas'
    } else if (dungeonData.value && imageData.value) {
      visualizationMode.value = 'canvas' // 默认优先使用交互式
    }
    
    // 发出加载完成事件
    emit('loaded', {
      dungeonName: props.dungeonName,
      overallScore: overallScore.value,
      detailedScores: detailedScores.value,
      dungeonData: dungeonData.value,
      imageData: imageData.value,
      grade: grade.value
    })
    
  } catch (err) {
    console.error('获取分析结果时出错:', err)
    error.value = err instanceof Error ? err.message : '获取数据失败'
    emit('error', error.value)
    
    // 清空数据
    overallScore.value = 0
    detailedScores.value = {}
  } finally {
    loading.value = false
  }
}

// 监听数据变化
watch(() => dungeonData.value, (newData) => {
  console.log('DungeonData changed:', newData)
  console.log('Rooms count:', newData?.rooms.length)
  console.log('Corridors count:', newData?.corridors.length)
}, { deep: true })

// 监听props变化，重新加载数据
watch(() => props.dungeonName, async (newDungeonName, oldDungeonName) => {
  console.log('DungeonName changed:', oldDungeonName, '->', newDungeonName)
  if (newDungeonName && newDungeonName !== oldDungeonName) {
    console.log('重新加载地下城数据:', newDungeonName)
    // 清空之前的数据
    dungeonData.value = undefined
    overallScore.value = 0
    detailedScores.value = {}
    imageData.value = null
    error.value = null
    loading.value = true
    
    // 重新获取数据
    await fetchAnalysisResult()
  }
}, { immediate: false })

// 监听fileId变化
watch(() => props.fileId, async (newFileId, oldFileId) => {
  console.log('FileId changed:', oldFileId, '->', newFileId)
  if (newFileId && newFileId !== oldFileId) {
    console.log('重新加载地下城数据，文件ID:', newFileId)
    // 清空之前的数据
    dungeonData.value = undefined
    overallScore.value = 0
    detailedScores.value = {}
    imageData.value = null
    error.value = null
    loading.value = true
    
    // 重新获取数据
    await fetchAnalysisResult()
  }
}, { immediate: false })

const improvementSuggestions = computed<ImprovementSuggestion[]>(() => {
  const suggestions: ImprovementSuggestion[] = []
  
  // 死胡同比例建议
  if (detailedScores.value.dead_end_ratio < 0.5) {
    suggestions.push({
      title: t('suggestions.deadEndRatio.title'),
      description: t('suggestions.deadEndRatio.description')
    })
  } else if (detailedScores.value.dead_end_ratio < 0.7) {
    suggestions.push({
      title: t('suggestions.deadEndRatioOptimize.title'),
      description: t('suggestions.deadEndRatioOptimize.description')
    })
  }
  
  // 几何平衡建议
  if (detailedScores.value.geometric_balance < 0.7) {
    suggestions.push({
      title: t('suggestions.geometricBalance.title'),
      description: t('suggestions.geometricBalance.description')
    })
  }
  
  // 宝藏怪物分布建议
  if (detailedScores.value.treasure_monster_distribution < 0.5) {
    suggestions.push({
      title: t('suggestions.treasureMonsterDistribution.title'),
      description: t('suggestions.treasureMonsterDistribution.description')
    })
  } else if (detailedScores.value.treasure_monster_distribution < 0.7) {
    suggestions.push({
      title: t('suggestions.treasureMonsterDistributionBalance.title'),
      description: t('suggestions.treasureMonsterDistributionBalance.description')
    })
  }
  
  // 可达性建议
  if (detailedScores.value.accessibility < 0.7) {
    suggestions.push({
      title: t('suggestions.accessibility.title'),
      description: t('suggestions.accessibility.description')
    })
  }
  
  // 路径多样性建议
  if (detailedScores.value.path_diversity < 0.5) {
    suggestions.push({
      title: t('suggestions.pathDiversity.title'),
      description: t('suggestions.pathDiversity.description')
    })
  } else if (detailedScores.value.path_diversity < 0.7) {
    suggestions.push({
      title: t('suggestions.pathDiversityOptimize.title'),
      description: t('suggestions.pathDiversityOptimize.description')
    })
  }
  
  // 环路比例建议
  if (detailedScores.value.loop_ratio < 0.3) {
    suggestions.push({
      title: t('suggestions.loopRatio.title'),
      description: t('suggestions.loopRatio.description')
    })
  } else if (detailedScores.value.loop_ratio < 0.5) {
    suggestions.push({
      title: t('suggestions.loopRatioOptimize.title'),
      description: t('suggestions.loopRatioOptimize.description')
    })
  }
  
  // 度方差建议
  if (detailedScores.value.degree_variance < 0.5) {
    suggestions.push({
      title: t('suggestions.degreeVariance.title'),
      description: t('suggestions.degreeVariance.description')
    })
  }
  
  // 门分布建议
  if (detailedScores.value.door_distribution < 0.5) {
    suggestions.push({
      title: t('suggestions.doorDistribution.title'),
      description: t('suggestions.doorDistribution.description')
    })
  }
  
  // 关键路径长度建议
  if (detailedScores.value.key_path_length < 0.5) {
    suggestions.push({
      title: t('suggestions.keyPathLength.title'),
      description: t('suggestions.keyPathLength.description')
    })
  }
  
  // 基于具体数据的建议
  if (dungeonData.value) {
    const roomCount = dungeonData.value.rooms?.length || 0
    const corridorCount = dungeonData.value.corridors?.length || 0
    
    // 房间数量建议
    if (roomCount < 10) {
      suggestions.push({
        title: t('suggestions.roomCount.title'),
        description: t('suggestions.roomCount.description', { count: roomCount })
      })
    } else if (roomCount > 30) {
      suggestions.push({
        title: t('suggestions.roomCountOptimize.title'),
        description: t('suggestions.roomCountOptimize.description', { count: roomCount })
      })
    }
    
    // 通道密度建议
    const corridorRatio = corridorCount / roomCount
    if (corridorRatio < 0.8) {
      suggestions.push({
        title: t('suggestions.corridorDensity.title'),
        description: t('suggestions.corridorDensity.description')
      })
    } else if (corridorRatio > 2.0) {
      suggestions.push({
        title: t('suggestions.corridorDensityOptimize.title'),
        description: t('suggestions.corridorDensityOptimize.description')
      })
    }
  }
  
  // 总体评分建议
  if (overallScore.value < 0.5) {
    suggestions.push({
      title: t('suggestions.overallScoreRedesign.title'),
      description: t('suggestions.overallScoreRedesign.description')
    })
  } else if (overallScore.value < 0.7) {
    suggestions.push({
      title: t('suggestions.overallScoreOptimize.title'),
      description: t('suggestions.overallScoreOptimize.description')
    })
  } else if (overallScore.value >= 0.8) {
    suggestions.push({
      title: t('suggestions.overallScoreExcellent.title'),
      description: t('suggestions.overallScoreExcellent.description')
    })
  }
  
  // 如果没有具体建议，提供一般性建议
  if (suggestions.length === 0) {
    suggestions.push({
      title: t('suggestions.continuousOptimization.title'),
      description: t('suggestions.continuousOptimization.description')
    })
  }
  
  return suggestions
})

const getScoreClass = (score: number): string => {
  if (score >= 0.8) return 'excellent'
  if (score >= 0.65) return 'good'
  if (score >= 0.5) return 'average'
  if (score >= 0.35) return 'poor'
  return 'very-poor'
}

const getScoreDescription = (score: number): string => {
  if (score >= 0.8) return t('detail.scoreDescription.excellent')
  if (score >= 0.65) return t('detail.scoreDescription.good')
  if (score >= 0.5) return t('detail.scoreDescription.average')
  if (score >= 0.35) return t('detail.scoreDescription.poor')
  return t('detail.scoreDescription.poor')
}

// 获取指标名称
const getMetricName = (metric: string): string => {
  return t(`metrics.${metric}`)
}

// 获取指标描述
const getMetricDescription = (metric: string, score: number): string => {
  const scoreClass = getScoreClass(score)
  const description = t(`metricDescriptions.${metric}.description`)
  const quality = scoreClass === 'excellent' || scoreClass === 'good' ? 'good' : 'poor'
  const qualityText = t(`metricDescriptions.${metric}.${quality}`)
  return `${description} ${qualityText}`
}

// 获取指标分数
const getMetricScore = (metric: string): number => {
  return detailedScores.value[metric]?.score || 0
}

// 定义所有指标的名称和描述
const allMetrics = computed(() => {
  return [
    { key: 'dead_end_ratio', name: getMetricName('dead_end_ratio'), description: getMetricDescription('dead_end_ratio', 0) },
    { key: 'geometric_balance', name: getMetricName('geometric_balance'), description: getMetricDescription('geometric_balance', 0) },
    { key: 'treasure_monster_distribution', name: getMetricName('treasure_monster_distribution'), description: getMetricDescription('treasure_monster_distribution', 0) },
    { key: 'accessibility', name: getMetricName('accessibility'), description: getMetricDescription('accessibility', 0) },
    { key: 'path_diversity', name: getMetricName('path_diversity'), description: getMetricDescription('path_diversity', 0) },
    { key: 'loop_ratio', name: getMetricName('loop_ratio'), description: getMetricDescription('loop_ratio', 0) },
    { key: 'degree_variance', name: getMetricName('degree_variance'), description: getMetricDescription('degree_variance', 0) },
    { key: 'door_distribution', name: getMetricName('door_distribution'), description: getMetricDescription('door_distribution', 0) },
    { key: 'key_path_length', name: getMetricName('key_path_length'), description: getMetricDescription('key_path_length', 0) }
  ]
})

const handleRoomClick = (room: Room) => {
  selectedRoom.value = room
}

const handleCorridorClick = (corridor: Corridor) => {
  console.log('点击通道:', corridor)
}

const closeRoomModal = () => {
  selectedRoom.value = null
}

const refresh = () => {
  console.log('Refreshing dungeon detail...')
  emit('refresh')
  fetchAnalysisResult()
}

const exportReport = async () => {
  console.log('Exporting report...')
  
  try {
    // 创建详细的报告数据
    const reportData = {
      dungeon_name: props.dungeonName,
      analysis_date: new Date().toISOString(),
      overall_score: overallScore.value,
      detailed_scores: detailedScores.value,
      dungeon_data: dungeonData.value,
      improvement_suggestions: improvementSuggestions.value,
      summary: {
        grade: getScoreClass(overallScore.value),
        description: getScoreDescription(overallScore.value),
        overall_score: overallScore.value
      }
    }
    
    emit('export', reportData)
    
    console.log('Report data prepared for export:', props.dungeonName)
  } catch (error) {
    console.error('Error preparing report:', error)
    emit('error', '报告准备失败')
  }
}

const goBackToHome = () => {
  console.log('返回主页重新上传')
  window.location.href = '/'
}

// 下载图片功能
const downloadImage = () => {
  if (!imageData.value) return
  
  try {
    // 创建下载链接
    const link = document.createElement('a')
    link.href = `data:image/png;base64,${imageData.value}`
    link.download = `dungeon-${props.dungeonName}-${new Date().toISOString().slice(0, 10)}.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    console.log('图片下载成功')
  } catch (error) {
    console.error('图片下载失败:', error)
  }
}

// 打开全屏图片查看
const openImageFullscreen = () => {
  showFullscreenImage.value = true
}

// 关闭全屏图片查看
const closeFullscreenImage = () => {
  showFullscreenImage.value = false
}

// 暴露方法给父组件
defineExpose({
  fetchAnalysisResult,
  refresh,
  exportReport
})

onMounted(async () => {
  console.log('DungeonDetail mounted')
  
  // 加载选中的指标
  loadSelectedMetrics()
  
  if (props.autoLoad) {
    await fetchAnalysisResult()
  }
})
</script>

<style scoped>
/* 只保留必要的动画 */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 响应式设计优化 */
@media (max-width: 1536px) {
  .grid.grid-cols-1.2xl\:grid-cols-12 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
    gap: 1rem;
  }
  
  .2xl\:col-span-8 {
    grid-column: span 1 / span 1;
  }
  
  .2xl\:col-span-4 {
    grid-column: span 1 / span 1;
  }
}

@media (max-width: 1280px) {
  .grid.grid-cols-1.xl\:grid-cols-5 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
    gap: 1rem;
  }
  
  .xl\:col-span-4 {
    grid-column: span 1 / span 1;
  }
}

@media (max-width: 768px) {
  .grid {
    grid-template-columns: repeat(1, minmax(0, 1fr));
    gap: 0.75rem;
  }
  
  .flex {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .gap-6 {
    gap: 0.75rem;
  }
  
  .p-6 {
    padding: 1rem;
  }
  
  .p-4 {
    padding: 0.75rem;
  }
  
  .text-lg {
    font-size: 1rem;
    line-height: 1.5rem;
  }
  
  .text-base {
    font-size: 0.875rem;
    line-height: 1.25rem;
  }
  
  /* 最小高度在移动端的调整 */
  .min-h-\[600px\] {
    min-height: 400px;
  }
  
  .min-h-\[500px\] {
    min-height: 300px;
  }
  
  /* 全屏图片在移动端的优化 */
  .fixed.inset-0 {
    padding: 0.5rem;
  }
}

@media (max-width: 640px) {
  .text-3xl {
    font-size: 1.25rem;
    line-height: 1.75rem;
  }
  
  .text-xl {
    font-size: 1.125rem;
    line-height: 1.75rem;
  }
  
  .px-6 {
    padding-left: 0.75rem;
    padding-right: 0.75rem;
  }
  
  .py-4 {
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
  }
  
  .gap-4 {
    gap: 0.5rem;
  }
  
  .gap-3 {
    gap: 0.5rem;
  }
  
  .w-10.h-10 {
    width: 2rem;
    height: 2rem;
  }
  
  .w-6.h-6 {
    width: 1.25rem;
    height: 1.25rem;
  }
  
  /* 隐藏移动端不必要的元素 */
  .hidden.sm\:block {
    display: none;
  }
  
  /* 按钮在移动端的优化 */
  .px-3.py-1 {
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
    line-height: 1rem;
  }
}
</style> 