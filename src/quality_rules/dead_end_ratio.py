from .base import BaseQualityRule

class DeadEndRatioRule(BaseQualityRule):
    """
    Dead end ratio assessment based on player psychology and game design principles.
    
    Theoretical foundations:
    1. Player Psychology (Schell, 2008) - Exploration experience and frustration
    2. Game Design Theory (Fullerton, 2014) - Flow and engagement
    3. Environmental Psychology - Spatial exploration patterns
    
    References:
    - Schell, J. (2008). The art of game design.
    - Fullerton, T. (2014). Game design workshop.
    """
    
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
        
        # 提取所有房间ID - Based on graph theory analysis
        all_room_ids = set()
        for conn in connections:
            all_room_ids.add(conn['from_room'])
            all_room_ids.add(conn['to_room'])
        
        if not all_room_ids:
            return 0.0, {"reason": "No valid rooms found in connections"}
        
        # 计算每个房间的度数 - Based on network analysis
        degree = {room_id: 0 for room_id in all_room_ids}
        for conn in connections:
            if conn['from_room'] in degree:
                degree[conn['from_room']] += 1
            if conn['to_room'] in degree:
                degree[conn['to_room']] += 1
        
        # 死胡同：度数为1的房间 - Based on Schell (2008) exploration design
        dead_ends = [rid for rid, d in degree.items() if d == 1]
        dead_end_ratio = len(dead_ends) / len(all_room_ids) if all_room_ids else 0.0
        
        # 基于游戏设计理论的评分 - Based on Fullerton (2014) flow theory
        # 理论基础：适度的死胡同可以提供探索奖励，但过多会影响游戏体验
        # 理想范围：0.1-0.3 (10%-30%的死胡同比例)
        
        if dead_end_ratio <= 0.1:
            # 死胡同太少：缺乏探索奖励，线性惩罚 - Based on player psychology
            score = 0.7 + 0.3 * (dead_end_ratio / 0.1)
        elif 0.1 < dead_end_ratio <= 0.3:
            # 理想范围：满分 - Based on optimal exploration balance
            score = 1.0
        elif 0.3 < dead_end_ratio <= 0.5:
            # 死胡同较多：线性惩罚 - Based on frustration theory
            score = 1.0 - 0.5 * ((dead_end_ratio - 0.3) / 0.2)
        else:
            # 死胡同过多：严重惩罚 - Based on player experience research
            score = max(0.1, 0.5 - 0.4 * ((dead_end_ratio - 0.5) / 0.5))
        
        return score, {
            "dead_end_ratio": dead_end_ratio,
            "dead_end_count": len(dead_ends),
            "total_rooms": len(all_room_ids),
            "dead_end_rooms": dead_ends,
            "optimal_range": "0.1-0.3"
        } 