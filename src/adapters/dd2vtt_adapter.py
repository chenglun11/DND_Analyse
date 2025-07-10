from typing import Dict, Any, Optional
from src.adapters.base import BaseAdapter
from src.schema import UnifiedDungeonFormat

import numpy as np
from collections import defaultdict

class DD2VTTAdapter(BaseAdapter):
    """适配 dd2vtt (DungeonDraft to VTT) 格式。"""
    @property
    def format_name(self) -> str:
        return "dd2vtt"

    def detect(self, data: Dict[str, Any]) -> bool:
        # dd2vtt格式通常有format字段和resolution字段
        return (
            isinstance(data, dict)
            and "format" in data
            and "resolution" in data
            and "line_of_sight" in data
        )

    def convert(self, data: Dict[str, Any]) -> Optional[UnifiedDungeonFormat]:
        try:
            res = data.get("resolution", {})
            map_size = res.get("map_size", {"x": 0, "y": 0})
            grid_size = res.get("pixels_per_grid", 70)
            name = data.get("name", "DD2VTT Dungeon")
            
            unified = UnifiedDungeonFormat(
                name=name,
                author="dd2vtt",
                description="Converted from dd2vtt format",
                grid={"type": "square", "size": grid_size, "unit": "px"}
            )

            # 门
            doors = []
            for i, door in enumerate(data.get("doors", [])):
                doors.append({
                    "id": f"door_{i}",
                    "position": {"x": door.get("x"), "y": door.get("y")},
                    "dir": door.get("dir"),
                    "type": door.get("type")
                })

            # 墙体/可视线
            walls = []
            wall_segments = []
            for i, seg in enumerate(data.get("line_of_sight", [])):
                if len(seg) == 2:
                    walls.append({
                        "id": f"wall_{i}",
                        "from": seg[0],
                        "to": seg[1]
                    })
                    # 修正：明确取x,y坐标
                    p1 = (seg[0]["x"], seg[0]["y"])
                    p2 = (seg[1]["x"], seg[1]["y"])
                    wall_segments.append((p1, p2))

            print(f"处理了 {len(wall_segments)} 个墙段")
            
            # --- 基于端点的房间推断 ---
            rooms = self._infer_rooms_from_endpoints(wall_segments, map_size)
            
            # --- 走廊推断 ---
            corridors = self._infer_corridors(wall_segments, map_size)

            # 可选：lights
            lights = data.get("lights", [])

            unified.levels.append({
                "id": "level_1",
                "name": "Main Level",
                "map": {"width": map_size.get("x", 0), "height": map_size.get("y", 0)},
                "rooms": rooms,
                "corridors": corridors,
                "doors": doors,
                "walls": walls,
                "lights": lights
            })
            return unified
        except Exception as e:
            import logging
            logging.error(f"Error converting dd2vtt: {e}")
            return None

    def _infer_rooms_from_endpoints(self, wall_segments, map_size):
        """
        基于墙段端点的房间推断：
        1. 收集所有墙段端点
        2. 使用DBSCAN聚类找到密集区域
        3. 为每个聚类创建房间
        """
        if not wall_segments:
            print("没有墙段数据，创建默认房间")
            return self._create_default_rooms(map_size)
            
        print(f"使用端点聚类推断房间，墙段数量: {len(wall_segments)}")
        
        # 1. 收集所有端点
        all_points = []
        for p1, p2 in wall_segments:
            all_points.append(p1)
            all_points.append(p2)
        
        if len(all_points) < 4:
            return self._infer_rooms_simple(wall_segments, map_size)
        
        # 转换为numpy数组
        points_array = np.array(all_points)
        
        # 2. 使用简单的距离聚类
        clusters = self._simple_clustering(points_array, eps=10.0)
        
        print(f"找到 {len(clusters)} 个端点聚类")
        
        # 3. 为每个聚类创建房间
        rooms = []
        for i, cluster_points in enumerate(clusters):
            if len(cluster_points) < 3:  # 过滤太小的聚类
                continue
                
            # 计算聚类的边界框
            xs = [p[0] for p in cluster_points]
            ys = [p[1] for p in cluster_points]
            
            x_min, x_max = min(xs), max(xs)
            y_min, y_max = min(ys), max(ys)
            
            width = x_max - x_min
            height = y_max - y_min
            
            # 扩展房间边界，确保包含相关墙段
            padding = 5.0
            x_min -= padding
            y_min -= padding
            width += 2 * padding
            height += 2 * padding
            
            if width > 3 and height > 3:  # 过滤太小的房间
                rooms.append({
                    "id": f"room_{i}",
                    "x": x_min,
                    "y": y_min,
                    "width": width,
                    "height": height,
                    "name": f"Room {i+1}"
                })
        
        # 如果没有找到房间，使用备用方法
        if not rooms:
            print("端点聚类失败，使用备用方法")
            return self._infer_rooms_simple(wall_segments, map_size)
        
        print(f"端点聚类创建了 {len(rooms)} 个房间")
        return rooms
    
    def _simple_clustering(self, points, eps=10.0):
        """
        简单的距离聚类算法
        """
        if len(points) == 0:
            return []
        
        clusters = []
        visited = set()
        
        for i, point in enumerate(points):
            if i in visited:
                continue
                
            # 开始新的聚类
            cluster = [point]
            visited.add(i)
            
            # 寻找附近的点
            changed = True
            while changed:
                changed = False
                for j, other_point in enumerate(points):
                    if j in visited:
                        continue
                    
                    # 检查是否与聚类中的任何点足够近
                    for cluster_point in cluster:
                        distance = np.sqrt((other_point[0] - cluster_point[0])**2 + 
                                         (other_point[1] - cluster_point[1])**2)
                        if distance <= eps:
                            cluster.append(other_point)
                            visited.add(j)
                            changed = True
                            break
                    if changed:
                        break
            
            clusters.append(cluster)
        
        return clusters
    
    def _infer_rooms_simple(self, wall_segments, map_size):
        """
        简单的房间推断：基于地图尺寸创建占位房间
        """
        if not wall_segments:
            print("没有墙段数据，创建默认房间")
            return self._create_default_rooms(map_size)
            
        print(f"使用简单房间推断，地图尺寸: {map_size}")
        
        # 计算地图边界
        all_x = []
        all_y = []
        for p1, p2 in wall_segments:
            all_x.extend([p1[0], p2[0]])
            all_y.extend([p1[1], p2[1]])
            
        if not all_x or not all_y:
            return self._create_default_rooms(map_size)
            
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        
        print(f"墙段边界: ({min_x:.1f}, {min_y:.1f}) 到 ({max_x:.1f}, {max_y:.1f})")
        
        # 创建几个大房间覆盖地图区域
        rooms = []
        room_width = (max_x - min_x) / 3
        room_height = (max_y - min_y) / 3
        
        if room_width < 5 or room_height < 5:
            # 如果区域太小，创建单个房间
            rooms.append({
                "id": "room_0",
                "x": min_x,
                "y": min_y,
                "width": max_x - min_x,
                "height": max_y - min_y,
                "name": "Main Area"
            })
        else:
            # 创建3x3网格房间
            for i in range(3):
                for j in range(3):
                    x = min_x + i * room_width
                    y = min_y + j * room_height
                    rooms.append({
                        "id": f"room_{i*3+j}",
                        "x": x,
                        "y": y,
                        "width": room_width,
                        "height": room_height,
                        "name": f"Area {i*3+j+1}"
                    })
        
        print(f"创建了 {len(rooms)} 个房间")
        return rooms
    
    def _create_default_rooms(self, map_size):
        """创建默认房间"""
        width = map_size.get("x", 100)
        height = map_size.get("y", 100)
        
        return [{
            "id": "room_0",
            "x": 0,
            "y": 0,
            "width": width,
            "height": height,
            "name": "Main Dungeon"
        }]

    def _infer_corridors(self, wall_segments, map_size):
        """
        基于墙体推断走廊：
        1. 分析墙体之间的空间
        2. 识别长而窄的通道
        3. 连接房间之间的路径
        """
        if not wall_segments:
            print("没有墙段数据，无法推断走廊")
            return []
            
        print(f"推断走廊，墙段数量: {len(wall_segments)}")
        
        # 首先获取房间信息（如果还没有房间，先创建）
        rooms = self._infer_rooms_from_endpoints(wall_segments, map_size)
        
        corridors = []
        
        # 方法1：基于房间之间的连接空间识别走廊
        room_connections = self._find_corridors_between_rooms(rooms, wall_segments)
        
        # 方法2：基于墙体密度低的区域识别走廊
        density_corridors = self._find_corridors_by_density(wall_segments, rooms)
        
        # 方法3：添加缺失的重要连接
        missing_connections = self._add_missing_connections(rooms, wall_segments)
        
        # 合并结果
        all_corridors = room_connections + density_corridors + missing_connections
        
        # 去重和过滤
        unique_corridors = self._deduplicate_corridors(all_corridors)
        
        # 过滤掉与房间重叠的走廊
        filtered_corridors = self._filter_overlapping_corridors(unique_corridors, rooms)
        
        # 为每个走廊分配ID
        for i, corridor in enumerate(filtered_corridors):
            corridor["id"] = f"corridor_{i}"
            corridor["name"] = f"Corridor {i}"
            corridors.append(corridor)
        
        print(f"推断出 {len(corridors)} 个走廊")
        return corridors
    
    def _find_corridors_between_rooms(self, rooms, wall_segments):
        """基于房间之间的连接空间识别走廊"""
        corridors = []
        
        if len(rooms) < 2:
            return corridors
        
        # 分析每对房间之间的空间
        for i, room1 in enumerate(rooms):
            for j, room2 in enumerate(rooms[i+1:], i+1):
                # 计算房间之间的距离
                distance = self._distance_between_rooms(room1, room2)
                
                if 5.0 <= distance <= 30.0:  # 合理的房间间距
                    # 检查两个房间之间是否有连接空间
                    corridor = self._create_corridor_between_rooms(room1, room2, wall_segments)
                    if corridor:
                        corridors.append(corridor)
        
        return corridors
    
    def _distance_between_rooms(self, room1, room2):
        """计算两个房间中心点之间的距离"""
        center1_x = room1['x'] + room1['width'] / 2
        center1_y = room1['y'] + room1['height'] / 2
        center2_x = room2['x'] + room2['width'] / 2
        center2_y = room2['y'] + room2['height'] / 2
        
        return np.sqrt((center1_x - center2_x)**2 + (center1_y - center2_y)**2)
    
    def _create_corridor_between_rooms(self, room1, room2, wall_segments):
        """在两个房间之间创建走廊"""
        # 计算房间的边界
        room1_min_x, room1_max_x = room1['x'], room1['x'] + room1['width']
        room1_min_y, room1_max_y = room1['y'], room1['y'] + room1['height']
        room2_min_x, room2_max_x = room2['x'], room2['x'] + room2['width']
        room2_min_y, room2_max_y = room2['y'], room2['y'] + room2['height']
        
        # 计算连接区域
        corridor_min_x = max(room1_min_x, room2_min_x)
        corridor_max_x = min(room1_max_x, room2_max_x)
        corridor_min_y = max(room1_min_y, room2_min_y)
        corridor_max_y = min(room1_max_y, room2_max_y)
        
        # 如果房间在x方向有重叠，创建垂直走廊
        if corridor_max_x > corridor_min_x:
            corridor_width = corridor_max_x - corridor_min_x
            corridor_height = 3.0  # 标准走廊宽度
            corridor_x = corridor_min_x
            corridor_y = (room1_max_y + room2_min_y) / 2 - corridor_height / 2
            
            # 检查这个区域是否被墙体占据
            if not self._is_area_blocked_by_walls(corridor_x, corridor_y, corridor_width, corridor_height, wall_segments):
                return {
                    "x": corridor_x,
                    "y": corridor_y,
                    "width": corridor_width,
                    "height": corridor_height
                }
        
        # 如果房间在y方向有重叠，创建水平走廊
        if corridor_max_y > corridor_min_y:
            corridor_width = 3.0  # 标准走廊宽度
            corridor_height = corridor_max_y - corridor_min_y
            corridor_x = (room1_max_x + room2_min_x) / 2 - corridor_width / 2
            corridor_y = corridor_min_y
            
            # 检查这个区域是否被墙体占据
            if not self._is_area_blocked_by_walls(corridor_x, corridor_y, corridor_width, corridor_height, wall_segments):
                return {
                    "x": corridor_x,
                    "y": corridor_y,
                    "width": corridor_width,
                    "height": corridor_height
                }
        
        return None
    
    def _is_area_blocked_by_walls(self, x, y, width, height, wall_segments):
        """检查区域是否被墙体占据"""
        area_center_x = x + width / 2
        area_center_y = y + height / 2
        
        for p1, p2 in wall_segments:
            # 检查墙体是否穿过走廊区域
            wall_center_x = (p1[0] + p2[0]) / 2
            wall_center_y = (p1[1] + p2[1]) / 2
            
            # 计算墙体到走廊中心的距离
            distance = np.sqrt((wall_center_x - area_center_x)**2 + (wall_center_y - area_center_y)**2)
            
            if distance < max(width, height) / 2:
                return True
        
        return False
    
    def _find_corridors_by_density(self, wall_segments, rooms):
        """基于墙体密度识别走廊"""
        corridors = []
        
        # 创建墙体密度图
        density_map = self._create_density_map(wall_segments, grid_size=3.0)
        
        # 找到低密度区域
        low_density_areas = self._find_low_density_areas(density_map, threshold=0)
        
        # 过滤掉与房间重叠的区域
        for area in low_density_areas:
            if area['width'] > 2 and area['height'] > 2:  # 最小尺寸
                # 检查是否与任何房间重叠
                overlaps_with_room = False
                for room in rooms:
                    if self._rectangles_overlap(area, room):
                        overlaps_with_room = True
                        break
                
                if not overlaps_with_room:
                    corridors.append(area)
        
        return corridors
    
    def _rectangles_overlap(self, rect1, rect2):
        """检查两个矩形是否重叠"""
        x1_min, x1_max = rect1['x'], rect1['x'] + rect1['width']
        y1_min, y1_max = rect1['y'], rect1['y'] + rect1['height']
        
        x2_min, x2_max = rect2['x'], rect2['x'] + rect2['width']
        y2_min, y2_max = rect2['y'], rect2['y'] + rect2['height']
        
        return not (x1_max < x2_min or x2_max < x1_min or y1_max < y2_min or y2_max < y1_min)
    
    def _filter_overlapping_corridors(self, corridors, rooms):
        """过滤掉与房间重叠的走廊"""
        filtered_corridors = []
        
        for corridor in corridors:
            overlaps_with_room = False
            
            for room in rooms:
                if self._rectangles_overlap(corridor, room):
                    overlaps_with_room = True
                    break
            
            if not overlaps_with_room:
                filtered_corridors.append(corridor)
        
        return filtered_corridors
    
    def _create_density_map(self, wall_segments, grid_size=5.0):
        """创建墙体密度图"""
        if not wall_segments:
            return {}
        
        # 计算地图边界
        all_x = []
        all_y = []
        for p1, p2 in wall_segments:
            all_x.extend([p1[0], p2[0]])
            all_y.extend([p1[1], p2[1]])
        
        if not all_x or not all_y:
            return {}
        
        x_min, x_max = min(all_x), max(all_x)
        y_min, y_max = min(all_y), max(all_y)
        
        # 创建网格
        density_map = {}
        for x in np.arange(x_min, x_max + grid_size, grid_size):
            for y in np.arange(y_min, y_max + grid_size, grid_size):
                grid_key = (int(x/grid_size), int(y/grid_size))
                density_map[grid_key] = 0
        
        # 计算每个网格的墙体密度
        for p1, p2 in wall_segments:
            # 简化的密度计算
            mid_x = (p1[0] + p2[0]) / 2
            mid_y = (p1[1] + p2[1]) / 2
            grid_x = int(mid_x / grid_size)
            grid_y = int(mid_y / grid_size)
            grid_key = (grid_x, grid_y)
            
            if grid_key in density_map:
                density_map[grid_key] += 1
        
        return density_map
    
    def _find_low_density_areas(self, density_map, threshold=1):
        """找到低密度区域作为走廊候选"""
        areas = []
        
        if not density_map:
            return areas
        
        # 找到密度低于阈值的网格
        low_density_grids = []
        for grid_key, density in density_map.items():
            if density <= threshold:
                low_density_grids.append(grid_key)
        
        # 聚类相邻的低密度网格
        clusters = self._cluster_adjacent_grids(low_density_grids)
        
        # 为每个聚类创建走廊区域
        for cluster in clusters:
            if len(cluster) >= 2:  # 至少2个网格
                area = self._create_area_from_grid_cluster(cluster)
                if area:
                    areas.append(area)
        
        return areas
    
    def _cluster_adjacent_grids(self, grids):
        """聚类相邻的网格"""
        if not grids:
            return []
        
        clusters = []
        visited = set()
        
        for grid in grids:
            if grid in visited:
                continue
            
            # 开始新的聚类
            cluster = [grid]
            visited.add(grid)
            
            # 寻找相邻的网格
            changed = True
            while changed:
                changed = False
                for other_grid in grids:
                    if other_grid in visited:
                        continue
                    
                    # 检查是否与聚类中的任何网格相邻
                    for cluster_grid in cluster:
                        if self._are_grids_adjacent(cluster_grid, other_grid):
                            cluster.append(other_grid)
                            visited.add(other_grid)
                            changed = True
                            break
                    if changed:
                        break
            
            clusters.append(cluster)
        
        return clusters
    
    def _are_grids_adjacent(self, grid1, grid2):
        """检查两个网格是否相邻"""
        x1, y1 = grid1
        x2, y2 = grid2
        return abs(x1 - x2) <= 1 and abs(y1 - y2) <= 1
    
    def _create_area_from_grid_cluster(self, cluster, grid_size=5.0):
        """从网格聚类创建区域"""
        if not cluster:
            return None
        
        # 计算聚类的边界
        xs = [grid[0] * grid_size for grid in cluster]
        ys = [grid[1] * grid_size for grid in cluster]
        
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        
        width = x_max - x_min + grid_size
        height = y_max - y_min + grid_size
        
        return {
            "x": x_min,
            "y": y_min,
            "width": width,
            "height": height
        }
    
    def _deduplicate_corridors(self, corridors):
        """去重走廊"""
        if not corridors:
            return []
        
        unique_corridors = []
        for corridor in corridors:
            is_duplicate = False
            for existing in unique_corridors:
                if self._corridors_overlap(corridor, existing):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_corridors.append(corridor)
        
        return unique_corridors
    
    def _corridors_overlap(self, corridor1, corridor2, threshold=0.5):
        """检查两个走廊是否重叠"""
        # 计算重叠面积
        x1_min, x1_max = corridor1['x'], corridor1['x'] + corridor1['width']
        y1_min, y1_max = corridor1['y'], corridor1['y'] + corridor1['height']
        
        x2_min, x2_max = corridor2['x'], corridor2['x'] + corridor2['width']
        y2_min, y2_max = corridor2['y'], corridor2['y'] + corridor2['height']
        
        # 计算重叠区域
        x_overlap = max(0, min(x1_max, x2_max) - max(x1_min, x2_min))
        y_overlap = max(0, min(y1_max, y2_max) - max(y1_min, y2_min))
        
        overlap_area = x_overlap * y_overlap
        area1 = corridor1['width'] * corridor1['height']
        area2 = corridor2['width'] * corridor2['height']
        
        # 如果重叠面积超过任一走廊面积的50%，认为是重复
        return overlap_area > threshold * min(area1, area2)

    def _add_missing_connections(self, rooms, wall_segments):
        """添加缺失的重要连接"""
        corridors = []
        
        # 计算所有房间对之间的距离
        room_pairs = []
        for i, room1 in enumerate(rooms):
            for j, room2 in enumerate(rooms[i+1:], i+1):
                distance = self._distance_between_rooms(room1, room2)
                room_pairs.append((room1, room2, distance))
        
        # 按距离排序，优先连接近距离的房间
        room_pairs.sort(key=lambda x: x[2])
        
        # 检查每个房间的连接度
        room_connections = {}
        for room in rooms:
            room_connections[room['id']] = 0
        
        # 统计现有连接
        existing_connections = self._count_existing_connections(rooms, wall_segments)
        for room1_id, room2_id in existing_connections:
            room_connections[room1_id] += 1
            room_connections[room2_id] += 1
        
        # 找出孤立的房间
        isolated_rooms = [room_id for room_id, count in room_connections.items() if count == 0]
        print(f"发现 {len(isolated_rooms)} 个孤立房间: {isolated_rooms}")
        
        # 为孤立房间添加连接
        added_connections = 0
        for room_pair in room_pairs:
            room1, room2, distance = room_pair
            
            # 如果距离太远，跳过
            if distance > 30:
                continue
            
            # 检查是否已经有连接
            if self._rooms_already_connected(room1, room2, wall_segments):
                continue
            
            # 优先连接孤立房间
            room1_isolated = room_connections[room1['id']] == 0
            room2_isolated = room_connections[room2['id']] == 0
            
            # 更积极的连接策略
            should_connect = (
                room1_isolated or 
                room2_isolated or 
                distance < 20 or
                (room_connections[room1['id']] < 2 and room_connections[room2['id']] < 2)
            )
            
            if should_connect:
                corridor = self._create_direct_corridor(room1, room2, wall_segments)
                if corridor:
                    corridors.append(corridor)
                    room_connections[room1['id']] += 1
                    room_connections[room2['id']] += 1
                    added_connections += 1
                    print(f"添加连接: {room1['name']} <-> {room2['name']} (距离: {distance:.2f})")
                    
                    # 限制添加的连接数量，避免过度连接
                    if added_connections >= 10:
                        break
        
        print(f"总共添加了 {added_connections} 个新连接")
        return corridors
    
    def _count_existing_connections(self, rooms, wall_segments):
        """统计现有的房间连接"""
        connections = []
        
        for i, room1 in enumerate(rooms):
            for j, room2 in enumerate(rooms[i+1:], i+1):
                if self._rooms_already_connected(room1, room2, wall_segments):
                    connections.append((room1['id'], room2['id']))
        
        return connections
    
    def _rooms_already_connected(self, room1, room2, wall_segments):
        """检查两个房间是否已经有连接"""
        # 检查是否有走廊连接这两个房间
        existing_corridors = self._find_corridors_between_rooms([room1, room2], wall_segments)
        
        # 也检查密度方法是否已经创建了连接
        density_corridors = self._find_corridors_by_density(wall_segments, [room1, room2])
        
        return len(existing_corridors) > 0 or len(density_corridors) > 0
    
    def _create_direct_corridor(self, room1, room2, wall_segments):
        """在两个房间之间创建直接走廊"""
        # 计算房间中心点
        center1_x = room1['x'] + room1['width'] / 2
        center1_y = room1['y'] + room1['height'] / 2
        center2_x = room2['x'] + room2['width'] / 2
        center2_y = room2['y'] + room2['height'] / 2
        
        # 计算走廊方向
        dx = center2_x - center1_x
        dy = center2_y - center1_y
        
        # 选择主要方向
        if abs(dx) > abs(dy):
            # 水平走廊
            corridor_width = 3.0
            corridor_height = min(abs(dy), 8.0)  # 限制高度
            corridor_x = min(center1_x, center2_x) - corridor_width / 2
            corridor_y = (center1_y + center2_y) / 2 - corridor_height / 2
        else:
            # 垂直走廊
            corridor_width = min(abs(dx), 8.0)  # 限制宽度
            corridor_height = 3.0
            corridor_x = (center1_x + center2_x) / 2 - corridor_width / 2
            corridor_y = min(center1_y, center2_y) - corridor_height / 2
        
        # 检查是否被墙体阻挡
        if self._is_area_blocked_by_walls(corridor_x, corridor_y, corridor_width, corridor_height, wall_segments):
            return None
        
        return {
            "x": corridor_x,
            "y": corridor_y,
            "width": corridor_width,
            "height": corridor_height
        }

        
