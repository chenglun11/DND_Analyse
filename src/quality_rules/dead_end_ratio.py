from .base import BaseQualityRule

class DeadEndRatioRule(BaseQualityRule):
    @property
    def name(self):
        return "dead_end_ratio"
    
    @property
    def description(self):
        return "评估死胡同比例的合理性，平衡探索体验和挑战性"

    def evaluate(self, dungeon_data):
        levels = dungeon_data.get('levels', [])
        if not levels:
            return 0.0, {"reason": "No level data"}
        level = levels[0]
        connections = level.get('connections', [])
        if not connections:
            return 0.0, {"reason": "No connection information"}
        
        # 提取所有房间ID
        all_room_ids = set()
        for conn in connections:
            all_room_ids.add(conn['from_room'])
            all_room_ids.add(conn['to_room'])
        
        if not all_room_ids:
            return 0.0, {"reason": "No valid rooms found in connections"}
        
        # 计算每个房间的度数
        degree = {room_id: 0 for room_id in all_room_ids}
        for conn in connections:
            if conn['from_room'] in degree:
                degree[conn['from_room']] += 1
            if conn['to_room'] in degree:
                degree[conn['to_room']] += 1
        
        # 死胡同：度数为1的房间
        dead_ends = [rid for rid, d in degree.items() if d == 1]
        dead_end_ratio = len(dead_ends) / len(all_room_ids) if all_room_ids else 0.0
        
        # 基于游戏设计理论的评分
        # 理论基础：适度的死胡同可以提供探索奖励，但过多会影响游戏体验
        # 理想范围：0.1-0.3 (10%-30%的死胡同比例)
        
        if dead_end_ratio <= 0.1:
            # 死胡同太少：缺乏探索奖励，线性惩罚
            score = 0.7 + 0.3 * (dead_end_ratio / 0.1)
        elif 0.1 < dead_end_ratio <= 0.3:
            # 理想范围：满分
            score = 1.0
        elif 0.3 < dead_end_ratio <= 0.5:
            # 死胡同较多：线性惩罚
            score = 1.0 - 0.5 * ((dead_end_ratio - 0.3) / 0.2)
        else:
            # 死胡同过多：严重惩罚
            score = max(0.1, 0.5 - 0.4 * ((dead_end_ratio - 0.5) / 0.5))
        
        # 复杂度因子：大地牢可以容忍更多死胡同
        room_count = len(all_room_ids)
        if room_count <= 5:
            complexity_factor = 0.8  # 小地牢对死胡同更敏感
        elif room_count <= 15:
            complexity_factor = 0.9
        elif room_count <= 30:
            complexity_factor = 1.0
        else:
            complexity_factor = 1.1  # 大地牢可以容忍更多死胡同
        
        final_score = min(1.0, score * complexity_factor)
        
        return final_score, {
            "dead_end_count": len(dead_ends), 
            "dead_end_ratio": dead_end_ratio, 
            "dead_end_rooms": dead_ends,
            "total_rooms": len(all_room_ids),
            "all_rooms": list(all_room_ids),
            "score_breakdown": {
                "base_score": score,
                "complexity_factor": complexity_factor,
                "final_score": final_score
            },
            "assessment": self._get_assessment(dead_end_ratio, room_count)
        }
    
    def _get_assessment(self, dead_end_ratio, room_count):
        """根据死胡同比例和房间数量提供评估建议"""
        if dead_end_ratio <= 0.1:
            if room_count <= 10:
                return "死胡同过少，考虑添加一些探索分支以增加探索奖励"
            else:
                return "死胡同比例偏低，大地牢可以适当增加一些死胡同"
        elif dead_end_ratio <= 0.3:
            return "死胡同比例合理，提供了良好的探索体验"
        elif dead_end_ratio <= 0.5:
            return "死胡同较多，考虑减少一些死胡同或增加连接"
        else:
            return "死胡同过多，严重影响探索体验，建议大幅减少死胡同数量" 