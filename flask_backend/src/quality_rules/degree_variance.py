from .base import BaseQualityRule
from collections import defaultdict
from typing import Dict, Any, Tuple, List
import math

class DegreeVarianceRule(BaseQualityRule):
    """
    Degree variance assessment: 无主观权重，纯客观评估节点度数分布的方差

    子指标:
      1. raw_variance: 度数分布的方差
      2. normalized_variance: 相对于理论最大方差归一化 (0-1)

    评分: score = 1 - normalized_variance，度数越均匀评分越高
    
    改进:
    - 修正了小规模地图下理论最大方差计算过小的问题
    - 使用更合理的归一化方法
    """

    @property
    def name(self) -> str:
        return "degree_variance"

    @property
    def description(self) -> str:
        return "Objective assessment of degree variance in dungeon graph"

    def evaluate(self, dungeon_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        levels = dungeon_data.get('levels', [])
        if not levels:
            return 0.0, {"reason": "No level data"}
        level = levels[0]
        connections = level.get('connections', [])
        rooms = level.get('rooms', [])
        if not rooms or not connections:
            return 0.0, {"reason": "No rooms or connections"}

        # 构建图的度数映射，确保所有房间都包含
        degree = defaultdict(int)
        room_ids = [r['id'] for r in rooms]
        for c in connections:
            degree[c['from_room']] += 1
            degree[c['to_room']] += 1
        for rid in room_ids:
            degree.setdefault(rid, 0)

        # 计算方差
        degrees: List[float] = [degree[rid] for rid in room_ids]
        n = len(degrees)
        mean_deg = sum(degrees) / n
        raw_variance = sum((d - mean_deg) ** 2 for d in degrees) / n

        # 改进的理论最大方差计算
        # 考虑实际可能的度数分布情况
        if n <= 2:
            # 对于小规模地图，使用更合理的最大方差
            max_var = max(1.0, raw_variance)  # 至少为1.0，或实际方差
        else:
            # 对于大规模地图，使用改进的理论最大方差
            # 考虑实际可能的度数分布：从0到(n-1)
            max_degree = n - 1
            min_degree = 0
            # 理论最大方差：当一半节点为最小度数，一半为最大度数时
            theoretical_max_var = ((max_degree - min_degree) / 2) ** 2
            max_var = max(theoretical_max_var, raw_variance)

        # 归一化
        normalized_variance = raw_variance / max_var if max_var > 0 else 0.0
        normalized_variance = min(max(normalized_variance, 0.0), 1.0)

        # 评分: 度数越均匀 (方差越低) 得分越高
        score = 1.0 - normalized_variance

        return score, {
            'raw_variance': raw_variance,
            'normalized_variance': normalized_variance,
            'score': score,
            'degrees': degrees,
            'max_variance': max_var,
            'room_count': n,
            'mean_degree': mean_deg
        } 