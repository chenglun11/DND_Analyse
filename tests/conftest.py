"""
pytest配置文件
设置测试环境和通用fixture
"""

import pytest
import sys
import os
from pathlib import Path
import json
import tempfile
import shutil

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture(scope="session")
def project_root_path():
    """返回项目根目录路径"""
    return project_root

@pytest.fixture(scope="session")
def test_data_dir():
    """返回测试数据目录路径"""
    return project_root / "tests" / "test_data"

@pytest.fixture(scope="session")
def sample_data_dir():
    """返回样例数据目录路径"""
    return project_root / "samples"

@pytest.fixture
def temp_dir():
    """创建临时目录，测试后自动清理"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_watabou_data():
    """Watabou格式的样例数据"""
    return {
        "title": "Test Dungeon",
        "version": "1.0",
        "rects": [
            {"x": 10, "y": 10, "w": 8, "h": 6, "name": "Room 1"},
            {"x": 25, "y": 15, "w": 6, "h": 8, "name": "Room 2"}
        ],
        "doors": [
            {"x": 18, "y": 13, "connects": ["Room 1", "Room 2"]}
        ],
        "notes": []
    }

@pytest.fixture
def sample_dungeondraft_data():
    """DungeonDraft格式的样例数据"""
    return {
        "version": "1.0",
        "name": "Test DungeonDraft Map",
        "elements": [
            {
                "type": "room",
                "id": "room_1",
                "x": 10,
                "y": 10,
                "width": 8,
                "height": 6,
                "name": "Test Room"
            }
        ]
    }

@pytest.fixture
def unified_dungeon_data():
    """统一格式的样例数据"""
    return {
        "header": {
            "schemaName": "dnd-dungeon-unified",
            "schemaVersion": "1.0.0",
            "name": "Test Unified Dungeon",
            "author": "Test Author",
            "description": "A test dungeon in unified format",
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
                        "x": 10,
                        "y": 10,
                        "width": 8,
                        "height": 6,
                        "name": "Entrance",
                        "description": "Main entrance"
                    }
                ],
                "doors": [
                    {
                        "id": "door_1",
                        "position": {"x": 18, "y": 13},
                        "connects": ["room_1", "corridor_1"]
                    }
                ],
                "corridors": [
                    {
                        "id": "corridor_1",
                        "x": 18,
                        "y": 13,
                        "width": 7,
                        "height": 2
                    }
                ]
            }
        ]
    }

@pytest.fixture
def mock_adapter_manager():
    """模拟的适配器管理器"""
    from src.adapter_manager import AdapterManager
    return AdapterManager()

@pytest.fixture
def mock_quality_assessor():
    """模拟的质量评估器"""
    from src.quality_assessor import DungeonQualityAssessor
    return DungeonQualityAssessor()

@pytest.fixture(autouse=True)
def setup_logging():
    """设置测试日志"""
    import logging
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ) 