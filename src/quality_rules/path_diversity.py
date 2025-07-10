from .base import BaseQualityRule
import numpy as np
import math
from collections import deque

class PathDiversityRule(BaseQualityRule):
    name = "path_diversity"
    description = "路径多样性评分，适中最好（2.0最佳）"

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
        
        # 构建图
        graph = {node['id']: [] for node in all_nodes}
        for conn in connections:
            if conn['from_room'] in graph and conn['to_room'] in graph:
                graph[conn['from_room']].append(conn['to_room'])
                graph[conn['to_room']].append(conn['from_room'])
        
        # 计算所有房间对的最短路径数量
        def count_shortest_paths(start, end):
            if start == end:
                return 1
            
            # 使用BFS找到最短路径长度
            visited = set()
            queue = deque([(start, 0)])
            visited.add(start)
            shortest_length = None
            
            while queue:
                curr, length = queue.popleft()
                if curr == end:
                    shortest_length = length
                    break
                for nb in graph[curr]:
                    if nb not in visited:
                        visited.add(nb)
                        queue.append((nb, length + 1))
            
            if shortest_length is None:
                return 0  # 不可达
            
            # 计算最短路径的数量
            def count_paths_with_length(curr, target, remaining_length, visited):
                if remaining_length == 0:
                    return 1 if curr == target else 0
                if remaining_length < 0:
                    return 0
                
                count = 0
                for nb in graph[curr]:
                    if nb not in visited:
                        count += count_paths_with_length(nb, target, remaining_length - 1, visited | {curr})
                return count
            
            return count_paths_with_length(start, end, shortest_length, set())
        
        path_counts = []
        room_ids = [room['id'] for room in rooms]
        
        for i in range(len(room_ids)):
            for j in range(i+1, len(room_ids)):
                cnt = count_shortest_paths(room_ids[i], room_ids[j])
                if cnt > 0:
                    path_counts.append(cnt)
        
        if not path_counts:
            # 如果没有可达路径，给一个基础分数
            return 0.3, {"avg_path_diversity": 0.0, "path_counts": [], "reason": "No reachable paths between rooms"}
        
        avg_path_div = float(np.mean(path_counts))
        
        # 高斯型映射，中心2.0，σ=1.0（更宽松）
        mu, sigma = 2.0, 1.0
        score = math.exp(-((avg_path_div-mu)**2)/(2*sigma**2))
        
        return score, {"avg_path_diversity": avg_path_div, "path_counts": path_counts} 