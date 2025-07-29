<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
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
  const names: Record<string, string> = {
    accessibility: '可达性',
    aesthetic_balance: '美学平衡',
    loop_ratio: '环路比例',
    dead_end_ratio: '死胡同比例',
    treasure_distribution: '宝藏分布',
    monster_distribution: '怪物分布',
    degree_variance: '度方差',
    door_distribution: '门分布',
    key_path_length: '关键路径长度',
    path_diversity: '路径多样性',
    treasure_monster_distribution: '宝藏怪物分布'
  }
  return names[metric] || metric
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
  // TODO: 实现报告导出功能
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

const loadSampleFiles = async () => {
  // 这里可以加载一些示例文件
  // 由于前端无法直接访问文件系统，我们创建一个示例文件
  const sampleData = {
    name: "示例地下城",
    rooms: [
      { id: "room_1", x: 10, y: 10, width: 20, height: 15, type: "entrance" },
      { id: "room_2", x: 40, y: 10, width: 25, height: 20, type: "treasure" },
      { id: "room_3", x: 70, y: 10, width: 30, height: 25, type: "boss" }
    ],
    corridors: [
      { id: "corridor_1", start: { x: 30, y: 17 }, end: { x: 40, y: 20 } },
      { id: "corridor_2", start: { x: 65, y: 22 }, end: { x: 70, y: 22 } }
    ]
  }
  
  const sampleFile = new File([JSON.stringify(sampleData, null, 2)], 'sample_dungeon.json', { type: 'application/json' })
  addFiles([sampleFile])
  console.log('已加载示例文件')
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
    <div class="main-content">
      <!-- 文件上传区域 -->
      <div class="upload-section">
        <h2>上传地下城文件</h2>
        <div class="upload-area" @drop="handleDrop" @dragover.prevent @dragenter.prevent>
          <div class="upload-content">
            <div class="upload-icon">📁</div>
            <p>拖拽文件到此处或点击选择文件</p>
            <p class="supported-formats">支持格式: JSON, Watabou, Donjon, DungeonDraft</p>
            <input
              ref="fileInput"
              type="file"
              accept=".json"
              multiple
              @change="handleFileSelect"
              style="display: none"
            />
            <button class="upload-btn" @click="fileInput?.click()">
              选择文件
            </button>
          </div>
        </div>
        
        <div v-if="uploadedFiles.length > 0" class="file-list">
          <h3>已上传文件:</h3>
          <div v-for="(file, index) in uploadedFiles" :key="index" class="file-item">
            <span class="file-name">{{ file.name }}</span>
            <span class="file-size">{{ formatFileSize(file.size) }}</span>
            <button class="remove-btn" @click="removeFile(index)">删除</button>
          </div>
        </div>
      </div>

      <!-- 快速操作 -->
      <div class="analysis-options">
        <h2>快速操作</h2>
        <div class="quick-actions">
          <div class="action-card" @click="clearFiles" :class="{ 'disabled': uploadedFiles.length === 0 }">
            <div class="action-icon">🗑️</div>
            <h3>清空文件</h3>
            <p>{{ uploadedFiles.length === 0 ? '没有文件需要清除' : `清除 ${uploadedFiles.length} 个文件` }}</p>
          </div>
          <div class="action-card" @click="loadSampleFiles">
            <div class="action-icon">📁</div>
            <h3>加载示例</h3>
            <p>加载示例地下城文件进行测试</p>
          </div>
          <div class="action-card" @click="exportAllResults" :class="{ 'disabled': analysisResults.length === 0 }">
            <div class="action-icon">📤</div>
            <h3>导出结果</h3>
            <p>{{ analysisResults.length === 0 ? '没有结果可以导出' : `导出 ${analysisResults.length} 个结果` }}</p>
          </div>
          <div class="action-card" @click="showHelp">
            <div class="action-icon">❓</div>
            <h3>使用帮助</h3>
            <p>查看详细的使用说明和教程</p>
          </div>
          <div class="action-card" @click="router.push('/about')">
            <div class="action-icon">ℹ️</div>
            <h3>关于我们</h3>
            <p>了解项目信息和技术特性</p>
          </div>
        </div>
        
        <div class="stats-section">
          <h3>📈 系统统计</h3>
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-number">{{ uploadedFiles.length }}</div>
              <div class="stat-label">已上传文件</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{{ analysisResults.length }}</div>
              <div class="stat-label">分析结果</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">9</div>
              <div class="stat-label">评估指标</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">4</div>
              <div class="stat-label">支持格式</div>
            </div>
          </div>
        </div>
        
        <div class="usage-tips">
          <h3>💡 使用提示</h3>
          <ul>
            <li>支持多种地下城格式：Watabou、Donjon、DungeonDraft等</li>
            <li>拖拽文件到上传区域或点击选择文件按钮</li>
            <li>分析完成后可查看详细的可视化结果</li>
            <li>建议使用Chrome或Firefox浏览器获得最佳体验</li>
          </ul>
        </div>
        
        <button 
          class="analyze-btn" 
          @click="startAnalysis"
          :disabled="uploadedFiles.length === 0 || isAnalyzing"
        >
          {{ isAnalyzing ? '分析中...' : '开始分析' }}
        </button>
      </div>

      <!-- 分析结果 -->
      <div v-if="analysisResults.length > 0" class="results-section">
        <h2>分析结果</h2>
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
                  <span class="score-label">总体评分</span>
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
                  查看详情
                </button>
                <button class="export-btn" @click="exportResult(result)">
                  导出报告
                </button>
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
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  flex: 1;
}

.upload-section {
  margin-bottom: 40px;
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
  margin-bottom: 40px;
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
}

.analyze-btn:hover:not(:disabled) {
  background: #218838;
}

.analyze-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.results-section {
  margin-top: 40px;
  /* 移除flex: 1和overflow: hidden，让内容自然流动 */
  /* flex: 1; */
  /* display: flex; */
  /* flex-direction: column; */
  /* overflow: hidden; */
}

.results-section h2 {
  color: white;
  margin-bottom: 20px;
  text-align: center;
  font-size: 2rem;
  /* 移除flex-shrink: 0; */
  /* flex-shrink: 0; */
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
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
}

.result-card {
  background: #f8f9fa;
  border-radius: 15px;
  padding: 25px;
  border: 1px solid #e9ecef;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.result-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
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

@media (max-width: 768px) {
  .home {
    padding: 10px;
  }
  
  .main-content {
    padding: 20px;
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
}
</style>
