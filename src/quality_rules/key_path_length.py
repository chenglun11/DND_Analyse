from .base import BaseQualityRule
from collections import deque

class KeyPathLengthRule(BaseQualityRule):
    name = "key_path_length"
    description = "关键路径长度，入口到出口的最短路径长度"

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
        
        # 节点集为rooms+corridors
        all_nodes = rooms + corridors
        graph = {node['id']: [] for node in all_nodes}
        for conn in connections:
            if conn['from_room'] in graph and conn['to_room'] in graph:
                graph[conn['from_room']].append(conn['to_room'])
                graph[conn['to_room']].append(conn['from_room'])
        
        # 查找入口和出口房间
        entrance_room = None
        exit_room = None
        
        for room in rooms:
            if room.get('is_entrance', False):
                entrance_room = room['id']
            elif room.get('is_exit', False):
                exit_room = room['id']
        
        # 如果没有明确标记的入口出口，使用启发式方法
        if not entrance_room or not exit_room:
            # 只选有连接的主房间作为入口/出口候选
            def get_pos(room):
                pos = room.get('position', {})
                return pos.get('x', 0), pos.get('y', 0)
            
            connected_rooms = [room for room in rooms if len(graph[room['id']]) > 0]
            if not connected_rooms:
                return 0.0, {"reason": "无连通房间"}
            
            # 使用坐标推断作为备选方案
            entrance_room = min(connected_rooms, key=get_pos)['id']
            exit_room = max(connected_rooms, key=get_pos)['id']
        
        # BFS允许经过corridor节点
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
            score = 0.0
        elif 5 <= path_len <= 15:
            score = 1.0
        elif 3 <= path_len < 5 or 15 < path_len <= 20:
            score = 0.8
        elif 1 <= path_len < 3 or 20 < path_len <= 25:
            score = 0.6
        else:
            score = 0.3
        
        return score, {
            "key_path_length": path_len, 
            "entrance": entrance_room, 
            "exit": exit_room,
            "entrance_marked": entrance_room in [r['id'] for r in rooms if r.get('is_entrance', False)],
            "exit_marked": exit_room in [r['id'] for r in rooms if r.get('is_exit', False)]
        } 