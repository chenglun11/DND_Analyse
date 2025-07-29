#!/usr/bin/env python3
"""
简单可视化测试
"""

import json
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from flask_backend.src.visualizer import DungeonVisualizer

def test_simple_visualization():
    """测试简单可视化"""
    print("测试简单可视化...")
    
    # 创建测试数据
    test_data = {
        "levels": [{
            "rooms": [
                {
                    "id": "rect_0",
                    "name": "Room 1",
                    "position": {"x": 0, "y": 0},
                    "size": {"width": 3, "height": 3},
                    "is_room": True,
                    "description": "Test room 1"
                },
                {
                    "id": "rect_1", 
                    "name": "Corridor 1",
                    "position": {"x": 3, "y": 1},
                    "size": {"width": 1, "height": 1},
                    "is_corridor": True,
                    "description": "Test corridor 1"
                },
                {
                    "id": "rect_2",
                    "name": "Room 2", 
                    "position": {"x": 5, "y": 0},
                    "size": {"width": 2, "height": 2},
                    "is_room": True,
                    "description": "Test room 2"
                }
            ],
            "connections": [
                {
                    "from_room": "rect_0",
                    "to_room": "rect_1", 
                    "door_id": "door_1"
                },
                {
                    "from_room": "rect_1",
                    "to_room": "rect_2",
                    "door_id": "door_2"
                }
            ]
        }]
    }
    
    # 测试可视化器
    visualizer = DungeonVisualizer()
    vis_data = visualizer._extract_visualization_data(test_data)
    
    print(f"测试数据:")
    print(f"  - 输入房间数: {len(test_data['levels'][0]['rooms'])}")
    print(f"  - 输入连接数: {len(test_data['levels'][0]['connections'])}")
    
    print(f"\n可视化器输出:")
    print(f"  - 前端房间数: {len(vis_data.get('rooms', []))}")
    print(f"  - 前端通道数: {len(vis_data.get('corridors', []))}")
    print(f"  - 地图尺寸: {vis_data.get('width', 0)} x {vis_data.get('height', 0)}")
    
    # 显示房间和通道详情
    rooms = vis_data.get('rooms', [])
    corridors = vis_data.get('corridors', [])
    
    print(f"\n前端房间:")
    for i, room in enumerate(rooms):
        print(f"  {i+1}. {room.get('name', 'Unknown')} - 位置: ({room['x']:.0f}, {room['y']:.0f}) - 尺寸: {room['width']:.0f}x{room['height']:.0f}")
    
    print(f"\n前端通道:")
    for i, corridor in enumerate(corridors):
        start = corridor['start']
        end = corridor['end']
        print(f"  {i+1}. {corridor.get('name', 'Unknown')} - 从 ({start['x']:.0f}, {start['y']:.0f}) 到 ({end['x']:.0f}, {end['y']:.0f})")

if __name__ == "__main__":
    test_simple_visualization() 