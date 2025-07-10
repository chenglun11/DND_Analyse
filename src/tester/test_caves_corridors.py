#!/usr/bin/env python3
"""
测试Caves Of Chaos地牢的走廊可视化
"""

import json
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from visualizer import visualize_dungeon
except ImportError:
    # 如果直接导入失败，尝试相对导入
    sys.path.insert(0, os.path.dirname(__file__))
    from src.visualizer import visualize_dungeon

def main():
    # 读取包含走廊的地牢数据
    input_file = "output/caves_with_corridors.json"
    output_file = "output/caves_corridors_visualization.png"
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            dungeon_data = json.load(f)
        
        print(f"读取地牢数据: {input_file}")
        print(f"房间数量: {len(dungeon_data['levels'][0]['rooms'])}")
        print(f"走廊数量: {len(dungeon_data['levels'][0]['corridors'])}")
        print(f"墙体数量: {len(dungeon_data['levels'][0]['walls'])}")
        
        # 可视化地牢
        success = visualize_dungeon(
            dungeon_data=dungeon_data,
            output_path=output_file,
            figsize=(16, 12),
            dpi=150,
            show_connections=True,
            show_room_ids=True,
            show_grid=True
        )
        
        if success:
            print(f"✓ 可视化成功: {output_file}")
        else:
            print("✗ 可视化失败")
            
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 