#!/usr/bin/env python3
"""
BFS可视化器命令行工具
用于启动地牢BFS算法可视化窗口
"""

import sys
import os
import json
import argparse
import logging
from pathlib import Path

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from bfs_visualizer import create_bfs_visualizer, visualize_bfs_from_file
except ImportError as e:
    print(f"错误: 无法导入BFS可视化器模块: {e}")
    print("请确保已安装所需的依赖包:")
    print("pip install matplotlib numpy")
    sys.exit(1)

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='地牢BFS算法可视化器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python bfs_visualizer_cli.py samples/population_eval_524288/feasible_pop/ind_101.json
  python bfs_visualizer_cli.py output/thunderscar_shrine.json
        """
    )
    
    parser.add_argument(
        'input_file',
        help='输入的地牢JSON文件路径'
    )
    
    parser.add_argument(
        '--start-node',
        help='BFS起始节点ID (可选)'
    )
    
    parser.add_argument(
        '--target-node', 
        help='BFS目标节点ID (可选)'
    )
    
    parser.add_argument(
        '--analysis-type',
        choices=['bfs', 'accessibility', 'path-diversity', 'interactive'],
        default='interactive',
        help='分析类型 (默认: interactive)'
    )
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging()
    
    # 检查输入文件
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"错误: 输入文件不存在: {input_path}")
        sys.exit(1)
    
    try:
        # 加载地牢数据
        print(f"正在加载地牢数据: {input_path}")
        with open(input_path, 'r', encoding='utf-8') as f:
            dungeon_data = json.load(f)
        
        # 创建可视化器
        print("正在初始化BFS可视化器...")
        visualizer = create_bfs_visualizer(dungeon_data)
        
        # 根据分析类型执行不同的可视化
        if args.analysis_type == 'bfs':
            if not args.start_node:
                print("错误: BFS分析需要指定起始节点 (--start-node)")
                sys.exit(1)
            
            print(f"执行BFS遍历: 从 {args.start_node} 开始")
            if args.target_node:
                print(f"目标节点: {args.target_node}")
            
            visualizer.visualize_bfs(args.start_node, args.target_node)
            
        elif args.analysis_type == 'accessibility':
            print("执行可达性分析...")
            visualizer.visualize_accessibility_analysis()
            
        elif args.analysis_type == 'path-diversity':
            print("执行路径多样性分析...")
            visualizer.visualize_path_diversity()
            
        elif args.analysis_type == 'interactive':
            print("启动交互式窗口...")
            print("在窗口中您可以:")
            print("  - 点击'可达性分析'按钮查看每个节点的可达性")
            print("  - 点击'路径多样性分析'按钮查看房间对之间的路径数量")
            print("  - 点击'BFS遍历'按钮进行交互式BFS遍历")
            visualizer.create_interactive_window()
        
        print("可视化完成!")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main() 