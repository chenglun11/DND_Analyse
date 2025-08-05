<template>
  <div class="dungeon-visualizer">
    <div class="controls">
      <button @click="resetCamera" class="control-btn">重置视角</button>
      <button @click="toggleGrid" class="control-btn">{{ showGrid ? '隐藏网格' : '显示网格' }}</button>
      <button @click="toggleLabels" class="control-btn">{{ showLabels ? '隐藏标签' : '显示标签' }}</button>
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

interface Props {
  dungeonData?: DungeonData
  showGrid?: boolean
  showLabels?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showGrid: true,
  showLabels: true
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

const showGrid = ref(props.showGrid)
const showLabels = ref(props.showLabels)

// 颜色映射
const roomColors = {
  room: '#3498db',
  chamber: '#e74c3c', 
  boss: '#f39c12',
  treasure: '#f1c40f',
  entrance: '#2ecc71',
  exit: '#e67e22',
  corridor: '#95a5a6',
  hall: '#9b59b6',
  bathroom: '#1abc9c',
  storage: '#34495e'
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
  console.log('Rendering dungeon...')
  if (!canvas.value || !props.dungeonData) {
    console.log('Canvas or dungeon data not available')
    return
  }
  
  console.log('Dungeon data:', props.dungeonData)
  console.log('Canvas size:', canvas.value.width, 'x', canvas.value.height)
  
  const ctx = canvas.value.getContext('2d')!
  const { width, height } = canvas.value
  
  // 清除画布
  ctx.clearRect(0, 0, width, height)
  
  // 设置背景
  ctx.fillStyle = '#2c3e50'
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
  
  ctx.strokeStyle = '#34495e'
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
      ctx.strokeStyle = '#e74c3c'
      ctx.lineWidth = 4 / zoom.value
      ctx.setLineDash([5, 5])
    } else {
      // 物理通道
      ctx.strokeStyle = '#8b4513'
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

const renderRooms = (ctx: CanvasRenderingContext2D) => {
  if (!props.dungeonData) {
    console.log('No dungeon data for rendering rooms')
    return
  }
  
  console.log('Rendering rooms:', props.dungeonData.rooms.length)
  for (const room of props.dungeonData.rooms) {
    console.log('Rendering room:', room.id, 'at', room.x, room.y, 'size', room.width, 'x', room.height)
    
    // 绘制房间背景
    ctx.fillStyle = roomColors[room.type] || '#3498db'
    ctx.fillRect(room.x, room.y, room.width, room.height)
    
    // 绘制房间边框
    ctx.strokeStyle = '#ffffff'
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
    
    // 根据房间类型绘制图标
    const roomIcon = getRoomIcon(room.type)
    if (roomIcon) {
      ctx.fillText(roomIcon, centerX, centerY - iconSize / 4)
    }
    
    // 绘制标签
    if (showLabels.value) {
      ctx.fillStyle = '#ffffff'
      ctx.font = `${10 / zoom.value}px Arial`
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      
      // 房间ID标签
      ctx.fillText(
        `#${room.id}`,
        room.x + room.width / 2,
        room.y + room.height + 15 / zoom.value
      )
      
      // 房间类型标签  
      ctx.fillText(
        room.type,
        room.x + room.width / 2,
        room.y + room.height / 2 + iconSize / 2
      )
    }
  }
}

// 控制函数
const resetCamera = () => {
  zoom.value = 1
  offsetX.value = 0
  offsetY.value = 0
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

// 获取房间图标
const getRoomIcon = (roomType: string): string => {
  const iconMap: Record<string, string> = {
    room: '🏠',
    chamber: '🏛️',
    boss: '👑',
    treasure: '💰',
    entrance: '🚪',
    exit: '🚫',
    corridor: '➡️',
    hall: '🏰',
    bathroom: '🚿',
    storage: '📦'
  }
  return iconMap[roomType] || '❓'
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
      render()
    })
  }
}, { deep: true })

watch([showGrid, showLabels], () => {
  console.log('Grid or labels changed, re-rendering...')
  render()
})

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
    
    render()
  } else {
    console.error('Canvas or container not found')
  }
})

onUnmounted(() => {
  // 清理资源
})
</script>

<style scoped>
.dungeon-visualizer {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  background: #2c3e50;
  border-radius: 8px;
  overflow: hidden;
}

.controls {
  display: flex;
  gap: 8px;
  padding: 10px;
  background: #34495e;
  border-bottom: 1px solid #2c3e50;
}

.control-btn {
  background: #3498db;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: background 0.2s;
}

.control-btn:hover {
  background: #2980b9;
}

.zoom-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

.zoom-btn {
  background: #e74c3c;
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
  background: #c0392b;
}

.zoom-level {
  color: white;
  font-size: 14px;
  min-width: 50px;
  text-align: center;
}

.canvas-container {
  flex: 1;
  position: relative;
  overflow: hidden;
  min-height: 600px;
  height: 600px;
  background: #2c3e50;
  border: 1px solid #34495e;
}

canvas {
  display: block;
  cursor: grab;
  width: 100%;
  height: 100%;
  background: #2c3e50;
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