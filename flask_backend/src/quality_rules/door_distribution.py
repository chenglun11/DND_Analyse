from .base import BaseQualityRule
from collections import defaultdict
import math
from typing import List, Dict, Tuple, Any, Optional

class DoorDistributionRule(BaseQualityRule):
    """
    Door distribution assessment based on spatial topology and architectural principles.
    
    Uses entropy-weighting over three normalized sub-metrics:
      1. CV of door counts per room (lower is better)
      2. Average door-to-door distance (higher is better)
      3. Average per-room door-angle entropy (higher is better)
    """
    
    @property
    def name(self) -> str:
        return "door_distribution"
    
    @property
    def description(self) -> str:
        return "Entropy-weighted door distribution score"

    def evaluate(self, dungeon_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        # extract level
        levels = dungeon_data.get('levels', [])
        if not levels:
            return 0.0, {"reason": "No level data"}
        level = levels[0]

        rooms = level.get('rooms', [])
        corridors = level.get('corridors', [])
        connections = level.get('connections', [])
        doors = level.get('doors', [])  # raw door list with coords
        
        # Combine rooms and corridors
        all_rooms = rooms + corridors
        
        if not all_rooms or not connections:
            return 0.0, {"reason": "Insufficient geometry or connections"}

        # 1. CV of door counts
        room_counts = defaultdict(int)
        for c in connections:
            room_counts[c['from_room']] += 1
            room_counts[c['to_room']] += 1
        counts = list(room_counts.values())
        mean_c = sum(counts) / len(counts)
        var_c = sum((x - mean_c)**2 for x in counts) / len(counts)
        cv = math.sqrt(var_c) / mean_c if mean_c > 0 else 0.0

        # 2. Avg door-to-door distance
        avg_dist, dist_info = self._calculate_avg_door_distance(all_rooms, connections, doors)

        # 3. Avg room-angle entropy
        avg_entropy = self._calculate_avg_room_entropy(all_rooms, connections)

        # 4. 归一化常数 (基于图论理论)
        MAX_CV = 2.0  # CV的理论最大值
        
        # 距离归一化：使用平均房间间距离作为基准
        # 理论依据：Delaunay三角剖分中的平均边长
        room_positions = [(r['position']['x'] + r['size']['width']/2, 
                          r['position']['y'] + r['size']['height']/2) for r in all_rooms]
        if len(room_positions) >= 2:
            # 计算所有房间对的距离，取平均值作为特征距离
            total_dist = 0
            pair_count = 0
            for i in range(len(room_positions)):
                for j in range(i+1, min(i+11, len(room_positions))):  # 每个房间最多考虑10个邻居
                    x1, y1 = room_positions[i]
                    x2, y2 = room_positions[j]
                    total_dist += math.hypot(x2-x1, y2-y1)
                    pair_count += 1
            D_char = total_dist / pair_count if pair_count > 0 else avg_dist + 1
        else:
            D_char = avg_dist + 1  # 防止除零
            
        MAX_ENT = math.log(4)  # 4象限的最大熵

        # 5. 归一化
        norm_cv = max(0.0, min(1.0, 1 - cv / MAX_CV))
        norm_dist = min(avg_dist / D_char, 1.0)
        norm_ent = min(avg_entropy / MAX_ENT, 1.0)

        # 6. 权重同等
        w_cv, w_dist, w_ent = 1/3, 1/3, 1/3

        # 6. final score
        score = w_cv * norm_cv + w_dist * norm_dist + w_ent * norm_ent

        return score, {
            'cv': cv,
            'avg_distance': avg_dist,
            'avg_entropy': avg_entropy,
            'weights': [w_cv, w_dist, w_ent],
            'normalized': [norm_cv, norm_dist, norm_ent],
            'score': score,
            'debug': dist_info
        }

    def _min_max(self, x: float, arr: List[float]) -> float:
        mn, mx = min(arr), max(arr)
        if mx <= mn:
            return 1.0
        return (x - mn) / (mx - mn)

    def _calculate_avg_door_distance(self, rooms: List[Dict], connections: List[Dict], doors: List[Dict]) -> Tuple[float, Dict[str, Any]]:
        # build coord maps
        door_pos = {d['id']:(d['position']['x'], d['position']['y']) for d in doors if 'position' in d}
        room_pos = {r['id']:(r['position']['x'], r['position']['y']) for r in rooms}
        dists = []
        for c in connections:
            # door-level
            if 'door_id' in c and c['door_id'] in door_pos:
                dx, dy = door_pos[c['door_id']]
                fr = room_pos.get(c['from_room']); to = room_pos.get(c['to_room'])
                if fr and to:
                    # 统一使用欧几里得距离
                    dist1 = math.hypot(dx - fr[0], dy - fr[1])
                    dist2 = math.hypot(dx - to[0], dy - to[1])
                    avg_dist = (dist1 + dist2) / 2
                    dists.append(avg_dist)
            else:
                fr = room_pos.get(c['from_room']); to = room_pos.get(c['to_room'])
                if fr and to:
                    # 统一使用欧几里得距离
                    dists.append(math.hypot(to[0]-fr[0], to[1]-fr[1]))
        avg_d = sum(dists)/len(dists) if dists else 0.0
        return avg_d, {'count': len(dists)}

    def _calculate_avg_room_entropy(self, rooms: List[Dict], connections: List[Dict]) -> float:
        room_doors = defaultdict(list)
        room_pos = {r['id']:(r['position']['x'], r['position']['y']) for r in rooms}
        room_ids = set(room_pos.keys())
        
        # Only process connections between actual rooms, not game elements
        for c in connections:
            from_room = c.get('from_room')
            to_room = c.get('to_room')
            if from_room in room_ids and to_room in room_ids:
                room_doors[from_room].append(to_room)
                room_doors[to_room].append(from_room)
        
        ent_list = []
        for rid, nbrs in room_doors.items():
            if len(nbrs) < 2: 
                # 单门房间返回小常数，避免对后续步骤不友好
                ent_list.append(0.1)
                continue
            cx, cy = room_pos[rid]
            quad = [0]*4
            for nr in nbrs:
                nx_, ny = room_pos.get(nr, (cx,cy))
                ang = (math.degrees(math.atan2(ny-cy, nx_-cx)) + 360) % 360
                quad[int(ang//90)] += 1
            tot = sum(quad)
            if tot > 0:
                ent = -sum((q/tot)*math.log(q/tot) for q in quad if q>0)
                ent_list.append(ent)
            else:
                # 避免log(0)错误
                ent_list.append(0.1)
        return sum(ent_list)/len(ent_list) if ent_list else 0.1

    def _calculate_entropy_weights(self, data: List[Dict[str, float]]) -> List[float]:
        N = len(data)
        if N < 2:
            return [1/3, 1/3, 1/3]
        cv_vals = [d['cv'] for d in data]
        dist_vals = [d['dist'] for d in data]
        ent_vals = [d['ent'] for d in data]
        norm_cv = [self._min_max(v, cv_vals) for v in cv_vals]
        norm_dist = [self._min_max(v, dist_vals) for v in dist_vals]
        norm_ent = [self._min_max(v, ent_vals) for v in ent_vals]
        norm = [norm_cv, norm_dist, norm_ent]
        # invert cv
        norm[0] = [1 - v for v in norm[0]]
        # entropy weights
        probs = []
        for col in norm:
            s = sum(col)
            probs.append([v/s if s>0 else 1/N for v in col])
        ent = [ -sum(p*math.log(p) for p in col if p>0)/math.log(N) for col in probs]
        dif = [1 - e for e in ent]
        total = sum(dif)
        return [d/total if total>0 else 1/3 for d in dif] 