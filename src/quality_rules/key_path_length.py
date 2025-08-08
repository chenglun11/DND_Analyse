from .base import BaseQualityRule
import math
from collections import deque, defaultdict
from typing import Dict, Any, List, Tuple
from ..schema import identify_entrance_exit

class KeyPathLengthRule(BaseQualityRule):
    """
    Key path length assessment: 评估从入口到出口的最短路径长度
    
    核心指标:
      1. raw_length: BFS最短路径长度
      2. diameter: 图直径（从入口到所有节点的最大距离）
      3. normalized_length: 相对于图直径的归一化长度 L_key_hat = L_key / Diam(G)
    
    理论基础:
    - 基于图论中的最短路径理论
    - 图直径定义参考: Watts & Strogatz, 1998
    - 归一化确保指标在不同规模地图间的可比性
    
    算法特点:
    - 使用BFS确保只计算entrance到exit的最短路径
    - 从entrance对全图做BFS计算直径
    - 完全客观，无主观权重
    """
    
    @property
    def name(self) -> str:
        return "key_path_length"

    @property
    def description(self) -> str:
        return "Objective key path length using normalized length relative to graph diameter"

    def evaluate(self, dungeon_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        levels = dungeon_data.get('levels', [])
        if not levels:
            return 0.0, {"reason": "No level data"}
        level = levels[0]

        rooms = level.get('rooms', [])
        corridors = level.get('corridors', [])
        connections = level.get('connections', [])
        if not rooms or not connections:
            return 0.0, {"reason": "No rooms or connections"}

        # 构建无向图（包含房间和走廊，排除游戏元素）
        # 将房间和走廊都视为图中的节点，因为它们都是可以穿越的空间
        all_spaces = rooms + corridors
        space_ids = {space['id'] for space in all_spaces}
        graph = defaultdict(list)
        for c in connections:
            u, v = c.get('from_room'), c.get('to_room')
            # 添加空间（房间+走廊）间的连接，排除游戏元素
            if u in space_ids and v in space_ids:
                graph[u].append(v)
                graph[v].append(u)

        # 统一入口出口识别：使用identify_entrance_exit函数
        processed_data = identify_entrance_exit(dungeon_data)
        processed_rooms = processed_data['levels'][0]['rooms']
        
        # 获取识别出的入口和出口
        entrance = next((r['id'] for r in processed_rooms if r.get('is_entrance')), None)
        exit_room = next((r['id'] for r in processed_rooms if r.get('is_exit')), None)
        
        if not entrance or not exit_room:
            # 降级方案：使用最中心路径 (Center Path Fallback)
            center_path_result = self._evaluate_center_path(graph, all_spaces)
            if center_path_result is not None:
                return center_path_result
            return 0.0, {"reason": "Could not identify entrance and exit, and center path fallback failed"}

        # 1. 计算从入口到出口的最短路径长度
        path, distances = self._bfs_shortest_path(graph, entrance, exit_room)
        if path is None:
            return 0.0, {"reason": "No path from entrance to exit"}
        
        raw_length = len(path) - 1  # 路径长度 = 节点数 - 1

        # 2. 计算图直径：从入口到所有节点的最大距离
        # 使用BFS从入口计算到所有节点的距离，取最大值
        diameter = max(distances.values()) if distances else raw_length

        # 3. 计算归一化长度
        normalized_length = raw_length / diameter if diameter > 0 else 0.0

        # 评分: 关键路径长度越短越好
        # 使用指数衰减函数，避免极端情况下的0分
        # 当normalized_length = 1.0时（最差情况），score ≈ 0.135
        # 当normalized_length = 0.0时（最好情况），score = 1.0
        score = math.exp(-2.0 * normalized_length)

        return score, {
            'raw_length': raw_length,
            'diameter': diameter,
            'normalized_length': normalized_length,
            'score': score,
            'path': path,
            'entrance': entrance,
            'exit': exit_room
        }

    def _bfs_shortest_path(self, graph: Dict[Any, List[Any]], start: Any, goal: Any) -> Tuple[List[Any] | None, Dict[Any, int]]:
        """
        BFS获取从start到goal的最短路径和全图最短距离映射
        
        Args:
            graph: 无向图
            start: 起始节点
            goal: 目标节点
            
        Returns:
            (path, distances): 最短路径和从start到所有节点的距离映射
        """
        visited = {start}
        queue = deque([(start, [start])])
        distances = {start: 0}

        while queue:
            node, path = queue.popleft()
            for nbr in graph[node]:
                if nbr not in visited:
                    visited.add(nbr)
                    distances[nbr] = distances[node] + 1
                    new_path = path + [nbr]
                    if nbr == goal:
                        # 继续BFS以计算到所有节点的距离（用于直径计算）
                        self._fill_remaining_distances(graph, distances)
                        return new_path, distances
                    queue.append((nbr, new_path))
        
        # 如果没有找到路径，仍然返回距离映射
        self._fill_remaining_distances(graph, distances)
        return None, distances

    def _fill_remaining_distances(self, graph: Dict[Any, List[Any]], distances: Dict[Any, int]) -> None:
        """
        BFS从已访问节点继续计算其他节点距离
        
        Args:
            graph: 无向图
            distances: 已有的距离映射
        """
        queue = deque(distances.items())
        visited = set(distances.keys())
        
        while queue:
            node, d = queue.popleft()
            for nbr in graph[node]:
                if nbr not in visited:
                    visited.add(nbr)
                    distances[nbr] = d + 1
                    queue.append((nbr, d + 1))

    def _evaluate_center_path(self, graph: Dict[str, List[str]], all_spaces: List[Dict[str, Any]]) -> Tuple[float, Dict[str, Any]] | None:
        """
        降级方案：使用最中心路径评估
        
        策略：
        1. 计算图的中心节点（最小化到其他所有节点的最大距离）
        2. 找到图的外围节点（距离中心最远的节点）
        3. 计算从中心到外围的最长路径作为"关键路径"
        
        理论基础：
        - 中心性 (Centrality): Freeman, 1978
        - 图的半径和直径: Harary, 1969
        """
        if not graph or not all_spaces:
            return None
            
        space_ids = [s['id'] for s in all_spaces if s['id'] in graph]
        if len(space_ids) < 2:
            return None
            
        try:
            # 1. 计算每个节点的偏心率 (eccentricity)
            # 偏心率 = 从该节点到其他所有节点的最大最短距离
            eccentricities = {}
            all_distances = {}
            
            for node in space_ids:
                distances = self._bfs_all_distances_from_node(graph, node)
                if not distances or len(distances) < 2:
                    continue
                    
                all_distances[node] = distances
                # 偏心率 = 最大距离
                eccentricities[node] = max(distances.values())
            
            if not eccentricities:
                return None
                
            # 2. 找到中心节点（最小偏心率）
            min_eccentricity = min(eccentricities.values())
            center_nodes = [node for node, ecc in eccentricities.items() if ecc == min_eccentricity]
            center_node = center_nodes[0]  # 如果有多个中心，选择第一个
            
            # 3. 找到外围节点（距离中心最远的节点）
            center_distances = all_distances[center_node]
            max_distance_from_center = max(center_distances.values())
            periphery_nodes = [node for node, dist in center_distances.items() 
                             if dist == max_distance_from_center and node != center_node]
            
            if not periphery_nodes:
                return None
                
            periphery_node = periphery_nodes[0]  # 选择第一个外围节点
            
            # 4. 计算中心路径
            path, distances = self._bfs_shortest_path(graph, center_node, periphery_node)
            if path is None:
                return None
                
            raw_length = len(path) - 1
            
            # 5. 计算图的真实直径（所有节点对之间的最大最短距离）
            diameter = max(eccentricities.values())
            
            # 6. 归一化长度
            normalized_length = raw_length / diameter if diameter > 0 else 0.0
            
            # 7. 评分（使用与主路径相同的评分函数）
            score = math.exp(-2.0 * normalized_length)
            
            return score, {
                'raw_length': raw_length,
                'diameter': diameter,
                'normalized_length': normalized_length,
                'score': score,
                'path': path,
                'center_node': center_node,
                'periphery_node': periphery_node,
                'center_eccentricity': min_eccentricity,
                'graph_radius': min_eccentricity,  # 图的半径 = 最小偏心率
                'fallback_method': 'center_path',
                'note': 'Used center path fallback due to unidentifiable entrance/exit'
            }
            
        except Exception as e:
            # 如果中心路径计算失败，返回None让主函数返回0分
            return None
    
    def _bfs_all_distances_from_node(self, graph: Dict[str, List[str]], source: str) -> Dict[str, int]:
        """
        从指定节点计算到所有其他节点的最短距离
        
        Args:
            graph: 无向图
            source: 起始节点
            
        Returns:
            从source到所有可达节点的距离映射
        """
        if source not in graph:
            return {}
            
        visited = {source}
        queue = deque([(source, 0)])
        distances = {source: 0}
        
        while queue:
            node, dist = queue.popleft()
            for neighbor in graph[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    distances[neighbor] = dist + 1
                    queue.append((neighbor, dist + 1))
        
        return distances 