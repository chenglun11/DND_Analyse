#!/usr/bin/env python3
"""
专门测试blackspear_maze的脚本
"""

import sys
import os
import json
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.adapter_manager import AdapterManager
from src.visualizer import visualize_from_file

def test_blackspear_maze():
    """测试blackspear_maze的完整转换和可视化流程"""
    print("=== Blackspear Maze 测试 ===\n")
    
    input_file = "samples/source_format_2/blackspear_maze.json"
    output_file = "output/blackspear_maze_test.json"
    vis_file = "output/blackspear_maze_test.png"
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"❌ 输入文件不存在: {input_file}")
        return False
    
    print(f"📁 输入文件: {input_file}")
    
    # 创建适配器管理器
    adapter_manager = AdapterManager()
    
    try:
        # 读取源文件
        with open(input_file, 'r', encoding='utf-8') as f:
            source_data = json.load(f)
        
        print(f"📖 成功读取源文件")
        print(f"   - 标题: {source_data.get('title', 'Unknown')}")
        print(f"   - 版本: {source_data.get('version', 'Unknown')}")
        print(f"   - 矩形数量: {len(source_data.get('rects', []))}")
        print(f"   - 门数量: {len(source_data.get('doors', []))}")
        print(f"   - 注释数量: {len(source_data.get('notes', []))}")
        
        # 检测格式
        detected_format = adapter_manager.detect_format(source_data)
        print(f"🔍 检测到的格式: {detected_format}")
        
        # 转换数据
        print("\n🔄 开始转换...")
        unified_data = adapter_manager.convert(source_data)
        if not unified_data:
            print("❌ 转换失败")
            return False
        
        print("✅ 转换成功")
        
        # 保存转换后的数据
        os.makedirs("output", exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(unified_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 保存转换结果: {output_file}")
        
        # 分析转换结果
        levels = unified_data.get('levels', [])
        if levels:
            level = levels[0]
            rooms = level.get('rooms', [])
            corridors = level.get('corridors', [])
            connections = level.get('connections', [])
            
            print(f"\n📊 转换结果统计:")
            print(f"   - 房间数量: {len(rooms)}")
            print(f"   - 走廊数量: {len(corridors)}")
            print(f"   - 连接数量: {len(connections)}")
            
            # 显示房间信息
            print(f"\n🏠 房间详情:")
            for i, room in enumerate(rooms[:5]):  # 只显示前5个房间
                name = room.get('name', room.get('id', 'Unknown'))
                desc = room.get('description', '')
                if desc:
                    desc = desc[:50] + "..." if len(desc) > 50 else desc
                print(f"   {i+1}. {name}: {desc}")
            
            if len(rooms) > 5:
                print(f"   ... 还有 {len(rooms) - 5} 个房间")
        
        # 生成可视化
        print(f"\n🎨 生成可视化...")
        if visualize_from_file(output_file, vis_file):
            print(f"✅ 可视化成功: {vis_file}")
        else:
            print("❌ 可视化失败")
            return False
        
        print(f"\n🎉 测试完成！")
        print(f"   - JSON文件: {output_file}")
        print(f"   - 图像文件: {vis_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_blackspear_structure():
    """分析blackspear_maze的原始结构"""
    print("\n=== Blackspear Maze 结构分析 ===\n")
    
    input_file = "samples/source_format_2/blackspear_maze.json"
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("📋 原始数据结构:")
        print(f"   - 版本: {data.get('version')}")
        print(f"   - 标题: {data.get('title')}")
        print(f"   - 故事: {data.get('story', '')[:100]}...")
        
        rects = data.get('rects', [])
        doors = data.get('doors', [])
        notes = data.get('notes', [])
        
        print(f"\n📐 矩形 (rects): {len(rects)} 个")
        if rects:
            print(f"   第一个矩形: x={rects[0]['x']}, y={rects[0]['y']}, w={rects[0]['w']}, h={rects[0]['h']}")
            print(f"   最后一个矩形: x={rects[-1]['x']}, y={rects[-1]['y']}, w={rects[-1]['w']}, h={rects[-1]['h']}")
        
        print(f"\n🚪 门 (doors): {len(doors)} 个")
        if doors:
            print(f"   第一个门: x={doors[0]['x']}, y={doors[0]['y']}, dir={doors[0]['dir']}, type={doors[0]['type']}")
        
        print(f"\n📝 注释 (notes): {len(notes)} 个")
        for note in notes:
            print(f"   - {note.get('ref', '?')}: {note.get('text', '')[:50]}...")
        
        # 分析矩形大小分布
        sizes = [(r['w'], r['h']) for r in rects]
        small_rects = [s for s in sizes if s[0] <= 2 and s[1] <= 2]
        large_rects = [s for s in sizes if s[0] > 5 or s[1] > 5]
        
        print(f"\n📊 矩形大小分析:")
        print(f"   - 小矩形 (≤2x2): {len(small_rects)} 个")
        print(f"   - 大矩形 (>5x5): {len(large_rects)} 个")
        print(f"   - 中等矩形: {len(rects) - len(small_rects) - len(large_rects)} 个")
        
    except Exception as e:
        print(f"❌ 分析过程中出错: {e}")

if __name__ == "__main__":
    print("Blackspear Maze 完整测试")
    print("=" * 50)
    
    # 分析原始结构
    analyze_blackspear_structure()
    
    # 测试完整流程
    success = test_blackspear_maze()
    
    if success:
        print("\n✅ 所有测试通过！")
    else:
        print("\n❌ 测试失败！")
        sys.exit(1) 