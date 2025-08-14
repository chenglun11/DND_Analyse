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
from scipy.stats import spearmanr
# 可选依赖
try:
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False

try:
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StatisticalAnalyzer:
    """统计分析器"""
    
    def __init__(self):
        # 设置matplotlib后端
        plt.switch_backend('Agg')
        
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
        if 'detailed_results' in summary_data:
            detailed_results = summary_data['detailed_results']
        else:
            detailed_results = summary_data
        
        data_rows = []
        for file_name, result in detailed_results.items():
            if isinstance(result, dict) and 'overall_score' in result:
                row = {'file_name': file_name, 'overall_score': result['overall_score']}
                
                if 'scores' in result:
                    row.update(result['scores'])
                elif 'detailed_scores' in result:
                    row.update(result['detailed_scores'])
                elif 'detailed_metrics' in result:
                    # Extract scores from detailed_metrics
                    for metric_name, metric_data in result['detailed_metrics'].items():
                        if isinstance(metric_data, dict) and 'score' in metric_data:
                            row[metric_name] = metric_data['score']
                
                data_rows.append(row)
        
        if not data_rows:
            logger.warning("No valid data found in summary")
            return pd.DataFrame()
        
        return pd.DataFrame(data_rows)
    
    def calculate_spearman_correlation(self, data: pd.DataFrame) -> Dict[str, Any]:
        """计算Spearman相关性"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        if 'file_name' in numeric_cols:
            numeric_cols.remove('file_name')
        
        if len(numeric_cols) < 2:
            return {'error': 'Not enough numeric columns for correlation'}
        
        numeric_data = data[numeric_cols]
        
        # 计算相关性矩阵和p值
        correlation_matrix = numeric_data.corr(method='spearman')
        
        # 计算p值矩阵
        n = len(numeric_cols)
        p_matrix = np.ones((n, n))
        for i in range(n):
            for j in range(n):
                if i != j:
                    _, p_val = spearmanr(numeric_data.iloc[:, i], numeric_data.iloc[:, j])
                    p_matrix[i, j] = p_val
        
        p_df = pd.DataFrame(p_matrix, index=numeric_cols, columns=numeric_cols)
        
        return {
            'correlation_matrix': correlation_matrix,
            'p_values': p_df,
            'numeric_columns': numeric_cols
        }
    
    def calculate_vif(self, data: pd.DataFrame) -> Dict[str, Any]:
        """计算方差膨胀因子(VIF)"""
        if not HAS_STATSMODELS:
            return {'error': 'statsmodels not available for VIF calculation'}
            
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        if 'file_name' in numeric_cols:
            numeric_cols.remove('file_name')
        
        if len(numeric_cols) < 2:
            return {'error': 'Not enough numeric columns for VIF'}
        
        numeric_data = data[numeric_cols].dropna()
        
        try:
            vif_data = []
            for i, col in enumerate(numeric_cols):
                vif_value = variance_inflation_factor(numeric_data.values, i)
                vif_data.append({'Variable': col, 'VIF': vif_value})
            
            vif_df = pd.DataFrame(vif_data)
            return {
                'vif_dataframe': vif_df,
                'high_vif_variables': vif_df[vif_df['VIF'] > 5]['Variable'].tolist()
            }
        except Exception as e:
            logger.warning(f"VIF calculation failed: {e}")
            return {'error': str(e)}
    
    def perform_pca(self, data: pd.DataFrame) -> Dict[str, Any]:
        """执行主成分分析"""
        if not HAS_SKLEARN:
            return {'error': 'scikit-learn not available for PCA'}
            
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        if 'file_name' in numeric_cols:
            numeric_cols.remove('file_name')
        
        if len(numeric_cols) < 2:
            return {'error': 'Not enough numeric columns for PCA'}
        
        numeric_data = data[numeric_cols].dropna()
        
        try:
            # 标准化数据
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(numeric_data)
            
            # 执行PCA
            pca = PCA()
            pca_result = pca.fit_transform(scaled_data)
            
            # 计算累积方差解释比
            cumulative_variance = np.cumsum(pca.explained_variance_ratio_)
            
            return {
                'explained_variance_ratio': pca.explained_variance_ratio_,
                'cumulative_variance': cumulative_variance,
                'components': pca.components_,
                'feature_names': numeric_cols,
                'n_components_90': np.argmax(cumulative_variance >= 0.9) + 1
            }
        except Exception as e:
            logger.warning(f"PCA failed: {e}")
            return {'error': str(e)}
    
    def perform_clustering(self, correlation_matrix: pd.DataFrame) -> Dict[str, Any]:
        """执行层次聚类分析"""
        try:
            # 将相关性矩阵转换为距离矩阵
            distance_matrix = 1 - np.abs(correlation_matrix)
            
            # 执行层次聚类
            condensed_distances = pdist(distance_matrix)
            linkage_matrix = linkage(condensed_distances, method='ward')
            
            # 生成聚类标签
            clusters = fcluster(linkage_matrix, t=3, criterion='maxclust')
            
            cluster_df = pd.DataFrame({
                'Variable': correlation_matrix.columns,
                'Cluster': clusters
            })
            
            return {
                'linkage_matrix': linkage_matrix,
                'clusters': cluster_df,
                'n_clusters': len(set(clusters))
            }
        except Exception as e:
            logger.warning(f"Clustering failed: {e}")
            return {'error': str(e)}
    
    def generate_charts(self, 
                       correlation_data: Dict[str, Any],
                       vif_data: Dict[str, Any],
                       pca_data: Dict[str, Any],
                       clustering_data: Dict[str, Any],
                       output_dir: str) -> Dict[str, str]:
        """生成可视化图表"""
        charts_info = {}
        output_path = Path(output_dir) / "charts"
        output_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # 1. Spearman相关性热力图
            if 'correlation_matrix' in correlation_data:
                plt.figure(figsize=(12, 10))
                sns.heatmap(correlation_data['correlation_matrix'], 
                           annot=True, cmap='coolwarm', center=0,
                           square=True, fmt='.3f')
                plt.title('Spearman Correlation Heatmap')
                plt.tight_layout()
                chart_path = output_path / "spearman_heatmap.png"
                plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                plt.close()
                charts_info['spearman_heatmap'] = str(chart_path)
            
            # 2. VIF分析图
            if 'vif_dataframe' in vif_data:
                plt.figure(figsize=(10, 6))
                vif_df = vif_data['vif_dataframe']
                bars = plt.bar(vif_df['Variable'], vif_df['VIF'])
                plt.axhline(y=5, color='r', linestyle='--', label='VIF = 5')
                plt.axhline(y=10, color='darkred', linestyle='--', label='VIF = 10')
                plt.xlabel('Variables')
                plt.ylabel('VIF Value')
                plt.title('Variance Inflation Factor (VIF) Analysis')
                plt.xticks(rotation=45, ha='right')
                plt.legend()
                plt.tight_layout()
                chart_path = output_path / "vif_analysis.png"
                plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                plt.close()
                charts_info['vif_analysis'] = str(chart_path)
            
            # 3. PCA碎石图
            if 'explained_variance_ratio' in pca_data:
                plt.figure(figsize=(10, 6))
                plt.plot(range(1, len(pca_data['explained_variance_ratio']) + 1), 
                        pca_data['explained_variance_ratio'], 'bo-')
                plt.plot(range(1, len(pca_data['cumulative_variance']) + 1), 
                        pca_data['cumulative_variance'], 'ro-')
                plt.xlabel('Principal Component')
                plt.ylabel('Explained Variance Ratio')
                plt.title('PCA Scree Plot')
                plt.legend(['Individual', 'Cumulative'])
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                chart_path = output_path / "pca_analysis.png"
                plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                plt.close()
                charts_info['pca_analysis'] = str(chart_path)
            
        except Exception as e:
            logger.warning(f"Chart generation failed: {e}")
        
        return charts_info
    
    def analyze_batch_results(self, summary_path: str, output_dir: str = "output/analysis") -> bool:
        """分析批量评估结果的主函数"""
        logger.info(f"Starting statistical analysis of {summary_path}")
        
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 加载数据
        summary_data = self.load_batch_summary(summary_path)
        if not summary_data:
            return False
        
        # 提取指标数据
        df = self.extract_metrics_data(summary_data)
        if df.empty:
            logger.error("No valid data found for analysis")
            return False
        
        logger.info(f"Loaded {len(df)} records with {len(df.columns)} metrics")
        
        # 执行各项分析
        correlation_data = self.calculate_spearman_correlation(df)
        vif_data = self.calculate_vif(df)
        pca_data = self.perform_pca(df)
        
        clustering_data = {}
        if 'correlation_matrix' in correlation_data:
            clustering_data = self.perform_clustering(correlation_data['correlation_matrix'])
        
        # 生成图表
        charts_info = self.generate_charts(correlation_data, vif_data, pca_data, clustering_data, output_dir)
        
        # 生成分析报告
        report = {
            'summary': {
                'total_samples': len(df),
                'numeric_variables': len(correlation_data.get('numeric_columns', [])),
                'analysis_timestamp': pd.Timestamp.now().isoformat()
            },
            'correlation_analysis': correlation_data if 'error' not in correlation_data else None,
            'vif_analysis': vif_data if 'error' not in vif_data else None,
            'pca_analysis': pca_data if 'error' not in pca_data else None,
            'clustering_analysis': clustering_data if 'error' not in clustering_data else None,
            'charts': charts_info
        }
        
        # 保存报告
        report_path = output_path / "statistical_analysis_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            # 处理numpy数组的序列化
            def numpy_converter(obj):
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, pd.DataFrame):
                    return obj.to_dict('records')
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
            
            json.dump(report, f, ensure_ascii=False, indent=2, default=numpy_converter)
        
        logger.info(f"Statistical analysis completed. Report saved to {report_path}")
        logger.info(f"Charts saved to {output_path / 'charts'}")
        
        return True

def main():
    """主函数 - 提供命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Statistical Analysis of Batch Assessment Results')
    parser.add_argument('summary_path', help='Path to batch summary JSON file')
    parser.add_argument('--output', '-o', default='output/analysis', help='Output directory')
    
    args = parser.parse_args()
    
    analyzer = StatisticalAnalyzer()
    success = analyzer.analyze_batch_results(args.summary_path, args.output)
    
    return 0 if success else 1

if __name__ == '__main__':
    import sys
    sys.exit(main())