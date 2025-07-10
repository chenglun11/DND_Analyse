from .base import BaseQualityRule

class DeadEndRatioRule(BaseQualityRule):
    name = "dead_end_ratio"
    description = "dead end ratio, the higher the better"

    def evaluate(self, dungeon_data):
        levels = dungeon_data.get('levels', [])
        if not levels:
            return 0.0, {"reason": "No level data"}
        level = levels[0]
        connections = level.get('connections', [])
        if not connections:
            return 0.0, {"reason": "No connection information"}
        
        # extract all actual room IDs from connections
        all_room_ids = set()
        for conn in connections:
            all_room_ids.add(conn['from_room'])
            all_room_ids.add(conn['to_room'])
        
        if not all_room_ids:
            return 0.0, {"reason": "No valid rooms found in connections"}
        
        # count the degree of each room
        degree = {room_id: 0 for room_id in all_room_ids}
        for conn in connections:
            if conn['from_room'] in degree:
                degree[conn['from_room']] += 1
            if conn['to_room'] in degree:
                degree[conn['to_room']] += 1
        
        # dead end: rooms with degree 1
        dead_ends = [rid for rid, d in degree.items() if d == 1]
        dead_end_ratio = len(dead_ends) / len(all_room_ids) if all_room_ids else 0.0
        
        # linear mapping - the higher the better
        score = max(0.2, 1.0 - dead_end_ratio * 0.8)
        
        return score, {
            "dead_end_count": len(dead_ends), 
            "dead_end_ratio": dead_end_ratio, 
            "dead_end_rooms": dead_ends,
            "total_rooms": len(all_room_ids),
            "all_rooms": list(all_room_ids)
        } 