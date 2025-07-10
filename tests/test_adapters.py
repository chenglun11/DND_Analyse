"""
测试各种适配器
"""

import pytest
from unittest.mock import Mock, patch
from src.adapters.base import BaseAdapter
from src.schema import UnifiedDungeonFormat


@pytest.mark.unit
class TestBaseAdapter:
    """测试BaseAdapter基类"""

    def test_abstract_methods(self):
        """测试抽象方法定义"""
        # 不能直接实例化抽象类
        with pytest.raises(TypeError):
            BaseAdapter()

    def test_convert_with_inference_default(self):
        """测试默认的空间推断转换"""
        # 创建一个具体的适配器实现
        class TestAdapter(BaseAdapter):
            @property
            def format_name(self) -> str:
                return "test_format"
            
            def detect(self, data):
                return "test_format" in data
            
            def convert(self, data):
                return UnifiedDungeonFormat(
                    name="Test Dungeon",
                    author="Test Author"
                )
        
        adapter = TestAdapter()
        test_data = {"test_format": True}
        
        # 测试默认启用空间推断
        result = adapter.convert_with_inference(test_data)
        assert result is not None
        assert isinstance(result, UnifiedDungeonFormat)
        assert result.name == "Test Dungeon"

    def test_convert_with_inference_disabled(self):
        """测试禁用空间推断的转换"""
        class TestAdapter(BaseAdapter):
            @property
            def format_name(self) -> str:
                return "test_format"
            
            def detect(self, data):
                return "test_format" in data
            
            def convert(self, data):
                return UnifiedDungeonFormat(
                    name="Test Dungeon",
                    author="Test Author"
                )
        
        adapter = TestAdapter()
        test_data = {"test_format": True}
        
        # 测试禁用空间推断
        result = adapter.convert_with_inference(test_data, enable_spatial_inference=False)
        assert result is not None
        assert isinstance(result, UnifiedDungeonFormat)

    def test_convert_with_inference_failure(self):
        """测试转换失败时的空间推断"""
        class FailingAdapter(BaseAdapter):
            @property
            def format_name(self) -> str:
                return "failing_format"
            
            def detect(self, data):
                return "failing_format" in data
            
            def convert(self, data):
                return None  # 转换失败
        
        adapter = FailingAdapter()
        test_data = {"failing_format": True}
        
        # 转换失败时应该返回None
        result = adapter.convert_with_inference(test_data)
        assert result is None


@pytest.mark.unit
class TestWatabouAdapter:
    """测试Watabou适配器"""

    def test_format_name(self):
        """测试格式名称"""
        from src.adapters.watabou_adapter import WatabouAdapter
        adapter = WatabouAdapter()
        assert adapter.format_name == "watabou_dungeon"

    def test_detect_success(self, sample_watabou_data):
        """测试成功检测Watabou格式"""
        from src.adapters.watabou_adapter import WatabouAdapter
        adapter = WatabouAdapter()
        assert adapter.detect(sample_watabou_data) is True

    def test_detect_failure(self):
        """测试检测Watabou格式失败"""
        from src.adapters.watabou_adapter import WatabouAdapter
        adapter = WatabouAdapter()
        test_data = {"not_watabou": True}
        assert adapter.detect(test_data) is False

    def test_convert_success(self, sample_watabou_data):
        """测试成功转换Watabou格式"""
        from src.adapters.watabou_adapter import WatabouAdapter
        adapter = WatabouAdapter()
        result = adapter.convert(sample_watabou_data)
        
        assert result is not None
        assert isinstance(result, UnifiedDungeonFormat)
        assert result.name == "Test Dungeon"
        assert result.schema_name == "dnd-dungeon-unified"

    def test_convert_with_empty_data(self):
        """测试转换空数据"""
        from src.adapters.watabou_adapter import WatabouAdapter
        adapter = WatabouAdapter()
        empty_data = {"title": "Empty", "rects": [], "doors": [], "notes": []}
        result = adapter.convert(empty_data)
        
        assert result is not None
        assert isinstance(result, UnifiedDungeonFormat)

    def test_convert_with_missing_fields(self):
        """测试转换缺少字段的数据"""
        from src.adapters.watabou_adapter import WatabouAdapter
        adapter = WatabouAdapter()
        incomplete_data = {"title": "Incomplete"}
        result = adapter.convert(incomplete_data)
        
        # 应该能处理缺少字段的情况
        assert result is not None


# ======= 注释掉已废弃适配器相关测试 =======
# @pytest.mark.unit
# class TestOnePageAdapter:
#     """测试OnePage适配器"""

#     def test_format_name(self):
#         """测试格式名称"""
#         from src.adapters.onepage_adapter import OnePageAdapter
#         adapter = OnePageAdapter()
#         assert adapter.format_name == "onepage_dungeon"

#     def test_detect_success(self, sample_onepage_data):
#         """测试成功检测OnePage格式"""
#         from src.adapters.onepage_adapter import OnePageAdapter
#         adapter = OnePageAdapter()
#         assert adapter.detect(sample_onepage_data) is True

#     def test_detect_failure(self):
#         """测试检测OnePage格式失败"""
#         from src.adapters.onepage_adapter import OnePageAdapter
#         adapter = OnePageAdapter()
#         test_data = {"not_onepage": True}
#         assert adapter.detect(test_data) is False

