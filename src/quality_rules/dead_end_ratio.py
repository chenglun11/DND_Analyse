from .base import BaseQualityRule
import math
from collections import defaultdict, deque
from typing import Dict, Any, List, Tuple

class DeadEndRatioRule(BaseQualityRule):
    """
    Dead end ratio assessment: pure objective scoring, no subjective weights
    
    Sub-indicators:
      1. dead_end_ratio: Ratio of rooms with degree 1 (0-1)
      2. avg_dead_end_length: Average dead end length (optional)

    Scoring: score = 1 - dead_end_ratio, fewer dead ends result in higher scores
    """
    
    def __init__(self, include_length: bool = False):
        """
        Initialize rule
        Args:
            include_length: Whether to include dead end length analysis
        """
        self.include_length = include_length
    
    @property
    def name(self) -> str:
        return "dead_end_ratio"

    @property
    def description(self) -> str:
        return "Objective dead end ratio assessment"

    def evaluate(self, dungeon_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        levels = dungeon_data.get('levels', [])
        if not levels:
            return 0.0, {"reason": "No level data"}
        level = levels[0]

        rooms = level.get('rooms', [])
        connections = level.get('connections', [])
        if not rooms or not connections:
            return 0.0, {"reason": "No rooms or connections"}

        # Build graph and ensure all rooms are included in graph nodes
        graph = defaultdict(list)
        for c in connections:
            u, v = c['from_room'], c['to_room']
            graph[u].append(v)
            graph[v].append(u)
        # Ensure isolated rooms are also counted
        room_ids = [r['id'] for r in rooms]
        for rid in room_ids:
            graph.setdefault(rid, [])

        # 1. Dead end ratio: ratio of rooms with degree 1
        total_rooms = len(room_ids)
        dead_ends = [rid for rid, nbrs in graph.items() if len(nbrs) == 1]
        dead_end_count = len(dead_ends)
        dead_end_ratio = dead_end_count / total_rooms if total_rooms > 0 else 0.0

        # 2. Pure objective scoring: fewer dead ends result in higher scores
        score = 1.0 - dead_end_ratio

        result = {
            'dead_end_ratio': dead_end_ratio,
            'dead_end_count': dead_end_count,
            'total_rooms': total_rooms,
            'dead_end_rooms': dead_ends,
            'score': score
        }

        # 3. Optional: average dead end length
        if self.include_length and dead_ends:
            avg_length = self._calculate_avg_dead_end_length(graph, dead_ends)
            result['avg_dead_end_length'] = avg_length

        return score, result

    def _calculate_avg_dead_end_length(self, graph: Dict[str, List[str]], dead_ends: List[str]) -> float:
        """
        Calculate average dead end length: trace unique path from leaf node to branch point depth
        Args:
            graph: Graph structure
            dead_ends: List of dead end nodes
        Returns:
            Average dead end length
        """
        lengths = []
        for dead_end in dead_ends:
            lengths.append(self._trace_dead_end_path(graph, dead_end))
        return sum(lengths) / len(lengths) if lengths else 0.0

    def _trace_dead_end_path(self, graph: Dict[str, List[str]], dead_end: str) -> int:
        """
        Trace dead end path to branch point
        Args:
            graph: Graph structure
            dead_end: Dead end node
        Returns:
            Path length
        """
        visited = {dead_end}
        queue = deque([(dead_end, 0)])  # (node, dist)
        while queue:
            node, dist = queue.popleft()
            nbrs = [n for n in graph[node] if n not in visited]
            # If current node is not degree=1 with no unvisited neighbors, or degree>2, then reached branch or endpoint
            if len(nbrs) != 1:
                return dist
            visited.add(nbrs[0])
            queue.append((nbrs[0], dist+1))
        return 0 