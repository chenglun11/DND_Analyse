import type { DungeonData, Room, Corridor } from '@/types/dungeon'

export function generateTestDungeonData(): DungeonData {
  const rooms: Room[] = [
    {
      id: 'entrance',
      x: 100,
      y: 100,
      width: 80,
      height: 60,
      type: 'room',
      connections: ['corridor1']
    },
    {
      id: 'chamber1',
      x: 300,
      y: 80,
      width: 100,
      height: 80,
      type: 'chamber',
      connections: ['corridor1', 'corridor2']
    },
    {
      id: 'treasure1',
      x: 500,
      y: 120,
      width: 60,
      height: 60,
      type: 'treasure',
      connections: ['corridor2', 'corridor3']
    },
    {
      id: 'boss',
      x: 700,
      y: 100,
      width: 120,
      height: 100,
      type: 'boss',
      connections: ['corridor3']
    },
    {
      id: 'side_room',
      x: 200,
      y: 250,
      width: 70,
      height: 50,
      type: 'room',
      connections: ['corridor4']
    }
  ]

  const corridors: Corridor[] = [
    {
      id: 'corridor1',
      start: { x: 180, y: 130 },
      end: { x: 300, y: 120 },
      width: 8
    },
    {
      id: 'corridor2',
      start: { x: 400, y: 120 },
      end: { x: 500, y: 150 },
      width: 8
    },
    {
      id: 'corridor3',
      start: { x: 560, y: 150 },
      end: { x: 700, y: 150 },
      width: 8
    },
    {
      id: 'corridor4',
      start: { x: 150, y: 160 },
      end: { x: 200, y: 250 },
      width: 8
    }
  ]

  return {
    rooms,
    corridors,
    width: 900,
    height: 400
  }
}

export function convertUnifiedDataToDungeonData(unifiedData: any): DungeonData {
  console.log('开始转换统一数据:', unifiedData)
  
  if (!unifiedData || !unifiedData.levels || unifiedData.levels.length === 0) {
    console.warn('没有找到有效的层级数据')
    return generateTestDungeonData()
  }
  
  const level = unifiedData.levels[0]
  console.log('处理第一层:', level)
  
  const rooms: Room[] = []
  const corridors: Corridor[] = []
  
  // 参考visualizer.py的实现，只处理rooms数组
  const allRooms = level.rooms || []
  console.log('找到房间数据:', allRooms.length, '个房间')
  
  // 处理所有房间节点
  allRooms.forEach((room: any, index: number) => {
    console.log('处理房间', index, ':', room)
    
    let x = 0, y = 0, width = 50, height = 50
    
    // 处理不同的位置格式
    if (room.position && room.position.x !== undefined && room.position.y !== undefined) {
      x = room.position.x
      y = room.position.y
      console.log('房间', index, '位置:', { x, y })
    } else if (room.x !== undefined && room.y !== undefined) {
      x = room.x
      y = room.y
      console.log('房间', index, '直接坐标:', { x, y })
    }
    
    // 处理不同的大小格式
    if (room.size && room.size.width !== undefined && room.size.height !== undefined) {
      width = room.size.width
      height = room.size.height
      console.log('房间', index, '大小:', { width, height })
    } else if (room.width !== undefined && room.height !== undefined) {
      width = room.width
      height = room.height
      console.log('房间', index, '直接大小:', { width, height })
    }
    
    // 基于尺寸判断是否为房间（参考WatabouAdapter的逻辑）
    // 如果宽度或高度为1，且另一个维度也较小，则认为是通道
    const isThinCorridor = (width === 1 && height <= 3) || (height === 1 && width <= 3)
    const isSmallCorridor = width <= 2 && height <= 2
    
    // 判断是否为房间
    const isRoom = room.is_room === true || 
                   (!room.is_corridor && !isThinCorridor && !isSmallCorridor) ||
                   (width > 2 && height > 2) || 
                   room.type === 'room' ||
                   room.name?.toLowerCase().includes('room')
    
    console.log('房间', index, '判断结果:', { 
      width, height, isThinCorridor, isSmallCorridor, isRoom, 
      is_room: room.is_room, is_corridor: room.is_corridor 
    })
    
    if (isRoom) {
      rooms.push({
        id: room.id || `room_${index}`,
        x: x * 50 + 400, // 缩放并居中
        y: y * 50 + 300,
        width: width * 50,
        height: height * 50,
        type: 'room',
        connections: room.connections || [],
        name: room.name || `Room ${index}`,
        description: room.description || ''
      })
      console.log('添加房间:', rooms[rooms.length - 1])
    } else {
      // 这是通道，转换为线段
      let startX = 0, startY = 0, endX = 0, endY = 0
      
      if (width > height) {
        // 水平通道
        startX = x
        startY = y + height / 2
        endX = x + width
        endY = y + height / 2
      } else {
        // 垂直通道
        startX = x + width / 2
        startY = y
        endX = x + width / 2
        endY = y + height
      }
      
      corridors.push({
        id: room.id || `corridor_${index}`,
        start: { x: startX * 50 + 400, y: startY * 50 + 300 },
        end: { x: endX * 50 + 400, y: endY * 50 + 300 },
        width: 8,
        name: room.name || `Corridor ${index}`
      })
      console.log('添加通道:', corridors[corridors.length - 1])
    }
  })
  
  // 参考visualizer.py的_draw_connections方法，只从明确的连接信息创建通道
  if (level.connections && level.connections.length > 0) {
    console.log('从明确连接创建通道:', level.connections.length, '个连接')
    
    // 创建房间ID到房间对象的映射（参考visualizer.py）
    const roomMap = new Map<string, Room>()
    rooms.forEach(room => {
      roomMap.set(room.id, room)
    })
    
    level.connections.forEach((connection: any, index: number) => {
      const fromRoomId = connection.from_room || connection.from
      const toRoomId = connection.to_room || connection.to
      
      console.log(`处理连接${index}:`, { fromRoomId, toRoomId })
      
      const fromRoom = roomMap.get(fromRoomId)
      const toRoom = roomMap.get(toRoomId)
      
      if (fromRoom && toRoom) {
        // 计算房间中心点（参考visualizer.py的逻辑）
        const fromCenterX = fromRoom.x + fromRoom.width / 2
        const fromCenterY = fromRoom.y + fromRoom.height / 2
        const toCenterX = toRoom.x + toRoom.width / 2
        const toCenterY = toRoom.y + toRoom.height / 2
        
        corridors.push({
          id: connection.door_id || `connection_${index}`,
          start: { x: fromCenterX, y: fromCenterY },
          end: { x: toCenterX, y: toCenterY },
          width: 8,
          name: `Connection ${index}`
        })
        console.log('从明确连接创建通道:', corridors[corridors.length - 1])
      } else {
        console.warn('连接', connection, '找不到对应的房间:', { fromRoomId, toRoomId })
        console.warn('可用的房间ID:', Array.from(roomMap.keys()))
      }
    })
  }
  
  // 计算地图边界
  let minX = 0, minY = 0, maxX = 800, maxY = 600
  
  if (rooms.length > 0) {
    const roomXs = rooms.map(r => [r.x, r.x + r.width]).flat()
    const roomYs = rooms.map(r => [r.y, r.y + r.height]).flat()
    minX = Math.min(...roomXs)
    maxX = Math.max(...roomXs)
    minY = Math.min(...roomYs)
    maxY = Math.max(...roomYs)
  }
  
  if (corridors.length > 0) {
    const corridorXs = corridors.map(c => [c.start.x, c.end.x]).flat()
    const corridorYs = corridors.map(c => [c.start.y, c.end.y]).flat()
    minX = Math.min(minX, ...corridorXs)
    maxX = Math.max(maxX, ...corridorXs)
    minY = Math.min(minY, ...corridorYs)
    maxY = Math.max(maxY, ...corridorYs)
  }
  
  const result: DungeonData = {
    width: Math.max(800, maxX - minX + 100),
    height: Math.max(600, maxY - minY + 100),
    rooms,
    corridors
  }
  
  console.log('转换完成:', result)
  console.log('房间数量:', rooms.length)
  console.log('通道数量:', corridors.length)
  console.log('地图尺寸:', result.width, 'x', result.height)
  
  return result
}

