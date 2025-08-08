<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { DocumentTextIcon, ArrowLeftIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const { t, locale } = useI18n()

const goBack = () => {
  router.push('/')
}

// 获取当前语言
const getCurrentLanguage = () => {
  return locale.value as 'zh' | 'en'
}

// 多语言schema内容
const schemaContent = {
  title: {
    zh: '统一格式Schema',
    en: 'Unified Format Schema'
  },
  description: {
    zh: 'dnd-dungeon-unified 格式说明',
    en: 'dnd-dungeon-unified Format Documentation'
  },
  overview: {
    zh: [
      '系统使用 "dnd-dungeon-unified" 格式作为分析的标准数据结构',
      '所有上传的文件都会自动转换为这种统一格式后再进行处理',
      '格式包含头部元数据（名称、作者、描述）和关卡数据（房间、走廊、连接）',
      '房间对象包含位置、大小、形状和可选的游戏元素（怪物、宝藏）',
      '连接定义了房间和走廊之间的通道，用于精确的布局分析',
      '这种统一方法确保了不同地牢格式之间一致且可靠的质量评估'
    ],
    en: [
      'System uses the "dnd-dungeon-unified" format as a standard data structure for analysis',
      'All uploaded files are automatically converted to this unified format before processing',
      'The format includes header metadata (name, author, description) and level data (rooms, corridors, connections)',
      'Room objects contain position, size, shape, and optional game elements (monsters, treasures)',
      'Connections define pathways between rooms and corridors for accurate layout analysis',
      'This unified approach ensures consistent and reliable quality assessment across different dungeon formats'
    ]
  },
  keyComponents: {
    title: {
      zh: '关键组件',
      en: 'Key Components'
    },
    items: {
      zh: [
        'header: 包含元数据和网格信息',
        'levels: 包含房间、连接和元素的关卡数据数组',
        'rooms: 具有位置、大小和属性的房间定义',
        'connections: 房间和走廊之间的通道',
        'game_elements: 怪物、宝藏和其他交互对象'
      ],
      en: [
        'header: Contains metadata and grid information',
        'levels: Array of level data with rooms, connections, and elements',
        'rooms: Room definitions with position, size, and properties',
        'connections: Pathways between rooms and corridors',
        'game_elements: Monsters, treasures, and other interactive objects'
      ]
    }
  }
}
</script>

<template>
  <div class="min-h-screen bg-[#f0f8ff]">
    <!-- 页头 -->
    <header class="bg-white shadow-sm border-b border-[#6DAEDB]">
      <div class="max-w-7xl mx-auto px-6 py-4">
        <div class="flex items-center gap-6">
          <button 
            @click="goBack" 
            class="flex items-center gap-2 px-4 py-2 bg-[#f0f8ff] hover:bg-[#e6f3ff] rounded-lg transition-colors duration-200 text-[#173753] font-medium"
          >
            <ArrowLeftIcon class="w-5 h-5" />
            {{ getCurrentLanguage() === 'zh' ? '返回' : 'Back' }}
          </button>
          <h1 class="text-2xl font-bold text-[#173753]">
            {{ schemaContent.title[getCurrentLanguage()] || schemaContent.title.en }}
          </h1>
        </div>
      </div>
    </header>

    <div class="max-w-7xl mx-auto p-6">
      <div class="bg-white rounded-2xl shadow-xl p-8">
        
        <!-- Schema概览 -->
        <section class="mb-12">
          <div class="flex items-center gap-3 mb-6">
            <DocumentTextIcon class="w-8 h-8 text-[#2892D7]" />
            <h2 class="text-2xl font-bold text-gray-800">
              {{ schemaContent.description[getCurrentLanguage()] || schemaContent.description.en }}
            </h2>
          </div>
          <div class="space-y-4 text-gray-700 leading-relaxed">
            <div 
              v-for="(item, index) in schemaContent.overview[getCurrentLanguage()] || schemaContent.overview.en" 
              :key="index"
              class="flex items-start gap-3"
            >
              <div class="w-2 h-2 bg-[#2892D7] rounded-full mt-2 flex-shrink-0"></div>
              <span>{{ item }}</span>
            </div>
          </div>
        </section>

        <!-- Schema示例 -->
        <section class="mb-12">
          <div class="flex items-center gap-3 mb-6">
            <DocumentTextIcon class="w-8 h-8 text-[#2892D7]" />
            <h2 class="text-2xl font-bold text-gray-800">
              {{ getCurrentLanguage() === 'zh' ? '格式示例' : 'Format Example' }}
            </h2>
          </div>
          <div class="bg-gray-900 rounded-lg p-6 text-gray-100">
            <pre class="text-sm overflow-x-auto"><code>{
  "header": {
    "schemaName": "dnd-dungeon-unified",
    "schemaVersion": "1.0.0",
    "name": "Example Dungeon",
    "author": "System Converter",
    "description": "A converted dungeon layout",
    "grid": {
      "type": "square",
      "size": 5,
      "unit": "ft"
    }
  },
  "levels": [
    {
      "id": "level_1",
      "name": "Main Level",
      "map": { "width": 50, "height": 40 },
      "rooms": [
        {
          "id": "room_1",
          "shape": "rectangle",
          "position": { "x": 0, "y": 0 },
          "size": { "width": 10, "height": 8 },
          "name": "Entrance Hall",
          "description": "A large entrance chamber",
          "is_entrance": true,
          "monsters": [],
          "treasures": []
        }
      ],
      "corridors": [],
      "connections": [
        {
          "id": "conn_1",
          "from_room": "room_1",
          "to_room": "room_2",
          "door_type": "normal"
        }
      ],
      "doors": [],
      "game_elements": []
    }
  ]
}</code></pre>
          </div>
          
          <!-- 关键组件说明 -->
          <div class="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h4 class="text-lg font-semibold text-blue-800 mb-2">
              {{ schemaContent.keyComponents.title[getCurrentLanguage()] || schemaContent.keyComponents.title.en }}
            </h4>
            <ul class="space-y-2 text-blue-700">
              <li 
                v-for="(item, index) in schemaContent.keyComponents.items[getCurrentLanguage()] || schemaContent.keyComponents.items.en" 
                :key="index"
                class="flex items-start gap-2"
              >
                <span class="text-blue-500 font-bold">•</span>
                <span>{{ item }}</span>
              </li>
            </ul>
          </div>
        </section>

      </div>
    </div>

    <!-- 页脚 -->
    <footer class="bg-white border-t border-[#6DAEDB] mt-12">
      <div class="max-w-7xl mx-auto px-6 py-4">
        <p class="text-center text-gray-500 text-sm">
          &copy; 2024 {{ getCurrentLanguage() === 'zh' ? '地下城适配器' : 'Dungeon Adapter' }}
        </p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* 响应式设计 */
@media (max-width: 768px) {
  .max-w-7xl {
    @apply px-4;
  }
  
  .p-6 {
    @apply p-4;
  }
  
  .p-8 {
    @apply p-4;
  }
  
  .text-2xl {
    @apply text-xl;
  }
  
  .gap-6 {
    @apply gap-4;
  }
}

/* 代码块样式优化 */
pre {
  white-space: pre-wrap;
  word-wrap: break-word;
}

@media (max-width: 640px) {
  pre {
    font-size: 0.75rem;
  }
}
</style> 