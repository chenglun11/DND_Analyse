<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
    <!-- 顶部导航栏 - 与全局页头配合 -->
    <div class="bg-white/95 backdrop-blur-xl border-b border-gray-200/60 shadow-sm sticky top-16 z-40">
      <div class="max-w-full mx-auto px-4 py-3">
        <div class="flex items-center justify-between">
          <!-- 左侧：返回按钮和标题 -->
          <div class="flex items-center gap-3">
            <button 
              @click="goBack"
              class="flex items-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all duration-300 shadow-sm text-sm font-medium"
              :title="t('detail.backButtonTitle')"
            >
              <ArrowLeftIcon class="w-4 h-4" />
              返回
            </button>
            
            <div class="text-lg font-semibold text-gray-800">
              {{ currentDetail?.name || dungeonName || '地下城详情' }}
            </div>
          </div>
          
          <!-- 右侧：批量概览切换 -->
          <div v-if="isMultiDetail" class="flex items-center gap-3">
            <button 
              @click="showBatchOverview = !showBatchOverview"
              class="flex items-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
              </svg>
              {{ showBatchOverview ? '隐藏概览' : '批量概览' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 多详情导航栏 - 独立于sticky页头 -->
    <div v-if="isMultiDetail && detailList.length > 1" class="bg-white/80 backdrop-blur-sm border-b border-gray-200/60 shadow-sm">
      <div class="max-w-full mx-auto px-4 py-3">
        <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
          <!-- 当前地下城信息 -->
          <div class="flex-1">
            <div class="text-sm text-gray-500">
              第 {{ currentPage }} 页，共 {{ totalPages }} 页
            </div>
          </div>
          
          <!-- 分页控制 -->
          <div class="flex items-center gap-3">
            <button 
              @click="goToPage(currentPage - 1)"
              :disabled="currentPage <= 1"
              class="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm font-medium"
            >
              ← 上一个
            </button>
            
            <div class="flex gap-1">
              <button 
                v-for="page in visiblePages" 
                :key="page"
                @click="page > 0 ? goToPage(page) : null"
                :class="[
                  'px-3 py-2 rounded-lg transition-colors text-sm font-medium',
                  page === currentPage 
                    ? 'bg-blue-600 text-white' 
                    : page > 0
                      ? 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      : 'bg-transparent text-gray-400 cursor-default'
                ]"
                :disabled="page <= 0"
              >
                {{ page > 0 ? page : '...' }}
              </button>
            </div>
            
            <button 
              @click="goToPage(currentPage + 1)"
              :disabled="currentPage >= totalPages"
              class="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm font-medium"
            >
              下一个 →
            </button>
          </div>
        </div>
        
        <!-- 快速导航 -->
        <div class="mt-4">
          <div class="text-sm font-medium text-gray-700 mb-2">快速导航</div>
          <div class="flex flex-wrap gap-2">
            <button 
              v-for="(detail, index) in detailList" 
              :key="detail.name"
              @click="goToPage(index + 1)"
              :class="[
                'px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                currentPage === index + 1
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              ]"
              :title="detail.name"
            >
              {{ detail.name.length > 15 ? detail.name.substring(0, 15) + '...' : detail.name }}
            </button>
          </div>
        </div>
        
        <!-- 键盘导航提示 -->
        <div class="mt-3 p-2 bg-blue-50 border border-blue-200 rounded-lg">
          <div class="flex items-center gap-2 text-sm text-blue-700">
            <span class="text-lg">💡</span>
            <span>键盘快捷键：← → 切换地下城，Home/End 跳转到第一个/最后一个</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 两列布局 -->
    <div class="max-w-full mx-auto p-4">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-4">
        <!-- 左侧边栏：操作面板 -->
        <div class="lg:col-span-2">
          <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-3 sticky top-24">
            <h3 class="text-base font-semibold text-gray-800 mb-3">操作</h3>
            
            <!-- 基础操作 -->
            <div class="space-y-2 mb-4">
              <button 
                @click="refreshData"
                class="w-full flex items-center gap-2 px-2 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
                刷新
              </button>
              
              <button 
                @click="exportReport"
                class="w-full flex items-center gap-2 px-2 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                导出
              </button>
            </div>
            
            <!-- 批量操作 -->
            <div v-if="isMultiDetail" class="space-y-2 mb-4">
              <button 
                @click="exportBatchReport"
                class="w-full flex items-center gap-2 px-2 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                导出全部
              </button>
            </div>
            
            <!-- 当前信息 -->
            <div class="space-y-2">
              <div class="bg-gray-50 rounded-lg p-2">
                <div class="text-xs text-gray-600 mb-1">当前地下城</div>
                <div class="text-xs font-medium text-gray-800 truncate">
                  {{ currentDetail?.name || dungeonName || '未知' }}
                </div>
              </div>
              
              <div v-if="isMultiDetail" class="bg-gray-50 rounded-lg p-2">
                <div class="text-xs text-gray-600 mb-1">进度</div>
                <div class="text-xs font-medium text-gray-800">
                  {{ currentPage }} / {{ totalPages }}
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 右侧：主要内容区域 -->
        <div class="lg:col-span-10">
          <!-- 批量评估概览面板 -->
          <div v-if="showBatchOverview" class="bg-white rounded-xl shadow-lg border border-gray-200 p-6 mb-6">
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-xl font-bold text-gray-800">批量评估概览</h3>
              <div class="flex gap-2">
                <button 
                  @click="showBatchOverview = false"
                  class="px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm"
                >
                  关闭概览
                </button>
              </div>
            </div>
            
            <!-- 统计卡片 -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div class="bg-gradient-to-br from-green-50 to-green-100 border border-green-200 rounded-xl p-4 text-center">
                <div class="text-2xl font-bold text-green-600">{{ excellentCount }}</div>
                <div class="text-sm text-green-700 font-medium">优秀</div>
              </div>
              <div class="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-xl p-4 text-center">
                <div class="text-2xl font-bold text-blue-600">{{ goodCount }}</div>
                <div class="text-sm text-blue-700 font-medium">良好</div>
              </div>
              <div class="bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200 rounded-xl p-4 text-center">
                <div class="text-2xl font-bold text-yellow-600">{{ averageCount }}</div>
                <div class="text-sm text-yellow-700 font-medium">一般</div>
              </div>
              <div class="bg-gradient-to-br from-red-50 to-red-100 border border-red-200 rounded-xl p-4 text-center">
                <div class="text-2xl font-bold text-red-600">{{ poorCount }}</div>
                <div class="text-sm text-red-700 font-medium">需改进</div>
              </div>
            </div>
            
            <!-- 筛选和排序控制 -->
            <div class="flex flex-col md:flex-row gap-4 mb-6">
              <div class="flex-1">
                <label class="block text-sm font-medium text-gray-700 mb-2">排序方式</label>
                <select v-model="sortBy" @change="sortDetails" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm">
                  <option value="name">按名称排序</option>
                  <option value="score">按评分排序</option>
                  <option value="grade">按等级排序</option>
                </select>
              </div>
              
              <div class="flex-1">
                <label class="block text-sm font-medium text-gray-700 mb-2">筛选等级</label>
                <select v-model="filterBy" @change="filterDetails" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm">
                  <option value="all">全部等级</option>
                  <option value="excellent">仅优秀</option>
                  <option value="good">仅良好</option>
                  <option value="average">仅一般</option>
                  <option value="poor">仅需改进</option>
                </select>
              </div>
            </div>
            
            <!-- 地下城卡片网格 -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              <div v-for="(detail, index) in filteredDetailList" :key="detail.name" 
                   :class="[
                     'border-2 rounded-xl p-4 hover:shadow-lg transition-all duration-200 cursor-pointer transform hover:scale-105',
                     currentDetail?.name === detail.name 
                       ? 'border-blue-400 bg-blue-50 shadow-lg' 
                       : 'border-gray-200 bg-white hover:border-gray-300'
                   ]"
                   @click="goToDetail(detail.name)">
                <div class="flex items-start justify-between mb-3">
                  <h4 class="font-semibold text-gray-800 text-sm leading-tight">{{ detail.name }}</h4>
                  <span :class="[
                    'px-2 py-1 rounded-full text-xs font-medium',
                    getScoreClass(detail.overallScore || 0) === 'excellent' ? 'bg-green-100 text-green-700' :
                    getScoreClass(detail.overallScore || 0) === 'good' ? 'bg-blue-100 text-blue-700' :
                    getScoreClass(detail.overallScore || 0) === 'average' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-red-100 text-red-700'
                  ]">
                    {{ getScoreClass(detail.overallScore || 0) === 'excellent' ? '优秀' :
                       getScoreClass(detail.overallScore || 0) === 'good' ? '良好' :
                       getScoreClass(detail.overallScore || 0) === 'average' ? '一般' : '需改进' }}
                  </span>
                </div>
                
                <div class="space-y-2">
                  <div class="text-xs text-gray-500 truncate">{{ detail.filename }}</div>
                  <div class="flex items-center justify-between">
                    <span class="text-lg font-bold" :class="[
                      getScoreClass(detail.overallScore || 0) === 'excellent' ? 'text-green-600' :
                      getScoreClass(detail.overallScore || 0) === 'good' ? 'text-blue-600' :
                      getScoreClass(detail.overallScore || 0) === 'average' ? 'text-yellow-600' :
                      'text-red-600'
                    ]">
                      {{ detail.score?.toFixed(2) || detail.overallScore?.toFixed(2) || '0.00' }}
                    </span>
                    <span class="text-xs text-gray-400">{{ index + 1 }}/{{ filteredDetailList.length }}</span>
                  </div>
                  
                  <button class="w-full mt-3 bg-blue-600 text-white px-3 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
                    {{ currentDetail?.name === detail.name ? '当前查看' : '查看详情' }}
                  </button>
                </div>
              </div>
            </div>
            
            <div v-if="filteredDetailList.length === 0" class="text-center py-8 text-gray-500">
              <div class="text-4xl mb-2">📭</div>
              <div class="text-lg font-medium">没有找到匹配的地下城</div>
              <div class="text-sm">请尝试调整筛选条件</div>
            </div>
          </div>

          <!-- 主要内容区域 -->
          <div class="max-w-full mx-auto px-6 py-6">
            <!-- 批量概览面板 -->
            <div v-if="isMultiDetail && showBatchOverview" class="mb-8">
              <div class="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 p-6">
                <div class="flex items-center justify-between mb-6">
                  <h2 class="text-2xl font-bold text-gray-800">批量分析概览</h2>
                  <div class="text-sm text-gray-600">
                    共 {{ detailList.length }} 个地下城
                  </div>
                </div>
                
                <!-- 统计卡片 -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                  <div class="bg-gradient-to-br from-blue-500 to-blue-600 text-white p-6 rounded-xl shadow-lg">
                    <div class="text-3xl font-bold">{{ averageScore.toFixed(1) }}</div>
                    <div class="text-blue-100">平均评分</div>
                  </div>
                  <div class="bg-gradient-to-br from-green-500 to-green-600 text-white p-6 rounded-xl shadow-lg">
                    <div class="text-3xl font-bold">{{ bestScore.toFixed(1) }}</div>
                    <div class="text-green-100">最高评分</div>
                  </div>
                  <div class="bg-gradient-to-br from-purple-500 to-purple-600 text-white p-6 rounded-xl shadow-lg">
                    <div class="text-3xl font-bold">{{ detailList.length }}</div>
                    <div class="text-purple-100">地下城数量</div>
                  </div>
                </div>
                
                <!-- 过滤和排序 -->
                <div class="flex flex-col lg:flex-row gap-4 mb-6">
                  <div class="flex-1">
                    <label class="block text-sm font-medium text-gray-700 mb-2">排序方式</label>
                    <select 
                      v-model="sortBy" 
                      class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="name">按名称</option>
                      <option value="score">按评分</option>
                      <option value="index">按顺序</option>
                    </select>
                  </div>
                  <div class="flex-1">
                    <label class="block text-sm font-medium text-gray-700 mb-2">评分范围</label>
                    <select 
                      v-model="scoreFilter" 
                      class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="all">全部</option>
                      <option value="high">高分 (8.0+)</option>
                      <option value="medium">中等 (5.0-8.0)</option>
                      <option value="low">低分 (<5.0)</option>
                    </select>
                  </div>
                </div>
                
                <!-- 地下城卡片网格 -->
                <div class="grid xl:grid-cols-4 gap-6">
                  <div 
                    v-for="(detail, index) in filteredAndSortedDetails" 
                    :key="detail.name"
                    class="bg-white/60 backdrop-blur-sm rounded-xl shadow-md border border-white/20 hover:shadow-lg transition-all duration-300 cursor-pointer"
                    :class="currentPage === index + 1 ? 'ring-2 ring-blue-500 bg-blue-50/80' : ''"
                    @click="goToPage(index + 1)"
                  >
                    <div class="p-6">
                      <div class="flex items-start justify-between mb-4">
                        <div class="flex-1">
                          <h3 class="text-lg font-semibold text-gray-800 mb-2 line-clamp-2">
                            {{ detail.name }}
                          </h3>
                          <div class="text-sm text-gray-600">
                            第 {{ index + 1 }} 个地下城
                          </div>
                        </div>
                        <div class="flex flex-col items-end">
                          <div class="text-2xl font-bold text-gray-800">
                            {{ detail.score?.toFixed(1) || 'N/A' }}
                          </div>
                          <div class="text-xs text-gray-500">
                            {{ getGradeLabel(detail.score) }}
                          </div>
                        </div>
                      </div>
                      
                      <div class="flex items-center justify-between">
                        <div class="text-sm text-gray-600">
                          {{ currentPage === index + 1 ? '当前' : '查看详情' }}
                        </div>
                        <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                          <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                          </svg>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- 空状态 -->
                <div v-if="filteredAndSortedDetails.length === 0" class="text-center py-12">
                  <div class="text-gray-400 text-lg">没有找到匹配的地下城</div>
                </div>
              </div>
            </div>

            <!-- 主要内容网格 -->
            <div class="grid lg:grid-cols-12 gap-8">
              <!-- 主要内容区域 -->
              <div class="lg:col-span-12">
                <DungeonDetail 
                  v-if="currentDetail"
                  :dungeon-name="currentDetail.name"
                  :file-id="currentDetail.fileId"
                  :scores="currentDetail.score"
                  :selected-metrics="selectedMetrics"
                  :visualization-mode="visualizationMode"
                  @visualization-mode-change="visualizationMode = $event"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, watch, nextTick, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { TabGroup, TabList, Tab, TabPanels, TabPanel } from '@headlessui/vue'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { ArrowLeftIcon, DocumentArrowDownIcon } from '@heroicons/vue/24/outline'
