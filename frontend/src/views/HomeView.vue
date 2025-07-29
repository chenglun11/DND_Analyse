<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { DungeonAPI } from '../services/api'

interface AnalysisOptions {
  accessibility: boolean
  aestheticBalance: boolean
  loopRatio: boolean
  deadEndRatio: boolean
  treasureDistribution: boolean
  monsterDistribution: boolean
}

interface AnalysisResult {
  id: string
  name: string
  overallScore: number
  detailedScores: Record<string, { score: number; detail?: any }>
  unifiedData?: any
}

const router = useRouter()
const { t } = useI18n()
const fileInput = ref<HTMLInputElement>()
const uploadedFiles = ref<File[]>([])
const isAnalyzing = ref(false)
const analysisResults = ref<AnalysisResult[]>([])

// 移除analysisOptions，因为不再需要
// const analysisOptions = reactive<AnalysisOptions>({
//   accessibility: true,
//   aestheticBalance: true,
//   loopRatio: true,
//   deadEndRatio: true,
//   treasureDistribution: true,
//   monsterDistribution: true
// })

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
  uploadedFiles.value.push(...jsonFiles)
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

const startAnalysis = async () => {
  if (uploadedFiles.value.length === 0) return
  
  isAnalyzing.value = true
  
  try {
    // 转换选项格式
    const apiOptions = {
      accessibility: true, // 默认值，如果需要从选项中获取，则需要修改
      aesthetic_balance: true, // 默认值
      loop_ratio: true, // 默认值
      dead_end_ratio: true, // 默认值
      treasure_distribution: true, // 默认值
      monster_distribution: true // 默认值
    }
    
    if (uploadedFiles.value.length === 1) {
      // 单个文件分析
      const result = await DungeonAPI.analyzeDungeon(uploadedFiles.value[0], apiOptions)
      
      if (result.success) {
        console.log('分析成功，结果:', result)
        console.log('统一数据:', result.result.unified_data)
        
        analysisResults.value = [{
          id: `result-0`,
          name: uploadedFiles.value[0].name.replace('.json', ''),
          overallScore: result.result.overall_score || 0,
          detailedScores: result.result.scores || {},
          unifiedData: result.result.unified_data || null
        }]
        
        // 保存到localStorage以便详情页面使用
        localStorage.setItem('analysisResults', JSON.stringify(analysisResults.value))
        console.log('已保存到localStorage:', analysisResults.value)
      } else {
        console.error('分析失败:', result.error)
      }
    } else {
      // 批量分析
      const result = await DungeonAPI.analyzeBatch(uploadedFiles.value, apiOptions)
      
      if (result.success && result.results) {
        console.log('批量分析成功，结果:', result)
        analysisResults.value = result.results.map((result: any, index: number) => {
          console.log(`结果 ${index}:`, result)
          console.log(`统一数据 ${index}:`, result.unified_data)
          return {
            id: `result-${index}`,
            name: uploadedFiles.value[index].name.replace('.json', ''),
            overallScore: result.overall_score || 0,
            detailedScores: result.scores || {},
            unifiedData: result.unified_data || null
          }
        })
        
        // 保存到localStorage以便详情页面使用
        localStorage.setItem('analysisResults', JSON.stringify(analysisResults.value))
        console.log('已保存到localStorage:', analysisResults.value)
      } else {
        console.error('批量分析失败:', result.error)
      }
    }
  } catch (error) {
    console.error('分析过程中出错:', error)
  } finally {
    isAnalyzing.value = false
  }
}

const getScoreClass = (score: number): string => {
  if (score >= 8) return 'excellent'
  if (score >= 6) return 'good'
  if (score >= 4) return 'average'
  return 'poor'
}

const getMetricName = (metric: string): string => {
  return t(`metrics.${metric}`) || metric
}

