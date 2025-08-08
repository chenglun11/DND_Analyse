#!/usr/bin/env python3
"""
DnD地牢地图JSON适配器命令行工具
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
import json
import logging


# Add project root to path to allow running as a script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.adapter_manager import AdapterManager
from src.visualizer import visualize_dungeon
from src.quality_assessor import DungeonQualityAssessor

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """加载并读取JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        logger.error(f"JSON format error: {file_path}")
        return None
    except Exception as e:
        logger.error(f"Error reading file: {str(e)}")
        return None

def save_json_file(data: Dict[str, Any], file_path: str) -> bool:
    """将数据保存为JSON文件"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"File saved: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        return False

def convert_single_file(adapter_manager: AdapterManager, input_path: str, output_path: str, format_name: Optional[str] = None, visualize: bool = False, enable_spatial_inference: bool = True, adjacency_threshold: float = 1.0, enable_entrance_exit_identification: bool = True) -> bool:
    """转换单个文件"""
    source_data = load_json_file(input_path)
    if not source_data: return False
    
    unified_data = adapter_manager.convert(source_data, format_name, enable_spatial_inference, adjacency_threshold)
    if not unified_data: return False
    
    # 入口出口识别（如果启用）
    if enable_entrance_exit_identification:
        from src.schema import identify_entrance_exit
        unified_data = identify_entrance_exit(unified_data)
    
    if not save_json_file(unified_data, output_path): return False

    if visualize:
        vis_output_path = Path(output_path).with_suffix('.png')
        from src.visualizer import visualize_dungeon
        visualize_dungeon(unified_data, str(vis_output_path), show_room_ids=True, show_grid=True)
    
    return True

def convert_directory(adapter_manager: AdapterManager, input_dir: str, output_dir: str, format_name: Optional[str] = None, visualize: bool = False, enable_spatial_inference: bool = True, adjacency_threshold: float = 1.0, enable_entrance_exit_identification: bool = True) -> int:
    """转换目录中的所有JSON文件"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # 确保输出目录存在
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 查找所有JSON文件
    json_files = list(input_path.glob("*.json"))
    if not json_files:
        print(f"No JSON files found in directory: {input_dir}")
        return 0
    
    success_count = 0
    for json_file in json_files:
        print(f"Processing: {json_file.name}")
        
        # 加载源文件
        source_data = load_json_file(str(json_file))
        if not source_data:
            continue
        
        # 转换数据
        unified_data = adapter_manager.convert(source_data, format_name, enable_spatial_inference, adjacency_threshold)
        if not unified_data:
            continue
        
        # 入口出口识别（如果启用）
        if enable_entrance_exit_identification:
            from src.schema import identify_entrance_exit
            unified_data = identify_entrance_exit(unified_data)
        
        # 保存转换后的文件
        output_file = output_path / json_file.name
        if save_json_file(unified_data, str(output_file)):
            success_count += 1
            print(f"✓ Successfully converted: {json_file.name}")
            if visualize:
                vis_output_path = output_path / json_file.with_suffix('.png').name
                from src.visualizer import visualize_dungeon
                visualize_dungeon(unified_data, str(vis_output_path), show_room_ids=True, show_grid=True)
        else:
            print(f"✗ Failed to convert: {json_file.name}")
    
    return success_count

def detect_format(adapter_manager: AdapterManager, file_path: str) -> str:
    """检测文件格式"""
    source_data = load_json_file(file_path)
    if not source_data: return "Unknown"
    detected_format = adapter_manager.detect_format(source_data)
    return detected_format if detected_format else "Unknown"

# 合并visualize相关命令和实现，只保留全细节可视化
# 删除outline等简化模式及相关参数，命令行只保留一个visualize命令
def visualize_file(input_path: str, output_path: Optional[str] = None, show_room_ids: bool = True, show_corridor_ids: bool = True, show_grid: bool = True, show_game_elements: bool = True):
    """为指定的统一格式JSON文件生成可视化图像（默认显示所有细节）"""
    print(f"Generating visualization for {input_path}...")
    unified_data = load_json_file(input_path)
    if not unified_data:
        print(f"✗ Failed to load file: {input_path}")
        return

    if not output_path:
        output_path = str(Path(input_path).with_suffix('.png'))
    
    # 默认画所有细节
    from src.visualizer import visualize_dungeon
    visualize_dungeon(unified_data, output_path, show_room_ids=show_room_ids, show_grid=show_grid, show_game_elements=show_game_elements)

