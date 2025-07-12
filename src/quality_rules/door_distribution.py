from .base import BaseQualityRule
import numpy as np
from collections import defaultdict

class DoorDistributionRule(BaseQualityRule):
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
        
        # 统计每个房间的门数
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
        
        # 计算理想的 door-to-room 比例
        # 对于好的地牢设计，每个房间平均应该有1.5-3个门
        ideal_min_doors = 1.5
        ideal_max_doors = 3.0
        
        # 评估门数量是否合理
        if mean_doors < 1.0:
            # 门太少，连通性差
            door_quantity_score = mean_doors / 1.0
        elif 1.0 <= mean_doors <= ideal_max_doors:
            # 理想范围
            door_quantity_score = 1.0
        else:
            # 门太多，可能过于复杂
            door_quantity_score = max(0.0, 1.0 - (mean_doors - ideal_max_doors) / ideal_max_doors)
        
        # 评估门分布的均匀性（方差越小越好）
        # 标准化方差：用方差除以平均值的平方
        if mean_doors > 0:
            normalized_variance = door_variance / (mean_doors ** 2)
            # 方差越小，分布越均匀，得分越高
            distribution_score = max(0.0, 1.0 - normalized_variance)
        else:
            distribution_score = 0.0
        
        # 评估连通性（确保没有孤立房间）
        isolated_rooms = sum(1 for count in door_counts if count == 0)
        connectivity_score = max(0.0, 1.0 - (isolated_rooms / room_count)) if room_count > 0 else 0.0
        
        # 综合评分：门数量(40%) + 分布均匀性(40%) + 连通性(20%)
        final_score = (door_quantity_score * 0.4 + 
                      distribution_score * 0.4 + 
                      connectivity_score * 0.2)
        
        return final_score, {
            "door_variance": door_variance,
            "mean_doors": mean_doors,
            "door_counts": door_counts,
            "room_count": room_count,
            "total_doors": total_doors,
            "door_quantity_score": door_quantity_score,
            "distribution_score": distribution_score,
            "connectivity_score": connectivity_score,
            "isolated_rooms": isolated_rooms,
            "normalized_variance": door_variance / (mean_doors ** 2) if mean_doors > 0 else 0.0
        } 