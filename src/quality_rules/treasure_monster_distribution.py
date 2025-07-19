from .base import BaseQualityRule
import math
from collections import defaultdict
from typing import Dict, Any, List, Tuple

class TreasureMonsterDistributionRule(BaseQualityRule):
    """
    Treasure-Monster distribution assessment: 客观融合宝藏与怪物的空间与数量分布

    子指标:
      1. treasure_uniformity: 宝藏数量在各房间间的变异系数一致性 (CV -> uniformity)
      2. monster_uniformity: 怪物数量在各房间间的变异系数一致性
      3. proximity_score: 宝藏到最近怪物的平均距离一致性

    归一化:
      - 对数量变异系数 CV 使用理论最大 CV=sqrt(n-1) 归一化，再取 1-CV_norm
      - 对平均距离使用图边界对角线归一化，取 1 - (avg_dist/D_map)

    融合: 几何平均，仅使用非零因子
    """
    
    @property
    def name(self) -> str:
        return "treasure_monster_distribution"

    @property
    def description(self) -> str:
        return "Objective assessment of treasure and monster spatial & quantitative distribution"

    def evaluate(self, dungeon_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        levels = dungeon_data.get('levels', [])
        if not levels:
            return 0.0, {"reason": "No level data"}
        level = levels[0]

        rooms = level.get('rooms', [])
        game_elements = level.get('game_elements', [])
        if not rooms or not game_elements:
            return 0.0, {"reason": "Insufficient rooms or entities"}

        # 从game_elements中提取treasures和monsters（包括boss）
        treasures = [elem for elem in game_elements if elem.get('type') == 'treasure']
        monsters = [elem for elem in game_elements if elem.get('type') in ['monster', 'boss']]
        
        if not treasures:
            return 0.0, {"reason": "No treasures found"}

        # 房间坐标列表
        room_pos = {r['id']:(r['position']['x'], r['position']['y']) for r in rooms}
        room_ids = list(room_pos.keys())
        n = len(room_ids)

        # 1. 统计每房间宝藏和怪物计数，并获取位置
        t_counts = defaultdict(int)
        m_counts = defaultdict(int)
        t_positions = []
        m_positions = []
        
        for t in treasures:
            pos = t.get('position', {})
            tx, ty = pos.get('x', 0), pos.get('y', 0)
            t_positions.append((tx, ty))
            # 找到最近的房间
            nearest_room = min(room_ids, key=lambda rid: math.hypot(tx - room_pos[rid][0], ty - room_pos[rid][1]))
            t_counts[nearest_room] += 1
            
        for m in monsters:
            pos = m.get('position', {})
            mx, my = pos.get('x', 0), pos.get('y', 0)
            m_positions.append((mx, my))
            # 找到最近的房间
            nearest_room = min(room_ids, key=lambda rid: math.hypot(mx - room_pos[rid][0], my - room_pos[rid][1]))
            m_counts[nearest_room] += 1
            
        # 确保所有房间都有key
        for rid in room_ids:
            t_counts.setdefault(rid, 0)
            m_counts.setdefault(rid, 0)

        # 2. 计算变异系数 CV
        def compute_cv(counts: List[int]) -> float:
            mean = sum(counts) / len(counts)
            var = sum((x - mean)**2 for x in counts) / len(counts)
            return math.sqrt(var) / mean if mean>0 else 0.0

        t_vals = [t_counts[rid] for rid in room_ids]
        cv_t = compute_cv(t_vals)
        # 理论最大 CV
        max_cv = math.sqrt(n-1) if n>1 else 1.0
        # 归一化并转为"均匀度"
        uni_t = max(0.0, 1.0 - min(cv_t / max_cv, 1.0))

        # 3. 计算其他指标
        uni_m = 0.0
        prox_score = 0.0
        avg_dist = 0.0
        
        if monsters:
            # 如果有monsters，计算monster分布和接近度
            m_vals = [m_counts[rid] for rid in room_ids]
            cv_m = compute_cv(m_vals)
            uni_m = max(0.0, 1.0 - min(cv_m / max_cv, 1.0))
            
            # 计算地图对角线
            xs = [x for x,_ in room_pos.values()]
            ys = [y for _,y in room_pos.values()]
            D_map = math.hypot(max(xs)-min(xs), max(ys)-min(ys))

            # 对每个宝藏位置，找最近怪物位置距离
            dists = []
            for tx, ty in t_positions:
                if m_positions:
                    min_d = min(math.hypot(tx-mx, ty-my) for mx, my in m_positions)
                    dists.append(min_d)
            avg_dist = sum(dists)/len(dists) if dists else D_map
            prox_score = max(0.0, 1.0 - min(avg_dist/D_map, 1.0))

        # 4. 几何平均融合
        factors = [f for f in [uni_t, uni_m, prox_score] if f>0]
        score = math.exp(sum(math.log(f) for f in factors)/len(factors)) if factors else 0.0

        detail: Dict[str, Any] = {
            'cv_treasure': cv_t,
            'uniformity_treasure': uni_t,
            'score': score
        }
        
        if monsters:
            detail.update({
                'cv_monster': cv_m,
                'uniformity_monster': uni_m,
                'avg_t2m_dist': avg_dist,
                'proximity_score': prox_score
            })
        else:
            detail.update({
                'cv_monster': 0.0,
                'uniformity_monster': 0.0,
                'avg_t2m_dist': 0.0,
                'proximity_score': 0.0,
                'note': 'Only treasure distribution evaluated (no monsters found)'
            })
            
        return score, detail 