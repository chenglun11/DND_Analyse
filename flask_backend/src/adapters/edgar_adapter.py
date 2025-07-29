import logging
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from src.adapters.base import BaseAdapter
from src.schema import UnifiedDungeonFormat

logger = logging.getLogger(__name__)

class EdgarAdapter(BaseAdapter):
    """适配 Edgar 地牢生成器格式。"""
    
    @property
    def format_name(self) -> str:
        return "edgar_dungeon"

    def detect(self, data: Dict[str, Any]) -> bool:
        """检测是否为 Edgar 格式。"""
        # Edgar格式的特征：包含Rooms数组，每个房间有Room、RoomDescription、Outline、Position等字段
        if 'Rooms' in data and isinstance(data['Rooms'], list):
            if len(data['Rooms']) > 0:
                first_room = data['Rooms'][0]
                # 检查关键字段
                required_fields = ['Room', 'RoomDescription', 'Outline', 'Position', 'Doors']
                if all(field in first_room for field in required_fields):
                    return True
        return False

    def _generate_corridor_path(self, room1_pos: Tuple[float, float], room2_pos: Tuple[float, float], 
                               room1_size: Tuple[float, float], room2_size: Tuple[float, float]) -> List[Tuple[float, float, float, float]]:
        """生成走廊路径，支持拐弯"""
        x1, y1 = room1_pos
        x2, y2 = room2_pos
        w1, h1 = room1_size
        w2, h2 = room2_size
        
        # 计算房间中心
        center1_x = x1 + w1 / 2
        center1_y = y1 + h1 / 2
        center2_x = x2 + w2 / 2
        center2_y = y2 + h2 / 2
        
        # 走廊宽度
        corridor_width = 3
        
        # 计算房间边界上的连接点
        # 从房间1的边界到房间2的边界
        if abs(center1_x - center2_x) > abs(center1_y - center2_y):
            # 水平距离更大，先水平移动
            if center1_x < center2_x:
                # 从房间1右边到房间2左边
                start_x = x1 + w1
                start_y = center1_y
                end_x = x2
                end_y = center2_y
            else:
                # 从房间1左边到房间2右边
                start_x = x1
                start_y = center1_y
                end_x = x2 + w2
                end_y = center2_y
            
            # 创建L形走廊
            corridor_segments = []
            
            # 水平段
            corridor_segments.append((
                start_x, start_y - corridor_width/2,
                abs(end_x - start_x), corridor_width
            ))
            
            # 垂直段（如果需要）
            if abs(start_y - end_y) > corridor_width:
                if start_y < end_y:
                    corridor_segments.append((
                        end_x - corridor_width/2, start_y,
                        corridor_width, abs(end_y - start_y)
                    ))
                else:
                    corridor_segments.append((
                        end_x - corridor_width/2, end_y,
                        corridor_width, abs(start_y - end_y)
                    ))
        else:
            # 垂直距离更大，先垂直移动
            if center1_y < center2_y:
                # 从房间1下边到房间2上边
                start_x = center1_x
                start_y = y1 + h1
                end_x = center2_x
                end_y = y2
            else:
                # 从房间1上边到房间2下边
                start_x = center1_x
                start_y = y1
                end_x = center2_x
                end_y = y2 + h2
            
            # 创建L形走廊
            corridor_segments = []
            
            # 垂直段
            corridor_segments.append((
                start_x - corridor_width/2, start_y,
                corridor_width, abs(end_y - start_y)
            ))
            
            # 水平段（如果需要）
            if abs(start_x - end_x) > corridor_width:
                if start_x < end_x:
                    corridor_segments.append((
                        start_x, end_y - corridor_width/2,
                        abs(end_x - start_x), corridor_width
                    ))
                else:
                    corridor_segments.append((
                        end_x, end_y - corridor_width/2,
                        abs(start_x - end_x), corridor_width
                    ))
        
        return corridor_segments

    def convert(self, data: Dict[str, Any]) -> Optional[UnifiedDungeonFormat]:
        """将 Edgar 格式数据转换为统一格式。"""
        try:
            unified = UnifiedDungeonFormat(
                name="Edgar Dungeon",
                author='Edgar Generator',
                description='Converted from Edgar format',
                grid={"type": "square", "size": 5, "unit": "ft"}
            )

            rooms_data = data.get('Rooms', [])
            if not rooms_data:
                unified.levels = [{"id": "level_1", "name": "Main Level", "map": {"width": 0, "height": 0}, "rooms": [], "doors": [], "connections": []}]
                return unified

            # 转换房间数据
            rooms = []
            connections = []
            game_elements = []
            
            # 计算地图边界
            min_x, min_y = float('inf'), float('inf')
            max_x, max_y = float('-inf'), float('-inf')
            
            # 首先收集所有连接信息，用于布局计算
            connections_info = []
            for room_data in rooms_data:
                doors = room_data.get('Doors', [])
                for door in doors:
                    from_room = str(door.get('FromRoom', ''))
                    to_room = str(door.get('ToRoom', ''))
                    if from_room and to_room:
                        connections_info.append((from_room, to_room))
            
            # 创建房间ID到索引的映射
            room_ids = [str(room_data.get('Room', '')) for room_data in rooms_data]
            room_id_to_index = {room_id: idx for idx, room_id in enumerate(room_ids)}
            
            # 使用最小生成树算法优化连接，减少循环
            essential_connections = self._get_minimum_spanning_tree(room_ids, connections_info)
            
            # 为每个房间计算位置
            room_positions = {}
            
            for room_data in rooms_data:
                room_id = str(room_data.get('Room', ''))
                
                # 获取房间位置和尺寸
                outline = room_data.get('Outline', {})
                bounding_rect = outline.get('BoundingRectangle', {})
                center = bounding_rect.get('Center', {})
                width = bounding_rect.get('Width', 0)
                height = bounding_rect.get('Height', 0)
                
                # 使用基于最小生成树的布局算法
                room_index = room_id_to_index.get(room_id, 0)
                
                # 基于最小生成树连接关系计算位置
                # 找到与当前房间在最小生成树中直接连接的房间
                connected_rooms = []
                for from_room, to_room in essential_connections:
                    if from_room == room_id:
                        connected_rooms.append(to_room)
                    elif to_room == room_id:
                        connected_rooms.append(from_room)
                
                # 使用基于最小生成树的布局算法
                if room_index == 0:
                    # 第一个房间放在中心
                    x = 50
                    y = 50
                else:
                    # 基于最小生成树连接关系计算位置
                    # 找到已布局的连接房间
                    connected_positions = []
                    for connected_room_id in connected_rooms:
                        if connected_room_id in room_positions:
                            connected_positions.append(room_positions[connected_room_id])
                    
                    if connected_positions:
                        # 计算连接房间的平均位置
                        avg_x = sum(pos[0] for pos in connected_positions) / len(connected_positions)
                        avg_y = sum(pos[1] for pos in connected_positions) / len(connected_positions)
                        
                        # 在平均位置附近选择一个网格位置
                        grid_x = round(avg_x / 20) * 20
                        grid_y = round(avg_y / 20) * 20
                        
                        # 添加一些随机偏移，避免完全重叠
                        hash_val = int(hashlib.md5(room_id.encode()).hexdigest()[:8], 16)
                        offset_x = ((hash_val % 40) - 20)  # -20到20的偏移
                        offset_y = (((hash_val >> 8) % 40) - 20)  # -20到20的偏移
                        
                        x = grid_x + offset_x
                        y = grid_y + offset_y
                        
                        # 确保位置在合理范围内
                        x = max(10, min(190, x))
                        y = max(10, min(190, y))
                    else:
                        # 如果没有已布局的连接房间，使用网格布局
                        grid_x = (room_index % 5) * 30  # 5x5网格
                        grid_y = (room_index // 5) * 30
                        x = grid_x + 20
                        y = grid_y + 20
                
                # 存储房间位置
                room_positions[room_id] = (x, y)
                
                # 更新边界
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x + width)
                max_y = max(max_y, y + height)
                
                # 创建房间对象
                room = {
                    "id": f"room_{room_id}",
                    "name": f"Room {room_id}",
                    "shape": "rectangle",
                    "position": {"x": x, "y": y},
                    "size": {"width": width, "height": height},
                    "is_room": True,
                    "description": f"Room {room_id} from Edgar generator"
                }
                
                # 检查是否为走廊
                if room_data.get('IsCorridor', False):
                    room["is_corridor"] = True
                    room["is_room"] = False
                
                rooms.append(room)
                
                # 处理门连接 - 只保留最小生成树中的连接
                doors = room_data.get('Doors', [])
                for door in doors:
                    from_room = str(door.get('FromRoom', ''))
                    to_room = str(door.get('ToRoom', ''))
                    
                    if from_room and to_room:
                        # 检查是否在最小生成树中
                        if (from_room, to_room) in essential_connections or (to_room, from_room) in essential_connections:
                            connection = {
                                "from_room": f"room_{from_room}",
                                "to_room": f"room_{to_room}",
                                "door_id": f"door_{from_room}_{to_room}"
                            }
                            # 避免重复连接
                            if connection not in connections:
                                connections.append(connection)
            
            # 创建地图信息
            map_info = {
                "width": max_x - min_x if max_x > min_x else 100,
                "height": max_y - min_y if max_y > min_y else 100
            }
            
            # 创建关卡
            level = {
                "id": "level_1",
                "name": "Main Level",
                "map": map_info,
                "rooms": rooms,
                "doors": [],  # Edgar格式没有独立的门对象
                "connections": connections,
                "game_elements": game_elements
            }
            
            unified.levels = [level]
            return unified
            
        except Exception as e:
            logger.error(f"转换 Edgar 格式时出错: {e}")
            return None

    def _get_minimum_spanning_tree(self, room_ids: List[str], connections_info: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """使用Kruskal算法计算最小生成树，减少循环连接"""
        if not room_ids:
            return []
        
        # 创建并查集用于检测循环
        parent = {room_id: room_id for room_id in room_ids}
        
        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]
        
        def union(x, y):
            parent[find(x)] = find(y)
        
        # 计算所有连接的距离（使用房间ID的哈希值作为距离）
        edges = []
        for from_room, to_room in connections_info:
            # 使用房间ID的哈希值作为距离权重
            hash1 = int(hashlib.md5(from_room.encode()).hexdigest()[:8], 16)
            hash2 = int(hashlib.md5(to_room.encode()).hexdigest()[:8], 16)
            distance = abs(hash1 - hash2)
            edges.append((distance, from_room, to_room))
        
        # 按距离排序
        edges.sort()
        
        # Kruskal算法
        mst_edges = []
        for distance, from_room, to_room in edges:
            if find(from_room) != find(to_room):
                union(from_room, to_room)
                mst_edges.append((from_room, to_room))
        
        # 确保所有房间都连接（如果原图是连通的）
        # 如果最小生成树不包含所有房间，添加一些额外的连接
        connected_rooms = set()
        for from_room, to_room in mst_edges:
            connected_rooms.add(from_room)
            connected_rooms.add(to_room)
        
        # 对于未连接的房间，添加一些连接
        unconnected_rooms = set(room_ids) - connected_rooms
        if unconnected_rooms:
            # 为每个未连接的房间找到最近的已连接房间
            for unconnected_room in unconnected_rooms:
                min_distance = float('inf')
                best_connected_room = None
                
                for connected_room in connected_rooms:
                    # 计算距离
                    hash1 = int(hashlib.md5(unconnected_room.encode()).hexdigest()[:8], 16)
                    hash2 = int(hashlib.md5(connected_room.encode()).hexdigest()[:8], 16)
                    distance = abs(hash1 - hash2)
                    
                    if distance < min_distance:
                        min_distance = distance
                        best_connected_room = connected_room
                
                if best_connected_room:
                    mst_edges.append((unconnected_room, best_connected_room))
                    connected_rooms.add(unconnected_room)
        
        return mst_edges 