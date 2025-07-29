#!/usr/bin/env python3
"""
可视化功能测试脚本
测试地牢可视化生成功能
"""

import json
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.visualizer import DungeonVisualizer, visualize_dungeon
from src.adapter_manager import AdapterManager

def test_visualization():
    """测试可视化功能"""
    print("开始测试可视化功能...")
    
    # 初始化组件
    adapter_manager = AdapterManager()
    visualizer = DungeonVisualizer()
    
    # 测试数据文件
    test_files = [
        "samples/watabou_test/abandoned_hold_of_rhun-hakrax.json",
        "samples/edger/1.json",
        "samples/source_format_1/donjon_example.json"
    ]
    
    for test_file in test_files:
        if not os.path.exists(test_file):
            print(f"跳过不存在的文件: {test_file}")
            continue
            
        print(f"\n测试文件: {test_file}")
        
        try:
            # 读取测试数据
            with open(test_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 转换为统一格式
            unified_data = adapter_manager.convert(data)
            
            if unified_data is None:
                print(f"  ❌ 无法转换文件格式")
                continue
            
            print(f"  ✅ 成功转换为统一格式")
            print(f"  - 层级数: {len(unified_data.get('levels', []))}")
            
            if unified_data.get('levels'):
                level = unified_data['levels'][0]
                print(f"  - 房间数: {len(level.get('rooms', []))}")
                print(f"  - 通道数: {len(level.get('corridors', []))}")
                print(f"  - 连接数: {len(level.get('connections', []))}")
            
            # 测试可视化数据提取
            try:
                vis_data = visualizer._extract_visualization_data(unified_data)
                print(f"  ✅ 成功提取可视化数据")
                print(f"  - 前端房间数: {len(vis_data.get('rooms', []))}")
                print(f"  - 前端通道数: {len(vis_data.get('corridors', []))}")
                print(f"  - 地图尺寸: {vis_data.get('width', 0)} x {vis_data.get('height', 0)}")
            except Exception as e:
                print(f"  ❌ 可视化数据提取失败: {e}")
            
            # 测试图像生成
            output_path = f"test_output_{Path(test_file).stem}.png"
            try:
                # 确保输出目录存在
                output_dir = Path(output_path).parent
                output_dir.mkdir(exist_ok=True)
                
                success = visualize_dungeon(
                    unified_data, 
                    output_path,
                    show_connections=True,
                    show_room_ids=True,
                    show_grid=True,
                    show_game_elements=True
                )
                
                if success:
                    print(f"  ✅ 成功生成可视化图像: {output_path}")
                    if os.path.exists(output_path):
                        file_size = os.path.getsize(output_path)
                        print(f"  - 文件大小: {file_size} bytes")
                else:
                    print(f"  ❌ 可视化图像生成失败")
                    
            except Exception as e:
                print(f"  ❌ 图像生成异常: {e}")
            
        except Exception as e:
            print(f"  ❌ 处理文件时出错: {e}")
    
    print("\n可视化功能测试完成!")

def test_edgar_visualization():
    """专门测试Edgar格式可视化"""
    print("\n开始测试Edgar格式可视化...")
    
    edgar_file = "samples/edger/1.json"
    if not os.path.exists(edgar_file):
        print(f"Edgar测试文件不存在: {edgar_file}")
        return
    
    try:
        with open(edgar_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        adapter_manager = AdapterManager()
        unified_data = adapter_manager.convert(data)
        
        if unified_data:
            visualizer = DungeonVisualizer()
            
            # 测试Edgar专用可视化
            output_path = "test_edgar_visualization.png"
            success = visualizer._visualize_edgar_dungeon(
                unified_data,
                output_path,
                show_connections=True,
                show_room_ids=True,
                show_grid=True,
                show_game_elements=True
            )
            
            if success:
                print(f"✅ Edgar可视化成功: {output_path}")
            else:
                print("❌ Edgar可视化失败")
        
    except Exception as e:
        print(f"❌ Edgar可视化测试失败: {e}")

if __name__ == "__main__":
    test_visualization()
    test_edgar_visualization() 