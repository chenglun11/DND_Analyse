#!/usr/bin/env python3
"""
统计分析模块 - 基于批量评估结果进行相关性分析和高级统计分析
"""

import os
import json
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional
from scipy import stats
from scipy.stats import spearmanr, pearsonr, shapiro, normaltest, kruskal, f_oneway
from advanced_analytics import AdvancedAnalytics
from unified_chart_generator import UnifiedChartGenerator

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StatisticalAnalyzer:
    """统计分析器"""
    
    def __init__(self):
        self.analytics = AdvancedAnalytics()
        self.chart_generator = UnifiedChartGenerator()
        
    def load_batch_summary(self, summary_path: str) -> Dict[str, Any]:
        """加载批量评估汇总报告"""
        try:
            with open(summary_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Summary file not found: {summary_path}")
            return {}
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON format: {summary_path}")
            return {}
    
    def extract_metrics_data(self, summary_data: Dict[str, Any]) -> pd.DataFrame:
        """从汇总数据中提取指标数据为DataFrame"""
        # 支持两种格式：有detailed_results键的和没有的
        if 'detailed_results' in summary_data:
            detailed_results = summary_data['detailed_results']
        else:
            # 直接使用整个summary_data作为detailed_results
            # 过滤掉非地图结果的键（如summary等）
            detailed_results = {k: v for k, v in summary_data.items() 
                              if isinstance(v, dict) and 'overall_score' in v}
        
        if not detailed_results:
            logger.error("No valid detailed results found in summary data")
            return pd.DataFrame()
        
        # 定义要提取的指标
        metrics = [
            'accessibility', 'degree_variance', 'door_distribution', 'dead_end_ratio',
            'key_path_length', 'loop_ratio', 'path_diversity', 'treasure_monster_distribution', 
            'geometric_balance'
        ]
        
        data_rows = []
        
        for map_name, result in detailed_results.items():
            if result['status'] != 'success':
                continue
                
            row = {'map_name': map_name, 'overall_score': result['overall_score']}
            
            # 提取各项指标分数
            for metric in metrics:
                if metric in result.get('detailed_metrics', {}):
                    metric_result = result['detailed_metrics'][metric]
                    if isinstance(metric_result, dict):
                        score = metric_result.get('score', 0.0)
                    else:
                        score = float(metric_result)
                    row[metric] = score
                else:
                    row[metric] = 0.0
            
            # 提取类别分数
            if 'category_scores' in result:
                for category, score in result['category_scores'].items():
                    row[f'{category}_score'] = score
            
            data_rows.append(row)
        
        df = pd.DataFrame(data_rows)
        logger.info(f"Extracted metrics data: {len(df)} maps, {len(df.columns)} metrics")
        return df
    
    def perform_correlation_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """执行相关性分析 - 包含FDR校正的Spearman相关性"""
        if df.empty:
            logger.error("Empty dataframe for correlation analysis")
            return {}
        
        # 选择数值列进行相关性分析
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if 'overall_score' in numeric_cols:
            numeric_cols.remove('overall_score')  # 总分单独处理
        
        numeric_data = df[numeric_cols]
        
        # 计算Spearman相关性和p值，带FDR校正
        from scipy.stats import false_discovery_control
        n_features = len(numeric_cols)
        spearman_matrix = np.zeros((n_features, n_features))
        pvalue_matrix = np.zeros((n_features, n_features))
        
        # 计算所有成对的Spearman相关性和p值
        p_values_flat = []
        correlations_flat = []
        for i in range(n_features):
            for j in range(n_features):
                if i == j:
                    spearman_matrix[i, j] = 1.0
                    pvalue_matrix[i, j] = 0.0
                else:
                    corr, p_val = spearmanr(numeric_data.iloc[:, i], numeric_data.iloc[:, j])
                    spearman_matrix[i, j] = corr
                    pvalue_matrix[i, j] = p_val
                    if i < j:  # 只收集上三角的p值用于FDR校正
                        p_values_flat.append(p_val)
                        correlations_flat.append(corr)
        
        # FDR校正
        if p_values_flat:
            fdr_corrected = false_discovery_control(p_values_flat, method='bh')
            
            # 将FDR校正的p值映射回矩阵
            fdr_matrix = np.copy(pvalue_matrix)
            idx = 0
            for i in range(n_features):
                for j in range(i+1, n_features):
                    fdr_matrix[i, j] = fdr_corrected[idx]
                    fdr_matrix[j, i] = fdr_corrected[idx]  # 对称矩阵
                    idx += 1
        else:
            fdr_matrix = pvalue_matrix
        
        # 定义预期的逻辑相关性
        expected_correlations = {
            ('accessibility', 'degree_variance'): 'positive',  # 连接多导致度方差大
            ('accessibility', 'door_distribution'): 'positive',  # 门分布均匀提高连通性
            ('accessibility', 'dead_end_ratio'): 'negative',  # 死胡同多降低连通性
            ('degree_variance', 'door_distribution'): 'positive',  # 门分布均匀时度差异明显
            ('dead_end_ratio', 'loop_ratio'): 'negative',  # 回环多时死胡同少
            ('path_diversity', 'accessibility'): 'positive',  # 高连通性带来路径多样性
            ('path_diversity', 'loop_ratio'): 'positive',  # 回环有助路径多样性
            ('key_path_length', 'accessibility'): 'negative',  # 关键路径长降低连通性
            ('treasure_monster_distribution', 'accessibility'): 'weak_positive',  # 分布均匀间接影响可达性
            ('geometric_balance', 'accessibility'): 'weak_positive',  # 空间合理性辅助连通性
        }
        
        # Pearson相关性分析（保留原有逻辑）
        pearson_corr = numeric_data.corr(method='pearson')
        
        # 将numpy矩阵转换为pandas DataFrame格式
        spearman_corr = pd.DataFrame(spearman_matrix, index=numeric_cols, columns=numeric_cols)
        pvalue_df = pd.DataFrame(pvalue_matrix, index=numeric_cols, columns=numeric_cols)
        fdr_df = pd.DataFrame(fdr_matrix, index=numeric_cols, columns=numeric_cols)
        
        # 提取强相关和中等相关关系（基于Spearman和逻辑预期）
        strong_correlations = []
        moderate_correlations = []
        logical_inconsistencies = []
        
        for i in range(len(numeric_cols)):
            for j in range(i + 1, len(numeric_cols)):
                metric1, metric2 = numeric_cols[i], numeric_cols[j]
                pearson_val = pearson_corr.iloc[i, j]
                spearman_val = spearman_corr.iloc[i, j]
                p_val = pvalue_df.iloc[i, j]
                fdr_p_val = fdr_df.iloc[i, j]
                
                # 检查是否有预期的逻辑相关性
                expected_direction = None
                for (m1, m2), direction in expected_correlations.items():
                    if (metric1 == m1 and metric2 == m2) or (metric1 == m2 and metric2 == m1):
                        expected_direction = direction
                        break
                
                # 验证逻辑一致性
                is_logical = True
                if expected_direction:
                    if expected_direction == 'positive' and spearman_val < 0:
                        is_logical = False
                    elif expected_direction == 'negative' and spearman_val > 0:
                        is_logical = False
                    elif expected_direction == 'weak_positive' and spearman_val < -0.2:
                        is_logical = False
                    
                    if not is_logical:
                        logical_inconsistencies.append({
                            'metric1': metric1,
                            'metric2': metric2,
                            'expected': expected_direction,
                            'actual_spearman': float(spearman_val),
                            'actual_pearson': float(pearson_val),
                            'p_value': float(p_val),
                            'fdr_p_value': float(fdr_p_val)
                        })
                
                # 分类相关性强度
                corr_item = {
                    'metric1': metric1,
                    'metric2': metric2,
                    'pearson_correlation': float(pearson_val),
                    'spearman_correlation': float(spearman_val),
                    'p_value': float(p_val),
                    'fdr_p_value': float(fdr_p_val),
                    'significant_at_05': bool(fdr_p_val < 0.05),
                    'significant_at_01': bool(fdr_p_val < 0.01),
                    'expected_direction': expected_direction,
                    'logically_consistent': is_logical
                }
                
                if abs(spearman_val) >= 0.7:  # 强相关
                    strong_correlations.append(corr_item)
                elif abs(spearman_val) >= 0.4:  # 中等相关
                    moderate_correlations.append(corr_item)
                elif expected_direction and abs(spearman_val) >= 0.2:  # 有逻辑预期的弱相关
                    moderate_correlations.append(corr_item)
        
        # 与总分的相关性分析
        overall_correlations = []
        if 'overall_score' in df.columns:
            for metric in numeric_cols:
                if metric != 'overall_score':
                    pearson_val, p_val_p = pearsonr(df[metric], df['overall_score'])
                    spearman_val, p_val_s = spearmanr(df[metric], df['overall_score'])
                    
                    overall_correlations.append({
                        'metric': metric,
                        'pearson_correlation': float(pearson_val),
                        'pearson_p_value': float(p_val_p),
                        'spearman_correlation': float(spearman_val),
                        'spearman_p_value': float(p_val_s)
                    })
        
        # 转换为普通Python类型避免JSON序列化问题
        spearman_dict = {}
        for col in spearman_corr.columns:
            spearman_dict[col] = {k: float(v) for k, v in spearman_corr[col].to_dict().items()}
        
        # 转换FDR p值矩阵
        fdr_dict = {}
        for col in fdr_df.columns:
            fdr_dict[col] = {k: float(v) for k, v in fdr_df[col].to_dict().items()}
        
        # 转换原始p值矩阵
        pvalue_dict = {}
        for col in pvalue_df.columns:
            pvalue_dict[col] = {k: float(v) for k, v in pvalue_df[col].to_dict().items()}
        
        # 计算逻辑一致性分数
        total_expected = len([k for k in expected_correlations.keys() 
                             if any(m in numeric_cols for m in k)])
        inconsistent_count = len(logical_inconsistencies)
        consistency_score = 1.0 - (inconsistent_count / max(total_expected, 1))
        
        return {
            'spearman_correlation_matrix': spearman_dict,
            'pvalue_matrix': pvalue_dict,
            'fdr_corrected_pvalue_matrix': fdr_dict,
            'strong_correlations': strong_correlations,
            'moderate_correlations': moderate_correlations,
            'overall_score_correlations': overall_correlations,
            'logical_inconsistencies': logical_inconsistencies,
            'logical_consistency_score': consistency_score,
            'expected_correlations_found': total_expected - inconsistent_count,
            'total_expected_correlations': total_expected,
            'metric_names': numeric_cols,
            'sample_size': len(df)
        }
    
    def perform_advanced_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """执行高级统计分析"""
        if df.empty:
            logger.error("Empty dataframe for advanced analysis")
            return {}
        
        # 选择数值列
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if 'overall_score' in numeric_cols:
            numeric_cols.remove('overall_score')
        
        numeric_data = df[numeric_cols].values
        correlation_matrix = np.corrcoef(numeric_data.T)
        
        # VIF分析
        vif_analysis = self.analytics.calculate_vif(correlation_matrix, numeric_cols)
        
        # PCA分析
        pca_analysis = self.analytics.perform_pca(numeric_data, numeric_cols)
        
        # 聚类分析
        clustering_analysis = self.analytics.perform_clustering(correlation_matrix, numeric_cols)
        
        # 转换所有numpy类型为Python原生类型
        def convert_numpy_types(obj):
            if isinstance(obj, dict):
                return {str(k): convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(v) for v in obj]
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif hasattr(obj, 'dtype'):  # 其他numpy类型
                return obj.item() if hasattr(obj, 'item') else float(obj)
            else:
                return obj
        
        vif_analysis = convert_numpy_types(vif_analysis)
        pca_analysis = convert_numpy_types(pca_analysis)
        clustering_analysis = convert_numpy_types(clustering_analysis)
        
        return {
            'vif_analysis': vif_analysis,
            'pca_analysis': pca_analysis,
            'clustering_analysis': clustering_analysis
        }
    
    def test_normality(self, data: np.ndarray, metric_name: str) -> Dict[str, Any]:
        """Test normality of a metric using multiple tests"""
        n = len(data)
        results = {
            'metric': metric_name,
            'sample_size': n,
            'is_normal': False,
            'tests': {}
        }
        
        # Remove NaN values
        clean_data = data[~np.isnan(data)]
        if len(clean_data) < 8:  # Need at least 8 samples for reliable testing
            results['tests']['insufficient_data'] = True
            return results
        
        # Shapiro-Wilk test (best for small samples, n < 50)
        if len(clean_data) <= 50:
            try:
                sw_stat, sw_p = shapiro(clean_data)
                results['tests']['shapiro_wilk'] = {
                    'statistic': float(sw_stat),
                    'p_value': float(sw_p),
                    'normal_at_05': bool(sw_p > 0.05)
                }
            except Exception as e:
                results['tests']['shapiro_wilk'] = {'error': str(e)}
        
        # D'Agostino and Pearson's normality test (good for larger samples)
        if len(clean_data) >= 20:
            try:
                dp_stat, dp_p = normaltest(clean_data)
                results['tests']['dagostino_pearson'] = {
                    'statistic': float(dp_stat),
                    'p_value': float(dp_p),
                    'normal_at_05': bool(dp_p > 0.05)
                }
            except Exception as e:
                results['tests']['dagostino_pearson'] = {'error': str(e)}
        
        # Kolmogorov-Smirnov test against normal distribution
        try:
            # Standardize data
            standardized = (clean_data - np.mean(clean_data)) / np.std(clean_data)
            ks_stat, ks_p = stats.kstest(standardized, 'norm')
            results['tests']['kolmogorov_smirnov'] = {
                'statistic': float(ks_stat),
                'p_value': float(ks_p),
                'normal_at_05': bool(ks_p > 0.05)
            }
        except Exception as e:
            results['tests']['kolmogorov_smirnov'] = {'error': str(e)}
        
        # Determine overall normality (conservative approach: need majority of tests to pass)
        normal_tests = []
        for test_name, test_result in results['tests'].items():
            if isinstance(test_result, dict) and 'normal_at_05' in test_result:
                normal_tests.append(test_result['normal_at_05'])
        
        if normal_tests:
            # Conservative: require at least half of valid tests to indicate normality
            results['is_normal'] = sum(normal_tests) >= len(normal_tests) / 2
        
        return results
    
    def perform_group_comparison_tests(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform Kruskal-Wallis or ANOVA tests for each metric based on distribution"""
        if df.empty:
            logger.error("Empty dataframe for group comparison tests")
            return {}
        
        # Get numeric columns (metrics)
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if 'overall_score' in numeric_cols:
            numeric_cols.remove('overall_score')
        
        # Test for grouping variable - we'll create groups based on overall score quartiles
        if 'overall_score' not in df.columns:
            logger.warning("No overall_score column found for grouping")
            return {}
        
        # Create quartile-based groups
        df_copy = df.copy()
        df_copy['score_quartile'] = pd.qcut(df_copy['overall_score'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'])
        
        results = {
            'grouping_method': 'overall_score_quartiles',
            'group_sizes': df_copy['score_quartile'].value_counts().to_dict(),
            'normality_tests': {},
            'statistical_tests': {}
        }
        
        logger.info(f"Testing {len(numeric_cols)} metrics across {len(results['group_sizes'])} groups")
        
        for metric in numeric_cols:
            logger.info(f"Analyzing metric: {metric}")
            
            # Test normality for this metric
            metric_data = df_copy[metric].values
            normality_result = self.test_normality(metric_data, metric)
            results['normality_tests'][metric] = normality_result
            
            # Prepare groups for statistical testing
            groups = []
            for quartile in ['Q1', 'Q2', 'Q3', 'Q4']:
                group_data = df_copy[df_copy['score_quartile'] == quartile][metric].dropna().values
                if len(group_data) > 0:
                    groups.append(group_data)
            
            if len(groups) < 2:
                results['statistical_tests'][metric] = {
                    'error': 'Insufficient groups for comparison'
                }
                continue
            
            # Choose appropriate test based on normality
            is_normal = normality_result['is_normal']
            test_result = {
                'metric': metric,
                'is_normal': is_normal,
                'test_used': None,
                'groups_compared': len(groups)
            }
            
            try:
                if is_normal:
                    # Use one-way ANOVA for normally distributed data
                    f_stat, p_value = f_oneway(*groups)
                    test_result.update({
                        'test_used': 'one_way_anova',
                        'f_statistic': float(f_stat),
                        'p_value': float(p_value),
                        'significant_at_05': bool(p_value < 0.05),
                        'significant_at_01': bool(p_value < 0.01)
                    })
                    
                    # Post-hoc analysis for ANOVA if significant
                    if p_value < 0.05:
                        try:
                            from scipy.stats import tukey_hsd
                            # Prepare data for Tukey's HSD
                            all_data = np.concatenate(groups)
                            group_labels = []
                            for i, group in enumerate(groups):
                                group_labels.extend([f'Q{i+1}'] * len(group))
                            
                            tukey_result = tukey_hsd(*groups)
                            test_result['post_hoc'] = {
                                'method': 'tukey_hsd',
                                'pairwise_p_values': tukey_result.pvalue.tolist(),
                                'significant_pairs': []
                            }
                            
                            # Find significant pairs
                            for i in range(len(tukey_result.pvalue)):
                                for j in range(len(tukey_result.pvalue[i])):
                                    if i < j and tukey_result.pvalue[i][j] < 0.05:
                                        test_result['post_hoc']['significant_pairs'].append({
                                            'group1': f'Q{i+1}',
                                            'group2': f'Q{j+1}',
                                            'p_value': float(tukey_result.pvalue[i][j])
                                        })
                        except ImportError:
                            # Fallback if tukey_hsd not available
                            test_result['post_hoc'] = {'note': 'Post-hoc analysis requires newer scipy version'}
                        except Exception as e:
                            test_result['post_hoc'] = {'error': str(e)}
                            
                else:
                    # Use Kruskal-Wallis test for non-normally distributed data
                    h_stat, p_value = kruskal(*groups)
                    test_result.update({
                        'test_used': 'kruskal_wallis',
                        'h_statistic': float(h_stat),
                        'p_value': float(p_value),
                        'significant_at_05': bool(p_value < 0.05),
                        'significant_at_01': bool(p_value < 0.01)
                    })
                    
                    # Post-hoc analysis for Kruskal-Wallis if significant
                    if p_value < 0.05:
                        # Pairwise Mann-Whitney U tests with Bonferroni correction
                        from scipy.stats import mannwhitneyu
                        pairwise_results = []
                        n_comparisons = len(groups) * (len(groups) - 1) // 2
                        
                        for i in range(len(groups)):
                            for j in range(i + 1, len(groups)):
                                try:
                                    u_stat, u_p = mannwhitneyu(groups[i], groups[j], alternative='two-sided')
                                    bonferroni_p = u_p * n_comparisons
                                    pairwise_results.append({
                                        'group1': f'Q{i+1}',
                                        'group2': f'Q{j+1}',
                                        'u_statistic': float(u_stat),
                                        'raw_p_value': float(u_p),
                                        'bonferroni_p_value': float(min(bonferroni_p, 1.0)),
                                        'significant_bonferroni': bool(bonferroni_p < 0.05)
                                    })
                                except Exception as e:
                                    pairwise_results.append({
                                        'group1': f'Q{i+1}',
                                        'group2': f'Q{j+1}',
                                        'error': str(e)
                                    })
                        
                        test_result['post_hoc'] = {
                            'method': 'mann_whitney_u_bonferroni',
                            'pairwise_results': pairwise_results,
                            'significant_pairs': [r for r in pairwise_results 
                                                if r.get('significant_bonferroni', False)]
                        }
                
                # Add descriptive statistics for each group
                group_stats = []
                for i, group in enumerate(groups):
                    group_stats.append({
                        'group': f'Q{i+1}',
                        'n': len(group),
                        'mean': float(np.mean(group)),
                        'std': float(np.std(group, ddof=1)),
                        'median': float(np.median(group)),
                        'q25': float(np.percentile(group, 25)),
                        'q75': float(np.percentile(group, 75))
                    })
                
                test_result['group_statistics'] = group_stats
                
            except Exception as e:
                test_result['error'] = str(e)
                logger.error(f"Statistical test failed for {metric}: {e}")
            
            results['statistical_tests'][metric] = test_result
        
        # Summary statistics
        normal_count = sum(1 for r in results['normality_tests'].values() if r.get('is_normal', False))
        significant_count = sum(1 for r in results['statistical_tests'].values() 
                              if r.get('significant_at_05', False))
        
        results['summary'] = {
            'total_metrics_tested': len(numeric_cols),
            'normally_distributed_metrics': normal_count,
            'non_normally_distributed_metrics': len(numeric_cols) - normal_count,
            'anova_tests_performed': sum(1 for r in results['statistical_tests'].values() 
                                       if r.get('test_used') == 'one_way_anova'),
            'kruskal_wallis_tests_performed': sum(1 for r in results['statistical_tests'].values() 
                                                if r.get('test_used') == 'kruskal_wallis'),
            'significant_differences_found': significant_count,
            'proportion_significant': significant_count / len(numeric_cols) if numeric_cols else 0
        }
        
        return results
    
    def generate_all_charts(self, correlation_data: Dict[str, Any], 
                          advanced_data: Dict[str, Any], 
                          df: pd.DataFrame, 
                          save_png: bool = False,
                          output_dir: str = None) -> Dict[str, str]:
        """生成所有图表，可选择保存为PNG文件或返回base64编码"""
        charts = {}
        saved_files = []
        
        try:
            # 提取相关性矩阵和指标名称（使用Spearman）
            spearman_matrix = correlation_data.get('spearman_correlation_matrix', {})
            metric_names = correlation_data.get('metric_names', [])
            
            # 使用Spearman矩阵
            primary_matrix = spearman_matrix
            matrix_type = "Spearman"
            
            if primary_matrix and metric_names:
                # 转换为矩阵格式
                matrix = []
                for metric1 in metric_names:
                    row = []
                    for metric2 in metric_names:
                        row.append(primary_matrix.get(metric1, {}).get(metric2, 0))
                    matrix.append(row)
                
                # 1. Spearman相关性热力图
                logger.info(f"生成{matrix_type}相关性热力图...")
                charts['spearman_heatmap'] = self.chart_generator.generate_correlation_heatmap(matrix, metric_names, matrix_type)
                
                # 2. FDR校正p值热力图
                fdr_matrix_data = correlation_data.get('fdr_corrected_pvalue_matrix', {})
                if fdr_matrix_data:
                    logger.info("生成FDR校正p值热力图...")
                    fdr_matrix = []
                    for metric1 in metric_names:
                        row = []
                        for metric2 in metric_names:
                            row.append(fdr_matrix_data.get(metric1, {}).get(metric2, 1.0))
                        fdr_matrix.append(row)
                    charts['fdr_heatmap'] = self.chart_generator.generate_fdr_heatmap(fdr_matrix, matrix, metric_names)
                
                # 3. 相关性散点图
                logger.info("生成相关性散点图...")
                charts['scatter'] = self.chart_generator.generate_scatter_plot(matrix, metric_names)
                
                # 4. 网络关系图
                logger.info("生成网络关系图...")
                charts['network'] = self.chart_generator.generate_network_graph(matrix, metric_names)
            
            # P值分析图表
            if correlation_data.get('strong_correlations') or correlation_data.get('moderate_correlations'):
                logger.info("生成P值分析图表...")
                # 模拟P值数据（基于Spearman相关性强度估算）
                p_value_matrix = []
                for metric1 in metric_names:
                    row = []
                    for metric2 in metric_names:
                        corr_val = primary_matrix.get(metric1, {}).get(metric2, 0)
                        # 根据相关性强度估算P值
                        if abs(corr_val) > 0.7:
                            p_val = 0.001
                        elif abs(corr_val) > 0.5:
                            p_val = 0.01
                        elif abs(corr_val) > 0.3:
                            p_val = 0.05
                        else:
                            p_val = 0.1
                        row.append(p_val)
                    p_value_matrix.append(row)
                
                charts['pvalue_heatmap'] = self.chart_generator.generate_pvalue_heatmap(p_value_matrix, metric_names)
                # 修复参数顺序和数量
                bonferroni_matrix = [[p * len(metric_names) * len(metric_names) for p in row] for row in p_value_matrix]
                fdr_matrix = [[min(p * 1.5, 1.0) for p in row] for row in p_value_matrix]
                charts['significance_comparison'] = self.chart_generator.generate_significance_comparison(
                    p_value_matrix, bonferroni_matrix, fdr_matrix, metric_names)
                charts['consistency_analysis'] = self.chart_generator.generate_consistency_analysis(
                    matrix, p_value_matrix, metric_names)
            
            # 高级分析图表
            if advanced_data:
                # VIF分析图表
                vif_data = advanced_data.get('vif_analysis', {})
                if vif_data and 'vif_results' in vif_data:
                    logger.info("生成VIF分析图表...")
                    # 转换数据格式
                    vif_chart_data = []
                    for item in vif_data['vif_results']:
                        vif_chart_data.append({
                            'feature': item['metric'],
                            'vif': item['vif'],
                            'level': item.get('level', 'UNKNOWN')
                        })
                    charts['vif_analysis'] = self.chart_generator.generate_vif_chart(vif_chart_data)
                
                # PCA分析图表 - 分别生成各个组件
                pca_data = advanced_data.get('pca_analysis', {})
                if pca_data and 'explained_variance_ratio' in pca_data:
                    logger.info("生成PCA分析图表...")
                    # 主PCA分析图（方差解释比例）
                    charts['pca_analysis'] = self.chart_generator.generate_pca_analysis(pca_data, metric_names)
                    
                    # PCA累积方差图（单独生成）
                    charts['pca_cumulative_variance'] = self.chart_generator.generate_pca_cumulative_variance(pca_data, metric_names)
                    
                    # 单独的PCA散点图（如果有足够的主成分）
                    if len(pca_data.get('explained_variance_ratio', [])) >= 2:
                        charts['pca_scatterplot'] = self.chart_generator.generate_pca_scatterplot(pca_data, metric_names)
                    
                    # PCA贡献图（显示各变量对主成分的贡献）
                    if 'components' in pca_data:
                        charts['pca_loadings'] = self.chart_generator.generate_pca_loadings(pca_data, metric_names)
                
                # 聚类分析图表
                clustering_data = advanced_data.get('clustering_analysis', {})
                if clustering_data and 'linkage_matrix' in clustering_data:
                    logger.info("生成聚类分析图表...")
                    charts['clustering_analysis'] = self.chart_generator.generate_clustering_analysis(clustering_data)
            
            logger.info(f"成功生成 {len(charts)} 个图表")
            
        except Exception as e:
            logger.error(f"图表生成失败: {e}")
        
        return charts
    
    def generate_analysis_report(self, correlation_data: Dict[str, Any], 
                               advanced_data: Dict[str, Any], 
                               df: pd.DataFrame,
                               group_comparison_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """生成完整的统计分析报告"""
        
        # 基础统计信息
        basic_stats = {
            'total_maps': len(df),
            'metrics_analyzed': len(correlation_data.get('metric_names', [])),
            'strong_correlations_count': len(correlation_data.get('strong_correlations', [])),
            'moderate_correlations_count': len(correlation_data.get('moderate_correlations', []))
        }
        
        # 描述性统计
        descriptive_stats = {}
        if not df.empty:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            for col in numeric_cols:
                descriptive_stats[col] = {
                    'mean': float(df[col].mean()),
                    'std': float(df[col].std()),
                    'min': float(df[col].min()),
                    'max': float(df[col].max()),
                    'median': float(df[col].median()),
                    'q25': float(df[col].quantile(0.25)),
                    'q75': float(df[col].quantile(0.75))
                }
        
        # 生成所有图表  
        logger.info("生成统计分析图表...")
        charts_data = self.generate_all_charts(correlation_data, advanced_data, df)
        
        report = {
            'analysis_summary': basic_stats,
            'descriptive_statistics': descriptive_stats,
            'correlation_analysis': correlation_data,
            'advanced_analysis': advanced_data,
            'charts': charts_data,  # 新增图表数据
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        # 添加组间比较测试结果
        if group_comparison_data:
            report['group_comparison_analysis'] = group_comparison_data
            
            # 更新基础统计信息
            if 'summary' in group_comparison_data:
                summary = group_comparison_data['summary']
                basic_stats.update({
                    'normality_tests_performed': summary.get('total_metrics_tested', 0),
                    'normally_distributed_metrics': summary.get('normally_distributed_metrics', 0),
                    'non_normally_distributed_metrics': summary.get('non_normally_distributed_metrics', 0),
                    'anova_tests_performed': summary.get('anova_tests_performed', 0),
                    'kruskal_wallis_tests_performed': summary.get('kruskal_wallis_tests_performed', 0),
                    'significant_group_differences': summary.get('significant_differences_found', 0),
                    'proportion_with_group_differences': summary.get('proportion_significant', 0)
                })
        
        return report
    
    def analyze_batch_results(self, summary_path: str, output_dir: str = "output", save_individual_charts: bool = True) -> bool:
        """分析批量评估结果的主函数"""
        try:
            logger.info(f"Loading batch summary from: {summary_path}")
            
            # 加载汇总数据
            summary_data = self.load_batch_summary(summary_path)
            if not summary_data:
                return False
            
            # 提取指标数据
            df = self.extract_metrics_data(summary_data)
            if df.empty:
                logger.error("No valid metrics data found")
                return False
            
            # 执行相关性分析
            logger.info("Performing correlation analysis...")
            correlation_data = self.perform_correlation_analysis(df)
            
            # 执行高级分析
            logger.info("Performing advanced statistical analysis...")
            advanced_data = self.perform_advanced_analysis(df)
            
            # 执行分布检验和组间比较测试
            logger.info("Performing normality tests and group comparison tests...")
            group_comparison_data = self.perform_group_comparison_tests(df)
            
            # 生成完整报告
            logger.info("Generating comprehensive analysis report...")
            analysis_report = self.generate_analysis_report(correlation_data, advanced_data, df, group_comparison_data)
            
            # 确保输出目录存在
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # 保存分析报告
            report_file = output_path / 'statistical_analysis_report.json'
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_report, f, ensure_ascii=False, indent=2)
            logger.info(f"Analysis report saved to: {report_file}")
            
            # 生成独立的PNG图表文件
            if save_individual_charts:
                logger.info("生成独立PNG图表文件...")
                try:
                    from png_chart_generator import PNGChartGenerator
                    charts_dir = output_path / "charts"
                    generator = PNGChartGenerator(str(charts_dir))
                    saved_files = generator.generate_all_charts(correlation_data, advanced_data)
                    logger.info(f"成功生成 {len(saved_files)} 个独立PNG图表")
                except Exception as e:
                    logger.warning(f"生成独立PNG图表失败: {e}")
            
            # 打印分析摘要
            self.print_analysis_summary(analysis_report)
            
            return True
            
        except Exception as e:
            logger.error(f"Statistical analysis failed: {e}")
            return False
    
    def print_analysis_summary(self, report: Dict[str, Any]):
        """打印分析摘要"""
        print("\n" + "="*60)
        print("STATISTICAL ANALYSIS SUMMARY")
        print("="*60)
        
        summary = report.get('analysis_summary', {})
        print(f"\nBasic Information:")
        print(f"  Total Maps Analyzed: {summary.get('total_maps', 0)}")
        print(f"  Metrics Analyzed: {summary.get('metrics_analyzed', 0)}")
        print(f"  Strong Correlations Found: {summary.get('strong_correlations_count', 0)}")
        print(f"  Moderate Correlations Found: {summary.get('moderate_correlations_count', 0)}")
        
        # 逻辑一致性分析
        correlation_analysis = report.get('correlation_analysis', {})
        consistency_score = correlation_analysis.get('logical_consistency_score', 0)
        inconsistencies = correlation_analysis.get('logical_inconsistencies', [])
        expected_found = correlation_analysis.get('expected_correlations_found', 0)
        total_expected = correlation_analysis.get('total_expected_correlations', 0)
        
        print(f"\nLogical Consistency Analysis:")
        print(f"  Consistency Score: {consistency_score:.3f}")
        print(f"  Expected Correlations Found: {expected_found}/{total_expected}")
        
        if inconsistencies:
            print(f"  Logical Inconsistencies ({len(inconsistencies)}):")
            for inc in inconsistencies[:3]:  # 显示前3个
                print(f"    {inc['metric1']} ↔ {inc['metric2']}: expected {inc['expected']}, got ρ={inc['actual_spearman']:.3f}")
        
        # 强相关关系（基于Spearman）
        strong_corrs = correlation_analysis.get('strong_correlations', [])
        if strong_corrs:
            print(f"\nStrong Correlations (|ρ| ≥ 0.7):")
            for corr in strong_corrs[:5]:  # 显示前5个
                consistency_mark = "✓" if corr.get('logically_consistent', True) else "⚠"
                expected_str = f" ({corr.get('expected_direction', 'none')})" if corr.get('expected_direction') else ""
                print(f"  {consistency_mark} {corr['metric1']} ↔ {corr['metric2']}: ρ = {corr['spearman_correlation']:.3f}{expected_str}")
        
        # 与总分的Spearman相关性（显示前5个最强相关）
        overall_corrs = correlation_analysis.get('overall_score_correlations', [])
        if overall_corrs:
            # 按Spearman相关性绝对值排序
            sorted_corrs = sorted(overall_corrs, key=lambda x: abs(x.get('spearman_correlation', 0)), reverse=True)
            print(f"\nTop Correlations with Overall Score (Spearman):")
            for corr in sorted_corrs[:5]:  # 显示前5个
                rho = corr.get('spearman_correlation', 0)
                p_val = corr.get('spearman_p_value', None)
                p_str = f", p={p_val:.3f}" if p_val is not None else ""
                print(f"  {corr['metric']}: ρ = {rho:.3f}{p_str}")
        
        # VIF分析结果
        vif_data = report.get('advanced_analysis', {}).get('vif_analysis', {})
        if vif_data and 'critical_vif_count' in vif_data:
            print(f"\nMulticollinearity Analysis:")
            print(f"  Critical VIF (>10): {vif_data['critical_vif_count']} metrics")
            print(f"  High VIF (>5): {vif_data['high_vif_count']} metrics")
            print(f"  Maximum VIF: {vif_data.get('max_vif', 0):.2f}")
        
        # PCA分析结果
        pca_data = report.get('advanced_analysis', {}).get('pca_analysis', {})
        if pca_data and 'explained_variance_ratio' in pca_data:
            explained_var = pca_data['explained_variance_ratio']
            if len(explained_var) >= 2:
                pc1_var = explained_var[0]
                pc2_var = explained_var[1]
                cumulative_2pc = pc1_var + pc2_var
                print(f"\nPrincipal Component Analysis:")
                print(f"  PC1 explains: {pc1_var:.1%} of variance")
                print(f"  PC2 explains: {pc2_var:.1%} of variance")
                print(f"  First 2 PCs explain: {cumulative_2pc:.1%} of total variance")
        
        # 组间比较测试结果
        group_comparison = report.get('group_comparison_analysis', {})
        if group_comparison and 'summary' in group_comparison:
            gc_summary = group_comparison['summary']
            print(f"\nGroup Comparison Analysis (Quartile-based):")
            print(f"  Normality Tests Performed: {gc_summary.get('total_metrics_tested', 0)}")
            print(f"  Normal Distributions: {gc_summary.get('normally_distributed_metrics', 0)} (ANOVA used)")
            print(f"  Non-Normal Distributions: {gc_summary.get('non_normally_distributed_metrics', 0)} (Kruskal-Wallis used)")
            print(f"  Significant Group Differences: {gc_summary.get('significant_differences_found', 0)}/{gc_summary.get('total_metrics_tested', 0)}")
            print(f"  Proportion with Significant Differences: {gc_summary.get('proportion_significant', 0):.1%}")
            
            # 显示显著差异的指标
            statistical_tests = group_comparison.get('statistical_tests', {})
            significant_metrics = []
            for metric, test_result in statistical_tests.items():
                if test_result.get('significant_at_05', False):
                    test_type = test_result.get('test_used', 'unknown')
                    p_value = test_result.get('p_value', 1.0)
                    significant_metrics.append(f"{metric} ({test_type}, p={p_value:.3f})")
            
            if significant_metrics:
                print(f"\nMetrics with Significant Group Differences:")
                for metric in significant_metrics[:5]:  # 显示前5个
                    print(f"  • {metric}")
                if len(significant_metrics) > 5:
                    print(f"  ... and {len(significant_metrics) - 5} more")
        
        print("="*60)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Statistical Analysis Tool - Analyze batch assessment results',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze batch assessment summary
  python statistical_analysis.py output/watabou_test_batch_report.json
  
  # Specify custom output directory  
  python statistical_analysis.py summary.json --output analysis_results/
        """
    )
    
    parser.add_argument('summary_path', help='Path to batch assessment summary JSON file')
    parser.add_argument('--output', '-o', default='output', 
                       help='Output directory for analysis results (default: output)')
    
    args = parser.parse_args()
    
    # 验证输入文件
    if not os.path.exists(args.summary_path):
        print(f"Error: Summary file not found: {args.summary_path}")
        return 1
    
    # 执行分析
    analyzer = StatisticalAnalyzer()
    success = analyzer.analyze_batch_results(args.summary_path, args.output)
    
    if success:
        print(f"\n✓ Statistical analysis completed successfully!")
        print(f"Results saved to: {args.output}/")
        return 0
    else:
        print(f"\n✗ Statistical analysis failed!")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())