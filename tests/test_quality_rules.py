"""
测试质量评估规则
"""

import pytest
from src.quality_rules.base import BaseQualityRule


@pytest.mark.unit
class TestBaseQualityRule:
    """测试BaseQualityRule基类"""

    def test_abstract_methods(self):
        """测试抽象方法定义"""
        # 不能直接实例化抽象类
        with pytest.raises(TypeError):
            BaseQualityRule()

    def test_concrete_rule_implementation(self):
        """测试具体规则实现"""
        class TestRule(BaseQualityRule):
            name = "test_rule"
            description = "A test rule"
            
            def evaluate(self, dungeon_data):
                return 0.5, {"test": "data"}
        
        rule = TestRule()
        assert rule.name == "test_rule"
        assert rule.description == "A test rule"
        
        # 测试评估方法
        test_data = {"test": "dungeon"}
        score, detail = rule.evaluate(test_data)
        assert score == 0.5
        assert detail == {"test": "data"}


@pytest.mark.unit
class TestAccessibilityRule:
    """测试可达性规则"""

    def test_rule_loading(self):
        """测试规则加载"""
        from src.quality_rules.accessibility import AccessibilityRule
        rule = AccessibilityRule()
        assert rule.name == "accessibility"
        assert hasattr(rule, 'evaluate')

    def test_evaluate_connected_dungeon(self, unified_dungeon_data):
        """测试连接良好的地牢"""
        from src.quality_rules.accessibility import AccessibilityRule
        rule = AccessibilityRule()
        score, detail = rule.evaluate(unified_dungeon_data)

        assert 0.0 <= score <= 1.0
        assert isinstance(detail, dict)
        if "connected_rooms" in detail:
            assert isinstance(detail["connected_rooms"], list)
        else:
            assert "reason" in detail

    def test_evaluate_disconnected_dungeon(self):
        """测试不连接的地牢"""
        from src.quality_rules.accessibility import AccessibilityRule
        rule = AccessibilityRule()
        
        # 创建不连接的地牢
        disconnected_dungeon = {
            "header": {
                "schemaName": "dnd-dungeon-unified",
                "schemaVersion": "1.0.0",
                "name": "Disconnected Dungeon",
                "author": "Test",
                "description": "Dungeon with disconnected rooms",
                "grid": {"type": "square", "size": 5, "unit": "ft"}
            },
            "levels": [
                {
                    "id": "level_1",
                    "name": "Main Level",
                    "map": {"width": 50, "height": 50},
                    "rooms": [
                        {
                            "id": "room_1",
                            "shape": "rectangle",
                            "position": {"x": 10, "y": 10},
                            "size": {"width": 8, "height": 6},
                            "name": "Room 1"
                        },
                        {
                            "id": "room_2",
                            "shape": "rectangle",
                            "position": {"x": 30, "y": 30},
                            "size": {"width": 8, "height": 6},
                            "name": "Room 2"
                        }
                    ],
                    "doors": [],
                    "corridors": []
                }
            ]
        }
        
        score, detail = rule.evaluate(disconnected_dungeon)
        assert score == 0.0  # 不连接的房间应该得0分

    def test_evaluate_empty_dungeon(self):
        """测试空地牢"""
        from src.quality_rules.accessibility import AccessibilityRule
        rule = AccessibilityRule()
        
        empty_dungeon = {
            "header": {
                "schemaName": "dnd-dungeon-unified",
                "schemaVersion": "1.0.0",
                "name": "Empty Dungeon",
                "author": "Test",
                "description": "Empty dungeon",
                "grid": {"type": "square", "size": 5, "unit": "ft"}
            },
            "levels": []
        }
        
        score, detail = rule.evaluate(empty_dungeon)
        assert score == 0.0