import DungeonDetail from '../components/DungeonDetail.vue'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()

// 分页相关
const currentPage = ref(1)
const itemsPerPage = 1 // 每页显示1个详情
const forceUpdate = ref(0) // 强制更新计数器

// 多详情相关
const detailList = ref<any[]>([])
const showBatchOverview = ref(false)

// 批量评估相关
const sortBy = ref('name')
const filterBy = ref('all')
const filteredDetailList = ref<any[]>([])

// Headless UI 状态
const showExportDialog = ref(false)
const pendingExportData = ref<any>(null)

// 监听detailList变化
watch(detailList, (newList) => {
  console.log('详情列表变化:', newList.length, '项')
  if (newList.length > 0 && currentPage.value > Math.ceil(newList.length / itemsPerPage)) {
    console.log('当前页超出范围，重置到第一页')
    currentPage.value = 1
  }
  // 更新筛选后的列表
  filterAndSortDetails()
}, { deep: true })

// 监听当前页变化
watch(currentPage, (newPage) => {
  console.log('当前页变化:', newPage)
})

const goBack = () => {
  // 直接返回主页，而不是使用浏览器历史记录
  router.push('/')
}

// 判断是否为多详情模式
const isMultiDetail = computed(() => {
  // 检查路由名称或参数
  return route.name === 'detail-multi' || route.params.names !== undefined
})

