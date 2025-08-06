<template>
  <div class="space-y-4 sm:space-y-6">
    <!-- 优化的响应式布局 - 更好的空间分配 -->
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-4 sm:gap-6">
      <!-- 可视化区域 (2/4) -->
      <div class="lg:col-span-2 bg-white rounded-lg border border-gray-200 p-3 sm:p-4 min-h-[400px]">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-base font-semibold text-gray-900">
            地下城可视化
          </h3>
          <div class="flex items-center space-x-2">
            <div class="flex bg-gray-100 rounded-md p-1">
              <button 
                @click="visualizationMode = 'canvas'"
                :class="['px-2 py-1 text-xs font-medium rounded transition-colors', 
                  visualizationMode === 'canvas' 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-600 hover:text-gray-800']"
              >
                交互
              </button>
              <button 
                @click="visualizationMode = 'image'"
                :class="['px-2 py-1 text-xs font-medium rounded transition-colors', 
                  visualizationMode === 'image' 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-600 hover:text-gray-800']"
              >
                图片
              </button>
            </div>
            <button 
              v-if="imageData" 
              @click="downloadImage"
              class="px-2 py-1 text-xs font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded transition-colors"
            >
              下载
            </button>
          </div>
        </div>
        
        <div v-if="loading" class="flex items-center justify-center py-12 bg-gray-50 rounded-lg">
          <div class="text-center">
            <div class="w-8 h-8 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin mx-auto mb-3"></div>
            <p class="text-sm text-gray-600">{{ t('common.loading') }}</p>
          </div>
        </div>
        
        <div v-else-if="error" class="text-center py-12 bg-gray-50 rounded-lg">
          <div class="text-gray-600 mb-4">
            <div class="text-red-500 text-2xl mb-2">⚠</div>
            <h3 class="text-sm font-medium mb-1">加载失败</h3>
            <p class="text-xs text-gray-500">{{ error }}</p>
          </div>
          <button 
            @click="fetchAnalysisResult"
            class="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            重试
          </button>
        </div>
        
        <!-- 交互式可视化 -->
        <div v-else-if="visualizationMode === 'canvas' && dungeonData" class="space-y-3">
          <div class="border border-gray-200 rounded-lg overflow-hidden bg-white min-h-[400px]">
            <DungeonVisualizer 
              :dungeon-data="dungeonData"
              @room-click="handleRoomClick"
              @corridor-click="handleCorridorClick"
            />
          </div>
        </div>
        
        <!-- 静态图片可视化 -->
        <div v-else-if="visualizationMode === 'image' && imageData" class="space-y-3">
          <div class="border border-gray-200 rounded-lg overflow-hidden bg-white">
            <div class="relative group">
              <img 
                :src="`data:image/png;base64,${imageData}`" 
                alt="Generated visualization" 
                class="w-full h-auto" 
              />
              <div class="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors flex items-center justify-center opacity-0 group-hover:opacity-100">
                <button 
                  @click="openImageFullscreen"
                  class="bg-white/90 text-gray-800 px-3 py-2 rounded text-sm hover:bg-white transition-colors"
                >
                  查看大图
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 自动切换到有效的可视化模式 -->
        <div v-else-if="dungeonData && !imageData" class="space-y-3">
          <div class="border border-gray-200 rounded-lg overflow-hidden bg-white min-h-[400px]">
            <DungeonVisualizer 
              :dungeon-data="dungeonData"
              @room-click="handleRoomClick"
              @corridor-click="handleCorridorClick"
            />
          </div>
        </div>
        
        <div v-else-if="!dungeonData && imageData" class="space-y-3">
          <div class="border border-gray-200 rounded-lg overflow-hidden bg-white">
            <div class="relative group">
              <img 
                :src="`data:image/png;base64,${imageData}`" 
                alt="Generated visualization" 
                class="w-full h-auto" 
              />
              <div class="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors flex items-center justify-center opacity-0 group-hover:opacity-100">
                <button 
                  @click="openImageFullscreen"
                  class="bg-white/90 text-gray-800 px-3 py-2 rounded text-sm hover:bg-white transition-colors"
                >
                  查看大图
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div v-else class="flex items-center justify-center min-h-[300px] bg-gray-50 rounded-lg">
          <div class="text-center">
            <div class="text-gray-400 text-xl mb-2">⏳</div>
            <p class="text-sm text-gray-600 mb-1">{{ t('detail.noVisualizationData') }}</p>
            <p class="text-xs text-gray-500">正在生成可视化数据...</p>
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
              ×
            </button>
          </div>
        </div>
      </div>
      
      <!-- 优化的分析结果区域 (2/4) -->
      <div class="lg:col-span-2 bg-white rounded-lg border border-gray-200 p-3 overflow-hidden min-h-[400px]">
        <div class="mb-3">
          <h3 class="text-sm font-semibold text-gray-900">{{ t('detail.analysisResults') }}</h3>
        </div>
        
        <div class="space-y-4 h-full">
          <!-- 充分展示的总体评分 -->
          <div class="bg-gray-50 rounded-lg p-4">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-sm font-medium text-gray-700">{{ t('detail.overallScore') }}</h4>
              <span class="px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-700">
                {{ grade || 'N/A' }}
              </span>
            </div>
            <div class="text-center">
              <div class="text-3xl font-bold mb-3" :class="[
                getScoreClass(overallScore) === 'excellent' ? 'text-green-600' :
                getScoreClass(overallScore) === 'good' ? 'text-blue-600' :
                getScoreClass(overallScore) === 'average' ? 'text-yellow-600' :
                'text-gray-600'
              ]">
                {{ overallScore ? formatOverallScore(overallScore) : 'N/A' }}
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="h-2 rounded-full transition-all duration-500" 
                  :class="[
                    getScoreClass(overallScore) === 'excellent' ? 'bg-green-500' :
                    getScoreClass(overallScore) === 'good' ? 'bg-blue-500' :
                    getScoreClass(overallScore) === 'average' ? 'bg-yellow-500' :
                    'bg-gray-400'
                  ]"
                  :style="{ width: `${(overallScore || 0) * 100}%` }"
                ></div>
              </div>
            </div>
          </div>
          
          <!-- 充分的选项卡导航 -->
          <div class="border-b border-gray-200">
            <nav class="flex space-x-6">
              <button @click="activeTab = 'detailed'" 
                      :class="[
                        'pb-2 px-1 text-sm font-medium border-b-2 transition-colors',
                        activeTab === 'detailed' 
                          ? 'text-blue-600 border-blue-600' 
                          : 'text-gray-500 border-transparent hover:text-gray-700'
                      ]">
                指标详情
              </button>
              <button @click="activeTab = 'suggestions'" 
                      :class="[
                        'pb-2 px-1 text-sm font-medium border-b-2 transition-colors',
                        activeTab === 'suggestions' 
                          ? 'text-blue-600 border-blue-600' 
                          : 'text-gray-500 border-transparent hover:text-gray-700'
                      ]">
                改进建议
              </button>
            </nav>
          </div>
          
          <!-- 充分展示的内容区域 -->
          <div class="mt-4 flex-1 min-h-0">
            <div v-if="activeTab === 'detailed'" class="h-full">
              <AnalysisReport 
                :scores="detailedScores"
                :overall-score="overallScore"
                :grade="grade || '未知'"
                :dungeon-name="dungeonName"
                :compact="false"
              />
            </div>
            
            <div v-if="activeTab === 'suggestions'" class="h-full">
              <ImprovementSuggestions 
                :scores="detailedScores"
                :overall-score="overallScore"
                :compact="false"
              />
            </div>
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