@pytest.mark.unit
class TestPathDiversityRule:
    """测试路径多样性规则"""

    def test_rule_loading(self):
        """测试规则加载"""
        from src.quality_rules.path_diversity import PathDiversityRule
        rule = PathDiversityRule()
        assert rule.name == "path_diversity"
        assert hasattr(rule, 'evaluate')

    def test_evaluate_simple_path(self, unified_dungeon_data):
        """测试简单路径"""
        from src.quality_rules.path_diversity import PathDiversityRule
        rule = PathDiversityRule()
        score, detail = rule.evaluate(unified_dungeon_data)

        assert 0.0 <= score <= 1.0
        assert isinstance(detail, dict)
        if "path_count" in detail:
            assert isinstance(detail["path_count"], int)
        else:
            assert "reason" in detail

    def test_evaluate_complex_path(self):
        """测试复杂路径"""
        from src.quality_rules.path_diversity import PathDiversityRule
        rule = PathDiversityRule()
        
        # 创建有多个路径的地牢
        complex_dungeon = {
            "header": {
                "schemaName": "dnd-dungeon-unified",
                "schemaVersion": "1.0.0",
                "name": "Complex Dungeon",
                "author": "Test",
                "description": "Dungeon with multiple paths",
                "grid": {"type": "square", "size": 5, "unit": "ft"}
            },
            "levels": [
                {
                    "id": "level_1",
                    "name": "Main Level",
                    "map": {"width": 50, "height": 50},
                    "rooms": [
                        {
                            "id": "room_1",
                            "shape": "rectangle",
                            "position": {"x": 10, "y": 10},
                            "size": {"width": 8, "height": 6},
                            "name": "Start"
                        },
                        {
                            "id": "room_2",
                            "shape": "rectangle",
                            "position": {"x": 25, "y": 10},
                            "size": {"width": 8, "height": 6},
                            "name": "Middle 1"
                        },
                        {
                            "id": "room_3",
                            "shape": "rectangle",
                            "position": {"x": 40, "y": 10},
                            "size": {"width": 8, "height": 6},
                            "name": "Middle 2"
                        },
                        {
                            "id": "room_4",
                            "shape": "rectangle",
                            "position": {"x": 25, "y": 25},
                            "size": {"width": 8, "height": 6},
                            "name": "End"
                        }
                    ],
                    "doors": [
                        {"id": "door_1", "position": {"x": 18, "y": 13}, "connects": ["room_1", "room_2"]},
                        {"id": "door_2", "position": {"x": 33, "y": 13}, "connects": ["room_2", "room_3"]},
                        {"id": "door_3", "position": {"x": 29, "y": 28}, "connects": ["room_2", "room_4"]},
                        {"id": "door_4", "position": {"x": 44, "y": 28}, "connects": ["room_3", "room_4"]}
                    ],
                    "corridors": []
                }
            ]
        }
        
        score, detail = rule.evaluate(complex_dungeon)
        assert 0.0 <= score <= 1.0
        if "path_count" in detail and isinstance(detail["path_count"], int):
            assert detail["path_count"] > 1  # 应该有多个路径
        else:
            assert "reason" in detail


