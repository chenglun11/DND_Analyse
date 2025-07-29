<template>
  <div class="detail-view">
    <!-- 页头 -->
    <header class="page-header">
      <div class="header-content">
                  <button @click="goBack" class="back-btn" :title="t('detail.backButtonTitle')">{{ t('detail.backButton') }}</button>
        <div class="page-info">
          <h1>{{ dungeonName }}</h1>
          <p class="page-subtitle">{{ t('detail.analysisResults') }}</p>
        </div>
        <div class="header-right">
          <button @click="forceRefresh" class="refresh-btn">{{ t('detail.refreshButton') }}</button>
        </div>
      </div>
    </header>

    <div class="content">
      <div class="dungeon-details">
        <div class="visualization-section">
          <h2>{{ t('detail.dungeonVisualization') }}</h2>
          
          <div v-if="loading" class="loading">
            <p>{{ t('common.loading') }}</p>
          </div>
          
          <div v-else-if="error" class="error">
            <p>{{ error }}</p>
          </div>
          
          <div v-if="dungeonData" class="canvas-visualization">
            <h3>{{ t('detail.canvasVisualization') }}</h3>
            <div class="visualizer-container">
              <DungeonVisualizer 
                :dungeon-data="dungeonData"
                @room-click="handleRoomClick"
                @corridor-click="handleCorridorClick"
              />
            </div>
          </div>
          
          <div v-if="imageData" class="generated-image">
            <h3>{{ t('detail.generatedImage') }}</h3>
            <div class="image-container">
              <img :src="`data:image/png;base64,${imageData}`" alt="Generated visualization" />
            </div>
          </div>
          
          <div v-else class="no-data">
            <p>{{ t('detail.noVisualizationData') }}</p>
          </div>
        </div>
      </div>

      <div class="analysis-section">
        <h2>{{ t('detail.analysisResults') }}</h2>
        
        <div class="analysis-content">
          <!-- 总体评分 -->
          <div class="overall-score-card">
            <h3>{{ t('detail.overallScore') }}</h3>
            <div class="score-display">
              <div class="score-circle" :class="getScoreClass(overallScore)">
                {{ overallScore.toFixed(1) }}
              </div>
              <div class="score-description">
                <p>{{ getScoreDescription(overallScore) }}</p>
              </div>
            </div>
          </div>

          <!-- 详细指标 -->
          <div class="metrics-grid">
            <div v-for="(score, metric) in detailedScores" :key="metric" class="metric-card" :class="getScoreClass(score)">
              <div class="metric-header">
                <h4>{{ getMetricName(metric) }}</h4>
                <span class="metric-score" :class="getScoreClass(score)">
                  {{ (score * 100).toFixed(0) }}%
                </span>
              </div>
              <div class="metric-bar">
                <div class="bar-fill" :style="{ width: `${score * 100}%` }" :class="getScoreClass(score)"></div>
              </div>
              <p class="metric-description">{{ getMetricDescription(metric, score) }}</p>
            </div>
          </div>

          <!-- 建议改进 -->
          <div class="improvements-section">
            <h3>{{ t('detail.improvementSuggestions') }}</h3>
            <div class="improvements-list">
              <div v-for="(suggestion, index) in improvementSuggestions" :key="index" class="suggestion-item">
                <div class="suggestion-icon">💡</div>
                <div class="suggestion-content">
                  <h4>{{ suggestion.title }}</h4>
                  <p>{{ suggestion.description }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 页脚 -->
    <footer class="footer">
      <p>&copy; 2024 地下城适配器</p>
    </footer>

    <!-- 房间详情弹窗 -->
    <div v-if="selectedRoom" class="room-modal" @click="closeRoomModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ selectedRoom.type }} 房间</h3>
          <button @click="closeRoomModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <div class="room-info">
            <p><strong>位置:</strong> ({{ selectedRoom.x }}, {{ selectedRoom.y }})</p>
            <p><strong>尺寸:</strong> {{ selectedRoom.width }} × {{ selectedRoom.height }}</p>
            <p><strong>连接数:</strong> {{ selectedRoom.connections.length }}</p>
          </div>
          <div class="room-connections">
            <h4>连接房间:</h4>
            <ul>
              <li v-for="connection in selectedRoom.connections" :key="connection">
                {{ connection }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import DungeonVisualizer from '../components/DungeonVisualizer.vue'
import { DungeonAPI } from '../services/api'
import type { DungeonData, Room, Corridor } from '../types/dungeon'

interface ImprovementSuggestion {
  title: string
  description: string
}

const route = useRoute()
const router = useRouter()
const { t } = useI18n()

const goBack = () => {
  // 如果有历史记录，返回上一页
  if (window.history.length > 1) {
    router.back()
  } else {
    // 否则返回首页
    router.push('/')
  }
}
const dungeonData = ref<DungeonData | undefined>(undefined);
const overallScore = ref(0);
const detailedScores = ref<Record<string, number>>({});
const loading = ref(false);
const error = ref<string | null>(null);
const imageData = ref<string | null>(null);
const selectedRoom = ref<Room | null>(null)

const dungeonName = computed(() => {
  return route.params.name as string || '未知地下城'
})

// 获取分析结果
const fetchAnalysisResult = async () => {
  try {
    loading.value = true
    error.value = null
    
    const filename = route.params.filename as string
    const dungeonName = route.params.name as string
    
    console.log('获取分析结果，文件名:', filename, '地下城名称:', dungeonName)
    
    // 如果没有文件名，显示错误
    if (!filename) {
      error.value = '缺少文件名参数'
      return
    }
    
    // 创建文件对象（这里需要实际的文件内容）
    // 由于前端无法直接访问文件系统，我们需要从后端获取数据
    const file = new File([''], filename, { type: 'application/json' })
    
    // 首先尝试生成图像
    try {
      const imageResult = await DungeonAPI.visualizeDungeonByFilename(filename, {
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
      console.warn('图像生成失败，回退到Canvas可视化:', imageErr)
    }
    
    // 获取可视化数据（作为备用）
    try {
      const result = await DungeonAPI.getVisualizationDataByFilename(filename)
      if (result.success && result.visualization_data) {
        dungeonData.value = result.visualization_data
      }
    } catch (dataErr) {
      console.warn('可视化数据获取失败:', dataErr)
    }
    
    // 获取分析结果
    const analysisResult = await DungeonAPI.analyzeDungeonByFilename(filename)
    console.log('分析结果:', analysisResult)
    
    if (analysisResult.success && analysisResult.result) {
      const assessment = analysisResult.result
      console.log('评估数据:', assessment)
      
      overallScore.value = assessment.overall_score || 0
      console.log('整体分数:', overallScore.value)
      
      // 处理详细分数 - 从scores中提取分数
      const scores = assessment.scores || {}
      const processedScores: Record<string, number> = {}
      
      for (const [metric, scoreData] of Object.entries(scores)) {
        if (typeof scoreData === 'object' && scoreData !== null && 'score' in scoreData) {
          // 保持0-1的分数范围
          processedScores[metric] = scoreData.score as number
        }
      }
      
      detailedScores.value = processedScores
      console.log('处理后的分数:', processedScores)
      
      // 如果没有整体分数，计算平均分
      if (!assessment.overall_score && Object.keys(processedScores).length > 0) {
        const totalScore = Object.values(processedScores).reduce((sum, score) => sum + score, 0)
        overallScore.value = (totalScore / Object.keys(processedScores).length) * 10
        console.log('计算的整体分数:', overallScore.value)
      }
    }
  } catch (err) {
    console.error('获取分析结果时出错:', err)
    error.value = err instanceof Error ? err.message : '获取数据失败'
    
    // 清空数据，不设置默认值
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

// 处理地下城数据
const processDungeonData = (unifiedData: any) => {
  try {
    // 检查是否是FiMap Elites格式
    if (unifiedData.plan_graph && unifiedData.plan_graph.graph) {
      return unifiedData // 直接返回，因为已经处理过
    } else {
      // 假设是其他格式，尝试转换
      // 这里需要根据实际的统一数据格式进行转换
      // 例如，如果统一数据包含 rooms 和 corridors 数组
      return {
        rooms: unifiedData.rooms || [],
        corridors: unifiedData.corridors || [],
        width: unifiedData.width || 800,
        height: unifiedData.height || 600
      }
    }
  } catch (error) {
    console.error('Error processing dungeon data:', error)
    // 返回默认数据
    return {
      width: 800,
      height: 600,
      rooms: [],
      corridors: []
    }
  }
}

const improvementSuggestions = computed<ImprovementSuggestion[]>(() => {
  const suggestions: ImprovementSuggestion[] = []
  
  if (detailedScores.value.dead_end_ratio < 0.5) {
    suggestions.push({
      title: '减少死胡同',
      description: '当前死胡同比例较高，建议增加环路连接以提高探索体验。'
    })
  }
  
  if (detailedScores.value.aesthetic_balance < 0.7) {
    suggestions.push({
      title: '改善美学平衡',
      description: '房间布局可以更加平衡，考虑调整房间大小和位置分布。'
    })
  }
  
  if (detailedScores.value.treasure_monster_distribution < 0.5) {
    suggestions.push({
      title: '优化宝藏和怪物分布',
      description: '宝藏和怪物的分布需要调整，以提供更好的游戏体验。'
    })
  }
  
  if (detailedScores.value.accessibility < 0.7) {
    suggestions.push({
      title: '改善可达性',
      description: '某些区域难以到达，建议优化路径设计。'
    })
  }
  
  if (detailedScores.value.path_diversity < 0.5) {
    suggestions.push({
      title: '增加路径多样性',
      description: '路径多样性较低，建议增加不同的探索路径。'
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

const getMetricName = (metric: string): string => {
  return t(`metrics.${metric}`) || metric
}

const getMetricDescription = (metric: string, score: number): string => {
  const descriptions: Record<string, string> = {
    accessibility: score >= 0.7 ? '玩家可以轻松到达各个区域' : '某些区域难以到达，需要改善路径设计',
    aesthetic_balance: score >= 0.7 ? '房间布局美观且平衡' : '房间布局可以更加美观和平衡',
    loop_ratio: score >= 0.7 ? '环路设计合理，避免线性体验' : '环路较少，可能导致线性体验',
    dead_end_ratio: score >= 0.5 ? '死胡同比例适中' : '死胡同过多，影响探索体验',
    treasure_monster_distribution: score >= 0.5 ? '宝藏和怪物分布合理' : '宝藏和怪物分布需要调整',
    degree_variance: score >= 0.5 ? '房间连接度分布均匀' : '房间连接度分布不均匀',
    door_distribution: score >= 0.5 ? '门分布合理' : '门分布需要优化',
    key_path_length: score >= 0.7 ? '关键路径长度适中' : '关键路径过长或过短',
    path_diversity: score >= 0.5 ? '路径多样性良好' : '路径多样性需要改善'
  }
  return descriptions[metric] || '暂无描述'
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

const forceRefresh = () => {
  console.log('Forcing refresh...')
  fetchAnalysisResult()
}

onMounted(async () => {
  console.log('DetailView mounted')
  await fetchAnalysisResult()
  
  // 添加键盘事件监听器
  const handleKeydown = (event: KeyboardEvent) => {
    if (event.key === 'Escape') {
      goBack()
    }
  }
  
  document.addEventListener('keydown', handleKeydown)
  
  // 清理事件监听器
  onUnmounted(() => {
    document.removeEventListener('keydown', handleKeydown)
  })
})
</script>

<style scoped>
.detail-view {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  min-height: calc(100vh - 80px); /* 减去页头高度 */
  /* 确保页面可以正常滚动 */
}

.page-header {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
  margin-bottom: 30px;
  position: sticky;
  top: 0;
  z-index: 100;
  position: relative;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  position: relative;
}

.page-info {
  flex: 1;
  text-align: center;
  margin: 0 20px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}



.back-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.3s ease;
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.refresh-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.3s ease;
}

.refresh-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.page-info h1 {
  font-size: 2.5rem;
  font-weight: bold;
  margin: 0;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.page-info p {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
}

.content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 30px;
  max-width: 1400px;
  margin: 0 auto;
  margin-bottom: 40px;
}

.visualization-section,
.analysis-section {
  background: white;
  border-radius: 15px;
  padding: 25px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.analysis-content {
  /* 移除固定高度和滚动，让内容自然流动 */
  /* max-height: 600px; */
  /* overflow-y: auto; */
  padding-right: 10px;
}

/* 移除滚动条样式，因为不再需要 */
/* .analysis-content::-webkit-scrollbar {
  width: 8px;
}

.analysis-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.analysis-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.analysis-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
} */

.visualization-section h2,
.analysis-section h2 {
  color: #333;
  margin-bottom: 20px;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.visualizer-container {
  height: 600px;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 20px;
}

.overall-score-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 25px;
}

.overall-score-card h3 {
  color: #333;
  margin-bottom: 15px;
}

.score-display {
  display: flex;
  align-items: center;
  gap: 20px;
}

.score-circle {
  width: 80px;
  height: 80px;
  border-radius: 50% !important;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: bold;
  color: white;
  flex-shrink: 0;
  overflow: hidden;
  position: relative;
  min-width: 80px;
  min-height: 80px;
  max-width: 80px;
  max-height: 80px;
}

.score-circle.excellent {
  background: linear-gradient(135deg, #28a745, #20c997);
  box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
}

.score-circle.good {
  background: linear-gradient(135deg, #17a2b8, #20c997);
  box-shadow: 0 4px 15px rgba(23, 162, 184, 0.3);
}

.score-circle.average {
  background: linear-gradient(135deg, #ffc107, #fd7e14);
  color: #333;
  box-shadow: 0 4px 15px rgba(255, 193, 7, 0.3);
}

.score-circle.poor {
  background: linear-gradient(135deg, #dc3545, #e83e8c);
  box-shadow: 0 4px 15px rgba(220, 53, 69, 0.3);
}

.score-circle.very-poor {
  background: linear-gradient(135deg, #6c757d, #495057);
  box-shadow: 0 4px 15px rgba(108, 117, 125, 0.3);
}

.score-description p {
  color: #666;
  margin: 0;
  line-height: 1.5;
}

.metrics-grid {
  display: grid;
  gap: 15px;
  margin-bottom: 25px;
}

.metric-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  border-left: 4px solid #dee2e6;
  transition: all 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.metric-card.excellent {
  border-left-color: #28a745;
  background: linear-gradient(135deg, #f8fff9, #f0fff4);
}

.metric-card.good {
  border-left-color: #17a2b8;
  background: linear-gradient(135deg, #f8feff, #f0f9ff);
}

.metric-card.average {
  border-left-color: #ffc107;
  background: linear-gradient(135deg, #fffdf8, #fffbf0);
}

.metric-card.poor {
  border-left-color: #dc3545;
  background: linear-gradient(135deg, #fff8f8, #fff0f0);
}

.metric-card.very-poor {
  border-left-color: #6c757d;
  background: linear-gradient(135deg, #f8f9fa, #f0f0f0);
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.metric-header h4 {
  color: #333;
  margin: 0;
  font-size: 1rem;
}

.metric-score {
  font-weight: bold;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.9rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.metric-score:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.metric-score.excellent {
  background: #d4edda;
  color: #155724;
}

.metric-score.good {
  background: #d1ecf1;
  color: #0c5460;
}

.metric-score.average {
  background: #fff3cd;
  color: #856404;
}

.metric-score.poor {
  background: #f8d7da;
  color: #721c24;
}

.metric-score.very-poor {
  background: #e2e3e5;
  color: #383d41;
}

.metric-bar {
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  margin-bottom: 10px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.bar-fill.excellent {
  background: #28a745;
}

.bar-fill.good {
  background: #17a2b8;
}

.bar-fill.average {
  background: #ffc107;
}

.bar-fill.poor {
  background: #dc3545;
}

.bar-fill.very-poor {
  background: #6c757d;
}

.metric-description {
  color: #666;
  font-size: 0.9rem;
  margin: 0;
  line-height: 1.4;
}

.improvements-section h3 {
  color: #333;
  margin-bottom: 15px;
}

.improvements-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.suggestion-item {
  display: flex;
  gap: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #007bff;
}

.suggestion-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.suggestion-content h4 {
  color: #333;
  margin: 0 0 8px 0;
  font-size: 1rem;
}

.suggestion-content p {
  color: #666;
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.4;
}

.room-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 0;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.3s ease;
}

.close-btn:hover {
  background: #e9ecef;
}

.modal-body {
  padding: 20px;
}

.room-info {
  margin-bottom: 20px;
}

.room-info p {
  margin: 8px 0;
  color: #333;
}

.room-connections h4 {
  color: #333;
  margin-bottom: 10px;
}

.room-connections ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.room-connections li {
  padding: 5px 0;
  color: #666;
  border-bottom: 1px solid #f0f0f0;
}

.room-connections li:last-child {
  border-bottom: none;
}

.generated-image {
  margin: 20px 0;
}

.image-container {
  margin: 20px 0;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  text-align: center;
}

.image-container img {
  max-width: 100%;
  height: auto;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.canvas-visualization {
  margin: 20px 0;
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e9ecef;
}

.loading, .error, .no-data {
  text-align: center;
  padding: 40px;
  color: #6c757d;
}

.error {
  color: #dc3545;
}

@media (max-width: 1024px) {
  .content {
    grid-template-columns: 1fr;
  }
  
  .page-info h1 {
    font-size: 2rem;
  }
  

}

@media (max-width: 768px) {
  .detail-view {
    padding: 10px;
  }
  
  .page-header {
    padding: 10px 15px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 15px;
    position: relative;
  }
  
  .page-info {
    margin: 0;
    order: 2;
  }
  
  .header-right {
    order: 3;
    justify-content: center;
  }
  
  .back-btn {
    position: static;
    transform: none;
    align-self: flex-start;
    padding: 10px 20px;
    font-size: 16px;
    order: 1;
  }
  
  .page-info h1 {
    font-size: 1.5rem;
  }
  
  .page-info p {
    font-size: 0.9rem;
  }
  
  .visualization-section,
  .analysis-section {
    padding: 15px;
  }
  
  .score-display {
    flex-direction: column;
    text-align: center;
  }
  
  .visualizer-container {
    height: 400px;
  }
}

/* 页脚样式 */
.footer {
  background: rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  margin-top: 40px;
  padding: 20px;
  color: white;
  text-align: center;
}

.footer p {
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
}
</style> 