// 处理FiMap Elites格式
export function convertFimapDataToDungeonData(fimapData: any): DungeonData {
  const rooms: Room[] = []
  const corridors: Corridor[] = []
  
  if (fimapData.plan_graph && fimapData.plan_graph.graph) {
    const graphData = fimapData.plan_graph.graph
    const weightData = graphData.weight_per_neighbor_per_vertex || {}
    
    const nodes = Object.keys(weightData)
    const gridSize = 60
    const gridCols = Math.ceil(Math.sqrt(nodes.length))
    
    // 创建房间
    nodes.forEach((nodeId, index) => {
      const row = Math.floor(index / gridCols)
      const col = index % gridCols
      const x = col * gridSize
      const y = row * gridSize
      
      rooms.push({
        id: nodeId,
        x,
        y,
        width: 50,
        height: 50,
        type: 'room',
        connections: Object.keys(weightData[nodeId] || {})
      })
    })
    
    // 创建通道
    nodes.forEach((nodeId, index) => {
      const neighbors = weightData[nodeId] || {}
      const fromRoom = rooms.find(r => r.id === nodeId)
      
      if (fromRoom) {
        Object.keys(neighbors).forEach(neighborId => {
          const toRoom = rooms.find(r => r.id === neighborId)
          if (toRoom && !corridors.some(c => 
            (c.start.x === fromRoom.x + fromRoom.width / 2 && c.start.y === fromRoom.y + fromRoom.height / 2 &&
             c.end.x === toRoom.x + toRoom.width / 2 && c.end.y === toRoom.y + toRoom.height / 2) ||
            (c.start.x === toRoom.x + toRoom.width / 2 && c.start.y === toRoom.y + toRoom.height / 2 &&
             c.end.x === fromRoom.x + fromRoom.width / 2 && c.end.y === fromRoom.y + fromRoom.height / 2)
          )) {
            corridors.push({
              id: `${nodeId}_to_${neighborId}`,
              start: { 
                x: fromRoom.x + fromRoom.width / 2, 
                y: fromRoom.y + fromRoom.height / 2 
              },
              end: { 
                x: toRoom.x + toRoom.width / 2, 
                y: toRoom.y + toRoom.height / 2 
              },
              width: 8
            })
          }
        })
      }
    })
  }
  
  return {
    rooms,
    corridors,
    width: 800,
    height: 600
  }
} 