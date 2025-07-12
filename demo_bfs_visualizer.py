#!/usr/bin/env python3
"""
BFS可视化器演示脚本
展示如何使用BFS可视化器分析地牢的可达性和路径多样性
"""

import sys
import os
import json
import logging
from pathlib import Path

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def find_sample_dungeon():
    """查找示例地牢文件"""
    # 查找可用的地牢文件
    sample_paths = [
        "samples/population_eval_524288/feasible_pop/ind_101.json",
        "output/thunderscar_shrine.json",
        "output/grimscar_hold.json",
        "output/blackspear_maze.json"
    ]
    
    for path in sample_paths:
        if os.path.exists(path):
            return path
    
    return None

def main():
    """主函数"""
    setup_logging()
    
    print("=== 地牢BFS算法可视化器演示 ===")
    print()
    
    # 查找示例文件
    sample_file = find_sample_dungeon()
    if not sample_file:
        print("错误: 找不到示例地牢文件")
        print("请确保以下文件之一存在:")
        print("  - samples/population_eval_524288/feasible_pop/ind_101.json")
        print("  - output/thunderscar_shrine.json")
        print("  - output/grimscar_hold.json")
        print("  - output/blackspear_maze.json")
        sys.exit(1)
    
    print(f"使用示例文件: {sample_file}")
    print()
    
    try:
        # 加载地牢数据
        print("正在加载地牢数据...")
        with open(sample_file, 'r', encoding='utf-8') as f:
            dungeon_data = json.load(f)
        
        # 显示地牢基本信息
        levels = dungeon_data.get('levels', [])
        if levels:
            level = levels[0]
            rooms = level.get('rooms', [])
            corridors = level.get('corridors', [])
            connections = level.get('connections', [])
            
            print(f"地牢信息:")
            print(f"  - 房间数量: {len(rooms)}")
            print(f"  - 走廊数量: {len(corridors)}")
            print(f"  - 连接数量: {len(connections)}")
            print(f"  - 总节点数: {len(rooms) + len(corridors)}")
            print()
            
            # 显示房间ID
            room_ids = [room.get('id', 'unknown') for room in rooms]
            print(f"房间ID: {', '.join(room_ids)}")
            print()
        
        # 尝试导入BFS可视化器
        try:
            from bfs_visualizer import create_bfs_visualizer
            print("BFS可视化器导入成功!")
            print()
            
            # 创建可视化器
            print("正在初始化BFS可视化器...")
            visualizer = create_bfs_visualizer(dungeon_data)
            print("初始化完成!")
            print()
            
            # 显示可用功能
            print("可用功能:")
            print("1. 可达性分析 - 显示每个节点的可达性分数")
            print("2. 路径多样性分析 - 显示房间对之间的路径数量")
            print("3. BFS遍历 - 实时显示BFS算法执行过程")
            print("4. 交互式窗口 - 包含所有功能的图形界面")
            print()
            
            # 询问用户选择
            print("请选择要演示的功能:")
            print("1. 可达性分析")
            print("2. 路径多样性分析") 
            print("3. BFS遍历")
            print("4. 交互式窗口")
            print("5. 退出")
            
            while True:
                choice = input("\n请输入选择 (1-5): ").strip()
                
                if choice == '1':
                    print("执行可达性分析...")
                    visualizer.visualize_accessibility_analysis()
                    break
                elif choice == '2':
                    print("执行路径多样性分析...")
                    visualizer.visualize_path_diversity()
                    break
                elif choice == '3':
                    if room_ids:
                        print(f"可用的起始节点: {', '.join(room_ids)}")
                        start_node = input("请输入起始节点ID: ").strip()
                        if start_node in room_ids:
                            target_node = input("请输入目标节点ID (可选): ").strip()
                            if not target_node or target_node in room_ids:
                                print(f"执行BFS遍历: 从 {start_node} 开始")
                                visualizer.visualize_bfs(start_node, target_node if target_node else None)
                                break
                            else:
                                print(f"无效的目标节点: {target_node}")
                        else:
                            print(f"无效的起始节点: {start_node}")
                    else:
                        print("没有可用的房间节点")
                    break
                elif choice == '4':
                    print("启动交互式窗口...")
                    print("在窗口中您可以:")
                    print("  - 点击'可达性分析'按钮查看每个节点的可达性")
                    print("  - 点击'路径多样性分析'按钮查看房间对之间的路径数量")
                    print("  - 点击'BFS遍历'按钮进行交互式BFS遍历")
                    visualizer.create_interactive_window()
                    break
                elif choice == '5':
                    print("退出演示")
                    break
                else:
                    print("无效选择，请输入1-5")
            
            print("演示完成!")
            
        except ImportError as e:
            print(f"错误: 无法导入BFS可视化器: {e}")
            print("请确保已安装所需的依赖包:")
            print("pip install matplotlib numpy")
            print()
            print("如果您在macOS上，可能还需要安装tkinter:")
            print("brew install python-tk")
            
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
    
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main() 