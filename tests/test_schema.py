"""
测试schema模块
"""

import pytest
from src.schema import UnifiedDungeonFormat


@pytest.mark.unit
class TestUnifiedDungeonFormat:
    """测试UnifiedDungeonFormat类"""

    def test_default_initialization(self):
        """测试默认初始化"""
        dungeon = UnifiedDungeonFormat()
        
        assert dungeon.schema_name == "dnd-dungeon-unified"
        assert dungeon.schema_version == "1.0.0"
        assert dungeon.name == "Unnamed Dungeon"
        assert dungeon.author == "Adapter"
        assert dungeon.description == "Converted from other formats"
        assert dungeon.grid == {"type": "square", "size": 5, "unit": "ft"}
        assert dungeon.levels == []

    def test_custom_initialization(self):
        """测试自定义初始化"""
        dungeon = UnifiedDungeonFormat(
            name="Test Dungeon",
            author="Test Author",
            description="A test dungeon",
            grid={"type": "hex", "size": 10, "unit": "m"}
        )
        
        assert dungeon.name == "Test Dungeon"
        assert dungeon.author == "Test Author"
        assert dungeon.description == "A test dungeon"
        assert dungeon.grid == {"type": "hex", "size": 10, "unit": "m"}

    def test_to_dict(self):
        """测试to_dict方法"""
        dungeon = UnifiedDungeonFormat(
            name="Test Dungeon",
            author="Test Author",
            description="A test dungeon"
        )
        
        result = dungeon.to_dict()
        
        assert "header" in result
        assert "levels" in result
        
        header = result["header"]
        assert header["schemaName"] == "dnd-dungeon-unified"
        assert header["schemaVersion"] == "1.0.0"
        assert header["name"] == "Test Dungeon"
        assert header["author"] == "Test Author"
        assert header["description"] == "A test dungeon"
        assert header["grid"] == {"type": "square", "size": 5, "unit": "ft"}

    def test_from_dict(self):
        """测试from_dict类方法"""
        data = {
            "header": {
                "schemaName": "dnd-dungeon-unified",
                "schemaVersion": "1.0.0",
                "name": "Test Dungeon",
                "author": "Test Author",
                "description": "A test dungeon",
                "grid": {"type": "hex", "size": 10, "unit": "m"}
            },
            "levels": [
                {
                    "id": "level_1",
                    "name": "Main Level",
                    "rooms": []
                }
            ]
        }
        
        dungeon = UnifiedDungeonFormat.from_dict(data)
        
        assert dungeon.schema_name == "dnd-dungeon-unified"
        assert dungeon.schema_version == "1.0.0"
        assert dungeon.name == "Test Dungeon"
        assert dungeon.author == "Test Author"
        assert dungeon.description == "A test dungeon"
        assert dungeon.grid == {"type": "hex", "size": 10, "unit": "m"}
        assert len(dungeon.levels) == 1
        assert dungeon.levels[0]["id"] == "level_1"

    def test_from_dict_with_missing_fields(self):
        """测试from_dict方法处理缺失字段"""
        data = {
            "header": {
                "name": "Test Dungeon"
            },
            "levels": []
        }
        
        dungeon = UnifiedDungeonFormat.from_dict(data)
        
        # 应该使用默认值
        assert dungeon.schema_name == "dnd-dungeon-unified"
        assert dungeon.schema_version == "1.0.0"
        assert dungeon.name == "Test Dungeon"
        assert dungeon.author == "Adapter"
        assert dungeon.description == "Converted from other formats"
        assert dungeon.grid == {"type": "square", "size": 5, "unit": "ft"}

    def test_from_dict_without_header(self):
        """测试from_dict方法处理没有header的情况"""
        data = {
            "levels": []
        }
        
        dungeon = UnifiedDungeonFormat.from_dict(data)
        
        # 应该使用默认值
        assert dungeon.schema_name == "dnd-dungeon-unified"
        assert dungeon.schema_version == "1.0.0"
        assert dungeon.name == "Unnamed Dungeon"
        assert dungeon.author == "Adapter"
        assert dungeon.description == "Converted from other formats"
        assert dungeon.grid == {"type": "square", "size": 5, "unit": "ft"}

    def test_round_trip_conversion(self):
        """测试to_dict和from_dict的往返转换"""
        original = UnifiedDungeonFormat(
            name="Test Dungeon",
            author="Test Author",
            description="A test dungeon",
            grid={"type": "hex", "size": 10, "unit": "m"}
        )
        
        # 添加一些levels
        original.levels = [
            {
                "id": "level_1",
                "name": "Main Level",
                "rooms": [
                    {
                        "id": "room_1",
                        "name": "Entrance",
                        "position": {"x": 10, "y": 10},
                        "size": {"width": 8, "height": 6}
                    }
                ]
            }
        ]
        
        # 转换为字典
        dict_data = original.to_dict()
        
        # 从字典重新创建对象
        restored = UnifiedDungeonFormat.from_dict(dict_data)
        
        # 验证所有字段都正确恢复
        assert restored.schema_name == original.schema_name
        assert restored.schema_version == original.schema_version
        assert restored.name == original.name
        assert restored.author == original.author
        assert restored.description == original.description
        assert restored.grid == original.grid
        assert restored.levels == original.levels 