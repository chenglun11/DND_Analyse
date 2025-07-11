"""
测试质量评估器
"""

import pytest
from unittest.mock import Mock, patch
from src.quality_assessor import DungeonQualityAssessor


@pytest.mark.unit
class TestDungeonQualityAssessor:
    """测试DungeonQualityAssessor类"""

    def test_initialization(self):
        """测试初始化"""
        assessor = DungeonQualityAssessor()
        assert hasattr(assessor, 'rules')
        assert hasattr(assessor, 'rule_weights')
        assert hasattr(assessor, 'enable_spatial_inference')
        assert hasattr(assessor, 'adjacency_threshold')

    def test_initialization_with_custom_weights(self):
        """测试自定义权重初始化"""
        custom_weights = {
            'accessibility': 0.5,
            'path_diversity': 0.5
        }
        assessor = DungeonQualityAssessor(rule_weights=custom_weights)
        assert assessor.rule_weights == custom_weights

    def test_initialization_with_spatial_inference_disabled(self):
        """测试禁用空间推断的初始化"""
        assessor = DungeonQualityAssessor(enable_spatial_inference=False)
        assert assessor.enable_spatial_inference is False

    def test_initialization_with_custom_threshold(self):
        """测试自定义阈值的初始化"""
        assessor = DungeonQualityAssessor(adjacency_threshold=2.0)
        assert assessor.adjacency_threshold == 2.0

    def test_load_rules(self):
        """测试规则加载"""
        assessor = DungeonQualityAssessor()
        assert len(assessor.rules) > 0
        # 验证每个规则都有必要的方法
        for rule in assessor.rules:
            assert hasattr(rule, 'name')
            assert hasattr(rule, 'evaluate')
            assert callable(rule.evaluate)

    def test_assess_quality_basic(self, unified_dungeon_data):
        """测试基本质量评估"""
        assessor = DungeonQualityAssessor()
        result = assessor.assess_quality(unified_dungeon_data)
        
        assert 'scores' in result
        assert 'overall_score' in result
        assert 'grade' in result
        assert 'details' in result
        assert 'recommendations' in result
        assert 'spatial_inference_used' in result
        
        assert isinstance(result['scores'], dict)
        assert isinstance(result['overall_score'], float)
        assert isinstance(result['grade'], str)
        assert isinstance(result['details'], dict)
        assert isinstance(result['recommendations'], list)
        assert isinstance(result['spatial_inference_used'], bool)

    def test_assess_quality_score_range(self, unified_dungeon_data):
        """测试评分范围"""
        assessor = DungeonQualityAssessor()
        result = assessor.assess_quality(unified_dungeon_data)
        
        # 总体评分应该在0-1之间
        assert 0.0 <= result['overall_score'] <= 1.0
        
        # 各项评分应该在0-1之间
        for rule_result in result['scores'].values():
            assert 0.0 <= rule_result['score'] <= 1.0

    def test_assess_quality_grade_assignment(self, unified_dungeon_data):
        """测试等级分配"""
        assessor = DungeonQualityAssessor()
        result = assessor.assess_quality(unified_dungeon_data)
        
        grade = result['grade']
        assert grade in ['A', 'B', 'C', 'D', 'F']

    def test_assess_quality_with_spatial_inference(self, unified_dungeon_data):
        """测试启用空间推断的评估"""
        assessor = DungeonQualityAssessor(enable_spatial_inference=True)
        result = assessor.assess_quality(unified_dungeon_data)
        
        # 应该包含空间推断使用情况
        assert 'spatial_inference_used' in result

    def test_assess_quality_without_spatial_inference(self, unified_dungeon_data):
        """测试禁用空间推断的评估"""
        assessor = DungeonQualityAssessor(enable_spatial_inference=False)
        result = assessor.assess_quality(unified_dungeon_data)
        
        # 空间推断应该被禁用
        assert result['spatial_inference_used'] is False

    def test_assess_quality_with_empty_dungeon(self):
        """测试空地牢的评估"""
        empty_dungeon = {
            "header": {
                "schemaName": "dnd-dungeon-unified",
                "schemaVersion": "1.0.0",
                "name": "Empty Dungeon",
                "author": "Test",
                "description": "Empty dungeon for testing",
                "grid": {"type": "square", "size": 5, "unit": "ft"}
            },
            "levels": []
        }
        
        assessor = DungeonQualityAssessor()
        result = assessor.assess_quality(empty_dungeon)
        
        # 应该能正常处理空地牢
        assert 'scores' in result
        assert 'overall_score' in result
        assert 'grade' in result

    def test_assess_quality_with_missing_levels(self):
        """测试缺少levels的评估"""
        incomplete_dungeon = {
            "header": {
                "schemaName": "dnd-dungeon-unified",
                "schemaVersion": "1.0.0",
                "name": "Incomplete Dungeon",
                "author": "Test",
                "description": "Dungeon without levels",
                "grid": {"type": "square", "size": 5, "unit": "ft"}
            }
        }
        
        assessor = DungeonQualityAssessor()
        result = assessor.assess_quality(incomplete_dungeon)
        
        # 应该能正常处理不完整的地牢
        assert 'scores' in result
        assert 'overall_score' in result

    def test_assess_quality_with_rule_exception(self, unified_dungeon_data):
        """测试规则评估时发生异常"""
        # 创建一个会抛出异常的规则
        mock_rule = Mock()
        mock_rule.name = "failing_rule"
        mock_rule.evaluate.side_effect = Exception("Test rule exception")
        
        assessor = DungeonQualityAssessor()
        # 临时添加会失败的规则
        assessor.rules.append(mock_rule)
        
        # 应该能正常处理规则异常
        result = assessor.assess_quality(unified_dungeon_data)
        assert 'scores' in result
        assert 'overall_score' in result

    def test_get_grade_methods(self):
        """测试等级分配方法"""
        assessor = DungeonQualityAssessor()
        
        # 测试不同分数对应的等级
        assert assessor._get_grade(0.9) == "A"
        assert assessor._get_grade(0.8) == "A"
        assert assessor._get_grade(0.7) == "B"
        assert assessor._get_grade(0.6) == "B"
        assert assessor._get_grade(0.5) == "C"
        assert assessor._get_grade(0.4) == "C"
        assert assessor._get_grade(0.3) == "D"
        assert assessor._get_grade(0.2) == "F"
        assert assessor._get_grade(0.0) == "F"

    def test_get_recommendations(self):
        """测试建议生成"""
        assessor = DungeonQualityAssessor()
        
        # 测试低分情况下的建议
        low_scores = {
            'accessibility': {'score': 0.3},
            'degree_variance': {'score': 0.4},
            'path_diversity': {'score': 0.2},
            'loop_ratio': {'score': 0.5},
            'door_distribution': {'score': 0.3},
            'treasure_monster_distribution': {'score': 0.4},
            'dead_end_ratio': {'score': 0.3},
            'aesthetic_balance': {'score': 0.5}
        }
        
        # 计算分类分数
        category_scores = assessor._calculate_category_scores(low_scores)
        
        recommendations = assessor._get_recommendations(low_scores, category_scores)
        assert len(recommendations) > 0
        assert all(isinstance(rec, str) for rec in recommendations)

    def test_weighted_scoring(self, unified_dungeon_data):
        """测试加权评分"""
        custom_weights = {
            'accessibility': 0.5,
            'degree_variance': 0.3,
            'path_diversity': 0.2
        }
        
        assessor = DungeonQualityAssessor(rule_weights=custom_weights)
        result = assessor.assess_quality(unified_dungeon_data)
        
        # 验证加权评分计算
        weighted_sum = 0.0
        total_weight = 0.0
        
        for rule_name, weight in custom_weights.items():
            if rule_name in result['scores']:
                weighted_sum += result['scores'][rule_name]['score'] * weight
                total_weight += weight
        
        expected_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        assert abs(result['overall_score'] - expected_score) < 0.01

    def test_zero_weights_handling(self, unified_dungeon_data):
        """测试零权重的处理"""
        zero_weights = {
            'accessibility': 0.0,
            'degree_variance': 0.0,
            'path_diversity': 0.0
        }
        
        assessor = DungeonQualityAssessor(rule_weights=zero_weights)
        result = assessor.assess_quality(unified_dungeon_data)
        
        # 当所有权重为0时，总体评分应该为0
        assert result['overall_score'] == 0.0 