#     def test_convert_success(self, sample_onepage_data):
#         """测试成功转换OnePage格式"""
#         from src.adapters.onepage_adapter import OnePageAdapter
#         adapter = OnePageAdapter()
#         result = adapter.convert(sample_onepage_data)
        
#         assert result is not None
#         assert isinstance(result, UnifiedDungeonFormat)
#         assert result.name == "Test OnePage Dungeon"
#         assert result.author == "Test Author"

#     def test_convert_with_empty_data(self):
#         """测试转换空数据"""
#         from src.adapters.onepage_adapter import OnePageAdapter
#         adapter = OnePageAdapter()
#         empty_data = {"name": "Empty", "rooms": [], "doors": [], "corridors": []}
#         result = adapter.convert(empty_data)
        
#         assert result is not None
#         assert isinstance(result, UnifiedDungeonFormat)


@pytest.mark.unit
class TestDungeonDraftAdapter:
    """测试DungeonDraft适配器"""

    def test_format_name(self):
        """测试格式名称"""
        from src.adapters.dungeondraft_adapter import DungeonDraftAdapter
        adapter = DungeonDraftAdapter()
        assert adapter.format_name == "dungeondraft"

    def test_detect_success(self, sample_dungeondraft_data):
        """测试成功检测DungeonDraft格式"""
        from src.adapters.dungeondraft_adapter import DungeonDraftAdapter
        adapter = DungeonDraftAdapter()
        assert adapter.detect(sample_dungeondraft_data) is True

    def test_detect_failure(self):
        """测试检测DungeonDraft格式失败"""
        from src.adapters.dungeondraft_adapter import DungeonDraftAdapter
        adapter = DungeonDraftAdapter()
        test_data = {"not_dungeondraft": True}
        assert adapter.detect(test_data) is False

    def test_convert_success(self, sample_dungeondraft_data):
        """测试成功转换DungeonDraft格式"""
        from src.adapters.dungeondraft_adapter import DungeonDraftAdapter
        adapter = DungeonDraftAdapter()
        result = adapter.convert(sample_dungeondraft_data)
        
        assert result is not None
        assert isinstance(result, UnifiedDungeonFormat)
        assert result.name == "Test DungeonDraft Map"


# @pytest.mark.unit
# class TestVTTAdapter:
#     """测试VTT适配器"""

#     def test_format_name(self):
#         """测试格式名称"""
#         from src.adapters.vtt_adapter import VTTAdapter
#         adapter = VTTAdapter()
#         assert adapter.format_name == "vtt"

#     def test_detect_success(self, sample_vtt_data):
#         """测试成功检测VTT格式"""
#         from src.adapters.vtt_adapter import VTTAdapter
#         adapter = VTTAdapter()
#         assert adapter.detect(sample_vtt_data) is True

#     def test_detect_failure(self):
#         """测试检测VTT格式失败"""
#         from src.adapters.vtt_adapter import VTTAdapter
#         adapter = VTTAdapter()
#         test_data = {"not_vtt": True}
#         assert adapter.detect(test_data) is False

#     def test_convert_success(self, sample_vtt_data):
#         """测试成功转换VTT格式"""
#         from src.adapters.vtt_adapter import VTTAdapter
#         adapter = VTTAdapter()
#         result = adapter.convert(sample_vtt_data)
        
#         assert result is not None
#         assert isinstance(result, UnifiedDungeonFormat)
#         assert result.name == "Test VTT Scene"


@pytest.mark.unit
class TestAdapterIntegration:
    """测试适配器集成"""

    def test_all_adapters_implement_interface(self, mock_adapter_manager):
        """测试所有适配器都正确实现了接口"""
        for format_name, adapter in mock_adapter_manager.adapters.items():
            # 验证必要的方法存在
            assert hasattr(adapter, 'format_name')
            assert hasattr(adapter, 'detect')
            assert hasattr(adapter, 'convert')
            assert hasattr(adapter, 'convert_with_inference')
            
            # 验证方法是可调用的
            assert callable(adapter.detect)
            assert callable(adapter.convert)
            assert callable(adapter.convert_with_inference)
            
            # 验证format_name是字符串
            assert isinstance(adapter.format_name, str)
            assert len(adapter.format_name) > 0

    def test_adapter_detection_uniqueness(self, mock_adapter_manager):
        """测试适配器检测的唯一性"""
        # 每个适配器应该只检测自己的格式
        test_cases = [
            ({"title": "Test", "rects": [], "doors": [], "notes": []}, "watabou_dungeon"),
            ({"name": "Test", "rooms": [], "doors": [], "corridors": []}, "onepage_dungeon"),
            ({"version": "1.0", "elements": []}, "dungeondraft"),
            ({"scene": {"name": "Test", "walls": []}}, "vtt")
        ]
        
        for test_data, expected_format in test_cases:
            detected_format = mock_adapter_manager.detect_format(test_data)
            if detected_format:
                assert detected_format == expected_format

    def test_adapter_conversion_consistency(self, mock_adapter_manager):
        """测试适配器转换的一致性"""
        test_data = {"title": "Test", "rects": [], "doors": [], "notes": []}
        
        # 多次转换应该产生相同的结果
        result1 = mock_adapter_manager.convert(test_data)
        result2 = mock_adapter_manager.convert(test_data)
        
        if result1 and result2:
            assert result1["header"]["name"] == result2["header"]["name"]
            assert result1["header"]["schemaName"] == result2["header"]["schemaName"] 