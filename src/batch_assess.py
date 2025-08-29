#!/usr/bin/env python3
"""
Batch Quality Assessment Script
Generates quality assessment reports for all converted dungeon map files
"""

import os
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import signal
import pandas as pd
import numpy as np
from scipy import stats

from .quality_assessor import DungeonQualityAssessor

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("操作超时")

def assess_all_maps(input_dir: str = "output", output_dir: str = "output/reports", timeout_per_file: int = 30) -> Dict[str, Any]:
    """评估目录中所有统一格式的地牢地图文件"""
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 递归查找所有统一格式的JSON文件
    json_files = list(input_path.rglob("*.json"))
    
    # 过滤掉报告文件
    json_files = [f for f in json_files if not f.name.startswith("quality_report") and not f.name.startswith("report")]
    
    logger.info(f"{len(json_files)} map files have been located.")
    
    results = {}
    assessor = DungeonQualityAssessor()
    
    for i, json_file in enumerate(json_files, 1):
        try:
            # 计算相对路径以保持目录结构
            relative_path = json_file.relative_to(input_path)
            logger.info(f"Assessment [{i}/{len(json_files)}]: {relative_path}")
            
            # 设置超时
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_per_file)
            
            try:
                # 读取地图数据
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 评估质量
                start_time = time.time()
                metrics = assessor.assess_quality(data)
                end_time = time.time()
                
                # 取消超时
                signal.alarm(0)
                
                # 保存单独的报告，保持目录结构
                report_relative_path = relative_path.with_stem(f"quality_report_{relative_path.stem}")
                report_file = output_path / report_relative_path
                # 确保报告文件的目录存在
                report_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(report_file, 'w', encoding='utf-8') as f:
                    json.dump(metrics, f, ensure_ascii=False, indent=2)
                
                # 收集结果，使用相对路径作为key
                results[str(relative_path)] = {
                    'overall_score': metrics['overall_score'],
                    'grade': metrics['grade'],
                    'detailed_metrics': metrics['scores'],
                    # 'category_scores': metrics['category_scores'],
                    'recommendations': metrics['recommendations'],
                    'processing_time': end_time - start_time,
                    'status': 'success'
                }
                
                logger.info(f"✓ {relative_path}: {metrics['overall_score']:.3f} ({metrics['grade']}) - {end_time - start_time:.2f}s")
                
            except TimeoutError:
                signal.alarm(0)
                logger.error(f"Assess {relative_path} timeout")
                results[str(relative_path)] = {
                    'error': 'timeout',
                    'overall_score': 0.0,
                    'grade': 'timeout',
                    'status': 'timeout'
                }
            except Exception as e:
                signal.alarm(0)
                logger.error(f"Assess {relative_path} error: {e}")
                results[str(relative_path)] = {
                    'error': str(e),
                    'overall_score': 0.0,
                    'grade': 'error',
                    'status': 'error'
                }
                
        except Exception as e:
            logger.error(f"Assess {json_file} unexepcted error: {e}")
            relative_path = json_file.relative_to(input_path)
            results[str(relative_path)] = {
                'error': f'unexpected error: {str(e)}',
                'overall_score': 0.0,
                'grade': 'unexpected error',
                'status': 'error'
            }
    
    # 生成汇总报告
    try:
        summary_report = generate_summary_report(results)
        
        # 保存汇总报告
        summary_file = output_path / "quality_summary_report.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_report, f, ensure_ascii=False, indent=2)
        
        # 不打印到控制台，只记录到日志
        logger.info("Batch assessment completed; summary report generated.")
        
    except Exception as e:
        logger.error(f"An error occurred while generating the summary report.: {e}")
        # 即使汇总报告失败，也返回已处理的结果
        results['_summary_error'] = str(e)
    
    return results

