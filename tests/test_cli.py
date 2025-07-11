"""
测试命令行界面
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
from src.cli import (
    load_json_file, 
    save_json_file, 
    convert_single_file, 
    convert_directory,
    detect_format,
    visualize_file,
    assess_quality
)


class TestCLIUtilities:
    """测试CLI工具函数"""

    def test_load_json_file_success(self, temp_dir):
        """测试成功加载JSON文件"""
        test_data = {"test": "data", "number": 42}
        file_path = os.path.join(temp_dir, "test.json")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        result = load_json_file(file_path)
        assert result == test_data

    def test_load_json_file_not_found(self):
        """测试加载不存在的文件"""
        result = load_json_file("nonexistent.json")
        assert result is None

    def test_load_json_file_invalid_json(self, temp_dir):
        """测试加载无效的JSON文件"""
        file_path = os.path.join(temp_dir, "invalid.json")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("invalid json content")
        
        result = load_json_file(file_path)
        assert result is None

    def test_save_json_file_success(self, temp_dir):
        """测试成功保存JSON文件"""
        test_data = {"test": "data", "number": 42}
        file_path = os.path.join(temp_dir, "output.json")
        
        result = save_json_file(test_data, file_path)
        assert result is True
        assert os.path.exists(file_path)
        
        # 验证保存的内容
        with open(file_path, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        assert loaded_data == test_data

    def test_save_json_file_create_directory(self, temp_dir):
        """测试保存文件时创建目录"""
        test_data = {"test": "data"}
        file_path = os.path.join(temp_dir, "subdir", "output.json")
        
        result = save_json_file(test_data, file_path)
        assert result is True
        assert os.path.exists(file_path)

    def test_save_json_file_permission_error(self):
        """测试保存文件时权限错误"""
        test_data = {"test": "data"}
        # 尝试保存到根目录（通常需要权限）
        file_path = "/root/test.json"
        
        result = save_json_file(test_data, file_path)
        assert result is False


class TestCLICommands:
    """测试CLI命令"""

    @patch('src.cli.AdapterManager')
    def test_convert_single_file_success(self, mock_adapter_manager_class, sample_watabou_data, temp_dir):
        """测试成功转换单个文件"""
        # 模拟适配器管理器
        mock_manager = MagicMock()
        mock_manager.convert.return_value = {
            "header": {"schemaName": "dnd-dungeon-unified"},
            "levels": []
        }
        mock_adapter_manager_class.return_value = mock_manager
        
        # 创建输入文件
        input_file = os.path.join(temp_dir, "input.json")
        with open(input_file, 'w', encoding='utf-8') as f:
            json.dump(sample_watabou_data, f)
        
        output_file = os.path.join(temp_dir, "output.json")
        
        # 测试转换
        result = convert_single_file(mock_manager, input_file, output_file)
        assert result is True
        assert os.path.exists(output_file)

    @patch('src.cli.AdapterManager')
    def test_convert_single_file_with_visualization(self, mock_adapter_manager_class, sample_watabou_data, temp_dir):
        """测试带可视化的文件转换"""
        # 模拟适配器管理器
        mock_manager = MagicMock()
        mock_manager.convert.return_value = {
            "header": {"schemaName": "dnd-dungeon-unified"},
            "levels": [
                {
                    "id": "level_1",
                    "name": "Main Level",
                    "map": {"width": 50, "height": 50},
                    "rooms": [
                        {
                            "id": "room_1",
                            "x": 10,
                            "y": 10,
                            "width": 8,
                            "height": 6,
                            "name": "Test Room"
                        }
                    ],
                    "corridors": [],
                    "doors": [],
                    "connections": []
                }
            ]
        }
        mock_adapter_manager_class.return_value = mock_manager
        
        # 模拟可视化函数
        with patch('src.visualizer.visualize_dungeon') as mock_visualize:
            mock_visualize.return_value = True
            
            # 创建输入文件
            input_file = os.path.join(temp_dir, "input.json")
            with open(input_file, 'w', encoding='utf-8') as f:
                json.dump(sample_watabou_data, f)
            
            output_file = os.path.join(temp_dir, "output.json")
            
            # 测试转换（带可视化）
            result = convert_single_file(mock_manager, input_file, output_file, visualize=True)
            assert result is True
            assert os.path.exists(output_file)
            
            # 验证可视化被调用
            mock_visualize.assert_called_once()

    @patch('src.cli.AdapterManager')
    def test_convert_single_file_failure(self, mock_adapter_manager_class, temp_dir):
        """测试文件转换失败"""
        # 模拟适配器管理器
        mock_manager = MagicMock()
        mock_manager.convert.return_value = None
        mock_adapter_manager_class.return_value = mock_manager
        
        # 创建输入文件
        input_file = os.path.join(temp_dir, "input.json")
        with open(input_file, 'w', encoding='utf-8') as f:
            json.dump({"invalid": "data"}, f)
        
        output_file = os.path.join(temp_dir, "output.json")
        
        # 测试转换失败
        result = convert_single_file(mock_manager, input_file, output_file)
        assert result is False

    @patch('src.cli.AdapterManager')
    def test_convert_directory_success(self, mock_adapter_manager_class, temp_dir):
        """测试成功转换目录"""
        # 模拟适配器管理器
        mock_manager = MagicMock()
        mock_manager.convert.return_value = {
            "header": {"schemaName": "dnd-dungeon-unified"},
            "levels": []
        }
        mock_adapter_manager_class.return_value = mock_manager
        
        # 创建输入目录和文件
        input_dir = os.path.join(temp_dir, "input")
        output_dir = os.path.join(temp_dir, "output")
        os.makedirs(input_dir)
        
        # 创建多个测试文件
        for i in range(3):
            file_path = os.path.join(input_dir, f"test_{i}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({"title": f"Test {i}", "rects": [], "doors": [], "notes": []}, f)
        
        # 测试目录转换
        success_count = convert_directory(mock_manager, input_dir, output_dir)
        assert success_count == 3
        
        # 验证输出文件
        for i in range(3):
            output_file = os.path.join(output_dir, f"test_{i}.json")
            assert os.path.exists(output_file)

    @patch('src.cli.AdapterManager')
    def test_convert_directory_empty(self, mock_adapter_manager_class, temp_dir):
        """测试转换空目录"""
        # 模拟适配器管理器
        mock_manager = MagicMock()
        mock_adapter_manager_class.return_value = mock_manager
        
        # 创建空目录
        input_dir = os.path.join(temp_dir, "empty")
        output_dir = os.path.join(temp_dir, "output")
        os.makedirs(input_dir)
        
        # 测试空目录转换
        success_count = convert_directory(mock_manager, input_dir, output_dir)
        assert success_count == 0

    @patch('src.cli.AdapterManager')
    def test_detect_format_success(self, mock_adapter_manager_class, sample_watabou_data, temp_dir):
        """测试成功检测格式"""
        # 模拟适配器管理器
        mock_manager = MagicMock()
        mock_manager.detect_format.return_value = "watabou_dungeon"
        mock_adapter_manager_class.return_value = mock_manager
        
        # 创建测试文件
        file_path = os.path.join(temp_dir, "test.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(sample_watabou_data, f)
        
        # 测试格式检测
        detected_format = detect_format(mock_manager, file_path)
        assert detected_format == "watabou_dungeon"

    @patch('src.cli.AdapterManager')
    def test_detect_format_failure(self, mock_adapter_manager_class, temp_dir):
        """测试格式检测失败"""
        # 模拟适配器管理器
        mock_manager = MagicMock()
        mock_manager.detect_format.return_value = None
        mock_adapter_manager_class.return_value = mock_manager
        
        # 创建测试文件
        file_path = os.path.join(temp_dir, "test.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({"invalid": "data"}, f)
        
        # 测试格式检测失败
        detected_format = detect_format(mock_manager, file_path)
        assert detected_format == "Unknown"

    def test_visualize_file_success(self, unified_dungeon_data, temp_dir):
        """测试成功可视化文件"""
        # 创建测试文件
        input_file = os.path.join(temp_dir, "test.json")
        with open(input_file, 'w', encoding='utf-8') as f:
            json.dump(unified_dungeon_data, f)
        
        output_file = os.path.join(temp_dir, "test.png")
        
        # 模拟可视化函数
        with patch('src.visualizer.visualize_dungeon') as mock_visualize:
            mock_visualize.return_value = True
            
            # 测试可视化
            visualize_file(input_file, output_file)
            
            # 验证可视化被调用
            mock_visualize.assert_called_once()

    def test_visualize_file_failure(self, temp_dir):
        """测试可视化文件失败"""
        # 创建不存在的文件
        input_file = os.path.join(temp_dir, "nonexistent.json")
        output_file = os.path.join(temp_dir, "test.png")
        
        # 测试可视化失败
        visualize_file(input_file, output_file)
        # 应该不会抛出异常，只是静默失败

    def test_assess_quality_success(self, unified_dungeon_data, temp_dir):
        """测试成功质量评估"""
        # 创建测试文件
        input_file = os.path.join(temp_dir, "test.json")
        with open(input_file, 'w', encoding='utf-8') as f:
            json.dump(unified_dungeon_data, f)
        
        # 模拟质量评估器
        with patch('src.cli.DungeonQualityAssessor') as mock_assessor_class:
            mock_assessor = MagicMock()
            mock_assessor.assess_quality.return_value = {
                "scores": {"accessibility": 0.8},
                "overall_score": 0.8,
                "grade": "A",
                "recommendations": ["Good dungeon!"]
            }
            mock_assessor_class.return_value = mock_assessor
            
            # 测试质量评估
            result = assess_quality(input_file)
            assert result is True
            
            # 验证评估器被调用
            mock_assessor.assess_quality.assert_called_once()

    def test_assess_quality_failure(self, temp_dir):
        """测试质量评估失败"""
        # 创建不存在的文件
        input_file = os.path.join(temp_dir, "nonexistent.json")
        
        # 测试质量评估失败
        result = assess_quality(input_file)
        assert result is False


class TestCLIArgumentParsing:
    """测试CLI参数解析"""

    @patch('src.cli.AdapterManager')
    @patch('sys.argv', ['cli.py', 'convert', 'input.json', 'output.json'])
    def test_convert_command_parsing(self, mock_adapter_manager_class):
        """测试convert命令参数解析"""
        with patch('src.cli.convert_single_file') as mock_convert:
            mock_convert.return_value = True
            
            # 模拟main函数
            from src.cli import main
            main()
            
            # 验证转换函数被调用
            mock_convert.assert_called_once()

    @patch('src.cli.AdapterManager')
    @patch('sys.argv', ['cli.py', 'convert-dir', 'input_dir', 'output_dir'])
    def test_convert_dir_command_parsing(self, mock_adapter_manager_class):
        """测试convert-dir命令参数解析"""
        with patch('src.cli.convert_directory') as mock_convert_dir:
            mock_convert_dir.return_value = 3
            
            # 模拟main函数
            from src.cli import main
            main()
            
            # 验证目录转换函数被调用
            mock_convert_dir.assert_called_once()

    @patch('src.cli.AdapterManager')
    @patch('sys.argv', ['cli.py', 'detect', 'test.json'])
    def test_detect_command_parsing(self, mock_adapter_manager_class):
        """测试detect命令参数解析"""
        with patch('src.cli.detect_format') as mock_detect:
            mock_detect.return_value = "watabou_dungeon"
            
            # 模拟main函数
            from src.cli import main
            main()
            
            # 验证检测函数被调用
            mock_detect.assert_called_once()

    @patch('src.cli.AdapterManager')
    @patch('sys.argv', ['cli.py', 'list-formats'])
    def test_list_formats_command_parsing(self, mock_adapter_manager_class):
        """测试list-formats命令参数解析"""
        # 模拟适配器管理器
        mock_manager = MagicMock()
        mock_manager.get_supported_formats.return_value = ["watabou_dungeon", "onepage_dungeon"]
        mock_adapter_manager_class.return_value = mock_manager
        
        # 模拟main函数
        from src.cli import main
        main()
        
        # 验证获取格式列表函数被调用
        mock_manager.get_supported_formats.assert_called_once()

    @patch('src.cli.AdapterManager')
    @patch('sys.argv', ['cli.py', 'visualize', 'test.json'])
    def test_visualize_command_parsing(self, mock_adapter_manager_class):
        """测试visualize命令参数解析"""
        with patch('src.cli.visualize_file') as mock_visualize:
            # 模拟main函数
            from src.cli import main
            main()
            
            # 验证可视化函数被调用
            mock_visualize.assert_called_once()

    @patch('src.cli.AdapterManager')
    @patch('sys.argv', ['cli.py', 'assess', 'test.json'])
    def test_assess_command_parsing(self, mock_adapter_manager_class):
        """测试assess命令参数解析"""
        # 创建临时测试文件
        import tempfile
        import json
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"header": {"name": "Test"}, "levels": []}, f)
            test_file = f.name
        
        try:
            with patch('sys.argv', ['cli.py', 'assess', test_file]):
                with patch('src.cli.DungeonQualityAssessor') as mock_assessor_class:
                    mock_assessor = Mock()
                    mock_assessor.assess_quality.return_value = {
                        "scores": {"test": {"score": 0.8}},
                        "overall_score": 0.8,
                        "grade": "A",
                        "recommendations": []
                    }
                    mock_assessor_class.return_value = mock_assessor
                    
                    # 模拟main函数
                    from src.cli import main
                    main()
                    
                    # 验证评估器被调用
                    mock_assessor.assess_quality.assert_called_once()
        finally:
            # 清理临时文件
            os.unlink(test_file)


class TestCLIErrorHandling:
    """测试CLI错误处理"""

    def test_main_no_command(self):
        """测试没有命令时显示帮助"""
        with patch('sys.argv', ['cli.py']):
            with patch('argparse.ArgumentParser.print_help') as mock_help:
                from src.cli import main
                main()
                mock_help.assert_called_once()

    def test_main_invalid_command(self):
        """测试无效命令的处理"""
        with patch('sys.argv', ['cli.py', 'invalid_command']):
            from src.cli import main
            with pytest.raises(SystemExit) as excinfo:
                main()
            assert excinfo.value.code == 2

    @patch('src.cli.AdapterManager')
    def test_convert_with_file_not_found(self, mock_adapter_manager_class):
        """测试转换不存在的文件"""
        mock_manager = MagicMock()
        mock_adapter_manager_class.return_value = mock_manager
        
        result = convert_single_file(mock_manager, "nonexistent.json", "output.json")
        assert result is False

    @patch('src.cli.AdapterManager')
    def test_convert_with_invalid_json(self, mock_adapter_manager_class, temp_dir):
        """测试转换无效的JSON文件"""
        mock_manager = MagicMock()
        mock_adapter_manager_class.return_value = mock_manager
        
        # 创建无效的JSON文件
        input_file = os.path.join(temp_dir, "invalid.json")
        with open(input_file, 'w', encoding='utf-8') as f:
            f.write("invalid json")
        
        result = convert_single_file(mock_manager, input_file, "output.json")
        assert result is False 