# 合并/精简assess_quality相关实现，只保留一套评估报告输出逻辑
def assess_quality(input_file: str, enable_spatial_inference: bool = True, adjacency_threshold: float = 1.0) -> bool:
    """评估地图质量，并自动保存详细报告到output/reports"""
    import os
    import json
    try:
        # 读取输入文件
        with open(input_file, 'r', encoding='utf-8') as f:
            dungeon_data = json.load(f)
        # 初始化质量评估器
        assessor = DungeonQualityAssessor(
            enable_spatial_inference=enable_spatial_inference,
            adjacency_threshold=adjacency_threshold
        )
        # 执行评估
        result = assessor.assess_quality(dungeon_data)
        # 输出评估报告
        print("=" * 50)
        print("Dungeon Map Quality Assessment Report")
        print("=" * 50)
        print(f"\nOverall Score: {result['overall_score']:.3f}")
        print(f"Grade: {result['grade']}")
        if result.get('spatial_inference_used'):
            print(f"\nSpatial Inference: Enabled (Threshold: {adjacency_threshold})")
        print(f"\nDetailed Metrics:")
        for metric, score in result['scores'].items():
            print(f"  {metric}: {score:.3f}")
        print(f"\nImprovements:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"  {i}. {rec}")
        print("=" * 50)
        # 自动保存详细报告
        report_dir = "output/reports"
        os.makedirs(report_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        report_path = os.path.join(report_dir, f"{base_name}_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"详细评估报告已保存到: {report_path}")
        return True
    except Exception as e:
        logger.error(f"Assessment failed: {e}")
        return False

def batch_assess(input_dir: str, output_dir: str, enable_spatial_inference: bool = True, adjacency_threshold: float = 1.0, timeout_per_file: int = 30):
    """批量评估地图质量"""
    try:
        from src.batch_assess import batch_assess_quality
        batch_assess_quality(input_dir, output_dir, enable_spatial_inference, adjacency_threshold, timeout_per_file)
        logger.info(f"Batch assessment completed: {output_dir}")
    except Exception as e:
        logger.error(f"Batch assessment failed: {e}")
        sys.exit(1)

# ======= argparse 实现 =======
def main():
    parser = argparse.ArgumentParser(
        description="DnD Dungeon JSON Adapter - Convert various dungeon formats to unified format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
  # Convert single file (auto-detect format)
  python cli.py convert samples/onepage_example.json output/

  # Convert single file (specify format)
  python cli.py convert samples/onepage_example.json output/ --format onepage_dungeon

  # Convert entire directory
  python cli.py convert-dir samples/ output/

  # Detect file format
  python cli.py detect samples/onepage_example.json

  # List supported formats
  python cli.py list-formats

  # Generate visualization image for converted JSON file
  python cli.py visualize output/test_onepage_example.json

  # Assess single file quality
  python cli.py assess output/test_onepage_example.json

  # Batch assess directory quality
  python cli.py batch-assess output/watabou_test/ output/batch_reports/
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令 / available commands')
    
    # convert 命令
    convert_parser = subparsers.add_parser('convert', help='转换单个文件 / convert single file')
    convert_parser.add_argument('input', help='输入文件路径 / input file path')
    convert_parser.add_argument('output', help='输出文件路径或目录 / output file path or directory')
    convert_parser.add_argument('--format', '-f', help='指定源格式（可选，会自动检测） / specify source format (optional, will be detected automatically)')
    convert_parser.add_argument('--visualize', action='store_true', help='为转换成功的文件生成可视化PNG图像 / generate visualization PNG image for successfully converted file')
    convert_parser.add_argument('--no-spatial-inference', action='store_true', help='禁用空间推断功能 / disable spatial inference')
    convert_parser.add_argument('--adjacency-threshold', type=float, default=1.0, help='邻接判定阈值 (默认: 1.0) / adjacency threshold (default: 1.0)')
    convert_parser.add_argument('--no-entrance-exit-identification', action='store_true', help='禁用入口出口识别功能 / disable entrance/exit identification')
    
    # convert-dir 命令
    convert_dir_parser = subparsers.add_parser('convert-dir', help='转换目录中的所有JSON文件 / convert all JSON files in the directory')
    convert_dir_parser.add_argument('input', help='输入目录路径 / input directory path')
    convert_dir_parser.add_argument('output', help='输出目录路径 / output directory path')
    convert_dir_parser.add_argument('--format', '-f', help='指定源格式（可选，会自动检测） / specify source format (optional, will be detected automatically)')
    convert_dir_parser.add_argument('--visualize', action='store_true', help='为每个转换成功的文件生成可视化PNG图像 / generate visualization PNG image for each successfully converted file')
    convert_dir_parser.add_argument('--no-spatial-inference', action='store_true', help='禁用空间推断功能 / disable spatial inference')
    convert_dir_parser.add_argument('--adjacency-threshold', type=float, default=1.0, help='邻接判定阈值 (默认: 1.0) / adjacency threshold (default: 1.0)')
    convert_dir_parser.add_argument('--no-entrance-exit-identification', action='store_true', help='禁用入口出口识别功能 / disable entrance/exit identification')
    
    # detect 命令
    detect_parser = subparsers.add_parser('detect', help='检测文件格式 / detect file format')
    detect_parser.add_argument('file', help='要检测的文件路径 / file path to detect')
    
    # list-formats 命令
    subparsers.add_parser('list-formats', help='列出支持的格式 / list supported formats')

    # 'visualize' command
    visualize_parser = subparsers.add_parser('visualize', help='为统一格式的JSON文件创建可视化图像 / create visualization image for unified JSON file')
    visualize_parser.add_argument('input', help='输入的统一格式JSON文件路径 / input unified JSON file path')
    visualize_parser.add_argument('output', nargs='?', default=None, help='输出的PNG图像文件路径 (可选) / output PNG image file path (optional)')
    visualize_parser.add_argument('--no-room-ids', action='store_true', default=False, help='不显示房间ID / do not show room ids')
    visualize_parser.add_argument('--no-corridor-ids', action='store_true', default=False, help='不显示走廊ID / do not show corridor ids')
    visualize_parser.add_argument('--no-grid', action='store_true', default=False, help='不显示grid / do not show grid')
    visualize_parser.add_argument('--no-game-elements', action='store_true', default=False, help='不显示游戏元素 / do not show game elements')
    
    # 'assess' command
    assess_parser = subparsers.add_parser('assess', help='评估地图质量 / assess dungeon quality')
    assess_parser.add_argument('input', help='输入文件路径 / input file path')
    assess_parser.add_argument('--infer-connections', '-i', action='store_true', 
                              help='在评估前启用空间推断来补全连接')
    assess_parser.add_argument('--no-spatial-inference', action='store_true', 
                              help='禁用空间推断功能')
    assess_parser.add_argument('--adjacency-threshold', type=float, default=1.0,
                              help='邻接判定阈值 (默认: 1.0)')

    # 'batch-assess' command
    batch_parser = subparsers.add_parser('batch-assess', help='批量评估地图质量 / batch assess dungeon quality')
    batch_parser.add_argument('input_dir', help='输入目录路径 / input directory path')
    batch_parser.add_argument('output_dir', help='输出目录路径 / output directory path')
    batch_parser.add_argument('--no-spatial-inference', action='store_true',
                              help='禁用空间推断功能')
    batch_parser.add_argument('--adjacency-threshold', type=float, default=1.0,
                              help='邻接判定阈值 (默认: 1.0)')
    batch_parser.add_argument('--timeout', type=int, default=30,
                              help='每个文件的超时时间（秒）(默认: 30)')

    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    adapter_manager = AdapterManager()

    if args.command == 'convert':
        input_path = args.input
        output_path = args.output
        
        # 如果输出是目录，使用原文件名
        if os.path.isdir(output_path) or not output_path.endswith('.json'):
            if not os.path.exists(output_path):
                os.makedirs(output_path, exist_ok=True)
            output_path = os.path.join(output_path, os.path.basename(input_path))
        
        if convert_single_file(adapter_manager, input_path, output_path, args.format, args.visualize, not args.no_spatial_inference, args.adjacency_threshold, not args.no_entrance_exit_identification):
            print(f"✓ Successfully converted: {output_path}")
        else:
            print(f"✗ Failed to convert")
            sys.exit(1)
    
    elif args.command == 'convert-dir':
        success_count = convert_directory(adapter_manager, args.input, args.output, args.format, args.visualize, not args.no_spatial_inference, args.adjacency_threshold, not args.no_entrance_exit_identification)
        print(f"\nConversion completed: {success_count} files successfully converted")
    
    elif args.command == 'detect':
        detected_format = detect_format(adapter_manager, args.file)
        print(f"Detected format: {detected_format}")
    
    elif args.command == 'list-formats':
        print("Supported formats:")
        for format_name in adapter_manager.get_supported_formats():
            print(f"  - {format_name}")

    elif args.command == 'visualize':
        visualize_file(
            args.input, 
            args.output, 
            show_room_ids=not args.no_room_ids, 
            show_corridor_ids=not args.no_corridor_ids,
            show_grid=not args.no_grid,
            show_game_elements=not args.no_game_elements
        )

    elif args.command == 'assess':
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                dungeon_data = json.load(f)

            if args.infer_connections:
                logger.info("Enable spatial inference to complete connections...")
                from src.spatial_inference import infer_connections_from_geometry
                if dungeon_data.get('levels'):
                    level = dungeon_data['levels'][0]
                    all_nodes = level.get('rooms', []) + level.get('corridors', [])
                    if all_nodes:
                        inferred_connections = infer_connections_from_geometry(all_nodes, connection_threshold=2.0)
                        existing_connections_count = len(level.get('connections', []))
                        level['connections'] = inferred_connections
                        logger.info(f"Spatial inference completed. Replaced {existing_connections_count} existing connections with {len(inferred_connections)} new connections.")

            assessor = DungeonQualityAssessor(
                enable_spatial_inference=not args.no_spatial_inference,
                adjacency_threshold=args.adjacency_threshold
            )
            report = assessor.assess_quality(dungeon_data)
            print("\n" + "="*50)
            print("Dungeon Map Quality Assessment Report")
            print("="*50 + "\n")
            print(f"Overall Score: {report['overall_score']:.3f}")
            print(f"Grade: {report['grade']}")
            print("\nDetailed Metrics:")
            for rule_name, rule_result in report['scores'].items():
                score = rule_result.get('score', 0.0) if isinstance(rule_result, dict) else rule_result
                print(f"  {rule_name}: {score:.3f}")
            print("\nImprovements:")
            for rec in report.get('recommendations', []):
                print(f"  - {rec}")
            print("\n" + "="*50 + "\n")
            # 自动保存详细报告
            report_dir = "output/reports"
            os.makedirs(report_dir, exist_ok=True)
            base_name = os.path.splitext(os.path.basename(args.input))[0]
            auto_report_path = os.path.join(report_dir, f"{base_name}_report.json")
            with open(auto_report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"Automaticaly saved detailed report to: {auto_report_path}")
        except Exception as e:
            logger.error(f"Error during assessment: {e}")
            sys.exit(1)

    elif args.command == 'batch-assess':
        try:
            results = batch_assess(args.input_dir, args.output_dir, not args.no_spatial_inference, args.adjacency_threshold, args.timeout)
            
            # 显示总体统计
            print("\n" + "=" * 60)
            print("BATCH ASSESSMENT SUMMARY")
            print("=" * 60)
            
            # 计算总体统计
            valid_results = {k: v for k, v in results.items() if v.get('status') == 'success'}
            if valid_results:
                scores = [r['overall_score'] for r in valid_results.values()]
                avg_score = sum(scores) / len(scores)
                max_score = max(scores)
                min_score = min(scores)
                
                best_map = max(valid_results.items(), key=lambda x: x[1]['overall_score'])
                worst_map = min(valid_results.items(), key=lambda x: x[1]['overall_score'])
                
                # 等级分布
                grade_counts = {}
                for result in valid_results.values():
                    grade = result['grade']
                    grade_counts[grade] = grade_counts.get(grade, 0) + 1
                
                print(f"Total Maps: {len(results)}")
                print(f"Valid Maps: {len(valid_results)}")
                print(f"Failed Maps: {len(results) - len(valid_results)}")
                print(f"\nOverall Statistics:")
                print(f"  Average Score: {avg_score:.3f}")
                print(f"  Max Score: {max_score:.3f} ({best_map[0]})")
                print(f"  Min Score: {min_score:.3f} ({worst_map[0]})")
                
                print(f"\nGrade Distribution:")
                for grade, count in sorted(grade_counts.items(), reverse=True):
                    percentage = (count / len(valid_results)) * 100
                    print(f"  {grade}: {count} maps ({percentage:.1f}%)")
                
                # 指标统计
                metrics = ['accessibility', 'degree_variance', 'door_distribution', 'dead_end_ratio', 
                          'key_path_length', 'loop_ratio', 'path_diversity', 'treasure_monster_distribution', 
                          'geometric_balance']
                
                print(f"\nMetric Averages:")
                for metric in metrics:
                    values = []
                    for r in valid_results.values():
                        metric_result = r.get('detailed_metrics', {}).get(metric, {})
                        if isinstance(metric_result, dict):
                            score = metric_result.get('score', 0.0)
                        else:
                            score = metric_result
                        values.append(score)
                    
                    if values:
                        avg = sum(values) / len(values)
                        print(f"  {metric}: {avg:.3f}")
            
            print("=" * 60)
            print("Detailed reports saved to output directory")
            print("=" * 60)
            
        except Exception as e:
            logger.error(f"Error during batch assessment: {e}")
            sys.exit(1)

if __name__ == '__main__':
    main() 