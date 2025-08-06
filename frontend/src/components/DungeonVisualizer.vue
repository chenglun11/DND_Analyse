<template>
  <div class="dungeon-visualizer">
    <div class="controls">
      <button @click="resetCamera" class="control-btn">{{t('dungeonVisualizer.resetCamera') }}</button>
      <button @click="toggleGrid" class="control-btn">{{t('dungeonVisualizer.hideGrid') }}</button>
      <button @click="toggleLabels" class="control-btn">{{t('dungeonVisualizer.hideLabels') }}</button>
      <div class="zoom-controls">
        <button @click="zoomIn" class="zoom-btn">+</button>
        <span class="zoom-level">{{ Math.round(zoom * 100) }}%</span>
        <button @click="zoomOut" class="zoom-btn">-</button>
      </div>
    </div>
    <div class="canvas-container" ref="canvasContainer">
      <canvas 
        ref="canvas" 
        @mousedown="onMouseDown"
        @mousemove="onMouseMove"
        @mouseup="onMouseUp"
        @wheel="onWheel"
        @click="onClick"
      ></canvas>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import type { DungeonData, Room, Corridor } from '@/types/dungeon'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

interface Props {
  dungeonData?: DungeonData
  showGrid?: boolean
  showLabels?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showGrid: true,
  showLabels: false
})

const emit = defineEmits<{
  roomClick: [room: Room]
  corridorClick: [corridor: Corridor]
}>()

const canvas = ref<HTMLCanvasElement>()
const canvasContainer = ref<HTMLDivElement>()

// 状态变量
const zoom = ref(1)
const offsetX = ref(0)
const offsetY = ref(0)
const isDragging = ref(false)
const lastMouseX = ref(0)
const lastMouseY = ref(0)

// 地图边界
const mapBounds = ref({
  minX: 0,
  maxX: 0,
  minY: 0,
  maxY: 0
})

const showGrid = ref(props.showGrid)
const showLabels = ref(props.showLabels)

// 颜色映射 - 使用专业蓝色色彩集
const roomColors = {
  room: '#2892D7',      // Celestial Blue - 普通房间
  chamber: '#1D70A2',   // Bice blue - 大厅
  boss: '#173753',      // Prussian blue - Boss房间
  treasure: '#6DAEDB',  // Carolina blue - 宝藏房间
  entrance: '#6DAEDB',  // Carolina blue - 入口
  exit: '#173753',      // Prussian blue - 出口
  corridor: '#1B4353',  // Charcoal - 走廊
  hall: '#1D70A2',      // Bice blue - 大厅
  bathroom: '#6DAEDB',  // Carolina blue - 浴室
  storage: '#1B4353'    // Charcoal - 储藏室
}

// 鼠标事件处理
const onMouseDown = (e: MouseEvent) => {
  isDragging.value = true
  lastMouseX.value = e.clientX
  lastMouseY.value = e.clientY
  e.preventDefault()
}

const onMouseMove = (e: MouseEvent) => {
  if (isDragging.value) {
    const deltaX = e.clientX - lastMouseX.value
    const deltaY = e.clientY - lastMouseY.value
    
    offsetX.value += deltaX
    offsetY.value += deltaY
    
    lastMouseX.value = e.clientX
    lastMouseY.value = e.clientY
    
    render()
  }
}

const onMouseUp = () => {
  isDragging.value = false
}

const onWheel = (e: WheelEvent) => {
  e.preventDefault()
  const delta = e.deltaY > 0 ? 0.9 : 1.1
  const newZoom = Math.max(0.1, Math.min(3, zoom.value * delta))
  
  // 以鼠标位置为中心缩放
  const rect = canvas.value!.getBoundingClientRect()
  const mouseX = e.clientX - rect.left
  const mouseY = e.clientY - rect.top
  
  const worldX = (mouseX - offsetX.value) / zoom.value
  const worldY = (mouseY - offsetY.value) / zoom.value
  
  zoom.value = newZoom
  
  offsetX.value = mouseX - worldX * zoom.value
  offsetY.value = mouseY - worldY * zoom.value
  
  render()
}

