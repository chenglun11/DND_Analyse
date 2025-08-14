"""
空间邻接推断模块
基于房间位置和尺寸自动推断房间之间的连接关系
"""

import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

class SpatialInferenceEngine:
    """
    空间邻接推断引擎
    spatial adjacency inference engine

    - 提取边界
    - 判断邻接
    - 计算置信度
    - 补全连接信息
    - 补全门信息
    - 返回增强后的地牢数据

    - extract the boundary
    - determine the adjacency
    - calculate the confidence
    - complete the connection information
    - complete the door information
    - return the enhanced dungeon data
    """
    
    def __init__(self, adjacency_threshold: float = 2.5):
        """
        初始化推断引擎
        Args:
            adjacency_threshold: 邻接判定阈值，允许房间间的最小间隙
        """
        self.adjacency_threshold = adjacency_threshold
    
    def infer_connections_and_doors(self, rooms: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        基于空间邻接推断房间连接关系和自动补全门信息
        Args:
            rooms: 房间列表
        Returns:
            (推断出的连接关系列表, 推断出的门列表)
        """
        if not rooms or len(rooms) < 2:
            return [], []
        connections = []
        doors = []
        seen_pairs = set()
        for i, room_a in enumerate(rooms):
            for j, room_b in enumerate(rooms):
                if i >= j:
                    continue
                pair_key = tuple(sorted([room_a['id'], room_b['id']]))
                if pair_key in seen_pairs:
                    continue
                adjacent = self._are_rooms_adjacent(room_a, room_b)
                if adjacent:
                    # 连接 - 无向图，从room_a到room_b
                    # This is an unidirectional connection, from room_a to room_b[because the structure of some of the systems they provide the name as from_room and to_room, so i define it in this way]
                    # NOTES: the name only represent the two points, not the direction
                    connection = {
                        'from_room': room_a['id'],
                        'to_room': room_b['id'],
                        'inferred': True,
                        'connection_type': 'spatial_adjacency',
                        'confidence': self._calculate_adjacency_confidence(room_a, room_b)
                    }
                    connections.append(connection)
                    # 门
                    door = {
                        'id': f"door_{room_a['id']}_{room_b['id']}",
                        'position': self._infer_door_position(room_a, room_b),
                        'connects': [room_a['id'], room_b['id']],
                        'inferred': True
                    }
                    doors.append(door)
                    seen_pairs.add(pair_key)
        return connections, doors

    def _infer_door_position(self, room_a: Dict, room_b: Dict) -> Dict[str, float]:
        """
        推断两房间之间门的位置（取相邻边的中点）
        """
        ax1, ay1, ax2, ay2 = self._get_room_bounds(room_a)
        bx1, by1, bx2, by2 = self._get_room_bounds(room_b)
        # 取重叠部分的中点
        overlap_x1 = max(ax1, bx1)
        overlap_x2 = min(ax2, bx2)
        overlap_y1 = max(ay1, by1)
        overlap_y2 = min(ay2, by2)
        # 判断邻接方向
        if self._ranges_overlap(ay1, ay2, by1, by2):  # 水平邻接
            x = overlap_x1 if abs(ax2 - bx1) <= self.adjacency_threshold else overlap_x2
            y = (overlap_y1 + overlap_y2) / 2
        elif self._ranges_overlap(ax1, ax2, bx1, bx2):  # 垂直邻接
            y = overlap_y1 if abs(ay2 - by1) <= self.adjacency_threshold else overlap_y2
            x = (overlap_x1 + overlap_x2) / 2
        else:
            # 默认取两房间中心点的中点
            center_a_x = (ax1 + ax2) / 2
            center_a_y = (ay1 + ay2) / 2
            center_b_x = (bx1 + bx2) / 2
            center_b_y = (by1 + by2) / 2
            x = (center_a_x + center_b_x) / 2
            y = (center_a_y + center_b_y) / 2
        return {'x': x, 'y': y}

    def enhance_dungeon_data(self, dungeon_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        补全连接信息；外部调用函数
        enhance the dungeon data, automatically complete the missing connection and door information ｜ externally invoked function
        Args:
            dungeon_data: the dungeon data
        Returns:
            the enhanced dungeon data
        """
        import copy
        enhanced_data = copy.deepcopy(dungeon_data)
        for level in enhanced_data.get('levels', []):
            rooms = level.get('rooms', [])
            corridors = level.get('corridors', [])
            connections = level.get('connections', [])
            doors = level.get('doors', []) if 'doors' in level else []
            
            # 合并所有节点（房间和走廊）进行空间推断
            all_nodes = rooms + corridors
            
            # 总是进行空间推断，以补充或改进现有连接
            if len(all_nodes) > 1:
                inferred_connections, inferred_doors = self.infer_connections_and_doors(all_nodes)
                if inferred_connections:
                    # 合并现有连接和推断连接，去重
                    existing_connection_pairs = set()
                    for conn in connections:
                        pair = tuple(sorted([conn['from_room'], conn['to_room']]))
                        existing_connection_pairs.add(pair)
                    # 不再限制最大推断连接数
                    added_count = 0
                    for conn in inferred_connections:
                        pair = tuple(sorted([conn['from_room'], conn['to_room']]))
                        if pair not in existing_connection_pairs:
                            if conn.get('confidence', 0) > 0.1:
                                connections.append(conn)
                                existing_connection_pairs.add(pair)
                                added_count += 1
                    if added_count > 0:
                        level['connections'] = connections
                        level['connections_inferred'] = True
                        logger.info(f"Added {added_count} inferred connections to level {level.get('id', 'unknown')}")
                if (not doors or len(doors) == 0) and inferred_doors:
                    level['doors'] = inferred_doors
                    level['doors_inferred'] = True
                    logger.info(f"Added {len(inferred_doors)} inferred doors to level {level.get('id', 'unknown')}")
        return enhanced_data

    def _are_rooms_adjacent(self, room_a: Dict, room_b: Dict) -> bool:
        """
        判断两个房间是否足够近，边界是否在阈值内，如果两个房间的边界在阈值内，则认为两个房间邻接
        Determine whether the two rooms are close enough and whether the boundary is within the threshold, if the boundary of the two rooms is within the threshold, the two rooms are considered neighbouring
        """
        ax1, ay1, ax2, ay2 = self._get_room_bounds(room_a)
        bx1, by1, bx2, by2 = self._get_room_bounds(room_b)
        horizontally_adjacent = (
            self._ranges_overlap(ay1, ay2, by1, by2) and
            (abs(ax2 - bx1) <= self.adjacency_threshold or abs(bx2 - ax1) <= self.adjacency_threshold)
        )
        vertically_adjacent = (
            self._ranges_overlap(ax1, ax2, bx1, bx2) and
            (abs(ay2 - by1) <= self.adjacency_threshold or abs(by2 - ay1) <= self.adjacency_threshold)
        )
        return horizontally_adjacent or vertically_adjacent

    def _get_room_bounds(self, room: Dict) -> Tuple[float, float, float, float]:
        """
        获取房间或走廊的边界坐标 (x1, y1, x2, y2)
        """
        # 处理走廊（使用path字段）
        if 'path' in room:
            path = room.get('path', [])
            if not path:
                return 0, 0, 0, 0
            
            # 计算path的边界
            x_coords = [point['x'] for point in path]
            y_coords = [point['y'] for point in path]
            width = room.get('width', 1)
            
            x1 = min(x_coords) - width/2
            y1 = min(y_coords) - width/2
            x2 = max(x_coords) + width/2
            y2 = max(y_coords) + width/2
            return x1, y1, x2, y2
        
        # 处理房间（使用position和size字段）
        pos = room.get('position', {})
        size = room.get('size', {})
        x1 = pos.get('x', 0)
        y1 = pos.get('y', 0)
        x2 = x1 + size.get('width', 0)
        y2 = y1 + size.get('height', 0)
        return x1, y1, x2, y2

    def _ranges_overlap(self, a1: float, a2: float, b1: float, b2: float) -> bool:
        """
        判断两个范围是否重叠
        """
        return not (a2 <= b1 or b2 <= a1)

    def _calculate_adjacency_confidence(self, room_a: Dict, room_b: Dict) -> float:
        """
        计算邻接置信度（0-1）
        返回置信度，若有边界重叠则上浮
        """
        ax1, ay1, ax2, ay2 = self._get_room_bounds(room_a)
        bx1, by1, bx2, by2 = self._get_room_bounds(room_b)
        
        # 计算重叠区域
        overlap_x = max(0, min(ax2, bx2) - max(ax1, bx1))
        overlap_y = max(0, min(ay2, by2) - max(ay1, by1))
        overlap_area = overlap_x * overlap_y
        
        # 计算两个房间的面积
        area_a = (ax2 - ax1) * (ay2 - ay1)
        area_b = (bx2 - bx1) * (by2 - by1)
        
        # 简化置信度计算：如果房间邻接，给予基础置信度
        if self._are_rooms_adjacent(room_a, room_b):
            # 基础置信度为0.5，根据重叠程度调整
            base_confidence = 0.5
            if overlap_area > 0:
                min_area = min(area_a, area_b)
                if min_area > 0:
                    overlap_ratio = overlap_area / min_area
                    confidence = base_confidence + overlap_ratio * 0.5
                else:
                    confidence = base_confidence
            else:
                confidence = base_confidence
        else:
            confidence = 0.0
            
        return min(1.0, max(0.0, confidence))

def auto_infer_connections(dungeon_data: Dict[str, Any], threshold: float = 1.0) -> Dict[str, Any]:
    """
    自动推断连接的便捷函数
    
    Args:
        dungeon_data: 地牢数据
        threshold: 邻接阈值
        
    Returns:
        增强后的地牢数据
    """
    engine = SpatialInferenceEngine(threshold)
    return engine.enhance_dungeon_data(dungeon_data) 