const activeTab = ref<'detailed' | 'suggestions'>('detailed')
const visualizationMode = ref<'canvas' | 'image'>('canvas')
const showFullscreenImage = ref(false)
const grade = ref<string>('未知')



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
            const validScores = Object.values(scores).filter((scoreData: any) => 
              scoreData && typeof scoreData === 'object' && scoreData.score > 0
            )
            if (validScores.length > 0) {
              const totalScore = validScores.reduce((sum: number, scoreData: any) => sum + scoreData.score, 0)
              overallScore.value = (totalScore / validScores.length)
              console.log('计算的整体分数:', overallScore.value, '基于', validScores.length, '个有效指标')
            } else {
              console.log('没有有效的详细分数，不计算整体分数')
            }
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
          const validScores = Object.values(scores).filter((scoreData: any) => 
            scoreData && typeof scoreData === 'object' && scoreData.score > 0
          )
          if (validScores.length > 0) {
            const totalScore = validScores.reduce((sum: number, scoreData: any) => sum + scoreData.score, 0)
            overallScore.value = (totalScore / validScores.length)
            console.log('计算的整体分数:', overallScore.value, '基于', validScores.length, '个有效指标')
          } else {
            console.log('没有有效的详细分数，不计算整体分数')
          }
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
  if (detailedScores.value.dead_end_ratio?.score < 0.5) {
    suggestions.push({
      title: t('suggestions.deadEndRatio.title'),
      description: t('suggestions.deadEndRatio.description')
    })
  } else if (detailedScores.value.dead_end_ratio?.score < 0.7) {
    suggestions.push({
      title: t('suggestions.deadEndRatioOptimize.title'),
      description: t('suggestions.deadEndRatioOptimize.description')
    })
  }
  
  // 几何平衡建议
  if (detailedScores.value.geometric_balance?.score < 0.7) {
    suggestions.push({
      title: t('suggestions.geometricBalance.title'),
      description: t('suggestions.geometricBalance.description')
    })
  }
  
  // 宝藏怪物分布建议
  if (detailedScores.value.treasure_monster_distribution?.score < 0.5) {
    suggestions.push({
      title: t('suggestions.treasureMonsterDistribution.title'),
      description: t('suggestions.treasureMonsterDistribution.description')
    })
  } else if (detailedScores.value.treasure_monster_distribution?.score < 0.7) {
    suggestions.push({
      title: t('suggestions.treasureMonsterDistributionBalance.title'),
      description: t('suggestions.treasureMonsterDistributionBalance.description')
    })
  }
  
  // 可达性建议
  if (detailedScores.value.accessibility?.score < 0.7) {
    suggestions.push({
      title: t('suggestions.accessibility.title'),
      description: t('suggestions.accessibility.description')
    })
  }
  
  // 路径多样性建议
  if (detailedScores.value.path_diversity?.score < 0.5) {
    suggestions.push({
      title: t('suggestions.pathDiversity.title'),
      description: t('suggestions.pathDiversity.description')
    })
  } else if (detailedScores.value.path_diversity?.score < 0.7) {
    suggestions.push({
      title: t('suggestions.pathDiversityOptimize.title'),
      description: t('suggestions.pathDiversityOptimize.description')
    })
  }
  
  // 环路比例建议
  if (detailedScores.value.loop_ratio?.score < 0.3) {
    suggestions.push({
      title: t('suggestions.loopRatio.title'),
      description: t('suggestions.loopRatio.description')
    })
  } else if (detailedScores.value.loop_ratio?.score < 0.5) {
    suggestions.push({
      title: t('suggestions.loopRatioOptimize.title'),
      description: t('suggestions.loopRatioOptimize.description')
    })
  }
  
  // 度方差建议
  if (detailedScores.value.degree_variance?.score < 0.5) {
    suggestions.push({
      title: t('suggestions.degreeVariance.title'),
      description: t('suggestions.degreeVariance.description')
    })
  }
  
  // 门分布建议
  if (detailedScores.value.door_distribution?.score < 0.5) {
    suggestions.push({
      title: t('suggestions.doorDistribution.title'),
      description: t('suggestions.doorDistribution.description')
    })
  }
  
  // 关键路径长度建议
  if (detailedScores.value.key_path_length?.score < 0.5) {
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

// 格式化总体评分显示
const formatOverallScore = (score: number): string => {
  if (score === 0) return '0.00'
  if (score < 0.01) return '< 0.01'
  if (score >= 1) return '1.00'
  // 限制小数位数为3位，避免超长小数
  return Number(score.toFixed(3)).toString()
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
  
  if (props.autoLoad) {
    await fetchAnalysisResult()
  }
})
</script>

<style scoped>
/* 简化的样式 - 依赖Tailwind CSS的响应式类 */
</style> 