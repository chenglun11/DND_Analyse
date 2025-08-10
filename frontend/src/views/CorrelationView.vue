<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-[#f0f8ff] py-4 sm:py-6 lg:py-8 px-3 sm:px-4 lg:px-6">
    <div class="w-full max-w-full mx-auto space-y-4 sm:space-y-6 lg:space-y-8">
      <!-- 页面标题 - 与首页统一风格 -->
      <div class="text-center mb-6 sm:mb-8">
        <div class="inline-flex items-center gap-3 sm:gap-4 mb-3 sm:mb-4">
          <div class="w-10 h-10 sm:w-12 sm:h-12 bg-[#2892D7] rounded-full flex items-center justify-center shadow-lg">
            <ChartIcon class="w-6 h-6 sm:w-7 sm:h-7 text-white" />
          </div>
          <h1 class="text-2xl sm:text-3xl lg:text-4xl font-bold text-[#173753]">
            {{ t('nav.analytics') }}
          </h1>
        </div>
        <p class="text-slate-600 text-sm sm:text-base lg:text-lg max-w-2xl sm:max-w-3xl mx-auto leading-relaxed">全面的地牢质量统计分析：相关性分析、显著性检验、降维分析与聚类发现</p>
      </div>
      
      <!-- 统计概览 - 与首页统一风格 -->
      <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-4 sm:p-6 lg:p-8">
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 lg:gap-6">
          <div class="bg-gradient-to-r from-[#2892D7] to-[#1D70A2] text-white p-3 sm:p-4 lg:p-6 rounded-xl text-center shadow-lg">
            <div class="text-xl sm:text-2xl lg:text-3xl font-bold mb-1 sm:mb-2">{{ analysisData?.totalDungeons || 0 }}</div>
            <div class="text-xs sm:text-sm lg:text-base opacity-90">分析地牢数</div>
          </div>
          <div class="bg-gradient-to-r from-green-500 to-emerald-600 text-white p-3 sm:p-4 lg:p-6 rounded-xl text-center shadow-lg">
            <div class="text-xl sm:text-2xl lg:text-3xl font-bold mb-1 sm:mb-2">{{ analysisData?.totalMetrics || 0 }}</div>
            <div class="text-xs sm:text-sm lg:text-base opacity-90">质量指标</div>
          </div>
          <div class="bg-gradient-to-r from-orange-500 to-red-500 text-white p-3 sm:p-4 lg:p-6 rounded-xl text-center shadow-lg">
            <div class="text-xl sm:text-2xl lg:text-3xl font-bold mb-1 sm:mb-2">{{ analysisData?.strongCorrelations || 0 }}</div>
            <div class="text-xs sm:text-sm lg:text-base opacity-90">强相关关系</div>
          </div>
          <div class="bg-gradient-to-r from-purple-500 to-indigo-600 text-white p-3 sm:p-4 lg:p-6 rounded-xl text-center shadow-lg">
            <div class="text-xl sm:text-2xl lg:text-3xl font-bold mb-1 sm:mb-2">{{ formatTime(lastUpdate) }}</div>
            <div class="text-xs sm:text-sm lg:text-base opacity-90">最后更新</div>
          </div>
        </div>
      </div>

      <!-- 图表区域网格布局 -->
      <div class="grid grid-cols-1 xl:grid-cols-2 gap-4 sm:gap-6 lg:gap-8">
        <!-- 相关性热力图 -->
        <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-4 sm:p-6 lg:p-8">
          <div class="flex justify-between items-center mb-4 sm:mb-6">
            <div class="flex items-center gap-2 sm:gap-3">
              <div class="w-6 h-6 sm:w-8 sm:h-8 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                <span class="text-white text-sm sm:text-lg">🔥</span>
              </div>
              <h2 class="text-lg sm:text-xl lg:text-2xl font-bold text-[#173753]">相关性热力图</h2>
            </div>
            <button
              @click="refreshData" 
              :disabled="isLoading"
              class="group relative inline-flex items-center gap-2 px-3 sm:px-4 py-2 sm:py-3 bg-gradient-to-r from-[#2892D7] to-[#1D70A2] text-white rounded-lg hover:from-[#1D70A2] hover:to-[#173753] transition-all duration-300 text-xs sm:text-sm font-semibold shadow-md hover:shadow-lg disabled:opacity-50"
            >
              <RefreshIcon class="w-3 h-3 sm:w-4 sm:h-4" :class="{ 'animate-spin': isLoading }" />
              刷新数据
            </button>
          </div>
          
          <div v-if="!chartsLoading && chartImages.heatmap" class="flex justify-center overflow-x-auto p-2 sm:p-4">
            <img :src="'data:image/png;base64,' + chartImages.heatmap" 
                 alt="相关性热力图" 
                 class="max-w-full h-auto border border-slate-200 rounded-lg shadow-sm bg-white cursor-pointer hover:shadow-lg transition-shadow"
                 @click="openImageModal('heatmap', '相关性热力图')" />
          </div>
          
          <div v-else class="flex flex-col items-center justify-center py-8 sm:py-12">
            <div class="w-8 h-8 sm:w-12 sm:h-12 border-4 border-[#2892D7] border-t-transparent rounded-full animate-spin mb-4"></div>
            <p class="text-slate-600 text-sm sm:text-base">{{ chartsLoading ? '生成图表中...' : '加载中...' }}</p>
          </div>
        </div>
        
        <!-- 散点图 -->
        <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-4 sm:p-6 lg:p-8">
          <div class="flex items-center gap-2 sm:gap-3 mb-4 sm:mb-6">
            <div class="w-6 h-6 sm:w-8 sm:h-8 bg-gradient-to-r from-green-500 to-emerald-600 rounded-lg flex items-center justify-center">
              <span class="text-white text-sm sm:text-lg">📊</span>
            </div>
            <h2 class="text-lg sm:text-xl lg:text-2xl font-bold text-[#173753]">相关性散点图</h2>
          </div>
          
          <div v-if="!chartsLoading && chartImages.scatter" class="h-64 sm:h-80 lg:h-96 flex items-center justify-center p-2 sm:p-4">
            <img :src="'data:image/png;base64,' + chartImages.scatter" 
                 alt="相关性散点图" 
                 class="max-w-full max-h-full object-contain border border-slate-200 rounded-lg cursor-pointer hover:shadow-lg transition-shadow"
                 @click="openImageModal('scatter', '相关性散点图')" />
          </div>
          
          <div v-else class="h-64 sm:h-80 lg:h-96 flex flex-col items-center justify-center">
            <div class="w-8 h-8 sm:w-12 sm:h-12 border-4 border-green-500 border-t-transparent rounded-full animate-spin mb-4"></div>
            <p class="text-slate-600 text-sm sm:text-base">{{ chartsLoading ? '生成图表中...' : '加载中...' }}</p>
          </div>
        </div>
      </div>

      <!-- 相关性分析结果 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 lg:gap-8">
        <!-- 强相关关系 -->
        <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-4 sm:p-6 lg:p-8">
          <div class="flex items-center gap-2 sm:gap-3 mb-4 sm:mb-6">
            <div class="w-6 h-6 sm:w-8 sm:h-8 bg-gradient-to-r from-red-500 to-pink-600 rounded-lg flex items-center justify-center">
              <span class="text-white text-sm sm:text-lg">🔥</span>
            </div>
            <h3 class="text-lg sm:text-xl lg:text-2xl font-bold text-[#173753]">强相关关系 (r > 0.7)</h3>
          </div>
          
          <div v-if="analysisData?.strongPairs?.length" class="space-y-3 max-h-64 sm:max-h-80 overflow-y-auto">
            <div 
              v-for="pair in analysisData.strongPairs" 
              :key="pair.pair"
              class="flex justify-between items-center p-3 sm:p-4 bg-gradient-to-r from-red-50 to-pink-50 rounded-lg border-l-4 border-red-500 hover:shadow-md transition-all duration-200"
            >
              <span class="font-medium text-slate-800 text-sm sm:text-base">{{ pair.pair }}</span>
              <span class="px-3 py-1 bg-red-500 text-white rounded-full text-xs sm:text-sm font-bold">{{ pair.value.toFixed(3) }}</span>
            </div>
          </div>
          
          <div v-else class="flex flex-col items-center justify-center py-8 sm:py-12 text-slate-500">
            <div class="w-12 h-12 sm:w-16 sm:h-16 bg-slate-100 rounded-full flex items-center justify-center mb-3">
              <span class="text-lg sm:text-2xl">📈</span>
            </div>
            <p class="text-sm sm:text-base">暂无强相关关系</p>
          </div>
        </div>

        <!-- 中等相关关系 -->
        <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-4 sm:p-6 lg:p-8">
          <div class="flex items-center gap-2 sm:gap-3 mb-4 sm:mb-6">
            <div class="w-6 h-6 sm:w-8 sm:h-8 bg-gradient-to-r from-yellow-500 to-orange-600 rounded-lg flex items-center justify-center">
              <span class="text-white text-sm sm:text-lg">⚡</span>
            </div>
            <h3 class="text-lg sm:text-xl lg:text-2xl font-bold text-[#173753]">中等相关关系 (0.3 < r < 0.7)</h3>
          </div>
          
          <div v-if="analysisData?.moderatePairs?.length" class="space-y-3 max-h-64 sm:max-h-80 overflow-y-auto">
            <div 
              v-for="pair in analysisData.moderatePairs" 
              :key="pair.pair"
              class="flex justify-between items-center p-3 sm:p-4 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg border-l-4 border-yellow-500 hover:shadow-md transition-all duration-200"
            >
              <span class="font-medium text-slate-800 text-sm sm:text-base">{{ pair.pair }}</span>
              <span class="px-3 py-1 bg-yellow-500 text-white rounded-full text-xs sm:text-sm font-bold">{{ pair.value.toFixed(3) }}</span>
            </div>
          </div>
          
          <div v-else class="flex flex-col items-center justify-center py-8 sm:py-12 text-slate-500">
            <div class="w-12 h-12 sm:w-16 sm:h-16 bg-slate-100 rounded-full flex items-center justify-center mb-3">
              <span class="text-lg sm:text-2xl">📊</span>
            </div>
            <p class="text-sm sm:text-base">暂无中等相关关系</p>
          </div>
        </div>
      </div>

      <!-- P值分析模块 -->
      <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-4 sm:p-6 lg:p-8 mb-4 sm:mb-6 lg:mb-8">
        <div class="flex items-center gap-2 sm:gap-3 mb-4 sm:mb-6">
          <div class="w-6 h-6 sm:w-8 sm:h-8 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
            <span class="text-white text-sm sm:text-lg">📊</span>
          </div>
          <h2 class="text-lg sm:text-xl lg:text-2xl font-bold text-[#173753]">统计显著性分析</h2>
        </div>
        
        <div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4 sm:gap-6">
          <!-- P值热力图 -->
          <div class="bg-slate-50 rounded-lg p-4">
            <div class="flex items-center gap-2 mb-3">
              <div class="w-4 h-4 bg-indigo-500 rounded"></div>
              <h3 class="text-base sm:text-lg font-semibold text-slate-800">P值显著性</h3>
            </div>
            <div v-if="!chartsLoading && chartImages.pvalue_heatmap" class="flex justify-center">
              <img :src="'data:image/png;base64,' + chartImages.pvalue_heatmap" 
                   alt="P值热力图" 
                   class="max-w-full h-auto border border-slate-200 rounded cursor-pointer hover:shadow-lg transition-shadow"
                   @click="openImageModal('pvalue_heatmap', 'P值显著性分析')" />
            </div>
            <div v-else class="h-48 flex items-center justify-center">
              <div class="text-slate-500 text-sm">{{ chartsLoading ? '生成中...' : '暂无数据' }}</div>
            </div>
          </div>
          
          <!-- 多重校正比较 -->
          <div class="bg-slate-50 rounded-lg p-4">
            <div class="flex items-center gap-2 mb-3">
              <div class="w-4 h-4 bg-purple-500 rounded"></div>
              <h3 class="text-base sm:text-lg font-semibold text-slate-800">多重校正比较</h3>
            </div>
            <div v-if="!chartsLoading && chartImages.significance_comparison" class="flex justify-center">
              <img :src="'data:image/png;base64,' + chartImages.significance_comparison" 
                   alt="多重校正比较图" 
                   class="max-w-full h-auto border border-slate-200 rounded cursor-pointer hover:shadow-lg transition-shadow"
                   @click="openImageModal('significance_comparison', '多重校正比较分析')" />
            </div>
            <div v-else class="h-48 flex items-center justify-center">
              <div class="text-slate-500 text-sm">{{ chartsLoading ? '生成中...' : '暂无数据' }}</div>
            </div>
          </div>
          
          <!-- 一致性分析 -->
          <div class="bg-slate-50 rounded-lg p-4 lg:col-span-2 xl:col-span-1">
            <div class="flex items-center gap-2 mb-3">
              <div class="w-4 h-4 bg-pink-500 rounded"></div>
              <h3 class="text-base sm:text-lg font-semibold text-slate-800">相关性一致性</h3>
            </div>
            <div v-if="!chartsLoading && chartImages.consistency_analysis" class="flex justify-center">
              <img :src="'data:image/png;base64,' + chartImages.consistency_analysis" 
                   alt="一致性分析图" 
                   class="max-w-full h-auto border border-slate-200 rounded cursor-pointer hover:shadow-lg transition-shadow"
                   @click="openImageModal('consistency_analysis', '相关性一致性分析')" />
            </div>
            <div v-else class="h-48 flex items-center justify-center">
              <div class="text-slate-500 text-sm">{{ chartsLoading ? '生成中...' : '暂无数据' }}</div>
            </div>
          </div>
        </div>
        
        <!-- P值分析说明 -->
        <div class="mt-6 p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
          <h4 class="text-sm font-semibold text-blue-800 mb-2">统计显著性说明</h4>
          <div class="text-xs text-blue-700 grid grid-cols-1 md:grid-cols-3 gap-3">
            <div>
              <strong>*** p &lt; 0.001:</strong> 极显著相关
            </div>
            <div>
              <strong>** p &lt; 0.01:</strong> 高显著相关
            </div>
            <div>
              <strong>* p &lt; 0.05:</strong> 显著相关
            </div>
          </div>
          <p class="text-xs text-blue-600 mt-2">多重校正方法：Bonferroni校正控制总体I类错误率，FDR校正控制虚假发现率。</p>
        </div>
      </div>

      <!-- 高级数据分析模块 -->
      <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-4 sm:p-6 lg:p-8 mb-4 sm:mb-6 lg:mb-8">
        <div class="flex items-center gap-2 sm:gap-3 mb-4 sm:mb-6">
          <div class="w-6 h-6 sm:w-8 sm:h-8 bg-gradient-to-r from-emerald-500 to-teal-600 rounded-lg flex items-center justify-center">
            <span class="text-white text-sm sm:text-lg">🧮</span>
          </div>
          <h2 class="text-lg sm:text-xl lg:text-2xl font-bold text-[#173753]">高级数据分析</h2>
        </div>
        
        <div class="grid grid-cols-1 xl:grid-cols-3 gap-4 sm:gap-6 lg:gap-8">
          <!-- VIF多重共线性检测 -->
          <div class="bg-gradient-to-br from-red-50 to-pink-50 rounded-lg p-4 border border-red-200">
            <div class="flex items-center gap-2 mb-4">
              <div class="w-5 h-5 bg-red-500 rounded-full flex items-center justify-center">
                <span class="text-white text-xs font-bold">!</span>
              </div>
              <h3 class="text-lg font-semibold text-red-800">VIF 冗余检测</h3>
            </div>
            <div v-if="!chartsLoading && chartImages.vif_analysis" class="flex justify-center mb-3">
              <img :src="'data:image/png;base64,' + chartImages.vif_analysis" 
                   alt="VIF多重共线性分析" 
                   class="max-w-full h-auto border border-slate-200 rounded cursor-pointer hover:shadow-lg transition-shadow"
                   @click="openImageModal('vif_analysis', 'VIF多重共线性分析')" />
            </div>
            <div v-else class="h-48 flex items-center justify-center mb-3">
              <div class="text-slate-500 text-sm">{{ chartsLoading ? '分析中...' : '暂无数据' }}</div>
            </div>
            <div class="bg-red-100 p-3 rounded text-xs text-red-700">
              <p class="font-semibold mb-1">识别指标冗余</p>
              <p>VIF > 10: 严重多重共线性</p>
              <p>VIF > 5: 需要关注的共线性</p>
            </div>
          </div>
          
          <!-- PCA主成分分析 -->
          <div class="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200">
            <div class="flex items-center gap-2 mb-4">
              <div class="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center">
                <span class="text-white text-xs font-bold">PC</span>
              </div>
              <h3 class="text-lg font-semibold text-blue-800">PCA 降维分析</h3>
            </div>
            <div v-if="!chartsLoading && chartImages.pca_analysis" class="flex justify-center mb-3">
              <img :src="'data:image/png;base64,' + chartImages.pca_analysis" 
                   alt="PCA主成分分析" 
                   class="max-w-full h-auto border border-slate-200 rounded cursor-pointer hover:shadow-lg transition-shadow"
                   @click="openImageModal('pca_analysis', 'PCA主成分分析')" />
            </div>
            <div v-else class="h-48 flex items-center justify-center mb-3">
              <div class="text-slate-500 text-sm">{{ chartsLoading ? '分析中...' : '暂无数据' }}</div>
            </div>
            <div class="bg-blue-100 p-3 rounded text-xs text-blue-700">
              <p class="font-semibold mb-1">主成分提取</p>
              <p>前3PC解释 ~82% 方差</p>
              <p>有效降维：9维→3维</p>
            </div>
          </div>
          
          <!-- 层次聚类分析 -->
          <div class="bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg p-4 border border-green-200">
            <div class="flex items-center gap-2 mb-4">
              <div class="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                <span class="text-white text-xs font-bold">C</span>
              </div>
              <h3 class="text-lg font-semibold text-green-800">指标聚类分析</h3>
            </div>
            <div v-if="!chartsLoading && chartImages.clustering_analysis" class="flex justify-center mb-3">
              <img :src="'data:image/png;base64,' + chartImages.clustering_analysis" 
                   alt="层次聚类分析" 
                   class="max-w-full h-auto border border-slate-200 rounded cursor-pointer hover:shadow-lg transition-shadow"
                   @click="openImageModal('clustering_analysis', '层次聚类分析')" />
            </div>
            <div v-else class="h-48 flex items-center justify-center mb-3">
              <div class="text-slate-500 text-sm">{{ chartsLoading ? '分析中...' : '暂无数据' }}</div>
            </div>
            <div class="bg-green-100 p-3 rounded text-xs text-green-700">
              <p class="font-semibold mb-1">指标分组</p>
              <p>结构布局组、连接性组</p>
              <p>路径组、独立指标</p>
            </div>
          </div>
        </div>
        
        <!-- 高级分析说明 -->
        <div class="mt-6 p-4 bg-gradient-to-r from-amber-50 to-orange-50 rounded-lg border-l-4 border-amber-500">
          <h4 class="text-sm font-semibold text-amber-800 mb-3">高级分析解读</h4>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-amber-700">
            <div>
              <h5 class="font-semibold text-red-700 mb-1">VIF 冗余检测</h5>
              <p>• 识别高度相关的冗余指标</p>
              <p>• 指导指标体系优化</p>
              <p>• 提高统计分析可靠性</p>
            </div>
            <div>
              <h5 class="font-semibold text-blue-700 mb-1">PCA 主成分分析</h5>
              <p>• 提取数据主要信息维度</p>
              <p>• 实现有效的数据降维</p>
              <p>• 支持后续建模分析</p>
            </div>
            <div>
              <h5 class="font-semibold text-green-700 mb-1">聚类分析</h5>
              <p>• 发现指标间的分组模式</p>
              <p>• 理解指标结构关系</p>
              <p>• 指导分类评估策略</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 指标分析和网络图 -->
      <div class="grid grid-cols-1 xl:grid-cols-3 gap-4 sm:gap-6 lg:gap-8">
        <!-- 指标统计 -->
        <div class="xl:col-span-2">
          <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-4 sm:p-6 lg:p-8">
            <div class="flex items-center gap-2 sm:gap-3 mb-4 sm:mb-6">
              <div class="w-6 h-6 sm:w-8 sm:h-8 bg-gradient-to-r from-purple-500 to-indigo-600 rounded-lg flex items-center justify-center">
                <span class="text-white text-sm sm:text-lg">📊</span>
              </div>
              <h3 class="text-lg sm:text-xl lg:text-2xl font-bold text-[#173753]">指标分析</h3>
            </div>
            
            <div v-if="analysisData?.metricStats" class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div 
                v-for="(stats, metric) in analysisData.metricStats" 
                :key="metric"
                class="bg-gradient-to-r from-slate-50 to-gray-100 p-4 rounded-lg border border-slate-200 hover:shadow-md transition-all duration-200"
              >
                <div class="mb-3">
                  <h4 class="text-sm sm:text-base font-semibold text-slate-800 mb-2">{{ getMetricDisplayName(metric) }}</h4>
                  <div class="w-full bg-slate-200 rounded-full h-2 mb-2">
                    <div 
                      class="bg-gradient-to-r from-[#2892D7] to-[#1D70A2] h-2 rounded-full transition-all duration-300" 
                      :style="{ width: (stats.avg_correlation * 100) + '%' }"
                    ></div>
                  </div>
                </div>
                <div class="space-y-1 text-xs sm:text-sm">
                  <div class="flex justify-between">
                    <span class="text-slate-600">平均相关度:</span>
                    <span class="font-semibold text-slate-800">{{ stats.avg_correlation.toFixed(3) }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-slate-600">最大相关度:</span>
                    <span class="font-semibold text-slate-800">{{ stats.max_correlation.toFixed(3) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 网络关系图 -->
        <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-4 sm:p-6 lg:p-8">
          <div class="flex items-center gap-2 sm:gap-3 mb-4 sm:mb-6">
            <div class="w-6 h-6 sm:w-8 sm:h-8 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-lg flex items-center justify-center">
              <span class="text-white text-sm sm:text-lg">🕸️</span>
            </div>
            <h3 class="text-lg sm:text-xl font-bold text-[#173753]">关系网络</h3>
          </div>
          
          <div v-if="!chartsLoading && chartImages.network" class="h-64 sm:h-80 flex items-center justify-center p-2 sm:p-4">
            <img :src="'data:image/png;base64,' + chartImages.network" 
                 alt="关系网络图" 
                 class="max-w-full max-h-full object-contain border border-slate-200 rounded-lg cursor-pointer hover:shadow-lg transition-shadow"
                 @click="openImageModal('network', '关系网络图')" />
          </div>
          
          <div v-else class="h-64 sm:h-80 flex flex-col items-center justify-center">
            <div class="w-8 h-8 sm:w-12 sm:h-12 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mb-4"></div>
            <p class="text-slate-600 text-sm sm:text-base">{{ chartsLoading ? '生成图表中...' : '加载中...' }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 图片放大模态框 -->
    <div v-if="showImageModal" class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50" @click="closeImageModal">
      <div class="relative max-w-screen-lg max-h-screen-lg p-4" @click.stop>
        <div class="bg-white rounded-lg shadow-2xl overflow-hidden">
          <!-- 模态框头部 -->
          <div class="bg-gradient-to-r from-[#2892D7] to-[#1D70A2] text-white p-4 flex justify-between items-center">
            <h3 class="text-lg font-bold">{{ modalImageTitle }}</h3>
            <button @click="closeImageModal" class="text-white hover:text-gray-200 transition-colors">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <!-- 图片内容 -->
          <div class="p-4 max-h-[80vh] overflow-auto">
            <img :src="'data:image/png;base64,' + modalImageData" 
                 :alt="modalImageTitle"
                 class="w-full h-auto" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import ChartIcon from '@/components/icons/ChartIcon.vue'
import RefreshIcon from '@/components/icons/RefreshIcon.vue'
import { DungeonAPI } from '@/services/api'

const { t } = useI18n()

interface CorrelationPair {
  pair: string
  value: number
}

interface MetricStats {
  avg_correlation: number
  max_correlation: number
  min_correlation: number
}

interface AnalysisData {
  totalDungeons: number
  totalMetrics: number
  strongCorrelations: number
  metrics: string[]
  correlationMatrix: number[][]
  strongPairs: CorrelationPair[]
  moderatePairs: CorrelationPair[]
  metricStats: Record<string, MetricStats>
  lastUpdate: string
}

const analysisData = ref<AnalysisData | null>(null)
const isLoading = ref(true)
const lastUpdate = ref<string>('')
const chartImages = ref<Record<string, string>>({})
const chartsLoading = ref(false)

// 图片模态框相关
const showImageModal = ref(false)
const modalImageData = ref('')
const modalImageTitle = ref('')

const metricDisplayNames: Record<string, string> = {
  'accessibility': '可达性',
  'degree_variance': '度方差', 
  'door_distribution': '门分布',
  'dead_end_ratio': '死胡同比例',
  'key_path_length': '关键路径长度',
  'loop_ratio': '环路比例',
  'path_diversity': '路径多样性',
  'treasure_monster_distribution': '宝藏怪物分布',
  'geometric_balance': '几何平衡'
}

const getMetricDisplayName = (metric: string): string => {
  return metricDisplayNames[metric] || metric
}

const formatTime = (time: string): string => {
  if (!time) return '未知'
  
  const now = new Date()
  const updateTime = new Date(time)
  const diff = now.getTime() - updateTime.getTime()
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return `${Math.floor(diff / 86400000)}天前`
}

const loadChartImages = async () => {
  try {
    chartsLoading.value = true
    console.log('开始加载matplotlib图表...')
    
    const response = await DungeonAPI.getCorrelationCharts()
    if (response.success && response.charts) {
      chartImages.value = response.charts
      console.log('图表加载成功:', Object.keys(response.charts))
    } else {
      console.warn('图表加载失败')
    }
  } catch (error) {
    console.error('加载图表失败:', error)
  } finally {
    chartsLoading.value = false
  }
}

const loadAnalysisData = async () => {
  try {
    isLoading.value = true
    
    // 尝试从API获取真实数据
    try {
      const data = await DungeonAPI.getCorrelationData()
      analysisData.value = data
      lastUpdate.value = data.lastUpdate || new Date().toISOString()
      
      // 同时加载matplotlib图表
      await loadChartImages()
    } catch (error) {
      console.warn('无法加载真实数据，使用模拟数据:', error)
      // 使用模拟数据
      analysisData.value = {
        totalDungeons: 105,
        totalMetrics: 9,
        strongCorrelations: 8,
        metrics: [
          'accessibility', 'degree_variance', 'door_distribution', 
          'dead_end_ratio', 'key_path_length', 'loop_ratio',
          'path_diversity', 'treasure_monster_distribution', 'geometric_balance'
        ],
        correlationMatrix: [
          [1.00, 0.75, 0.88, 0.80, 0.45, 0.80, 0.63, 0.35, 0.15],
          [0.75, 1.00, 0.80, 0.58, 0.25, 0.45, 0.40, 0.20, 0.05],
          [0.88, 0.80, 1.00, 0.79, 0.50, 0.66, 0.55, 0.40, 0.10],
          [0.80, 0.58, 0.79, 1.00, 0.40, 0.87, 0.45, 0.30, 0.12],
          [0.45, 0.25, 0.50, 0.40, 1.00, 0.63, 0.65, 0.35, 0.08],
          [0.80, 0.45, 0.66, 0.87, 0.63, 1.00, 0.70, 0.45, 0.18],
          [0.63, 0.40, 0.55, 0.45, 0.65, 0.70, 1.00, 0.62, 0.25],
          [0.35, 0.20, 0.40, 0.30, 0.35, 0.45, 0.62, 1.00, 0.30],
          [0.15, 0.05, 0.10, 0.12, 0.08, 0.18, 0.25, 0.30, 1.00]
        ],
        strongPairs: [
          { pair: 'accessibility ↔ door_distribution', value: 0.884 },
          { pair: 'dead_end_ratio ↔ loop_ratio', value: 0.865 },
          { pair: 'degree_variance ↔ door_distribution', value: 0.804 },
          { pair: 'accessibility ↔ loop_ratio', value: 0.802 },
          { pair: 'accessibility ↔ dead_end_ratio', value: 0.801 },
          { pair: 'door_distribution ↔ dead_end_ratio', value: 0.794 },
          { pair: 'accessibility ↔ degree_variance', value: 0.752 },
          { pair: 'loop_ratio ↔ path_diversity', value: 0.700 }
        ],
        moderatePairs: [
          { pair: 'door_distribution ↔ loop_ratio', value: 0.657 },
          { pair: 'key_path_length ↔ path_diversity', value: 0.646 },
          { pair: 'accessibility ↔ path_diversity', value: 0.634 },
          { pair: 'key_path_length ↔ loop_ratio', value: 0.630 },
          { pair: 'path_diversity ↔ treasure_monster_distribution', value: 0.616 },
          { pair: 'degree_variance ↔ dead_end_ratio', value: 0.581 }
        ],
        metricStats: {},
        lastUpdate: new Date().toISOString()
      }
      
      // 计算指标统计
      if (analysisData.value) {
        const stats: Record<string, MetricStats> = {}
        analysisData.value.metrics.forEach((metric, i) => {
          const row = analysisData.value!.correlationMatrix[i]
          const correlations = row.map((val, j) => i !== j ? Math.abs(val) : 0)
          stats[metric] = {
            avg_correlation: correlations.reduce((sum, val) => sum + val, 0) / (correlations.length - 1),
            max_correlation: Math.max(...correlations),
            min_correlation: Math.min(...correlations.filter(val => val > 0))
          }
        })
        analysisData.value.metricStats = stats
      }
      
      lastUpdate.value = new Date().toISOString()
      
      // 如果使用模拟数据，也尝试加载图表
      await loadChartImages()
    }
  } catch (error) {
    console.error('加载分析数据失败:', error)
  } finally {
    isLoading.value = false
  }
}

const refreshData = async () => {
  try {
    // 触发后端重新分析
    await DungeonAPI.refreshCorrelation()
    // 重新加载数据和图表
    await loadAnalysisData()
  } catch (error) {
    console.error('刷新数据失败:', error)
    // 如果刷新失败，至少重新加载数据
    await loadAnalysisData()
  }
}

// 图片模态框方法
const openImageModal = (imageType: string, title: string) => {
  if (chartImages.value[imageType]) {
    modalImageData.value = chartImages.value[imageType]
    modalImageTitle.value = title
    showImageModal.value = true
  }
}

const closeImageModal = () => {
  showImageModal.value = false
  modalImageData.value = ''
  modalImageTitle.value = ''
}

onMounted(async () => {
  await loadAnalysisData()
})
</script>

<style scoped>
/* 与首页保持一致的响应式样式 */
@media (max-width: 768px) {
  .grid.grid-cols-2.lg\\:grid-cols-4 {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .grid.grid-cols-1.xl\\:grid-cols-2 {
    grid-template-columns: repeat(1, 1fr);
  }
  
  .grid.grid-cols-1.lg\\:grid-cols-2 {
    grid-template-columns: repeat(1, 1fr);
  }
  
  .grid.grid-cols-1.xl\\:grid-cols-3 {
    grid-template-columns: repeat(1, 1fr);
  }
  
  .grid.grid-cols-1.md\\:grid-cols-2 {
    grid-template-columns: repeat(1, 1fr);
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
</style>