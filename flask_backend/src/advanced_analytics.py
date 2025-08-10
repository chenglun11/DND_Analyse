"""
高级数据分析模块 - PCA、聚类分析、VIF冗余检测
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import io
import base64
from typing import List, Dict, Tuple, Optional
from scipy.linalg import eigh
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
import warnings
warnings.filterwarnings('ignore')

# 继承ChartGenerator的基础功能
from .chart_generator import ChartGenerator

class AdvancedAnalytics(ChartGenerator):
    """高级数据分析图表生成器"""
    
    def __init__(self):
        super().__init__()
        
    def calculate_vif(self, correlation_matrix: np.ndarray, metric_names: List[str]) -> Dict:
        """计算方差膨胀因子(VIF)检测多重共线性"""
        try:
            # 计算VIF = 1 / (1 - R²)，其中R²是该变量对其他变量回归的决定系数
            corr_inv = np.linalg.inv(correlation_matrix)
            vif_values = np.diag(corr_inv)
            
            vif_results = []
            for i, (metric, vif) in enumerate(zip(metric_names, vif_values)):
                if vif > 10:
                    level = 'CRITICAL'
                elif vif > 5:
                    level = 'HIGH'
                elif vif > 2.5:
                    level = 'MODERATE'
                else:
                    level = 'LOW'
                    
                vif_results.append({
                    'metric': metric,
                    'vif': float(vif),
                    'level': level
                })
            
            # 按VIF值排序
            vif_results.sort(key=lambda x: x['vif'], reverse=True)
            
            return {
                'vif_results': vif_results,
                'high_vif_count': sum(1 for x in vif_results if x['vif'] > 5),
                'critical_vif_count': sum(1 for x in vif_results if x['vif'] > 10),
                'max_vif': max(x['vif'] for x in vif_results)
            }
            
        except np.linalg.LinAlgError:
            return {
                'vif_results': [],
                'high_vif_count': 0,
                'critical_vif_count': 0,
                'max_vif': 0,
                'error': 'Correlation matrix is not invertible'
            }
    
    def perform_pca(self, data_matrix: np.ndarray, metric_names: List[str]) -> Dict:
        """执行主成分分析"""
        # 标准化数据
        data_mean = np.mean(data_matrix, axis=0)
        data_std = np.std(data_matrix, axis=0, ddof=1)
        data_scaled = (data_matrix - data_mean) / data_std
        
        # 计算协方差矩阵的特征值和特征向量
        cov_matrix = np.cov(data_scaled.T)
        eigenvalues, eigenvectors = eigh(cov_matrix)
        
        # 按特征值降序排列
        idx = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]
        
        # 计算解释方差比
        explained_variance_ratio = eigenvalues / np.sum(eigenvalues)
        cumulative_variance = np.cumsum(explained_variance_ratio)
        
        # 计算主成分载荷（变量与主成分的相关系数）
        loadings = eigenvectors * np.sqrt(eigenvalues)
        
        return {
            'eigenvalues': eigenvalues.tolist(),
            'explained_variance_ratio': explained_variance_ratio.tolist(),
            'cumulative_variance': cumulative_variance.tolist(),
            'loadings': loadings.tolist(),
            'metric_names': metric_names,
            'n_components': len(eigenvalues)
        }
    
    def perform_clustering(self, correlation_matrix: np.ndarray, metric_names: List[str]) -> Dict:
        """执行指标聚类分析"""
        # 计算距离矩阵
        distances = pdist(correlation_matrix, metric='euclidean')
        
        # 层次聚类
        linkage_matrix = linkage(distances, method='ward')
        
        # 生成不同聚类数的结果
        clustering_results = {}
        for k in range(2, min(8, len(metric_names))):
            clusters = fcluster(linkage_matrix, k, criterion='maxclust')
            
            # 组织聚类结果
            cluster_groups = {}
            for i, cluster_id in enumerate(clusters):
                if cluster_id not in cluster_groups:
                    cluster_groups[cluster_id] = []
                cluster_groups[cluster_id].append(metric_names[i])
            
            clustering_results[k] = {
                'clusters': clusters.tolist(),
                'groups': cluster_groups
            }
        
        return {
            'linkage_matrix': linkage_matrix.tolist(),
            'clustering_results': clustering_results,
            'metric_names': metric_names
        }
    
    def generate_vif_chart(self, vif_data: Dict) -> str:
        """生成VIF多重共线性检测图表"""
        if not vif_data['vif_results']:
            # 生成错误信息图表
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'VIF Analysis Failed\nCorrelation matrix not invertible', 
                   ha='center', va='center', transform=ax.transAxes, 
                   fontsize=16, color='red')
            ax.set_title('VIF Multicollinearity Detection', fontsize=16, fontweight='bold')
            ax.axis('off')
            
            image_b64 = self._fig_to_base64(fig)
            plt.close(fig)
            return image_b64
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # 上图：VIF值柱状图
        metrics = [x['metric'] for x in vif_data['vif_results']]
        vif_values = [x['vif'] for x in vif_data['vif_results']]
        colors = []
        
        for vif in vif_values:
            if vif > 10:
                colors.append('#DC2626')  # 红色 - 严重
            elif vif > 5:
                colors.append('#EA580C')  # 橙色 - 高
            elif vif > 2.5:
                colors.append('#D97706')  # 黄色 - 中等  
            else:
                colors.append('#059669')  # 绿色 - 低
        
        bars = ax1.bar(range(len(metrics)), vif_values, color=colors, alpha=0.8)
        
        # 添加阈值线
        ax1.axhline(y=10, color='red', linestyle='--', alpha=0.7, label='Critical (VIF > 10)')
        ax1.axhline(y=5, color='orange', linestyle='--', alpha=0.7, label='High (VIF > 5)')
        ax1.axhline(y=2.5, color='yellow', linestyle='--', alpha=0.7, label='Moderate (VIF > 2.5)')
        
        # 在柱子上添加数值标签
        for i, (bar, vif) in enumerate(zip(bars, vif_values)):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{vif:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
        
        ax1.set_title('Variance Inflation Factor (VIF) Analysis', fontsize=16, fontweight='bold')
        ax1.set_ylabel('VIF Value', fontsize=12)
        ax1.set_xticks(range(len(metrics)))
        ax1.set_xticklabels(metrics, rotation=45, ha='right')
        ax1.legend()
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 下图：多重共线性影响分析饼图
        levels = ['LOW (VIF ≤ 2.5)', 'MODERATE (2.5 < VIF ≤ 5)', 'HIGH (5 < VIF ≤ 10)', 'CRITICAL (VIF > 10)']
        counts = [0, 0, 0, 0]
        
        for result in vif_data['vif_results']:
            vif = result['vif']
            if vif > 10:
                counts[3] += 1
            elif vif > 5:
                counts[2] += 1
            elif vif > 2.5:
                counts[1] += 1
            else:
                counts[0] += 1
        
        # 只显示非零的部分
        non_zero_indices = [i for i, count in enumerate(counts) if count > 0]
        pie_labels = [levels[i] for i in non_zero_indices]
        pie_counts = [counts[i] for i in non_zero_indices]
        pie_colors = ['#059669', '#D97706', '#EA580C', '#DC2626']
        pie_colors = [pie_colors[i] for i in non_zero_indices]
        
        wedges, texts, autotexts = ax2.pie(pie_counts, labels=pie_labels, colors=pie_colors,
                                          autopct='%1.0f', startangle=90, textprops={'fontsize': 10})
        ax2.set_title('Multicollinearity Risk Distribution', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        # 转换为base64
        image_b64 = self._fig_to_base64(fig)
        plt.close(fig)
        
        return image_b64
    
    def generate_pca_chart(self, pca_data: Dict) -> str:
        """生成PCA主成分分析图表"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        n_components = min(len(pca_data['explained_variance_ratio']), 8)
        
        # 图1：碎石图 (Scree Plot)
        components = list(range(1, n_components + 1))
        explained_var = pca_data['explained_variance_ratio'][:n_components]
        
        ax1.plot(components, explained_var, 'bo-', linewidth=2, markersize=8)
        ax1.set_xlabel('Principal Component', fontsize=12)
        ax1.set_ylabel('Explained Variance Ratio', fontsize=12)
        ax1.set_title('Scree Plot - Eigenvalue Analysis', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.set_xticks(components)
        
        # 添加Kaiser准则线 (特征值=1对应的方差比)
        kaiser_line = 1.0 / len(pca_data['metric_names'])
        ax1.axhline(y=kaiser_line, color='red', linestyle='--', alpha=0.7, 
                   label=f'Kaiser Criterion ({kaiser_line:.3f})')
        ax1.legend()
        
        # 图2：累积方差解释图
        cumvar = pca_data['cumulative_variance'][:n_components]
        ax2.bar(components, cumvar, alpha=0.7, color='steelblue')
        ax2.axhline(y=0.8, color='red', linestyle='--', alpha=0.7, label='80% Threshold')
        ax2.axhline(y=0.9, color='orange', linestyle='--', alpha=0.7, label='90% Threshold')
        
        # 在柱子上添加数值标签
        for i, (comp, cum_var) in enumerate(zip(components, cumvar)):
            ax2.text(comp, cum_var + 0.01, f'{cum_var:.2f}', ha='center', va='bottom', fontweight='bold')
        
        ax2.set_xlabel('Number of Components', fontsize=12)
        ax2.set_ylabel('Cumulative Variance Explained', fontsize=12)
        ax2.set_title('Cumulative Variance Explained', fontsize=14, fontweight='bold')
        ax2.set_xticks(components)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 图3：PC1 vs PC2 载荷图
        if len(pca_data['loadings']) >= 2:
            loadings = np.array(pca_data['loadings'])
            pc1_loadings = loadings[:, 0]
            pc2_loadings = loadings[:, 1]
            
            # 绘制载荷向量
            ax3.scatter(pc1_loadings, pc2_loadings, alpha=0.7, s=100, c='red')
            
            # 添加变量标签
            for i, metric in enumerate(pca_data['metric_names']):
                ax3.annotate(metric, (pc1_loadings[i], pc2_loadings[i]), 
                           xytext=(5, 5), textcoords='offset points', fontsize=9)
            
            # 添加坐标轴
            ax3.axhline(y=0, color='k', linestyle='-', alpha=0.3)
            ax3.axvline(x=0, color='k', linestyle='-', alpha=0.3)
            
            pc1_var = pca_data['explained_variance_ratio'][0]
            pc2_var = pca_data['explained_variance_ratio'][1]
            
            ax3.set_xlabel(f'PC1 ({pc1_var:.1%} variance)', fontsize=12)
            ax3.set_ylabel(f'PC2 ({pc2_var:.1%} variance)', fontsize=12)
            ax3.set_title('PCA Loading Plot (PC1 vs PC2)', fontsize=14, fontweight='bold')
            ax3.grid(True, alpha=0.3)
        
        # 图4：主成分贡献分析
        # 显示前3个主成分中每个变量的贡献
        if len(pca_data['loadings']) >= 3:
            loadings = np.array(pca_data['loadings'])
            top_pcs = min(3, loadings.shape[1])
            
            # 计算每个变量在前几个主成分中的平方载荷（贡献）
            contributions = loadings[:, :top_pcs] ** 2
            
            # 创建堆叠柱状图
            bottom = np.zeros(len(pca_data['metric_names']))
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
            
            for pc in range(top_pcs):
                pc_contrib = contributions[:, pc]
                ax4.bar(range(len(pca_data['metric_names'])), pc_contrib, 
                       bottom=bottom, label=f'PC{pc+1}', color=colors[pc], alpha=0.8)
                bottom += pc_contrib
            
            ax4.set_xlabel('Metrics', fontsize=12)
            ax4.set_ylabel('Squared Loadings (Contribution)', fontsize=12)
            ax4.set_title('Variable Contributions to Principal Components', fontsize=14, fontweight='bold')
            ax4.set_xticks(range(len(pca_data['metric_names'])))
            ax4.set_xticklabels(pca_data['metric_names'], rotation=45, ha='right')
            ax4.legend()
            ax4.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        # 转换为base64
        image_b64 = self._fig_to_base64(fig)
        plt.close(fig)
        
        return image_b64
    
    def generate_clustering_chart(self, clustering_data: Dict) -> str:
        """生成聚类分析图表"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # 图1：层次聚类树状图
        linkage_matrix = np.array(clustering_data['linkage_matrix'])
        
        dendrogram(linkage_matrix, 
                  labels=clustering_data['metric_names'],
                  ax=ax1,
                  leaf_rotation=45,
                  leaf_font_size=10)
        
        ax1.set_title('Hierarchical Clustering Dendrogram', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Metrics', fontsize=12)
        ax1.set_ylabel('Distance', fontsize=12)
        
        # 图2：不同聚类数的结果可视化
        clustering_results = clustering_data['clustering_results']
        k_values = sorted(clustering_results.keys())
        
        # 创建颜色映射
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#FFB347']
        
        # 为每个K值绘制聚类结果
        y_positions = np.arange(len(k_values))
        
        for i, k in enumerate(k_values):
            clusters = clustering_results[k]['clusters']
            groups = clustering_results[k]['groups']
            
            # 为每个指标分配颜色
            for j, metric in enumerate(clustering_data['metric_names']):
                cluster_id = clusters[j]
                color = colors[(cluster_id - 1) % len(colors)]
                ax2.scatter(j, i, c=color, s=100, alpha=0.8)
                
                # 添加指标名称
                if i == 0:  # 只在第一行添加标签
                    ax2.text(j, -0.3, metric, rotation=45, ha='right', va='top', fontsize=9)
        
        ax2.set_title('Clustering Results for Different K Values', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Metrics', fontsize=12)
        ax2.set_ylabel('Number of Clusters (K)', fontsize=12)
        ax2.set_yticks(y_positions)
        ax2.set_yticklabels([f'K={k}' for k in k_values])
        ax2.set_xticks(range(len(clustering_data['metric_names'])))
        ax2.set_xticklabels([''] * len(clustering_data['metric_names']))  # 隐藏x轴标签，使用上面的斜标签
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 转换为base64
        image_b64 = self._fig_to_base64(fig)
        plt.close(fig)
        
        return image_b64