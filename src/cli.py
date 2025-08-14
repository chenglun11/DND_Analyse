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
from src.csv_exporter import CSVExporter

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
    """转换目录中的所有JSON文件（包括子文件夹）"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # 确保输出目录存在
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 递归查找所有JSON文件
    json_files = list(input_path.rglob("*.json"))
    if not json_files:
        print(f"No JSON files found in directory and subdirectories: {input_dir}")
        return 0
    
    print(f"Found {len(json_files)} JSON files in {input_dir} and subdirectories")
    
    success_count = 0
    for json_file in json_files:
        # 计算相对路径以保持目录结构
        relative_path = json_file.relative_to(input_path)
        print(f"Processing: {relative_path}")
        
        # 加载源文件
        source_data = load_json_file(str(json_file))
        if not source_data:
            print(f"✗ Failed to load: {relative_path}")
            continue
        
        # 转换数据
        unified_data = adapter_manager.convert(source_data, format_name, enable_spatial_inference, adjacency_threshold)
        if not unified_data:
            print(f"✗ Failed to convert: {relative_path}")
            continue
        
        # 入口出口识别（如果启用）
        if enable_entrance_exit_identification:
            from src.schema import identify_entrance_exit
            unified_data = identify_entrance_exit(unified_data)
        
        # 保存转换后的文件，保持目录结构
        output_file = output_path / relative_path
        # 确保输出文件的目录存在
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        if save_json_file(unified_data, str(output_file)):
            success_count += 1
            print(f"✓ Successfully converted: {relative_path}")
            if visualize:
                vis_output_path = output_file.with_suffix('.png')
                # 确保可视化文件的目录存在
                vis_output_path.parent.mkdir(parents=True, exist_ok=True)
                from src.visualizer import visualize_dungeon
                visualize_dungeon(unified_data, str(vis_output_path), show_room_ids=True, show_grid=True)
                print(f"✓ Visualization saved: {vis_output_path.relative_to(output_path)}")
        else:
            print(f"✗ Failed to save: {relative_path}")
    
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

def batch_assess(input_dir: str, output_dir: str, enable_spatial_inference: bool = True, adjacency_threshold: float = 1.0, timeout_per_file: int = 30) -> Dict[str, Any]:
    """批量评估地图质量"""
    try:
        from src.batch_assess import batch_assess_quality
        results = batch_assess_quality(input_dir, output_dir, enable_spatial_inference, adjacency_threshold, timeout_per_file)
        logger.info(f"批量评估完成: {output_dir}")
        return results
    except Exception as e:
        logger.error(f"批量评估失败: {e}")
        raise

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

  # Convert entire directory (including subdirectories)
  python cli.py convert-dir samples/ output/

  # Detect file format
  python cli.py detect samples/onepage_example.json

  # List supported formats
  python cli.py list-formats

  # Generate visualization image for converted JSON file
  python cli.py visualize output/test_onepage_example.json

  # Assess single file quality
  python cli.py assess output/test_onepage_example.json

  # Batch assess directory quality (including subdirectories)
  python cli.py batch-assess output/watabou_test/ output/batch_reports/

  # Statistical analysis of batch results
  python cli.py statistical-analysis output/watabou_test_batch_report.json

  # Cross-dataset analysis for F_Q dataset
  python cli.py cross-dataset-analysis --input output/F_Q_Report --output output/F_Q_Report/SA

  # Export validation data to CSV
  python cli.py export-csv --validation output/validation_report.json --output validation_data.csv

  # Export descriptive statistics to CSV
  python cli.py export-csv --descriptive output/statistical_analysis_report.json --output descriptive_stats.csv

  # Auto-export all data from directory to CSV
  python cli.py export-csv --auto-dir output/ --output-dir csv_exports/
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
    convert_dir_parser = subparsers.add_parser('convert-dir', help='转换目录中的所有JSON文件（包括子文件夹） / convert all JSON files in directory and subdirectories')
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
    batch_parser = subparsers.add_parser('batch-assess', help='批量评估地图质量（包括子文件夹） / batch assess dungeon quality (including subdirectories)')
    batch_parser.add_argument('input_dir', help='输入目录路径 / input directory path')
    batch_parser.add_argument('output_dir', help='输出目录路径 / output directory path')
    batch_parser.add_argument('--no-spatial-inference', action='store_true',
                              help='禁用空间推断功能')
    batch_parser.add_argument('--adjacency-threshold', type=float, default=1.0,
                              help='邻接判定阈值 (默认: 1.0)')
    batch_parser.add_argument('--timeout', type=int, default=30,
                              help='每个文件的超时时间（秒）(默认: 30)')

    # 'statistical-analysis' command
    stats_parser = subparsers.add_parser('statistical-analysis', help='统计分析批量评估结果 / statistical analysis of batch assessment results')
    stats_parser.add_argument('summary_path', help='批量评估汇总JSON文件路径 / batch assessment summary JSON file path')
    stats_parser.add_argument('--output', '-o', default='output',
                             help='分析结果输出目录 (默认: output) / analysis results output directory (default: output)')

    # 'cross-dataset-analysis' command
    cross_parser = subparsers.add_parser('cross-dataset-analysis', help='跨数据集分析 / cross-dataset analysis')
    cross_parser.add_argument('--input', '-i', default='output/F_Q_Report',
                             help='输入根目录路径 (默认: output/F_Q_Report) / input root directory path (default: output/F_Q_Report)')
    cross_parser.add_argument('--output', '-o', default=None,
                             help='输出目录路径 (可选) / output directory path (optional)')

    # 'export-csv' command
    csv_parser = subparsers.add_parser('export-csv', help='导出数据为CSV格式 / export data to CSV format')
    csv_parser.add_argument('--validation', help='导出validation报告数据 / export validation report data')
    csv_parser.add_argument('--descriptive', help='导出描述性统计数据 / export descriptive statistics data')
    csv_parser.add_argument('--correlation', help='导出相关性分析数据 / export correlation analysis data')
    csv_parser.add_argument('--batch', help='导出批量质量评估数据 / export batch quality assessment data')
    csv_parser.add_argument('--auto-dir', help='自动导出目录中的所有数据 / auto-export all data from directory')
    csv_parser.add_argument('--output', help='输出CSV文件路径（单个导出时） / output CSV file path (for single exports)')
    csv_parser.add_argument('--output-dir', default='output/csv_exports', 
                           help='输出目录路径（自动导出时，默认: output/csv_exports) / output directory path (for auto export, default: output/csv_exports)')

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

    elif args.command == 'statistical-analysis':
        try:
            from src.statistical_analysis import StatisticalAnalyzer
            
            # 验证输入文件
            if not os.path.exists(args.summary_path):
                print(f"Error: Summary file not found: {args.summary_path}")
                sys.exit(1)
            
            # 执行统计分析
            analyzer = StatisticalAnalyzer()
            success = analyzer.analyze_batch_results(args.summary_path, args.output)
            
            if success:
                print(f"\n✓ Statistical analysis completed successfully!")
                print(f"Results saved to: {args.output}/")
            else:
                print(f"\n✗ Statistical analysis failed!")
                sys.exit(1)
                
        except Exception as e:
            logger.error(f"Error during statistical analysis: {e}")
            sys.exit(1)

    elif args.command == 'cross-dataset-analysis':
        try:
            from src.batch_assess import analyze_cross_datasets
            
            # 验证输入目录
            if not os.path.exists(args.input):
                print(f"Error: Input directory not found: {args.input}")
                sys.exit(1)
            
            # 执行跨数据集分析
            results = analyze_cross_datasets(args.input, args.output)
            
            if 'error' in results:
                print(f"✗ Cross-dataset analysis failed: {results['error']}")
                sys.exit(1)
            else:
                print(f"\n✓ Cross-dataset analysis completed successfully!")
                output_dir = args.output if args.output else os.path.join(args.input, 'SA')
                print(f"Results saved to: {output_dir}/")
                
        except Exception as e:
            logger.error(f"Error during cross-dataset analysis: {e}")
            sys.exit(1)

    elif args.command == 'export-csv':
        try:
            exporter = CSVExporter()
            success = False
            
            if args.auto_dir:
                # 自动导出模式
                if not os.path.exists(args.auto_dir):
                    print(f"Error: Input directory not found: {args.auto_dir}")
                    sys.exit(1)
                
                results = exporter.export_all_from_directories(args.auto_dir, args.output_dir)
                
                print(f"\nAuto-export results from {args.auto_dir}:")
                print("=" * 60)
                for task, result in results.items():
                    status = "✓" if result else "✗"
                    print(f"{status} {task}")
                
                success_count = sum(results.values())
                total_count = len(results)
                print(f"\nSummary: {success_count}/{total_count} exports successful")
                success = success_count > 0
                
            else:
                # 单个导出模式
                if not args.output:
                    print("Error: --output is required for single export modes")
                    sys.exit(1)
                
                if args.validation:
                    if not os.path.exists(args.validation):
                        print(f"Error: Validation file not found: {args.validation}")
                        sys.exit(1)
                    success = exporter.export_validation_data_csv(args.validation, args.output)
                    task_name = "validation data export"
                elif args.descriptive:
                    if not os.path.exists(args.descriptive):
                        print(f"Error: Descriptive data file not found: {args.descriptive}")
                        sys.exit(1)
                    success = exporter.export_quality_descriptive_csv(args.descriptive, args.output)
                    task_name = "descriptive statistics export"
                elif args.correlation:
                    if not os.path.exists(args.correlation):
                        print(f"Error: Correlation data file not found: {args.correlation}")
                        sys.exit(1)
                    success = exporter.export_correlation_analysis_csv(args.correlation, args.output)
                    task_name = "correlation analysis export"
                elif args.batch:
                    if not os.path.exists(args.batch):
                        print(f"Error: Batch data file not found: {args.batch}")
                        sys.exit(1)
                    success = exporter.export_batch_quality_scores_csv(args.batch, args.output)
                    task_name = "batch quality scores export"
                else:
                    print("Error: Please specify one of --validation, --descriptive, --correlation, --batch, or --auto-dir")
                    sys.exit(1)
                
                if success:
                    print(f"✓ {task_name} completed successfully!")
                    print(f"Output saved to: {args.output}")
                else:
                    print(f"✗ {task_name} failed!")
                    sys.exit(1)
                    
        except Exception as e:
            logger.error(f"Error during CSV export: {e}")
            sys.exit(1)

if __name__ == '__main__':
    main() 