const onClick = (e: MouseEvent) => {
  if (!props.dungeonData) return
  
  const rect = canvas.value!.getBoundingClientRect()
  const mouseX = (e.clientX - rect.left - offsetX.value) / zoom.value
  const mouseY = (e.clientY - rect.top - offsetY.value) / zoom.value
  
  // 检查房间点击
  for (const room of props.dungeonData.rooms) {
    if (mouseX >= room.x && mouseX <= room.x + room.width &&
        mouseY >= room.y && mouseY <= room.y + room.height) {
      emit('roomClick', room)
      return
    }
  }
  
  // 检查通道点击
  for (const corridor of props.dungeonData.corridors) {
    const distance = pointToLineDistance(
      mouseX, mouseY,
      corridor.start.x, corridor.start.y,
      corridor.end.x, corridor.end.y
    )
    if (distance <= corridor.width / 2) {
      emit('corridorClick', corridor)
      return
    }
  }
}

// 计算点到线段的距离
const pointToLineDistance = (px: number, py: number, x1: number, y1: number, x2: number, y2: number) => {
  const A = px - x1
  const B = py - y1
  const C = x2 - x1
  const D = y2 - y1
  
  const dot = A * C + B * D
  const lenSq = C * C + D * D
  
  if (lenSq === 0) return Math.sqrt(A * A + B * B)
  
  const param = dot / lenSq
  
  let xx, yy
  
  if (param < 0) {
    xx = x1
    yy = y1
  } else if (param > 1) {
    xx = x2
    yy = y2
  } else {
    xx = x1 + param * C
    yy = y1 + param * D
  }
  
  const dx = px - xx
  const dy = py - yy
  
  return Math.sqrt(dx * dx + dy * dy)
}

// 渲染函数
const render = () => {
  if (!canvas.value) return
  
  const ctx = canvas.value.getContext('2d')
  if (!ctx) return
  
  const { width, height } = canvas.value
  ctx.clearRect(0, 0, width, height)
  
  // 设置背景 - 使用专业蓝色色彩集
  ctx.fillStyle = '#f8fafc'
  ctx.fillRect(0, 0, width, height)
  
  // 应用变换
  ctx.save()
  ctx.translate(offsetX.value, offsetY.value)
  ctx.scale(zoom.value, zoom.value)
  
  // 渲染网格
  if (showGrid.value) {
    renderGrid(ctx)
  }
  
  // 渲染通道
  renderCorridors(ctx)
  
  // 渲染房间
  renderRooms(ctx)
  
  ctx.restore()
  console.log('Rendering complete')
}

const renderGrid = (ctx: CanvasRenderingContext2D) => {
  const gridSize = 50
  const { width, height } = canvas.value!
  
  ctx.strokeStyle = '#e2e8f0'
  ctx.lineWidth = 1 / zoom.value
  ctx.globalAlpha = 0.3
  
  // 计算网格范围
  const startX = Math.floor(-offsetX.value / zoom.value / gridSize) * gridSize
  const startY = Math.floor(-offsetY.value / zoom.value / gridSize) * gridSize
  const endX = startX + width / zoom.value + gridSize
  const endY = startY + height / zoom.value + gridSize
  
  // 绘制垂直线
  for (let x = startX; x <= endX; x += gridSize) {
    ctx.beginPath()
    ctx.moveTo(x, startY)
    ctx.lineTo(x, endY)
    ctx.stroke()
  }
  
  // 绘制水平线
  for (let y = startY; y <= endY; y += gridSize) {
    ctx.beginPath()
    ctx.moveTo(startX, y)
    ctx.lineTo(endX, y)
    ctx.stroke()
  }
  
  ctx.globalAlpha = 1
}

