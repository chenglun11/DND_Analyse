from .base import BaseQualityRule
from collections import deque
import logging

logger = logging.getLogger(__name__)

class KeyPathLengthRule(BaseQualityRule):
    """
    Key path length assessment based on graph theory and game design principles.
    
    Theoretical foundations:
    1. Graph Theory - Shortest path algorithms
    2. Game Design Theory (Schell, 2008) - Pacing and progression
    3. Player Psychology - Engagement and flow
    4. Network Analysis - Path optimization
    
    References:
    - Schell, J. (2008). The art of game design.
    - Newman, M. E. J. (2010). Networks: An introduction.
    - Csikszentmihalyi, M. (1990). Flow: The psychology of optimal experience.
    """
    
    @property
    def name(self):
        return "key_path_length"
    
    @property
    def description(self):
        return "关键路径长度，入口到出口的最短路径长度"

    def evaluate(self, dungeon_data):
        levels = dungeon_data.get('levels', [])
        if not levels:
            return 0.0, {"reason": "无层级数据"}
        level = levels[0]
        rooms = level.get('rooms', [])
        corridors = level.get('corridors', [])
        connections = level.get('connections', [])
        if not rooms or not connections:
            return 0.0, {"reason": "无房间或连接信息"}
        
        # 节点集为rooms+corridors - Based on graph theory
        all_nodes = rooms + corridors
        graph = {node['id']: [] for node in all_nodes}
        for conn in connections:
            if conn['from_room'] in graph and conn['to_room'] in graph:
                graph[conn['from_room']].append(conn['to_room'])
                graph[conn['to_room']].append(conn['from_room'])
        
        # 使用改进的入口出口识别 - Based on Schell (2008) game design principles
        from src.schema import identify_entrance_exit
        enhanced_data = identify_entrance_exit(dungeon_data)
        enhanced_rooms = enhanced_data['levels'][0]['rooms']
        
        # 查找识别出的入口和出口
        entrance_room = None
        exit_room = None
        
        for room in enhanced_rooms:
            if room.get('is_entrance', False):
                entrance_room = room['id']
                logger.debug(f"找到识别出的入口: {entrance_room}")
            elif room.get('is_exit', False):
                exit_room = room['id']
                logger.debug(f"找到识别出的出口: {exit_room}")
        
        # 如果识别失败，使用备用策略
        if not entrance_room or not exit_room:
            # 只考虑有连接的房间
            connected_rooms = [room for room in rooms if len(graph[room['id']]) > 0]
            if len(connected_rooms) >= 2:
                # 入口选择策略：连接度较低的房间
                if not entrance_room:
                    degree_1_rooms = [r for r in connected_rooms if len(graph[r['id']]) == 1]
                    if degree_1_rooms:
                        entrance_room = degree_1_rooms[0]['id']
                        logger.debug(f"备用策略找到入口: {entrance_room} (度=1)")
                    else:
                        entrance_room = min(connected_rooms, key=lambda r: len(graph[r['id']]))['id']
                        logger.debug(f"备用策略找到入口: {entrance_room} (最低度)")
                
                # 出口选择策略：另一个连接度较低且可达的房间
                if not exit_room:
                    exit_candidates = [r for r in connected_rooms if r['id'] != entrance_room]
                    if exit_candidates:
                        # 优先选择连接度为1的可达房间
                        degree_1_exits = [r for r in exit_candidates if len(graph[r['id']]) == 1]
                        for candidate in degree_1_exits:
                            if self._is_reachable(graph, entrance_room, candidate['id']):
                                exit_room = candidate['id']
                                logger.debug(f"备用策略找到出口: {exit_room} (度=1, 可达)")
                                break
                        
                        # 如果没有可达的度为1的房间，选择连接度最低的可达房间
                        if not exit_room:
                            for candidate in sorted(exit_candidates, key=lambda r: len(graph[r['id']])):
                                if self._is_reachable(graph, entrance_room, candidate['id']):
                                    exit_room = candidate['id']
                                    logger.debug(f"备用策略找到出口: {exit_room} (最低度, 可达)")
                                    break
        
        # 检查是否成功识别了入口和出口
        if not entrance_room or not exit_room:
            logger.warning(f"无法识别入口或出口: entrance={entrance_room}, exit={exit_room}")
            return 0.0, {
                "reason": "无法识别入口或出口",
                "entrance": entrance_room,
                "exit": exit_room
            }
        
        # 检查可达性
        if not self._is_reachable(graph, entrance_room, exit_room):
            logger.warning(f"入口 {entrance_room} 到出口 {exit_room} 不可达")
            return 0.0, {
                "reason": "入口到出口不可达",
                "entrance": entrance_room,
                "exit": exit_room,
                "entrance_degree": len(graph.get(entrance_room, [])),
                "exit_degree": len(graph.get(exit_room, []))
            }
        
        # BFS计算最短路径长度 - Based on Newman (2010) network analysis
        def bfs(start, end):
            queue = deque([(start, 0)])
            visited = set([start])
            while queue:
                curr, dist = queue.popleft()
                if curr == end:
                    return dist
                for nb in graph.get(curr, []):
                    if nb not in visited:
                        visited.add(nb)
                        queue.append((nb, dist+1))
            return None
        
        path_len = bfs(entrance_room, exit_room)
        if path_len is None:
            logger.warning(f"无法计算路径长度: {entrance_room} -> {exit_room}")
            score = 0.0
        elif 5 <= path_len <= 15:
            score = 1.0
        elif 3 <= path_len < 5 or 15 < path_len <= 20:
            score = 0.8
        elif 1 <= path_len < 3 or 20 < path_len <= 25:
            score = 0.6
        else:
            score = 0.3
        
        logger.info(f"关键路径长度: {path_len}, 得分: {score:.3f}")
        
        return score, {
            "key_path_length": path_len, 
            "entrance": entrance_room, 
            "exit": exit_room,
            "entrance_marked": entrance_room in [r['id'] for r in rooms if r.get('is_entrance', False)],
            "exit_marked": exit_room in [r['id'] for r in rooms if r.get('is_exit', False)],
            "entrance_degree": len(graph.get(entrance_room, [])),
            "exit_degree": len(graph.get(exit_room, []))
        }
    
    def _is_reachable(self, graph: dict, start: str, end: str) -> bool:
        """检查两个节点是否可达（BFS）"""
        if start == end:
            return True
        
        visited = set()
        queue = [start]
        visited.add(start)
        
        while queue:
            current = queue.pop(0)
            for neighbor in graph.get(current, []):
                if neighbor == end:
                    return True
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        return False 