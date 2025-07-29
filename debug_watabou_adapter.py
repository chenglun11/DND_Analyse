#!/usr/bin/env python3
"""
调试Watabou适配器
"""

import json
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.adapters.watabou_adapter import WatabouAdapter

def debug_watabou_adapter():
    """调试Watabou适配器"""
    print("调试Watabou适配器...")
    
    # 测试文件
    test_file = "samples/watabou_test/abandoned_hold_of_rhun-hakrax.json"
    
    try:
        # 读取原始数据
        with open(test_file, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
        
        print(f"原始Watabou数据:")
        print(f"  - 标题: {original_data.get('title', 'Unknown')}")
        print(f"  - 房间数: {len(original_data.get('rects', []))}")
        print(f"  - 门数: {len(original_data.get('doors', []))}")
        print(f"  - 注释数: {len(original_data.get('notes', []))}")
        
        # 使用Watabou适配器转换
        adapter = WatabouAdapter()
        unified_data = adapter.convert(original_data)
        
        if unified_data:
            print(f"\n转换后的统一格式数据:")
            print(f"  - 名称: {unified_data.name if hasattr(unified_data, 'name') else 'Unknown'}")
            print(f"  - 层级数: {len(unified_data.levels) if hasattr(unified_data, 'levels') else 0}")
            
            if hasattr(unified_data, 'levels') and unified_data.levels:
                level = unified_data.levels[0]
                print(f"  - 房间数: {len(level.get('rooms', []))}")
                print(f"  - 通道数: {len(level.get('corridors', []))}")
                print(f"  - 连接数: {len(level.get('connections', []))}")
                
                # 显示所有房间详情
                rooms = level.get('rooms', [])
                print(f"\n所有房间详情:")
                for i, room in enumerate(rooms):
                    pos = room.get('position', {})
                    size = room.get('size', {})
                    print(f"  {i+1}. ID: {room.get('id', 'Unknown')}")
                    print(f"     名称: {room.get('name', 'Unknown')}")
                    print(f"     位置: ({pos.get('x', 0)}, {pos.get('y', 0)})")
                    print(f"     尺寸: {size.get('width', 0)}x{size.get('height', 0)}")
                    print(f"     类型: is_room={room.get('is_room', False)}, is_corridor={room.get('is_corridor', False)}")
                    print(f"     描述: {room.get('description', '')[:50]}...")
                    print()
                
                # 显示连接详情
                connections = level.get('connections', [])
                print(f"连接详情 (前10个):")
                for i, conn in enumerate(connections[:10]):
                    print(f"  {i+1}. 从 {conn.get('from_room', 'Unknown')} 到 {conn.get('to_room', 'Unknown')} (门ID: {conn.get('door_id', 'Unknown')})")
                
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
    debug_watabou_adapter() 