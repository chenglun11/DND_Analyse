from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

@dataclass
class UnifiedDungeonFormat:
    """统一的地牢格式数据类 (数据模型)"""
    schema_name: str = "dnd-dungeon-unified"
    schema_version: str = "1.0.0"
    name: str = "Unnamed Dungeon"
    author: str = "Adapter"
    description: str = "Converted from other formats"
    grid: Dict[str, Any] = field(default_factory=lambda: {"type": "square", "size": 5, "unit": "ft"})
    levels: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """将数据对象转换为字典，以便序列化（例如存为JSON）"""
        return {
            "header": {
                "schemaName": self.schema_name,
                "schemaVersion": self.schema_version,
                "name": self.name,
                "author": self.author,
                "description": self.description,
                "grid": self.grid
            },
            "levels": self.levels
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UnifiedDungeonFormat':
        """从字典创建UnifiedDungeonFormat对象"""
        header = data.get('header', {})
        return cls(
            schema_name=header.get('schemaName', 'dnd-dungeon-unified'),
            schema_version=header.get('schemaVersion', '1.0.0'),
            name=header.get('name', 'Unnamed Dungeon'),
            author=header.get('author', 'Adapter'),
            description=header.get('description', 'Converted from other formats'),
            grid=header.get('grid', {"type": "square", "size": 5, "unit": "ft"}),
            levels=data.get('levels', [])
        )

def _analyze_room_semantics(room: Dict[str, Any]) -> Dict[str, float]:
    """
    分析房间的语义特征，返回入口/出口倾向性评分
    
    Args:
        room: 房间数据
        
    Returns:
        包含入口倾向性和出口倾向性的字典
    """
    room_name = room.get('name', '').lower()
    room_desc = room.get('description', '').lower()
    
    entrance_score = 0.0
    exit_score = 0.0
    
    # 入口特征分析
    entrance_features = {
        'gate': 0.8, 'door': 0.7, 'entrance': 1.0, 'entry': 1.0,
        'portal': 0.9, 'keyhole': 0.6, 'iron door': 0.8, 'great door': 0.8,
        '入口': 1.0, '进口': 1.0, '大门': 0.9, '门厅': 0.8, '大厅': 0.6
    }
    
    # 出口特征分析
    exit_features = {
        'exit': 1.0, '出口': 1.0, '终点': 0.9, 'boss': 0.8, 'boss room': 0.9,
        'final': 0.8, 'end': 0.7, 'treasure': 0.6, 'gold': 0.5, 'magic': 0.6,
        'legendary': 0.7, 'spellbook': 0.8, 'tome': 0.7, 'chest': 0.5,
        'corpse': 0.3, 'dead': 0.3, 'skeleton': 0.3  # 负面特征
    }
    
    # 计算入口分数
    for feature, weight in entrance_features.items():
        if feature in room_name or feature in room_desc:
            entrance_score += weight
    
    # 计算出口分数
    for feature, weight in exit_features.items():
        if feature in room_name or feature in room_desc:
            exit_score += weight
    
    # 特殊规则：如果房间描述包含"undead wyrm"或类似怪物，可能是出口
    monster_keywords = ['undead wyrm', 'dragon', 'boss', 'monster', 'creature']
    if any(keyword in room_desc for keyword in monster_keywords):
        exit_score += 0.5
    
    # 特殊规则：如果房间描述包含"key"或"pedestal"，可能是重要房间
    key_keywords = ['key', 'pedestal', 'altar', 'shrine']
    if any(keyword in room_desc for keyword in key_keywords):
        exit_score += 0.3
    
    return {'entrance_score': entrance_score, 'exit_score': exit_score}

def identify_entrance_exit(dungeon_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    智能识别地牢的入口和出口房间
    
    识别策略（按优先级）：
    1. 明确标记的房间（is_entrance/is_exit）
    2. 拓扑分析（连接度、连通性）
    3. 空间位置分析（坐标位置）
    """
    if not dungeon_data.get('levels'):
        return dungeon_data
    
    level = dungeon_data['levels'][0]
    rooms = level.get('rooms', [])
    connections = level.get('connections', [])
    
    if not rooms:
        return dungeon_data
    
    # 构建连接图
    graph = {room['id']: [] for room in rooms}
    for conn in connections:
        if conn['from_room'] in graph and conn['to_room'] in graph:
            graph[conn['from_room']].append(conn['to_room'])
            graph[conn['to_room']].append(conn['from_room'])
    
    # 1. 检查明确标记的房间
    entrance_room = None
    exit_room = None
    
    for room in rooms:
        if room.get('is_entrance', False):
            entrance_room = room['id']
        elif room.get('is_exit', False):
            exit_room = room['id']
    
    # 2. 拓扑分析识别（改进版）
    if not entrance_room or not exit_room:
        # 只考虑有连接的房间
        connected_rooms = [room for room in rooms if len(graph[room['id']]) > 0]
        
        if len(connected_rooms) >= 2:
            # 入口选择策略：连接度较低但不是死胡同的房间
            if not entrance_room:
                # 优先选择连接度为1的房间
                degree_1_rooms = [r for r in connected_rooms if len(graph[r['id']]) == 1]
                if degree_1_rooms:
                    entrance_room = degree_1_rooms[0]['id']
                else:
                    # 如果没有度为1的房间，选择连接度最低的
                    entrance_room = min(connected_rooms, key=lambda r: len(graph[r['id']]))['id']
            
            # 出口选择策略：另一个连接度较低的房间，且与入口可达
            if not exit_room:
                exit_candidates = [r for r in connected_rooms if r['id'] != entrance_room]
                if exit_candidates:
                    # 优先选择连接度为1的房间
                    degree_1_exits = [r for r in exit_candidates if len(graph[r['id']]) == 1]
                    if degree_1_exits:
                        # 检查可达性
                        for candidate in degree_1_exits:
                            if _is_reachable(graph, entrance_room, candidate['id']):
                                exit_room = candidate['id']
                                break
                    
                    # 如果没有可达的度为1的房间，选择连接度最低的可达房间
                    if not exit_room:
                        for candidate in sorted(exit_candidates, key=lambda r: len(graph[r['id']])):
                            if _is_reachable(graph, entrance_room, candidate['id']):
                                exit_room = candidate['id']
                                break
    
    # 3. 空间位置分析（如果拓扑分析失败）
    if not entrance_room or not exit_room:
        def get_room_center(room):
            pos = room.get('position', {})
            size = room.get('size', {})
            x = pos.get('x', 0) + size.get('width', 0) / 2
            y = pos.get('y', 0) + size.get('height', 0) / 2
            return x, y
        
        # 只考虑有连接的房间
        connected_rooms = [room for room in rooms if len(graph[room['id']]) > 0]
        if len(connected_rooms) >= 2:
            room_centers = []
            for room in connected_rooms:
                center = get_room_center(room)
                room_centers.append({
                    'room_id': room['id'],
                    'center': center,
                    'x': center[0],
                    'y': center[1]
                })
            
            if not entrance_room:
                # 选择最左下角的房间作为入口
                entrance_room = min(room_centers, key=lambda x: x['x'] + x['y'])['room_id']
            
            if not exit_room:
                # 选择最右上角的房间作为出口（排除入口）
                exit_candidates = [r for r in room_centers if r['room_id'] != entrance_room]
                if exit_candidates:
                    exit_room = max(exit_candidates, key=lambda x: x['x'] + x['y'])['room_id']
    
    # 4. 标记识别结果
    if entrance_room and exit_room:
        for room in rooms:
            if room['id'] == entrance_room:
                room['is_entrance'] = True
                room['is_exit'] = False
            elif room['id'] == exit_room:
                room['is_entrance'] = False
                room['is_exit'] = True
            else:
                # 清除其他房间的标记
                room.pop('is_entrance', None)
                room.pop('is_exit', None)
    
    return dungeon_data

def _is_reachable(graph: Dict[str, List[str]], start: str, end: str) -> bool:
    """
    检查两个节点是否可达（BFS）
    """
    if start == end:
        return True
    
    visited = set()
    queue = [start]
    visited.add(start)
    
    while queue:
        current = queue.pop(0)
        for neighbor in graph.get(current, []):
            if neighbor == end:
                return True
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return False 