const renderCorridors = (ctx: CanvasRenderingContext2D) => {
  if (!props.dungeonData) {
    console.log('No dungeon data for rendering corridors')
    return
  }
  
  console.log('Rendering corridors:', props.dungeonData.corridors.length)
  
  for (const corridor of props.dungeonData.corridors) {
    console.log('Rendering corridor:', corridor.id, 'from', corridor.start, 'to', corridor.end)
    
    // 根据通道类型设置不同的样式
    if (corridor.connection_type === 'room_to_room') {
      // 房间之间的连接线
      ctx.strokeStyle = '#6DAEDB'  // Carolina blue
      ctx.lineWidth = 4 / zoom.value
      ctx.setLineDash([5, 5])
    } else {
      // 物理通道
      ctx.strokeStyle = '#1D70A2'  // Bice blue
      ctx.lineWidth = (corridor.width || 6) / zoom.value
      ctx.setLineDash([])
    }
    
    ctx.lineCap = 'round'
    ctx.lineJoin = 'round'
    
    // 绘制通道线条
    ctx.beginPath()
    ctx.moveTo(corridor.start.x, corridor.start.y)
    ctx.lineTo(corridor.end.x, corridor.end.y)
    ctx.stroke()
    
    // 绘制通道端点
    ctx.fillStyle = ctx.strokeStyle
    ctx.beginPath()
    ctx.arc(corridor.start.x, corridor.start.y, 3 / zoom.value, 0, 2 * Math.PI)
    ctx.fill()
    ctx.beginPath()
    ctx.arc(corridor.end.x, corridor.end.y, 3 / zoom.value, 0, 2 * Math.PI)
    ctx.fill()
    
    // 重置线条样式
    ctx.setLineDash([])
  }
}

// 计算地图边界
const calculateMapBounds = () => {
  if (!props.dungeonData) return
  
  let minX = Infinity
  let maxX = -Infinity
  let minY = Infinity
  let maxY = -Infinity
  
  // 计算房间边界
  for (const room of props.dungeonData.rooms) {
    minX = Math.min(minX, room.x)
    maxX = Math.max(maxX, room.x + room.width)
    minY = Math.min(minY, room.y)
    maxY = Math.max(maxY, room.y + room.height)
  }
  
  // 计算通道边界
  for (const corridor of props.dungeonData.corridors) {
    minX = Math.min(minX, corridor.start.x, corridor.end.x)
    maxX = Math.max(maxX, corridor.start.x, corridor.end.x)
    minY = Math.min(minY, corridor.start.y, corridor.end.y)
    maxY = Math.max(maxY, corridor.start.y, corridor.end.y)
  }
  
  // 确保有有效的边界
  if (minX === Infinity) {
    minX = 0
    maxX = 100
    minY = 0
    maxY = 100
  }
  
  mapBounds.value = { minX, maxX, minY, maxY }
  console.log('Map bounds calculated:', mapBounds.value)
}

// 自动居中地图
const centerMap = () => {
  if (!canvas.value || !mapBounds.value) return
  
  const canvasWidth = canvas.value.width
  const canvasHeight = canvas.value.height
  
  const mapWidth = mapBounds.value.maxX - mapBounds.value.minX
  const mapHeight = mapBounds.value.maxY - mapBounds.value.minY
  
  // 确保地图有有效尺寸
  if (mapWidth <= 0 || mapHeight <= 0) {
    console.warn('Invalid map dimensions:', mapWidth, mapHeight)
    return
  }
  
  // 计算合适的缩放比例，留出20%的边距
  const scaleX = (canvasWidth * 0.8) / mapWidth
  const scaleY = (canvasHeight * 0.8) / mapHeight
  const scale = Math.min(scaleX, scaleY)
  
  zoom.value = Math.max(0.1, Math.min(3, scale))
  
  // 计算地图在缩放后的尺寸
  const scaledMapWidth = mapWidth * zoom.value
  const scaledMapHeight = mapHeight * zoom.value
  
  // 计算居中偏移 - 修正计算逻辑
  offsetX.value = (canvasWidth - scaledMapWidth) / 2 - (mapBounds.value.minX * zoom.value)
  offsetY.value = (canvasHeight - scaledMapHeight) / 2 - (mapBounds.value.minY * zoom.value)
  
  console.log('Map centered:', {
    canvasSize: `${canvasWidth}x${canvasHeight}`,
    mapSize: `${mapWidth}x${mapHeight}`,
    scaledSize: `${scaledMapWidth}x${scaledMapHeight}`,
    zoom: zoom.value,
    offset: { x: offsetX.value, y: offsetY.value }
  })
}