@pytest.mark.unit
class TestLoopRatioRule:
    """测试回环率规则"""

    def test_rule_loading(self):
        """测试规则加载"""
        from src.quality_rules.loop_ratio import LoopRatioRule
        rule = LoopRatioRule()
        assert rule.name == "loop_ratio"
        assert hasattr(rule, 'evaluate')

    def test_evaluate_linear_dungeon(self, unified_dungeon_data):
        """测试线性地牢"""
        from src.quality_rules.loop_ratio import LoopRatioRule
        rule = LoopRatioRule()
        score, detail = rule.evaluate(unified_dungeon_data)

        assert 0.0 <= score <= 1.0
        assert isinstance(detail, dict)
        if "loop_count" in detail:
            assert isinstance(detail["loop_count"], int)
        else:
            assert "reason" in detail

    def test_evaluate_loopy_dungeon(self):
        """测试有回环的地牢"""
        from src.quality_rules.loop_ratio import LoopRatioRule
        rule = LoopRatioRule()
        
        # 创建有回环的地牢
        loopy_dungeon = {
            "header": {
                "schemaName": "dnd-dungeon-unified",
                "schemaVersion": "1.0.0",
                "name": "Loopy Dungeon",
                "author": "Test",
                "description": "Dungeon with loops",
                "grid": {"type": "square", "size": 5, "unit": "ft"}
            },
            "levels": [
                {
                    "id": "level_1",
                    "name": "Main Level",
                    "map": {"width": 50, "height": 50},
                    "rooms": [
                        {
                            "id": "room_1",
                            "shape": "rectangle",
                            "position": {"x": 10, "y": 10},
                            "size": {"width": 8, "height": 6},
                            "name": "Center"
                        },
                        {
                            "id": "room_2",
                            "shape": "rectangle",
                            "position": {"x": 25, "y": 10},
                            "size": {"width": 8, "height": 6},
                            "name": "North"
                        },
                        {
                            "id": "room_3",
                            "shape": "rectangle",
                            "position": {"x": 25, "y": 25},
                            "size": {"width": 8, "height": 6},
                            "name": "East"
                        },
                        {
                            "id": "room_4",
                            "shape": "rectangle",
                            "position": {"x": 10, "y": 25},
                            "size": {"width": 8, "height": 6},
                            "name": "South"
                        }
                    ],
                    "doors": [
                        {"id": "door_1", "position": {"x": 18, "y": 13}, "connects": ["room_1", "room_2"]},
                        {"id": "door_2", "position": {"x": 29, "y": 13}, "connects": ["room_2", "room_3"]},
                        {"id": "door_3", "position": {"x": 18, "y": 28}, "connects": ["room_3", "room_4"]},
                        {"id": "door_4", "position": {"x": 14, "y": 19}, "connects": ["room_4", "room_1"]}
                    ],
                    "corridors": []
                }
            ]
        }
        
        score, detail = rule.evaluate(loopy_dungeon)
        assert 0.0 <= score <= 1.0
        if "loop_count" in detail and isinstance(detail["loop_count"], int):
            assert detail["loop_count"] > 0  # 应该有回环
        else:
            assert "reason" in detail


@pytest.mark.unit
class TestDegreeVarianceRule:
    """测试度差规则"""

    def test_rule_loading(self):
        """测试规则加载"""
        from src.quality_rules.degree_variance import DegreeVarianceRule
        rule = DegreeVarianceRule()
        assert rule.name == "degree_variance"
        assert hasattr(rule, 'evaluate')

    def test_evaluate_balanced_dungeon(self, unified_dungeon_data):
        """测试平衡的地牢"""
        from src.quality_rules.degree_variance import DegreeVarianceRule
        rule = DegreeVarianceRule()
        score, detail = rule.evaluate(unified_dungeon_data)

        assert 0.0 <= score <= 1.0
        assert isinstance(detail, dict)
        if "degree_variance" in detail:
            assert isinstance(detail["degree_variance"], (int, float))
        else:
            assert "reason" in detail

    def test_evaluate_unbalanced_dungeon(self):
        """测试不平衡的地牢"""
        from src.quality_rules.degree_variance import DegreeVarianceRule
        rule = DegreeVarianceRule()
        
        # 创建不平衡的地牢（一个房间连接很多，其他房间连接很少）
        unbalanced_dungeon = {
            "header": {
                "schemaName": "dnd-dungeon-unified",
                "schemaVersion": "1.0.0",
                "name": "Unbalanced Dungeon",
                "author": "Test",
                "description": "Dungeon with unbalanced connections",
                "grid": {"type": "square", "size": 5, "unit": "ft"}
            },
            "levels": [
                {
                    "id": "level_1",
                    "name": "Main Level",
                    "map": {"width": 50, "height": 50},
                    "rooms": [
                        {
                            "id": "room_1",
                            "shape": "rectangle",
                            "position": {"x": 10, "y": 10},
                            "size": {"width": 8, "height": 6},
                            "name": "Hub"
                        },
                        {
                            "id": "room_2",
                            "shape": "rectangle",
                            "position": {"x": 25, "y": 10},
                            "size": {"width": 8, "height": 6},
                            "name": "Spoke 1"
                        },
                        {
                            "id": "room_3",
                            "shape": "rectangle",
                            "position": {"x": 25, "y": 25},
                            "size": {"width": 8, "height": 6},
                            "name": "Spoke 2"
                        },
                        {
                            "id": "room_4",
                            "shape": "rectangle",
                            "position": {"x": 10, "y": 25},
                            "size": {"width": 8, "height": 6},
                            "name": "Spoke 3"
                        }
                    ],
                    "doors": [
                        {"id": "door_1", "position": {"x": 18, "y": 13}, "connects": ["room_1", "room_2"]},
                        {"id": "door_2", "position": {"x": 18, "y": 19}, "connects": ["room_1", "room_3"]},
                        {"id": "door_3", "position": {"x": 14, "y": 19}, "connects": ["room_1", "room_4"]}
                    ],
                    "corridors": []
                }
            ]
        }
        
        score, detail = rule.evaluate(unbalanced_dungeon)
        assert 0.0 <= score <= 1.0
        if "degree_variance" in detail and isinstance(detail["degree_variance"], (int, float)):
            assert detail["degree_variance"] > 0  # 应该有度差
        else:
            assert "reason" in detail


