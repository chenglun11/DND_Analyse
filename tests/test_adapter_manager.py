"""
测试适配器管理器
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.adapter_manager import AdapterManager
from src.adapters.base import BaseAdapter


@pytest.mark.unit
class MockAdapter(BaseAdapter):
    """模拟适配器用于测试"""
    
    @property
    def format_name(self) -> str:
        return "mock_format"
    
    def detect(self, data):
        return "mock_format" in data
    
    def convert(self, data):
        from src.schema import UnifiedDungeonFormat
        return UnifiedDungeonFormat(
            name="Mock Dungeon",
            author="Mock Author",
            description="Converted from mock format"
        )


@pytest.mark.unit
class TestAdapterManager:
    """测试AdapterManager类"""

    def test_initialization(self, mock_adapter_manager):
        """测试初始化"""
        assert isinstance(mock_adapter_manager, AdapterManager)
        assert hasattr(mock_adapter_manager, 'adapters')
        assert isinstance(mock_adapter_manager.adapters, dict)

    def test_get_supported_formats(self, mock_adapter_manager):
        """测试获取支持的格式列表"""
        formats = mock_adapter_manager.get_supported_formats()
        assert isinstance(formats, list)
        # 应该包含至少一个格式（实际加载的适配器）
        assert len(formats) > 0

    def test_detect_format_success(self, mock_adapter_manager):
        """测试成功检测格式"""
        # 使用实际的适配器数据
        test_data = {"title": "Test Dungeon", "version": "1.0", "rects": [], "doors": [], "notes": []}
        format_name = mock_adapter_manager.detect_format(test_data)
        assert format_name is not None
        assert format_name in mock_adapter_manager.get_supported_formats()

    def test_detect_format_failure(self, mock_adapter_manager):
        """测试检测格式失败"""
        test_data = {"unknown_format": True}
        format_name = mock_adapter_manager.detect_format(test_data)
        assert format_name is None

    def test_detect_format_with_exception(self, mock_adapter_manager):
        """测试检测格式时发生异常"""
        # 创建一个会抛出异常的适配器
        bad_adapter = Mock()
        bad_adapter.format_name = "bad_format"
        bad_adapter.detect.side_effect = Exception("Test exception")
        
        # 临时添加这个适配器
        mock_adapter_manager.adapters["bad_format"] = bad_adapter
        
        test_data = {"bad_format": True}
        format_name = mock_adapter_manager.detect_format(test_data)
        
        # 应该返回None而不是崩溃
        assert format_name is None

    def test_convert_with_auto_detection(self, mock_adapter_manager):
        """测试自动检测格式并转换"""
        test_data = {"title": "Test Dungeon", "version": "1.0", "rects": [], "doors": [], "notes": []}
        result = mock_adapter_manager.convert(test_data)
        
        assert result is not None
        assert "header" in result
        assert "levels" in result
        assert result["header"]["schemaName"] == "dnd-dungeon-unified"

    def test_convert_with_specified_format(self, mock_adapter_manager):
        """测试指定格式转换"""
        test_data = {"title": "Test Dungeon", "rects": [], "doors": [], "notes": []}
        # 获取一个实际支持的格式
        supported_formats = mock_adapter_manager.get_supported_formats()
        if supported_formats:
            format_name = supported_formats[0]
            result = mock_adapter_manager.convert(test_data, format_name)
            assert result is not None
            assert "header" in result

    def test_convert_with_unsupported_format(self, mock_adapter_manager):
        """测试不支持的格式转换"""
        test_data = {"title": "Test Dungeon"}
        result = mock_adapter_manager.convert(test_data, "unsupported_format")
        assert result is None

    def test_convert_with_detection_failure(self, mock_adapter_manager):
        """测试检测失败时的转换"""
        test_data = {"unknown_format": True}
        result = mock_adapter_manager.convert(test_data)
        assert result is None

    def test_convert_with_spatial_inference(self, mock_adapter_manager):
        """测试启用空间推断的转换"""
        test_data = {"title": "Test Dungeon", "version": "1.0", "rects": [], "doors": [], "notes": []}
        result = mock_adapter_manager.convert(
            test_data, 
            enable_spatial_inference=True,
            adjacency_threshold=1.0
        )
        assert result is not None

    def test_convert_without_spatial_inference(self, mock_adapter_manager):
        """测试禁用空间推断的转换"""
        test_data = {"title": "Test Dungeon", "version": "1.0", "rects": [], "doors": [], "notes": []}
        result = mock_adapter_manager.convert(
            test_data, 
            enable_spatial_inference=False
        )
        assert result is not None

    def test_convert_with_conversion_failure(self, mock_adapter_manager):
        """测试转换失败的情况"""
        # 创建一个会转换失败的适配器
        failing_adapter = Mock()
        failing_adapter.format_name = "failing_format"
        failing_adapter.detect.return_value = True
        failing_adapter.convert_with_inference.return_value = None
        
        # 临时添加这个适配器
        mock_adapter_manager.adapters["failing_format"] = failing_adapter
        
        test_data = {"failing_format": True}
        result = mock_adapter_manager.convert(test_data, "failing_format")
        assert result is None

    def test_convert_with_exception(self, mock_adapter_manager):
        """测试转换时发生异常"""
        # 创建一个会抛出异常的适配器
        exception_adapter = Mock()
        exception_adapter.format_name = "exception_format"
        exception_adapter.detect.return_value = True
        exception_adapter.convert_with_inference.side_effect = Exception("Test exception")
        
        # 临时添加这个适配器
        mock_adapter_manager.adapters["exception_format"] = exception_adapter
        
        test_data = {"exception_format": True}
        result = mock_adapter_manager.convert(test_data, "exception_format")
        assert result is None

    @patch('src.adapter_manager.importlib.import_module')
    def test_load_adapters_with_import_error(self, mock_import, mock_adapter_manager):
        """测试加载适配器时导入错误"""
        # 模拟导入错误
        mock_import.side_effect = ImportError("Test import error")
        
        # 创建新的管理器实例，应该不会崩溃
        manager = AdapterManager()
        assert isinstance(manager, AdapterManager)
        assert len(manager.adapters) == 0

    def test_adapter_loading_validation(self, mock_adapter_manager):
        """测试适配器加载验证"""
        # 验证所有加载的适配器都正确实现了接口
        for format_name, adapter in mock_adapter_manager.adapters.items():
            assert hasattr(adapter, 'format_name')
            assert hasattr(adapter, 'detect')
            assert hasattr(adapter, 'convert')
            assert hasattr(adapter, 'convert_with_inference')
            assert callable(adapter.detect)
            assert callable(adapter.convert)
            assert callable(adapter.convert_with_inference) 