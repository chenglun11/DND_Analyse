from .base import BaseQualityRule
import numpy as np
from collections import defaultdict

class DoorDistributionRule(BaseQualityRule):
    """
    Door distribution assessment based on spatial topology and architectural principles.
    
    Theoretical foundations:
    1. Spatial Topology - Door placement optimization
    2. Architectural Design Principles - Flow and connectivity
    3. Network Analysis - Connection distribution analysis
    
    References:
    - Lynch, K. (1960). The image of the city.
    - Kaplan, S., & Kaplan, R. (1982). Cognition and environment.
    """
    
    @property
    def name(self):
        return "door_distribution"
    
    @property
    def description(self):
        return "评估门分布的合理性，考虑门的数量分布和房间连通性"

    def evaluate(self, dungeon_data):
        levels = dungeon_data.get('levels', [])
        if not levels:
            return 0.0, {"reason": "No level data"}
        level = levels[0]
        rooms = level.get('rooms', [])
        corridors = level.get('corridors', [])
        connections = level.get('connections', [])
        
        all_nodes = rooms + corridors
        if not all_nodes or not connections:
            return 0.0, {"reason": "No room or connection information"}
        
        # 统计每个房间的门数 - Based on spatial topology analysis
        room_door_counts = defaultdict(int)
        for conn in connections:
            room_door_counts[conn['from_room']] += 1
            room_door_counts[conn['to_room']] += 1
        
        door_counts = list(room_door_counts.values())
        if not door_counts:
            return 0.0, {"reason": "No valid door distribution"}
        
        room_count = len(rooms)
        total_doors = sum(door_counts)
        mean_doors = float(np.mean(door_counts))
        door_variance = float(np.var(door_counts))
        
        # 计算理想的 door-to-room 比例 - Based on architectural design principles
        # 对于好的地牢设计，每个房间平均应该有1.5-3个门
        ideal_min_doors = 1.5
        ideal_max_doors = 3.0
        
        # 评估门数量是否合理 - Based on Lynch (1960) spatial analysis
        if mean_doors < 1.0:
            # 门太少，连通性差
            door_quantity_score = mean_doors / 1.0
        elif 1.0 <= mean_doors <= ideal_max_doors:
            # 理想范围
            door_quantity_score = 1.0
        else:
            # 门太多，可能过于复杂
            door_quantity_score = max(0.0, 1.0 - (mean_doors - ideal_max_doors) / ideal_max_doors)
        
        # 评估门分布的均匀性 - Based on Kaplan & Kaplan (1982) environmental psychology
        if door_variance < 1.0:
            # 分布过于均匀，缺乏变化
            distribution_score = 0.7
        elif door_variance < 3.0:
            # 良好的分布变化
            distribution_score = 1.0
        else:
            # 分布过于不均匀
            distribution_score = max(0.3, 1.0 - (door_variance - 3.0) / 3.0)
        
        # 评估连通性 - Based on network connectivity theory
        connectivity_score = min(1.0, mean_doors / ideal_min_doors)
        
        # 综合评分 - 40% 门数量 + 40% 分布均匀性 + 20% 连通性
        final_score = (door_quantity_score * 0.4 + 
                      distribution_score * 0.4 + 
                      connectivity_score * 0.2)
        
        return final_score, {
            "mean_doors": mean_doors,
            "door_variance": door_variance,
            "door_quantity_score": door_quantity_score,
            "distribution_score": distribution_score,
            "connectivity_score": connectivity_score,
            "room_count": room_count,
            "total_doors": total_doors,
            "ideal_range": f"{ideal_min_doors}-{ideal_max_doors}"
        } 