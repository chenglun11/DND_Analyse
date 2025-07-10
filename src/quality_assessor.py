"""
地牢地图质量评估框架
使用多种算法评估地牢地图的设计质量
"""

import logging
import os
import sys
import pkgutil
import importlib
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, deque
import math
from dataclasses import dataclass
from pathlib import Path

from .spatial_inference import auto_infer_connections

logger = logging.getLogger(__name__)
sys.path.append(os.path.dirname(__file__))
RULES_PATH = Path(__file__).parent / "quality_rules"

class DungeonQualityAssessor:
    """地牢地图质量评估器（插件式规则加载 + 空间推断）"""
    def __init__(self, rule_weights: Optional[Dict[str, float]] = None, enable_spatial_inference: bool = True, adjacency_threshold: float = 1.0):
        self.rules = self._load_rules()
        self.enable_spatial_inference = enable_spatial_inference
        self.adjacency_threshold = adjacency_threshold
        # 默认权重
        self.rule_weights = rule_weights or {
            'accessibility': 0.25,
            'degree_variance': 0.20,
            'path_diversity': 0.20,
            'loop_ratio': 0.15,
            'door_distribution': 0.20
        }

    def _load_rules(self) -> List:
        rules = []
        pkg_prefix = 'quality_rules'
        for _, modname, _ in pkgutil.iter_modules([str(RULES_PATH)]):
            if modname == 'base':
                continue
            module = importlib.import_module(f'{pkg_prefix}.{modname}')
            for attr in dir(module):
                obj = getattr(module, attr)
                if isinstance(obj, type) and hasattr(obj, 'evaluate') and hasattr(obj, 'name') and obj.name != 'base':
                    rules.append(obj())
        logger.info(f"Loaded quality assessment rules: {[r.name for r in rules]}")
        return rules

    def assess_quality(self, dungeon_data: Dict[str, Any]) -> Dict[str, Any]:
        """评估地牢地图质量，返回各项分数和聚合结果"""
        # 预处理：如果启用空间推断且没有连接信息，则自动补全
        if self.enable_spatial_inference:
            enhanced_data = auto_infer_connections(dungeon_data, self.adjacency_threshold)
            if enhanced_data != dungeon_data:
                logger.info("Spatial inference enabled, automatically complete connection information")
                dungeon_data = enhanced_data
        
        results = {}
        weighted_sum = 0.0
        total_weight = 0.0
        details = {}
        for rule in self.rules:
            score, detail = rule.evaluate(dungeon_data)
            results[rule.name] = score
            details[rule.name] = detail
            weight = self.rule_weights.get(rule.name, 0.0)
            weighted_sum += score * weight
            total_weight += weight
        overall_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        grade = self._get_grade(overall_score)
        return {
            'scores': results,
            'overall_score': overall_score,
            'grade': grade,
            'details': details,
            'recommendations': self._get_recommendations(results),
            'spatial_inference_used': self.enable_spatial_inference and any(level.get('connections_inferred', False) for level in dungeon_data.get('levels', []))
        }

    def _get_grade(self, score: float) -> str:
        if score >= 0.8:
            return "A"
        elif score >= 0.6:
            return "B"
        elif score >= 0.4:
            return "C"
        elif score >= 0.3:
            return "D"
        else:
            return "F"

    def _get_recommendations(self, scores: Dict[str, float]) -> List[str]:
        recs = []
        if scores.get('accessibility', 1) < 0.6:
            recs.append("Add more connections between rooms to improve accessibility")
        if scores.get('degree_variance', 1) < 0.6:
            recs.append("Balance the number of connections between rooms to avoid rooms with too many or too few connections")
        if scores.get('path_diversity', 1) < 0.6:
            recs.append("Add more path choices to provide more ways to reach the target")
        if scores.get('loop_ratio', 1) < 0.6:
            recs.append("Add more loop structures to improve the exploration of the map")
        if scores.get('door_distribution', 1) < 0.6:
            recs.append("Optimize the distribution of doors to ensure the rationality of room entrances")
        if not recs:
            recs.append("The map design is good, no major improvements are needed")
        return recs 