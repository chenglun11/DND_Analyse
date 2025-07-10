#!/usr/bin/env python3
"""
批量质量评估脚本
为所有转换后的地牢地图文件生成质量评估报告
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

from .quality_assessor import DungeonQualityAssessor

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def assess_all_maps(input_dir: str = "output", output_dir: str = "output/reports") -> Dict[str, Any]:
    """评估目录中所有统一格式的地牢地图文件"""
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 查找所有统一格式的JSON文件
    json_files = list(input_path.glob("*.json"))
    
    # 过滤掉报告文件
    json_files = [f for f in json_files if not f.name.startswith("quality_report") and not f.name.startswith("report")]
    
    logger.info(f"找到 {len(json_files)} 个地图文件进行评估")
    
    results = {}
    assessor = DungeonQualityAssessor()
    
    for json_file in json_files:
        try:
            logger.info(f"评估文件: {json_file.name}")
            
            # 读取地图数据
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 评估质量
            metrics = assessor.assess_quality(data)
            
            # 保存单独的报告
            report_file = output_path / f"quality_report_{json_file.stem}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, ensure_ascii=False, indent=2)
            
            # 收集结果
            results[json_file.name] = {
                'overall_score': metrics['overall_score'],
                'grade': metrics['grade'],
                'detailed_metrics': metrics['scores'],
                'recommendations': metrics['recommendations']
            }
            
            logger.info(f"✓ {json_file.name}: {metrics['overall_score']:.3f} ({metrics['grade']})")
            
        except Exception as e:
            logger.error(f"评估 {json_file.name} 时出错: {e}")
            results[json_file.name] = {
                'error': str(e),
                'overall_score': 0.0,
                'grade': '错误'
            }
    
    # 生成汇总报告
    summary_report = generate_summary_report(results)
    
    # 保存汇总报告
    summary_file = output_path / "quality_summary_report.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary_report, f, ensure_ascii=False, indent=2)
    
    # 打印汇总报告
    print_summary_report(summary_report)
    
    return results

def generate_summary_report(results: Dict[str, Any]) -> Dict[str, Any]:
    """生成汇总报告"""
    
    valid_results = {k: v for k, v in results.items() if 'error' not in v}
    
    if not valid_results:
        return {
            'summary': '没有有效的评估结果',
            'total_files': len(results),
            'valid_files': 0,
            'error_files': len(results)
        }
    
    # 计算统计信息
    scores = [r['overall_score'] for r in valid_results.values()]
    avg_score = sum(scores) / len(scores)
    max_score = max(scores)
    min_score = min(scores)
    
    # 按等级分类
    grade_counts = {}
    for result in valid_results.values():
        grade = result['grade']
        grade_counts[grade] = grade_counts.get(grade, 0) + 1
    
    # 找出最佳和最差的地图
    best_map = max(valid_results.items(), key=lambda x: x[1]['overall_score'])
    worst_map = min(valid_results.items(), key=lambda x: x[1]['overall_score'])
    
    # 计算各指标的统计
    metric_stats = {}
    metrics = ['accessibility', 'degree_variance', 'path_diversity', 
               'loop_ratio', 'door_distribution']
    
    for metric in metrics:
        values = []
        for r in valid_results.values():
            metric_result = r['detailed_metrics'].get(metric, {})
            if isinstance(metric_result, dict):
                score = metric_result.get('score', 0.0)
            else:
                score = metric_result
            values.append(score)
        metric_stats[metric] = {
            'average': sum(values) / len(values),
            'max': max(values),
            'min': min(values)
        }
    
    return {
        'summary': {
            'total_files': len(results),
            'valid_files': len(valid_results),
            'error_files': len(results) - len(valid_results),
            'average_score': avg_score,
            'max_score': max_score,
            'min_score': min_score,
            'best_map': {
                'name': best_map[0],
                'score': best_map[1]['overall_score'],
                'grade': best_map[1]['grade']
            },
            'worst_map': {
                'name': worst_map[0],
                'score': worst_map[1]['overall_score'],
                'grade': worst_map[1]['grade']
            }
        },
        'grade_distribution': grade_counts,
        'metric_statistics': metric_stats,
        'detailed_results': valid_results
    }

def print_summary_report(report: Dict[str, Any]) -> None:
    """打印汇总报告到控制台"""
    
    print("\n" + "="*60)
    print("地牢地图质量评估汇总报告")
    print("="*60)
    
    summary = report['summary']
    print(f"\n📊 总体统计:")
    print(f"  总文件数: {summary['total_files']}")
    print(f"  有效文件: {summary['valid_files']}")
    print(f"  错误文件: {summary['error_files']}")
    print(f"  平均评分: {summary['average_score']:.3f}")
    print(f"  最高评分: {summary['max_score']:.3f}")
    print(f"  最低评分: {summary['min_score']:.3f}")
    
    print(f"\n🏆 最佳地图:")
    best = summary['best_map']
    print(f"  {best['name']}: {best['score']:.3f} ({best['grade']})")
    
    print(f"\n⚠️  最差地图:")
    worst = summary['worst_map']
    print(f"  {worst['name']}: {worst['score']:.3f} ({worst['grade']})")
    
    print(f"\n📈 等级分布:")
    for grade, count in report['grade_distribution'].items():
        print(f"  {grade}: {count} 个")
    
    print(f"\n📋 指标统计:")
    for metric, stats in report['metric_statistics'].items():
        metric_name = {
            'accessibility': '可达性',
            'degree_variance': '度差',
            'path_diversity': '路径多样性',
            'loop_ratio': '回环率',
            'door_distribution': '门分布'
        }.get(metric, metric)
        print(f"  {metric_name}: 平均 {stats['average']:.3f}, 最高 {stats['max']:.3f}, 最低 {stats['min']:.3f}")
    
    print("="*60)

def batch_assess_quality(input_dir: str, output_file: str, enable_spatial_inference: bool = True, adjacency_threshold: float = 1.0):
    """批量评估地图质量 - CLI 调用的接口函数"""
    try:
        results = assess_all_maps(input_dir, os.path.dirname(output_file))
        
        # 保存到指定的输出文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"批量评估报告已保存到: {output_file}")
        return results
        
    except Exception as e:
        logger.error(f"批量评估失败: {e}")
        raise

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='批量评估地牢地图质量')
    parser.add_argument('--input', default='output', help='输入目录路径')
    parser.add_argument('--output', default='output/reports', help='输出目录路径')
    
    args = parser.parse_args()
    
    logger.info("开始批量质量评估...")
    results = assess_all_maps(args.input, args.output)
    logger.info("批量质量评估完成!")

if __name__ == '__main__':
    main() 