// 页面标题
const pageTitle = computed(() => {
  if (isMultiDetail.value) {
    return `${t('detail.multipleDetails')} (${detailList.value.length})`
  }
  return dungeonName.value
})

// 单个详情相关
const dungeonName = computed(() => {
  return route.params.name as string || t('common.unknown')
})

const fileId = computed(() => {
  return route.params.fileId as string
})

const filename = computed(() => {
  return route.params.filename as string
})

// 批量评估统计
const excellentCount = computed(() => {
  return detailList.value.filter(d => getScoreClass(d.overallScore || 0) === 'excellent').length
})

const goodCount = computed(() => {
  return detailList.value.filter(d => getScoreClass(d.overallScore || 0) === 'good').length
})

const averageCount = computed(() => {
  return detailList.value.filter(d => getScoreClass(d.overallScore || 0) === 'average').length
})

const poorCount = computed(() => {
  return detailList.value.filter(d => getScoreClass(d.overallScore || 0) === 'poor' || getScoreClass(d.overallScore || 0) === 'very-poor').length
})

// 筛选和排序
const filterAndSortDetails = () => {
  let filtered = [...detailList.value]
  
  // 筛选
  if (filterBy.value !== 'all') {
    filtered = filtered.filter(detail => {
      const scoreClass = getScoreClass(detail.overallScore || 0)
      switch (filterBy.value) {
        case 'excellent':
          return scoreClass === 'excellent'
        case 'good':
          return scoreClass === 'good'
        case 'average':
          return scoreClass === 'average'
        case 'poor':
          return scoreClass === 'poor' || scoreClass === 'very-poor'
        default:
          return true
      }
    })
  }
  
  // 排序
  filtered.sort((a, b) => {
    switch (sortBy.value) {
      case 'score':
        return (b.overallScore || 0) - (a.overallScore || 0)
      case 'grade':
        return getScoreClass(a.overallScore || 0).localeCompare(getScoreClass(b.overallScore || 0))
      case 'name':
      default:
        return a.name.localeCompare(b.name)
    }
  })
  
  filteredDetailList.value = filtered
}

