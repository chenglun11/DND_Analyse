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
    quickStart: '快速开始',
    functionGuide: '功能指南',
    faq: '常见问题',
    coreFeatures: '核心功能',
    unknown: '未知地下城',
    noData: '暂无数据'
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
    uploadTitle: '上传地下城文件',
    uploadDescription: '拖拽文件到此处或点击选择文件',
    supportedFormats: '支持格式: JSON, Watabou, Donjon, DungeonDraft',
    selectFiles: '选择文件',
    uploadedFiles: '已上传文件:',
    noFilesToClear: '没有文件需要清除',
    noResultsToExport: '没有结果可以导出',
    noResultsToClear: '没有结果需要清除',
    clearFilesConfirm: '确定要清除 {count} 个文件吗？',
    clearResultsConfirm: '确定要清除 {count} 个分析结果吗？',
    startAnalysis: '开始分析',
    analyzing: '分析中...',
    analysisResults: '分析结果',
    overallScore: '总体评分',
    viewDetails: '查看详情',
    quickActions: '快速操作',
    exportReport: '导出报告',
    exportAllResults: '导出所有结果',
    clearAll: '清空所有',
    help: '使用帮助',
    about: '关于我们',
    systemStats: '系统统计',
    uploadedFilesCount: '已上传文件',
    analysisResultsCount: '分析结果',
    evaluationMetrics: '评估指标',
    supportedFormatsCount: '支持格式',
    usageTips: '使用提示',
    usageTip1: '支持多种地下城格式：Watabou、Donjon、DungeonDraft等',
    usageTip2: '拖拽文件到上传区域或点击选择文件按钮',
    usageTip3: '分析完成后可查看详细的可视化结果',
    usageTip4: '建议使用Chrome或Firefox浏览器获得最佳体验',
    helpDescription: '查看详细的使用说明和教程',
    aboutDescription: '了解项目信息和技术特性',
    noFilesToAnalyze: '没有文件可以分析',
    startAnalysisDescription: '分析 {count} 个文件',
    exportAllResultsDescription: '导出 {count} 个结果',
    clearAllDescription: '清空所有文件和分析结果'
  },

  // 详情页
  detail: {
    backButton: '← 返回',
    backButtonTitle: '返回 (ESC)',
    refreshButton: '🔄 刷新',
    exportReport: '📄 导出报告',
    dungeonVisualization: '地牢可视化',
    canvasVisualization: 'Canvas可视化',
    generatedImage: '生成的可视化图像',
    noVisualizationData: '没有可视化数据',
    analysisResults: '分析结果',
    overallScore: '总体评分',
    detailedMetrics: '详细指标',
    improvementSuggestions: '改进建议',
    noData: '没有数据',
    scoreDescription: {
      excellent: '卓越的地下城设计，具有极佳的游戏体验',
      good: '优秀的地下城设计，具有很好的游戏体验',
      average: '良好的地下城设计，整体表现不错',
      poor: '需要大幅改进的地下城设计'
    }
  },

  // 帮助页
  help: {
    backButton: '← 返回首页',
    title: '使用帮助',
    subtitle: '详细的使用指南和常见问题',
    fileUpload: {
      title: '📁 文件上传',
      content: {
        0: '支持拖拽文件到上传区域',
        1: '支持点击选择文件按钮',
        2: '支持多种JSON格式的地下城文件',
        3: '支持批量上传多个文件',
        4: '支持的文件格式：Watabou、Donjon、DungeonDraft等'
      }
    },
    analysis: {
      title: '📊 分析功能',
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
      title: '💾 数据导出',
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
      },
      treasure_distribution: {
        title: '宝藏分布 (Treasure Distribution)',
        description: '分析宝藏和战利品的分布合理性，确保奖励的公平性。'
      },
      monster_distribution: {
        title: '怪物分布 (Monster Distribution)',
        description: '评估怪物和敌人的分布策略，平衡挑战性和可玩性。'
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
      title: '🎯 项目简介',
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
    treasure_distribution: '宝藏分布',
    monster_distribution: '怪物分布',
    degree_variance: '度方差',
    door_distribution: '门分布',
    key_path_length: '关键路径长度',
    path_diversity: '路径多样性',
    treasure_monster_distribution: '宝藏怪物分布'
  },

  // 指标描述
  metricDescriptions: {
    accessibility: {
      good: '玩家可以轻松到达各个区域',
      poor: '某些区域难以到达，需要改善路径设计'
    },
    geometric_balance: {
      good: '房间布局几何平衡良好',
      poor: '房间布局的几何平衡需要改善'
    },
    loop_ratio: {
      good: '环路设计合理，避免线性体验',
      poor: '环路较少，可能导致线性体验'
    },
    dead_end_ratio: {
      good: '死胡同比例适中',
      poor: '死胡同过多，影响探索体验'
    },
    treasure_monster_distribution: {
      good: '宝藏和怪物分布合理',
      poor: '宝藏和怪物分布需要调整'
    },
    degree_variance: {
      good: '房间连接度分布均匀',
      poor: '房间连接度分布不均匀'
    },
    door_distribution: {
      good: '门分布合理',
      poor: '门分布需要优化'
    },
    key_path_length: {
      good: '关键路径长度适中',
      poor: '关键路径过长或过短'
    },
    path_diversity: {
      good: '路径多样性良好',
      poor: '路径多样性需要改善'
    }
  },

  // 评分等级
  scoreLevels: {
    excellent: '优秀',
    good: '良好',
    average: '一般',
    poor: '较差'
  },

  // 错误信息
  errors: {
    fileUploadFailed: '文件上传失败',
    analysisFailed: '分析失败',
    networkError: '网络错误',
    serverError: '服务器错误',
    unknownError: '未知错误',
    fileNotSupported: '不支持的文件格式',
    fileTooLarge: '文件过大',
    noFilesSelected: '未选择文件',
    missingFilename: '缺少文件名参数',
    exportFailed: '报告导出失败，请重试'
  },

  // 成功信息
  success: {
    fileUploaded: '文件上传成功',
    analysisCompleted: '分析完成',
    dataExported: '数据导出成功',
    settingsSaved: '设置保存成功',
    reportExported: '报告导出成功！'
  },

  // 确认对话框
  confirm: {
    deleteFile: '确定要删除这个文件吗？',
    clearAllFiles: '确定要清除所有文件吗？',
    clearAllResults: '确定要清除所有结果吗？',
    exportData: '确定要导出数据吗？'
  },

  // 改进建议
  suggestions: {
    deadEndRatio: {
      title: '减少死胡同',
      description: '当前死胡同比例较高，建议增加环路连接以提高探索体验。'
    },
    geometricBalance: {
      title: '改善几何平衡',
      description: '房间布局的几何平衡需要改善，考虑调整房间大小和位置分布。'
    },
    treasureMonsterDistribution: {
      title: '优化宝藏和怪物分布',
      description: '宝藏和怪物的分布需要调整，以提供更好的游戏体验。'
    },
    accessibility: {
      title: '改善可达性',
      description: '某些区域难以到达，建议优化路径设计。'
    },
    pathDiversity: {
      title: '增加路径多样性',
      description: '路径多样性较低，建议增加不同的探索路径。'
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
    quickStart: 'Quick Start',
    functionGuide: 'Function Guide',
    faq: 'FAQ',
    coreFeatures: 'Core Features',
    unknown: 'Unknown Dungeon',
    noData: 'No Data'
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
    uploadTitle: 'Upload Dungeon Files',
    uploadDescription: 'Drag files here or click to select files',
    supportedFormats: 'Supported formats: JSON, Watabou, Donjon, DungeonDraft',
    selectFiles: 'Select Files',
    uploadedFiles: 'Uploaded files:',
    noFilesToClear: 'No files to clear',
    noResultsToExport: 'No results to export',
    noResultsToClear: 'No results to clear',
    clearFilesConfirm: 'Are you sure you want to clear {count} files?',
    clearResultsConfirm: 'Are you sure you want to clear {count} analysis results?',
    startAnalysis: 'Start Analysis',
    analyzing: 'Analyzing...',
    analysisResults: 'Analysis Results',
    overallScore: 'Overall Score',
    viewDetails: 'View Details',
    quickActions: 'Quick Actions',
    exportReport: 'Export Report',
    exportAllResults: 'Export All Results',
    clearAll: 'Clear All',
    help: 'Help',
    about: 'About',
    systemStats: 'System Statistics',
    uploadedFilesCount: 'Uploaded Files',
    analysisResultsCount: 'Analysis Results',
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
    startAnalysisDescription: 'Analyze {count} files',
    exportAllResultsDescription: 'Export {count} results',
    clearAllDescription: 'Clear all files and analysis results'
  },

  // Detail page
  detail: {
    backButton: '← Back',
    backButtonTitle: 'Back (ESC)',
    refreshButton: '🔄 Refresh',
    exportReport: '📄 Export Report',
    dungeonVisualization: 'Dungeon Visualization',
    canvasVisualization: 'Canvas Visualization',
    generatedImage: 'Generated Image',
    noVisualizationData: 'No visualization data available',
    improvementSuggestions: 'Improvement Suggestions',
    refreshButtonTitle: 'Refresh data',
    exportReportTitle: 'Export analysis report'
  },

  // Help page
  help: {
    backButton: '← Back to Home',
    title: 'Help & Documentation',
    subtitle: 'Complete user guide and FAQ',
    intro: {
      title: '📚 Help Center',
      description: 'Welcome to the Dungeon Analyzer help center. Here you can find detailed usage instructions, FAQ, and troubleshooting guides.'
    },
    fileUpload: {
      title: '📁 File Upload',
      content: {
        0: 'Support drag and drop files to upload area',
        1: 'Support click select file button',
        2: 'Support multiple JSON format dungeon files',
        3: 'Support batch upload multiple files',
        4: 'Supported formats: Watabou, Donjon, DungeonDraft, etc.'
      }
    },
    analysis: {
      title: '📊 Analysis Features',
      content: {
        0: 'Automatically evaluate dungeon quality',
        1: 'Generate visualization images',
        2: 'Provide detailed analysis reports',
        3: 'Support multiple evaluation metrics',
        4: 'Export analysis results'
      }
    },
    visualization: {
      title: '🎨 Visualization Features',
      content: {
        0: 'Interactive canvas visualization',
        1: 'Generated static images',
        2: 'Room and corridor highlighting',
        3: 'Zoom and pan controls',
        4: 'Export visualization images'
      }
    },
    metrics: {
      title: '📈 Evaluation Metrics',
      content: {
        0: 'Accessibility: Path length and reachability analysis',
        1: 'Geometric Balance: Room distribution and symmetry',
        2: 'Loop Ratio: Circular path analysis',
        3: 'Dead End Ratio: Dead end room analysis',
        4: 'Treasure/Monster Distribution: Game element balance'
      }
    },
    tips: {
      title: '💡 Usage Tips',
      content: {
        0: 'Use supported file formats for best results',
        1: 'Large files may take longer to process',
        2: 'Check browser console for detailed error messages',
        3: 'Refresh page if analysis seems stuck',
        4: 'Export results for offline viewing'
      }
    },
    faq: {
      title: '❓ Frequently Asked Questions',
      questions: {
        q1: 'What file formats are supported?',
        a1: 'Currently supports JSON files from Watabou, Donjon, DungeonDraft, and other compatible formats.',
        q2: 'How long does analysis take?',
        a2: 'Analysis time depends on file size and complexity, typically 1-10 seconds.',
        q3: 'Can I analyze multiple files at once?',
        a3: 'Yes, you can upload and analyze multiple files in batch.',
        q4: 'How accurate are the evaluation metrics?',
        a4: 'Metrics are based on established dungeon design principles and graph theory analysis.',
        q5: 'Can I export my analysis results?',
        a5: 'Yes, you can export detailed reports in JSON format.'
      }
    }
  },

  // About page
  about: {
    backButton: '← Back to Home',
    title: 'About Dungeon Analyzer',
    subtitle: 'Professional D&D Dungeon Quality Assessment Tool',
    description: 'A powerful tool for analyzing and evaluating dungeon designs using advanced algorithms and visualization techniques.',
    features: {
      title: '🚀 Key Features',
      list: {
        0: 'Multi-format dungeon file support',
        1: 'Advanced quality evaluation algorithms',
        2: 'Interactive visualization tools',
        3: 'Comprehensive analysis reports',
        4: 'Batch processing capabilities'
      }
    },
    technology: {
      title: '⚙️ Technology Stack',
      frontend: 'Frontend: Vue.js 3, TypeScript, Vite',
      backend: 'Backend: Python Flask, Graph Theory Algorithms',
      visualization: 'Visualization: Canvas API, SVG',
      analysis: 'Analysis: Custom Quality Metrics, Spatial Analysis'
    },
    metrics: {
      title: '📊 Analysis Metrics',
      accessibility: 'Accessibility: Path analysis and reachability',
      geometric: 'Geometric Balance: Room distribution and symmetry',
      loops: 'Loop Ratio: Circular path detection',
      deadEnds: 'Dead End Ratio: Dead end room analysis',
      distribution: 'Distribution: Treasure and monster placement'
    },
    development: {
      title: '🛠️ Development',
      version: 'Version: 1.0.0',
      license: 'License: MIT',
      repository: 'Repository: GitHub',
      contact: 'Contact: Support available through GitHub Issues'
    }
  },

  // Test page
  test: {
    backButton: '← Back to Home',
    title: 'Test Page',
    subtitle: 'Development and testing features',
    description: 'This page is used for testing new features and debugging.',
    features: {
      title: '🧪 Test Features',
      api: 'API Testing',
      visualization: 'Visualization Testing',
      analysis: 'Analysis Testing',
      performance: 'Performance Testing'
    }
  },

  // Error pages
  errors: {
    notFound: 'Page not found',
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

  // Metrics
  metrics: {
    accessibility: 'Accessibility',
    geometric_balance: 'Geometric Balance',
    loop_ratio: 'Loop Ratio',
    dead_end_ratio: 'Dead End Ratio',
    treasure_distribution: 'Treasure Distribution',
    monster_distribution: 'Monster Distribution',
    key_path_length: 'Key Path Length',
    degree_variance: 'Degree Variance',
    path_diversity: 'Path Diversity',
    door_distribution: 'Door Distribution'
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