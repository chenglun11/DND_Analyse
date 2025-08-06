import { HomeIcon } from '@heroicons/vue/24/outline'
import { getEmitHelpers } from 'typescript'
import { createI18n } from 'vue-i18n'

// 中文语言包
const zh = {
  // 通用
  common: {
    back: '返回',
    refresh: '刷新',
    loading: '加载中...',
    error: '错误',
    success: '成功',
    cancel: '取消',
    confirm: '确认',
    save: '保存',
    delete: '删除',
    edit: '编辑',
    view: '查看',
    export: '导出',
    import: '导入',
    search: '搜索',
    filter: '筛选',
    sort: '排序',
    clear: '清除',
    close: '关闭',
    next: '下一步',
    previous: '上一步',
    submit: '提交',
    reset: '重置',
    yes: '是',
    no: '否',
    ok: '确定',
    actions: '操作',
    quickStart: '快速开始',
    functionGuide: '功能指南',
    faq: '常见问题',
    coreFeatures: '核心功能',
    unknown: '未知地下城',
    noData: '暂无数据',
    notAvailable: 'N/A',
    download: '下载',
    loadingFailed: '加载失败',
    retry: '重试'
  },

  // 导航
  nav: {
    home: '首页',
    test: '测试',
    about: '关于',
    help: '帮助',
    detail: '详情'
  },

  // 应用信息 
  app: {
    title: '地下城分析器',
    subtitle: '专业的D&D地下城质量评估工具',
    description: '一个强大的地下城质量分析工具，支持多种格式的地下城文件分析'
  },

  // 首页
  home: {
    analysisResultsCount: '共评估 ({count}) 个文件',
    title: '地下城质量评估系统',
    subtitle: '上传地下城地图文件，获取详细的质量分析报告',
    uploadFiles: '上传文件',
    dragAndDrop: '拖拽文件到此处，或点击选择文件',
    supportedFormats: '支持格式：JSON',
    selectFiles: '选择文件',
    uploadedFiles: '已上传文件',
    uploadPrompt: '上传文件后即可开始分析',
    analysisConfig: '分析配置',
    analysisConfigDescription: '配置分析参数以获得更好的结果',
    startAnalysis: '开始分析 ({count} 个文件)',
    analyzing: '分析中... ({current}/{total})',
    progress: '已完成 {completed} / {total} 个文件 ({percentage}%)',
    clickToAnalyze: '点击开始批量分析所有上传的文件',
    pleaseUploadFirst: '请先上传文件',
    viewAllDetails: '查看所有详情',
    viewDetails: '查看详情',
    exportResults: '导出结果',
    clearResults: '清除结果',
    fileNumber: '文件 {current} / {total}',
    analyzeAll: '分析所有文件',
    analysisResults: '分析结果'
  },

  // 详情页
  detail: {
    sortBy: '排序方式',
    sortByName: '按名称排序',
    sortByScore: '按评分排序',
    sortByIndex: '按顺序排序',
    averageScore: '平均评分',
    highestScore: '最高评分',
    dungeonCount: '地下城数量',
    batchOverview: '批量分析概览',
    hideOverview: '隐藏概览',
    showOverview: '批量概览',
    backButton: '返回',
    backButtonTitle: '返回上一页',
    refreshButton: '刷新',
    exportReport: '导出报告',
    analysisResults: '分析结果',
    dungeonVisualization: '地下城可视化',
    canvasVisualization: 'Canvas可视化',
    generatedImage: '生成的图像',
    noVisualizationData: '没有可视化数据',
    overallScore: '总体评分',
    improvementSuggestions: '改进建议',
    metricDetails: '指标详情',
    disabled: '(已禁用)',
    noSuggestions: '当前设计表现优秀，暂无改进建议',
    noData: '没有数据',
    multipleDetails: '多个详情',
    showing: '显示',
    of: '共',
    items: '项',
    previous: '上一页',
    next: '下一页',
    page: '第',
    noDetailAvailable: '没有可用的详情数据',
    pageInfo: '第 {current} 页，共 {total} 页',
    analysisDisabled: '分析参数已禁用',
    noScoreData: '没有可用的评分数据',
    overallScoreDisabled: '已禁用总体评分',
    viewDetailedScores: '可查看详细指标分数',
    scoreInfo: '分数信息',
    scoreFilter: '评分筛选',
    allScore: '全部评分',
    highScore: '高分 0.8+',
    mediumScore: '中等 0.5-0.8',
    lowScore: '低分 <0.5',
    current: '当前',
    noMatchDungeon: '没有找到匹配的地下城',
    tryAdjustFilter: '请尝试调整筛选条件',
    homeButton: '首页',
    singleAnalysis: '单个分析',
    batchAnalysis: '批量分析 ({count} 个文件)',
    filteredCount: '已筛选: {count} / {total}',
    currentPage: '当前查看: {current} / {total}',
    loadingAnalysisResults: '正在加载分析结果...',
    pleaseWait: '请稍候',
    backToHome: '返回首页'
  },

  // 帮助页
  help: {
    backButton: '← 返回首页',
    title: '使用帮助',
    subtitle: '详细的使用指南和常见问题',
    fileUpload: {
      title: '文件上传',
      content: {
        0: '支持拖拽文件到上传区域',
        1: '支持点击选择文件按钮',
        2: '支持多种JSON格式的地下城文件',
        3: '支持批量上传多个文件',
        4: '支持的文件格式：Watabou、Donjon、DungeonDraft等'
      }
    },
    analysis: {
      title: '分析功能',
      content: {
        0: '自动评估地下城质量',
        1: '生成可视化图像',
        2: '提供详细的分析报告',
        3: '计算9个核心质量指标',
        4: '生成改进建议'
      }
    },
    results: {
      title: '📈 结果查看',
      content: {
        0: '点击"查看详情"查看完整报告',
        1: '支持导出分析结果',
        2: '提供改进建议',
        3: '可视化路径分析',
        4: '质量评分详情'
      }
    },
    export: {
      title: '数据导出',
      content: {
        0: '导出JSON格式的分析结果',
        1: '导出可视化图像',
        2: '批量导出多个文件结果',
        3: '自定义导出选项',
        4: '支持多种导出格式'
      }
    },
    quickSteps: [
      {
        step: 1,
        title: '上传文件',
        description: '拖拽或选择地下城JSON文件',
        icon: '📁'
      },
      {
        step: 2,
        title: '开始分析',
        description: '点击"开始分析"按钮',
        icon: '⚡'
      },
      {
        step: 3,
        title: '查看结果',
        description: '等待分析完成，查看评分',
        icon: '📊'
      },
      {
        step: 4,
        title: '导出报告',
        description: '导出详细的分析报告',
        icon: '💾'
      }
    ],
    faqs: [
      {
        question: '支持哪些地下城文件格式？',
        answer: '目前支持Watabou、Donjon、DungeonDraft等多种格式的JSON文件。每种格式都有专门的适配器进行转换。'
      },
      {
        question: '分析需要多长时间？',
        answer: '单个文件分析通常在几秒到几十秒之间，取决于地下城的复杂程度。批量分析时间会相应增加。'
      },
      {
        question: '如何理解质量评分？',
        answer: '评分范围是0-100，分数越高表示地下城质量越好。系统会从可达性、美学平衡、环路比例等多个维度进行评估。'
      },
      {
        question: '可以分析多大的地下城？',
        answer: '理论上没有大小限制，但建议单个地下城房间数量不超过1000个，以确保最佳性能。'
      },
      {
        question: '分析结果会保存吗？',
        answer: '当前会话的分析结果会保存在浏览器中，刷新页面后会丢失。建议及时导出重要结果。'
      },
      {
        question: '如何获得更好的分析结果？',
        answer: '确保地下城文件格式正确，房间和走廊信息完整。系统会自动处理常见的数据问题。'
      }
    ],
    usageTips: {
      title: '使用提示',
      tip1: '建议使用Chrome或Firefox浏览器获得最佳体验',
      tip2: '支持批量分析多个文件，提高工作效率',
      tip3: '分析结果会自动保存，刷新页面后会丢失',
      tip4: '可以随时导出分析结果，避免数据丢失',
      tip5: '系统会自动处理常见的数据格式问题',
      tip6: '可视化图像支持缩放和交互操作',
      tip7: '质量评分基于9个核心指标，全面评估地下城质量'
    },
    metricsExplanation: {
      title: '质量评估指标说明',
      accessibility: {
        title: '可达性评估 (Accessibility)',
        description: '评估地下城各区域的连通性和可达性，确保玩家能够到达所有重要区域。'
      },
      geometric_balance: {
        title: '几何平衡 (Geometric Balance)',
        description: '分析房间布局的几何平衡性，评估空间设计的合理性。'
      },
      loop_ratio: {
        title: '环路比例 (Loop Ratio)',
        description: '计算地下城中的环路结构比例，适当的环路可以增加探索的趣味性。'
      },
      dead_end_ratio: {
        title: '死胡同比例 (Dead End Ratio)',
        description: '评估死胡同和无效路径的比例，过多的死胡同会影响游戏体验。'
      }
    },
    quickActions: {
      title: '快速操作',
      startAnalysis: '开始分析',
      about: '关于我们',
      test: '功能测试'
    }
  },

  // 关于页
  about: {
    backButton: '← 返回首页',
    title: '关于地下城分析器',
    subtitle: '专业的D&D地下城质量评估工具',
    intro: {
      title: '项目简介',
      description1: '地下城分析器是一个专门为D&D（龙与地下城）游戏设计的智能工具，旨在帮助游戏设计师和地下城制作者创建高质量的地下城。',
      description2: '通过先进的算法和9个核心评估指标，我们能够自动分析地下城的结构、布局和游戏性，提供详细的质量评估和改进建议。'
    },
    features: [
      {
        icon: '🎯',
        title: '智能质量评估',
        description: '基于9个核心指标的地下城质量评估系统'
      },
      {
        icon: '📊',
        title: '可视化分析',
        description: '生成详细的可视化图表和路径分析'
      },
      {
        icon: '🔄',
        title: '多格式支持',
        description: '支持Watabou、Donjon、DungeonDraft等多种格式'
      },
      {
        icon: '⚡',
        title: '批量处理',
        description: '支持批量上传和分析多个地下城文件'
      },
      {
        icon: '📈',
        title: '详细报告',
        description: '生成包含改进建议的详细分析报告'
      },
      {
        icon: '💾',
        title: '结果导出',
        description: '支持导出分析结果和可视化图像'
      }
    ],
    qualityMetrics: [
      { name: '可达性评估', description: '评估地下城各区域的连通性和可达性' },
      { name: '几何平衡', description: '分析房间布局的几何平衡性' },
      { name: '环路比例', description: '计算地下城中的环路结构比例' },
      { name: '死胡同比例', description: '评估死胡同和无效路径的比例' },
      { name: '宝藏分布', description: '分析宝藏和战利品的分布合理性' },
      { name: '怪物分布', description: '评估怪物和敌人的分布策略' },
      { name: '关键路径长度', description: '分析主要路径的长度和复杂度' },
      { name: '度数方差', description: '评估房间连接度的分布情况' },
      { name: '空间推理', description: '分析空间布局的逻辑性和合理性' }
    ],
    techStack: [
      { category: '前端', items: ['Vue 3', 'TypeScript', 'Vite', 'Tailwind CSS'] },
      { category: '后端', items: ['Python', 'Flask', 'NumPy', 'Pandas'] },
      { category: '算法', items: ['A*路径算法', 'BFS搜索', '图论分析'] },
      { category: '可视化', items: ['Canvas API', 'SVG', 'Chart.js'] }
    ],
    techStackCategories: {
      0: '前端',
      1: '后端',
      2: '算法',
      3: '可视化'
    }
  },

  // 质量指标
  metrics: {
    accessibility: '可达性',
    geometric_balance: '几何平衡',
    loop_ratio: '环路比例',
    dead_end_ratio: '死胡同比例',
    degree_variance: '度方差',
    door_distribution: '门分布',
    key_path_length: '关键路径长度',
    path_diversity: '路径多样性',
    treasure_monster_distribution: '宝藏怪物分布'
  },

  // 指标类别
  metricCategories: {
    layout: '布局设计',
    gameplay: '游戏性',
    navigation: '导航路径'
  },

  // 指标描述
  metricDescriptions: {
    accessibility: {
      description: '评估各区域的可达性和连通程度',
      good: '玩家可以轻松到达各个区域',
      poor: '某些区域难以到达，需要改善路径设计'
    },
    geometric_balance: {
      description: '分析房间布局的几何平衡性和对称性',
      good: '房间布局几何平衡良好',
      poor: '房间布局的几何平衡需要改善'
    },
    loop_ratio: {
      description: '计算地下城中环路结构的比例',
      good: '环路设计合理，避免线性体验',
      poor: '环路较少，可能导致线性体验'
    },
    dead_end_ratio: {
      description: '评估死胡同和无效路径的比例',
      good: '死胡同比例适中',
      poor: '死胡同过多，影响探索体验'
    },
    treasure_monster_distribution: {
      description: '分析宝藏和怪物的分布合理性',
      good: '宝藏和怪物分布合理',
      poor: '宝藏和怪物分布需要调整'
    },
    degree_variance: {
      description: '评估房间连接度的分布情况',
      good: '房间连接度分布均匀',
      poor: '房间连接度分布不均匀'
    },
    door_distribution: {
      description: '分析门的分布和连接情况',
      good: '门分布合理',
      poor: '门分布需要优化'
    },
    key_path_length: {
      description: '评估关键路径的长度和复杂度',
      good: '关键路径长度适中',
      poor: '关键路径过长或过短'
    },
    path_diversity: {
      description: '分析路径的多样性和选择性',
      good: '路径多样性良好',
      poor: '路径多样性需要改善'
    }
  },

  // 指标选择器
  metricSelector: {
    title: '评估指标选择',
    selectAll: '全选',
    deselectAll: '全不选',
    selectedCount: '已选择 {count} / {total} 项',
    apply: '应用选择',
    reset: '重置',
    saved: '已保存'
  },

  // 评分等级
  scoreLevels: {
    excellent: '优秀',
    good: '良好',
    average: '一般',
    poor: '较差'
  },

  // 确认对话框
  confirm: {
    deleteFile: '确定要删除这个文件吗？',
    clearAllFiles: '确定要清除所有文件吗？',
    clearAllResults: '确定要清除所有结果吗？',
    clearResults: '确认清除',
    clearResultsConfirm: '确定要清除 {count} 个分析结果吗？此操作无法撤销。',
    exportData: '确定要导出数据吗？'
  },

  // 错误信息
  errors: {
    fileUploadFailed: '文件上传失败',
    analysisFailed: '分析失败',
    analysisError: '分析错误',
    networkError: '网络错误',
    serverError: '服务器错误',
    unknownError: '未知错误',
    fileNotSupported: '不支持的文件格式',
    fileTooLarge: '文件过大',
    noFilesSelected: '未选择文件',
    missingFilename: '缺少文件名参数',
    exportFailed: '报告导出失败，请重试',
    notFound: '页面未找到',
    pageNotFound: '抱歉，您访问的页面不存在或已被移除。',
    suggestions: '您可能想要访问：'
  },

  // 改进建议
  suggestions: {
    deadEndRatio: {
      title: '减少死胡同',
      description: '当前死胡同比例较高，建议增加环路连接以改善探索体验。'
    },
    deadEndRatioOptimize: {
      title: '优化死胡同分布',
      description: '死胡同比例适中但仍有优化空间。建议将死胡同放置在次要路径上，保持主要路径畅通。'
    },
    geometricBalance: {
      title: '改善几何平衡',
      description: '房间布局的几何平衡需要改善，建议调整房间大小和位置分布。'
    },
    treasureMonsterDistribution: {
      title: '优化宝藏和怪物分布',
      description: '宝藏和怪物分布需要调整，以提供更好的游戏体验。'
    },
    treasureMonsterDistributionBalance: {
      title: '平衡宝藏-怪物比例',
      description: '宝藏和怪物分布基本合理，但可以进一步优化比例，确保挑战与奖励的平衡。'
    },
    accessibility: {
      title: '改善可达性',
      description: '某些区域难以到达，建议优化路径设计。'
    },
    pathDiversity: {
      title: '增加路径多样性',
      description: '路径多样性较低，建议添加不同的探索路径。'
    },
    pathDiversityOptimize: {
      title: '优化路径设计',
      description: '路径多样性适中，考虑添加一些隐藏路径或分支路线来增加探索乐趣。'
    },
    loopRatio: {
      title: '增加环路设计',
      description: '环路比例较低，建议添加循环路径让玩家能够回到之前的区域，改善地图探索。'
    },
    loopRatioOptimize: {
      title: '优化环路分布',
      description: '环路设计基本合理，考虑在关键区域添加小环路来增强探索体验。'
    },
    degreeVariance: {
      title: '优化连接度分布',
      description: '房间连接度方差过大，建议平衡每个房间的连接数量，避免某些房间过于孤立或过于拥挤。'
    },
    doorDistribution: {
      title: '改善门分布',
      description: '门分布不合理，建议在关键路径上适当添加门，减少次要路径上的门使用。'
    },
    keyPathLength: {
      title: '优化关键路径长度',
      description: '关键路径过短或过长，建议设计适中的关键路径长度，既不会让玩家感到无聊也不会过于复杂。'
    },
    roomCount: {
      title: '增加房间数量',
      description: '目前只有{count}个房间，建议增加到10-20个房间以提供更丰富的探索空间。'
    },
    roomCountOptimize: {
      title: '精简房间设计',
      description: '房间数量较多({count}个房间)，建议合并一些功能相似的房间以避免过度复杂。'
    },
    corridorDensity: {
      title: '增加连接走廊',
      description: '房间连接较少，建议增加走廊数量以改善房间连通性。'
    },
    corridorDensityOptimize: {
      title: '优化走廊设计',
      description: '走廊过多可能使迷宫过于复杂，建议精简一些不必要的走廊。'
    },
    overallScoreRedesign: {
      title: '全面重新设计',
      description: '总体评分较低，建议从多个维度重新设计地下城，重点关注可达性、路径设计和游戏元素分布。'
    },
    overallScoreOptimize: {
      title: '关键优化',
      description: '设计基本合理但仍有改进空间。建议针对评分较低的指标进行针对性优化。'
    },
    overallScoreExcellent: {
      title: '保持优秀设计',
      description: '当前设计表现优秀！建议保持这种设计风格作为其他地下城设计的参考模板。'
    },
    continuousOptimization: {
      title: '持续优化',
      description: '当前设计表现良好，建议继续关注细节优化，如房间装饰和氛围营造。'
    }
  },

  // 成功信息
  success: {
    fileUploaded: '文件上传成功',
    analysisCompleted: '分析完成',
    dataExported: '数据导出成功',
    settingsSaved: '设置保存成功',
    reportExported: '报告导出成功！'
  },

  // 批量评估
  batch: {
    title: '批量评估详情',
    subtitle: '共 {count} 个地下城',
    summary: '批量统计',
    totalDungeons: '总地下城数',
    averageScore: '平均评分',
    excellentCount: '优秀数量',
    needsImprovementCount: '需改进数量',
    filterByScore: '按评分筛选',
    allScores: '所有评分',
    excellentOnly: '仅优秀',
    goodOnly: '仅良好',
    averageOnly: '仅一般',
    poorOnly: '仅较差',
    sortBy: '排序方式',
    sortByName: '按名称',
    sortByScore: '按评分',
    sortByGrade: '按等级',
    sortByDate: '按日期',
    gridView: '网格视图',
    listView: '列表视图',
    exportAll: '导出所有',
    refreshAll: '刷新所有',
    noResults: '没有符合条件的结果',
    showOverview: '批量概览',
    hideOverview: '隐藏概览',
    viewDetail: '查看详情',
    excellentCountLabel: '优秀地下城',
    goodCountLabel: '良好地下城',
    averageCountLabel: '一般地下城',
    poorCountLabel: '较差地下城'
  },

  // 批量测试
  batchTest: {
    title: '批量测试',
    subtitle: '批量评估多个地下城文件',
    testOptions: '测试选项',
    testMode: '测试模式',
    fileUpload: '文件上传',
    directoryPath: '目录路径',
    timeout: '超时时间（秒）',
    timeoutPlaceholder: '30',
    outputFormat: '输出格式',
    jsonFormat: 'JSON格式',
    summaryFormat: '汇总格式',
    uploadFiles: '上传文件',
    dragAndDrop: '拖拽文件到此处或点击选择文件',
    supportedFormats: '支持格式: JSON',
    selectFiles: '选择文件',
    uploadedFiles: '已上传文件',
    analyzeAll: '分析所有文件',
    analyzing: '分析中...',
    analysisResults: '分析结果',
    viewDetails: '查看详情',
    viewAllDetails: '查看所有详情',
    export: '导出'
  },

  // 多详情模态框
  multipleDetailsModal: {
    title: '多个地下城详情',
    subtitle: '共 {count} 个地下城',
    summary: '批量统计',
    totalDungeons: '总地下城数',
    averageScore: '平均评分',
    excellentCount: '优秀数量',
    needsImprovementCount: '需改进数量',
    filterByScore: '按评分筛选',
    allScores: '所有评分',
    excellentOnly: '仅优秀',
    goodOnly: '仅良好',
    averageOnly: '仅一般',
    poorOnly: '仅较差',
    sortBy: '排序方式',
    sortByName: '按名称',
    sortByScore: '按评分',
    sortByDate: '按日期',
    gridView: '网格视图',
    listView: '列表视图',
    exportAll: '导出所有',
    refreshAll: '刷新所有',
    noResults: '没有符合条件的结果'
  },
  dungeonVisualizer: {
    title: '地下城可视化',
    canvas: 'Canvas',
    image: 'Image',
    resetCamera: '重置视角',
    hideGrid: '隐藏网格',
    showGrid: '显示网格',
    hideLabels: '隐藏标签',
    showLabels: '显示标签',
    viewFullscreen: '查看大图'
  },
  fullyreport: {
    detailed: '详细分析',
    simple: '简化分析',
    detailedInfo: '指标详情',
    radarChart: '雷达图',
    analysisSummary: '总结',
    strength: '良好',
    improvement: '需改进',
    overallAssessment: '总体评价',
    OverallAssessment: {
      excellent: '该地牢设计优秀，各项指标表现良好，能够提供优质的游戏体验。',
      good: '该地牢设计良好，大部分指标达标，稍作调整即可进一步提升。',
      average: '该地牢设计中等，存在一些需要改进的地方，建议重点关注低分指标。',
      poor: '该地牢设计有较大改进空间，建议优先解决关键问题。'
    },
    suggestions: '改进建议',
    suggestionsSummaryOverall: '总体建议',
    noSuggestions: '恭喜！暂无改进建议，地牢设计已经非常优秀！',
    suggestionsSummary: '根据分析结果，该地牢在 {totalCategories} 个方面需要改进。建议优先处理 {highPrioritySuggestions} 个高优先级问题。',
    suggestionsActions: '建议措施：',
    expectedImprovement: '预期效果：'
  },
  forSuggesstions: {
    high: '高',
    medium: '中',
    low: '低',
    dead_end_ratio: {
      title: '减少死胡同设计',
      description: '当前地牢存在过多死胡同，可能导致玩家感到挫败或探索体验单调。',
      expected: '提升探索流畅性，减少玩家挫败感',
      category: '布局优化',
      actions: {
        0: '将部分死胡同连接到其他区域',
        1: '在死胡同末端放置有价值的奖励',
        2: '创建循环路径替代直线通道',
        3: '增加隐藏通道或秘密房间'
      }
    },
    geometric_balance: {
      title: '改善几何平衡',
      description: '房间布局的几何平衡需要改善，建议调整房间大小和位置分布。',
      expected: '改善地牢的视觉平衡性',
      category: '视觉设计',
      actions: {
        0: '调整房间大小和位置分布',
        1: '创建更对称的房间布局',
        2: '平衡不同区域的房间密度',
        3: '优化房间间的空间关系'
      }
    },
    treasure_monster_distribution: {
      title: '优化奖励分布策略',
      description: '宝藏和怪物的分布可能不够合理，影响游戏平衡性和探索动机。',
      actions: {
        0: '确保高价值奖励伴随相应的挑战',
        1: '在探索路径上合理分布小奖励',
        2: '避免奖励过于集中或分散',
        3: '根据地牢深度调整奖励价值'
      },
      expected: '改善宝藏和怪物分布的平衡性',
      category: '游戏平衡'
    },
    accessibility: {
      title: '改善区域连通性',
      description: '部分区域的可达性存在问题，可能导致玩家无法到达某些重要位置。',
      actions: {
        0: '检查并修复断开的连接',
        1: '增加备用路径到达重要区域',
        2: '确保所有房间都可以从入口到达',
        3: '考虑添加快捷通道或传送点'
      },
      expected: '确保完整的探索体验',
      category: '连通性'
    },
    path_diversity: {
      title: '增加路径选择多样性',
      description: '当前地牢的路径选择较为单一，缺乏探索的策略性和趣味性。',
      actions: {
        0: '创建多条通往目标的路径',
        1: '设计分支路径和可选区域',
        2: '增加需要特殊钥匙或技能的路径',
        3: '平衡不同路径的风险和奖励'
      },
      expected: '提升探索策略性和重玩价值',
      category: '探索体验'
    },
    loop_ratio: {
      title: '增加循环路径设计',
      description: '地牢缺乏足够的环路设计，可能导致线性化的探索体验。',
      actions: {
        0: '连接现有的死胡同形成环路',
        1: '设计大型循环区域',
        2: '创建多层次的环路结构',
        3: '确保环路有明确的游戏目的'
      },
      expected: '提升探索流畅性和导航便利性',
      category: '布局优化'
    },
    degree_variance: {
      title: '优化连接度分布',
      description: '房间连接度的变化不够丰富，可能影响地牢的复杂性和探索体验。',
      actions: {
        0: '创建具有不同连接数的房间',
        1: '设计中心枢纽房间',
        2: '平衡简单通道和复杂交叉点',
        3: '确保重要房间有多个入口'
      },
      expected: '增加地牢结构的复杂性和趣味性',
      category: '结构优化'
    }
  }
}

