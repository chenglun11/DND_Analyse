"""
Dungeon map quality assessment framework
Uses multiple algorithms to evaluate dungeon map design quality
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
from .adapter_manager import AdapterManager

logger = logging.getLogger(__name__)
sys.path.append(os.path.dirname(__file__))
RULES_PATH = Path(__file__).parent / "quality_rules"

class DungeonQualityAssessor:
    """Dungeon map quality assessor (plugin rule loading + spatial inference)"""
    def __init__(self, rule_weights: Optional[Dict[str, float]] = None, enable_spatial_inference: bool = True, adjacency_threshold: float = 1.0):
        self.rules = self._load_rules()
        self.enable_spatial_inference = enable_spatial_inference
        self.adjacency_threshold = adjacency_threshold
        self.adapter_manager = AdapterManager()
        
        # 重新设计权重系统：按类别分组，每个类别内部等权
        self.rule_weights = rule_weights or {
            # 结构性指标 (Structural) - 7个指标，每个权重1/7
            'accessibility': 1.0/7,  
            'degree_variance': 1.0/7,
            'door_distribution': 1.0/7,
            'dead_end_ratio': 1.0/7,
            'key_path_length': 1.0/7,
            'loop_ratio': 1.0/7,
            'path_diversity': 1.0/7,
            
            # 可玩性指标 (Gameplay) - 1个指标
            'treasure_monster_distribution': 1.0,
            
            # 视觉性指标 (Geometric) - 1个指标
            'geometric_balance': 1.0
        }
        
        # 重新定义规则类别
        self.rule_categories = {
            'structural': ['accessibility', 'degree_variance', 'door_distribution', 'dead_end_ratio', 'key_path_length', 'loop_ratio', 'path_diversity'],
            'gameplay': ['treasure_monster_distribution'],
            'aesthetic': ['geometric_balance']
        }
        
        # 类别权重（等权融合）
        self.category_weights = {
            'structural': 1.0/3,  # 33.33%
            'gameplay': 1.0/3,    # 33.33%
            'aesthetic': 1.0/3    # 33.33%
        }

    def _load_rules(self) -> List:
        rules = []
        from .quality_rules.base import BaseQualityRule
        from .quality_rules.accessibility import AccessibilityRule
        from .quality_rules.degree_variance import DegreeVarianceRule
        from .quality_rules.door_distribution import DoorDistributionRule
        from .quality_rules.dead_end_ratio import DeadEndRatioRule
        from .quality_rules.key_path_length import KeyPathLengthRule
        from .quality_rules.loop_ratio import LoopRatioRule
        from .quality_rules.path_diversity import PathDiversityRule
        from .quality_rules.treasure_monster_distribution import TreasureMonsterDistributionRule
        from .quality_rules.geometric_balance import GeometricBalanceRule
        
        # Direct instantiation of all specific rule classes
        rule_classes = [
            AccessibilityRule,
            DegreeVarianceRule,
            DoorDistributionRule,
            DeadEndRatioRule,
            KeyPathLengthRule,
            LoopRatioRule,
            PathDiversityRule,
            TreasureMonsterDistributionRule,
            GeometricBalanceRule
        ]
        
        for rule_class in rule_classes:
            if issubclass(rule_class, BaseQualityRule) and rule_class is not BaseQualityRule:
                # 特殊处理DeadEndRatioRule，支持include_length参数
                if rule_class.__name__ == 'DeadEndRatioRule':
                    rules.append(rule_class(include_length=False))  # 默认不包含长度分析
                else:
                    rules.append(rule_class())
        
        logger.info(f"Loaded quality assessment rules: {[r.name for r in rules]}")
        return rules

    def assess_quality(self, dungeon_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess dungeon map quality, return scores and aggregated results"""
        # Auto-convert to unified format if needed
        if not self._is_unified_format(dungeon_data):
            logger.info("Converting to unified format")
            converted_data = self.adapter_manager.convert(
                dungeon_data, 
                enable_spatial_inference=self.enable_spatial_inference,
                adjacency_threshold=self.adjacency_threshold
            )
            if converted_data is None:
                logger.error("Failed to convert data to unified format")
                return self._create_empty_result("Format conversion failed")
            dungeon_data = converted_data
        
        # Preprocessing: if spatial inference is enabled and no connection info, auto-complete
        if self.enable_spatial_inference:
            enhanced_data = auto_infer_connections(dungeon_data, self.adjacency_threshold)
            if enhanced_data != dungeon_data:
                logger.info("Spatial inference enabled, automatically complete connection information")
                dungeon_data = enhanced_data
        
        results = {}
        details = {}
        
        # Calculate scores for each rule
        for rule in self.rules:
            try:
                score, detail = rule.evaluate(dungeon_data)
            except Exception as e:
                score = 0.0
                detail = {'reason': 'rule exception', 'exception': str(e)}
            results[rule.name] = {'score': score, 'detail': detail}
            details[rule.name] = detail
        
        # 1. 类别打分：计算三大类别的加权平均分
        category_scores = self._calculate_category_scores(results)
        
        # 2. 整体评分：对三大类别分进行等权融合
        overall_score = self._calculate_overall_score(category_scores)
        grade = self._get_grade(overall_score)
        
        return {
            'scores': results,
            'category_scores': category_scores,
            'overall_score': overall_score,
            'grade': grade,
            'details': details,
            # for test, recommendations is blocked.
            'recommendations': self._get_recommendations(results, category_scores),
            'spatial_inference_used': self.enable_spatial_inference and any(level.get('connections_inferred', False) for level in dungeon_data.get('levels', []))
        }
    
    def _is_unified_format(self, data: Dict[str, Any]) -> bool:
        """Check if data is already in unified format"""
        if 'header' in data and 'levels' in data:
            header = data['header']
            if (isinstance(header, dict) and 
                'schemaName' in header and 
                header.get('schemaName') == 'dnd-dungeon-unified'):
                return True
        return False
    
    def _create_empty_result(self, reason: str) -> Dict[str, Any]:
        """Create empty result for failed conversions"""
        empty_scores = {}
        for rule in self.rules:
            empty_scores[rule.name] = {'score': 0.0, 'detail': {'reason': reason}}
        
        return {
            'scores': empty_scores,
            'category_scores': {'structural': 0.0, 'gameplay': 0.0, 'aesthetic': 0.0},
            'overall_score': 0.0,
            'grade': 'F',
            'details': {},
            'recommendations': [f"转换失败: {reason}"],
            'spatial_inference_used': False
        }

    def _calculate_category_scores(self, results: Dict[str, Any]) -> Dict[str, float]:
        """
        类别打分：将结构性、可玩性、几何性分别加权平均，得出三级类别分
        
        结构性：Accessibility、Degree Variance、Door Distribution、Dead-end Ratio、Key Path Length、Loop Ratio、Path Diversity
        可玩性：Treasure Monster Distribution
        视觉性：Geometric Balance
        """
        category_scores = {}
        
        for category, rule_names in self.rule_categories.items():
            category_weight_sum = 0.0
            category_score_sum = 0.0
            
            for rule_name in rule_names:
                weight = self.rule_weights.get(rule_name, 0.0)
                score = results.get(rule_name, {}).get('score', 0.0)
                category_weight_sum += weight
                category_score_sum += score * weight
            
            # 计算类别加权平均分
            category_scores[category] = category_score_sum / category_weight_sum if category_weight_sum > 0 else 0.0
        
        return category_scores

    def _calculate_overall_score(self, category_scores: Dict[str, float]) -> float:
        """
        整体评分：对三大类别分再进行等权融合，得到最终整体分
        
        三大类别等权：结构性 33.33% + 可玩性 33.33% + 几何性 33.33%
        """
        overall_score = 0.0
        total_weight = 0.0
        
        for category, score in category_scores.items():
            weight = self.category_weights.get(category, 0.0)
            overall_score += score * weight
            total_weight += weight
        
        return overall_score / total_weight if total_weight > 0 else 0.0

    def _get_grade(self, score: float) -> str:
        """
        映射为字母等级（A–F）
        
        A: 0.80-1.00 (优秀)
        B: 0.65-0.79 (良好)
        C: 0.50-0.64 (中等)
        D: 0.35-0.49 (及格)
        E: 0.20-0.34 (不及格)
        F: 0.00-0.19 (很差)
        """
        if score >= 0.80:
            return "A"
        elif score >= 0.65:
            return "B"
        elif score >= 0.50:
            return "C"
        elif score >= 0.35:
            return "D"
        elif score >= 0.20:
            return "E"
        else:
            return "F"

    def _get_recommendations(self, scores: Dict[str, Any], category_scores: Dict[str, float]) -> List[str]:
        recs = []
        
        # Extract scores from new structure
        accessibility_score = scores.get('accessibility', {}).get('score', 1.0)
        degree_variance_score = scores.get('degree_variance', {}).get('score', 1.0)
        path_diversity_score = scores.get('path_diversity', {}).get('score', 1.0)
        loop_ratio_score = scores.get('loop_ratio', {}).get('score', 1.0)
        treasure_monster_score = scores.get('treasure_monster_distribution', {}).get('score', 1.0)
        door_distribution_score = scores.get('door_distribution', {}).get('score', 1.0)
        dead_end_score = scores.get('dead_end_ratio', {}).get('score', 1.0)
        aesthetic_score = scores.get('geometric_balance', {}).get('score', 1.0)
        key_path_score = scores.get('key_path_length', {}).get('score', 1.0)
        
        # Category-based recommendations
        structural_score = category_scores.get('structural', 1.0)
        gameplay_score = category_scores.get('gameplay', 1.0)
        aesthetic_score_category = category_scores.get('aesthetic', 1.0)
        
        # 结构性建议
        if structural_score < 0.5:
            recs.append("结构性评分较低：需要改善房间连通性和门的位置分布")
        if accessibility_score < 0.5:
            recs.append("可达性不足：增加房间间的连接以提高可达性")
        if degree_variance_score < 0.5:
            recs.append("连接度差异过大：平衡房间连接，避免某些房间连接过多或过少")
        if door_distribution_score < 0.5:
            recs.append("门分布不合理：改善门的分布以获得更好的流动感")
        if loop_ratio_score < 0.5:
            recs.append("循环比例不当：调整房间连接以优化循环结构")
        if path_diversity_score < 0.5:
            recs.append("路径多样性不足：增加路径选择以提供更多到达目标的方式")
        if dead_end_score < 0.5:
            recs.append("死胡同过多：减少死胡同以改善探索流程")
        if key_path_score < 0.5:
            recs.append("关键路径过短：增加关键路径长度以提供更好的游戏体验")
        
        # 可玩性建议
        if gameplay_score < 0.5:
            recs.append("可玩性评分较低：需要增强游戏元素分布和路径多样性")
        if treasure_monster_score < 0.5:
            recs.append("游戏元素分布不当：确保平衡的密度，添加Boss，并在地图上分散元素")
        
        # 视觉性建议
        if aesthetic_score_category < 0.5:
            recs.append("视觉性评分较低：需要考虑几何平衡和主题元素")
        if aesthetic_score < 0.5:
            recs.append("几何平衡不足：适度变化房间大小，确保良好的空间分布，并保持主题一致性")
        
        return recs 