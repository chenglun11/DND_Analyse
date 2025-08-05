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
        connections = level.get('connections', [])
        if not rooms or not connections:
            return 0.0, {"reason": "No rooms or connections"}

        # 构建无向图
        graph = defaultdict(list)
        for c in connections:
            u, v = c['from_room'], c['to_room']
            graph[u].append(v)
            graph[v].append(u)

        # 统一入口出口识别：使用identify_entrance_exit函数
        processed_data = identify_entrance_exit(dungeon_data)
        processed_rooms = processed_data['levels'][0]['rooms']
        
        # 获取识别出的入口和出口
        entrance = next((r['id'] for r in processed_rooms if r.get('is_entrance')), None)
        exit_room = next((r['id'] for r in processed_rooms if r.get('is_exit')), None)
        
        if not entrance or not exit_room:
            return 0.0, {"reason": "Could not identify entrance and exit"}

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