const sortDetails = () => {
  filterAndSortDetails()
}

const filterDetails = () => {
  filterAndSortDetails()
}

// 导航到指定详情
const goToDetail = (name: string) => {
  const originalIndex = detailList.value.findIndex(d => d.name === name)
  if (originalIndex !== -1) {
    currentPage.value = originalIndex + 1
    showBatchOverview.value = false
  }
}

const viewDetail = (index: number) => {
  goToDetail(detailList.value[index].name)
}

// 分页计算
const totalPages = computed(() => {
  const pages = Math.ceil(detailList.value.length / itemsPerPage)
  console.log('总页数计算:', detailList.value.length, '/', itemsPerPage, '=', pages)
  return pages
})

const currentPageStart = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage + 1
  console.log('当前页起始索引:', start)
  return start
})

const currentPageEnd = computed(() => {
  const end = Math.min(currentPage.value * itemsPerPage, detailList.value.length)
  console.log('当前页结束索引:', end)
  return end
})

const currentDetail = computed(() => {
  if (!isMultiDetail.value || detailList.value.length === 0) {
    console.log('没有多详情数据或详情列表为空')
    return null
  }
  const index = (currentPage.value - 1) * itemsPerPage
  const detail = detailList.value[index]
  console.log('当前详情计算:', {
    currentPage: currentPage.value,
    index: index,
    totalItems: detailList.value.length,
    detail: detail,
    detailList: detailList.value
  })
  return detail
})