const renderRooms = (ctx: CanvasRenderingContext2D) => {
  if (!props.dungeonData) {
    console.log('No dungeon data for rendering rooms')
    return
  }
  
  console.log('Rendering rooms:', props.dungeonData.rooms.length)
  for (const room of props.dungeonData.rooms) {
    console.log('Rendering room:', room.id, 'at', room.x, room.y, 'size', room.width, 'x', room.height)
    
    // 绘制房间背景
    ctx.fillStyle = roomColors[room.type] || '#3b82f6'
    ctx.fillRect(room.x, room.y, room.width, room.height)
    
    // 绘制房间边框 - 使用专业蓝色色彩集
    ctx.strokeStyle = '#173753'  // Prussian blue
    ctx.lineWidth = 2 / zoom.value
    ctx.strokeRect(room.x, room.y, room.width, room.height)
    
    // 绘制房间内容图标
    const centerX = room.x + room.width / 2
    const centerY = room.y + room.height / 2
    const iconSize = Math.min(room.width, room.height) * 0.3
    
    ctx.fillStyle = '#ffffff'
    ctx.font = `${iconSize / zoom.value}px Arial`
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
  

    
    // 绘制标签
    if (showLabels.value) {
      ctx.fillStyle = '#173753'  // Prussian blue
      ctx.font = `${10 / zoom.value}px Arial`
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      
      // 房间ID标签
      ctx.fillText(
        `#${room.id}`,
        centerX,
        centerY + room.height / 2 - 15 / zoom.value
      )
      
      // 房间类型标签
      ctx.fillText(
        room.type,
        centerX,
        centerY + room.height / 2 + 5 / zoom.value
      )
    }
  }
}

// 控制函数
const resetCamera = () => {
  // 重新计算边界并居中
  calculateMapBounds()
  centerMap()
  render()
}

const zoomIn = () => {
  zoom.value = Math.min(3, zoom.value * 1.2)
  render()
}

const zoomOut = () => {
  zoom.value = Math.max(0.1, zoom.value / 1.2)
  render()
}

const toggleGrid = () => {
  showGrid.value = !showGrid.value
  render()
}

const toggleLabels = () => {
  showLabels.value = !showLabels.value
  render()
}

// 监听数据变化
watch(() => props.dungeonData, (newData) => {
  console.log('DungeonVisualizer received new data:', newData)
  if (newData) {
    console.log('Rooms:', newData.rooms?.length || 0)
    console.log('Corridors:', newData.corridors?.length || 0)
    
    // 验证数据格式
    if (!newData.rooms || !Array.isArray(newData.rooms)) {
      console.warn('Invalid rooms data:', newData.rooms)
      return
    }
    
    if (!newData.corridors || !Array.isArray(newData.corridors)) {
      console.warn('Invalid corridors data:', newData.corridors)
      return
    }
    
    // 验证房间数据
    for (let i = 0; i < newData.rooms.length; i++) {
      const room = newData.rooms[i]
      if (!room.x || !room.y || !room.width || !room.height) {
        console.warn(`Invalid room data at index ${i}:`, room)
      }
    }
    
    // 验证通道数据
    for (let i = 0; i < newData.corridors.length; i++) {
      const corridor = newData.corridors[i]
      if (!corridor.start || !corridor.end || 
          !corridor.start.x || !corridor.start.y ||
          !corridor.end.x || !corridor.end.y) {
        console.warn(`Invalid corridor data at index ${i}:`, corridor)
      }
    }
    
    nextTick(() => {
      // 计算地图边界并自动居中
      calculateMapBounds()
      centerMap()
      render()
      
      // 确保canvas尺寸正确
      if (canvas.value && canvasContainer.value) {
        const containerWidth = canvasContainer.value.clientWidth
        const containerHeight = canvasContainer.value.clientHeight
        if (canvas.value.width !== containerWidth || canvas.value.height !== containerHeight) {
          canvas.value.width = containerWidth
          canvas.value.height = containerHeight
          console.log('Canvas resized to:', containerWidth, 'x', containerHeight)
          render()
        }
      }
    })
  }
}, { deep: true })

