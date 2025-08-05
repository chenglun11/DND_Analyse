from .base import BaseQualityRule
import math
from collections import defaultdict
from typing import Dict, Any, Tuple, List

class GeometricBalanceRule(BaseQualityRule):
    """
    Geometric balance assessment: 客观评估地牢布局的几何平衡性

    子指标:
      1. symmetry_ratio: 左右/上下对称度 (0-1)
      2. area_uniformity: 房间面积均匀度 (1 - CV_norm)
      3. spacing_evenness: 相邻房间中心间距均匀度 (1 - CV_norm)

    融合: 几何平均，仅使用非零因子
    """
    
    @property
    def name(self) -> str:
        return "geometric_balance"

    @property
    def description(self) -> str:
        return "Objective assessment of geometric balance in dungeon layout"

    def evaluate(self, dungeon_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        levels = dungeon_data.get('levels', [])
        if not levels:
            return 0.0, {"reason": "No level data"}
        level = levels[0]
        rooms = level.get('rooms', [])
        connections = level.get('connections', [])
        if not rooms:
            return 0.0, {"reason": "No rooms"}

        # 1. 对称性：基于房间中心左右对称匹配
        xs = [r['position']['x'] + r.get('size', {}).get('width',0)/2 for r in rooms]
        ys = [r['position']['y'] + r.get('size', {}).get('height',0)/2 for r in rooms]
        min_x, max_x = min(xs), max(xs)
        mid_x = (min_x + max_x) / 2
        matched = 0
        coords = [(x,y) for x,y in zip(xs,ys)]
        tol = (max_x - min_x) * 0.01 if max_x>min_x else 1.0
        for x,y in coords:
            mirror = (2*mid_x - x, y)
            # 查找是否有近似坐标
            for xx,yy in coords:
                if abs(xx - mirror[0])<=tol and abs(yy - mirror[1])<=tol:
                    matched += 1
                    break
        symmetry_ratio = matched / len(coords) if coords else 0.0

        # 2. 面积均匀度: 1 - CV_norm
        areas = []
        for r in rooms:
            w = r.get('size', {}).get('width', 0)
            h = r.get('size', {}).get('height', 0)
            areas.append(w*h)
        uni_area = self._uniformity_from_values(areas)

        # 3. 间距均匀度: 邻接房间中心距离CV->1-CV_norm
        # 构建图获取相连房间对
        from collections import defaultdict
        adj = defaultdict(list)
        pos_map = {r['id']:(r['position']['x'] + r.get('size',{}).get('width',0)/2,
                           r['position']['y'] + r.get('size',{}).get('height',0)/2)
                   for r in rooms}
        
        # 只处理在pos_map中的房间连接
        valid_connections = 0
        for c in connections:
            u,v = c['from_room'], c['to_room']
            if u in pos_map and v in pos_map:
                adj[u].append(v)
                adj[v].append(u)
                valid_connections += 1
        
        dists = []
        if valid_connections > 0:
            # 使用连接房间之间的距离
            for u, neighs in adj.items():
                ux,uy = pos_map[u]
                for v in neighs:
                    vx,vy = pos_map[v]
                    dists.append(math.hypot(vx-ux, vy-uy))
        else:
            # 如果没有有效连接，使用所有房间对之间的距离
            room_ids = list(pos_map.keys())
            for i in range(len(room_ids)):
                for j in range(i+1, len(room_ids)):
                    ux,uy = pos_map[room_ids[i]]
                    vx,vy = pos_map[room_ids[j]]
                    dists.append(math.hypot(vx-ux, vy-uy))
        uni_spacing = self._uniformity_from_values(dists)

        # 融合几何平均
        factors = [f for f in [symmetry_ratio, uni_area, uni_spacing] if f>0]
        score = math.exp(sum(math.log(f) for f in factors)/len(factors)) if factors else 0.0

        return score, {
            'symmetry_ratio': symmetry_ratio,
            'uniformity_area': uni_area,
            'uniformity_spacing': uni_spacing,
            'score': score
        }

    def _uniformity_from_values(self, values: List[float]) -> float:
        """
        计算均匀度：1 - CV_norm，CV = σ/μ，理论最大CV = sqrt(n-1)
        """
        n = len(values)
        if n==0:
            return 0.0
        mean = sum(values)/n
        var = sum((v-mean)**2 for v in values)/n
        cv = math.sqrt(var)/mean if mean>0 else 0.0
        max_cv = math.sqrt(n-1) if n>1 else 1.0
        uni = max(0.0, 1.0 - min(cv/max_cv, 1.0))
        return uni 