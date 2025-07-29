export interface DungeonData {
  rooms: Room[]
  corridors: Corridor[]
  width: number
  height: number
}

export interface Room {
  id: string
  x: number
  y: number
  width: number
  height: number
  type: 'room' | 'chamber' | 'boss' | 'treasure'
  connections: string[]
  name?: string
  description?: string
}

export interface Corridor {
  id: string
  start: { x: number; y: number }
  end: { x: number; y: number }
  width: number
  name?: string
  connection_type?: 'room_to_room' | 'physical'
} 