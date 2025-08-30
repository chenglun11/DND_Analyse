from .base import BaseQualityRule
import math
from collections import defaultdict, deque
from typing import Dict, Any, Tuple, List

class AccessibilityRule(BaseQualityRule):
    """
    Objective accessibility assessment: no subjective weights, using geometric mean to fuse sub-indicators

    Sub-indicators:
      1. reachability_ratio: Maximum connected subgraph node ratio (0-1)
      2. normalized_avg_distance: Normalized average shortest path length
      3. normalized_variance: Normalized path length variance

    Fusion: Geometric mean, using only non-zero factors
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

        # Build graph
        graph = defaultdict(list)
        for c in connections:
            graph[c['from_room']].append(c['to_room'])
            graph[c['to_room']].append(c['from_room'])
        nodes = list(graph.keys())
        n = len(nodes)
        if n == 0:
            return 0.0, {"reason": "Empty graph"}

        # 1. Reachability ratio: largest connected component / total nodes
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

        # Assume entrance is the first room
        entrance = rooms[0]['id']
        # 2. Calculate shortest path lengths from entrance to all reachable nodes
        lengths = self._bfs_all_distances(graph, entrance)
        if not lengths:
            return 0.0, {"reason": "Entrance isolated"}
        avg_len = sum(lengths) / len(lengths)
        var_len = sum((d - avg_len)**2 for d in lengths) / len(lengths)

        # Theoretical maximum shortest path = graph diameter
        diameter = max(lengths)
        # Normalized average distance: (diameter - avg_len) / diameter
        norm_avg = (diameter - avg_len) / diameter if diameter > 0 else 0.0
        # Normalized variance: use strict upper bound Var ≤ Diam²/4 (better discrimination)
        strict_upper_bound = (diameter * diameter) / 4 if diameter > 0 else 0.0
        norm_var = 1 - (var_len / strict_upper_bound if strict_upper_bound > 0 else 0.0)
        norm_var = max(0.0, min(1.0, norm_var))

        # Geometric mean fusion
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
        """BFS calculate shortest path lengths from source to all nodes"""
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