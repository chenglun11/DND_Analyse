// API基础URL
const API_BASE_URL = 'http://localhost:5001/api'

export interface AnalysisOptions {
  accessibility?: boolean
  geometric_balance?: boolean
  loop_ratio?: boolean
  dead_end_ratio?: boolean
  treasure_distribution?: boolean
  monster_distribution?: boolean
}

export interface AnalysisResult {
  success: boolean
  result?: any
  error?: string
  filename?: string
  file_id?: string  // 添加文件ID支持
}

export interface BatchAnalysisResult {
  success: boolean
  results?: any[]
  error?: string
}

export interface VisualizationOptions {
  show_connections?: boolean
  show_room_ids?: boolean
  show_grid?: boolean
  show_game_elements?: boolean
}

export interface VisualizationResult {
  success: boolean
  image_data?: string
  visualization_data?: any
  error?: string
  filename?: string
  file_id?: string  // 添加文件ID支持
}

export interface CacheInfo {
  total_files: number
  files: Array<{
    file_id: string
    filename: string
    age_minutes: number
    size_bytes: number
  }>
}

export class DungeonAPI {
  private static async request(endpoint: string, options: RequestInit = {}): Promise<any> {
    const url = `${API_BASE_URL}${endpoint}`
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  static async healthCheck(): Promise<any> {
    return this.request('/health')
  }

  static async getSupportedFormats(): Promise<string[]> {
    const response = await this.request('/supported-formats')
    return response.formats
  }

  static async getAnalysisOptions(): Promise<any> {
    return this.request('/analysis-options')
  }

  // 新的基于内存缓存的API方法
  static async analyzeDungeon(file: File, options: AnalysisOptions = {}): Promise<AnalysisResult> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('options', JSON.stringify(options))

    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  // 通过文件ID分析（新的内存缓存API）
  static async analyzeDungeonById(fileId: string, options: AnalysisOptions = {}): Promise<AnalysisResult> {
    const formData = new FormData()
    formData.append('file_id', fileId)
    formData.append('options', JSON.stringify(options))

    const response = await fetch(`${API_BASE_URL}/analyze-by-id`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  // 通过文件ID获取可视化数据（新的内存缓存API）
  static async getVisualizationDataById(fileId: string): Promise<VisualizationResult> {
    const formData = new FormData()
    formData.append('file_id', fileId)

    const response = await fetch(`${API_BASE_URL}/visualize-data-by-id`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  // 通过文件ID生成可视化图像（新的内存缓存API）
  static async visualizeDungeonById(fileId: string, options: VisualizationOptions = {}): Promise<VisualizationResult> {
    const formData = new FormData()
    formData.append('file_id', fileId)
    formData.append('options', JSON.stringify(options))

    const response = await fetch(`${API_BASE_URL}/visualize-by-id`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  // 获取缓存信息
  static async getCacheInfo(): Promise<CacheInfo> {
    return this.request('/cache-info')
  }

  // 清理缓存
  static async clearCache(): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${API_BASE_URL}/clear-cache`, {
      method: 'POST',
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  // 旧的基于文件名的API方法（保持向后兼容）
  static async analyzeDungeonByFilename(filename: string, options: AnalysisOptions = {}): Promise<AnalysisResult> {
    const formData = new FormData()
    formData.append('filename', filename)
    formData.append('options', JSON.stringify(options))

    const response = await fetch(`${API_BASE_URL}/analyze-by-filename`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  static async analyzeBatch(files: File[], options: AnalysisOptions = {}): Promise<BatchAnalysisResult> {
    const formData = new FormData()
    
    files.forEach(file => {
      formData.append('files', file)
    })
    
    formData.append('options', JSON.stringify(options))

    const response = await fetch(`${API_BASE_URL}/analyze-batch`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  static async convertDungeon(file: File, targetFormat: string = 'unified'): Promise<any> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('target_format', targetFormat)

    const response = await fetch(`${API_BASE_URL}/convert-dungeon`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  static async visualizeDungeon(file: File, options: VisualizationOptions = {}): Promise<VisualizationResult> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('options', JSON.stringify(options))

    const response = await fetch(`${API_BASE_URL}/visualize`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  static async getVisualizationData(file: File): Promise<VisualizationResult> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(`${API_BASE_URL}/visualize-data`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  static async getVisualizationDataByFilename(filename: string): Promise<VisualizationResult> {
    const formData = new FormData()
    formData.append('filename', filename)

    const response = await fetch(`${API_BASE_URL}/visualize-data-by-filename`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  static async visualizeDungeonByFilename(filename: string, options: VisualizationOptions = {}): Promise<VisualizationResult> {
    const formData = new FormData()
    formData.append('filename', filename)
    formData.append('options', JSON.stringify(options))

    const response = await fetch(`${API_BASE_URL}/visualize-by-filename`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  }
} 