const viewDetails = (result: AnalysisResult) => {
  console.log('查看详情:', result)
  // 导航到详情页面，传递文件名
  router.push({ 
    name: 'detail', 
    params: { 
      name: result.name,
      filename: uploadedFiles.value.find(f => f.name.replace('.json', '') === result.name)?.name || result.name + '.json'
    } 
  })
}

const exportResult = (result: AnalysisResult) => {
  console.log('导出报告:', result)
  
  // 创建详细的报告数据
  const reportData = {
    dungeon_name: result.name,
    analysis_date: new Date().toISOString(),
    overall_score: result.overallScore,
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

// 生成改进建议
const generateRecommendations = (scores: Record<string, { score: number; detail?: any }>) => {
  const recommendations: string[] = []
  
  if (scores.dead_end_ratio?.score < 0.5) {
    recommendations.push('减少死胡同比例，增加环路连接以提高探索体验')
  }
  
  if (scores.aesthetic_balance?.score < 0.7) {
    recommendations.push('改善美学平衡，调整房间大小和位置分布')
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
  
  if (score >= 8) {
    grade = 'A'
    description = '优秀的地下城设计'
  } else if (score >= 6) {
    grade = 'B'
    description = '良好的地下城设计'
  } else if (score >= 4) {
    grade = 'C'
    description = '一般的地下城设计'
  } else if (score >= 2) {
    grade = 'D'
    description = '需要改进的地下城设计'
  }
  
  return {
    grade,
    description,
    overall_score: score,
    analysis_date: new Date().toISOString()
  }
}

const clearFiles = () => {
  if (uploadedFiles.value.length === 0) {
    alert('没有文件需要清除')
    return
  }
  
  if (confirm(`确定要清除 ${uploadedFiles.value.length} 个文件吗？`)) {
    uploadedFiles.value = []
    analysisResults.value = []
    console.log('已清除所有文件和分析结果')
  }
}

const clearResults = () => {
  if (analysisResults.value.length === 0) {
    alert('没有分析结果需要清除')
    return
  }
  
  if (confirm(`确定要清除 ${analysisResults.value.length} 个分析结果吗？`)) {
    analysisResults.value = []
    console.log('已清除所有分析结果')
  }
}



const exportAllResults = () => {
  if (analysisResults.value.length === 0) {
    alert('没有分析结果可以导出')
    return
  }
  
  const data = JSON.stringify(analysisResults.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `analysis_results_${new Date().toISOString().slice(0, 10)}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  console.log('已导出所有分析结果')
}

const showHelp = () => {
  router.push('/help')
}

onMounted(async () => {
  // 检查API连接
  try {
    await DungeonAPI.healthCheck()
    console.log('API连接正常')
  } catch (error) {
    console.error('API连接失败:', error)
  }
})
</script>

<template>
  <div class="home">
    <div class="main-content" :class="{ 'has-results': analysisResults.length > 0 }">
      <!-- 左侧栏：文件上传和操作 -->
      <div class="left-panel">
        <!-- 文件上传区域 -->
        <div class="upload-section">
          <h2>{{ t('home.uploadTitle') }}</h2>
          <div class="upload-area" @drop="handleDrop" @dragover.prevent @dragenter.prevent>
            <div class="upload-content">
              <div class="upload-icon">📁</div>
              <p>{{ t('home.uploadDescription') }}</p>
              <p class="supported-formats">{{ t('home.supportedFormats') }}</p>
              <input
                ref="fileInput"
                type="file"
                accept=".json"
                multiple
                @change="handleFileSelect"
                style="display: none"
              />
              <button class="upload-btn" @click="fileInput?.click()">
                {{ t('home.selectFiles') }}
              </button>
            </div>
          </div>
          
          <div v-if="uploadedFiles.length > 0" class="file-list">
            <h3>{{ t('home.uploadedFiles') }}</h3>
            <div v-for="(file, index) in uploadedFiles" :key="index" class="file-item">
              <span class="file-name">{{ file.name }}</span>
              <span class="file-size">{{ formatFileSize(file.size) }}</span>
              <button class="remove-btn" @click="removeFile(index)">{{ t('common.delete') }}</button>
            </div>
          </div>
        </div>

        <!-- 快速操作 -->
        <div class="analysis-options">
          <h2>{{ t('home.quickActions') }}</h2>
          <div class="quick-actions">
            <div class="action-card" @click="clearFiles" :class="{ 'disabled': uploadedFiles.length === 0 }">
              <div class="action-icon">🗑️</div>
              <h3>{{ t('home.clearFiles') }}</h3>
              <p>{{ uploadedFiles.length === 0 ? t('home.noFilesToClear') : t('home.clearFilesDescription', { count: uploadedFiles.length }) }}</p>
            </div>

            <div class="action-card" @click="exportAllResults" :class="{ 'disabled': analysisResults.length === 0 }">
              <div class="action-icon">📤</div>
              <h3>{{ t('home.exportResults') }}</h3>
              <p>{{ analysisResults.length === 0 ? t('home.noResultsToExport') : t('home.exportResultsDescription', { count: analysisResults.length }) }}</p>
            </div>
            <div class="action-card" @click="clearResults" :class="{ 'disabled': analysisResults.length === 0 }">
              <div class="action-icon">🗑️</div>
              <h3>{{ t('home.clearResults') }}</h3>
              <p>{{ analysisResults.length === 0 ? t('home.noResultsToClear') : t('home.clearResultsDescription', { count: analysisResults.length }) }}</p>
            </div>
            <div class="action-card" @click="showHelp">
              <div class="action-icon">❓</div>
              <h3>{{ t('home.help') }}</h3>
              <p>{{ t('home.helpDescription') }}</p>
            </div>
            <div class="action-card" @click="router.push('/about')">
              <div class="action-icon">ℹ️</div>
              <h3>{{ t('home.about') }}</h3>
              <p>{{ t('home.aboutDescription') }}</p>
            </div>
          </div>
          
          <div class="stats-section">
            <h3>📈 {{ t('home.systemStats') }}</h3>
            <div class="stats-grid">
              <div class="stat-item">
                <div class="stat-number">{{ uploadedFiles.length }}</div>
                <div class="stat-label">{{ t('home.uploadedFilesCount') }}</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ analysisResults.length }}</div>
                <div class="stat-label">{{ t('home.analysisResultsCount') }}</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">9</div>
                <div class="stat-label">{{ t('home.evaluationMetrics') }}</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">4</div>
                <div class="stat-label">{{ t('home.supportedFormatsCount') }}</div>
              </div>
            </div>
          </div>
          
          <div class="usage-tips">
            <h3>💡 {{ t('home.usageTips') }}</h3>
            <ul>
              <li>{{ t('home.usageTip1') }}</li>
              <li>{{ t('home.usageTip2') }}</li>
              <li>{{ t('home.usageTip3') }}</li>
              <li>{{ t('home.usageTip4') }}</li>
            </ul>
          </div>
          
          <div class="analyze-btn-container">
            <button 
              class="analyze-btn" 
              @click="startAnalysis"
              :disabled="uploadedFiles.length === 0 || isAnalyzing"
            >
              {{ isAnalyzing ? t('home.analyzing') : t('home.startAnalysis') }}
            </button>
          </div>
        </div>
      </div>

      <!-- 右侧栏：分析结果 -->
      <div v-if="analysisResults.length > 0" class="right-panel">
        <div class="results-section">
          <h2>{{ t('home.analysisResults') }}</h2>
          <div class="results-container">
            <div class="results-grid">
              <div 
                v-for="result in analysisResults" 
                :key="result.id" 
                class="result-card"
              >
                <h3>{{ result.name }}</h3>
                <div class="score-overview">
                  <div class="overall-score">
                    <span class="score-label">{{ t('home.overallScore') }}</span>
                    <span class="score-value" :class="getScoreClass(result.overallScore)">
                      {{ result.overallScore.toFixed(2) }}
                    </span>
                  </div>
                </div>
                <div class="detailed-scores">
                  <div v-for="(scoreData, metric) in result.detailedScores" :key="metric" class="metric-score">
                    <span class="metric-name">{{ getMetricName(metric) }}</span>
                    <span class="metric-value" :class="getScoreClass(scoreData.score || 0)">
                      {{ (scoreData.score || 0).toFixed(2) }}
                    </span>
                  </div>
                </div>
                <div class="result-actions">
                  <button class="view-details-btn" @click="viewDetails(result)">
                    {{ t('home.viewDetails') }}
                  </button>
                  <button class="export-btn" @click="exportResult(result)">
                    {{ t('home.exportReport') }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  min-height: calc(100vh - 80px); /* 减去页头高度 */
}

.main-content {
  max-width: 1400px;
  margin: 0 auto;
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: start;
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.main-content.has-results {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
}

.left-panel {
  display: flex;
  flex-direction: column;
  gap: 30px;
  max-width: 800px;
  width: 100%;
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.main-content.has-results .left-panel {
  max-width: none;
}

.right-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 600px;
  animation: slideInFromRight 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes slideInFromRight {
  from {
    opacity: 0;
    transform: translateX(100px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.upload-section {
  margin-bottom: 0;
}

.upload-section h2 {
  color: #333;
  margin-bottom: 20px;
}

.upload-area {
  border: 3px dashed #ddd;
  border-radius: 15px;
  padding: 40px;
  text-align: center;
  transition: all 0.3s ease;
  background: #fafafa;
}

.upload-area:hover {
  border-color: #667eea;
  background: #f0f4ff;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: 10px;
}

.supported-formats {
  color: #666;
  font-size: 0.9rem;
}

.upload-btn {
  background: #667eea;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.3s ease;
}

.upload-btn:hover {
  background: #5a6fd8;
}

.file-list {
  margin-top: 20px;
}

.file-list h3 {
  color: #333;
  margin-bottom: 15px;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 8px;
}

.file-name {
  font-weight: 500;
}

.file-size {
  color: #666;
  font-size: 0.9rem;
}

.remove-btn {
  background: #dc3545;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
}

.analysis-options {
  margin-bottom: 0;
}

.analysis-options h2 {
  color: #333;
  margin-bottom: 20px;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 10px;
  margin-bottom: 20px;
}

.action-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 10px;
  border: 1px solid #e9ecef;
  text-align: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
  user-select: none;
}

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  background: #f0f4ff;
  border-color: #667eea;
}

.action-card:active {
  transform: translateY(0px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.action-card:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.action-icon {
  font-size: 1.5rem;
  margin-bottom: 6px;
}

.action-card h3 {
  color: #333;
  margin-bottom: 4px;
  font-size: 0.9rem;
  font-weight: 600;
}

.action-card p {
  color: #666;
  font-size: 0.7rem;
  margin: 0;
  line-height: 1.2;
}

.stats-section {
  background: #f0f4ff;
  border-radius: 12px;
  padding: 15px;
  margin-bottom: 20px;
}

.stats-section h3 {
  color: #333;
  margin-bottom: 12px;
  font-size: 1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 1.5rem;
  font-weight: bold;
  color: #667eea;
  margin-bottom: 4px;
}

.stat-label {
  color: #555;
  font-size: 0.8rem;
}

.usage-tips {
  background: #f0f4ff;
  border-radius: 12px;
  padding: 15px;
  margin-bottom: 20px;
}

.usage-tips h3 {
  color: #333;
  margin-bottom: 12px;
  font-size: 1rem;
}

.usage-tips ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.usage-tips li {
  color: #555;
  font-size: 0.8rem;
  margin-bottom: 6px;
}

.usage-tips li:last-child {
  margin-bottom: 0;
}

.analyze-btn-container {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}

.analyze-btn {
  background: #28a745;
  color: white;
  border: none;
  padding: 15px 30px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.1rem;
  font-weight: 500;
  transition: background 0.3s ease;
  min-width: 200px;
}

.analyze-btn:hover:not(:disabled) {
  background: #218838;
}

.analyze-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.results-section {
  margin-top: 0;
}

.results-section h2 {
  color: #333;
  margin-bottom: 20px;
  font-size: 1.5rem;
}

.results-container {
  /* 移除flex: 1和overflow-y: auto，让内容自然流动 */
  /* flex: 1; */
  /* overflow-y: auto; */
  padding-right: 10px;
}

/* 移除滚动条样式，因为不再需要 */
/* .results-container::-webkit-scrollbar {
  width: 8px;
}

.results-container::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.results-container::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

.results-container::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
} */

.results-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.result-card {
  background: #f8f9fa;
  border-radius: 15px;
  padding: 20px;
  border: 1px solid #e9ecef;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.result-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.result-card h3 {
  color: #333;
  margin-bottom: 15px;
  font-size: 1.3rem;
}

.score-overview {
  margin-bottom: 20px;
}

.overall-score {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: white;
  border-radius: 8px;
  margin-bottom: 15px;
}

.score-label {
  font-weight: 500;
  color: #333;
}

.score-value {
  font-size: 1.5rem;
  font-weight: bold;
  padding: 5px 10px;
  border-radius: 6px;
}

.score-value.excellent {
  background: #d4edda;
  color: #155724;
}

.score-value.good {
  background: #d1ecf1;
  color: #0c5460;
}

.score-value.average {
  background: #fff3cd;
  color: #856404;
}

.score-value.poor {
  background: #f8d7da;
  color: #721c24;
}

.detailed-scores {
  margin-bottom: 20px;
}

.metric-score {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #e9ecef;
}

.metric-score:last-child {
  border-bottom: none;
}

.metric-name {
  color: #666;
  font-size: 0.9rem;
}

.metric-value {
  font-weight: 500;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.9rem;
}

.result-actions {
  display: flex;
  gap: 10px;
}

.view-details-btn,
.export-btn {
  flex: 1;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.3s ease;
}

.view-details-btn {
  background: #007bff;
  color: white;
}

.view-details-btn:hover {
  background: #0056b3;
}

.export-btn {
  background: #6c757d;
  color: white;
}

.export-btn:hover {
  background: #545b62;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 60px 20px;
  background: #f8f9fa;
  border-radius: 15px;
  border: 2px dashed #dee2e6;
  min-height: 400px;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  opacity: 0.6;
}

.empty-state h3 {
  color: #333;
  margin-bottom: 10px;
  font-size: 1.5rem;
}

.empty-state p {
  color: #666;
  font-size: 1rem;
  margin: 0;
}

@media (max-width: 768px) {
  .home {
    padding: 10px;
  }
  
  .main-content {
    padding: 20px;
  }
  
  .main-content.has-results {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .left-panel {
    gap: 20px;
    max-width: none;
  }
  
  .right-panel {
    min-height: auto;
  }
  
  .title {
    font-size: 2rem;
  }
  
  .quick-actions {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
  
  .action-card {
    padding: 8px;
  }
  
  .action-icon {
    font-size: 1.2rem;
    margin-bottom: 4px;
  }
  
  .action-card h3 {
    font-size: 0.8rem;
    margin-bottom: 2px;
  }
  
  .action-card p {
    font-size: 0.6rem;
  }
  
  .empty-state {
    min-height: 300px;
    padding: 40px 20px;
  }
  
  .empty-icon {
    font-size: 3rem;
  }
  
  .empty-state h3 {
    font-size: 1.2rem;
  }
  
  .empty-state p {
    font-size: 0.9rem;
  }
}
</style>
