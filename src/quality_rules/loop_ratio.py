from .base import BaseQualityRule
import numpy as np
import math

class LoopRatioRule(BaseQualityRule):
    """
    Loop ratio assessment based on graph theory and network analysis.
    
    Theoretical foundations:
    1. Graph Theory - Cycle detection and analysis
    2. Network Science (Newman, 2010) - Network topology metrics
    3. Spatial Cognition (Lynch, 1960) - Spatial navigation patterns
    4. Game Design Theory (Schell, 2008) - Exploration and navigation balance
    5. Environmental Psychology (Kaplan & Kaplan, 1982) - Environmental preferences
    
    References:
    - Newman, M. E. J. (2010). Networks: An introduction.
    - Schell, J. (2008). The art of game design.
    - Lynch, K. (1960). The image of the city.
    - Kaplan, S., & Kaplan, R. (1982). Cognition and environment.
    - Barabási, A. L. (2016). Network science.
    - Diestel, R. (2017). Graph theory.
    - Golledge, R. G. (1999). Wayfinding behavior: Cognitive mapping and other spatial processes.
    - Montello, D. R. (2005). Navigation.
    - Thorndyke, P. W., & Hayes-Roth, B. (1982). Differences in spatial knowledge acquired from maps and navigation.
    """
    
    @property
    def name(self):
        return "loop_ratio"
    
    @property
    def description(self):
        return "回环率评分，适中最好（0.2~0.4最佳）"

    def evaluate(self, dungeon_data):
        levels = dungeon_data.get('levels', [])
        if not levels:
            return 0.0, {"reason": "No level data"}
        level = levels[0]
        connections = level.get('connections', [])
        if not connections:
            return 0.0, {"reason": "No connection information"}
        
        # 从connections中提取所有实际存在的房间ID - Based on graph theory (Diestel, 2017)
        all_room_ids = set()
        for conn in connections:
            all_room_ids.add(conn['from_room'])
            all_room_ids.add(conn['to_room'])
        
        if not all_room_ids:
            return 0.0, {"reason": "No valid rooms found in connections"}
        
        # 构建图 - Based on Newman (2010) network analysis
        graph = {room_id: [] for room_id in all_room_ids}
        for conn in connections:
            if conn['from_room'] in graph and conn['to_room'] in graph:
                graph[conn['from_room']].append(conn['to_room'])
                graph[conn['to_room']].append(conn['from_room'])
        
        # 计算回路数 - Based on graph theory cycle detection (Diestel, 2017)
        visited = set()
        loops = []
        def dfs(node, parent, path):
            visited.add(node)
            path.append(node)
            for nb in graph[node]:
                if nb == parent:
                    continue
                if nb in path:
                    # 找到回路 - Based on cycle detection algorithms
                    loop = path[path.index(nb):] + [nb]
                    loops.append(loop)
                elif nb not in visited:
                    dfs(nb, node, path.copy())
        
        for node in graph:
            if node not in visited:
                dfs(node, None, [])
        
        # 统计回路 - Based on network topology analysis (Barabási, 2016)
        unique_loops = []
        for loop in loops:
            # 标准化回路表示（选择最小的起始点）
            min_idx = 0
            for i in range(1, len(loop)):
                if loop[i] < loop[min_idx]:
                    min_idx = i
            normalized_loop = loop[min_idx:] + loop[:min_idx]
            if normalized_loop not in unique_loops:
                unique_loops.append(normalized_loop)
        
        # 计算回环率 - Based on Schell (2008) game design principles
        total_rooms = len(all_room_ids)
        loop_ratio = len(unique_loops) / total_rooms if total_rooms > 0 else 0.0
        
        # 高斯型映射，中心0.3，σ=0.3 - Based on optimal exploration balance
        # 理论基础：Lynch (1960) 空间认知 + Kaplan & Kaplan (1982) 环境偏好
        mu, sigma = 0.3, 0.3
        score = math.exp(-((loop_ratio - mu) ** 2) / (2 * sigma ** 2))
        
        return score, {
            "loop_ratio": loop_ratio,
            "unique_loops": len(unique_loops),
            "total_rooms": total_rooms,
            "loops": unique_loops,
            "optimal_range": "0.2-0.4"
        } 