def generate_summary_report(results: Dict[str, Any]) -> Dict[str, Any]:
    """生成汇总报告"""
    
    # 过滤掉错误标记
    valid_results = {k: v for k, v in results.items() if 'error' not in v and not k.startswith('_')}
    
    if not valid_results:
        return {
            'summary': 'no valid reports',
            'total_files': len(results),
            'valid_files': 0,
            'error_files': len(results)
        }
    
    try:
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
                   'loop_ratio', 'door_distribution', 'treasure_monster_distribution', 'geometric_balance']
        
        for metric in metrics:
            values = []
            for r in valid_results.values():
                metric_result = r['detailed_metrics'].get(metric, {})
                if isinstance(metric_result, dict):
                    score = metric_result.get('score', 0.0)
                else:
                    score = metric_result
                values.append(score)
            
            if values:  # 确保有有效值
                metric_stats[metric] = {
                    'average': sum(values) / len(values),
                    'max': max(values),
                    'min': min(values)
                }
        
        # 计算类别评分统计
        category_stats = {}
        categories = ['structural', 'gameplay', 'aesthetic']
        
        for category in categories:
            values = []
            for r in valid_results.values():
                category_scores = r.get('category_scores', {})
                score = category_scores.get(category, 0.0)
                values.append(score)
            
            if values:  # 确保有有效值
                category_stats[category] = {
                    'average': sum(values) / len(values),
                    'max': max(values),
                    'min': min(values)
                }
        
        # 添加统计学分析
        statistical_analysis = generate_statistical_analysis(valid_results)
        
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
            'category_statistics': category_stats,
            'statistical_analysis': statistical_analysis,
            'detailed_results': valid_results
        }
        
    except Exception as e:
        logger.error(f"An error occurred while generating the summary report.: {e}")
        return {
            'summary': f'Failure to generate summary report: {str(e)}',
            'total_files': len(results),
            'valid_files': len(valid_results),
            'error_files': len(results) - len(valid_results)
        }