const visiblePages = computed(() => {
  const pages: number[] = []
  const total = totalPages.value
  const current = currentPage.value
  
  console.log('计算可见页码，总页数:', total, '当前页:', current)
  
  if (total <= 7) {
    // 如果总页数少于等于7，显示所有页码
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    // 如果总页数大于7，显示当前页附近的页码
    const start = Math.max(1, current - 3)
    const end = Math.min(total, current + 3)
    
    // 确保显示第一页和最后一页
    if (start > 1) {
      pages.push(1)
      if (start > 2) {
        pages.push(-1) // 表示省略号
      }
    }
    
    for (let i = start; i <= end; i++) {
      pages.push(i)
    }
    
    if (end < total) {
      if (end < total - 1) {
        pages.push(-1) // 表示省略号
      }
      pages.push(total)
    }
  }
  
  console.log('可见页码:', pages)
  return pages
})

// Tab切换处理
const handleTabChange = (index: number) => {
  console.log('Tab切换:', index)
  currentPage.value = index + 1
  forceUpdate.value++
}

// 分页导航
const goToPage = (page: number) => {
  console.log('尝试跳转到页面:', page, '总页数:', totalPages.value)
  if (page >= 1 && page <= totalPages.value) {
    console.log('页面跳转前 - 当前页:', currentPage.value)
    currentPage.value = page
    forceUpdate.value++ // 强制重新渲染
    console.log('页面跳转后 - 当前页:', currentPage.value)
    console.log('成功跳转到页面:', page)
    
    // 强制触发响应式更新
    nextTick(() => {
      console.log('nextTick后 - 当前页:', currentPage.value)
      console.log('nextTick后 - 当前详情:', currentDetail.value)
    })
  } else {
    console.warn('页面跳转失败，页码超出范围:', page)
  }
}

