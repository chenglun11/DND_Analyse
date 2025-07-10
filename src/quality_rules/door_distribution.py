from .base import BaseQualityRule
import numpy as np
from collections import defaultdict

class DoorDistributionRule(BaseQualityRule):
    name = "door_distribution"
    description = "door distribution, the lower the better"

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
        
        # infer the number of doors for each room from connections
        room_door_counts = defaultdict(int)
        for conn in connections:
            room_door_counts[conn['from_room']] += 1
            room_door_counts[conn['to_room']] += 1
        
        door_counts = list(room_door_counts.values())
        if not door_counts:
            return 0.0, {"reason": "No valid door distribution"}
        door_var = float(np.var(door_counts))
        mean_doors = float(np.mean(door_counts))
        
        room_count = len(rooms)
        complexity_factor = min(1.0, room_count / 6.0)  # 8 rooms as baseline
        door_ratio = mean_doors / room_count if room_count > 0 else 0.0

        # linear mapping: score 0~0.8 linearly from 0.1~0.8
        if door_ratio < 0.8:
            base_score = 0.1 + 0.7 * (door_ratio / 0.8)
        elif 0.8 <= door_ratio <= 1.5:
            base_score = 1.0
        else:
            # high door ratio also decreases, at most to 0.1
            base_score = max(0.1, 1.5 - abs(door_ratio - 1.5))
        
        # apply complexity factor
        score = base_score * complexity_factor
        
        return score, {"door_variance": door_var, "mean_doors": mean_doors, "door_counts": door_counts, "room_count": room_count, "door_ratio": door_ratio, "complexity_factor": complexity_factor} 