@pytest.mark.unit
class TestDoorDistributionRule:
    """测试门分布规则"""

    def test_rule_loading(self):
        """测试规则加载"""
        from src.quality_rules.door_distribution import DoorDistributionRule
        rule = DoorDistributionRule()
        assert rule.name == "door_distribution"
        assert hasattr(rule, 'evaluate')

    def test_evaluate_door_distribution(self, unified_dungeon_data):
        """测试门分布"""
        from src.quality_rules.door_distribution import DoorDistributionRule
        rule = DoorDistributionRule()
        score, detail = rule.evaluate(unified_dungeon_data)

        assert 0.0 <= score <= 1.0
        assert isinstance(detail, dict)
        if "door_count" in detail:
            assert isinstance(detail["door_count"], int)
        else:
            assert "reason" in detail

    def test_evaluate_no_doors(self):
        """测试没有门的地牢"""
        from src.quality_rules.door_distribution import DoorDistributionRule
        rule = DoorDistributionRule()
        
        no_doors_dungeon = {
            "header": {
                "schemaName": "dnd-dungeon-unified",
                "schemaVersion": "1.0.0",
                "name": "No Doors Dungeon",
                "author": "Test",
                "description": "Dungeon without doors",
                "grid": {"type": "square", "size": 5, "unit": "ft"}
            },
            "levels": [
                {
                    "id": "level_1",
                    "name": "Main Level",
                    "map": {"width": 50, "height": 50},
                    "rooms": [
                        {
                            "id": "room_1",
                            "shape": "rectangle",
                            "position": {"x": 10, "y": 10},
                            "size": {"width": 8, "height": 6},
                            "name": "Room 1"
                        }
                    ],
                    "doors": [],
                    "corridors": []
                }
            ]
        }
        
        score, detail = rule.evaluate(no_doors_dungeon)
        assert score == 0.0  # 没有门应该得0分


@pytest.mark.unit
class TestDeadEndRatioRule:
    """测试死胡同比例规则"""

    def test_rule_loading(self):
        """测试规则加载"""
        from src.quality_rules.dead_end_ratio import DeadEndRatioRule
        rule = DeadEndRatioRule()
        assert rule.name == "dead_end_ratio"
        assert hasattr(rule, 'evaluate')

    def test_evaluate_dead_end_ratio(self, unified_dungeon_data):
        """测试死胡同比例"""
        from src.quality_rules.dead_end_ratio import DeadEndRatioRule
        rule = DeadEndRatioRule()
        score, detail = rule.evaluate(unified_dungeon_data)

        assert 0.0 <= score <= 1.0
        assert isinstance(detail, dict)
        if "dead_end_count" in detail:
            assert isinstance(detail["dead_end_count"], int)
        else:
            assert "reason" in detail


@pytest.mark.unit
class TestKeyPathLengthRule:
    """测试关键路径长度规则"""

    def test_rule_loading(self):
        """测试规则加载"""
        from src.quality_rules.key_path_length import KeyPathLengthRule
        rule = KeyPathLengthRule()
        assert rule.name == "key_path_length"
        assert hasattr(rule, 'evaluate')

    def test_evaluate_key_path_length(self, unified_dungeon_data):
        """测试关键路径长度"""
        from src.quality_rules.key_path_length import KeyPathLengthRule
        rule = KeyPathLengthRule()
        score, detail = rule.evaluate(unified_dungeon_data)

        assert 0.0 <= score <= 1.0
        assert isinstance(detail, dict)
        if "key_path_length" in detail:
            assert isinstance(detail["key_path_length"], (int, float))
        else:
            assert "reason" in detail 