watch([showGrid, showLabels], () => {
  console.log('Grid or labels changed, re-rendering...')
  render()
})

// 窗口大小变化处理函数
const handleResize = () => {
  if (canvas.value && canvasContainer.value) {
    const containerWidth = canvasContainer.value.clientWidth
    const containerHeight = canvasContainer.value.clientHeight
    
    if (canvas.value.width !== containerWidth || canvas.value.height !== containerHeight) {
      canvas.value.width = containerWidth
      canvas.value.height = containerHeight
      console.log('Canvas resized to:', containerWidth, 'x', containerHeight)
      
      // 重新居中并渲染
      if (props.dungeonData) {
        calculateMapBounds()
        centerMap()
      }
      render()
    }
  }
}

// 生命周期
onMounted(() => {
  console.log('DungeonVisualizer mounted')
  if (canvas.value && canvasContainer.value) {
    const containerWidth = canvasContainer.value.clientWidth
    const containerHeight = canvasContainer.value.clientHeight
    console.log('Canvas container size:', containerWidth, 'x', containerHeight)
    
    canvas.value.width = containerWidth
    canvas.value.height = containerHeight
    console.log('Canvas size set to:', canvas.value.width, 'x', canvas.value.height)
    
    // 如果有数据，立即计算边界并居中
    if (props.dungeonData) {
      calculateMapBounds()
      centerMap()
    }
    
    render()
    
    // 添加窗口大小变化监听器
    window.addEventListener('resize', handleResize)
  } else {
    console.error('Canvas or container not found')
  }
})

onUnmounted(() => {
  // 清理资源
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.dungeon-visualizer {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  background: #f8fafc;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

.controls {
  display: flex;
  gap: 8px;
  padding: 10px;
  background: #f1f5f9;
  border-bottom: 1px solid #e2e8f0;
}

.control-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: background 0.2s;
}

.control-btn:hover {
  background: #2563eb;
}

.zoom-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

.zoom-btn {
  background: #64748b;
  color: white;
  border: none;
  width: 24px;
  height: 24px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
}

.zoom-btn:hover {
  background: #475569;
}

.zoom-level {
  color: #334155;
  font-size: 14px;
  min-width: 50px;
  text-align: center;
}

.canvas-container {
  flex: 1;
  position: relative;
  overflow: hidden;
  min-height: 400px;
  height: 100%;
  background: #ffffff;
  border: 1px solid #e2e8f0;
}

canvas {
  display: block;
  cursor: grab;
  width: 100%;
  height: 100%;
  background: #ffffff;
}

canvas:active {
  cursor: grabbing;
}

@media (max-width: 768px) {
  .canvas-container {
    min-height: 400px;
  }
  
  .controls {
    flex-wrap: wrap;
    gap: 8px;
    padding: 10px;
  }
  
  .control-btn {
    padding: 6px 12px;
    font-size: 12px;
  }
  
  .zoom-controls {
    margin-left: 0;
    width: 100%;
    justify-content: center;
    margin-top: 10px;
  }
}
</style> 