import logging
from typing import Dict, Any, Optional, List, Tuple

from src.adapters.base import BaseAdapter
from src.schema import UnifiedDungeonFormat

logger = logging.getLogger(__name__)

class DonjonAdapter(BaseAdapter):
    """适配 donjon d20 随机地牢生成器格式。"""
    
    @property
    def format_name(self) -> str:
        return "donjon_d20"

    def detect(self, data: Dict[str, Any]) -> bool:
        """检测是否为 donjon d20 格式。"""
        # 检查关键字段
        required_fields = ['cell_bit', 'cells', 'rooms', 'settings']
        return all(field in data for field in required_fields)

    def _parse_cell_bits(self, cell_value: int, cell_bits: Dict[str, int]) -> Dict[str, bool]:
        """解析单元格的位标志。"""
        return {
            'room': bool(cell_value & cell_bits.get('room', 2)),
            'corridor': bool(cell_value & cell_bits.get('corridor', 4)),
            'door': bool(cell_value & cell_bits.get('door', 131072)),
            'wall': bool(cell_value & cell_bits.get('perimeter', 16)),
            'stairs_up': bool(cell_value & cell_bits.get('stair_up', 8388608)),
            'stairs_down': bool(cell_value & cell_bits.get('stair_down', 4194304)),
            'trapped': bool(cell_value & cell_bits.get('trapped', 524288)),
            'locked': bool(cell_value & cell_bits.get('locked', 262144)),
            'secret': bool(cell_value & cell_bits.get('secret', 1048576))
        }

    def _find_room_boundaries(self, cells: List[List[int]], cell_bits: Dict[str, int]) -> List[Dict[str, Any]]:
        """从单元格数据中识别房间边界。"""
        rooms = []
        visited = set()
        
        for row in range(len(cells)):
            for col in range(len(cells[row])):
                if (row, col) in visited:
                    continue
                    
                cell_value = cells[row][col]
                cell_flags = self._parse_cell_bits(cell_value, cell_bits)
                
                if cell_flags['room']:
                    # 找到房间的起始点，进行洪水填充
                    room_cells = self._flood_fill_room(cells, row, col, cell_bits, visited)
                    if room_cells:
                        # 计算房间边界
                        min_row = min(r for r, c in room_cells)
                        max_row = max(r for r, c in room_cells)
                        min_col = min(c for r, c in room_cells)
                        max_col = max(c for r, c in room_cells)
                        
                        rooms.append({
                            'id': f"room_{len(rooms)+1}",
                            'cells': room_cells,
                            'bounds': {
                                'min_row': min_row,
                                'max_row': max_row,
                                'min_col': min_col,
                                'max_col': max_col
                            }
                        })
        
        return rooms

    def _flood_fill_room(self, cells: List[List[int]], start_row: int, start_col: int, 
                        cell_bits: Dict[str, int], visited: set) -> List[Tuple[int, int]]:
        """使用洪水填充算法找到房间的所有单元格。"""
        if (start_row, start_col) in visited:
            return []
            
        room_cells = []
        stack = [(start_row, start_col)]
        
        while stack:
            row, col = stack.pop()
            
            if (row, col) in visited:
                continue
                
            # 检查边界
            if (row < 0 or row >= len(cells) or 
                col < 0 or col >= len(cells[row])):
                continue
                
            cell_value = cells[row][col]
            cell_flags = self._parse_cell_bits(cell_value, cell_bits)
            
            if not cell_flags['room']:
                continue
                
            visited.add((row, col))
            room_cells.append((row, col))
            
            # 添加相邻单元格
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_row, new_col = row + dr, col + dc
                if (new_row, new_col) not in visited:
                    stack.append((new_row, new_col))
        
        return room_cells

    def _find_doors(self, cells: List[List[int]], cell_bits: Dict[str, int], rooms_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从单元格数据和房间数据中识别门及其连接信息。"""
        doors = []
        
        # 处理room_data可能是列表或字典的情况
        if isinstance(rooms_data, list):
            room_dict = {}
            for i, room_info in enumerate(rooms_data):
                if room_info is not None:
                    room_dict[str(i)] = room_info
            rooms_data = room_dict
        
        # 从房间数据中提取门信息
        for room_id, room_info in rooms_data.items():
            if room_id == 'null' or room_info is None:
                continue
                
            room_doors = room_info.get('doors', {})
            for direction, door_list in room_doors.items():
                if isinstance(door_list, list):
                    for door_info in door_list:
                        door_obj = {
                            'id': f"door_{len(doors)+1}",
                            'position': {
                                'x': door_info.get('col', 0),
                                'y': door_info.get('row', 0)
                            },
                            'type': 'normal',
                            'description': door_info.get('desc', ''),
                            'connects': [room_id]
                        }
                        
                        # 确定门类型
                        if door_info.get('trap'):
                            door_obj['type'] = 'trapped'
                        elif door_info.get('type') == 'locked':
                            door_obj['type'] = 'locked'
                        elif door_info.get('secret'):
                            door_obj['type'] = 'secret'
                        
                        # 添加连接信息
                        out_id = door_info.get('out_id')
                        if out_id and str(out_id) in rooms_data:
                            door_obj['connects'].append(str(out_id))
                        
                        doors.append(door_obj)
        
        # 也从单元格数据中检测门（作为备用）
        for row in range(len(cells)):
            for col in range(len(cells[row])):
                cell_value = cells[row][col]
                cell_flags = self._parse_cell_bits(cell_value, cell_bits)
                
                if cell_flags['door']:
                    # 检查是否已经添加了这个位置的门
                    door_exists = any(d['position']['x'] == col and d['position']['y'] == row for d in doors)
                    if not door_exists:
                        door_type = 'normal'
                        if cell_flags['trapped']:
                            door_type = 'trapped'
                        elif cell_flags['locked']:
                            door_type = 'locked'
                        elif cell_flags['secret']:
                            door_type = 'secret'
                        
                        doors.append({
                            'id': f"door_{len(doors)+1}",
                            'position': {'x': col, 'y': row},
                            'type': door_type,
                            'connects': []
                        })
        
        return doors

    def _find_corridors(self, cells: List[List[int]], cell_bits: Dict[str, int]) -> List[Dict[str, Any]]:
        """从单元格数据中识别走廊。"""
        corridors = []
        visited = set()
        
        for row in range(len(cells)):
            for col in range(len(cells[row])):
                if (row, col) in visited:
                    continue
                    
                cell_value = cells[row][col]
                cell_flags = self._parse_cell_bits(cell_value, cell_bits)
                
                if cell_flags['corridor']:
                    # 找到走廊的起始点，进行洪水填充
                    corridor_cells = self._flood_fill_corridor(cells, row, col, cell_bits, visited)
                    if corridor_cells:
                        # 计算走廊边界
                        min_row = min(r for r, c in corridor_cells)
                        max_row = max(r for r, c in corridor_cells)
                        min_col = min(c for r, c in corridor_cells)
                        max_col = max(c for r, c in corridor_cells)
                        
                        corridors.append({
                            'id': f"corridor_{len(corridors)+1}",
                            'cells': corridor_cells,
                            'bounds': {
                                'min_row': min_row,
                                'max_row': max_row,
                                'min_col': min_col,
                                'max_col': max_col
                            }
                        })
        
        return corridors

    def _flood_fill_corridor(self, cells: List[List[int]], start_row: int, start_col: int, 
                           cell_bits: Dict[str, int], visited: set) -> List[Tuple[int, int]]:
        """使用洪水填充算法找到走廊的所有单元格。"""
        if (start_row, start_col) in visited:
            return []
            
        corridor_cells = []
        stack = [(start_row, start_col)]
        
        while stack:
            row, col = stack.pop()
            
            if (row, col) in visited:
                continue
                
            # 检查边界
            if (row < 0 or row >= len(cells) or 
                col < 0 or col >= len(cells[row])):
                continue
                
            cell_value = cells[row][col]
            cell_flags = self._parse_cell_bits(cell_value, cell_bits)
            
            if not cell_flags['corridor']:
                continue
                
            visited.add((row, col))
            corridor_cells.append((row, col))
            
            # 添加相邻单元格
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_row, new_col = row + dr, col + dc
                if (new_row, new_col) not in visited:
                    stack.append((new_row, new_col))
        
        return corridor_cells

    def _match_rooms_with_data(self, detected_rooms: List[Dict[str, Any]], 
                              room_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """将检测到的房间与donjon的房间数据匹配。"""
        matched_rooms = []
        
        # 处理room_data可能是列表或字典的情况
        if isinstance(room_data, list):
            # 如果是列表，转换为字典格式
            room_dict = {}
            for i, room_info in enumerate(room_data):
                if room_info is not None:  # 跳过None值
                    room_dict[str(i)] = room_info
            room_data = room_dict
        
        for i, detected_room in enumerate(detected_rooms):
            bounds = detected_room['bounds']
            center_col = (bounds['min_col'] + bounds['max_col']) // 2
            center_row = (bounds['min_row'] + bounds['max_row']) // 2
            
            # 尝试匹配房间数据
            matched_room_data = None
            matched_room_id = None
            for room_id, room_info in room_data.items():
                if room_id == 'null' or room_info is None:
                    continue
                    
                room_col = room_info.get('col', 0)
                room_row = room_info.get('row', 0)
                
                # 检查房间中心是否在检测到的房间范围内
                if (bounds['min_col'] <= room_col <= bounds['max_col'] and
                    bounds['min_row'] <= room_row <= bounds['max_row']):
                    matched_room_data = room_info
                    matched_room_id = room_id
                    break
            
            # 创建房间对象
            room_obj = {
                'id': f"room_{i+1}",
                'original_id': matched_room_id,  # 保存原始ID用于连接匹配
                'shape': 'rectangle',
                'position': {
                    'x': bounds['min_col'],
                    'y': bounds['min_row']
                },
                'size': {
                    'width': bounds['max_col'] - bounds['min_col'] + 1,
                    'height': bounds['max_row'] - bounds['min_row'] + 1
                },
                'name': f"房间 {i+1}",
                'description': ''
            }
            
            if matched_room_data:
                room_obj['name'] = matched_room_data.get('id', f"房间 {i+1}")
                contents = matched_room_data.get('contents', {})
                if contents:
                    summary = contents.get('summary', '')
                    detail = contents.get('detail', {})
                    if detail:
                        monster_info = detail.get('monster', [])
                        if monster_info:
                            room_obj['description'] = f"包含: {', '.join(monster_info[:2])}"
                        else:
                            room_obj['description'] = summary
                    else:
                        room_obj['description'] = summary
            
            matched_rooms.append(room_obj)
        
        return matched_rooms

    def _generate_room_connections(self, rooms: List[Dict[str, Any]], doors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """根据门信息生成房间连接关系。"""
        connections = []
        
        # 创建原始ID到房间对象的映射
        room_map = {}
        for room in rooms:
            if room.get('original_id'):
                room_map[room['original_id']] = room
        
        for door in doors:
            connects = door.get('connects', [])
            if len(connects) >= 2:
                # 找到连接的两个房间
                room1_original_id = connects[0]
                room2_original_id = connects[1]
                
                # 查找房间对象
                room1 = room_map.get(room1_original_id)
                room2 = room_map.get(room2_original_id)
                
                if room1 and room2:
                    connections.append({
                        'id': f"connection_{len(connections)+1}",
                        'from_room': room1['id'],
                        'to_room': room2['id'],
                        'door_id': door['id'],
                        'type': door['type'],
                        'position': door['position']
                    })
        
        return connections

    def convert(self, data: Dict[str, Any]) -> Optional[UnifiedDungeonFormat]:
        """将 donjon d20 格式数据转换为统一格式。"""
        try:
            # 提取基本信息
            settings = data.get('settings', {})
            name = settings.get('name', 'Donjon D20 Dungeon')
            cell_bits = data.get('cell_bit', {})
            cells = data.get('cells', [])
            rooms_data = data.get('rooms', {})
            
            # 创建统一格式对象
            unified = UnifiedDungeonFormat(
                name=name,
                author='Donjon D20 Generator',
                description=f"Generated dungeon with {len(rooms_data)} rooms",
                grid={
                    "type": "square",
                    "size": settings.get('cell_size', 16),
                    "unit": "ft"
                }
            )
            
            # 检测房间、门和走廊
            detected_rooms = self._find_room_boundaries(cells, cell_bits)
            doors = self._find_doors(cells, cell_bits, rooms_data)
            corridors = self._find_corridors(cells, cell_bits)
            
            # 匹配房间数据
            matched_rooms = self._match_rooms_with_data(detected_rooms, rooms_data)
            
            # 转换走廊为统一格式
            unified_corridors = []
            for corridor in corridors:
                bounds = corridor['bounds']
                unified_corridors.append({
                    'id': corridor['id'],
                    'shape': 'rectangle',
                    'position': {
                        'x': bounds['min_col'],
                        'y': bounds['min_row']
                    },
                    'size': {
                        'width': bounds['max_col'] - bounds['min_col'] + 1,
                        'height': bounds['max_row'] - bounds['min_row'] + 1
                    }
                })
            
            # 生成房间连接关系
            room_connections = self._generate_room_connections(matched_rooms, doors)
            
            # 添加层级
            unified.levels.append({
                'id': 'level_1',
                'name': '主层',
                'map': {
                    'width': len(cells[0]) if cells else 0,
                    'height': len(cells) if cells else 0
                },
                'rooms': matched_rooms,
                'doors': doors,
                'corridors': unified_corridors,
                'connections': room_connections
            })
            
            logger.info(f"Donjon D20转换完成: {len(matched_rooms)} 房间, {len(doors)} 门, {len(unified_corridors)} 走廊, {len(room_connections)} 连接")
            return unified
            
        except Exception as e:
            logger.error(f"转换Donjon D20格式时出错: {e}")
            return None 