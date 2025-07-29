#!/usr/bin/env python3
"""
调试可视化逻辑
"""

import json
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.adapter_manager import AdapterManager
from flask_backend.src.visualizer import DungeonVisualizer

def debug_visualization_logic():
    """调试可视化逻辑"""
    print("调试可视化逻辑...")
    
    # 测试文件
    test_file = "samples/watabou_test/abandoned_hold_of_rhun-hakrax.json"
    
    try:
        # 读取原始数据
        with open(test_file, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
        
        # 使用适配器管理器转换
        adapter_manager = AdapterManager()
        unified_data = adapter_manager.convert(original_data)
        
        if not unified_data or not unified_data.get('levels'):
            print("❌ 转换失败或没有层级数据")
            return False
        
        level = unified_data['levels'][0]
        all_nodes = level.get('rooms', [])
        
        print(f"统一格式数据:")
        print(f"  - 总节点数: {len(all_nodes)}")
        
        # 分析每个节点
        rooms_count = 0
        corridors_count = 0
        other_count = 0
        
        print(f"\n节点分析:")
        for i, node in enumerate(all_nodes):
            node_id = node.get('id', f'node_{i}')
            is_room = node.get('is_room', False)
            is_corridor = node.get('is_corridor', False)
            has_description = bool(node.get('description', '').strip())
            has_name = bool(node.get('name', '').strip())
            
            pos = node.get('position', {})
            size = node.get('size', {})
            width = size.get('width', 0) * 50  # 缩放后的宽度
            height = size.get('height', 0) * 50  # 缩放后的高度
            
            is_thin_corridor = (width <= 50 and height <= 150) or (height <= 50 and width <= 150)
            
            print(f"  {i+1}. {node_id}:")
            print(f"     标记: is_room={is_room}, is_corridor={is_corridor}")
            print(f"     内容: has_description={has_description}, has_name={has_name}")
            print(f"     尺寸: {width:.0f}x{height:.0f} (缩放后)")
            print(f"     细通道: {is_thin_corridor}")
            
            # 模拟可视化逻辑
            if not is_room and not is_corridor:
                if has_description or has_name:
                    is_room = True
                elif is_thin_corridor:
                    is_corridor = True
                else:
                    if width > 100 and height > 100:
                        is_room = True
                    else:
                        is_corridor = True
            
            if is_room:
                rooms_count += 1
                print(f"     → 分类为房间")
            elif is_corridor:
                corridors_count += 1
                print(f"     → 分类为通道")
            else:
                other_count += 1
                print(f"     → 分类为其他")
            print()
        
        print(f"分类统计:")
        print(f"  - 房间: {rooms_count}")
        print(f"  - 通道: {corridors_count}")
        print(f"  - 其他: {other_count}")
        
        # 测试可视化器
        print(f"\n测试可视化器...")
        visualizer = DungeonVisualizer()
        vis_data = visualizer._extract_visualization_data(unified_data)
        
        print(f"可视化器输出:")
        print(f"  - 前端房间数: {len(vis_data.get('rooms', []))}")
        print(f"  - 前端通道数: {len(vis_data.get('corridors', []))}")
        print(f"  - 地图尺寸: {vis_data.get('width', 0)} x {vis_data.get('height', 0)}")
        
        # 显示前几个房间和通道
        rooms = vis_data.get('rooms', [])
        corridors = vis_data.get('corridors', [])
        
        print(f"\n前端房间 (前5个):")
        for i, room in enumerate(rooms[:5]):
            print(f"  {i+1}. {room.get('name', 'Unknown')} - 位置: ({room['x']:.0f}, {room['y']:.0f}) - 尺寸: {room['width']:.0f}x{room['height']:.0f}")
        
        print(f"\n前端通道 (前5个):")
        for i, corridor in enumerate(corridors[:5]):
            start = corridor['start']
            end = corridor['end']
            print(f"  {i+1}. {corridor.get('name', 'Unknown')} - 从 ({start['x']:.0f}, {start['y']:.0f}) 到 ({end['x']:.0f}, {end['y']:.0f})")
            
    except Exception as e:
        print(f"❌ 调试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    debug_visualization_logic() 