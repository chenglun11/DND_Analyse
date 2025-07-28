from .base import BaseQualityRule
import math
from collections import defaultdict, deque
from typing import List, Set, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class LoopRatioRule(BaseQualityRule):
    """
    基于cyclomatic formula的客观loop ratio评估
    
    核心改进：
    1. 使用cyclomatic formula直接计算独立环数
    2. 移除Paton算法的复杂实现，提高性能
    3. 基于图论理论设计科学的评估指标
    4. 适用于大规模图的快速计算
    5. 使用sigmoid函数将loop ratio映射到0-1区间
    
    理论基础：
    - 环数公式：|E| - |V| + C，其中C是连通分量数
    - 通常C=1（连通图），所以环数 = |E| - |V| + 1
    - loop_ratio = 环数 / 节点数
    - 最终分数 = sigmoid(loop_ratio) 映射到0-1区间
    """
    
    @property
    def name(self):
        return "loop_ratio"
    
    @property
    def description(self):
        return "基于cyclomatic formula的客观loop ratio评估（高性能，sigmoid归一化）"

    def evaluate(self, dungeon_data):
        levels = dungeon_data.get('levels', [])
        if not levels:
            return 0.0, {"reason": "No level data"}
        level = levels[0]
        connections = level.get('connections', [])
        if not connections:
            return 0.0, {"reason": "No connection information"}
        
        # 构建图
        graph = self._build_graph(connections)
        if not graph:
            return 0.0, {"reason": "No valid graph constructed"}
        
        # 使用cyclomatic formula计算客观指标
        metrics = self._calculate_cyclomatic_metrics(graph)
        
        # 获取原始loop ratio
        raw_loop_ratio = metrics['loop_ratio']
        
        # 如果loop ratio为0，给予最小分数
        if raw_loop_ratio == 0:
            raw_loop_ratio = 0.1
        
        # 使用sigmoid函数将loop ratio映射到0-1区间
        # sigmoid(x) = 1 / (1 + e^(-x))
        # 为了更好的映射效果，我们使用 sigmoid(loop_ratio - 1)
        # 这样当loop_ratio=1时，sigmoid(0)=0.5，这是一个合理的中间值
        sigmoid_loop_ratio = self._sigmoid(raw_loop_ratio - 1)
        
        # 添加调试信息
        detail_info = {
            "total_rooms": metrics['vertices'],
            "total_edges": metrics['edges'],
            "connected_components": metrics['components_count'],
            "cyclomatic_number": metrics['cyclomatic_number'],
            "loop_ratio": raw_loop_ratio,
            "sigmoid_loop_ratio": sigmoid_loop_ratio,
            "algorithm": "Cyclomatic formula + Sigmoid normalization",
            "note": "Direct calculation using E - V + C formula, then sigmoid mapping to [0,1]",
            "score_breakdown": {
                "raw_loop_ratio": raw_loop_ratio,
                "sigmoid_loop_ratio": sigmoid_loop_ratio,
                "final_score": sigmoid_loop_ratio
            }
        }
        
        return sigmoid_loop_ratio, detail_info
    
    def _sigmoid(self, x: float) -> float:
        """
        计算sigmoid函数值
        sigmoid(x) = 1 / (1 + e^(-x))
        
        这个函数将任意实数映射到(0,1)区间
        - 当x很大时，sigmoid(x)接近1
        - 当x很小时，sigmoid(x)接近0
        - 当x=0时，sigmoid(0)=0.5
        """
        return 1.0 / (1.0 + math.exp(-x))
    
    def _build_graph(self, connections: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """构建无向图"""
        graph = defaultdict(list)
        for conn in connections:
            from_room = conn['from_room']
            to_room = conn['to_room']
            graph[from_room].append(to_room)
            graph[to_room].append(from_room)
        return dict(graph)
    
    def _calculate_cyclomatic_metrics(self, graph: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        使用cyclomatic formula计算客观指标
        
        核心公式：
        - 环数 = |E| - |V| + C
        - loop_ratio = 环数 / |V|
        """
        V = len(graph)  # 顶点数
        E = sum(len(neighbors) for neighbors in graph.values()) // 2  # 边数
        C = self._count_components(graph)  # 连通分量数
        
        # 计算cyclomatic number（独立环数）
        cyclomatic_number = E - V + C
        
        # 计算loop ratio
        loop_ratio = cyclomatic_number / V if V > 0 else 0.0
        
        # 其他有用的指标
        graph_density = E / (V * (V - 1) / 2) if V > 1 else 0.0
        average_degree = 2 * E / V if V > 0 else 0.0
        
        return {
            'vertices': V,
            'edges': E,
            'components_count': C,
            'cyclomatic_number': cyclomatic_number,
            'loop_ratio': loop_ratio,
            'graph_density': graph_density,
            'average_degree': average_degree,
            'is_connected': C == 1
        }
    
    def _count_components(self, graph: Dict[str, List[str]]) -> int:
        """计算连通分量数量"""
        if not graph:
            return 0
        
        visited = set()
        components = 0
        
        for node in graph:
            if node not in visited:
                components += 1
                queue = deque([node])
                visited.add(node)
                
                while queue:
                    current = queue.popleft()
                    for neighbor in graph[current]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
        
        return components
    
 