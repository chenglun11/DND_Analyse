from .base import BaseQualityRule
import numpy as np
import math

class LoopRatioRule(BaseQualityRule):
    name = "loop_ratio"
    description = "回环率评分，适中最好（0.2~0.4最佳）"

    def evaluate(self, dungeon_data):
        levels = dungeon_data.get('levels', [])
        if not levels:
            return 0.0, {"reason": "No level data"}
        level = levels[0]
        connections = level.get('connections', [])
        if not connections:
            return 0.0, {"reason": "No connection information"}
        
        # 从connections中提取所有实际存在的房间ID
        all_room_ids = set()
        for conn in connections:
            all_room_ids.add(conn['from_room'])
            all_room_ids.add(conn['to_room'])
        
        if not all_room_ids:
            return 0.0, {"reason": "No valid rooms found in connections"}
        
        # 构建图
        graph = {room_id: [] for room_id in all_room_ids}
        for conn in connections:
            if conn['from_room'] in graph and conn['to_room'] in graph:
                graph[conn['from_room']].append(conn['to_room'])
                graph[conn['to_room']].append(conn['from_room'])
        
        # 计算回路数
        visited = set()
        loops = []
        def dfs(node, parent, path):
            visited.add(node)
            path.append(node)
            for nb in graph[node]:
                if nb == parent:
                    continue
                if nb in path:
                    # 找到回路
                    loop = path[path.index(nb):] + [nb]
                    loops.append(loop)
                elif nb not in visited:
                    dfs(nb, node, path.copy())
        
        for node in graph:
            if node not in visited:
                dfs(node, None, [])
        
        # 统计回路
        unique_loops = []
        for loop in loops:
            loop_set = set(loop)
            if not any(loop_set == set(l) for l in unique_loops):
                unique_loops.append(loop)
        
        loop_ratio = len(unique_loops) / len(all_room_ids) if all_room_ids else 0.0
        
        # 高斯型映射，中心0.3，σ=0.3（更宽松）
        mu, sigma = 0.3, 0.3
        score = math.exp(-((loop_ratio-mu)**2)/(2*sigma**2))
        
        return score, {
            "loop_ratio": loop_ratio, 
            "loop_count": len(unique_loops), 
            "total_nodes": len(all_room_ids), 
            "loops": unique_loops,
            "all_rooms": list(all_room_ids)
        } 