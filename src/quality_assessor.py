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

logger = logging.getLogger(__name__)
sys.path.append(os.path.dirname(__file__))
RULES_PATH = Path(__file__).parent / "quality_rules"

class DungeonQualityAssessor:
    """Dungeon map quality assessor (plugin rule loading + spatial inference)"""
    def __init__(self, rule_weights: Optional[Dict[str, float]] = None, enable_spatial_inference: bool = True, adjacency_threshold: float = 1.0):
        self.rules = self._load_rules()
        self.enable_spatial_inference = enable_spatial_inference
        self.adjacency_threshold = adjacency_threshold
        
        # Categorized rule weights with balanced distribution
        self.rule_weights = rule_weights or {
            # Structural rules (40% total)
            'accessibility': 0.15,
            'degree_variance': 0.10,
            'door_distribution': 0.10,
            'loop_ratio': 0.05,
            
            # Gameplay rules (40% total)
            'path_diversity': 0.15,
            'treasure_monster_distribution': 0.20,
            'dead_end_ratio': 0.05,
            
            # Aesthetic rules (20% total)
            'aesthetic_balance': 0.20
        }
        
        # Rule categories for better organization
        self.rule_categories = {
            'structural': ['accessibility', 'degree_variance', 'door_distribution', 'loop_ratio'],
            'gameplay': ['path_diversity', 'treasure_monster_distribution', 'dead_end_ratio'],
            'aesthetic': ['aesthetic_balance']
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
        from .quality_rules.aesthetic_balance import AestheticBalanceRule
        
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
            AestheticBalanceRule
        ]
        
        for rule_class in rule_classes:
            if issubclass(rule_class, BaseQualityRule) and rule_class is not BaseQualityRule:
                rules.append(rule_class())
        
        logger.info(f"Loaded quality assessment rules: {[r.name for r in rules]}")
        return rules

    def assess_quality(self, dungeon_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess dungeon map quality, return scores and aggregated results"""
        # Preprocessing: if spatial inference is enabled and no connection info, auto-complete
        if self.enable_spatial_inference:
            enhanced_data = auto_infer_connections(dungeon_data, self.adjacency_threshold)
            if enhanced_data != dungeon_data:
                logger.info("Spatial inference enabled, automatically complete connection information")
                dungeon_data = enhanced_data
        
        results = {}
        weighted_sum = 0.0
        total_weight = 0.0
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
            weight = self.rule_weights.get(rule.name, 0.0)
            weighted_sum += score * weight
            total_weight += weight
        
        overall_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        grade = self._get_grade(overall_score)
        
        # Calculate category scores
        category_scores = self._calculate_category_scores(results)
        
        return {
            'scores': results,
            'category_scores': category_scores,
            'overall_score': overall_score,
            'grade': grade,
            'details': details,
            'recommendations': self._get_recommendations(results, category_scores),
            'spatial_inference_used': self.enable_spatial_inference and any(level.get('connections_inferred', False) for level in dungeon_data.get('levels', []))
        }

    def _calculate_category_scores(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate scores for each category"""
        category_scores = {}
        
        for category, rule_names in self.rule_categories.items():
            category_weight_sum = 0.0
            category_score_sum = 0.0
            
            for rule_name in rule_names:
                weight = self.rule_weights.get(rule_name, 0.0)
                score = results.get(rule_name, {}).get('score', 0.0)
                category_weight_sum += weight
                category_score_sum += score * weight
            
            category_scores[category] = category_score_sum / category_weight_sum if category_weight_sum > 0 else 0.0
        
        return category_scores

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
        aesthetic_score = scores.get('aesthetic_balance', {}).get('score', 1.0)
        
        # Category-based recommendations
        structural_score = category_scores.get('structural', 1.0)
        gameplay_score = category_scores.get('gameplay', 1.0)
        aesthetic_score_category = category_scores.get('aesthetic', 1.0)
        
        # Structural recommendations
        if structural_score < 0.6:
            recs.append("Structural issues detected: improve room connectivity and door placement")
        if accessibility_score < 0.6:
            recs.append("Add more connections between rooms to improve accessibility")
        if degree_variance_score < 0.6:
            recs.append("Balance room connections to avoid rooms with too many or too few connections")
        if door_distribution_score < 0.6:
            recs.append("Improve door distribution for better flow")
        
        # Gameplay recommendations
        if gameplay_score < 0.6:
            recs.append("Gameplay issues detected: enhance path diversity and element distribution")
        if path_diversity_score < 0.6:
            recs.append("Add more path choices to provide more ways to reach the target")
        if treasure_monster_score < 0.6:
            recs.append("Improve treasure and monster distribution: ensure balanced density, add bosses, and spread elements spatially")
        if dead_end_score < 0.6:
            recs.append("Reduce dead ends for better exploration flow")
        
        # Aesthetic recommendations
        if aesthetic_score_category < 0.6:
            recs.append("Aesthetic issues detected: consider visual balance and thematic elements")
        if aesthetic_score < 0.6:
            recs.append("Improve visual balance: vary room sizes moderately, ensure good spatial distribution, and maintain thematic consistency")
        
        return recs 