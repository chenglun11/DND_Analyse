from .base import BaseQualityRule
import numpy as np
import math
from collections import defaultdict

class DegreeVarianceRule(BaseQualityRule):
    """
    Degree variance assessment based on network science and complex network theory.
    
    Theoretical foundations:
    1. Network Science (Newman, 2010) - Degree distribution analysis
    2. Complex Network Theory (Barabási, 2016) - Network topology metrics
    3. Graph Theory - Node connectivity balance
    
    References:
    - Newman, M. E. J. (2010). Networks: An introduction.
    - Barabási, A. L. (2016). Network science.
    """
    
    @property
    def name(self):
        return "degree_variance"
    
    @property
    def description(self):
        return "度方差评分，适中最好（1.0~3.0最佳）"

    def evaluate(self, dungeon_data):
        levels = dungeon_data.get('levels', [])
        if not levels:
            return 0.0, {"reason": "No level data"}
        level = levels[0]
        rooms = level.get('rooms', [])
        corridors = level.get('corridors', [])
        connections = level.get('connections', [])
        all_nodes = rooms + corridors
        if not all_nodes or not connections:
            return 0.0, {"reason": "No room or connection information"}
        
        # 统计每个节点的度 - Based on Newman (2010) degree analysis
        degree = defaultdict(int)
        for conn in connections:
            degree[conn['from_room']] += 1
            degree[conn['to_room']] += 1
        degrees = [degree[node['id']] for node in all_nodes]
        degree_var = float(np.var(degrees)) if degrees else 0.0
        mean_degree = float(np.mean(degrees)) if degrees else 0.0
        complexity_factor = min(1.0, len(rooms) / 6.0)
        
        # 高斯型映射，中心2.0，σ=1.5（更宽松）- Based on Barabási (2016) network metrics
        mu, sigma = 2.0, 1.5
        score = math.exp(-((degree_var-mu)**2)/(2*sigma**2)) * complexity_factor
        
        return score, {
            "degree_variance": degree_var, 
            "mean_degree": mean_degree, 
            "complexity_factor": complexity_factor, 
            "degrees": degrees
        } 