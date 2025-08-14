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
    zh: '统一格式Schema详解',
    en: 'Unified Format Schema Documentation'
  },
  description: {
    zh: 'dnd-dungeon-unified 格式完整结构说明',
    en: 'dnd-dungeon-unified Format Complete Structure Guide'
  },
  overview: {
    zh: [
      '统一格式是所有地牢文件转换后的标准数据结构，确保分析的一致性',
      '格式分为两个主要部分：header（头部信息）和 levels（关卡数据）',
      'header 包含地牢的基本信息：名称、作者、描述和网格设置',
      'levels 是数组结构，每个level代表地牢的一层，包含房间、连接和游戏元素',
      '所有空间坐标使用统一的网格系统，便于精确的布局分析和质量评估'
    ],
    en: [
      'Unified format is the standard data structure after all dungeon files are converted, ensuring analysis consistency',
      'Format consists of two main parts: header (metadata) and levels (level data)',
      'header contains basic dungeon information: name, author, description, and grid settings',
      'levels is an array structure, each level represents a dungeon floor with rooms, connections, and game elements',
      'All spatial coordinates use a unified grid system for precise layout analysis and quality assessment'
    ]
  },
  schemaStructure: {
    title: {
      zh: 'Schema结构详解',
      en: 'Schema Structure Details'
    },
    components: {
      zh: [
        {
          name: 'header',
          type: 'Object',
          description: '地牢元数据信息',
          contains: [
            'schemaName: 格式标识符，固定为 "dnd-dungeon-unified"',
            'schemaVersion: 版本号，当前为 "1.0.0"',
            'name: 地牢名称，字符串类型',
            'author: 作者信息，通常包含原作者和转换器信息',
            'description: 地牢描述，可以为空',
            'grid: 网格设置对象，包含type（网格类型）、size（格子大小）、unit（单位）'
          ]
        },
        {
          name: 'levels',
          type: 'Array<Object>',
          description: '关卡数据数组，每个元素代表一层',
          contains: [
            'id: 关卡唯一标识符',
            'name: 关卡名称',
            'map: 地图尺寸信息，包含width和height',
            'rooms: 房间数组，每个房间有id、形状、位置、大小、名称、描述',
            'corridors: 走廊数组（可选），结构类似房间',
            'connections: 连接数组，定义房间/走廊间的通道关系',
            'doors: 门数组（可选），包含位置、类型、方向信息',
            'game_elements: 游戏元素数组（可选），包含怪物、宝藏、机关等'
          ]
        }
      ],
      en: [
        {
          name: 'header',
          type: 'Object',
          description: 'Dungeon metadata information',
          contains: [
            'schemaName: Format identifier, fixed as "dnd-dungeon-unified"',
            'schemaVersion: Version number, currently "1.0.0"',
            'name: Dungeon name, string type',
            'author: Author information, usually includes original author and converter info',
            'description: Dungeon description, can be empty',
            'grid: Grid settings object, contains type (grid type), size (cell size), unit (measurement unit)'
          ]
        },
        {
          name: 'levels',
          type: 'Array<Object>',
          description: 'Level data array, each element represents one floor',
          contains: [
            'id: Unique level identifier',
            'name: Level name',
            'map: Map size information, contains width and height',
            'rooms: Room array, each room has id, shape, position, size, name, description',
            'corridors: Corridor array (optional), similar structure to rooms',
            'connections: Connection array, defines passage relationships between rooms/corridors',
            'doors: Door array (optional), contains position, type, direction information',
            'game_elements: Game element array (optional), includes monsters, treasures, mechanisms, etc.'
          ]
        }
      ]
    }
  },
  detailedFields: {
    title: {
      zh: '字段详细说明',
      en: 'Detailed Field Descriptions'
    },
    rooms: {
      title: {
        zh: 'rooms 房间对象',
        en: 'rooms Room Objects'
      },
      fields: {
        zh: [
          'id: 房间唯一标识符，字符串类型，如 "room_1", "rect_0"',
          'shape: 房间形状，通常为 "rectangle" 或 "circle"',
          'position: 位置对象 {x, y}，表示房间左上角坐标',
          'size: 尺寸对象 {width, height}，表示房间的宽度和高度',
          'name: 房间名称，用于显示和标识',
          'description: 房间描述，包含房间内容和特征',
          'is_entrance: 布尔值（可选），标记是否为入口房间',
          'is_exit: 布尔值（可选），标记是否为出口房间'
        ],
        en: [
          'id: Unique room identifier, string type, like "room_1", "rect_0"',
          'shape: Room shape, usually "rectangle" or "circle"',
          'position: Position object {x, y}, represents top-left corner coordinates',
          'size: Size object {width, height}, represents room width and height',
          'name: Room name, used for display and identification',
          'description: Room description, contains room contents and features',
          'is_entrance: Boolean (optional), marks if this is an entrance room',
          'is_exit: Boolean (optional), marks if this is an exit room'
        ]
      }
    },
    connections: {
      title: {
        zh: 'connections 连接对象',
        en: 'connections Connection Objects'
      },
      fields: {
        zh: [
          'id: 连接唯一标识符，字符串类型',
          'from_room: 起始房间/走廊的id',
          'to_room: 目标房间/走廊的id',
          'door_type: 门的类型（可选），如 "normal", "secret", "locked"',
          'door_id: 关联的门对象id（可选）',
          'bidirectional: 布尔值（可选），表示是否为双向连接，默认为true'
        ],
        en: [
          'id: Unique connection identifier, string type',
          'from_room: Source room/corridor id',
          'to_room: Target room/corridor id',
          'door_type: Door type (optional), like "normal", "secret", "locked"',
          'door_id: Associated door object id (optional)',
          'bidirectional: Boolean (optional), indicates if bidirectional, default true'
        ]
      }
    },
    gameElements: {
      title: {
        zh: 'game_elements 游戏元素',
        en: 'game_elements Game Elements'
      },
      fields: {
        zh: [
          'id: 元素唯一标识符',
          'name: 元素名称，如 "Treasure", "Monster", "Trap"',
          'type: 元素类型，如 "treasure", "monster", "trap", "npc", "mechanism"',
          'position: 位置对象 {x, y}，元素在地图上的坐标',
          'description: 元素描述，详细说明元素的特征和作用',
          'ref: 原始引用标识符（可选），用于追溯原始数据',
          'properties: 扩展属性对象（可选），存储特定于元素类型的额外信息'
        ],
        en: [
          'id: Unique element identifier',
          'name: Element name, like "Treasure", "Monster", "Trap"',
          'type: Element type, like "treasure", "monster", "trap", "npc", "mechanism"',
          'position: Position object {x, y}, element coordinates on the map',
          'description: Element description, detailed explanation of features and function',
          'ref: Original reference identifier (optional), for tracing original data',
          'properties: Extended properties object (optional), stores additional type-specific information'
        ]
      }
    }
  },
  refField: {
    title: {
      zh: 'ref字段详解',
      en: 'ref Field Explanation'
    },
    description: {
      zh: 'ref字段是Watabou格式中重要的标识符，用于标记和引用地图上的特定兴趣点：',
      en: 'The ref field is an important identifier in Watabou format, used to mark and reference specific points of interest on the map:'
    },
    features: {
      zh: [
        '唯一标识符：每个note都有一个唯一的ref值（如"1", "2", "3"等）',
        '地图标记：在视觉地图上显示为数字标记，帮助玩家定位',
        '内容关联：ref将地图位置与具体的描述文本关联起来',
        '游戏元素：转换后的game_elements保留原始ref，便于追溯',
        '房间命名：有notes的房间会使用ref来生成房间名称（如"room_1"）'
      ],
      en: [
        'Unique Identifier: Each note has a unique ref value (like "1", "2", "3", etc.)',
        'Map Markers: Displayed as numbered markers on visual maps to help players navigate',
        'Content Association: ref links map positions with specific descriptive text',
        'Game Elements: Converted game_elements retain original ref for traceability',
        'Room Naming: Rooms with notes use ref to generate room names (like "room_1")'
      ]
    },
    example: {
      zh: {
        title: 'ref字段使用示例',
        original: '原始Watabou数据',
        converted: '转换后的统一格式'
      },
      en: {
        title: 'ref Field Usage Example',
        original: 'Original Watabou Data',
        converted: 'Converted Unified Format'
      }
    }
  },
  doorTypes: {
    title: {
      zh: 'Watabou门类型定义',
      en: 'Watabou Door Type Definitions'
    },
    description: {
      zh: '在Watabou地牢生成器中，每个门都有一个type字段，表示门的类型和功能：',
      en: 'In Watabou dungeon generator, each door has a type field indicating the door\'s type and function:'
    },
    types: {
      zh: [
        { type: '0', name: 'EMPTY/OPENING', desc: '空口/开放通道 - 没有实际的门，只是一个开口', usage: '最常见，用于房间间的基本通道' },
        { type: '1', name: 'NORMAL', desc: '普通门 - 标准的木门或石门', usage: '很常见，标准的房间入口' },
        { type: '2', name: 'ARCHWAY', desc: '拱门 - 装饰性的拱形入口', usage: '中等频率，用于重要房间' },
        { type: '3', name: 'STAIRS', desc: '楼梯 - 连接不同楼层的楼梯', usage: '用于多层地牢的垂直连接' },
        { type: '4', name: 'PORTCULLIS', desc: '闸门 - 可升降的栅格门', usage: '防御性结构，可能需要机关操作' },
        { type: '5', name: 'SPECIAL', desc: '特殊门 - 具有特殊功能或外观', usage: '用于重要或独特的位置' },
        { type: '6', name: 'SECRET', desc: '秘密门 - 隐藏的入口', usage: '连接秘密房间，需要特殊方式发现' },
        { type: '7', name: 'BARRED', desc: '封闭门 - 被栅栏或障碍物阻挡', usage: '极少使用，表示被封锁的通道' },
        { type: '8', name: 'UNKNOWN_8', desc: '未知类型8 - 可能是保留类型', usage: '极少使用，功能未明确定义' },
        { type: '9', name: 'UNKNOWN_9', desc: '未知类型9 - 可能是保留类型', usage: '少见使用，功能未明确定义' }
      ],
      en: [
        { type: '0', name: 'EMPTY/OPENING', desc: 'Empty/Opening - No actual door, just an opening', usage: 'Most common, basic passages between rooms' },
        { type: '1', name: 'NORMAL', desc: 'Normal Door - Standard wooden or stone door', usage: 'Very common, standard room entrances' },
        { type: '2', name: 'ARCHWAY', desc: 'Archway - Decorative arched entrance', usage: 'Medium frequency, for important rooms' },
        { type: '3', name: 'STAIRS', desc: 'Stairs - Connecting different levels', usage: 'For vertical connections in multi-level dungeons' },
        { type: '4', name: 'PORTCULLIS', desc: 'Portcullis - Raiseable grated gate', usage: 'Defensive structure, may need mechanism operation' },
        { type: '5', name: 'SPECIAL', desc: 'Special Door - With special function or appearance', usage: 'For important or unique locations' },
        { type: '6', name: 'SECRET', desc: 'Secret Door - Hidden entrance', usage: 'Connects secret rooms, needs special discovery' },
        { type: '7', name: 'BARRED', desc: 'Barred Door - Blocked by bars or obstacles', usage: 'Rarely used, represents blocked passages' },
        { type: '8', name: 'UNKNOWN_8', desc: 'Unknown Type 8 - Possibly reserved type', usage: 'Rarely used, function not clearly defined' },
        { type: '9', name: 'UNKNOWN_9', desc: 'Unknown Type 9 - Possibly reserved type', usage: 'Occasionally used, function not clearly defined' }
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

        <!-- Schema结构详解 -->
        <section class="mb-12">
          <div class="flex items-center gap-3 mb-6">
            <DocumentTextIcon class="w-8 h-8 text-[#2892D7]" />
            <h2 class="text-2xl font-bold text-gray-800">
              {{ schemaContent.schemaStructure.title[getCurrentLanguage()] || schemaContent.schemaStructure.title.en }}
            </h2>
          </div>
          
          <div class="space-y-6">
            <div 
              v-for="component in schemaContent.schemaStructure.components[getCurrentLanguage()] || schemaContent.schemaStructure.components.en"
              :key="component.name"
              class="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow duration-200"
            >
              <div class="flex items-center gap-3 mb-4">
                <div class="bg-gradient-to-r from-[#2892D7] to-[#6DAEDB] text-white px-3 py-1 rounded-md font-mono text-sm">
                  {{ component.name }}
                </div>
                <span class="text-gray-500 text-sm font-mono">{{ component.type }}</span>
              </div>
              
              <p class="text-gray-700 mb-4">{{ component.description }}</p>
              
              <div class="space-y-2">
                <h4 class="font-semibold text-gray-800">
                  {{ getCurrentLanguage() === 'zh' ? '包含字段：' : 'Contains:' }}
                </h4>
                <ul class="space-y-2">
                  <li 
                    v-for="field in component.contains"
                    :key="field"
                    class="flex items-start gap-2 text-sm text-gray-600"
                  >
                    <span class="text-[#2892D7] font-bold mt-1">•</span>
                    <span class="font-mono">{{ field }}</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        <!-- 字段详细说明 -->
        <section class="mb-12">
          <div class="flex items-center gap-3 mb-6">
            <DocumentTextIcon class="w-8 h-8 text-[#2892D7]" />
            <h2 class="text-2xl font-bold text-gray-800">
              {{ schemaContent.detailedFields.title[getCurrentLanguage()] || schemaContent.detailedFields.title.en }}
            </h2>
          </div>

          <!-- Rooms 详解 -->
          <div class="mb-8">
            <h3 class="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
              <span class="bg-green-100 text-green-800 px-2 py-1 rounded text-sm font-mono">rooms</span>
              {{ schemaContent.detailedFields.rooms.title[getCurrentLanguage()] || schemaContent.detailedFields.rooms.title.en }}
            </h3>
            <div class="bg-green-50 border border-green-200 rounded-lg p-4">
              <ul class="space-y-2">
                <li 
                  v-for="field in schemaContent.detailedFields.rooms.fields[getCurrentLanguage()] || schemaContent.detailedFields.rooms.fields.en"
                  :key="field"
                  class="flex items-start gap-2 text-sm text-green-800"
                >
                  <span class="text-green-600 font-bold mt-1">▸</span>
                  <span class="font-mono">{{ field }}</span>
                </li>
              </ul>
            </div>
          </div>

          <!-- Connections 详解 -->
          <div class="mb-8">
            <h3 class="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
              <span class="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm font-mono">connections</span>
              {{ schemaContent.detailedFields.connections.title[getCurrentLanguage()] || schemaContent.detailedFields.connections.title.en }}
            </h3>
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <ul class="space-y-2">
                <li 
                  v-for="field in schemaContent.detailedFields.connections.fields[getCurrentLanguage()] || schemaContent.detailedFields.connections.fields.en"
                  :key="field"
                  class="flex items-start gap-2 text-sm text-blue-800"
                >
                  <span class="text-blue-600 font-bold mt-1">▸</span>
                  <span class="font-mono">{{ field }}</span>
                </li>
              </ul>
            </div>
          </div>

          <!-- Game Elements 详解 -->
          <div class="mb-8">
            <h3 class="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
              <span class="bg-purple-100 text-purple-800 px-2 py-1 rounded text-sm font-mono">game_elements</span>
              {{ schemaContent.detailedFields.gameElements.title[getCurrentLanguage()] || schemaContent.detailedFields.gameElements.title.en }}
            </h3>
            <div class="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <ul class="space-y-2">
                <li 
                  v-for="field in schemaContent.detailedFields.gameElements.fields[getCurrentLanguage()] || schemaContent.detailedFields.gameElements.fields.en"
                  :key="field"
                  class="flex items-start gap-2 text-sm text-purple-800"
                >
                  <span class="text-purple-600 font-bold mt-1">▸</span>
                  <span class="font-mono">{{ field }}</span>
                </li>
              </ul>
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
    "name": "Spiral Orbit of the Stars",
    "author": "Colin Lawler (converted by System Converter)",
    "description": "A spiral stair descends to a Zodiac orrery",
    "grid": { "type": "square", "size": 10, "unit": "ft" }
  },
  "levels": [
    {
      "id": "level_1",
      "name": "Main Level",
      "map": { "width": 60, "height": 60 },
      "rooms": [
        {
          "id": "room_surface_entry",
          "shape": "rectangle",
          "position": { "x": 6, "y": 6 },
          "size": { "width": 10, "height": 8 },
          "name": "Surface Entry", 
          "description": "Iron disk with constellations...",
          "is_entrance": true
        },
        {
          "id": "room_center", 
          "shape": "circle",
          "position": { "x": 32, "y": 28 },
          "size": { "width": 16, "height": 16 },
          "name": "Center Orrery",
          "description": "8 crystalline planets and a luminous sun..."
        },
        {
          "id": "room_island",
          "shape": "rectangle", 
          "position": { "x": 54, "y": 8 },
          "size": { "width": 12, "height": 8 },
          "name": "Island (Infinite Ocean)",
          "description": "Rocky isle in an endless sea...",
          "is_exit": true
        }
      ],
      "connections": [
        {
          "id": "so_01",
          "from_room": "room_surface_entry", 
          "to_room": "room_study",
          "door_type": "normal"
        },
        {
          "id": "so_02",
          "from_room": "room_study",
          "to_room": "room_center", 
          "door_type": "normal"
        }
      ],
      "doors": [
        {
          "id": "door_01",
          "between": {
            "from_room": "room_surface_entry",
            "to_room": "room_study"
          },
          "type": "normal",
          "notes": "standard door"
        }
      ],
      "game_elements": [
        {
          "id": "treasure_6",
          "name": "Gear", 
          "type": "treasure",
          "position": { "x": 46, "y": 20 },
          "description": "Repairs the Orrery crank",
          "ref": "6"
        },
        {
          "id": "boss_5",
          "name": "Sun Lion",
          "type": "boss", 
          "position": { "x": 46, "y": 20 },
          "description": "Guardian of knowledge; sleeping"
        },
        {
          "id": "mechanism_0", 
          "name": "Spiral Stairs",
          "type": "mechanism",
          "position": { "x": 8, "y": 8 },
          "description": "Connects surface entry to main level"
        }
      ]
    }
  ]
}</code></pre>
          </div>
          
          <!-- 示例说明 -->
          <div class="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h4 class="text-lg font-semibold text-blue-800 mb-3">
              {{ getCurrentLanguage() === 'zh' ? '示例说明' : 'Example Explanation' }}
            </h4>
            <div class="space-y-3 text-blue-700 text-sm">
              <div class="flex items-start gap-2">
                <span class="bg-blue-200 text-blue-800 px-2 py-0.5 rounded text-xs font-mono mt-0.5">header</span>
                <span>{{ getCurrentLanguage() === 'zh' 
                  ? '包含地牢基本信息，grid设置定义了10ft方格网格系统' 
                  : 'Contains basic dungeon info, grid setting defines 10ft square grid system' 
                }}</span>
              </div>
              <div class="flex items-start gap-2">
                <span class="bg-green-200 text-green-800 px-2 py-0.5 rounded text-xs font-mono mt-0.5">rooms</span>
                <span>{{ getCurrentLanguage() === 'zh' 
                  ? '3个房间示例：入口（标记entrance）、中心房间（圆形）、出口（标记exit）' 
                  : '3 room examples: entrance (marked entrance), center room (circular), exit (marked exit)' 
                }}</span>
              </div>
              <div class="flex items-start gap-2">
                <span class="bg-blue-200 text-blue-800 px-2 py-0.5 rounded text-xs font-mono mt-0.5">connections</span>
                <span>{{ getCurrentLanguage() === 'zh' 
                  ? '定义房间间的通道关系，支持双向连接' 
                  : 'Defines passage relationships between rooms, supports bidirectional connections' 
                }}</span>
              </div>
              <div class="flex items-start gap-2">
                <span class="bg-purple-200 text-purple-800 px-2 py-0.5 rounded text-xs font-mono mt-0.5">game_elements</span>
                <span>{{ getCurrentLanguage() === 'zh' 
                  ? '包含3种类型元素：宝藏（Gear）、Boss（Sun Lion）、机关（楼梯）' 
                  : 'Contains 3 element types: treasure (Gear), boss (Sun Lion), mechanism (Stairs)' 
                }}</span>
              </div>
            </div>
          </div>
        </section>

        <!-- ref字段详解 -->
        <section class="mb-12">
          <div class="flex items-center gap-3 mb-6">
            <DocumentTextIcon class="w-8 h-8 text-[#2892D7]" />
            <h2 class="text-2xl font-bold text-gray-800">
              {{ schemaContent.refField.title[getCurrentLanguage()] || schemaContent.refField.title.en }}
            </h2>
          </div>
          
          <div class="mb-6">
            <p class="text-gray-700 leading-relaxed">
              {{ schemaContent.refField.description[getCurrentLanguage()] || schemaContent.refField.description.en }}
            </p>
          </div>

          <div class="grid gap-4 mb-6">
            <div 
              v-for="(feature, index) in schemaContent.refField.features[getCurrentLanguage()] || schemaContent.refField.features.en"
              :key="index"
              class="flex items-start gap-3 p-3 bg-green-50 border border-green-200 rounded-lg"
            >
              <div class="w-6 h-6 bg-green-500 text-white rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0 mt-0.5">
                {{ index + 1 }}
              </div>
              <span class="text-green-800">{{ feature }}</span>
            </div>
          </div>

          <!-- ref字段示例 -->
          <div class="bg-gray-50 border border-gray-200 rounded-lg p-6">
            <h4 class="text-lg font-semibold text-gray-800 mb-4">
              {{ (schemaContent.refField.example[getCurrentLanguage()] || schemaContent.refField.example.en).title }}
            </h4>
            
            <div class="grid lg:grid-cols-2 gap-6">
              <!-- 原始数据 -->
              <div>
                <h5 class="font-medium text-gray-700 mb-3">
                  {{ (schemaContent.refField.example[getCurrentLanguage()] || schemaContent.refField.example.en).original }}
                </h5>
                <div class="bg-gray-900 rounded-lg p-4 text-gray-100">
                  <pre class="text-sm overflow-x-auto"><code>{
  "notes": [
    {
      "text": "A rear entrance into the palace.",
      "ref": "1",
      "pos": { "x": 0.5, "y": -1.5 }
    },
    {
      "text": "A basket holds gold and hammer.",
      "ref": "8", 
      "pos": { "x": 19.5, "y": -5.5 }
    }
  ]
}</code></pre>
                </div>
              </div>

              <!-- 转换后数据 -->
              <div>
                <h5 class="font-medium text-gray-700 mb-3">
                  {{ (schemaContent.refField.example[getCurrentLanguage()] || schemaContent.refField.example.en).converted }}
                </h5>
                <div class="bg-gray-900 rounded-lg p-4 text-gray-100">
                  <pre class="text-sm overflow-x-auto"><code>{
  "rooms": [
    {
      "id": "rect_0",
      "name": "room_1",
      "description": "A rear entrance..."
    }
  ],
  "game_elements": [
    {
      "id": "special_0",
      "name": "Gate",
      "type": "special",
      "description": "A rear entrance...",
      "ref": "1"
    },
    {
      "id": "treasure_3", 
      "name": "Treasure",
      "type": "treasure",
      "description": "A basket holds gold...",
      "ref": "8"
    }
  ]
}</code></pre>
                </div>
              </div>
            </div>
          </div>

          <!-- ref字段重要提示 -->
          <div class="mt-6 p-4 bg-purple-50 border border-purple-200 rounded-lg">
            <h4 class="text-lg font-semibold text-purple-800 mb-2">
              {{ getCurrentLanguage() === 'zh' ? '重要提示' : 'Important Notes' }}
            </h4>
            <div class="text-purple-700 space-y-2 text-sm">
              <div class="flex items-start gap-2">
                <span class="text-purple-500 font-bold mt-0.5">•</span>
                <span>{{ getCurrentLanguage() === 'zh' 
                  ? 'ref字段在转换过程中会保留，确保原始数据的可追溯性' 
                  : 'ref field is preserved during conversion, ensuring traceability of original data' 
                }}</span>
              </div>
              <div class="flex items-start gap-2">
                <span class="text-purple-500 font-bold mt-0.5">•</span>
                <span>{{ getCurrentLanguage() === 'zh' 
                  ? '地图标记数字与ref值一一对应，方便玩家查找具体位置' 
                  : 'Map marker numbers correspond one-to-one with ref values, making it easy for players to find specific locations' 
                }}</span>
              </div>
              <div class="flex items-start gap-2">
                <span class="text-purple-500 font-bold mt-0.5">•</span>
                <span>{{ getCurrentLanguage() === 'zh' 
                  ? 'ref字段是字符串类型，通常是数字，但也可能包含字母' 
                  : 'ref field is string type, usually numeric, but may contain letters' 
                }}</span>
              </div>
            </div>
          </div>
        </section>

        <!-- 门类型详解 -->
        <section class="mb-12">
          <div class="flex items-center gap-3 mb-6">
            <DocumentTextIcon class="w-8 h-8 text-[#2892D7]" />
            <h2 class="text-2xl font-bold text-gray-800">
              {{ schemaContent.doorTypes.title[getCurrentLanguage()] || schemaContent.doorTypes.title.en }}
            </h2>
          </div>
          
          <div class="mb-6">
            <p class="text-gray-700 leading-relaxed">
              {{ schemaContent.doorTypes.description[getCurrentLanguage()] || schemaContent.doorTypes.description.en }}
            </p>
          </div>

          <div class="grid gap-4">
            <div 
              v-for="doorType in schemaContent.doorTypes.types[getCurrentLanguage()] || schemaContent.doorTypes.types.en"
              :key="doorType.type"
              class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow duration-200"
            >
              <div class="flex items-start gap-4">
                <div class="flex-shrink-0">
                  <div class="w-12 h-12 bg-gradient-to-br from-[#2892D7] to-[#6DAEDB] rounded-lg flex items-center justify-center text-white font-bold text-lg">
                    {{ doorType.type }}
                  </div>
                </div>
                <div class="flex-1">
                  <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-2">
                    <h4 class="text-lg font-semibold text-gray-800">{{ doorType.name }}</h4>
                    <span class="text-sm bg-gray-100 text-gray-600 px-2 py-1 rounded-md w-fit">
                      {{ getCurrentLanguage() === 'zh' ? '类型' : 'Type' }} {{ doorType.type }}
                    </span>
                  </div>
                  <p class="text-gray-700 mb-2">{{ doorType.desc }}</p>
                  <div class="text-sm text-blue-600 bg-blue-50 px-3 py-1 rounded-md inline-block">
                    <strong>{{ getCurrentLanguage() === 'zh' ? '用途：' : 'Usage: ' }}</strong>{{ doorType.usage }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 门类型统计说明 -->
          <div class="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <h4 class="text-lg font-semibold text-yellow-800 mb-2">
              {{ getCurrentLanguage() === 'zh' ? '使用频率统计' : 'Usage Frequency Statistics' }}
            </h4>
            <div class="text-yellow-700 space-y-2">
              <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 text-sm">
                <div>{{ getCurrentLanguage() === 'zh' ? '高频：类型 0, 1' : 'High: Types 0, 1' }}</div>
                <div>{{ getCurrentLanguage() === 'zh' ? '中频：类型 2, 3, 6, 9' : 'Medium: Types 2, 3, 6, 9' }}</div>
                <div>{{ getCurrentLanguage() === 'zh' ? '低频：类型 4, 5, 7, 8' : 'Low: Types 4, 5, 7, 8' }}</div>
              </div>
              <p class="text-sm mt-3">
                {{ getCurrentLanguage() === 'zh' 
                  ? '基于实际样本数据分析，Type 0（空口）和Type 1（普通门）占总数的70%以上' 
                  : 'Based on actual sample data analysis, Type 0 (Empty) and Type 1 (Normal) account for over 70% of all doors' 
                }}
              </p>
            </div>
          </div>
        </section>

      </div>
    </div>
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