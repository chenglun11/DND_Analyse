from .base import BaseQualityRule
import math
from collections import defaultdict, deque
from typing import Dict, Any, List, Tuple

class DeadEndRatioRule(BaseQualityRule):
    """
    死胡同比例评估：纯客观评分，无任何主观权重
    
    子指标:
      1. dead_end_ratio: 度数为1的房间比例 (0-1)
      2. avg_dead_end_length: 平均死胡同长度（可选）

    评分: score = 1 - dead_end_ratio，死胡同越少评分越高
    """
    
    def __init__(self, include_length: bool = False):
        """
        初始化规则
        Args:
            include_length: 是否包含死胡同长度分析
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

        # 构建图，并确保所有房间都在图节点中
        graph = defaultdict(list)
        for c in connections:
            u, v = c['from_room'], c['to_room']
            graph[u].append(v)
            graph[v].append(u)
        # 确保孤立房间也被计入
        room_ids = [r['id'] for r in rooms]
        for rid in room_ids:
            graph.setdefault(rid, [])

        # 1. 死胡同比例：度数为1的房间比例
        total_rooms = len(room_ids)
        dead_ends = [rid for rid, nbrs in graph.items() if len(nbrs) == 1]
        dead_end_count = len(dead_ends)
        dead_end_ratio = dead_end_count / total_rooms if total_rooms > 0 else 0.0

        # 2. 纯客观评分：死胡同越少评分越高
        score = 1.0 - dead_end_ratio

        result = {
            'dead_end_ratio': dead_end_ratio,
            'dead_end_count': dead_end_count,
            'total_rooms': total_rooms,
            'dead_end_rooms': dead_ends,
            'score': score
        }

        # 3. 可选：平均死胡同长度
        if self.include_length and dead_ends:
            avg_length = self._calculate_avg_dead_end_length(graph, dead_ends)
            result['avg_dead_end_length'] = avg_length

        return score, result

    def _calculate_avg_dead_end_length(self, graph: Dict[str, List[str]], dead_ends: List[str]) -> float:
        """
        计算平均死胡同长度：沿叶节点唯一路径追溯到分岔点的深度
        Args:
            graph: 图结构
            dead_ends: 死胡同节点列表
        Returns:
            平均死胡同长度
        """
        lengths = []
        for dead_end in dead_ends:
            lengths.append(self._trace_dead_end_path(graph, dead_end))
        return sum(lengths) / len(lengths) if lengths else 0.0

    def _trace_dead_end_path(self, graph: Dict[str, List[str]], dead_end: str) -> int:
        """
        追溯死胡同路径到分岔点
        Args:
            graph: 图结构
            dead_end: 死胡同节点
        Returns:
            路径长度
        """
        visited = {dead_end}
        queue = deque([(dead_end, 0)])  # (node, dist)
        while queue:
            node, dist = queue.popleft()
            nbrs = [n for n in graph[node] if n not in visited]
            # 若当前节点不是度=1且无未访问邻居，或度>2，则到达分岔或终点
            if len(nbrs) != 1:
                return dist
            visited.add(nbrs[0])
            queue.append((nbrs[0], dist+1))
        return 0 