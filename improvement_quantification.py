#!/usr/bin/env python3
"""
改进效果量化评估系统
提供多种量化指标来评估地牢生成方法的改进效果
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy import stats
from dataclasses import dataclass

# 添加src目录到Python路径
sys.path.append('src')
from quality_assessor import DungeonQualityAssessor
from benchmark_standards import DungeonBenchmarkStandards

@dataclass
class ImprovementMetrics:
    """改进效果指标"""
    metric_name: str
    before_mean: float
    after_mean: float
    improvement_pct: float
    effect_size: float  # Cohen's d
    t_statistic: float
    p_value: float
    significance: bool
    benchmark_grade_before: str
    benchmark_grade_after: str
    grade_improvement: bool

class ImprovementQuantifier:
    """改进效果量化器"""
    
    def __init__(self):
        self.assessor = DungeonQualityAssessor()
        self.standards = DungeonBenchmarkStandards()
        
    def quantify_improvement(self, before_dir: str, after_dir: str) -> Dict:
        """量化改进效果"""
        print("🔍 开始量化改进效果...")
        
        # 收集数据
        before_data = self._collect_data(before_dir, "改进前")
        after_data = self._collect_data(after_dir, "改进后")
        
        if before_data.empty or after_data.empty:
            return {"error": "数据不足，无法进行量化分析"}
        
        # 计算各项改进指标
        improvement_metrics = self._calculate_improvement_metrics(before_data, after_data)
        
        # 计算综合改进分数
        overall_improvement = self._calculate_overall_improvement(improvement_metrics)
        
        # 生成改进报告
        improvement_report = self._generate_improvement_report(
            improvement_metrics, overall_improvement, before_data, after_data
        )
        
        return improvement_report
    
    def _collect_data(self, data_dir: str, label: str) -> pd.DataFrame:
        """收集评估数据"""
        records = []
        
        if not os.path.exists(data_dir):
            print(f"警告: 目录 {data_dir} 不存在")
            return pd.DataFrame()
        
        json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
        
        for fname in json_files:
            try:
                path = os.path.join(data_dir, fname)
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                result = self.assessor.assess_quality(data)
                
                row = {
                    'file': fname,
                    'label': label,
                    'overall_score': result['overall_score'],
                    'grade': result['grade']
                }
                
                # 添加各项指标分数
                for rule, score in result['scores'].items():
                    row[rule] = score
                
                records.append(row)
                
            except Exception as e:
                print(f"处理文件 {fname} 时出错: {e}")
        
        return pd.DataFrame(records)
    
    def _calculate_improvement_metrics(self, before_data: pd.DataFrame, 
                                     after_data: pd.DataFrame) -> List[ImprovementMetrics]:
        """计算改进指标"""
        metrics = ['accessibility', 'dead_end_ratio', 'degree_variance', 
                  'door_distribution', 'key_path_length', 'loop_ratio', 'path_diversity']
        
        improvement_metrics = []
        
        for metric in metrics:
            before_scores = before_data[metric].dropna()
            after_scores = after_data[metric].dropna()
            
            if len(before_scores) > 0 and len(after_scores) > 0:
                # 基本统计
                before_mean = before_scores.mean()
                after_mean = after_scores.mean()
                improvement_pct = ((after_mean - before_mean) / before_mean * 100) if before_mean > 0 else 0
                
                # 效应量 (Cohen's d)
                pooled_std = np.sqrt(((len(before_scores) - 1) * before_scores.var() + 
                                    (len(after_scores) - 1) * after_scores.var()) / 
                                   (len(before_scores) + len(after_scores) - 2))
                effect_size = (after_mean - before_mean) / pooled_std if pooled_std > 0 else 0
                
                # 统计显著性检验
                if len(before_scores) > 1 and len(after_scores) > 1:
                    t_stat, p_value = stats.ttest_ind(before_scores, after_scores)
                    significance = p_value < 0.05
                else:
                    t_stat, p_value, significance = 0, 1, False
                
                # 基准等级评估
                benchmark_before = self.standards.evaluate_against_benchmark(before_mean, metric)
                benchmark_after = self.standards.evaluate_against_benchmark(after_mean, metric)
                grade_improvement = benchmark_after[1] > benchmark_before[1]
                
                improvement_metrics.append(ImprovementMetrics(
                    metric_name=metric,
                    before_mean=before_mean,
                    after_mean=after_mean,
                    improvement_pct=improvement_pct,
                    effect_size=effect_size,
                    t_statistic=t_stat,
                    p_value=p_value,
                    significance=significance,
                    benchmark_grade_before=benchmark_before[0],
                    benchmark_grade_after=benchmark_after[0],
                    grade_improvement=grade_improvement
                ))
        
        return improvement_metrics
    
    def _calculate_overall_improvement(self, improvement_metrics: List[ImprovementMetrics]) -> Dict:
        """计算综合改进分数"""
        if not improvement_metrics:
            return {"overall_score": 0.0, "grade": "no_improvement"}
        
        # 计算加权改进分数
        total_weighted_score = 0.0
        total_weight = 0.0
        significant_improvements = 0
        grade_improvements = 0
        
        # 指标权重 (基于重要性)
        metric_weights = {
            'accessibility': 0.25,
            'path_diversity': 0.20,
            'dead_end_ratio': 0.15,
            'loop_ratio': 0.15,
            'degree_variance': 0.10,
            'door_distribution': 0.10,
            'key_path_length': 0.05
        }
        
        for metric in improvement_metrics:
            weight = metric_weights.get(metric.metric_name, 0.1)
            
            # 改进分数 (基于效应量和显著性)
            improvement_score = 0.0
            if metric.significance:
                significant_improvements += 1
                if abs(metric.effect_size) >= 0.8:
                    improvement_score = 1.0  # 大效应
                elif abs(metric.effect_size) >= 0.5:
                    improvement_score = 0.8  # 中等效应
                elif abs(metric.effect_size) >= 0.2:
                    improvement_score = 0.6  # 小效应
                else:
                    improvement_score = 0.4  # 微小效应
            else:
                improvement_score = 0.2  # 无显著改进
            
            # 如果改进百分比为正，给予额外奖励
            if metric.improvement_pct > 0:
                improvement_score *= 1.2
            
            if metric.grade_improvement:
                grade_improvements += 1
                improvement_score *= 1.1
            
            total_weighted_score += improvement_score * weight
            total_weight += weight
        
        overall_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
        
        # 确定总体改进等级
        if overall_score >= 0.8:
            grade = "excellent_improvement"
        elif overall_score >= 0.6:
            grade = "good_improvement"
        elif overall_score >= 0.4:
            grade = "moderate_improvement"
        elif overall_score >= 0.2:
            grade = "minimal_improvement"
        else:
            grade = "no_improvement"
        
        return {
            "overall_score": overall_score,
            "grade": grade,
            "significant_improvements": significant_improvements,
            "total_metrics": len(improvement_metrics),
            "grade_improvements": grade_improvements,
            "improvement_rate": significant_improvements / len(improvement_metrics) if improvement_metrics else 0
        }
    
    def _generate_improvement_report(self, improvement_metrics: List[ImprovementMetrics],
                                   overall_improvement: Dict,
                                   before_data: pd.DataFrame,
                                   after_data: pd.DataFrame) -> Dict:
        """生成改进报告"""
        
        # 计算总体统计
        before_overall_mean = before_data['overall_score'].mean()
        after_overall_mean = after_data['overall_score'].mean()
        overall_improvement_pct = ((after_overall_mean - before_overall_mean) / before_overall_mean * 100) if before_overall_mean > 0 else 0
        
        # 生成详细报告
        detailed_metrics = []
        for metric in improvement_metrics:
            detailed_metrics.append({
                "metric": metric.metric_name,
                "before_mean": round(metric.before_mean, 3),
                "after_mean": round(metric.after_mean, 3),
                "improvement_pct": round(metric.improvement_pct, 1),
                "effect_size": round(metric.effect_size, 3),
                "p_value": round(metric.p_value, 3),
                "significant": metric.significance,
                "benchmark_before": metric.benchmark_grade_before,
                "benchmark_after": metric.benchmark_grade_after,
                "grade_improvement": metric.grade_improvement
            })
        
        # 改进效果分类
        improvements_by_category = {
            "major_improvements": [m for m in improvement_metrics if m.improvement_pct > 20 and m.significance],
            "moderate_improvements": [m for m in improvement_metrics if 5 <= m.improvement_pct <= 20 and m.significance],
            "minor_improvements": [m for m in improvement_metrics if 0 < m.improvement_pct < 5 and m.significance],
            "no_change": [m for m in improvement_metrics if abs(m.improvement_pct) < 1],
            "regressions": [m for m in improvement_metrics if m.improvement_pct < -1]
        }
        
        return {
            "summary": {
                "overall_improvement_score": round(overall_improvement["overall_score"], 3),
                "overall_grade": overall_improvement["grade"],
                "overall_improvement_pct": round(overall_improvement_pct, 1),
                "significant_improvements": overall_improvement["significant_improvements"],
                "total_metrics": overall_improvement["total_metrics"],
                "improvement_rate": round(overall_improvement["improvement_rate"] * 100, 1),
                "grade_improvements": overall_improvement["grade_improvements"]
            },
            "detailed_metrics": detailed_metrics,
            "improvements_by_category": {
                category: len(metrics) for category, metrics in improvements_by_category.items()
            },
            "sample_sizes": {
                "before": len(before_data),
                "after": len(after_data)
            }
        }
    
    def print_improvement_report(self, report: Dict):
        """打印改进报告"""
        print("\n" + "="*80)
        print("🏆 改进效果量化评估报告")
        print("="*80)
        
        summary = report["summary"]
        print(f"\n📊 总体改进效果:")
        print(f"  综合改进分数: {summary['overall_improvement_score']:.3f}")
        print(f"  改进等级: {summary['overall_grade']}")
        print(f"  总体改进百分比: {summary['overall_improvement_pct']:+.1f}%")
        print(f"  显著改进指标: {summary['significant_improvements']}/{summary['total_metrics']}")
        print(f"  改进成功率: {summary['improvement_rate']}%")
        print(f"  等级提升指标: {summary['grade_improvements']}")
        
        print(f"\n📈 详细指标改进:")
        for metric in report["detailed_metrics"]:
            direction = "↗️" if metric["improvement_pct"] > 0 else "↘️"
            significance = "✅" if metric["significant"] else "❌"
            grade_improvement = "⭐" if metric["grade_improvement"] else ""
            
            print(f"  {metric['metric']}: {metric['before_mean']:.3f} → {metric['after_mean']:.3f} "
                  f"({metric['improvement_pct']:+.1f}%) {direction} {significance} {grade_improvement}")
        
        print(f"\n📋 改进分类统计:")
        for category, count in report["improvements_by_category"].items():
            if count > 0:
                print(f"  {category}: {count} 个指标")
        
        print(f"\n📊 样本信息:")
        print(f"  改进前样本: {report['sample_sizes']['before']} 个地牢")
        print(f"  改进后样本: {report['sample_sizes']['after']} 个地牢")
        
        print("="*80)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='改进效果量化评估')
    parser.add_argument('--before', required=True, help='改进前目录')
    parser.add_argument('--after', required=True, help='改进后目录')
    parser.add_argument('--output', help='输出报告文件')
    
    args = parser.parse_args()
    
    quantifier = ImprovementQuantifier()
    report = quantifier.quantify_improvement(args.before, args.after)
    
    if "error" in report:
        print(f"错误: {report['error']}")
        return
    
    # 打印报告
    quantifier.print_improvement_report(report)
    
    # 保存报告
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n✓ 报告已保存到: {args.output}")

if __name__ == '__main__':
    main() 