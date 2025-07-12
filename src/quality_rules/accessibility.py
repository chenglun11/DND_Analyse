from .base import BaseQualityRule
from collections import deque
import numpy as np

class AccessibilityRule(BaseQualityRule):
    name = "accessibility"
    description = "accessibility, the higher the better"

    def evaluate(self, dungeon_data):
        levels = dungeon_data.get('levels', [])
        if not levels:
            return 0.0, {"reason": "no level data"}
        level = levels[0]
        rooms = level.get('rooms', [])
        corridors = level.get('corridors', [])
        connections = level.get('connections', [])
        
        all_nodes = rooms + corridors
        if not all_nodes:
            return 0.0, {"reason": "no room or connection information"}

        # 统一ID为字符串
        def norm_id(x):
            return str(x)
        for node in all_nodes:
            node['id'] = norm_id(node['id'])
        for conn in connections:
            conn['from_room'] = norm_id(conn['from_room'])
            conn['to_room'] = norm_id(conn['to_room'])

        # build graph
        graph = {node['id']: [] for node in all_nodes}
        for conn in connections:
            if conn['from_room'] in graph and conn['to_room'] in graph:
                graph[conn['from_room']].append(conn['to_room'])
                graph[conn['to_room']].append(conn['from_room'])

        import math
        def get_pos(node):
            pos = node.get('position', {})
            return pos.get('x', node.get('x', 0)), pos.get('y', node.get('y', 0))
        node_by_id = {node['id']: node for node in all_nodes}
        added_connections = []

        # 1. 补全孤立房间
        for node in all_nodes:
            if len(graph[node['id']]) == 0:
                min_dist = float('inf')
                nearest = None
                x0, y0 = get_pos(node)
                for other in all_nodes:
                    if other['id'] == node['id']:
                        continue
                    x1, y1 = get_pos(other)
                    dist = math.hypot(x1 - x0, y1 - y0)
                    if dist < min_dist:
                        min_dist = dist
                        nearest = other
                if nearest is not None:
                    graph[node['id']].append(nearest['id'])
                    graph[nearest['id']].append(node['id'])
                    added_connections.append((node['id'], nearest['id']))

        # 2. 检查所有连通分量，补全分量间最短距离的连接，直到全图连通
        def find_components(graph):
            visited = set()
            components = []
            for node in graph:
                if node not in visited:
                    comp = set()
                    queue = deque([node])
                    visited.add(node)
                    while queue:
                        curr = queue.popleft()
                        comp.add(curr)
                        for nb in graph[curr]:
                            if nb not in visited:
                                visited.add(nb)
                                queue.append(nb)
                    components.append(comp)
            return components

        while True:
            components = find_components(graph)
            if len(components) <= 1:
                break
            # 找到两个分量间最近的节点对
            min_dist = float('inf')
            pair = None
            for i in range(len(components)):
                for j in range(i+1, len(components)):
                    for n1 in components[i]:
                        for n2 in components[j]:
                            x1, y1 = get_pos(node_by_id[n1])
                            x2, y2 = get_pos(node_by_id[n2])
                            dist = math.hypot(x1 - x2, y1 - y2)
                            if dist < min_dist:
                                min_dist = dist
                                pair = (n1, n2)
            if pair:
                n1, n2 = pair
                graph[n1].append(n2)
                graph[n2].append(n1)
                added_connections.append((n1, n2))
            else:
                break

        # calculate accessibility
        scores = []
        isolated_nodes = []
        for node in all_nodes:
            visited = set()
            queue = deque([node['id']])
            visited.add(node['id'])
            while queue:
                curr = queue.popleft()
                for nb in graph.get(curr, []):
                    if nb not in visited:
                        visited.add(nb)
                        queue.append(nb)
            scores.append(len(visited) / len(all_nodes))
            if len(visited) == 1:
                isolated_nodes.append(node['id'])
        
        avg_access = float(np.mean(scores)) if scores else 0.0
        complexity_factor = min(1.0, len(all_nodes) / 6.0)

        # 新评分映射逻辑
        if avg_access >= 0.95:
            base_score = 1.0
        elif 0.6 <= avg_access < 0.95:
            base_score = 0.5 + 0.5 * (avg_access - 0.6) / 0.35
        else:
            base_score = 0.3 + 0.7 * (avg_access / 0.6)
        score = base_score * complexity_factor

        return score, {
            "avg_accessibility": avg_access,
            "complexity_factor": complexity_factor,
            "detail": scores,
            "added_connections": added_connections,
            "isolated_nodes": isolated_nodes,
            "component_count": len(find_components(graph))
        } 