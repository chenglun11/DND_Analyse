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

        return normalized_length, {
            'raw_length': raw_length,
            'diameter': diameter,
            'normalized_length': normalized_length,
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
        降级方案：多中心径向路径聚合评估 (Multi-Center Radial Path Aggregation)
        
        优化策略：
        1. 基于度中心性的快速中心候选筛选
        2. 多中心-外围路径组合评估
        3. 自适应采样降低大图计算复杂度
        4. 加权聚合多路径结果
        
        理论基础：
        - 度中心性 (Degree Centrality): Freeman, 1978
        - 图的半径和直径: Harary, 1969
        - 多路径聚合: Bollobás, 1998
        """
        if not graph or not all_spaces:
            return None
            
        space_ids = [s['id'] for s in all_spaces if s['id'] in graph]
        if len(space_ids) < 2:
            return None
            
        try:
            # 自适应采样：大图使用采样策略降低复杂度
            num_nodes = len(space_ids)
            use_sampling = num_nodes > 50  # 超过50个节点使用采样
            
            if use_sampling:
                # 基于度中心性的快速中心候选筛选
                degree_centralities = {node: len(graph[node]) for node in space_ids}
                sorted_by_degree = sorted(degree_centralities.items(), key=lambda x: x[1], reverse=True)
                # 选择度最高的前30%节点作为候选中心
                num_candidates = max(3, min(15, num_nodes // 3))
                center_candidates = [node for node, _ in sorted_by_degree[:num_candidates]]
            else:
                center_candidates = space_ids
            
            # 1. 计算候选节点的偏心率
            eccentricities = {}
            all_distances = {}
            
            for node in center_candidates:
                distances = self._bfs_all_distances_from_node(graph, node)
                if not distances or len(distances) < 2:
                    continue
                    
                all_distances[node] = distances
                eccentricities[node] = max(distances.values())
            
            if not eccentricities:
                return None
            
            # 2. 找到多个中心节点（选择前3个最佳中心）
            min_eccentricity = min(eccentricities.values())
            center_nodes = [node for node, ecc in eccentricities.items() if ecc == min_eccentricity]
            
            # 如果只有一个真正的中心，添加次佳候选
            if len(center_nodes) == 1:
                sorted_centers = sorted(eccentricities.items(), key=lambda x: x[1])
                for node, ecc in sorted_centers[1:4]:  # 最多添加3个次佳中心
                    if ecc <= min_eccentricity + 1:  # 偏心率相差不超过1
                        center_nodes.append(node)
            
            # 限制中心节点数量
            center_nodes = center_nodes[:3]
            
            # 3. 多中心-外围路径评估
            path_results = []
            
            for center_node in center_nodes:
                center_distances = all_distances.get(center_node, {})
                if not center_distances:
                    continue
                    
                max_distance_from_center = max(center_distances.values())
                periphery_nodes = [node for node, dist in center_distances.items() 
                                 if dist == max_distance_from_center and node != center_node]
                
                # 评估多个外围节点（最多3个）
                for periphery_node in periphery_nodes[:3]:
                    path, distances = self._bfs_shortest_path(graph, center_node, periphery_node)
                    if path is not None:
                        path_length = len(path) - 1
                        weight = 1.0 / (eccentricities[center_node] + 0.1)  # 中心性越好权重越高
                        path_results.append({
                            'length': path_length,
                            'weight': weight,
                            'path': path,
                            'center': center_node,
                            'periphery': periphery_node
                        })
            
            if not path_results:
                return None
            
            # 4. 加权聚合多路径结果
            total_weight = sum(result['weight'] for result in path_results)
            weighted_avg_length = sum(result['length'] * result['weight'] for result in path_results) / total_weight
            
            # 选择最具代表性的路径（长度最接近加权平均的路径）
            best_result = min(path_results, key=lambda x: abs(x['length'] - weighted_avg_length))
            
            # 5. 计算图直径（使用已计算的偏心率）
            if use_sampling:
                # 对于大图，估算直径：使用已知的最大偏心率
                diameter = max(eccentricities.values())
            else:
                # 对于小图，计算真实直径
                diameter = max(eccentricities.values()) if eccentricities else weighted_avg_length
            
            # 6. 归一化和评分
            normalized_length = weighted_avg_length / diameter if diameter > 0 else 0.0
            score = math.exp(-2.0 * normalized_length)
            
            return score, {
                'raw_length': weighted_avg_length,
                'diameter': diameter,
                'normalized_length': normalized_length,
                'score': score,
                'path': best_result['path'],
                'center_node': best_result['center'],
                'periphery_node': best_result['periphery'],
                'center_eccentricity': min_eccentricity,
                'graph_radius': min_eccentricity,
                'fallback_method': 'multi_center_radial',
                'algorithm_variant': 'sampling' if use_sampling else 'full_computation',
                'num_centers_evaluated': len(center_nodes),
                'num_paths_evaluated': len(path_results),
                'note': f'Multi-center radial path aggregation ({len(path_results)} paths evaluated)'
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