// 初始化多详情数据
const initMultiDetails = () => {
  if (!isMultiDetail.value) return
  
  const names = route.params.names as string
  if (!names) return
  
  console.log('初始化多详情数据，names参数:', names)
  
  // 从localStorage获取分析结果
  const analysisResults = localStorage.getItem('analysisResults')
  if (analysisResults) {
    try {
      const results = JSON.parse(analysisResults)
      console.log('从localStorage获取的分析结果:', results)
      
      detailList.value = results.map((result: any) => ({
        name: result.name,
        fileId: result.fileId || result.id,
        filename: result.filename || result.name,
        overallScore: result.overallScore,
        grade: result.grade
      }))
      
      console.log('处理后的详情列表:', detailList.value)
      
      // 重置到第一页
      currentPage.value = 1
      
      // 初始化筛选和排序
      filterAndSortDetails()
    } catch (error) {
      console.error('解析分析结果失败:', error)
    }
  } else {
    console.warn('localStorage中没有找到analysisResults')
  }
}

// 键盘导航
const handleKeydown = (event: KeyboardEvent) => {
  if (!isMultiDetail.value || detailList.value.length <= 1) return
  
  switch (event.key) {
    case 'ArrowLeft':
      event.preventDefault()
      if (currentPage.value > 1) {
        goToPage(currentPage.value - 1)
      }
      break
    case 'ArrowRight':
      event.preventDefault()
      if (currentPage.value < totalPages.value) {
        goToPage(currentPage.value + 1)
      }
      break
    case 'Home':
      event.preventDefault()
      goToPage(1)
      break
    case 'End':
      event.preventDefault()
      goToPage(totalPages.value)
      break
  }
}

const handleExport = (data: any) => {
  console.log('导出报告:', data)
  pendingExportData.value = data
  showExportDialog.value = true
}

