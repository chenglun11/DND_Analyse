<template>
  <div class="min-h-screen bg-slate-50">

    <!-- 主内容区域 -->
    <div class="max-w-full mx-auto px-4 sm:px-6 lg:px-8 xl:px-12 py-6 lg:py-8">
      
      <!-- 面包屑导航 -->
      <nav class="mb-4" aria-label="面包屑">
        <div class="flex items-center space-x-2 text-sm text-gray-600">
          <button @click="goBack" class="hover:text-gray-900 transition-colors">
            {{t('detail.homeButton')}}
          </button>
          <span>›</span>
          <span v-if="isMultiDetail && detailList.length > 1" class="text-gray-900">
            {{t('detail.batchAnalysis',{count:detailList.length})}}
          </span>
          <span v-else-if="isMultiDetail && detailList.length === 1" class="text-gray-900">
            {{t('detail.singleAnalysis')}}
          </span>
          <span v-else class="text-gray-900">
            {{ dungeonName || '地下城分析' }}
          </span>
          <span v-if="isMultiDetail && currentDetail">›</span>
          <span v-if="isMultiDetail && currentDetail" class="text-blue-600 font-medium">
            {{ currentDetail.name }}
          </span>
        </div>
      </nav>
      
      <!-- 统一的操作按钮 -->
      <div class="bg-white rounded-lg border border-gray-200 p-4 mb-6 shadow-sm">
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <div class="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              <h2 class="text-lg font-semibold text-gray-900">
                {{ currentDetail?.name || dungeonName || t('common.unknown') }}
              </h2>
            </div>
          </div>
          
          <!-- 三个大按钮 -->
          <div class="flex items-center space-x-3">
            <!-- 刷新按钮 -->
            <button 
              @click="refreshAnalysis"
              class="inline-flex items-center px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium rounded-lg transition-colors"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
              {{t('detail.refreshButton')}}
            </button>
            
            <!-- 批量概览按钮(仅批量模式) -->
            <button 
              v-if="isMultiDetail && detailList.length > 1"
              @click="showBatchOverview = !showBatchOverview"
              class="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
              </svg>
              {{ showBatchOverview ? t('detail.hideOverview') : t('detail.showOverview') }}
            </button>
            
            <!-- 导出按钮(单独模式或批量模式下当前项) -->
            <button 
              v-if="!isMultiDetail || (isMultiDetail && currentDetail)"
              @click="exportCurrentReport"
              class="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
              {{t('detail.exportReport')}}
            </button>
            
            <!-- 导航按钮 -->
            <button 
              v-if="isMultiDetail && detailList.length > 1"
              @click="toggleNavigation"
              class="inline-flex items-center px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
              </svg>
              {{ currentPage < totalPages ? t('detail.next') : t('detail.first') }}
            </button>
            
            <!-- 返回按钮 -->
            <button 
              @click="goBack"
              class="inline-flex items-center px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
              </svg>
              {{t('detail.backButton')}}
            </button>
          </div>
        </div>
      </div>
      
      <!-- 批量分析概览面板(仅批量模式且多个文件时显示) -->
      <div v-if="isMultiDetail && detailList.length > 1 && showBatchOverview" class="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <div class="mb-6">
          <h2 class="text-xl font-semibold text-gray-900">{{t('detail.batchOverview')}}</h2>
        </div>
            
        <!-- 优化的响应式统计卡片 -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 mb-6">
          <div class="bg-white border border-gray-200 rounded-lg p-3 sm:p-4 min-w-0">
            <div class="text-lg sm:text-xl lg:text-2xl font-semibold text-gray-900 truncate">{{ isNaN(averageScore) ? '0.00' : formatScore(averageScore) }}</div>
            <div class="text-xs sm:text-sm text-gray-600">{{t('detail.averageScore')}}</div>
          </div>
          <div class="bg-white border border-gray-200 rounded-lg p-3 sm:p-4 min-w-0">
            <div class="text-lg sm:text-xl lg:text-2xl font-semibold text-gray-900 truncate">{{ isNaN(bestScore) ? '0.00' : formatScore(bestScore) }}</div>
            <div class="text-xs sm:text-sm text-gray-600">{{t('detail.highestScore')}}</div>
          </div>
          <div class="bg-white border border-gray-200 rounded-lg p-3 sm:p-4 min-w-0 sm:col-span-2 lg:col-span-1">
            <div class="text-lg sm:text-xl lg:text-2xl font-semibold text-gray-900 truncate">{{ detailList.length }}</div>
            <div class="text-xs sm:text-sm text-gray-600">{{t('detail.dungeonCount')}}</div>
          </div>
        </div>
            
        <!-- 优化的响应式过滤和排序 -->
        <div class="flex flex-col sm:flex-row gap-3 sm:gap-4 mb-6">
          <div class="flex-1 min-w-0">
            <label class="block text-xs font-medium text-gray-700 mb-1">{{t('detail.sortBy')}}</label>
            <select 
              v-model="sortBy" 
              class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 truncate"
            >
              <option value="name">{{t('detail.sortByName')}}</option>
              <option value="score">{{t('detail.sortByScore')}}</option>
              <option value="index">{{t('detail.sortByIndex')}}</option>
            </select>
          </div>
          <div class="flex-1 min-w-0">
            <label class="block text-xs font-medium text-gray-700 mb-1">{{t('detail.scoreFilter')}}</label>
            <select 
              v-model="scoreFilter" 
              class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 truncate"
            >
              <option value="all">{{t('detail.allScore')}}</option>
              <option value="high">{{t('detail.highScore')}}</option>
              <option value="medium">{{t('detail.mediumScore')}}</option>
              <option value="low">{{t('detail.lowScore')}}</option>
            </select>
          </div>
          <div class="flex-shrink-0 flex items-end">
            <div class="text-xs text-gray-500 px-2 py-2">
              {{t('detail.filteredCount',{count:filteredAndSortedDetails.length,total:detailList.length})}}
            </div>
          </div>
        </div>
            
        <!-- 优化的响应式地下城卡片网格 -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 sm:gap-4">
          <div 
            v-for="(detail, index) in filteredAndSortedDetails" 
            :key="detail.name"
            class="bg-white border border-gray-200 rounded-lg p-3 sm:p-4 hover:border-gray-300 cursor-pointer transition-colors min-w-0"
            :class="currentPage === index + 1 ? 'ring-2 ring-blue-500 bg-blue-50' : ''"
            @click="goToPage(index + 1)"
          >
            <div class="flex flex-col space-y-2">
              <div class="flex items-start justify-between">
                <h3 class="text-xs sm:text-sm font-medium text-gray-900 truncate flex-1 pr-2" :title="detail.name">
                  {{ detail.name }}
                </h3>
                <div class="text-right flex-shrink-0">
                  <div class="text-sm sm:text-lg font-semibold" :class="[
                    getScoreClass(detail.overallScore || 0) === 'excellent' ? 'text-green-600' :
                    getScoreClass(detail.overallScore || 0) === 'good' ? 'text-blue-600' :
                    getScoreClass(detail.overallScore || 0) === 'average' ? 'text-yellow-600' :
                    'text-gray-600'
                  ]">
                    {{ (detail.overallScore && !isNaN(detail.overallScore)) ? formatScore(detail.overallScore) : 'N/A' }}
                  </div>
                </div>
              </div>
              
              <div class="flex items-center justify-between text-xs text-gray-500">
                <span class="truncate">
                  {{ getGradeLabel(detail.overallScore) }}
                </span>
                <span class="text-xs text-gray-400 ml-2">
                  #{{ index + 1 }}{{ currentPage === index + 1 ? ' ('+t('detail.current')+')' : '' }}
                </span>
              </div>
            </div>
          </div>
        </div>
            
        <!-- 空状态 -->
        <div v-if="filteredAndSortedDetails.length === 0" class="text-center py-12">
          <div class="text-gray-400 text-lg mb-2">{{t('detail.noMatchDungeon')}}</div>
          <div class="text-sm text-gray-500">{{t('detail.tryAdjustFilter')}}</div>
        </div>
      </div>

      <!-- 主要内容区域 -->
      <div class="bg-white rounded-lg border border-gray-200">
        <!-- 批量模式的导航提示(仅多个文件时) -->
        <div v-if="isMultiDetail && detailList.length > 1" class="bg-blue-50 border-b border-blue-200 px-4 py-3">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <div class="text-sm text-blue-700 font-medium">
                {{t('detail.currentPage',{current:currentPage,total:totalPages})}}
              </div>
            </div>
            <div class="flex items-center gap-1">
              <button 
                @click="goToPage(currentPage - 1)"
                :disabled="currentPage <= 1"
                class="p-1 text-blue-600 hover:bg-blue-100 rounded disabled:opacity-50 disabled:cursor-not-allowed"
              >
                ←
              </button>
              <button 
                @click="goToPage(currentPage + 1)"
                :disabled="currentPage >= totalPages"
                class="p-1 text-blue-600 hover:bg-blue-100 rounded disabled:opacity-50 disabled:cursor-not-allowed"
              >
                →
              </button>
            </div>
          </div>
        </div>
        
        <DungeonDetail 
          v-if="currentDetail || (!isMultiDetail && dungeonName)"
          :dungeon-name="currentDetail?.name || dungeonName"
          :file-id="currentDetail?.fileId || fileId"
          :filename="currentDetail?.filename || filename"
          :scores="currentDetail?.detailedScores || {}"
          :selected-metrics="selectedMetrics"
          :visualization-mode="visualizationMode"
          @visualization-mode-change="visualizationMode = $event"
        />
        
        <!-- 加载状态 -->
        <div v-else-if="isMultiDetail && detailList.length === 0" class="text-center py-12">
          <div class="w-8 h-8 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin mx-auto mb-3"></div>
          <div class="text-gray-600 mb-2">{{t('detail.loadingAnalysisResults')}}</div>
          <div class="text-sm text-gray-500">{{t('detail.pleaseWait')}}</div>
        </div>
        
        <!-- 无数据状态 -->
        <div v-else class="text-center py-12">
          <div class="text-6xl mb-4">📁</div>
          <div class="text-gray-400 text-lg mb-2">{{ t('detail.noDetailAvailable') }}</div>
          <div class="text-sm text-gray-500 mb-4">{{t('detail.noDetailAvailable')}}</div>
          <button 
            @click="goBack"
            class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            {{t('detail.backToHome')}}
          </button>
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

