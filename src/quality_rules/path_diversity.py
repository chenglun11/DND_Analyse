import numpy as np
from .base import BaseQualityRule
import math
from collections import deque
import logging
logger = logging.getLogger(__name__)

class PathDiversityRule(BaseQualityRule):
    """
    Path diversity assessment based on choice theory and game design principles.
    
    Theoretical foundations:
    1. Choice Theory (Schwartz, 2004) - Paradox of choice and optimal selection
    2. Game Design Theory (Schell, 2008) - Exploration and player agency
    3. Graph Theory - Path analysis and routing
    
    References:
    - Schwartz, B. (2004). The paradox of choice: Why more is less.
    - Schell, J. (2008). The art of game design.
    """
    
    @property
    def name(self):
        return "path_diversity"

    @property
    def description(self):
        return "Path diversity score, the higher the score, the more diverse the paths, normalized to [0,1], max=10.0 "

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
        
        # 构建图 - Based on graph theory
        graph = {node['id']: [] for node in all_nodes}
        for conn in connections:
            if conn['from_room'] in graph and conn['to_room'] in graph:
                graph[conn['from_room']].append(conn['to_room'])
                graph[conn['to_room']].append(conn['from_room'])
        
        # 计算所有房间对的最短路径数量 - Based on Schwartz (2004) choice theory
        def count_shortest_paths(start, end):
            if start == end:
                return 1
            
            # 使用BFS找到最短路径长度 - Based on graph theory algorithms
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
            
            # 计算最短路径的数量 - Based on Schell (2008) player agency principles
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
        
        logger.debug(f'path_counts: {path_counts}')
        if not path_counts:
            # 如果没有可达路径，给一个基础分数 - Based on choice theory minimum viable options
            return 0.3, {
                "avg_path_diversity": 0.0, 
                "path_counts": [], 
                "reason": "No reachable paths between rooms"
            }
        
        avg_path_div = float(np.mean(path_counts))
        logger.debug(f'avg_path_diversity: {avg_path_div}')
        
        # 归一化评分，分支均值越高分数越高，最大值max_diversity时为满分
        # Based on Schwartz (2004) optimal choice range
        max_diversity = 10.0  # 可根据实际情况调整
        score = min(1.0, avg_path_div / max_diversity)
        
        return score, {
            "avg_path_diversity": avg_path_div, 
            "path_counts": path_counts,
            "max_diversity": max_diversity
        } 