from .base import BaseQualityRule
import math
from collections import defaultdict, deque
from typing import Dict, Any, Tuple, List

class AccessibilityRule(BaseQualityRule):
    """
    客观可达性评估：无主观权重，使用几何平均融合子指标

    子指标:
      1. reachability_ratio: 最大连通子图节点占比 (0-1)
      2. normalized_avg_distance: 平均最短路径长度归一化
      3. normalized_variance: 路径长度方差归一化

    融合: 几何平均，仅使用非零因子
    """

    @property
    def name(self) -> str:
        return "accessibility"

    @property
    def description(self) -> str:
        return "Objective accessibility assessment using geometric mean fusion"

    def evaluate(self, dungeon_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        level = dungeon_data.get('levels', [])
        if not level:
            return 0.0, {"reason": "No level data"}
        rooms = level[0].get('rooms', [])
        connections = level[0].get('connections', [])
        if not rooms or not connections:
            return 0.0, {"reason": "No rooms or connections"}

        # 构建图
        graph = defaultdict(list)
        for c in connections:
            graph[c['from_room']].append(c['to_room'])
            graph[c['to_room']].append(c['from_room'])
        nodes = list(graph.keys())
        n = len(nodes)
        if n == 0:
            return 0.0, {"reason": "Empty graph"}

        # 1. 可达率: 最大连通分量 / 总节点
        visited = set()
        def bfs_count(start):
            q = deque([start])
            visited.add(start)
            cnt = 1
            while q:
                u = q.popleft()
                for v in graph[u]:
                    if v not in visited:
                        visited.add(v)
                        cnt += 1
                        q.append(v)
            return cnt
        largest = 0
        for u in nodes:
            if u not in visited:
                size = bfs_count(u)
                if size > largest:
                    largest = size
        reachability = largest / n

        # 假设入口为第一个房间
        entrance = rooms[0]['id']
        # 2. 计算从入口到所有可达节点的最短路径长度
        lengths = self._bfs_all_distances(graph, entrance)
        if not lengths:
            return 0.0, {"reason": "Entrance isolated"}
        avg_len = sum(lengths) / len(lengths)
        var_len = sum((d - avg_len)**2 for d in lengths) / len(lengths)

        # 理论最大最短路径 = 图的直径
        diameter = max(lengths)
        # 归一化平均距离: (diameter - avg_len) / diameter
        norm_avg = (diameter - avg_len) / diameter if diameter > 0 else 0.0
        # 归一化方差: 使用严格上界 Var ≤ Diam²/4（区分度更好）
        strict_upper_bound = (diameter * diameter) / 4 if diameter > 0 else 0.0
        norm_var = 1 - (var_len / strict_upper_bound if strict_upper_bound > 0 else 0.0)
        norm_var = max(0.0, min(1.0, norm_var))

        # 几何平均融合
        factors = [f for f in [reachability, norm_avg, norm_var] if f > 0]
        if factors:
            score = math.exp(sum(math.log(f) for f in factors) / len(factors))
        else:
            score = 0.0

        return score, {
            'reachability_ratio': reachability,
            'avg_path_length': avg_len,
            'path_variance': var_len,
            'normalized': [reachability, norm_avg, norm_var],
            'score': score
        }

    def _bfs_all_distances(self, graph: Dict[str, List[str]], source: Any) -> List[float]:
        """BFS 计算从 source 到所有节点的最短路径长度"""
        visited = {source}
        q = deque([(source, 0)])
        dists = []
        while q:
            u, d = q.popleft()
            dists.append(d)
            for v in graph[u]:
                if v not in visited:
                    visited.add(v)
                    q.append((v, d+1))
        return dists 