// 批量导出报告
const exportBatchReport = () => {
  try {
    const batchReportData = {
      export_date: new Date().toISOString(),
      total_dungeons: detailList.value.length,
      summary: {
        excellent_count: excellentCount.value,
        good_count: goodCount.value,
        average_count: averageCount.value,
        poor_count: poorCount.value,
        average_score: detailList.value.reduce((sum, d) => sum + (d.overallScore || 0), 0) / detailList.value.length
      },
      dungeons: detailList.value.map(detail => ({
        name: detail.name,
        filename: detail.filename,
        overall_score: detail.overallScore,
        grade: detail.grade,
        score_class: getScoreClass(detail.overallScore || 0)
      }))
    }
    
    const reportData = JSON.stringify(batchReportData, null, 2)
    const blob = new Blob([reportData], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `batch_dungeon_report_${new Date().toISOString().slice(0, 10)}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    console.log('批量报告导出成功')
    alert('批量报告导出成功！')
  } catch (error) {
    console.error('批量导出失败:', error)
    alert('批量导出失败，请重试')
  }
}

const confirmExport = () => {
  if (!pendingExportData.value) return
  
  try {
    const reportData = JSON.stringify(pendingExportData.value, null, 2)
    const blob = new Blob([reportData], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${pendingExportData.value.dungeon_name}_detailed_report_${new Date().toISOString().slice(0, 10)}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    console.log('Report exported successfully:', pendingExportData.value.dungeon_name)
    alert(t('success.reportExported'))
  } catch (error) {
    console.error('Error exporting report:', error)
    alert(t('errors.exportFailed'))
  } finally {
    showExportDialog.value = false
    pendingExportData.value = null
  }
}

const handleRefresh = () => {
  console.log('刷新地下城详情')
}

const handleError = (errorMsg: string) => {
  console.error('地下城详情错误:', errorMsg)
}

const getScoreClass = (score: number): string => {
  if (score >= 0.8) return 'excellent'
  if (score >= 0.65) return 'good'
  if (score >= 0.5) return 'average'
  if (score >= 0.35) return 'poor'
  return 'very-poor'
}

const handleLoaded = (data: any) => {
  console.log('地下城详情加载完成:', data)
}

// 添加缺失的属性和方法
const refreshData = () => {
  console.log('刷新数据')
  handleRefresh()
}

const exportReport = () => {
  console.log('导出报告')
  // 这里可以调用handleExport方法
}

// 添加缺失的计算属性
const averageScore = computed(() => {
  if (detailList.value.length === 0) return 0
  const total = detailList.value.reduce((sum, d) => sum + (d.overallScore || 0), 0)
  return total / detailList.value.length
})

const bestScore = computed(() => {
  if (detailList.value.length === 0) return 0
  return Math.max(...detailList.value.map(d => d.overallScore || 0))
})

const scoreFilter = ref('all')

const filteredAndSortedDetails = computed(() => {
  let filtered = [...detailList.value]
  
  // 筛选
  if (scoreFilter.value !== 'all') {
    filtered = filtered.filter(detail => {
      const score = detail.overallScore || 0
      switch (scoreFilter.value) {
        case 'high':
          return score >= 8.0
        case 'medium':
          return score >= 5.0 && score < 8.0
        case 'low':
          return score < 5.0
        default:
          return true
      }
    })
  }
  
  // 排序
  filtered.sort((a, b) => {
    switch (sortBy.value) {
      case 'score':
        return (b.overallScore || 0) - (a.overallScore || 0)
      case 'name':
        return a.name.localeCompare(b.name)
      case 'index':
      default:
        return 0 // 保持原始顺序
    }
  })
  
  return filtered
})

const getGradeLabel = (score: number | undefined): string => {
  if (!score) return 'N/A'
  if (score >= 8.0) return '优秀'
  if (score >= 6.5) return '良好'
  if (score >= 5.0) return '一般'
  if (score >= 3.5) return '较差'
  return '很差'
}

// 添加缺失的方法
const refreshAnalysis = () => {
  console.log('刷新分析')
  handleRefresh()
}

const exportCurrentReport = () => {
  console.log('导出当前报告')
  if (currentDetail.value) {
    handleExport({
      dungeon_name: currentDetail.value.name,
      file_id: currentDetail.value.fileId,
      overall_score: currentDetail.value.overallScore,
      grade: currentDetail.value.grade
    })
  }
}

const exportAllReports = () => {
  console.log('导出全部报告')
  exportBatchReport()
}

// 添加selectedMetrics属性
const selectedMetrics = ref<string[]>([])
const visualizationMode = ref('radar')

// 加载选中的指标
const loadSelectedMetrics = () => {
  const saved = localStorage.getItem('selectedMetrics')
  if (saved) {
    try {
      selectedMetrics.value = JSON.parse(saved)
    } catch (error) {
      console.error('解析选中的指标失败:', error)
      selectedMetrics.value = []
    }
  } else {
    // 默认选择所有指标
    selectedMetrics.value = [
      'accessibility', 'aesthetic_balance', 'dead_end_ratio',
      'degree_variance', 'key_path_length', 'loop_ratio',
      'treasure_monster_distribution', 'connectivity', 'complexity'
    ]
  }
}

onMounted(() => {
  if (isMultiDetail.value) {
    initMultiDetails()
  }
  
  // 加载选中的指标
  loadSelectedMetrics()
  
  // 添加键盘事件监听
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  // 移除键盘事件监听
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
/* 只保留必要的动画和特殊效果 */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* TransitionGroup 动画 */
.thumbnail-list-enter-active,
.thumbnail-list-leave-active {
  transition: all 0.3s ease;
}

.thumbnail-list-enter-from,
.thumbnail-list-leave-to {
  opacity: 0;
  transform: scale(0.8);
}

.thumbnail-list-move {
  transition: transform 0.3s ease;
}

/* Transition 动画 */
.detail-fade-enter-active,
.detail-fade-leave-active {
  transition: all 0.3s ease;
}

.detail-fade-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.detail-fade-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .max-w-full {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  
  .p-6 {
    padding: 1rem;
  }
  
  .p-8 {
    padding: 1rem;
  }
  
  .text-2xl {
    font-size: 1.25rem;
    line-height: 1.75rem;
  }
  
  .gap-6 {
    gap: 1rem;
  }
  
  .flex {
    flex-direction: column;
  }
}

@media (max-width: 640px) {
  .p-3 {
    padding: 0.5rem;
  }
  
  .gap-2 {
    gap: 0.5rem;
  }
  
  .text-xs {
    font-size: 0.75rem;
    line-height: 1rem;
  }
}
</style> 