def generate_statistical_analysis(valid_results: Dict[str, Any]) -> Dict[str, Any]:
    """生成统计学分析"""
    try:
        # 构建DataFrame
        data_rows = []
        for map_name, result in valid_results.items():
            # 检查result类型
            if not isinstance(result, dict):
                logger.warning(f"Skipping {map_name}: result is not a dict, got {type(result)}")
                continue
                
            if 'overall_score' not in result:
                logger.warning(f"Skipping {map_name}: missing overall_score")
                continue
                
            row = {'map_name': map_name, 'overall_score': result['overall_score']}
            
            # 添加详细指标
            detailed_metrics = result.get('detailed_metrics', {})
            if detailed_metrics:
                for metric_name, metric_data in detailed_metrics.items():
                    if isinstance(metric_data, dict):
                        score = metric_data.get('score', 0.0)
                    else:
                        score = float(metric_data) if metric_data else 0.0
                    row[metric_name] = score
            
            # 添加类别分数
            category_scores = result.get('category_scores', {})
            if category_scores:
                for category, score in category_scores.items():
                    row[f'{category}_score'] = score
            
            data_rows.append(row)
        
        if not data_rows:
            return {'error': 'No valid data for analysis'}
        
        df = pd.DataFrame(data_rows)
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # 描述性统计
        descriptive_stats = {}
        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) > 0:
                descriptive_stats[col] = {
                    'count': int(len(series)),
                    'mean': float(series.mean()),
                    'std': float(series.std()),
                    'min': float(series.min()),
                    'max': float(series.max()),
                    'median': float(series.median()),
                    'q25': float(series.quantile(0.25)),
                    'q75': float(series.quantile(0.75)),
                    'skewness': float(series.skew()),
                    'kurtosis': float(series.kurtosis())
                }
        
        # Spearman相关性分析
        correlation_analysis = {}
        if len(numeric_cols) > 1:
            # 移除总分以单独分析
            analysis_cols = [col for col in numeric_cols if col != 'overall_score']
            if len(analysis_cols) > 1:
                # 计算Spearman相关系数
                corr_matrix = df[analysis_cols].corr(method='spearman')
                
                # 提取强相关关系（基于Spearman）
                strong_correlations = []
                moderate_correlations = []
                
                for i, col1 in enumerate(analysis_cols):
                    for j, col2 in enumerate(analysis_cols[i+1:], i+1):
                        spearman_val = corr_matrix.iloc[i, j]
                        
                        # 计算p值
                        try:
                            rho, p_val = stats.spearmanr(df[col1].dropna(), df[col2].dropna())
                        except:
                            p_val = None
                        
                        if abs(spearman_val) >= 0.7:
                            strong_correlations.append({
                                'metric1': col1,
                                'metric2': col2,
                                'spearman_correlation': float(spearman_val),
                                'p_value': float(p_val) if p_val else None
                            })
                        elif abs(spearman_val) >= 0.4:
                            moderate_correlations.append({
                                'metric1': col1,
                                'metric2': col2,
                                'spearman_correlation': float(spearman_val),
                                'p_value': float(p_val) if p_val else None
                            })
                
                # 转换相关性矩阵为纯Python类型
                correlation_matrix_dict = {}
                for col in corr_matrix.columns:
                    correlation_matrix_dict[col] = {k: float(v) for k, v in corr_matrix[col].to_dict().items()}
                
                correlation_analysis = {
                    'correlation_matrix': correlation_matrix_dict,
                    'strong_correlations': strong_correlations,
                    'moderate_correlations': moderate_correlations
                }
                
                # 与总分的相关性
                if 'overall_score' in df.columns:
                    overall_correlations = []
                    for col in analysis_cols:
                        try:
                            rho, p_val = stats.spearmanr(df[col].dropna(), df['overall_score'].dropna())
                            overall_correlations.append({
                                'metric': col,
                                'spearman_correlation': float(rho),
                                'p_value': float(p_val)
                            })
                        except:
                            continue
                    correlation_analysis['overall_score_correlations'] = overall_correlations
        
        # 正态性检验
        normality_tests = {}
        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) >= 8:  # Shapiro-Wilk需要至少8个样本
                try:
                    stat, p_val = stats.shapiro(series)
                    normality_tests[col] = {
                        'shapiro_wilk_statistic': float(stat),
                        'p_value': float(p_val),
                        'is_normal': bool(p_val > 0.05)
                    }
                except:
                    pass
        
        return {
            'sample_size': len(df),
            'metrics_analyzed': len(numeric_cols),
            'descriptive_statistics': descriptive_stats,
            'correlation_analysis': correlation_analysis,
            'normality_tests': normality_tests,
            'analysis_timestamp': pd.Timestamp.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Statistical analysis failed: {e}")
        return {'error': f'Statistical analysis failed: {str(e)}'}

def batch_assess_quality(input_dir: str, output_dir: str, enable_spatial_inference: bool = True, adjacency_threshold: float = 1.0, timeout_per_file: int = 30) -> Dict[str, Any]:
    """批量评估地图质量 - API 调用的接口函数（支持递归搜索子文件夹）"""
    try:
        logger.info(f"Commencing batch evaluation, input directory: {input_dir}")
        logger.info(f"Output directory: {output_dir}")
        logger.info(f"Timeout period for each file: {timeout_per_file}s")
        logger.info(f"Spatial Engine: {'Enable' if enable_spatial_inference else 'None'}")
        logger.info(f"Adjacency threshold: {adjacency_threshold}")
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成输出文件名
        input_dir_name = os.path.basename(input_dir.rstrip('/'))
        output_file = os.path.join(output_dir, f"{input_dir_name}_batch_report.json")
        
        results = assess_all_maps(input_dir, output_dir, timeout_per_file)
        
        # 保存到指定的输出文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"The batch assessment report has been saved to: {output_file}")
        return results
        
    except Exception as e:
        logger.error(f"Batch evaluation failed: {e}")
        raise

def batch_assess_files(file_paths: List[str], output_dir: str, timeout_per_file: int = 30) -> Dict[str, Any]:
    """批量评估指定的文件列表"""
    try:
        logger.info(f"Commencing batch assessment {len(file_paths)} files")
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        results = {}
        assessor = DungeonQualityAssessor()
        
        for i, file_path in enumerate(file_paths, 1):
            try:
                logger.info(f"Assess file [{i}/{len(file_paths)}]: {os.path.basename(file_path)}")
                
                # 设置超时
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(timeout_per_file)
                
                try:
                    # 读取地图数据
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 评估质量
                    start_time = time.time()
                    metrics = assessor.assess_quality(data)
                    end_time = time.time()
                    
                    # 取消超时
                    signal.alarm(0)
                    
                    # 收集结果
                    file_name = os.path.basename(file_path)
                    results[file_name] = {
                        'overall_score': metrics['overall_score'],
                        'grade': metrics['grade'],
                        'detailed_metrics': metrics['scores'],
                        'category_scores': metrics['category_scores'],
                        'recommendations': metrics['recommendations'],
                        'processing_time': end_time - start_time,
                        'status': 'success',
                        'file_path': file_path
                    }
                    
                    logger.info(f"✓ {file_name}: {metrics['overall_score']:.3f} ({metrics['grade']}) - {end_time - start_time:.2f}s")
                    
                except TimeoutError:
                    signal.alarm(0)
                    logger.error(f"Assess {file_name} timeout")
                    results[file_name] = {
                        'error': 'timeout',
                        'overall_score': 0.0,
                        'grade': 'timeout',
                        'status': 'timeout',
                        'file_path': file_path
                    }
                except Exception as e:
                    signal.alarm(0)
                    logger.error(f"Assess {file_name} error: {e}")
                    results[file_name] = {
                        'error': str(e),
                        'overall_score': 0.0,
                        'grade': 'error',
                        'status': 'error',
                        'file_path': file_path
                    }
                    
            except Exception as e:
                logger.error(f"Assess {file_path} unexpected error: {e}")
                file_name = os.path.basename(file_path)
                results[file_name] = {
                    'error': f'unexpected error: {str(e)}',
                    'overall_score': 0.0,
                    'grade': 'unexpected error',
                    'status': 'error',
                    'file_path': file_path
                }
        
        # 生成汇总报告
        summary_report = generate_summary_report(results)
        
        # 保存汇总报告
        summary_file = os.path.join(output_dir, "batch_assessment_summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_report, f, ensure_ascii=False, indent=2)
        
        # 保存详细结果
        results_file = os.path.join(output_dir, "batch_assessment_results.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Batch evaluation completed. Results saved to: {output_dir}")
        return results
        
    except Exception as e:
        logger.error(f"Batch evaluation failed: {e}")
        raise

def analyze_cross_datasets(root_dir: str = "output/F_Q_Report", output_dir: str = None) -> Dict[str, Any]:
    """跨数据集分析功能 - 分析多个子目录中的质量报告"""
    try:
        root_path = Path(root_dir)
        if not root_path.exists():
            logger.error(f"Root directory not found: {root_dir}")
            return {'error': f'Directory not found: {root_dir}'}
        
        if output_dir is None:
            output_dir = str(root_path / 'SA')
        
        logger.info(f"Commencing cross-dataset analysis, root directory: {root_dir}")
        
        # 扫描子目录
        subdirs = [d for d in root_path.iterdir() 
                  if d.is_dir() and d.name not in ['SA', 'charts'] and not d.name.startswith('.')]
        
        if not subdirs:
            logger.error("No valid subdirectories found")
            return {'error': 'No valid subdirectories found'}
        
        logger.info(f"Discover the dataset directory: {[d.name for d in subdirs]}")
        
        # 加载各数据集
        datasets = {}
        for subdir in subdirs:
            dataset_name = subdir.name
            data_rows = []
            
            # 加载该子目录下的所有质量报告JSON文件
            for json_file in subdir.glob("quality_report_*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 提取指标数据
                    row = {'filename': json_file.stem}
                    
                    # 提取总分
                    if 'overall_score' in data:
                        row['overall_score'] = data['overall_score']
                    
                    # 提取详细指标（从scores字段）
                    scores = data.get('scores', {})
                    for metric_name, metric_data in scores.items():
                        if isinstance(metric_data, dict):
                            score = metric_data.get('score', 0.0)
                        else:
                            score = float(metric_data) if metric_data else 0.0
                        row[metric_name] = score
                    
                    # 提取类别分数
                    category_scores = data.get('category_scores', {})
                    for category, score in category_scores.items():
                        row[f'{category}_score'] = score
                    
                    if 'overall_score' in row:  # 确保有有效数据
                        data_rows.append(row)
                        
                except Exception as e:
                    logger.warning(f"Failed to load {json_file}: {e}")
                    continue
            
            if data_rows:
                datasets[dataset_name] = pd.DataFrame(data_rows)
                logger.info(f"加载 {dataset_name} 数据集: {len(data_rows)} 个报告")
        
        if not datasets:
            return {'error': 'No valid datasets loaded'}
        
        # 生成跨数据集分析
        analysis_result = generate_cross_dataset_analysis(datasets, output_dir)
        
        logger.info(f"Cross-dataset analysis completed, results saved to: {output_dir}")
        return analysis_result
        
    except Exception as e:
        logger.error(f"跨数据集分析失败: {e}")
        return {'error': f'Analysis failed: {str(e)}'}

def generate_cross_dataset_analysis(datasets: Dict[str, pd.DataFrame], output_dir: str) -> Dict[str, Any]:
    """生成跨数据集分析报告"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 基础统计
    dataset_stats = {}
    for name, df in datasets.items():
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        stats_dict = {}
        
        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) > 0:
                stats_dict[col] = {
                    'count': int(len(series)),
                    'mean': float(series.mean()),
                    'std': float(series.std()),
                    'min': float(series.min()),
                    'max': float(series.max()),
                    'median': float(series.median()),
                    'q25': float(series.quantile(0.25)),
                    'q75': float(series.quantile(0.75)),
                    'skewness': float(series.skew()),
                    'kurtosis': float(series.kurtosis())
                }
        
        dataset_stats[name] = {
            'total_samples': len(df),
            'metrics': stats_dict
        }
    
    # 获取共同指标
    all_metrics = set()
    for df in datasets.values():
        all_metrics.update(df.select_dtypes(include=[np.number]).columns.tolist())
    
    # 计算各数据集在共同指标上的差异
    common_metrics = set(all_metrics)
    for df in datasets.values():
        current_metrics = set(df.select_dtypes(include=[np.number]).columns.tolist())
        common_metrics = common_metrics.intersection(current_metrics)
    
    common_metrics = list(common_metrics)
    logger.info(f"Common indicators: {len(common_metrics)}")
    
    # 跨数据集比较
    cross_comparison = {}
    for metric in common_metrics:
        metric_data = {}
        groups = []
        
        for dataset_name, df in datasets.items():
            if metric in df.columns:
                values = df[metric].dropna()
                if len(values) > 0:
                    groups.append(values.tolist())
                    metric_data[dataset_name] = {
                        'mean': float(values.mean()),
                        'std': float(values.std()),
                        'count': len(values)
                    }
        
        # Kruskal-Wallis检验
        if len(groups) >= 2 and all(len(group) > 0 for group in groups):
            try:
                h_stat, p_value = stats.kruskal(*groups)
                metric_data['kruskal_wallis'] = {
                    'h_statistic': float(h_stat),
                    'p_value': float(p_value),
                    'significant': bool(p_value < 0.05)
                }
            except:
                pass
        
        cross_comparison[metric] = metric_data
    
    # Spearman相关性分析（每个数据集内部）
    spearman_correlations = {}
    for dataset_name, df in datasets.items():
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) > 1 and 'overall_score' in numeric_cols:
            analysis_cols = [col for col in numeric_cols if col != 'overall_score']
            overall_correlations = []
            
            for col in analysis_cols:
                try:
                    rho, p_val = stats.spearmanr(df[col].dropna(), df['overall_score'].dropna())
                    overall_correlations.append({
                        'metric': col,
                        'spearman_correlation': float(rho),
                        'p_value': float(p_val),
                        'significant': bool(p_val < 0.05)
                    })
                except:
                    continue
            
            # 按相关性绝对值排序
            overall_correlations.sort(key=lambda x: abs(x['spearman_correlation']), reverse=True)
            
            # 所有指标都应该与overall_score正相关
            positive_corrs = [c for c in overall_correlations if c['spearman_correlation'] > 0]
            negative_corrs = [c for c in overall_correlations if c['spearman_correlation'] < 0]
            
            # 对负相关进行警告记录，但仍然按绝对值排序显示最强相关
            warning_negative_corrs = []
            if negative_corrs:
                warning_negative_corrs = negative_corrs[:3]  # 记录前3个负相关作为警告
            
            spearman_correlations[dataset_name] = {
                'overall_score_correlations': overall_correlations,
                'top_positive_correlation': positive_corrs[0] if positive_corrs else None,
                'warning_negative_correlations': warning_negative_corrs, 
                'top_correlation_by_abs_value': overall_correlations[0] if overall_correlations else None
            }
    
    # 生成汇总报告
    analysis_report = {
        'analysis_timestamp': pd.Timestamp.now().isoformat(),
        'datasets_analyzed': list(datasets.keys()),
        'dataset_statistics': dataset_stats,
        'cross_dataset_comparison': cross_comparison,
        'spearman_correlations': spearman_correlations,
        'common_metrics': common_metrics,
        'total_reports_analyzed': sum(len(df) for df in datasets.values())
    }
    
    # 保存JSON报告
    with open(output_path / 'cross_dataset_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(analysis_report, f, ensure_ascii=False, indent=2)
    
    # 保存CSV统计文件
    for name, df in datasets.items():
        basic_stats = df.describe()
        basic_stats.to_csv(output_path / f"{name}_statistics.csv")
        
        # 详细统计
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            detailed_stats = pd.DataFrame({
                'count': df[numeric_cols].count(),
                'mean': df[numeric_cols].mean(),
                'std': df[numeric_cols].std(),
                'min': df[numeric_cols].min(),
                'max': df[numeric_cols].max(),
                'median': df[numeric_cols].median(),
                'q25': df[numeric_cols].quantile(0.25),
                'q75': df[numeric_cols].quantile(0.75),
                'skewness': df[numeric_cols].skew(),
                'kurtosis': df[numeric_cols].kurtosis()
            }).round(4)
            
            detailed_stats.to_csv(output_path / f"{name}_detailed_statistics.csv")
    
    # 保存合并的汇总统计
    if datasets:
        all_data = pd.concat([df.assign(dataset=name) for name, df in datasets.items()], ignore_index=True)
        all_stats = all_data.groupby('dataset').describe()
        all_stats.to_csv(output_path / "cross_dataset_summary.csv")
    
    # 打印分析摘要
    print_cross_dataset_summary(analysis_report)
    
    return analysis_report

def print_cross_dataset_summary(report: Dict[str, Any]):
    """打印跨数据集分析摘要"""
    print("\n" + "="*60)
    print("CROSS-DATASET ANALYSIS SUMMARY")
    print("="*60)
    
    datasets_analyzed = report.get('datasets_analyzed', [])
    dataset_stats = report.get('dataset_statistics', {})
    
    print(f"\nDatasets Analyzed: {', '.join(datasets_analyzed)}")
    print(f"Total Reports: {report.get('total_reports_analyzed', 0)}")
    print(f"Common Metrics: {len(report.get('common_metrics', []))}")
    
    # 显示各数据集基本信息
    for dataset_name in datasets_analyzed:
        stats = dataset_stats.get(dataset_name, {})
        total_samples = stats.get('total_samples', 0)
        metrics = stats.get('metrics', {})
        
        print(f"\n{dataset_name} Dataset:")
        print(f"  Total Samples: {total_samples}")
        print(f"  Metrics Analyzed: {len(metrics)}")
        
        if 'overall_score' in metrics:
            overall_stats = metrics['overall_score']
            print(f"  Overall Score - Mean: {overall_stats['mean']:.3f}, Std: {overall_stats['std']:.3f}")
    
    # 显示显著差异的指标
    comparison = report.get('cross_dataset_comparison', {})
    significant_diffs = []
    
    for metric, data in comparison.items():
        kw_test = data.get('kruskal_wallis', {})
        if kw_test.get('significant', False):
            significant_diffs.append((metric, kw_test['p_value']))
    
    if significant_diffs:
        print(f"\nSignificant Differences Between Datasets:")
        for metric, p_val in significant_diffs[:5]:
            print(f"  {metric}: p = {p_val:.6f}")
    
    # 显示Spearman相关性摘要
    correlations = report.get('spearman_correlations', {})
    if correlations:
        print(f"\nTop Spearman Correlations with Overall Score:")
        for dataset_name in datasets_analyzed:
            dataset_corrs = correlations.get(dataset_name, {})
            top_pos = dataset_corrs.get('top_positive_correlation')
            top_abs = dataset_corrs.get('top_correlation_by_abs_value')
            warning_negs = dataset_corrs.get('warning_negative_correlations', [])
            
            if top_pos or top_abs:
                print(f"\n{dataset_name}:")
                if top_pos:
                    rho = top_pos['spearman_correlation']
                    p_val = top_pos['p_value']
                    sig_str = "*" if top_pos['significant'] else ""
                    print(f"  Strongest +: {top_pos['metric']}: ρ = {rho:.3f} (p={p_val:.3f}){sig_str}")
                
                if top_abs and top_abs != top_pos:
                    rho = top_abs['spearman_correlation']
                    p_val = top_abs['p_value']
                    sig_str = "*" if top_abs['significant'] else ""
                    print(f"  Strongest overall: {top_abs['metric']}: ρ = {rho:.3f} (p={p_val:.3f}){sig_str}")
                
                # 如果有负相关，作为警告显示
                if warning_negs:
                    print(f" Unexpected negative correlations detected:")
                    for neg_corr in warning_negs[:2]:  # 只显示前2个
                        rho = neg_corr['spearman_correlation']
                        p_val = neg_corr['p_value']
                        print(f"    {neg_corr['metric']}: ρ = {rho:.3f} (p={p_val:.3f}) - Check metric design")
    
    print("="*60)

def main():
    """主函数 - 保留用于直接运行脚本"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Batch assessment of dungeon map quality')
    parser.add_argument('--input', default='output', help='Enter directory path')
    parser.add_argument('--output', default='output/reports', help='Output directory path')
    parser.add_argument('--timeout', type=int, default=30, help='Timeout period for each file (s)')
    
    args = parser.parse_args()
    
    logger.info("Commencing batch quality assessment...")
    results = assess_all_maps(args.input, args.output, args.timeout)
    logger.info("Batch quality assessment completed!")

if __name__ == '__main__':
    main() 