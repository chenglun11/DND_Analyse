"""
集成测试
测试整个系统的端到端功能
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from src.adapter_manager import AdapterManager
from src.quality_assessor import DungeonQualityAssessor
from src.visualizer import visualize_dungeon


class TestEndToEndConversion:
    """测试端到端转换流程"""

    def test_watabou_to_unified_conversion(self, sample_watabou_data, temp_dir):
        """测试Watabou格式到统一格式的完整转换"""
        # 创建适配器管理器
        manager = AdapterManager()
        
        # 检测格式
        detected_format = manager.detect_format(sample_watabou_data)
        assert detected_format == "watabou_dungeon"
        
        # 转换数据
        unified_data = manager.convert(sample_watabou_data)
        assert unified_data is not None
        assert "header" in unified_data
        assert "levels" in unified_data
        assert unified_data["header"]["schemaName"] == "dnd-dungeon-unified"
        
        # 保存转换结果
        output_file = os.path.join(temp_dir, "test_watabou_unified.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(unified_data, f, ensure_ascii=False, indent=2)
        
        # 验证文件已保存
        assert os.path.exists(output_file)
        
        # 重新加载验证
        with open(output_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        assert loaded_data == unified_data

    def test_onepage_to_unified_conversion(self, sample_onepage_data, temp_dir):
        """测试OnePage格式到统一格式的完整转换"""
        manager = AdapterManager()
        
        # 检测格式
        detected_format = manager.detect_format(sample_onepage_data)
        assert detected_format == "onepage_dungeon"
        
        # 转换数据
        unified_data = manager.convert(sample_onepage_data)
        assert unified_data is not None
        assert "header" in unified_data
        assert "levels" in unified_data
        
        # 保存转换结果
        output_file = os.path.join(temp_dir, "test_onepage_unified.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(unified_data, f, ensure_ascii=False, indent=2)
        
        assert os.path.exists(output_file)

    def test_dungeondraft_to_unified_conversion(self, sample_dungeondraft_data, temp_dir):
        """测试DungeonDraft格式到统一格式的完整转换"""
        manager = AdapterManager()
        
        # 检测格式
        detected_format = manager.detect_format(sample_dungeondraft_data)
        assert detected_format == "dungeondraft"
        
        # 转换数据
        unified_data = manager.convert(sample_dungeondraft_data)
        assert unified_data is not None
        assert "header" in unified_data
        assert "levels" in unified_data
        
        # 保存转换结果
        output_file = os.path.join(temp_dir, "test_dungeondraft_unified.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(unified_data, f, ensure_ascii=False, indent=2)
        
        assert os.path.exists(output_file)

    def test_vtt_to_unified_conversion(self, sample_vtt_data, temp_dir):
        """测试VTT格式到统一格式的完整转换"""
        manager = AdapterManager()
        
        # 检测格式
        detected_format = manager.detect_format(sample_vtt_data)
        assert detected_format == "vtt"
        
        # 转换数据
        unified_data = manager.convert(sample_vtt_data)
        assert unified_data is not None
        assert "header" in unified_data
        assert "levels" in unified_data
        
        # 保存转换结果
        output_file = os.path.join(temp_dir, "test_vtt_unified.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(unified_data, f, ensure_ascii=False, indent=2)
        
        assert os.path.exists(output_file)


class TestQualityAssessmentIntegration:
    """测试质量评估集成"""

    def test_conversion_and_assessment(self, sample_watabou_data, temp_dir):
        """测试转换后立即进行质量评估"""
        # 转换数据
        manager = AdapterManager()
        unified_data = manager.convert(sample_watabou_data)
        assert unified_data is not None
        
        # 质量评估
        assessor = DungeonQualityAssessor()
        assessment_result = assessor.assess_quality(unified_data)
        
        # 验证评估结果
        assert "scores" in assessment_result
        assert "overall_score" in assessment_result
        assert "grade" in assessment_result
        assert "recommendations" in assessment_result
        
        # 保存评估结果
        assessment_file = os.path.join(temp_dir, "assessment_result.json")
        with open(assessment_file, 'w', encoding='utf-8') as f:
            json.dump(assessment_result, f, ensure_ascii=False, indent=2)
        
        assert os.path.exists(assessment_file)

    def test_assessment_with_spatial_inference(self, sample_watabou_data):
        """测试启用空间推断的质量评估"""
        # 转换数据
        manager = AdapterManager()
        unified_data = manager.convert(sample_watabou_data, enable_spatial_inference=True)
        assert unified_data is not None
        
        # 质量评估
        assessor = DungeonQualityAssessor(enable_spatial_inference=True)
        assessment_result = assessor.assess_quality(unified_data)
        
        # 验证空间推断使用情况
        assert "spatial_inference_used" in assessment_result
        assert isinstance(assessment_result["spatial_inference_used"], bool)

    def test_assessment_without_spatial_inference(self, sample_watabou_data):
        """测试禁用空间推断的质量评估"""
        # 转换数据
        manager = AdapterManager()
        unified_data = manager.convert(sample_watabou_data, enable_spatial_inference=False)
        assert unified_data is not None
        
        # 质量评估
        assessor = DungeonQualityAssessor(enable_spatial_inference=False)
        assessment_result = assessor.assess_quality(unified_data)
        
        # 验证空间推断被禁用
        assert assessment_result["spatial_inference_used"] is False


class TestVisualizationIntegration:
    """测试可视化集成"""

    def test_conversion_and_visualization(self, sample_watabou_data, temp_dir):
        """测试转换后立即进行可视化"""
        # 转换数据
        manager = AdapterManager()
        unified_data = manager.convert(sample_watabou_data)
        assert unified_data is not None
        
        # 生成可视化
        output_image = os.path.join(temp_dir, "test_visualization.png")
        success = visualize_dungeon(unified_data, output_image)
        
        # 验证可视化结果
        assert success is True
        assert os.path.exists(output_image)
        assert os.path.getsize(output_image) > 0

    def test_visualization_with_different_formats(self, temp_dir):
        """测试不同格式的可视化"""
        manager = AdapterManager()
        
        # 测试数据
        test_cases = [
            ({"title": "Test", "rects": [{"x": 10, "y": 10, "w": 8, "h": 6}], "doors": [], "notes": []}, "watabou_dungeon"),
            ({"name": "Test", "rooms": [{"id": "room_1", "position": {"x": 10, "y": 10}, "size": {"width": 8, "height": 6}}], "doors": [], "corridors": []}, "onepage_dungeon")
        ]
        
        for test_data, expected_format in test_cases:
            # 转换数据
            unified_data = manager.convert(test_data)
            assert unified_data is not None
            
            # 生成可视化
            output_image = os.path.join(temp_dir, f"test_{expected_format}.png")
            success = visualize_dungeon(unified_data, output_image)
            
            # 验证可视化结果
            assert success is True
            assert os.path.exists(output_image)


class TestBatchProcessing:
    """测试批量处理"""

    def test_batch_conversion(self, temp_dir):
        """测试批量转换"""
        manager = AdapterManager()
        
        # 创建多个测试文件
        test_files = []
        for i in range(3):
            test_data = {
                "title": f"Test Dungeon {i}",
                "rects": [{"x": 10, "y": 10, "w": 8, "h": 6}],
                "doors": [],
                "notes": []
            }
            
            input_file = os.path.join(temp_dir, f"input_{i}.json")
            with open(input_file, 'w', encoding='utf-8') as f:
                json.dump(test_data, f, ensure_ascii=False, indent=2)
            test_files.append(input_file)
        
        # 批量转换
        success_count = 0
        for input_file in test_files:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            unified_data = manager.convert(data)
            if unified_data:
                output_file = input_file.replace("input_", "output_")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(unified_data, f, ensure_ascii=False, indent=2)
                success_count += 1
        
        # 验证批量转换结果
        assert success_count == 3
        for i in range(3):
            output_file = os.path.join(temp_dir, f"output_{i}.json")
            assert os.path.exists(output_file)

    def test_batch_assessment(self, temp_dir):
        """测试批量评估"""
        manager = AdapterManager()
        assessor = DungeonQualityAssessor()
        
        # 创建多个测试文件
        test_files = []
        for i in range(3):
            test_data = {
                "title": f"Test Dungeon {i}",
                "rects": [{"x": 10, "y": 10, "w": 8, "h": 6}],
                "doors": [],
                "notes": []
            }
            
            input_file = os.path.join(temp_dir, f"input_{i}.json")
            with open(input_file, 'w', encoding='utf-8') as f:
                json.dump(test_data, f, ensure_ascii=False, indent=2)
            test_files.append(input_file)
        
        # 批量评估
        assessment_results = []
        for input_file in test_files:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            unified_data = manager.convert(data)
            if unified_data:
                assessment_result = assessor.assess_quality(unified_data)
                assessment_results.append({
                    "file": input_file,
                    "assessment": assessment_result
                })
        
        # 验证批量评估结果
        assert len(assessment_results) == 3
        for result in assessment_results:
            assert "scores" in result["assessment"]
            assert "overall_score" in result["assessment"]
            assert "grade" in result["assessment"]


class TestErrorHandling:
    """测试错误处理"""

    def test_invalid_format_handling(self, mock_adapter_manager):
        """测试无效格式的处理"""
        invalid_data = {"invalid": "format"}
        
        # 检测格式应该返回None
        detected_format = mock_adapter_manager.detect_format(invalid_data)
        assert detected_format is None
        
        # 转换应该返回None
        result = mock_adapter_manager.convert(invalid_data)
        assert result is None

    def test_malformed_data_handling(self, mock_adapter_manager):
        """测试格式错误数据的处理"""
        malformed_data = {"title": "Test"}  # 缺少必要字段
        
        # 转换应该能处理格式错误的数据
        result = mock_adapter_manager.convert(malformed_data)
        # 结果可能是None或有效的统一格式数据，取决于适配器的实现

    def test_empty_data_handling(self, mock_adapter_manager):
        """测试空数据的处理"""
        empty_data = {}
        
        # 检测格式应该返回None
        detected_format = mock_adapter_manager.detect_format(empty_data)
        assert detected_format is None
        
        # 转换应该返回None
        result = mock_adapter_manager.convert(empty_data)
        assert result is None


class TestPerformance:
    """测试性能"""

    def test_large_dungeon_conversion(self, temp_dir):
        """测试大地牢的转换性能"""
        manager = AdapterManager()
        
        # 创建大地牢数据
        large_dungeon = {
            "title": "Large Test Dungeon",
            "rects": [],
            "doors": [],
            "notes": []
        }
        
        # 添加大量房间
        for i in range(100):
            large_dungeon["rects"].append({
                "x": i * 10,
                "y": i * 10,
                "w": 8,
                "h": 6,
                "name": f"Room {i}"
            })
        
        # 测试转换性能
        import time
        start_time = time.time()
        unified_data = manager.convert(large_dungeon)
        end_time = time.time()
        
        # 验证转换成功
        assert unified_data is not None
        assert len(unified_data["levels"][0]["rooms"]) == 100
        
        # 验证性能（转换时间应该小于1秒）
        conversion_time = end_time - start_time
        assert conversion_time < 1.0

    def test_large_dungeon_assessment(self, temp_dir):
        """测试大地牢的评估性能"""
        manager = AdapterManager()
        assessor = DungeonQualityAssessor()
        
        # 创建大地牢数据
        large_dungeon = {
            "title": "Large Test Dungeon",
            "rects": [],
            "doors": [],
            "notes": []
        }
        
        # 添加大量房间
        for i in range(50):
            large_dungeon["rects"].append({
                "x": i * 10,
                "y": i * 10,
                "w": 8,
                "h": 6,
                "name": f"Room {i}"
            })
        
        # 转换数据
        unified_data = manager.convert(large_dungeon)
        assert unified_data is not None
        
        # 测试评估性能
        import time
        start_time = time.time()
        assessment_result = assessor.assess_quality(unified_data)
        end_time = time.time()
        
        # 验证评估成功
        assert "scores" in assessment_result
        assert "overall_score" in assessment_result
        
        # 验证性能（评估时间应该小于2秒）
        assessment_time = end_time - start_time
        assert assessment_time < 2.0 