// 英文语言包
const en = {
  // Common
  common: {
    back: 'Back',
    refresh: 'Refresh',
    loading: 'Loading...',
    error: 'Error',
    success: 'Success',
    cancel: 'Cancel',
    confirm: 'Confirm',
    save: 'Save',
    delete: 'Delete',
    edit: 'Edit',
    view: 'View',
    export: 'Export',
    import: 'Import',
    search: 'Search',
    filter: 'Filter',
    sort: 'Sort',
    clear: 'Clear',
    close: 'Close',
    next: 'Next',
    previous: 'Previous',
    submit: 'Submit',
    reset: 'Reset',
    yes: 'Yes',
    no: 'No',
    ok: 'OK',
    actions: 'Actions',
    quickStart: 'Quick Start',
    functionGuide: 'Function Guide',
    faq: 'FAQ',
    coreFeatures: 'Core Features',
    unknown: 'Unknown Duneon',
    noData: 'No Data',
    notAvailable: 'N/A',
    loadingFailed: 'Loading Failed',
    retry: 'Retry',
  },

  // Navigation
  nav: {
    home: 'Home',
    test: 'Test',
    about: 'About',
    help: 'Help',
    detail: 'Detail'
  },

  // App info
  app: {
    title: 'Dungeon Analyzer',
    subtitle: 'Professional D&D Dungeon Quality Assessment Tool',
    description: 'A powerful dungeon quality analysis tool that supports multiple dungeon file formats'
  },

  // Home page
  home: {
    analysisResultsCount: 'Analysised {count} files',
    dragAndDrop: 'Drag and drop files here or click to select files',
    uploadTitle: 'Upload Dungeon Files',
    uploadDescription: 'Drag files here or click to select files',
    supportedFormats: 'Supported formats: JSON, Watabou, Donjon, DungeonDraft',
    selectFiles: 'Select Files',
    uploadedFiles: 'Uploaded files:',
    uploadPrompt: 'Upload files to start analysis',
    analysisConfig: 'Analysis Configuration',
    analysisConfigDescription: 'Configure analysis parameters for better results',
    startAnalysis: 'Start Analysis ({count} files)',
    analyzing: 'Analyzing... ({current}/{total})',
    progress: 'Completed {completed} / {total} files ({percentage}%)',
    clickToAnalyze: 'Click to start batch analysis of all uploaded files',
    pleaseUploadFirst: 'Please upload files first',
    viewAllDetails: 'View All Details',
    viewDetails: 'View Details',
    exportResults: 'Export Results',
    clearResults: 'Clear Results',
    fileNumber: 'File {current} / {total}',
    noFilesToClear: 'No files to clear',
    noResultsToExport: 'No results to export',
    noResultsToClear: 'No results to clear',
    clearFilesConfirm: 'Are you sure you want to clear {count} files?',
    clearResultsConfirm: 'Are you sure you want to clear {count} analysis results?',
    analyzeAll: 'Analyze All Files',
    analysisResults: 'Analysis Results',
    overallScore: 'Overall Score',
    quickActions: 'Quick Actions',
    exportReport: 'Export Report',
    exportAllResults: 'Export All Results',
    clearAll: 'Clear All',
    help: 'Help',
    about: 'About',
    systemStats: 'System Statistics',
    uploadedFilesCount: 'Uploaded Files',
    evaluationMetrics: 'Evaluation Metrics',
    supportedFormatsCount: 'Supported Formats',
    usageTips: 'Usage Tips',
    usageTip1: 'Supports multiple dungeon formats: Watabou, Donjon, DungeonDraft, etc.',
    usageTip2: 'Drag files to upload area or click select files button',
    usageTip3: 'After analysis, you can view detailed visualization results',
    usageTip4: 'Recommended to use Chrome or Firefox browser for best experience',
    helpDescription: 'View detailed usage instructions and tutorials',
    aboutDescription: 'Learn about project information and technical features',
    noFilesToAnalyze: 'No files to analyze',
    exportAllResultsDescription: 'Export {count} results',
    clearAllDescription: 'Clear all files and analysis results',
    viewBatchDetails: 'Batch Details',
    viewBatchDetailsDescription: 'View detailed comparison of {count} dungeons',
    batchTest: 'Batch Test',
    batchTestDescription: 'Batch evaluate multiple dungeon files',
  },

  // Detail page
  detail: {
    sortBy: 'Sort By',
    sortByName: 'Sort By Name',
    sortByScore: 'Sort By Score',
    sortByIndex: 'Sort By Index',
    averageScore: 'Average Score',
    highestScore: 'Highest Score',
    dungeonCount: 'Dungeon Count',
    batchOverview: 'Batch Overview',
    hideOverview: 'Hide Overview',
    showOverview: 'Show Overview',
    exportReport: 'Export Report',
    backButton: 'Back',
    backButtonTitle: 'Back (ESC)',
    refreshButton: 'Refresh',
    scoreFilter: 'Score Filter',
    allScore: 'All Score',
    highScore: 'High Score',
    mediumScore: 'Medium Score',
    lowScore: 'Low Score',
    current: 'Current',
    noMatchDungeon: 'No Match Dungeon',
    tryAdjustFilter: 'Please try adjusting the filter conditions',
    improvementSuggestions: 'Improvement Suggestions',
    metricDetails: 'Metric Details',
    noSuggestions: 'Current design performs excellently, no improvement suggestions',
    noDetailAvailable: 'No detail data available',
    pageInfo: 'Page {current} of {total}',
    noScoreData: 'No scoring data available',
    viewDetailedScores: 'View detailed metric scores',
    scoreInfo: 'Score Information',
    analysisDisabled: 'Analysis parameters disabled',
    overallScoreDisabled: 'Overall score disabled',
    analysisResults: 'Analysis Results',
    dungeonVisualization: 'Dungeon Visualization',
    canvasVisualization: 'Canvas Visualization',
    generatedImage: 'Generated Image',
    noVisualizationData: 'No visualization data available',
    overallScore: 'Overall Score',
    disabled: '(Disabled)',
    homeButton: 'Home',
    singleAnalysis: 'Single Analysis',
    batchAnalysis: 'Batch Analysis ({count} files)',
    next: 'Next',
    first: 'First',
    currentPage: 'Current Page {current} of {total}',
    loadingAnalysisResults: 'Loading analysis results...',
    pleaseWait: 'Please wait',
    backToHome: 'Back to Home',
    
  },

  // Help page

  // About page

  // Test page

  // Error pages
  errors: {
    notFound: 'Page not found',
    pageNotFound: 'Sorry, the page you are looking for does not exist or has been removed.',
    suggestions: 'You might want to visit:',
    serverError: 'Server error',
    networkError: 'Network error',
    fileError: 'File error',
    analysisError: 'Analysis error',
    uploadError: 'Upload error',
    missingFilename: 'Missing filename parameter',
    invalidFile: 'Invalid file format',
    fileTooLarge: 'File too large',
    unsupportedFormat: 'Unsupported file format',
    analysisFailed: 'Analysis failed',
    visualizationFailed: 'Visualization failed'
  },

  // Confirm dialogs
  confirm: {
    deleteFile: 'Are you sure you want to delete this file?',
    clearAllFiles: 'Are you sure you want to clear all files?',
    clearAllResults: 'Are you sure you want to clear all results?',
    clearResults: 'Confirm Clear',
    clearResultsConfirm: 'Are you sure you want to clear {count} analysis results? This action cannot be undone.',
    exportData: 'Are you sure you want to export data?'
  },

  // Metrics
  metrics: {
    accessibility: 'Accessibility',
    geometric_balance: 'Geometric Balance',
    loop_ratio: 'Loop Ratio',
    dead_end_ratio: 'Dead End Ratio',
    key_path_length: 'Key Path Length',
    degree_variance: 'Degree Variance',
    path_diversity: 'Path Diversity',
    door_distribution: 'Door Distribution',
    treasure_monster_distribution: 'Treasure & Monster Distribution'
  },

  // Metric Categories
  metricCategories: {
    layout: 'Layout Design',
    gameplay: 'Gameplay',
    navigation: 'Navigation'
  },

  // Metric Descriptions
  metricDescriptions: {
    accessibility: {
      description: 'Evaluate reachability and connectivity of areas',
      good: 'Players can easily reach all areas',
      poor: 'Some areas are hard to reach, need better path design'
    },
    geometric_balance: {
      description: 'Analyze geometric balance and symmetry of room layout',
      good: 'Room layout has good geometric balance',
      poor: 'Room layout geometric balance needs improvement'
    },
    loop_ratio: {
      description: 'Calculate the ratio of loop structures in dungeon',
      good: 'Loop design is reasonable, avoiding linear experience',
      poor: 'Few loops, may lead to linear experience'
    },
    dead_end_ratio: {
      description: 'Evaluate the ratio of dead ends and invalid paths',
      good: 'Dead end ratio is moderate',
      poor: 'Too many dead ends, affecting exploration experience'
    },
    treasure_monster_distribution: {
      description: 'Analyze the reasonable distribution of treasures and monsters',
      good: 'Treasure and monster distribution is reasonable',
      poor: 'Treasure and monster distribution needs adjustment'
    },
    degree_variance: {
      description: 'Evaluate the distribution of room connectivity',
      good: 'Room connectivity distribution is even',
      poor: 'Room connectivity distribution is uneven'
    },
    door_distribution: {
      description: 'Analyze door distribution and connections',
      good: 'Door distribution is reasonable',
      poor: 'Door distribution needs optimization'
    },
    key_path_length: {
      description: 'Evaluate the length and complexity of key paths',
      good: 'Key path length is moderate',
      poor: 'Key path is too long or too short'
    },
    path_diversity: {
      description: 'Analyze path diversity and choices',
      good: 'Path diversity is good',
      poor: 'Path diversity needs improvement'
    }
  },

  // Metric Selector
  metricSelector: {
    title: 'Evaluation Metrics Selection',
    selectAll: 'Select All',
    deselectAll: 'Deselect All',
    selectedCount: 'Selected {count} / {total} items',
    apply: 'Apply Selection',
    reset: 'Reset',
    disabled: 'Disabled',
    saved: 'Saved'
  },

  // 多详情模态框
  multipleDetailsModal: {
    title: 'Multiple Dungeon Details',
    subtitle: 'Total {count} dungeons',
    summary: 'Batch Statistics',
    totalDungeons: 'Total Dungeons',
    averageScore: 'Average Score',
    excellentCount: 'Excellent Count',
    needsImprovementCount: 'Needs Improvement Count',
    filterByScore: 'Filter by Score',
    allScores: 'All Scores',
    excellentOnly: 'Only Excellent',
    goodOnly: 'Only Good',
    averageOnly: 'Only Average',
    poorOnly: 'Only Poor',
    sortBy: 'Sort By',
    sortByName: 'By Name',
    sortByScore: 'By Score',
    sortByGrade: 'By Grade',
    sortByDate: 'By Date',
    gridView: 'Grid View',
    listView: 'List View',
    exportAll: 'Export All',
    refreshAll: 'Refresh All',
    noResults: 'No results found',
    showOverview: 'Batch Overview',
    hideOverview: 'Hide Overview',
    viewDetail: 'View Detail',
    excellentCountLabel: 'Excellent Dungeons',
    goodCountLabel: 'Good Dungeons',
    averageCountLabel: 'Average Dungeons',
    poorCountLabel: 'Poor Dungeons'
  },

  // Suggestions
  suggestions: {
    deadEndRatio: {
      title: 'Reduce Dead Ends',
      description: 'Current dead end ratio is high, suggest adding loop connections to improve exploration experience.'
    },
    deadEndRatioOptimize: {
      title: 'Optimize Dead End Distribution',
      description: 'Dead end ratio is moderate but has room for optimization. Suggest placing dead ends on secondary paths, keeping main paths clear.'
    },
    geometricBalance: {
      title: 'Improve Geometric Balance',
      description: 'Room layout geometric balance needs improvement, consider adjusting room size and position distribution.'
    },
    treasureMonsterDistribution: {
      title: 'Optimize Treasure and Monster Distribution',
      description: 'Treasure and monster distribution needs adjustment to provide better gameplay experience.'
    },
    treasureMonsterDistributionBalance: {
      title: 'Balance Treasure-Monster Ratio',
      description: 'Treasure and monster distribution is basically reasonable, but can further optimize the ratio to ensure balance between challenge and reward.'
    },
    accessibility: {
      title: 'Improve Accessibility',
      description: 'Some areas are hard to reach, suggest optimizing path design.'
    },
    pathDiversity: {
      title: 'Increase Path Diversity',
      description: 'Path diversity is low, suggest adding different exploration paths.'
    },
    pathDiversityOptimize: {
      title: 'Optimize Path Design',
      description: 'Path diversity is moderate, consider adding some hidden paths or branch routes to increase exploration fun.'
    },
    loopRatio: {
      title: 'Increase Loop Design',
      description: 'Loop ratio is low, suggest adding circular paths to let players return to previous areas, improving map exploration.'
    },
    loopRatioOptimize: {
      title: 'Optimize Loop Distribution',
      description: 'Loop design is basically reasonable, consider adding small loops in key areas to enhance exploration experience.'
    },
    degreeVariance: {
      title: 'Optimize Connectivity Distribution',
      description: 'Room connectivity variance is too large, suggest balancing connection numbers of each room, avoiding some rooms being too isolated or too crowded.'
    },
    doorDistribution: {
      title: 'Improve Door Distribution',
      description: 'Door distribution is not reasonable, suggest appropriately adding doors on key paths and reducing door usage on secondary paths.'
    },
    keyPathLength: {
      title: 'Optimize Key Path Length',
      description: 'Key path is too short or too long, suggest designing moderate key path length that won\'t bore players or be too complex.'
    },
    roomCount: {
      title: 'Increase Room Count',
      description: 'Currently only {count} rooms, suggest increasing to 10-20 rooms to provide richer exploration space.'
    },
    roomCountOptimize: {
      title: 'Streamline Room Design',
      description: 'Room count is high ({count} rooms), suggest merging some functionally similar rooms to avoid over-complexity.'
    },
    corridorDensity: {
      title: 'Increase Connection Corridors',
      description: 'Room connections are few, suggest increasing corridor count to improve room connectivity.'
    },
    corridorDensityOptimize: {
      title: 'Optimize Corridor Design',
      description: 'Too many corridors may make the maze too complex, suggest streamlining some unnecessary corridors.'
    },
    overallScoreRedesign: {
      title: 'Complete Redesign',
      description: 'Overall score is low, suggest redesigning the dungeon from multiple dimensions, focusing on accessibility, path design, and game element distribution.'
    },
    overallScoreOptimize: {
      title: 'Key Optimization',
      description: 'Design is basically reasonable but has room for improvement. Suggest focusing on lower-scored metrics for targeted optimization.'
    },
    overallScoreExcellent: {
      title: 'Maintain Excellent Design',
      description: 'Current design performs excellently! Suggest maintaining this design style as a reference template for other dungeon designs.'
    },
    continuousOptimization: {
      title: 'Continuous Optimization',
      description: 'Current design performs well, suggest continuing to focus on detail optimization such as room decoration and atmosphere creation.'
    }
  },
  scoreLevels: {
    excellent: 'Excellent',
    good: 'Good',
    average: 'Medium',
    poor: 'Poor'
  },
  dungeonVisualizer: {
    title: 'Dungeon Visualizer',
    resetCamera: 'Reset Camera',
    hideGrid: 'Hide Grid',
    showGrid: 'Show Grid',
    hideLabels: 'Hide Labels',
    showLabels: 'Show Labels',
    image: 'Image',
    canvas: 'Canvas',
    download: 'Download',
    viewFullscreen: 'View Fullscreen'
  },
  fullyreport: {
    detailed: 'Detailed',
    suggestions: 'Suggestions',
    simple: 'Simple',
    detailedInfo: 'Detailed Information',
    radarChart: 'Radar Chart',
    analysisSummary: 'Analysis Summary',
    strength: 'Good',
    improvement: 'Poor',
    overallAssessment: 'Overall Assessment',
    OverallAssessment: {
      excellent: 'Excellent Design, all metrics are above 0.7',
      good: 'Good Design, most metrics are above 0.5',
      average: 'Average Design, some metrics are below 0.5',
      poor: 'Poor Design'
    },
    suggestionsSummaryOverall: 'Overall Suggestions',
    suggestionsSummary: 'According to the analysis results, the dungeon needs to be improved in {totalCategories} aspects. It is recommended to prioritize the processing of {highPrioritySuggestions} high-priority issues.',
    suggestionsActions: 'Suggestions Actions:',
    expectedImprovement: 'Expected Improvement:',
    noSuggestions: 'Congratulations! No improvement suggestions, the dungeon design is already excellent!'
  },
  forSuggesstions: {
    high: 'high priority',
    medium: 'medium priority',
    low: 'low priority',
    dead_end_ratio: {
      title: 'Reduce Dead End Design',
      description: 'Current dungeon has too many dead ends, which may cause player frustration or monotonous exploration experience.',
      expected: 'Improve exploration fluency, reduce player frustration',
      category: 'Layout Optimization',
      actions: {
        0: 'Connect some dead ends to other areas',
        1: 'Place valuable rewards at the end of dead ends',
        2: 'Create loop paths to replace linear corridors',
        3: 'Add hidden passages or secret rooms'
      }
    },
    geometric_balance: {
      title: 'Improve Geometric Balance',
      description: 'Room layout geometric balance needs improvement, consider adjusting room size and position distribution.',
      expected: 'Improve the visual balance of the dungeon',
      category: 'Visual Design',
      actions: {
        0: 'Adjust room size and position distribution',
        1: 'Create more symmetrical room layouts',
        2: 'Balance room density in different areas',
        3: 'Optimize spatial relationships between rooms'
      }
    },
    treasure_monster_distribution: {
      title: 'Optimize Reward Distribution Strategy',
      description: 'Treasure and monster distribution may not be reasonable, affecting game balance and exploration motivation.',
      actions: {
        0: 'Ensure high-value rewards come with corresponding challenges',
        1: 'Distribute small rewards reasonably along exploration paths',
        2: 'Avoid rewards being too concentrated or scattered',
        3: 'Adjust reward value based on dungeon depth'
      },
      expected: 'Improve the balance of treasure and monster distribution',
      category: 'Game Balance'
    },
    accessibility: {
      title: 'Improve Area Connectivity',
      description: 'Some areas have accessibility issues, which may prevent players from reaching certain important locations.',
      actions: {
        0: 'Check and fix broken connections',
        1: 'Add backup paths to reach important areas',
        2: 'Ensure all rooms are accessible from the entrance',
        3: 'Consider adding shortcuts or teleportation points'
      },
      expected: 'Ensure complete exploration experience',
      category: 'Connectivity'
    },
    path_diversity: {
      title: 'Increase Path Choice Diversity',
      description: 'Current dungeon path choices are relatively single, lacking strategic and interesting exploration.',
      actions: {
        0: 'Create multiple paths to the target',
        1: 'Design branch paths and optional areas',
        2: 'Add paths requiring special keys or skills',
        3: 'Balance risks and rewards of different paths'
      },
      expected: 'Enhance exploration strategy and replay value',
      category: 'Exploration Experience'
    },
    loop_ratio: {
      title: 'Increase Loop Path Design',
      description: 'Dungeon lacks sufficient loop design, which may lead to linear exploration experience.',
      actions: {
        0: 'Connect existing dead ends to form loops',
        1: 'Design large circular areas',
        2: 'Create multi-level loop structures',
        3: 'Ensure loops have clear gameplay purposes'
      },
      expected: 'Improve exploration fluency and navigation convenience',
      category: 'Layout Optimization'
    },
    degree_variance: {
      title: 'Optimize Connectivity Distribution',
      description: 'Room connectivity variation is not rich enough, which may affect dungeon complexity and exploration experience.',
      actions: {
        0: 'Create rooms with different connection numbers',
        1: 'Design central hub rooms',
        2: 'Balance simple corridors and complex intersections',
        3: 'Ensure important rooms have multiple entrances'
      },
      expected: 'Increase dungeon structure complexity and interest',
      category: 'Structure Optimization'
    }
  }
}

// 创建i18n实例
const i18n = createI18n({
  legacy: false, // 使用Composition API
  locale: 'zh', // 默认语言
  fallbackLocale: 'en', // 回退语言
  messages: {
    zh,
    en
  }
})

export default i18n 