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
        if not all_nodes or not connections:
            return 0.0, {"reason": "no room or connection information"}

        # build graph
        graph = {node['id']: [] for node in all_nodes}

        for conn in connections:
            if conn['from_room'] in graph and conn['to_room'] in graph:
                graph[conn['from_room']].append(conn['to_room'])
                graph[conn['to_room']].append(conn['from_room'])
        
        # calculate accessibility
        scores = []
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
        
        avg_access = float(np.mean(scores)) if scores else 0.0
        complexity_factor = min(1.0, len(all_nodes) / 6.0)

        # piecewise linear mapping - more lenient version
        if 0.6 <= avg_access <= 0.95:
            base_score = 1.0
        elif avg_access < 0.6:
            base_score = 0.3 + 0.7 * (avg_access / 0.6)
        else:
            base_score = max(0.5, 1.0 - (avg_access - 0.95) / 0.1)
        score = base_score * complexity_factor

        return score, {"avg_accessibility": avg_access, "complexity_factor": complexity_factor, "detail": scores} 