// 批量分析相关
const sortBy = ref('name')


// 监听detailList变化
watch(detailList, (newList) => {
  console.log('详情列表变化:', newList.length, '项')
  if (newList.length > 0 && currentPage.value > Math.ceil(newList.length / itemsPerPage)) {
    console.log('当前页超出范围，重置到第一页')
    currentPage.value = 1
  }
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
      console.log('结果类型:', typeof results)
      console.log('结果长度:', results.length)
      
      detailList.value = results.map((result: any) => {
        console.log('处理单个结果:', result)
        const mappedResult = {
          name: result.name,
          fileId: result.fileId || result.id,
          filename: result.filename || result.name,
          overallScore: result.overallScore || result.score || 0,
          grade: result.grade,
          detailedScores: result.detailedScores || {}
        }
        console.log('映射后的结果:', mappedResult)
        return mappedResult
      })
      
      console.log('处理后的详情列表:', detailList.value)
      console.log('详情列表长度:', detailList.value.length)
      console.log('第一个详情:', detailList.value[0])
      
      // 重置到第一页
      currentPage.value = 1
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






const getScoreClass = (score: number): string => {
  if (score >= 0.8) return 'excellent'
  if (score >= 0.65) return 'good'
  if (score >= 0.5) return 'average'
  if (score >= 0.35) return 'poor'
  return 'very-poor'
}



// 添加缺失的计算属性
const averageScore = computed(() => {
  if (detailList.value.length === 0) return 0
  const scores = detailList.value.map(d => d.overallScore || 0).filter(score => score > 0)
  if (scores.length === 0) return 0
  const total = scores.reduce((sum, score) => sum + score, 0)
  const average = total / scores.length
  console.log('平均分计算:', { scores, total, average, totalItems: detailList.value.length })
  return average
})

const bestScore = computed(() => {
  if (detailList.value.length === 0) return 0
  const scores = detailList.value.map(d => d.overallScore || 0).filter(score => score > 0)
  if (scores.length === 0) return 0
  const best = Math.max(...scores)
  console.log('最高分计算:', { scores, best })
  return best
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
          return score >= 0.8
        case 'medium':
          return score >= 0.5 && score < 0.8
        case 'low':
          return score < 0.5
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
  if (score >= 0.8) return '优秀'
  if (score >= 0.65) return '良好'
  if (score >= 0.5) return '一般'
  if (score >= 0.35) return '较差'
  return '很差'
}

// 格式化分数显示
const formatScore = (score: number): string => {
  if (score === 0) return '0.00'
  if (score < 0.01) return '< 0.01'
  if (score >= 1) return '1.00'
  // 限制小数位数为3位，避免超长小数
  return Number(score.toFixed(3)).toString()
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

// 新的统一按钮方法
const refreshAnalysis = () => {
  console.log('刷新分析')
  // 重新获取当前详情数据
  if (isMultiDetail.value) {
    initMultiDetails()
  }
}

const exportCurrentReport = () => {
  console.log('导出当前报告')
  if (currentDetail.value) {
    const reportData = {
      dungeon_name: currentDetail.value.name,
      file_id: currentDetail.value.fileId,
      overall_score: currentDetail.value.overallScore,
      detailed_scores: currentDetail.value.detailedScores,
      grade: currentDetail.value.grade,
      export_date: new Date().toISOString()
    }
    
    const jsonData = JSON.stringify(reportData, null, 2)
    const blob = new Blob([jsonData], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${currentDetail.value.name}_report_${new Date().toISOString().slice(0, 10)}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    console.log('报告导出成功')
  } else {
    console.warn('没有可导出的报告数据')
  }
}

const toggleNavigation = () => {
  if (isMultiDetail.value) {
    if (currentPage.value < totalPages.value) {
      goToPage(currentPage.value + 1)
    } else {
      goToPage(1)
    }
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
/* 简化的样式 */
.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

</style> 