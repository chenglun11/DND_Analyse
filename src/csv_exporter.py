#!/usr/bin/env python3
"""
CSV导出模块 - 导出validation测试和quality测试的数据为CSV格式
"""

import os
import json
import csv
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CSVExporter:
    """CSV导出器"""
    

    def _safe_get_score(self, block):
        """更宽容地从维度块里提取数值"""
        if block is None:
            return None
        if isinstance(block, (int, float)):
            return float(block)
        if isinstance(block, dict):
            # 常见的分数字段
            for k in ["score", "average_score", "avg_score", "mean_score", "performance_score", "value"]:
                v = block.get(k)
                if isinstance(v, (int, float)):
                    return float(v)
            # details 里再找一遍
            det = block.get("details")
            if isinstance(det, dict):
                for k in ["score", "average_score", "avg_score", "mean_score", "performance_score", "value"]:
                    v = det.get(k)
                    if isinstance(v, (int, float)):
                        return float(v)
        return None

    def __init__(self):
        pass
    
    def export_validation_data_csv(self, validation_report_path: str, output_path: str) -> bool:
        """
        导出validation测试数据到CSV
        
        Args:
            validation_report_path: validation报告JSON文件路径
            output_path: 输出CSV文件路径
        
        Returns:
            bool: 导出是否成功
        """
        try:
            # 加载validation报告
            with open(validation_report_path, 'r', encoding='utf-8') as f:
                report = json.load(f)
            
            # 准备CSV数据
            csv_rows = []

            # 定义一个列名映射表，把可能出现的不同命名统一起来
            name_map = {
                'metric_correlation_validation': 'metric_correlation',
                'metric_correlation_score': 'metric_correlation',
                'cross_validation_score': 'cross_validation',
                'inter_rater_reliability_score': 'inter_rater_reliability',
                'sensitivity_analysis_score': 'sensitivity_analysis',
                'statistical_validation_score': 'statistical_validation',
            }
                        
            # 检查报告格式 - 支持两种格式
            if 'detailed_results' in report:
                # 格式1: 标准validation报告格式
                detailed_results = report.get('detailed_results', {})
                
                # 为每个验证类型创建一行数据
                for validation_type, result in detailed_results.items():
                    row = {
                        'validation_type': validation_type,
                        'success': result.get('success', False),
                        'score': result.get('score', 0.0),
                        'timestamp': report.get('validation_summary', {}).get('timestamp', ''),
                    }
                    
                    # 添加详细信息（扁平化处理）
                    details = result.get('details', {})
                    for key, value in details.items():
                        if isinstance(value, (str, int, float, bool)):
                            row[f'detail_{key}'] = value
                        elif isinstance(value, list):
                            # 对于列表类型，计算基本统计信息
                            if value and all(isinstance(x, (int, float)) for x in value):
                                row[f'detail_{key}_count'] = len(value)
                                row[f'detail_{key}_mean'] = np.mean(value)
                                row[f'detail_{key}_std'] = np.std(value)
                                row[f'detail_{key}_min'] = np.min(value)
                                row[f'detail_{key}_max'] = np.max(value)
                            else:
                                row[f'detail_{key}_count'] = len(value)
                    
                    # 添加推荐数量
                    recommendations = result.get('recommendations', [])
                    row['recommendations_count'] = len(recommendations)
                    if recommendations:
                        # 将前3个推荐作为单独列
                        for i, rec in enumerate(recommendations[:3]):
                            row[f'recommendation_{i+1}'] = rec
                    
                    csv_rows.append(row)
                
                # 添加总体汇总信息
                summary = report.get('validation_summary', {})
                summary_row = {
                    'validation_type': 'SUMMARY',
                    'success': True,
                    'score': summary.get('overall_effectiveness_score', 0.0),
                    'timestamp': summary.get('timestamp', ''),
                    'detail_total_validations': summary.get('total_validations', 0),
                    'detail_validations_passed': summary.get('validations_passed', 0),
                    'detail_success_rate': summary.get('success_rate', 0.0),
                    'recommendations_count': len(report.get('recommendations', []))
                }
                csv_rows.append(summary_row)
                
            elif 'algorithm_results' in report or 'summary_stats' in report or ('executive_summary' in report and 'detailed_analysis' in report):
                # ====== 情况 1：标准 validation_summary.json ======
                if 'algorithm_results' in report:
                    algorithm_results = report.get('algorithm_results', {})
                    for algorithm_name, algorithm_data in algorithm_results.items():
                        row = {
                            'algorithm': algorithm_name,
                            'algorithm_overall_score': algorithm_data.get('overall_score'),
                            'algorithm_success_rate': algorithm_data.get('success_rate'),
                        }
                        # 取各维度分数
                        details = algorithm_data.get('details', {})
                        for dim_name, block in details.items():
                            # 统一列名
                            col_name = name_map.get(dim_name, dim_name)
                            if isinstance(block, dict):
                                row[col_name] = block.get('score', 0.0)
                            else:
                                row[col_name] = self._safe_get_score(block)
                        
                        # 确保所有验证维度都有值
                        for dim in ['cross_validation', 'inter_rater_reliability', 'metric_correlation', 'sensitivity_analysis', 'statistical_validation']:
                            if dim not in row:
                                row[dim] = 0.0
                        
                        # 为算法行添加空的汇总列
                        row['summary_algorithms_tested'] = None
                        row['summary_std_score'] = None
                        row['summary_min_score'] = None
                        row['summary_max_score'] = None
                                
                        csv_rows.append(row)
                            # ====== 情况 2：summary.json 格式 ======
                elif 'executive_summary' in report and 'detailed_analysis' in report:
                    eff = report['executive_summary'].get('effectiveness_scores', {})
                    ds = report['detailed_analysis'].get('dataset_comparison', {})
                    vda = report['detailed_analysis'].get('validation_dimension_analysis', {})
                    for algo, info in ds.items():
                        row = {
                            'algorithm': algo,
                            'algorithm_overall_score': info.get('effectiveness_score', eff.get(algo)),
                            'algorithm_success_rate': info.get('success_rate'),
                        }
                        for dim_key in ['cross_validation','inter_rater_reliability','metric_correlation','sensitivity_analysis','statistical_validation']:
                            row[dim_key] = self._safe_get_score(vda.get(dim_key))
                        csv_rows.append(row)
                
                # 添加总体汇总信息 - 使用与算法行一致的结构
                summary_stats = report.get('summary_stats', {})
                if summary_stats:
                    summary_row = {
                        'algorithm': 'OVERALL_SUMMARY',
                        'algorithm_overall_score': summary_stats.get('mean_score', 0.0),
                        'algorithm_success_rate': 1.0,  # 假设整体成功率为100%
                        'cross_validation': None,  # 汇总行不显示具体维度分数
                        'inter_rater_reliability': None,
                        'metric_correlation': None,
                        'sensitivity_analysis': None,
                        'statistical_validation': None,
                        # 额外的汇总统计信息
                        'summary_algorithms_tested': summary_stats.get('algorithms_tested', 0),
                        'summary_std_score': summary_stats.get('std_score', 0.0),
                        'summary_min_score': summary_stats.get('min_score', 0.0),
                        'summary_max_score': summary_stats.get('max_score', 0.0)
                    }
                    csv_rows.append(summary_row)
            
            else:
                # 直接处理单个validation结果（如果是单个文件）
                if 'validation_type' in report:
                    row = {
                        'validation_type': report.get('validation_type', 'unknown'),
                        'success': report.get('success', False),
                        'score': report.get('score', 0.0),
                        'timestamp': ''
                    }
                    
                    # 添加详细信息
                    details = report.get('details', {})
                    for key, value in details.items():
                        if isinstance(value, (str, int, float, bool)):
                            row[f'detail_{key}'] = value
                    
                    recommendations = report.get('recommendations', [])
                    row['recommendations_count'] = len(recommendations)
                    
                    csv_rows.append(row)
            
            # 写入CSV
            if csv_rows:
                df = pd.DataFrame(csv_rows)
                # 确保输出目录存在
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                df.to_csv(output_path, index=False, encoding='utf-8')
                logger.info(f"Validation data exported to {output_path} ({len(csv_rows)} rows)")
                return True
            else:
                logger.error("No validation data found to export")
                return False
                
        except Exception as e:
            logger.error(f"Failed to export validation data to CSV: {e}")
            return False
    
    def export_quality_descriptive_csv(self, input_data: Union[str, Dict[str, Any]], output_path: str) -> bool:
        """
        导出quality测试的描述性分析数据到CSV
        
        Args:
            input_data: 输入数据路径（statistical_analysis_report.json）或数据字典
            output_path: 输出CSV文件路径
        
        Returns:
            bool: 导出是否成功
        """
        try:
            # 加载数据
            if isinstance(input_data, str):
                with open(input_data, 'r', encoding='utf-8') as f:
                    report = json.load(f)
            else:
                report = input_data
            
            # 提取描述性统计数据
            descriptive_stats = report.get('descriptive_statistics', {})
            if not descriptive_stats:
                logger.error("No descriptive statistics found in report")
                return False
            
            # 准备CSV数据
            csv_rows = []
            
            for metric_name, stats in descriptive_stats.items():
                row = {
                    'metric_name': metric_name,
                    'mean': stats.get('mean', 0.0),
                    'std': stats.get('std', 0.0),
                    'min': stats.get('min', 0.0),
                    'max': stats.get('max', 0.0),
                    'median': stats.get('median', 0.0),
                    'q25': stats.get('q25', 0.0),
                    'q75': stats.get('q75', 0.0)
                }
                
                # 添加其他可能的统计信息
                for key, value in stats.items():
                    if key not in row and isinstance(value, (int, float)):
                        row[key] = value
                
                csv_rows.append(row)
            
            # 添加分析汇总信息
            analysis_summary = report.get('analysis_summary', {})
            if analysis_summary:
                summary_row = {
                    'metric_name': 'ANALYSIS_SUMMARY',
                    'mean': 0.0,  # 占位符
                    'std': 0.0,
                    'min': 0.0,
                    'max': 0.0,
                    'median': 0.0,
                    'q25': 0.0,
                    'q75': 0.0
                }
                
                # 添加分析汇总的具体数据
                for key, value in analysis_summary.items():
                    if isinstance(value, (int, float)):
                        summary_row[key] = value
                
                csv_rows.append(summary_row)
            
            # 写入CSV
            if csv_rows:
                df = pd.DataFrame(csv_rows)
                # 确保输出目录存在
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                df.to_csv(output_path, index=False, encoding='utf-8')
                logger.info(f"Quality descriptive data exported to {output_path} ({len(csv_rows)} rows)")
                return True
            else:
                logger.error("No descriptive statistics found to export")
                return False
                
        except Exception as e:
            logger.error(f"Failed to export quality descriptive data to CSV: {e}")
            return False
    
    def export_correlation_analysis_csv(self, statistical_report_path: str, output_path: str) -> bool:
        """
        导出相关性分析数据到CSV
        
        Args:
            statistical_report_path: 统计分析报告JSON文件路径
            output_path: 输出CSV文件路径
        
        Returns:
            bool: 导出是否成功
        """
        try:
            # 加载统计分析报告
            with open(statistical_report_path, 'r', encoding='utf-8') as f:
                report = json.load(f)
            
            correlation_analysis = report.get('correlation_analysis', {})
            if not correlation_analysis:
                logger.error("No correlation analysis found in report")
                return False
            
            # 准备CSV数据
            csv_rows = []
            
            # 导出强相关关系
            strong_correlations = correlation_analysis.get('strong_correlations', [])
            for corr in strong_correlations:
                row = {
                    'correlation_type': 'strong',
                    'metric1': corr.get('metric1', ''),
                    'metric2': corr.get('metric2', ''),
                    'pearson_correlation': corr.get('pearson_correlation', 0.0),
                    'spearman_correlation': corr.get('spearman_correlation', 0.0)
                }
                csv_rows.append(row)
            
            # 导出中等相关关系
            moderate_correlations = correlation_analysis.get('moderate_correlations', [])
            for corr in moderate_correlations:
                row = {
                    'correlation_type': 'moderate',
                    'metric1': corr.get('metric1', ''),
                    'metric2': corr.get('metric2', ''),
                    'pearson_correlation': corr.get('pearson_correlation', 0.0),
                    'spearman_correlation': corr.get('spearman_correlation', 0.0)
                }
                csv_rows.append(row)
            
            # 导出与总分的相关性
            overall_correlations = correlation_analysis.get('overall_score_correlations', [])
            for corr in overall_correlations:
                row = {
                    'correlation_type': 'with_overall_score',
                    'metric1': corr.get('metric', ''),
                    'metric2': 'overall_score',
                    'pearson_correlation': corr.get('pearson_correlation', 0.0),
                    'spearman_correlation': corr.get('spearman_correlation', 0.0),
                    'pearson_p_value': corr.get('pearson_p_value', 1.0),
                    'spearman_p_value': corr.get('spearman_p_value', 1.0)
                }
                csv_rows.append(row)
            
            # 写入CSV
            if csv_rows:
                df = pd.DataFrame(csv_rows)
                # 确保输出目录存在
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                df.to_csv(output_path, index=False, encoding='utf-8')
                logger.info(f"Correlation analysis data exported to {output_path} ({len(csv_rows)} rows)")
                return True
            else:
                logger.error("No correlation data found to export")
                return False
                
        except Exception as e:
            logger.error(f"Failed to export correlation analysis to CSV: {e}")
            return False
    
    def export_batch_quality_scores_csv(self, batch_report_path: str, output_path: str) -> bool:
        """
        导出批量质量评估的所有分数到CSV
        
        Args:
            batch_report_path: 批量评估报告JSON文件路径
            output_path: 输出CSV文件路径
        
        Returns:
            bool: 导出是否成功
        """
        try:
            # 加载批量评估报告
            with open(batch_report_path, 'r', encoding='utf-8') as f:
                report = json.load(f)
            
            # 支持两种格式：有detailed_results键的和没有的
            if 'detailed_results' in report:
                detailed_results = report['detailed_results']
            else:
                # 直接使用整个report作为detailed_results
                detailed_results = {k: v for k, v in report.items() 
                                  if isinstance(v, dict) and 'overall_score' in v}
            
            if not detailed_results:
                logger.error("No detailed results found in batch report")
                return False
            
            # 准备CSV数据
            csv_rows = []
            
            # 定义要提取的指标
            metrics = [
                'accessibility', 'degree_variance', 'door_distribution', 'dead_end_ratio',
                'key_path_length', 'loop_ratio', 'path_diversity', 'treasure_monster_distribution', 
                'geometric_balance'
            ]
            
            for map_name, result in detailed_results.items():
                if result.get('status') != 'success':
                    continue
                    
                row = {
                    'map_name': map_name,
                    'overall_score': result.get('overall_score', 0.0),
                    'status': result.get('status', 'unknown'),
                    'processing_time': result.get('processing_time', 0.0)
                }
                
                # 提取各项指标分数
                detailed_metrics = result.get('detailed_metrics', {})
                for metric in metrics:
                    if metric in detailed_metrics:
                        metric_result = detailed_metrics[metric]
                        if isinstance(metric_result, dict):
                            score = metric_result.get('score', 0.0)
                        else:
                            score = float(metric_result)
                        row[metric] = score
                    else:
                        row[metric] = 0.0
                
                # 提取类别分数
                category_scores = result.get('category_scores', {})
                for category, score in category_scores.items():
                    row[f'{category}_score'] = score
                
                csv_rows.append(row)
            
            # 写入CSV
            if csv_rows:
                df = pd.DataFrame(csv_rows)
                # 确保输出目录存在
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                df.to_csv(output_path, index=False, encoding='utf-8')
                logger.info(f"Batch quality scores exported to {output_path} ({len(csv_rows)} rows)")
                return True
            else:
                logger.error("No valid quality scores found to export")
                return False
                
        except Exception as e:
            logger.error(f"Failed to export batch quality scores to CSV: {e}")
            return False
    
    def export_all_from_directories(self, input_dir: str, output_dir: str = "output/csv_exports") -> Dict[str, bool]:
        """
        从指定目录自动导出所有可能的CSV数据
        
        Args:
            input_dir: 输入目录路径
            output_dir: 输出目录路径
        
        Returns:
            Dict[str, bool]: 各个导出任务的成功状态
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        results = {}
        
        # 查找validation报告 - 支持多种命名模式
        validation_patterns = [
            "**/validation_report*.json",
            "**/validation_*.json", 
            "**/validation*.json"
        ]
        validation_files = []
        for pattern in validation_patterns:
            validation_files.extend(input_path.glob(pattern))
        
        # 去重
        validation_files = list(set(validation_files))
        
        for file in validation_files:
            output_file = output_path / f"validation_data_{file.stem}.csv"
            results[f'validation_{file.name}'] = self.export_validation_data_csv(str(file), str(output_file))
        
        # 查找统计分析报告
        stat_files = list(input_path.glob("**/statistical_analysis_report*.json"))
        for file in stat_files:
            # 导出描述性统计
            desc_output = output_path / f"descriptive_stats_{file.stem}.csv"
            results[f'descriptive_{file.name}'] = self.export_quality_descriptive_csv(str(file), str(desc_output))
            
            # 导出相关性分析
            corr_output = output_path / f"correlation_analysis_{file.stem}.csv"
            results[f'correlation_{file.name}'] = self.export_correlation_analysis_csv(str(file), str(corr_output))
        
        # 查找批量评估报告
        batch_files = list(input_path.glob("**/*batch_report*.json"))
        for file in batch_files:
            output_file = output_path / f"batch_quality_scores_{file.stem}.csv"
            results[f'batch_scores_{file.name}'] = self.export_batch_quality_scores_csv(str(file), str(output_file))
        
        return results


def main():
    """主函数 - 提供命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='CSV Exporter - Export validation and quality test data to CSV format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export validation data
  python csv_exporter.py --validation output/validation_report.json --output validation_data.csv
  
  # Export quality descriptive statistics
  python csv_exporter.py --descriptive output/statistical_analysis_report.json --output descriptive_stats.csv
  
  # Export correlation analysis
  python csv_exporter.py --correlation output/statistical_analysis_report.json --output correlation_data.csv
  
  # Export batch quality scores
  python csv_exporter.py --batch output/batch_report.json --output batch_scores.csv
  
  # Auto-export all from directory
  python csv_exporter.py --auto-dir output/ --output-dir csv_exports/
        """
    )
    
    parser.add_argument('--validation', help='Path to validation report JSON file')
    parser.add_argument('--descriptive', help='Path to statistical analysis report JSON file (for descriptive stats)')
    parser.add_argument('--correlation', help='Path to statistical analysis report JSON file (for correlation analysis)')
    parser.add_argument('--batch', help='Path to batch assessment report JSON file')
    parser.add_argument('--auto-dir', help='Auto-export all data from input directory')
    
    parser.add_argument('--output', '-o', help='Output CSV file path (for single exports)')
    parser.add_argument('--output-dir', help='Output directory path (for auto export)')
    
    args = parser.parse_args()
    
    exporter = CSVExporter()
    success = False
    
    if args.auto_dir:
        # 自动导出模式
        output_dir = args.output_dir or "output/csv_exports"
        results = exporter.export_all_from_directories(args.auto_dir, output_dir)
        
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
            return 1
        
        if args.validation:
            success = exporter.export_validation_data_csv(args.validation, args.output)
            task_name = "validation data export"
        elif args.descriptive:
            success = exporter.export_quality_descriptive_csv(args.descriptive, args.output)
            task_name = "descriptive statistics export"
        elif args.correlation:
            success = exporter.export_correlation_analysis_csv(args.correlation, args.output)
            task_name = "correlation analysis export"
        elif args.batch:
            success = exporter.export_batch_quality_scores_csv(args.batch, args.output)
            task_name = "batch quality scores export"
        else:
            print("Error: Please specify one of --validation, --descriptive, --correlation, --batch, or --auto-dir")
            return 1
        
        if success:
            print(f"✓ {task_name} completed successfully!")
            print(f"Output saved to: {args.output}")
        else:
            print(f"✗ {task_name} failed!")
    
    return 0 if success else 1



if __name__ == '__main__':
    import sys
    sys.exit(main())