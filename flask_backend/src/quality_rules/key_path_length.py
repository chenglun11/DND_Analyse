from .base import BaseQualityRule
import math
from collections import deque, defaultdict
from typing import Dict, Any, List, Tuple

class KeyPathLengthRule(BaseQualityRule):
    """
    Key path length assessment: 评估从入口到关键目标（如出口/Boss房）的最短路径长度
    
    子指标:
      1. raw_length: BFS最短路径长度
      2. normalized_length: 相对于图直径的归一化长度 (0-1)
      3. branch_factor: 路径上分支节点比例，衡量路径的直线性 (0-1)

    融合: 几何平均，仅使用非零因子，完全无主观权重
    """
    
    @property
    def name(self) -> str:
        return "key_path_length"

    @property
    def description(self) -> str:
        return "Objective key path length using geometric mean fusion"

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

        # 确定入口和关键目标（假设rooms中有标记）
        entrance = next((r['id'] for r in rooms if r.get('type')=='entrance'), rooms[0]['id'])
        exit_room = next((r['id'] for r in rooms if r.get('type')=='exit'), rooms[-1]['id'])

        # 1. 计算最短路径长度
        path, lengths_map = self._bfs_shortest_path(graph, entrance, exit_room)
        if path is None:
            return 0.0, {"reason": "No path from entrance to exit"}
        raw_len = len(path)-1

        # 2. 图直径估计
        diameter = max(lengths_map.values()) if lengths_map else raw_len

        # 3. 计算路径分支因子（平均分支度数/最大度数）
        branch_counts = [len(graph[node]) - 2 for node in path[1:-1]]  # 去除入口出口
        # 分支因子 = 1 - (非直线节点比例)
        branched = sum(1 for b in branch_counts if b>0)
        node_count = len(branch_counts)
        branch_factor = 1 - (branched/node_count) if node_count>0 else 1.0

        # 4. 归一化
        norm_len = raw_len/diameter if diameter>0 else 0.0

        # 5. 几何平均融合
        factors = [f for f in [norm_len, branch_factor] if f>0]
        score = math.exp(sum(math.log(f) for f in factors)/len(factors)) if factors else 0.0

        return score, {
            'raw_length': raw_len,
            'diameter': diameter,
            'normalized_length': norm_len,
            'branch_factor': branch_factor,
            'score': score,
            'path': path
        }

    def _bfs_shortest_path(self, graph: Dict[Any,List[Any]], start: Any, goal: Any) -> Tuple[List[Any] | None, Dict[Any,int]]:
        """BFS获取从start到goal的最短路径和全图最短距离映射"""
        visited = {start}
        queue = deque([(start, [start])])
        distances = {start:0}

        while queue:
            node, path = queue.popleft()
            for nbr in graph[node]:
                if nbr not in visited:
                    visited.add(nbr)
                    distances[nbr] = distances[node] + 1
                    new_path = path+[nbr]
                    if nbr == goal:
                        # 填充后续距离为图直径计算使用
                        self._fill_remaining_distances(graph, distances)
                        return new_path, distances
                    queue.append((nbr, new_path))
        return None, distances

    def _fill_remaining_distances(self, graph: Dict[Any,List[Any]], distances: Dict[Any,int]) -> None:
        """BFS从已访问节点继续计算其他节点距离"""
        queue = deque(distances.items())
        visited = set(distances.keys())
        while queue:
            node, d = queue.popleft()
            for nbr in graph[node]:
                if nbr not in visited:
                    visited.add(nbr)
                    distances[nbr] = d+1
                    queue.append((nbr, d+1)) 