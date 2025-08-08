import numpy as np
from .base import BaseQualityRule
import networkx as nx
import logging
from collections import defaultdict, deque
from typing import List, Dict, Any, Tuple, Optional
import random
import time

logger = logging.getLogger(__name__)

class PathDiversityRule(BaseQualityRule):
    """
    基于蒙特卡洛随机游走采样的客观路径多样性评估
    
    核心改进：
    1. 使用蒙特卡洛随机游走采样替代昂贵的路径枚举
    2. 基于图论理论设计客观的多样性指标
    3. 使用几何平均融合多个子指标，避免主观权重
    4. 自适应参数设置，基于图的客观属性
    5. 完全可配置的参数系统，支持不同使用场景
    
    理论基础：
    - Jaccard距离：测量路径拓扑多样性
    - Shannon熵：测量路径长度分布多样性  
    - 变异系数：测量路径长度变化多样性
    - 几何平均：客观融合多个子指标
    """
    
    def __init__(self, 
                 random_seed: int = 42,
                 timeout_seconds: int = 30):
        """
        初始化路径多样性规则
        
        Args:
            random_seed: 随机种子，确保可重复性
            timeout_seconds: 计算超时时间（秒）
        """
        self.random_seed = random_seed
        self.timeout_seconds = timeout_seconds
        # 创建独立的随机数生成器，避免影响全局状态
        self.rng = random.Random(random_seed)
    
    @property
    def name(self) -> str:
        return "path_diversity"

    @property
    def description(self) -> str:
        return "Adaptive path diversity assessment using Monte Carlo sampling with geometric mean fusion"

    def evaluate(self, dungeon_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        # 使用独立的随机数生成器，不设置全局种子
        levels = dungeon_data.get('levels', [])
        if not levels:
            return 0.0, {"reason": "No level data"}
        level = levels[0]
        rooms = level.get('rooms', [])
        corridors = level.get('corridors', [])
        connections = level.get('connections', [])
        
        if not rooms or not connections:
            return 0.0, {"reason": "No room or connection information"}
        
        # 1. 节点定义一致性：只使用房间作为源/汇节点
        # 构建包含所有节点的图（房间+走廊）
        graph = self._build_graph(connections)
        if not graph:
            return 0.0, {"reason": "No valid graph constructed"}
        
        # 获取所有房间ID（不仅仅是游戏元素房间）
        room_ids = list(graph.keys())
        if not room_ids:
            return 0.0, {"reason": "No rooms found"}
        
        # 2. 自适应参数设置
        adaptive_params = self._calculate_adaptive_parameters(graph, room_ids)
        
        # 3. 多轮采样
        start_time = time.time()
        timeout_seconds = self.timeout_seconds  # 30秒超时
        
        all_round_results = []
        detailed_analysis = {}
        
        # 基于图的客观属性确定采样参数
        graph_diameter = self._estimate_graph_diameter(graph, room_ids)
        total_pairs = len(room_ids) * (len(room_ids) - 1) // 2
        
        # 理论依据：采样数应该与图的复杂度成正比
        # 复杂度 = 节点数 × 平均度数 × 直径
        avg_degree = sum(len(graph[node]) for node in graph) / len(graph) if graph else 0
        graph_complexity = len(room_ids) * avg_degree * graph_diameter
        
        # 采样数：基于统计学理论确定最小样本量
        # 理论依据：对于大图，需要足够的采样保证统计显著性
        # 使用 Cochran's formula: n = Z²pq/e²，简化为节点数平方根的常数倍
        total_edges = sum(len(graph[node]) for node in graph) // 2
        min_samples_for_significance = max(50, int(len(room_ids) ** 0.5 * 10))
        target_samples = min(total_pairs, max(min_samples_for_significance, total_edges // 2))
        
        # 确定采样轮数：基于图的客观属性
        # 理论依据：轮数应该与图的直径成正比，确保路径覆盖
        num_rounds = max(1, min(graph_diameter, target_samples // 2))
        
        # 每轮采样对数：确保均匀分布
        pairs_per_round = max(1, target_samples // num_rounds)
        
        # 添加调试信息
        logger.info(f"采样参数: 直径={graph_diameter}, 总对数={total_pairs}, 目标采样={target_samples}, 轮数={num_rounds}, 每轮对数={pairs_per_round}")
        
        for round_idx in range(num_rounds):
            # 检查超时
            if time.time() - start_time > timeout_seconds:
                logger.warning(f"Path diversity analysis timeout after {round_idx} rounds")
                break
            
            round_results = self._single_round_sampling(
                graph, room_ids, adaptive_params, pairs_per_round, round_idx, start_time, timeout_seconds
            )
            
            if round_results:
                all_round_results.extend(round_results)
                detailed_analysis[f"round_{round_idx}"] = {
                    "pairs_analyzed": len(round_results),
                    "avg_diversity": np.mean([r['overall_diversity'] for r in round_results])
                }
        
        if not all_round_results:
            # 降级方案：使用基于中心性的简化多样性评估
            fallback_result = self._evaluate_fallback_diversity(graph, room_ids)
            if fallback_result is not None:
                return fallback_result
            return 0.0, {
                "reason": "No valid path pairs found and fallback diversity evaluation failed",
                "detailed_analysis": detailed_analysis,
                "timeout": time.time() - start_time > timeout_seconds
            }
        
        # 4. 计算总体统计
        diversities = [result['overall_diversity'] for result in all_round_results]
        avg_diversity = float(np.mean(diversities))
        std_diversity = float(np.std(diversities)) if len(diversities) > 1 else 0.0
        
        # 5. 鲁棒归一化
        score = self._robust_normalize(avg_diversity, diversities)
        
        logger.info(f"路径多样性分析: 平均多样性={avg_diversity:.4f}±{std_diversity:.4f}, 轮数={len(detailed_analysis)}")
        logger.info(f"分析了 {len(all_round_results)} 个房间对，耗时 {time.time() - start_time:.2f}秒")
        
        return score, {
            "avg_path_diversity": avg_diversity,
            "std_path_diversity": std_diversity,
            "max_path_diversity": max(diversities) if diversities else 0.0,
            "min_path_diversity": min(diversities) if diversities else 0.0,
            "total_pairs_analyzed": len(all_round_results),
            "rounds_completed": len(detailed_analysis),
            "detailed_analysis": detailed_analysis,
            "adaptive_params": adaptive_params,
            "algorithm": "Adaptive_random_walk_sampling",
            "sampling_strategy": f"Multi-round ({num_rounds} rounds, {pairs_per_round} pairs/round)",
            "normalization": "Robust_with_predefined_bounds",
            "fusion_method": "Geometric_mean_of_normalized_metrics",
            "performance": {
                "time_taken": time.time() - start_time,
                "timeout": time.time() - start_time > timeout_seconds
            }
        }
    
    def _build_graph(self, connections: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """构建无向图"""
        graph = defaultdict(list)
        for conn in connections:
            from_room = conn['from_room']
            to_room = conn['to_room']
            graph[from_room].append(to_room)
            graph[to_room].append(from_room)
        return dict(graph)
    
    def _calculate_adaptive_parameters(self, graph: Dict[str, List[str]], room_ids: List[str]) -> Dict[str, Any]:
        """
        根据图的性质自适应设置参数
        """
        V = len(graph)
        E = sum(len(neighbors) for neighbors in graph.values()) // 2
        
        # 计算图的直径（最长最短路径）
        diameter = self._estimate_graph_diameter(graph, room_ids)
        
        # 计算平均度数
        avg_degree = 2 * E / V if V > 0 else 0
        
        # 基于图的基本性质计算参数
        total_nodes = len(graph)
        
        # 游走次数：基于图的边数，确保足够的采样覆盖率
        # 每条边至少被采样一次的概率较高
        num_walks = max(1, min(total_nodes, E))
        
        # 最大游走长度：基于图的直径
        max_walk_length = diameter
        
        return {
            'num_walks': num_walks,
            'max_walk_length': max_walk_length,
            'graph_diameter': diameter,
            'avg_degree': avg_degree,
            'total_nodes': V,
            'total_edges': E
        }
    
    def _estimate_graph_diameter(self, graph: Dict[str, List[str]], room_ids: List[str]) -> int:
        """
        估计图的直径（采样方法）
        """
        if not room_ids:
            return 1
        
        # 随机选择一些房间对计算最短路径
        # 基于房间数量确定采样大小
        total_pairs = len(room_ids) * (len(room_ids) - 1) // 2
        sample_size = min(total_pairs, max(1, len(room_ids) // 2))
        max_distances = []
        
        for _ in range(sample_size):
            source = self.rng.choice(room_ids)
            target = self.rng.choice(room_ids)
            if source != target:
                distance = self._bfs_shortest_path_length(graph, source, target)
                if distance is not None:
                    max_distances.append(distance)
        
        return max(max_distances) if max_distances else 5
    
    def _bfs_shortest_path_length(self, graph: Dict[str, List[str]], source: str, target: str) -> int | None:
        """使用BFS计算最短路径长度"""
        if source not in graph or target not in graph:
            return None
        
        visited = set()
        queue = deque([(source, 0)])
        visited.add(source)
        
        while queue:
            current, distance = queue.popleft()
            
            if current == target:
                return distance
            
            for neighbor in graph[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, distance + 1))
        
        return None
    
    def _single_round_sampling(self, graph: Dict[str, List[str]], room_ids: List[str], 
                              params: Dict[str, Any], pairs_per_round: int, round_idx: int,
                              start_time: float, timeout_seconds: int) -> List[Dict[str, Any]]:
        """
        单轮采样 - 使用基于最中心路径的策略确保覆盖核心路径
        
        改进策略：
        1. 识别图的中心节点和外围节点
        2. 优先采样中心-外围路径（主干路径）
        3. 采样中心-中心路径（核心连接）
        4. 采样外围-外围路径（边缘多样性）
        5. 补充随机采样确保覆盖完整性
        """
        # 计算图的中心性信息
        centrality_info = self._calculate_graph_centrality(graph, room_ids)
        
        selected_pairs = []
        
        # 1. 优先采样主干路径：中心到外围 (40% 的采样)
        center_periphery_pairs = self._get_center_periphery_pairs(centrality_info)
        if center_periphery_pairs:
            self.rng.shuffle(center_periphery_pairs)
            main_path_samples = min(len(center_periphery_pairs), max(1, pairs_per_round * 2 // 5))
            selected_pairs.extend(center_periphery_pairs[:main_path_samples])
        
        # 2. 采样核心连接：中心到中心 (30% 的采样)
        center_center_pairs = self._get_center_center_pairs(centrality_info)
        if center_center_pairs:
            self.rng.shuffle(center_center_pairs)
            core_samples = min(len(center_center_pairs), max(1, pairs_per_round * 3 // 10))
            selected_pairs.extend(center_center_pairs[:core_samples])
        
        # 3. 采样边缘多样性：外围到外围 (20% 的采样)
        periphery_periphery_pairs = self._get_periphery_periphery_pairs(centrality_info)
        if periphery_periphery_pairs:
            self.rng.shuffle(periphery_periphery_pairs)
            edge_samples = min(len(periphery_periphery_pairs), max(1, pairs_per_round // 5))
            selected_pairs.extend(periphery_periphery_pairs[:edge_samples])
        
        # 4. 补充随机采样确保覆盖完整性 (10% 的采样)
        remaining_pairs = pairs_per_round - len(selected_pairs)
        if remaining_pairs > 0:
            all_pairs = [(room_ids[i], room_ids[j]) 
                        for i in range(len(room_ids)) 
                        for j in range(i+1, len(room_ids))]
            # 排除已选择的房间对
            existing_pairs_set = set(selected_pairs)
            remaining_candidates = [pair for pair in all_pairs if pair not in existing_pairs_set]
            
            if remaining_candidates:
                self.rng.shuffle(remaining_candidates)
                selected_pairs.extend(remaining_candidates[:remaining_pairs])
        
        round_results = []
        
        for source, target in selected_pairs:
            # 精细化超时检查
            if time.time() - start_time > timeout_seconds:
                logger.warning(f"Path diversity analysis timeout during round {round_idx}")
                break
                
            try:
                # 随机游走采样
                path_samples = self._random_walk_sampling(
                    graph, source, target, params['num_walks'], params['max_walk_length']
                )
                
                if not path_samples:
                    continue
                
                # 计算多样性指标
                diversity_metrics = self._calculate_path_diversity(path_samples)
                
                round_results.append({
                    'source': source,
                    'target': target,
                    'path_samples_count': len(path_samples),
                    'unique_paths': len(set(tuple(path) for path in path_samples)),
                    'overall_diversity': diversity_metrics['overall_diversity'],
                    'jaccard_avg': diversity_metrics['avg_jaccard_distance'],
                    'normalized_entropy': diversity_metrics['normalized_entropy'],
                    'normalized_variance': diversity_metrics['normalized_variance']
                })
                
            except Exception as e:
                logger.warning(f"Error in round {round_idx} for {source}->{target}: {e}")
                continue
        
        return round_results
    
    def _random_walk_sampling(self, graph: Dict[str, List[str]], source: str, target: str, 
                            num_walks: int, max_length: int) -> List[List[str]]:
        """随机游走采样"""
        if source not in graph or target not in graph:
            return []
        
        path_samples = []
        
        for _ in range(num_walks):
            path = self._single_random_walk(graph, source, target, max_length)
            if path:
                path_samples.append(path)
        
        return path_samples
    
    def _single_random_walk(self, graph: Dict[str, List[str]], source: str, target: str, 
                           max_length: int) -> List[str] | None:
        """单次随机游走"""
        if source not in graph or target not in graph:
            return None
        
        path = [source]
        current = source
        visited = {source}
        
        for _ in range(max_length):
            if current == target:
                return path
            
            neighbors = graph[current]
            if not neighbors:
                break
            
            # 智能选择策略
            unvisited_neighbors = [n for n in neighbors if n not in visited]
            
            if unvisited_neighbors:
                # 随机选择未访问的节点
                next_node = self.rng.choice(unvisited_neighbors)
            else:
                # 如果所有邻居都访问过，随机选择一个
                next_node = self.rng.choice(neighbors)
            
            path.append(next_node)
            current = next_node
            visited.add(next_node)
        
        return path if current == target else None
    
    def _calculate_graph_centrality(self, graph: Dict[str, List[str]], room_ids: List[str]) -> Dict[str, Any]:
        """
        计算图的中心性信息
        
        基于偏心率 (eccentricity) 的中心性分析：
        1. 偏心率 = 从该节点到其他所有节点的最大最短距离
        2. 中心节点 = 偏心率最小的节点
        3. 外围节点 = 偏心率最大的节点
        4. 中等节点 = 介于中心和外围之间的节点
        
        理论基础：Freeman, 1978; Harary, 1969
        """
        if not room_ids or len(room_ids) < 2:
            return {
                'center_nodes': room_ids[:1] if room_ids else [],
                'periphery_nodes': [],
                'medium_nodes': [],
                'eccentricities': {}
            }
        
        # 1. 计算每个节点的偏心率
        eccentricities = {}
        all_distances = {}
        
        for node in room_ids:
            distances = self._bfs_all_distances_from_node(graph, node)
            if not distances or len(distances) < 2:
                # 孤立节点或只连接到自己，设置默认偏心率
                eccentricities[node] = float('inf')
                all_distances[node] = {node: 0}
            else:
                all_distances[node] = distances
                eccentricities[node] = max(distances.values())
        
        # 过滤掉无限偏心率的节点（孤立节点）
        valid_eccentricities = {node: ecc for node, ecc in eccentricities.items() if ecc != float('inf')}
        
        if not valid_eccentricities:
            # 所有节点都是孤立的，返回默认结果
            return {
                'center_nodes': room_ids[:1] if room_ids else [],
                'periphery_nodes': [],
                'medium_nodes': room_ids[1:] if len(room_ids) > 1 else [],
                'eccentricities': eccentricities
            }
        
        # 2. 分类节点
        min_eccentricity = min(valid_eccentricities.values())
        max_eccentricity = max(valid_eccentricities.values())
        
        # 中心节点：偏心率最小
        center_nodes = [node for node, ecc in valid_eccentricities.items() if ecc == min_eccentricity]
        
        # 外围节点：偏心率最大
        periphery_nodes = [node for node, ecc in valid_eccentricities.items() if ecc == max_eccentricity]
        
        # 中等节点：介于中心和外围之间
        medium_nodes = [node for node, ecc in valid_eccentricities.items() 
                       if min_eccentricity < ecc < max_eccentricity]
        
        return {
            'center_nodes': center_nodes,
            'periphery_nodes': periphery_nodes,
            'medium_nodes': medium_nodes,
            'eccentricities': eccentricities,
            'graph_radius': min_eccentricity,  # 图的半径
            'graph_diameter': max_eccentricity  # 图的直径
        }
    
    def _bfs_all_distances_from_node(self, graph: Dict[str, List[str]], source: str) -> Dict[str, int]:
        """
        从指定节点计算到所有其他节点的最短距离
        
        Args:
            graph: 无向图
            source: 起始节点
            
        Returns:
            从source到所有可达节点的距离映射
        """
        if source not in graph:
            return {}
            
        visited = {source}
        queue = deque([(source, 0)])
        distances = {source: 0}
        
        while queue:
            node, dist = queue.popleft()
            for neighbor in graph[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    distances[neighbor] = dist + 1
                    queue.append((neighbor, dist + 1))
        
        return distances
    
    def _get_center_periphery_pairs(self, centrality_info: Dict[str, Any]) -> List[Tuple[str, str]]:
        """获取中心-外围节点对（主干路径）"""
        center_nodes = centrality_info['center_nodes']
        periphery_nodes = centrality_info['periphery_nodes']
        
        pairs = []
        for center in center_nodes:
            for periphery in periphery_nodes:
                if center != periphery:
                    pairs.append((center, periphery))
        
        return pairs
    
    def _get_center_center_pairs(self, centrality_info: Dict[str, Any]) -> List[Tuple[str, str]]:
        """获取中心-中心节点对（核心连接）"""
        center_nodes = centrality_info['center_nodes']
        medium_nodes = centrality_info['medium_nodes']
        
        pairs = []
        # 中心节点之间的连接
        for i, center1 in enumerate(center_nodes):
            for center2 in center_nodes[i+1:]:
                pairs.append((center1, center2))
        
        # 中心节点到中等节点的连接
        for center in center_nodes:
            for medium in medium_nodes:
                pairs.append((center, medium))
        
        return pairs
    
    def _get_periphery_periphery_pairs(self, centrality_info: Dict[str, Any]) -> List[Tuple[str, str]]:
        """获取外围-外围节点对（边缘多样性）"""
        periphery_nodes = centrality_info['periphery_nodes']
        medium_nodes = centrality_info['medium_nodes']
        
        pairs = []
        # 外围节点之间的连接
        for i, periphery1 in enumerate(periphery_nodes):
            for periphery2 in periphery_nodes[i+1:]:
                pairs.append((periphery1, periphery2))
        
        # 中等节点之间的连接
        for i, medium1 in enumerate(medium_nodes):
            for medium2 in medium_nodes[i+1:]:
                pairs.append((medium1, medium2))
        
        # 外围节点到中等节点的连接
        for periphery in periphery_nodes:
            for medium in medium_nodes:
                pairs.append((periphery, medium))
        
        return pairs
    
    def _evaluate_fallback_diversity(self, graph: Dict[str, List[str]], room_ids: List[str]) -> Tuple[float, Dict[str, Any]] | None:
        """
        降级方案：基于图结构特征的简化多样性评估
        
        当无法进行有效的路径采样时，使用图的结构特征来估算多样性：
        1. 连通性多样性：基于连通分量的分布
        2. 度分布多样性：基于节点度数的分布熵
        3. 距离分布多样性：基于节点间距离的变异系数
        
        这种方法不需要具体的路径采样，纯粹基于图的拓扑性质
        """
        if not graph or not room_ids or len(room_ids) < 2:
            return None
            
        try:
            # 1. 连通性多样性：分析连通分量
            connectivity_diversity = self._calculate_connectivity_diversity(graph, room_ids)
            
            # 2. 度分布多样性：分析节点度数分布
            degree_diversity = self._calculate_degree_diversity(graph, room_ids)
            
            # 3. 距离分布多样性：分析节点间距离分布
            distance_diversity = self._calculate_distance_diversity(graph, room_ids)
            
            # 几何平均融合（与正常情况保持一致）
            diversity_factors = [f for f in [connectivity_diversity, degree_diversity, distance_diversity] if f > 0]
            
            if diversity_factors:
                fallback_score = np.exp(np.mean(np.log(diversity_factors)))
            else:
                fallback_score = 0.0
            
            return fallback_score, {
                'connectivity_diversity': connectivity_diversity,
                'degree_diversity': degree_diversity, 
                'distance_diversity': distance_diversity,
                'fallback_score': fallback_score,
                'fallback_method': 'structural_diversity',
                'note': 'Used structural diversity fallback due to insufficient valid path samples',
                'algorithm': 'Structural_graph_analysis',
                'sampling_strategy': 'Fallback_topological_analysis'
            }
            
        except Exception as e:
            return None
    
    def _calculate_connectivity_diversity(self, graph: Dict[str, List[str]], room_ids: List[str]) -> float:
        """计算连通性多样性：基于连通分量的分布"""
        # 找到所有连通分量
        visited = set()
        components = []
        
        for room_id in room_ids:
            if room_id not in visited:
                # BFS找连通分量
                component = set()
                queue = deque([room_id])
                visited.add(room_id)
                component.add(room_id)
                
                while queue:
                    current = queue.popleft()
                    for neighbor in graph.get(current, []):
                        if neighbor not in visited and neighbor in room_ids:
                            visited.add(neighbor)
                            component.add(neighbor)
                            queue.append(neighbor)
                
                if component:
                    components.append(len(component))
        
        if not components or len(components) == 1:
            return 1.0 if len(components) == 1 else 0.0
        
        # 计算连通分量大小分布的熵
        total_nodes = sum(components)
        proportions = [size / total_nodes for size in components]
        entropy = -sum(p * np.log2(p + 1e-9) for p in proportions)
        max_entropy = np.log2(len(components))
        
        return entropy / max_entropy if max_entropy > 0 else 0.0
    
    def _calculate_degree_diversity(self, graph: Dict[str, List[str]], room_ids: List[str]) -> float:
        """计算度分布多样性：基于节点度数分布的熵"""
        degrees = [len(graph.get(room_id, [])) for room_id in room_ids]
        
        if not degrees:
            return 0.0
        
        # 计算度数分布
        from collections import Counter
        degree_counts = Counter(degrees)
        total_nodes = len(degrees)
        
        # 计算度分布的熵
        proportions = [count / total_nodes for count in degree_counts.values()]
        entropy = -sum(p * np.log2(p + 1e-9) for p in proportions)
        max_entropy = np.log2(len(degree_counts))
        
        return entropy / max_entropy if max_entropy > 0 else 0.0
    
    def _calculate_distance_diversity(self, graph: Dict[str, List[str]], room_ids: List[str]) -> float:
        """计算距离分布多样性：基于节点间距离的变异系数"""
        if len(room_ids) < 2:
            return 0.0
        
        # 采样一些节点对计算距离分布
        sample_size = min(len(room_ids) * 2, 50)  # 限制采样大小避免过度计算
        distances = []
        
        sampled_pairs = 0
        for i, room1 in enumerate(room_ids):
            if sampled_pairs >= sample_size:
                break
            for room2 in room_ids[i+1:]:
                if sampled_pairs >= sample_size:
                    break
                distance = self._bfs_shortest_path_length(graph, room1, room2)
                if distance is not None:
                    distances.append(distance)
                    sampled_pairs += 1
        
        if len(distances) < 2:
            return 0.0
        
        # 计算变异系数
        mean_distance = np.mean(distances)
        std_distance = np.std(distances)
        
        if mean_distance > 0:
            cv = std_distance / mean_distance
            # 归一化变异系数到 [0,1] 范围
            return min(1.0, cv / 2.0)  # 除以2是经验性的归一化
        else:
            return 0.0
    
    def _calculate_path_diversity(self, path_samples: List[List[str]]) -> Dict[str, float]:
        """计算路径多样性指标 - 主函数"""
        if not path_samples:
            return {
                'avg_jaccard_distance': 0.0,
                'normalized_entropy': 0.0,
                'normalized_variance': 0.0,
                'overall_diversity': 0.0
            }
        
        # 1. 计算原始指标
        raw_metrics = self._compute_raw_metrics(path_samples)
        
        # 2. 归一化指标
        normalized_metrics = self._normalize_metrics(raw_metrics)
        
        # 3. 融合指标
        overall_diversity = self._fuse_metrics(normalized_metrics)
        
        return {
            'avg_jaccard_distance': raw_metrics['avg_jaccard_distance'],
            'normalized_entropy': normalized_metrics['normalized_entropy'],
            'normalized_variance': normalized_metrics['normalized_variance'],
            'overall_diversity': overall_diversity
        }
    
    def _compute_raw_metrics(self, path_samples: List[List[str]]) -> Dict[str, Any]:
        """计算原始指标：Jaccard距离、熵、方差"""
        # 1. Jaccard距离
        jaccard_distances = []
        for i in range(len(path_samples)):
            for j in range(i+1, len(path_samples)):
                s1, s2 = set(path_samples[i]), set(path_samples[j])
                union = len(s1 | s2)
                jaccard = 1 - (len(s1 & s2) / union if union else 0)
                jaccard_distances.append(jaccard)
        
        avg_jaccard_distance = np.mean(jaccard_distances) if jaccard_distances else 0.0
        
        # 2. 路径熵
        lengths = [len(p) for p in path_samples]
        counts = defaultdict(int)
        for l in lengths:
            counts[l] += 1
        
        p_vals = np.array(list(counts.values())) / len(lengths)
        entropy = -np.sum(p_vals * np.log2(p_vals + 1e-9))
        
        # 3. 长度方差
        length_variance = np.var(lengths) if len(lengths) > 1 else 0.0
        
        return {
            'avg_jaccard_distance': avg_jaccard_distance,
            'entropy': entropy,
            'length_variance': length_variance,
            'lengths': lengths,
            'unique_lengths': len(counts)
        }
    
    def _normalize_metrics(self, raw_metrics: Dict[str, Any]) -> Dict[str, float]:
        """归一化指标到[0,1]范围"""
        # Jaccard距离天然在[0,1]范围内
        avg_jaccard_distance = raw_metrics['avg_jaccard_distance']
        
        # 熵归一化：基于理论最大熵
        entropy = raw_metrics['entropy']
        unique_lengths = raw_metrics['unique_lengths']
        max_entropy = np.log2(unique_lengths) if unique_lengths > 1 else 0.0
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0
        
        # 方差归一化：使用变异系数
        length_variance = raw_metrics['length_variance']
        lengths = raw_metrics['lengths']
        
        if len(lengths) > 1 and np.mean(lengths) > 0:
            cv = np.sqrt(length_variance) / np.mean(lengths)
            normalized_variance = cv
        else:
            normalized_variance = 0.0
        
        return {
            'normalized_entropy': normalized_entropy,
            'normalized_variance': normalized_variance
        }
    
    def _fuse_metrics(self, normalized_metrics: Dict[str, float]) -> float:
        """融合归一化指标：几何平均，纯客观处理"""
        diversity_factors = []
        
        # 只使用非零的指标进行几何平均
        # 理论依据：零值表示该维度没有多样性，应该被排除
        if normalized_metrics['normalized_entropy'] > 0:
            diversity_factors.append(normalized_metrics['normalized_entropy'])
        if normalized_metrics['normalized_variance'] > 0:
            diversity_factors.append(normalized_metrics['normalized_variance'])
        
        if diversity_factors:
            overall_diversity = np.exp(np.mean(np.log(diversity_factors)))
        else:
            # 如果所有指标都为0，返回0（表示没有多样性）
            overall_diversity = 0.0
        
        return overall_diversity
    
    def _robust_normalize(self, value: float, all_values: List[float]) -> float:
        """
        纯客观归一化：基于数据分布，不使用任何主观边界
        """
        if not all_values:
            return 0.0
        
        # 纯客观归一化：使用数据的实际分布
        if len(all_values) > 1:
            # 使用数据的实际范围进行归一化
            min_val = min(all_values)
            max_val = max(all_values)
            
            if max_val > min_val:
                normalized = (value - min_val) / (max_val - min_val)
                return max(0.0, min(1.0, normalized))
            else:
                return 0.0
        else:
            # 单个值的情况
            return 1.0 if value > 0 else 0.0 