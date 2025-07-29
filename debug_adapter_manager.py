#!/usr/bin/env python3
"""
调试适配器管理器
"""

import json
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.adapter_manager import AdapterManager

def debug_adapter_manager():
    """调试适配器管理器"""
    print("调试适配器管理器...")
    
    # 测试文件
    test_file = "samples/watabou_test/abandoned_hold_of_rhun-hakrax.json"
    
    try:
        # 读取原始数据
        with open(test_file, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
        
        # 使用适配器管理器转换
        adapter_manager = AdapterManager()
        unified_data = adapter_manager.convert(original_data)
        
        if unified_data:
            print(f"适配器管理器输出:")
            print(f"  - 名称: {unified_data.get('name', 'Unknown')}")
            print(f"  - 层级数: {len(unified_data.get('levels', []))}")
            
            if unified_data.get('levels'):
                level = unified_data['levels'][0]
                print(f"  - 房间数: {len(level.get('rooms', []))}")
                print(f"  - 通道数: {len(level.get('corridors', []))}")
                print(f"  - 连接数: {len(level.get('connections', []))}")
                
                # 显示前几个房间
                rooms = level.get('rooms', [])
                print(f"\n房间详情 (前5个):")
                for i, room in enumerate(rooms[:5]):
                    pos = room.get('position', {})
                    size = room.get('size', {})
                    print(f"  {i+1}. ID: {room.get('id', 'Unknown')}")
                    print(f"     名称: {room.get('name', 'Unknown')}")
                    print(f"     位置: ({pos.get('x', 0)}, {pos.get('y', 0)})")
                    print(f"     尺寸: {size.get('width', 0)}x{size.get('height', 0)}")
                    print(f"     类型: is_room={room.get('is_room', False)}, is_corridor={room.get('is_corridor', False)}")
                    print()
                
                # 测试可视化器
                print(f"测试可视化器...")
                from flask_backend.src.visualizer import DungeonVisualizer
                visualizer = DungeonVisualizer()
                vis_data = visualizer._extract_visualization_data(unified_data)
                
                print(f"可视化器输出:")
                print(f"  - 前端房间数: {len(vis_data.get('rooms', []))}")
                print(f"  - 前端通道数: {len(vis_data.get('corridors', []))}")
                print(f"  - 地图尺寸: {vis_data.get('width', 0)} x {vis_data.get('height', 0)}")
                
            else:
                print("  - 没有层级数据")
        else:
            print("❌ 转换失败")
            return False
            
    except Exception as e:
        print(f"❌ 调试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    debug_adapter_manager() 