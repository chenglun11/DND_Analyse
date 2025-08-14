"""
统一图表生成模块 - 整合所有图表生成功能
包含相关性分析、P值分析、VIF分析、PCA分析、聚类分析等所有图表类型
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import io
import base64
from typing import List, Dict, Tuple, Optional, Any
import matplotlib.font_manager as fm
import warnings
warnings.filterwarnings('ignore')

try:
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'SimHei', 'Arial Unicode MS', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False
except:
    pass

try:
    plt.style.use('seaborn-v0_8')
except:
    pass
    
sns.set_palette("husl")

class UnifiedChartGenerator:
    """统一图表生成器 - 包含所有图表类型"""
    
    def __init__(self):
        self.colors = {
            'primary': '#2892D7',
            'secondary': '#1D70A2', 
            'accent': '#173753',
            'success': '#10B981',
            'warning': '#F59E0B',
            'danger': '#EF4444',
            'info': '#06B6D4'
        }
        
    def _convert_metric_name_to_readable(self, metric_name: str) -> str:
        """将metric名称转换为更易读的格式"""
        if not metric_name:
            return metric_name
            
        # 基础转换：下划线转空格，首字母大写
        readable_name = metric_name.replace('_', ' ').title()
        
        # 处理常见的缩写和术语 - 基于真实metric含义的精确映射
        replacements = {
            'Vif': 'VIF',
            'Pca': 'PCA', 
            'Avg': 'Average',
            'Std': 'Standard Dev',
            'Min': 'Minimum',
            'Max': 'Maximum',
            # Precise metric name mapping - clean English labels
            'Accessibility': 'Accessibility',
            'Degree Variance': 'Node Degree\nVariance', 
            'Door Distribution': 'Door\nDistribution',
            'Dead End Ratio': 'Dead End\nRatio',
            'Key Path Length': 'Critical Path\nLength',
            'Loop Ratio': 'Loop\nRatio',
            'Path Diversity': 'Path\nDiversity',
            'Treasure Monster Distribution': 'Treasure/Monster\nDistribution',
            'Geometric Balance': 'Geometric\nBalance',
            # 其他评分相关
            'Overall Score': 'Overall Quality',
            'Spatial Connectivity Score': 'Spatial Connect',
            'Navigation Score': 'Navigation',
            'Tactical Score': 'Tactical',
            'Reward Score': 'Reward',
            'Balance Score': 'Balance'
        }
        
        # 应用替换规则
        for old, new in replacements.items():
            readable_name = readable_name.replace(old, new)
        
        # 处理长标签的换行（对于网络图等需要紧凑显示的场合）
        if len(readable_name) > 12:
            words = readable_name.split()
            if len(words) >= 2:
                mid = len(words) // 2
                readable_name = ' '.join(words[:mid]) + '\n' + ' '.join(words[mid:])
        
        return readable_name
        
    def _fig_to_base64(self, fig) -> str:
        """将matplotlib图表转换为base64编码的字符串"""
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none', transparent=False)
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        
        graphic = base64.b64encode(image_png)
        return graphic.decode('utf-8')
    
    # ========== 相关性分析图表 ==========
    
    def generate_correlation_heatmap(self, correlation_matrix: List[List[float]], 
                                   metric_names: List[str], correlation_type: str = "Spearman") -> str:
        """生成相关性热力图"""
        # 创建更易读的标签
        readable_metric_names = [self._convert_metric_name_to_readable(name) for name in metric_names]
        
        df_corr = pd.DataFrame(correlation_matrix, 
                             index=readable_metric_names, 
                             columns=readable_metric_names)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        mask = np.triu(np.ones_like(df_corr, dtype=bool), k=1)
        heatmap = sns.heatmap(df_corr, 
                            mask=mask,
                            annot=True, 
                            cmap='RdYlBu_r', 
                            center=0,
                            square=True, 
                            fmt='.3f',
                            cbar_kws={"shrink": .8, "label": f"{correlation_type} Correlation"},
                            annot_kws={'size': 9},
                            ax=ax)
        
        ax.set_title(f'Dungeon Quality Metrics {correlation_type} Correlation Analysis', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('')
        ax.set_ylabel('')
        
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        
        image_b64 = self._fig_to_base64(fig)
        plt.close(fig)
        return image_b64
    
    def generate_spearman_clustering_comprehensive(self, spearman_data: Dict[str, Any], correlation_matrix: List[List[float]], metric_names: List[str]) -> str:
        """生成2x2布局的Spearman聚类综合分析图"""
        try:
            from scipy.cluster.hierarchy import dendrogram
            import numpy as np
            
            # 创建2x2布局
            fig, axes = plt.subplots(2, 2, figsize=(20, 16))
            
            # 转换metric名称为可读格式
            readable_labels = [self._convert_metric_name_to_readable(name).replace('\n', ' ') 
                              for name in metric_names]
            
            # 左上：Spearman相关性热力图
            ax1 = axes[0, 0]
            correlation_array = np.array(correlation_matrix)
            im1 = ax1.imshow(correlation_array, cmap='RdBu_r', aspect='equal', vmin=-1, vmax=1)
            
            # 设置热力图标签和标题
            ax1.set_xticks(range(len(readable_labels)))
            ax1.set_yticks(range(len(readable_labels)))
            ax1.set_xticklabels(readable_labels, rotation=45, ha='right', fontsize=10)
            ax1.set_yticklabels(readable_labels, fontsize=10)
            ax1.set_title('Spearman Correlation Heatmap', fontsize=14, fontweight='bold', pad=20)
            
            # 添加相关系数文本
            for i in range(len(readable_labels)):
                for j in range(len(readable_labels)):
                    corr_val = correlation_array[i, j]
                    color = 'white' if abs(corr_val) > 0.5 else 'black'
                    ax1.text(j, i, f'{corr_val:.2f}', ha='center', va='center', 
                            color=color, fontsize=8, fontweight='bold')
            
            # 添加颜色条
            cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.8)
            cbar1.set_label('Correlation Coefficient', fontsize=10)
            
            # 右上：聚类树状图
            ax2 = axes[0, 1]
            if spearman_data and 'linkage_matrix' in spearman_data:
                dendrogram_result = dendrogram(spearman_data['linkage_matrix'],
                                             labels=readable_labels,
                                             ax=ax2,
                                             orientation='top',
                                             distance_sort='descending',
                                             show_leaf_counts=False,
                                             color_threshold=0.7,
                                             leaf_rotation=45)
                ax2.set_title('Spearman Hierarchical Clustering\n(Distance: 1 - |ρ|)', 
                             fontsize=14, fontweight='bold', pad=20)
                ax2.set_ylabel('Distance (1 - |ρ|)', fontsize=12)
                ax2.tick_params(axis='x', labelsize=10)
            else:
                ax2.text(0.5, 0.5, 'No Clustering Data', ha='center', va='center', 
                        transform=ax2.transAxes, fontsize=16, color='gray')
                ax2.set_title('Spearman Hierarchical Clustering', fontsize=14, fontweight='bold')
                ax2.axis('off')
            
            # 左下：强相关对条形图
            ax3 = axes[1, 0]
            strong_correlations = []
            correlation_values = []
            
            for i in range(len(metric_names)):
                for j in range(i + 1, len(metric_names)):
                    corr_val = abs(correlation_array[i, j])
                    if corr_val >= 0.3:  # 显示中等以上相关性
                        pair_label = f"{readable_labels[i][:15]}...\n× {readable_labels[j][:15]}..."
                        strong_correlations.append(pair_label)
                        correlation_values.append(corr_val)
            
            # 按相关性强度排序
            if strong_correlations:
                sorted_pairs = sorted(zip(strong_correlations, correlation_values), 
                                    key=lambda x: x[1], reverse=True)
                strong_correlations, correlation_values = zip(*sorted_pairs[:10])  # 显示前10个
                
                colors = ['#d62728' if val >= 0.7 else '#ff7f0e' if val >= 0.5 else '#2ca02c' 
                         for val in correlation_values]
                bars = ax3.barh(range(len(strong_correlations)), correlation_values, color=colors, alpha=0.8)
                
                # 添加数值标签
                for i, (bar, val) in enumerate(zip(bars, correlation_values)):
                    ax3.text(val + 0.01, bar.get_y() + bar.get_height()/2, 
                            f'{val:.3f}', va='center', fontsize=9, fontweight='bold')
                
                ax3.set_yticks(range(len(strong_correlations)))
                ax3.set_yticklabels(strong_correlations, fontsize=9)
                ax3.set_xlabel('|Spearman ρ|', fontsize=12)
                ax3.set_title('Strong Correlations (|ρ| ≥ 0.3)', fontsize=14, fontweight='bold')
                ax3.grid(True, alpha=0.3, axis='x')
                ax3.set_xlim(0, 1)
            else:
                ax3.text(0.5, 0.5, 'No Strong Correlations Found', ha='center', va='center', 
                        transform=ax3.transAxes, fontsize=16, color='gray')
                ax3.set_title('Strong Correlations', fontsize=14, fontweight='bold')
            
            # 右下：相关性分布直方图
            ax4 = axes[1, 1]
            # 提取上三角矩阵的相关系数（排除对角线）
            upper_triangle = []
            for i in range(len(correlation_array)):
                for j in range(i + 1, len(correlation_array)):
                    upper_triangle.append(correlation_array[i, j])
            
            if upper_triangle:
                ax4.hist(upper_triangle, bins=20, alpha=0.7, color=self.colors['primary'], edgecolor='black')
                ax4.axvline(np.mean(upper_triangle), color='red', linestyle='--', 
                           label=f'Mean: {np.mean(upper_triangle):.3f}')
                ax4.axvline(0, color='black', linestyle='-', alpha=0.5)
                ax4.set_xlabel('Spearman Correlation Coefficient (ρ)', fontsize=12)
                ax4.set_ylabel('Frequency', fontsize=12)
                ax4.set_title('Distribution of Spearman Correlations', fontsize=14, fontweight='bold')
                ax4.legend()
                ax4.grid(True, alpha=0.3)
            else:
                ax4.text(0.5, 0.5, 'No Correlation Data', ha='center', va='center', 
                        transform=ax4.transAxes, fontsize=16, color='gray')
                ax4.set_title('Correlation Distribution', fontsize=14, fontweight='bold')
            
            plt.tight_layout(pad=3.0)
            
            image_b64 = self._fig_to_base64(fig)
            plt.close(fig)
            return image_b64
            
        except ImportError:
            # fallback to simple clustering analysis
            return self.generate_clustering_analysis(spearman_data)
    
    def generate_scatter_plot(self, correlation_matrix: List[List[float]], 
                            metric_names: List[str]) -> str:
        """生成相关性散点图"""
        correlations = []
        pairs = []
        
        for i in range(len(metric_names)):
            for j in range(i + 1, len(metric_names)):
                correlations.append(correlation_matrix[i][j])
                pairs.append(f"{metric_names[i]} × {metric_names[j]}")
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        colors = []
        sizes = []
        for corr in correlations:
            abs_corr = abs(corr)
            if abs_corr > 0.7:
                colors.append('#EF4444')
                sizes.append(100 + abs_corr * 100)
            elif abs_corr > 0.3:
                colors.append('#F59E0B')
                sizes.append(80 + abs_corr * 80)
            else:
                colors.append('#6B7280')
                sizes.append(50 + abs_corr * 50)
        
        scatter = ax.scatter(range(len(correlations)), correlations, 
                           c=colors, s=sizes, alpha=0.7, edgecolors='white', linewidth=1)
        
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax.axhline(y=0.7, color='red', linestyle='--', alpha=0.5, label='Strong Correlation (r=0.7)')
        ax.axhline(y=0.3, color='orange', linestyle='--', alpha=0.5, label='Moderate Correlation (r=0.3)')
        ax.axhline(y=-0.3, color='orange', linestyle='--', alpha=0.5)
        ax.axhline(y=-0.7, color='red', linestyle='--', alpha=0.5)
        
        ax.set_title('Metric Correlation Distribution', fontsize=16, fontweight='bold')
        ax.set_xlabel('Metric Pairs', fontsize=12)
        ax.set_ylabel('Correlation Coefficient', fontsize=12)
        ax.set_ylim(-1.1, 1.1)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        step = max(1, len(pairs) // 10)
        selected_indices = range(0, len(pairs), step)
        ax.set_xticks(selected_indices)
        ax.set_xticklabels([pairs[i][:20] + '...' if len(pairs[i]) > 20 else pairs[i] 
                           for i in selected_indices], rotation=45, ha='right')
        
        plt.tight_layout()
        
        image_b64 = self._fig_to_base64(fig)
        plt.close(fig)
        return image_b64
    
    def generate_spearman_clustering_comprehensive(self, spearman_data: Dict[str, Any], correlation_matrix: List[List[float]], metric_names: List[str]) -> str:
        """生成2x2布局的Spearman聚类综合分析图"""
        try:
            from scipy.cluster.hierarchy import dendrogram
            import numpy as np
            
            # 创建2x2布局
            fig, axes = plt.subplots(2, 2, figsize=(20, 16))
            
            # 转换metric名称为可读格式
            readable_labels = [self._convert_metric_name_to_readable(name).replace('\n', ' ') 
                              for name in metric_names]
            
            # 左上：Spearman相关性热力图
            ax1 = axes[0, 0]
            correlation_array = np.array(correlation_matrix)
            im1 = ax1.imshow(correlation_array, cmap='RdBu_r', aspect='equal', vmin=-1, vmax=1)
            
            # 设置热力图标签和标题
            ax1.set_xticks(range(len(readable_labels)))
            ax1.set_yticks(range(len(readable_labels)))
            ax1.set_xticklabels(readable_labels, rotation=45, ha='right', fontsize=10)
            ax1.set_yticklabels(readable_labels, fontsize=10)
            ax1.set_title('Spearman Correlation Heatmap', fontsize=14, fontweight='bold', pad=20)
            
            # 添加相关系数文本
            for i in range(len(readable_labels)):
                for j in range(len(readable_labels)):
                    corr_val = correlation_array[i, j]
                    color = 'white' if abs(corr_val) > 0.5 else 'black'
                    ax1.text(j, i, f'{corr_val:.2f}', ha='center', va='center', 
                            color=color, fontsize=8, fontweight='bold')
            
            # 添加颜色条
            cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.8)
            cbar1.set_label('Correlation Coefficient', fontsize=10)
            
            # 右上：聚类树状图
            ax2 = axes[0, 1]
            if spearman_data and 'linkage_matrix' in spearman_data:
                dendrogram_result = dendrogram(spearman_data['linkage_matrix'],
                                             labels=readable_labels,
                                             ax=ax2,
                                             orientation='top',
                                             distance_sort='descending',
                                             show_leaf_counts=False,
                                             color_threshold=0.7,
                                             leaf_rotation=45)
                ax2.set_title('Spearman Hierarchical Clustering\n(Distance: 1 - |ρ|)', 
                             fontsize=14, fontweight='bold', pad=20)
                ax2.set_ylabel('Distance (1 - |ρ|)', fontsize=12)
                ax2.tick_params(axis='x', labelsize=10)
            else:
                ax2.text(0.5, 0.5, 'No Clustering Data', ha='center', va='center', 
                        transform=ax2.transAxes, fontsize=16, color='gray')
                ax2.set_title('Spearman Hierarchical Clustering', fontsize=14, fontweight='bold')
                ax2.axis('off')
            
            # 左下：强相关对条形图
            ax3 = axes[1, 0]
            strong_correlations = []
            correlation_values = []
            
            for i in range(len(metric_names)):
                for j in range(i + 1, len(metric_names)):
                    corr_val = abs(correlation_array[i, j])
                    if corr_val >= 0.3:  # 显示中等以上相关性
                        pair_label = f"{readable_labels[i][:15]}...\n× {readable_labels[j][:15]}..."
                        strong_correlations.append(pair_label)
                        correlation_values.append(corr_val)
            
            # 按相关性强度排序
            if strong_correlations:
                sorted_pairs = sorted(zip(strong_correlations, correlation_values), 
                                    key=lambda x: x[1], reverse=True)
                strong_correlations, correlation_values = zip(*sorted_pairs[:10])  # 显示前10个
                
                colors = ['#d62728' if val >= 0.7 else '#ff7f0e' if val >= 0.5 else '#2ca02c' 
                         for val in correlation_values]
                bars = ax3.barh(range(len(strong_correlations)), correlation_values, color=colors, alpha=0.8)
                
                # 添加数值标签
                for i, (bar, val) in enumerate(zip(bars, correlation_values)):
                    ax3.text(val + 0.01, bar.get_y() + bar.get_height()/2, 
                            f'{val:.3f}', va='center', fontsize=9, fontweight='bold')
                
                ax3.set_yticks(range(len(strong_correlations)))
                ax3.set_yticklabels(strong_correlations, fontsize=9)
                ax3.set_xlabel('|Spearman ρ|', fontsize=12)
                ax3.set_title('Strong Correlations (|ρ| ≥ 0.3)', fontsize=14, fontweight='bold')
                ax3.grid(True, alpha=0.3, axis='x')
                ax3.set_xlim(0, 1)
            else:
                ax3.text(0.5, 0.5, 'No Strong Correlations Found', ha='center', va='center', 
                        transform=ax3.transAxes, fontsize=16, color='gray')
                ax3.set_title('Strong Correlations', fontsize=14, fontweight='bold')
            
            # 右下：相关性分布直方图
            ax4 = axes[1, 1]
            # 提取上三角矩阵的相关系数（排除对角线）
            upper_triangle = []
            for i in range(len(correlation_array)):
                for j in range(i + 1, len(correlation_array)):
                    upper_triangle.append(correlation_array[i, j])
            
            if upper_triangle:
                ax4.hist(upper_triangle, bins=20, alpha=0.7, color=self.colors['primary'], edgecolor='black')
                ax4.axvline(np.mean(upper_triangle), color='red', linestyle='--', 
                           label=f'Mean: {np.mean(upper_triangle):.3f}')
                ax4.axvline(0, color='black', linestyle='-', alpha=0.5)
                ax4.set_xlabel('Spearman Correlation Coefficient (ρ)', fontsize=12)
                ax4.set_ylabel('Frequency', fontsize=12)
                ax4.set_title('Distribution of Spearman Correlations', fontsize=14, fontweight='bold')
                ax4.legend()
                ax4.grid(True, alpha=0.3)
            else:
                ax4.text(0.5, 0.5, 'No Correlation Data', ha='center', va='center', 
                        transform=ax4.transAxes, fontsize=16, color='gray')
                ax4.set_title('Correlation Distribution', fontsize=14, fontweight='bold')
            
            plt.tight_layout(pad=3.0)
            
            image_b64 = self._fig_to_base64(fig)
            plt.close(fig)
            return image_b64
            
        except ImportError:
            # fallback to simple clustering analysis
            return self.generate_clustering_analysis(spearman_data)
    
    def generate_network_graph(self, correlation_matrix: List[List[float]], 
                             metric_names: List[str]) -> str:
        """生成网络关系图"""
        try:
            import networkx as nx
        except ImportError:
            return self.generate_radar_chart(correlation_matrix, metric_names)
        
        G = nx.Graph()
        
        for name in metric_names:
            G.add_node(name)
        
        for i in range(len(metric_names)):
            for j in range(i + 1, len(metric_names)):
                corr = abs(correlation_matrix[i][j])
                if corr > 0.3:
                    G.add_edge(metric_names[i], metric_names[j], weight=corr)
        
        fig, ax = plt.subplots(figsize=(12, 10))
        
        pos = nx.spring_layout(G, k=3, iterations=50)
        
        edges = G.edges(data=True)
        for (u, v, d) in edges:
            weight = d['weight']
            if weight > 0.7:
                color = '#EF4444'
                width = 3
                alpha = 0.8
            elif weight > 0.5:
                color = '#F59E0B'
                width = 2
                alpha = 0.6
            else:
                color = '#6B7280'
                width = 1
                alpha = 0.4
            
            nx.draw_networkx_edges(G, pos, [(u, v)], edge_color=color, 
                                 width=width, alpha=alpha, ax=ax)
        
        nx.draw_networkx_nodes(G, pos, node_color=self.colors['primary'], 
                             node_size=1000, alpha=0.8, ax=ax)
        
        # 创建更易读的标签
        readable_labels = {}
        for name in G.nodes():
            readable_name = self._convert_metric_name_to_readable(name)
            readable_labels[name] = readable_name
            
        nx.draw_networkx_labels(G, pos, labels=readable_labels, font_size=8, font_color='white', 
                              font_weight='bold', ax=ax)
        
        ax.set_title('Metric Relationship Network', fontsize=16, fontweight='bold')
        ax.axis('off')
        
        legend_elements = [
            plt.Line2D([0], [0], color='#EF4444', lw=3, label='Strong Correlation (r>0.7)'),
            plt.Line2D([0], [0], color='#F59E0B', lw=2, label='Moderate-Strong (r>0.5)'),
            plt.Line2D([0], [0], color='#6B7280', lw=1, label='Moderate Correlation (r>0.3)')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        
        image_b64 = self._fig_to_base64(fig)
        plt.close(fig)
        return image_b64
    
    def generate_spearman_clustering_comprehensive(self, spearman_data: Dict[str, Any], correlation_matrix: List[List[float]], metric_names: List[str]) -> str:
        """生成2x2布局的Spearman聚类综合分析图"""
        try:
            from scipy.cluster.hierarchy import dendrogram
            import numpy as np
            
            # 创建2x2布局
            fig, axes = plt.subplots(2, 2, figsize=(20, 16))
            
            # 转换metric名称为可读格式
            readable_labels = [self._convert_metric_name_to_readable(name).replace('\n', ' ') 
                              for name in metric_names]
            
            # 左上：Spearman相关性热力图
            ax1 = axes[0, 0]
            correlation_array = np.array(correlation_matrix)
            im1 = ax1.imshow(correlation_array, cmap='RdBu_r', aspect='equal', vmin=-1, vmax=1)
            
            # 设置热力图标签和标题
            ax1.set_xticks(range(len(readable_labels)))
            ax1.set_yticks(range(len(readable_labels)))
            ax1.set_xticklabels(readable_labels, rotation=45, ha='right', fontsize=10)
            ax1.set_yticklabels(readable_labels, fontsize=10)
            ax1.set_title('Spearman Correlation Heatmap', fontsize=14, fontweight='bold', pad=20)
            
            # 添加相关系数文本
            for i in range(len(readable_labels)):
                for j in range(len(readable_labels)):
                    corr_val = correlation_array[i, j]
                    color = 'white' if abs(corr_val) > 0.5 else 'black'
                    ax1.text(j, i, f'{corr_val:.2f}', ha='center', va='center', 
                            color=color, fontsize=8, fontweight='bold')
            
            # 添加颜色条
            cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.8)
            cbar1.set_label('Correlation Coefficient', fontsize=10)
            
            # 右上：聚类树状图
            ax2 = axes[0, 1]
            if spearman_data and 'linkage_matrix' in spearman_data:
                dendrogram_result = dendrogram(spearman_data['linkage_matrix'],
                                             labels=readable_labels,
                                             ax=ax2,
                                             orientation='top',
                                             distance_sort='descending',
                                             show_leaf_counts=False,
                                             color_threshold=0.7,
                                             leaf_rotation=45)
                ax2.set_title('Spearman Hierarchical Clustering\n(Distance: 1 - |ρ|)', 
                             fontsize=14, fontweight='bold', pad=20)
                ax2.set_ylabel('Distance (1 - |ρ|)', fontsize=12)
                ax2.tick_params(axis='x', labelsize=10)
            else:
                ax2.text(0.5, 0.5, 'No Clustering Data', ha='center', va='center', 
                        transform=ax2.transAxes, fontsize=16, color='gray')
                ax2.set_title('Spearman Hierarchical Clustering', fontsize=14, fontweight='bold')
                ax2.axis('off')
            
            # 左下：强相关对条形图
            ax3 = axes[1, 0]
            strong_correlations = []
            correlation_values = []
            
            for i in range(len(metric_names)):
                for j in range(i + 1, len(metric_names)):
                    corr_val = abs(correlation_array[i, j])
                    if corr_val >= 0.3:  # 显示中等以上相关性
                        pair_label = f"{readable_labels[i][:15]}...\n× {readable_labels[j][:15]}..."
                        strong_correlations.append(pair_label)
                        correlation_values.append(corr_val)
            
            # 按相关性强度排序
            if strong_correlations:
                sorted_pairs = sorted(zip(strong_correlations, correlation_values), 
                                    key=lambda x: x[1], reverse=True)
                strong_correlations, correlation_values = zip(*sorted_pairs[:10])  # 显示前10个
                
                colors = ['#d62728' if val >= 0.7 else '#ff7f0e' if val >= 0.5 else '#2ca02c' 
                         for val in correlation_values]
                bars = ax3.barh(range(len(strong_correlations)), correlation_values, color=colors, alpha=0.8)
                
                # 添加数值标签
                for i, (bar, val) in enumerate(zip(bars, correlation_values)):
                    ax3.text(val + 0.01, bar.get_y() + bar.get_height()/2, 
                            f'{val:.3f}', va='center', fontsize=9, fontweight='bold')
                
                ax3.set_yticks(range(len(strong_correlations)))
                ax3.set_yticklabels(strong_correlations, fontsize=9)
                ax3.set_xlabel('|Spearman ρ|', fontsize=12)
                ax3.set_title('Strong Correlations (|ρ| ≥ 0.3)', fontsize=14, fontweight='bold')
                ax3.grid(True, alpha=0.3, axis='x')
                ax3.set_xlim(0, 1)
            else:
                ax3.text(0.5, 0.5, 'No Strong Correlations Found', ha='center', va='center', 
                        transform=ax3.transAxes, fontsize=16, color='gray')
                ax3.set_title('Strong Correlations', fontsize=14, fontweight='bold')
            
            # 右下：相关性分布直方图
            ax4 = axes[1, 1]
            # 提取上三角矩阵的相关系数（排除对角线）
            upper_triangle = []
            for i in range(len(correlation_array)):
                for j in range(i + 1, len(correlation_array)):
                    upper_triangle.append(correlation_array[i, j])
            
            if upper_triangle:
                ax4.hist(upper_triangle, bins=20, alpha=0.7, color=self.colors['primary'], edgecolor='black')
                ax4.axvline(np.mean(upper_triangle), color='red', linestyle='--', 
                           label=f'Mean: {np.mean(upper_triangle):.3f}')
                ax4.axvline(0, color='black', linestyle='-', alpha=0.5)
                ax4.set_xlabel('Spearman Correlation Coefficient (ρ)', fontsize=12)
                ax4.set_ylabel('Frequency', fontsize=12)
                ax4.set_title('Distribution of Spearman Correlations', fontsize=14, fontweight='bold')
                ax4.legend()
                ax4.grid(True, alpha=0.3)
            else:
                ax4.text(0.5, 0.5, 'No Correlation Data', ha='center', va='center', 
                        transform=ax4.transAxes, fontsize=16, color='gray')
                ax4.set_title('Correlation Distribution', fontsize=14, fontweight='bold')
            
            plt.tight_layout(pad=3.0)
            
            image_b64 = self._fig_to_base64(fig)
            plt.close(fig)
            return image_b64
            
        except ImportError:
            # fallback to simple clustering analysis
            return self.generate_clustering_analysis(spearman_data)
    
    def generate_radar_chart(self, correlation_matrix: List[List[float]], 
                           metric_names: List[str]) -> str:
        """生成雷达图"""
        avg_correlations = []
        for i in range(len(metric_names)):
            correlations = [abs(correlation_matrix[i][j]) for j in range(len(metric_names)) if i != j]
            avg_correlations.append(np.mean(correlations))
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        angles = np.linspace(0, 2 * np.pi, len(metric_names), endpoint=False).tolist()
        angles += angles[:1]
        
        values = avg_correlations + avg_correlations[:1]
        
        ax.plot(angles, values, color=self.colors['primary'], linewidth=2)
        ax.fill(angles, values, color=self.colors['primary'], alpha=0.3)
        
        # 创建更易读的标签
        readable_metric_names = [self._convert_metric_name_to_readable(name) for name in metric_names]
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(readable_metric_names, fontsize=10)
        
        ax.set_ylim(0, 1)
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=8)
        ax.grid(True)
        
        ax.set_title('Metric Average Correlation Radar Chart', fontsize=16, fontweight='bold', pad=30)
        
        plt.tight_layout()
        
        image_b64 = self._fig_to_base64(fig)
        plt.close(fig)
        return image_b64
    
    def generate_spearman_clustering_comprehensive(self, spearman_data: Dict[str, Any], correlation_matrix: List[List[float]], metric_names: List[str]) -> str:
        """生成2x2布局的Spearman聚类综合分析图"""
        try:
            from scipy.cluster.hierarchy import dendrogram
            import numpy as np
            
            # 创建2x2布局
            fig, axes = plt.subplots(2, 2, figsize=(20, 16))
            
            # 转换metric名称为可读格式
            readable_labels = [self._convert_metric_name_to_readable(name).replace('\n', ' ') 
                              for name in metric_names]
            
            # 左上：Spearman相关性热力图
            ax1 = axes[0, 0]
            correlation_array = np.array(correlation_matrix)
            im1 = ax1.imshow(correlation_array, cmap='RdBu_r', aspect='equal', vmin=-1, vmax=1)
            
            # 设置热力图标签和标题
            ax1.set_xticks(range(len(readable_labels)))
            ax1.set_yticks(range(len(readable_labels)))
            ax1.set_xticklabels(readable_labels, rotation=45, ha='right', fontsize=10)
            ax1.set_yticklabels(readable_labels, fontsize=10)
            ax1.set_title('Spearman Correlation Heatmap', fontsize=14, fontweight='bold', pad=20)
            
            # 添加相关系数文本
            for i in range(len(readable_labels)):
                for j in range(len(readable_labels)):
                    corr_val = correlation_array[i, j]
                    color = 'white' if abs(corr_val) > 0.5 else 'black'
                    ax1.text(j, i, f'{corr_val:.2f}', ha='center', va='center', 
                            color=color, fontsize=8, fontweight='bold')
            
            # 添加颜色条
            cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.8)
            cbar1.set_label('Correlation Coefficient', fontsize=10)
            
            # 右上：聚类树状图
            ax2 = axes[0, 1]
            if spearman_data and 'linkage_matrix' in spearman_data:
                dendrogram_result = dendrogram(spearman_data['linkage_matrix'],
                                             labels=readable_labels,
                                             ax=ax2,
                                             orientation='top',
                                             distance_sort='descending',
                                             show_leaf_counts=False,
                                             color_threshold=0.7,
                                             leaf_rotation=45)
                ax2.set_title('Spearman Hierarchical Clustering\n(Distance: 1 - |ρ|)', 
                             fontsize=14, fontweight='bold', pad=20)
                ax2.set_ylabel('Distance (1 - |ρ|)', fontsize=12)
                ax2.tick_params(axis='x', labelsize=10)
            else:
                ax2.text(0.5, 0.5, 'No Clustering Data', ha='center', va='center', 
                        transform=ax2.transAxes, fontsize=16, color='gray')
                ax2.set_title('Spearman Hierarchical Clustering', fontsize=14, fontweight='bold')
                ax2.axis('off')
            
            # 左下：强相关对条形图
            ax3 = axes[1, 0]
            strong_correlations = []
            correlation_values = []
            
            for i in range(len(metric_names)):
                for j in range(i + 1, len(metric_names)):
                    corr_val = abs(correlation_array[i, j])
                    if corr_val >= 0.3:  # 显示中等以上相关性
                        pair_label = f"{readable_labels[i][:15]}...\n× {readable_labels[j][:15]}..."
                        strong_correlations.append(pair_label)
                        correlation_values.append(corr_val)
            
            # 按相关性强度排序
            if strong_correlations:
                sorted_pairs = sorted(zip(strong_correlations, correlation_values), 
                                    key=lambda x: x[1], reverse=True)
                strong_correlations, correlation_values = zip(*sorted_pairs[:10])  # 显示前10个
                
                colors = ['#d62728' if val >= 0.7 else '#ff7f0e' if val >= 0.5 else '#2ca02c' 
                         for val in correlation_values]
                bars = ax3.barh(range(len(strong_correlations)), correlation_values, color=colors, alpha=0.8)
                
                # 添加数值标签
                for i, (bar, val) in enumerate(zip(bars, correlation_values)):
                    ax3.text(val + 0.01, bar.get_y() + bar.get_height()/2, 
                            f'{val:.3f}', va='center', fontsize=9, fontweight='bold')
                
                ax3.set_yticks(range(len(strong_correlations)))
                ax3.set_yticklabels(strong_correlations, fontsize=9)
                ax3.set_xlabel('|Spearman ρ|', fontsize=12)
                ax3.set_title('Strong Correlations (|ρ| ≥ 0.3)', fontsize=14, fontweight='bold')
                ax3.grid(True, alpha=0.3, axis='x')
                ax3.set_xlim(0, 1)
            else:
                ax3.text(0.5, 0.5, 'No Strong Correlations Found', ha='center', va='center', 
                        transform=ax3.transAxes, fontsize=16, color='gray')
                ax3.set_title('Strong Correlations', fontsize=14, fontweight='bold')
            
            # 右下：相关性分布直方图
            ax4 = axes[1, 1]
            # 提取上三角矩阵的相关系数（排除对角线）
            upper_triangle = []
            for i in range(len(correlation_array)):
                for j in range(i + 1, len(correlation_array)):
                    upper_triangle.append(correlation_array[i, j])
            
            if upper_triangle:
                ax4.hist(upper_triangle, bins=20, alpha=0.7, color=self.colors['primary'], edgecolor='black')
                ax4.axvline(np.mean(upper_triangle), color='red', linestyle='--', 
                           label=f'Mean: {np.mean(upper_triangle):.3f}')
                ax4.axvline(0, color='black', linestyle='-', alpha=0.5)
                ax4.set_xlabel('Spearman Correlation Coefficient (ρ)', fontsize=12)
                ax4.set_ylabel('Frequency', fontsize=12)
                ax4.set_title('Distribution of Spearman Correlations', fontsize=14, fontweight='bold')
                ax4.legend()
                ax4.grid(True, alpha=0.3)
            else:
                ax4.text(0.5, 0.5, 'No Correlation Data', ha='center', va='center', 
                        transform=ax4.transAxes, fontsize=16, color='gray')
                ax4.set_title('Correlation Distribution', fontsize=14, fontweight='bold')
            
            plt.tight_layout(pad=3.0)
            
            image_b64 = self._fig_to_base64(fig)
            plt.close(fig)
            return image_b64
            
        except ImportError:
            # fallback to simple clustering analysis
            return self.generate_clustering_analysis(spearman_data)
    
    def generate_bar_chart(self, correlation_pairs: List[Dict], title: str) -> str:
        """生成相关性柱状图"""
        if not correlation_pairs:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No Data Available', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=16, color='gray')
            ax.set_title(title, fontsize=16, fontweight='bold')
            ax.axis('off')
            
            image_b64 = self._fig_to_base64(fig)
            plt.close(fig)
            return image_b64
        
        pairs = [pair['pair'] for pair in correlation_pairs]
        values = [pair['value'] for pair in correlation_pairs]
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        colors = []
        for val in values:
            if abs(val) > 0.7:
                colors.append('#EF4444')
            elif abs(val) > 0.5:
                colors.append('#F59E0B')
            else:
                colors.append(self.colors['primary'])
        
        bars = ax.bar(range(len(pairs)), values, color=colors, alpha=0.8, edgecolor='white')
        
        for i, (bar, val) in enumerate(zip(bars, values)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f'{val:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_ylabel('Correlation Coefficient', fontsize=12)
        ax.set_xlabel('Metric Pairs', fontsize=12)
        
        ax.set_xticks(range(len(pairs)))
        ax.set_xticklabels([pair.replace(' ↔ ', '\n×\n') for pair in pairs], 
                          rotation=45, ha='right', fontsize=9)
        
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_axisbelow(True)
        ax.set_ylim(0, max(values) * 1.1)
        
        plt.tight_layout()
        
        image_b64 = self._fig_to_base64(fig)
        plt.close(fig)
        return image_b64
    
    def generate_spearman_clustering_comprehensive(self, spearman_data: Dict[str, Any], correlation_matrix: List[List[float]], metric_names: List[str]) -> str:
        """生成2x2布局的Spearman聚类综合分析图"""
        try:
            from scipy.cluster.hierarchy import dendrogram
            import numpy as np
            
            # 创建2x2布局
            fig, axes = plt.subplots(2, 2, figsize=(20, 16))
            
            # 转换metric名称为可读格式
            readable_labels = [self._convert_metric_name_to_readable(name).replace('\n', ' ') 
                              for name in metric_names]
            
            # 左上：Spearman相关性热力图
            ax1 = axes[0, 0]
            correlation_array = np.array(correlation_matrix)
            im1 = ax1.imshow(correlation_array, cmap='RdBu_r', aspect='equal', vmin=-1, vmax=1)
            
            # 设置热力图标签和标题
            ax1.set_xticks(range(len(readable_labels)))
            ax1.set_yticks(range(len(readable_labels)))
            ax1.set_xticklabels(readable_labels, rotation=45, ha='right', fontsize=10)
            ax1.set_yticklabels(readable_labels, fontsize=10)
            ax1.set_title('Spearman Correlation Heatmap', fontsize=14, fontweight='bold', pad=20)
            
            # 添加相关系数文本
            for i in range(len(readable_labels)):
                for j in range(len(readable_labels)):
                    corr_val = correlation_array[i, j]
                    color = 'white' if abs(corr_val) > 0.5 else 'black'
                    ax1.text(j, i, f'{corr_val:.2f}', ha='center', va='center', 
                            color=color, fontsize=8, fontweight='bold')
            
            # 添加颜色条
            cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.8)
            cbar1.set_label('Correlation Coefficient', fontsize=10)
            
            # 右上：聚类树状图
            ax2 = axes[0, 1]
            if spearman_data and 'linkage_matrix' in spearman_data:
                dendrogram_result = dendrogram(spearman_data['linkage_matrix'],
                                             labels=readable_labels,
                                             ax=ax2,
                                             orientation='top',
                                             distance_sort='descending',
                                             show_leaf_counts=False,
                                             color_threshold=0.7,
                                             leaf_rotation=45)
                ax2.set_title('Spearman Hierarchical Clustering\n(Distance: 1 - |ρ|)', 
                             fontsize=14, fontweight='bold', pad=20)
                ax2.set_ylabel('Distance (1 - |ρ|)', fontsize=12)
                ax2.tick_params(axis='x', labelsize=10)
            else:
                ax2.text(0.5, 0.5, 'No Clustering Data', ha='center', va='center', 
                        transform=ax2.transAxes, fontsize=16, color='gray')
                ax2.set_title('Spearman Hierarchical Clustering', fontsize=14, fontweight='bold')
                ax2.axis('off')
            
            # 左下：强相关对条形图
            ax3 = axes[1, 0]
            strong_correlations = []
            correlation_values = []
            
            for i in range(len(metric_names)):
                for j in range(i + 1, len(metric_names)):
                    corr_val = abs(correlation_array[i, j])
                    if corr_val >= 0.3:  # 显示中等以上相关性
                        pair_label = f"{readable_labels[i][:15]}...\n× {readable_labels[j][:15]}..."
                        strong_correlations.append(pair_label)
                        correlation_values.append(corr_val)
            
            # 按相关性强度排序
            if strong_correlations:
                sorted_pairs = sorted(zip(strong_correlations, correlation_values), 
                                    key=lambda x: x[1], reverse=True)
                strong_correlations, correlation_values = zip(*sorted_pairs[:10])  # 显示前10个
                
                colors = ['#d62728' if val >= 0.7 else '#ff7f0e' if val >= 0.5 else '#2ca02c' 
                         for val in correlation_values]
                bars = ax3.barh(range(len(strong_correlations)), correlation_values, color=colors, alpha=0.8)
                
                # 添加数值标签
                for i, (bar, val) in enumerate(zip(bars, correlation_values)):
                    ax3.text(val + 0.01, bar.get_y() + bar.get_height()/2, 
                            f'{val:.3f}', va='center', fontsize=9, fontweight='bold')
                
                ax3.set_yticks(range(len(strong_correlations)))
                ax3.set_yticklabels(strong_correlations, fontsize=9)
                ax3.set_xlabel('|Spearman ρ|', fontsize=12)
                ax3.set_title('Strong Correlations (|ρ| ≥ 0.3)', fontsize=14, fontweight='bold')
                ax3.grid(True, alpha=0.3, axis='x')
                ax3.set_xlim(0, 1)
            else:
                ax3.text(0.5, 0.5, 'No Strong Correlations Found', ha='center', va='center', 
                        transform=ax3.transAxes, fontsize=16, color='gray')
                ax3.set_title('Strong Correlations', fontsize=14, fontweight='bold')
            
            # 右下：相关性分布直方图
            ax4 = axes[1, 1]
            # 提取上三角矩阵的相关系数（排除对角线）
            upper_triangle = []
            for i in range(len(correlation_array)):
                for j in range(i + 1, len(correlation_array)):
                    upper_triangle.append(correlation_array[i, j])
            
            if upper_triangle:
                ax4.hist(upper_triangle, bins=20, alpha=0.7, color=self.colors['primary'], edgecolor='black')
                ax4.axvline(np.mean(upper_triangle), color='red', linestyle='--', 
                           label=f'Mean: {np.mean(upper_triangle):.3f}')
                ax4.axvline(0, color='black', linestyle='-', alpha=0.5)
                ax4.set_xlabel('Spearman Correlation Coefficient (ρ)', fontsize=12)
                ax4.set_ylabel('Frequency', fontsize=12)
                ax4.set_title('Distribution of Spearman Correlations', fontsize=14, fontweight='bold')
                ax4.legend()
                ax4.grid(True, alpha=0.3)
            else:
                ax4.text(0.5, 0.5, 'No Correlation Data', ha='center', va='center', 
                        transform=ax4.transAxes, fontsize=16, color='gray')
                ax4.set_title('Correlation Distribution', fontsize=14, fontweight='bold')
            
            plt.tight_layout(pad=3.0)
            
            image_b64 = self._fig_to_base64(fig)
            plt.close(fig)
            return image_b64
            
        except ImportError:
            # fallback to simple clustering analysis
            return self.generate_clustering_analysis(spearman_data)
    
    # ========== P值分析图表 ==========
    
    def generate_pvalue_heatmap(self, pvalue_matrix: List[List[float]], 
                               metric_names: List[str], title: str = "Statistical Significance Analysis") -> str:
        """生成P值热力图显示统计显著性"""
        # 创建更易读的标签
        readable_metric_names = [self._convert_metric_name_to_readable(name) for name in metric_names]
        
        df_pval = pd.DataFrame(pvalue_matrix, 
                             index=readable_metric_names, 
                             columns=readable_metric_names)
        
        significance_labels = np.empty_like(df_pval, dtype=str)
        for i in range(len(metric_names)):
            for j in range(len(metric_names)):
                p_val = df_pval.iloc[i, j]
                if i == j:
                    significance_labels[i, j] = '-'
                elif p_val < 0.001:
                    significance_labels[i, j] = '***'
                elif p_val < 0.01:
                    significance_labels[i, j] = '**'
                elif p_val < 0.05:
                    significance_labels[i, j] = '*'
                else:
                    significance_labels[i, j] = ''
        
        fig, ax = plt.subplots(figsize=(12, 10))
        
        log_pvals = -np.log10(df_pval + 1e-100)
        mask = np.triu(np.ones_like(df_pval, dtype=bool), k=1)
        
        heatmap = sns.heatmap(log_pvals, 
                            mask=mask,
                            annot=significance_labels,
                            cmap='viridis',
                            square=True, 
                            fmt='',
                            cbar_kws={"shrink": .8, "label": "-log10(p-value)"},
                            annot_kws={'size': 10, 'fontweight': 'bold', 'color': 'white'},
                            ax=ax)
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('')
        ax.set_ylabel('')
        
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        
        legend_text = "Significance levels:\n*** p < 0.001\n** p < 0.01\n* p < 0.05"
        ax.text(1.02, 0.5, legend_text, transform=ax.transAxes, 
               fontsize=10, verticalalignment='center',
               bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        
        plt.tight_layout()
        
        image_b64 = self._fig_to_base64(fig)
        plt.close(fig)
        return image_b64
    
    def generate_spearman_clustering_comprehensive(self, spearman_data: Dict[str, Any], correlation_matrix: List[List[float]], metric_names: List[str]) -> str:
        """生成2x2布局的Spearman聚类综合分析图"""
        try:
            from scipy.cluster.hierarchy import dendrogram
            import numpy as np
            
            # 创建2x2布局
            fig, axes = plt.subplots(2, 2, figsize=(20, 16))
            
            # 转换metric名称为可读格式
            readable_labels = [self._convert_metric_name_to_readable(name).replace('\n', ' ') 
                              for name in metric_names]
            
            # 左上：Spearman相关性热力图
            ax1 = axes[0, 0]
            correlation_array = np.array(correlation_matrix)
            im1 = ax1.imshow(correlation_array, cmap='RdBu_r', aspect='equal', vmin=-1, vmax=1)
            
            # 设置热力图标签和标题
            ax1.set_xticks(range(len(readable_labels)))
            ax1.set_yticks(range(len(readable_labels)))
            ax1.set_xticklabels(readable_labels, rotation=45, ha='right', fontsize=10)
            ax1.set_yticklabels(readable_labels, fontsize=10)
            ax1.set_title('Spearman Correlation Heatmap', fontsize=14, fontweight='bold', pad=20)
            
            # 添加相关系数文本
            for i in range(len(readable_labels)):
                for j in range(len(readable_labels)):
                    corr_val = correlation_array[i, j]
                    color = 'white' if abs(corr_val) > 0.5 else 'black'
                    ax1.text(j, i, f'{corr_val:.2f}', ha='center', va='center', 
                            color=color, fontsize=8, fontweight='bold')
            
            # 添加颜色条
            cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.8)
            cbar1.set_label('Correlation Coefficient', fontsize=10)
            
            # 右上：聚类树状图
            ax2 = axes[0, 1]
            if spearman_data and 'linkage_matrix' in spearman_data:
                dendrogram_result = dendrogram(spearman_data['linkage_matrix'],
                                             labels=readable_labels,
                                             ax=ax2,
                                             orientation='top',
                                             distance_sort='descending',
                                             show_leaf_counts=False,
                                             color_threshold=0.7,
                                             leaf_rotation=45)
                ax2.set_title('Spearman Hierarchical Clustering\n(Distance: 1 - |ρ|)', 
                             fontsize=14, fontweight='bold', pad=20)
                ax2.set_ylabel('Distance (1 - |ρ|)', fontsize=12)
                ax2.tick_params(axis='x', labelsize=10)
            else:
                ax2.text(0.5, 0.5, 'No Clustering Data', ha='center', va='center', 
                        transform=ax2.transAxes, fontsize=16, color='gray')
                ax2.set_title('Spearman Hierarchical Clustering', fontsize=14, fontweight='bold')
                ax2.axis('off')
            
            # 左下：强相关对条形图
            ax3 = axes[1, 0]
            strong_correlations = []
            correlation_values = []
            
            for i in range(len(metric_names)):
                for j in range(i + 1, len(metric_names)):
                    corr_val = abs(correlation_array[i, j])
                    if corr_val >= 0.3:  # 显示中等以上相关性
                        pair_label = f"{readable_labels[i][:15]}...\n× {readable_labels[j][:15]}..."
                        strong_correlations.append(pair_label)
                        correlation_values.append(corr_val)
            
            # 按相关性强度排序
            if strong_correlations:
                sorted_pairs = sorted(zip(strong_correlations, correlation_values), 
                                    key=lambda x: x[1], reverse=True)
                strong_correlations, correlation_values = zip(*sorted_pairs[:10])  # 显示前10个
                
                colors = ['#d62728' if val >= 0.7 else '#ff7f0e' if val >= 0.5 else '#2ca02c' 
                         for val in correlation_values]
                bars = ax3.barh(range(len(strong_correlations)), correlation_values, color=colors, alpha=0.8)
                
                # 添加数值标签
                for i, (bar, val) in enumerate(zip(bars, correlation_values)):
                    ax3.text(val + 0.01, bar.get_y() + bar.get_height()/2, 
                            f'{val:.3f}', va='center', fontsize=9, fontweight='bold')
                
                ax3.set_yticks(range(len(strong_correlations)))
                ax3.set_yticklabels(strong_correlations, fontsize=9)
                ax3.set_xlabel('|Spearman ρ|', fontsize=12)
                ax3.set_title('Strong Correlations (|ρ| ≥ 0.3)', fontsize=14, fontweight='bold')
                ax3.grid(True, alpha=0.3, axis='x')
                ax3.set_xlim(0, 1)
            else:
                ax3.text(0.5, 0.5, 'No Strong Correlations Found', ha='center', va='center', 
                        transform=ax3.transAxes, fontsize=16, color='gray')
                ax3.set_title('Strong Correlations', fontsize=14, fontweight='bold')
            
            # 右下：相关性分布直方图
            ax4 = axes[1, 1]
            # 提取上三角矩阵的相关系数（排除对角线）
            upper_triangle = []
            for i in range(len(correlation_array)):
                for j in range(i + 1, len(correlation_array)):
                    upper_triangle.append(correlation_array[i, j])
            
            if upper_triangle:
                ax4.hist(upper_triangle, bins=20, alpha=0.7, color=self.colors['primary'], edgecolor='black')
                ax4.axvline(np.mean(upper_triangle), color='red', linestyle='--', 
                           label=f'Mean: {np.mean(upper_triangle):.3f}')
                ax4.axvline(0, color='black', linestyle='-', alpha=0.5)
                ax4.set_xlabel('Spearman Correlation Coefficient (ρ)', fontsize=12)
                ax4.set_ylabel('Frequency', fontsize=12)
                ax4.set_title('Distribution of Spearman Correlations', fontsize=14, fontweight='bold')
                ax4.legend()
                ax4.grid(True, alpha=0.3)
            else:
                ax4.text(0.5, 0.5, 'No Correlation Data', ha='center', va='center', 
                        transform=ax4.transAxes, fontsize=16, color='gray')
                ax4.set_title('Correlation Distribution', fontsize=14, fontweight='bold')
            
            plt.tight_layout(pad=3.0)
            
            image_b64 = self._fig_to_base64(fig)
            plt.close(fig)
            return image_b64
            
        except ImportError:
            # fallback to simple clustering analysis
            return self.generate_clustering_analysis(spearman_data)
    
    def generate_significance_comparison(self, pvalue_matrix: List[List[float]], 
                                       bonferroni_matrix: List[List[float]], 
                                       fdr_matrix: List[List[float]], 
                                       metric_names: List[str]) -> str:
        """生成多重校正比较图"""
        raw_pvals = []
        bonferroni_pvals = []
        fdr_pvals = []
        pair_labels = []
        
        for i in range(len(metric_names)):
            for j in range(i + 1, len(metric_names)):
                raw_pvals.append(pvalue_matrix[i][j])
                bonferroni_pvals.append(bonferroni_matrix[i][j])
                fdr_pvals.append(fdr_matrix[i][j])
                pair_labels.append(f"{metric_names[i]} × {metric_names[j]}")
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        indices = np.arange(len(pair_labels))
        
        ax1.scatter(indices, [-np.log10(p + 1e-100) for p in raw_pvals], 
                   alpha=0.7, label='Raw p-values', color='blue', s=50)
        ax1.scatter(indices, [-np.log10(p + 1e-100) for p in bonferroni_pvals], 
                   alpha=0.7, label='Bonferroni corrected', color='red', s=50)
        ax1.scatter(indices, [-np.log10(p + 1e-100) for p in fdr_pvals], 
                   alpha=0.7, label='FDR corrected', color='green', s=50)
        
        ax1.axhline(y=-np.log10(0.05), color='gray', linestyle='--', alpha=0.5, label='α = 0.05')
        ax1.axhline(y=-np.log10(0.01), color='gray', linestyle=':', alpha=0.5, label='α = 0.01')
        
        ax1.set_title('Multiple Testing Correction Comparison', fontsize=16, fontweight='bold')
        ax1.set_ylabel('-log10(p-value)', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        significance_levels = [0.05, 0.01, 0.001]
        level_names = ['p < 0.05', 'p < 0.01', 'p < 0.001']
        
        raw_counts = [sum(1 for p in raw_pvals if p < level) for level in significance_levels]
        bonf_counts = [sum(1 for p in bonferroni_pvals if p < level) for level in significance_levels]
        fdr_counts = [sum(1 for p in fdr_pvals if p < level) for level in significance_levels]
        
        x = np.arange(len(level_names))
        width = 0.25
        
        ax2.bar(x - width, raw_counts, width, label='Raw p-values', color='blue', alpha=0.7)
        ax2.bar(x, bonf_counts, width, label='Bonferroni corrected', color='red', alpha=0.7)
        ax2.bar(x + width, fdr_counts, width, label='FDR corrected', color='green', alpha=0.7)
        
        ax2.set_title('Significant Correlations Count by Correction Method', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Significance Level', fontsize=12)
        ax2.set_ylabel('Number of Significant Correlations', fontsize=12)
        ax2.set_xticks(x)
        ax2.set_xticklabels(level_names)
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')
        
        for i, (raw, bonf, fdr) in enumerate(zip(raw_counts, bonf_counts, fdr_counts)):
            ax2.text(i - width, raw + 0.1, str(raw), ha='center', va='bottom', fontweight='bold')
            ax2.text(i, bonf + 0.1, str(bonf), ha='center', va='bottom', fontweight='bold')
            ax2.text(i + width, fdr + 0.1, str(fdr), ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        image_b64 = self._fig_to_base64(fig)
        plt.close(fig)
        return image_b64
    
    def generate_spearman_clustering_comprehensive(self, spearman_data: Dict[str, Any], correlation_matrix: List[List[float]], metric_names: List[str]) -> str:
        """生成2x2布局的Spearman聚类综合分析图"""
        try:
            from scipy.cluster.hierarchy import dendrogram
            import numpy as np
            
            # 创建2x2布局
            fig, axes = plt.subplots(2, 2, figsize=(20, 16))
            
            # 转换metric名称为可读格式
            readable_labels = [self._convert_metric_name_to_readable(name).replace('\n', ' ') 
                              for name in metric_names]
            
            # 左上：Spearman相关性热力图
            ax1 = axes[0, 0]
            correlation_array = np.array(correlation_matrix)
            im1 = ax1.imshow(correlation_array, cmap='RdBu_r', aspect='equal', vmin=-1, vmax=1)
            
            # 设置热力图标签和标题
            ax1.set_xticks(range(len(readable_labels)))
            ax1.set_yticks(range(len(readable_labels)))
            ax1.set_xticklabels(readable_labels, rotation=45, ha='right', fontsize=10)
            ax1.set_yticklabels(readable_labels, fontsize=10)
            ax1.set_title('Spearman Correlation Heatmap', fontsize=14, fontweight='bold', pad=20)
            
            # 添加相关系数文本
            for i in range(len(readable_labels)):
                for j in range(len(readable_labels)):
                    corr_val = correlation_array[i, j]
                    color = 'white' if abs(corr_val) > 0.5 else 'black'
                    ax1.text(j, i, f'{corr_val:.2f}', ha='center', va='center', 
                            color=color, fontsize=8, fontweight='bold')
            
            # 添加颜色条
            cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.8)
            cbar1.set_label('Correlation Coefficient', fontsize=10)
            
            # 右上：聚类树状图
            ax2 = axes[0, 1]
            if spearman_data and 'linkage_matrix' in spearman_data:
                dendrogram_result = dendrogram(spearman_data['linkage_matrix'],
                                             labels=readable_labels,
                                             ax=ax2,
                                             orientation='top',
                                             distance_sort='descending',
                                             show_leaf_counts=False,
                                             color_threshold=0.7,
                                             leaf_rotation=45)
                ax2.set_title('Spearman Hierarchical Clustering\n(Distance: 1 - |ρ|)', 
                             fontsize=14, fontweight='bold', pad=20)
                ax2.set_ylabel('Distance (1 - |ρ|)', fontsize=12)
                ax2.tick_params(axis='x', labelsize=10)
            else:
                ax2.text(0.5, 0.5, 'No Clustering Data', ha='center', va='center', 
                        transform=ax2.transAxes, fontsize=16, color='gray')
                ax2.set_title('Spearman Hierarchical Clustering', fontsize=14, fontweight='bold')
                ax2.axis('off')
            
            # 左下：强相关对条形图
            ax3 = axes[1, 0]
            strong_correlations = []
            correlation_values = []
            
            for i in range(len(metric_names)):
                for j in range(i + 1, len(metric_names)):
                    corr_val = abs(correlation_array[i, j])
                    if corr_val >= 0.3:  # 显示中等以上相关性
                        pair_label = f"{readable_labels[i][:15]}...\n× {readable_labels[j][:15]}..."
                        strong_correlations.append(pair_label)
                        correlation_values.append(corr_val)
            
            # 按相关性强度排序
            if strong_correlations:
                sorted_pairs = sorted(zip(strong_correlations, correlation_values), 
                                    key=lambda x: x[1], reverse=True)
                strong_correlations, correlation_values = zip(*sorted_pairs[:10])  # 显示前10个
                
                colors = ['#d62728' if val >= 0.7 else '#ff7f0e' if val >= 0.5 else '#2ca02c' 
                         for val in correlation_values]
                bars = ax3.barh(range(len(strong_correlations)), correlation_values, color=colors, alpha=0.8)
                
                # 添加数值标签
                for i, (bar, val) in enumerate(zip(bars, correlation_values)):
                    ax3.text(val + 0.01, bar.get_y() + bar.get_height()/2, 
                            f'{val:.3f}', va='center', fontsize=9, fontweight='bold')
                
                ax3.set_yticks(range(len(strong_correlations)))
                ax3.set_yticklabels(strong_correlations, fontsize=9)
                ax3.set_xlabel('|Spearman ρ|', fontsize=12)
                ax3.set_title('Strong Correlations (|ρ| ≥ 0.3)', fontsize=14, fontweight='bold')
                ax3.grid(True, alpha=0.3, axis='x')
                ax3.set_xlim(0, 1)
            else:
                ax3.text(0.5, 0.5, 'No Strong Correlations Found', ha='center', va='center', 
                        transform=ax3.transAxes, fontsize=16, color='gray')
                ax3.set_title('Strong Correlations', fontsize=14, fontweight='bold')
            
            # 右下：相关性分布直方图
            ax4 = axes[1, 1]
            # 提取上三角矩阵的相关系数（排除对角线）
            upper_triangle = []
            for i in range(len(correlation_array)):
                for j in range(i + 1, len(correlation_array)):
                    upper_triangle.append(correlation_array[i, j])
            
            if upper_triangle:
                ax4.hist(upper_triangle, bins=20, alpha=0.7, color=self.colors['primary'], edgecolor='black')
                ax4.axvline(np.mean(upper_triangle), color='red', linestyle='--', 
                           label=f'Mean: {np.mean(upper_triangle):.3f}')
                ax4.axvline(0, color='black', linestyle='-', alpha=0.5)
                ax4.set_xlabel('Spearman Correlation Coefficient (ρ)', fontsize=12)
                ax4.set_ylabel('Frequency', fontsize=12)
                ax4.set_title('Distribution of Spearman Correlations', fontsize=14, fontweight='bold')
                ax4.legend()
                ax4.grid(True, alpha=0.3)
            else:
                ax4.text(0.5, 0.5, 'No Correlation Data', ha='center', va='center', 
                        transform=ax4.transAxes, fontsize=16, color='gray')
                ax4.set_title('Correlation Distribution', fontsize=14, fontweight='bold')
            
            plt.tight_layout(pad=3.0)
            
            image_b64 = self._fig_to_base64(fig)
            plt.close(fig)
            return image_b64
            
        except ImportError:
            # fallback to simple clustering analysis
            return self.generate_clustering_analysis(spearman_data)
    
    def generate_consistency_analysis(self, correlation_matrix: List[List[float]], 
                                    pvalue_matrix: List[List[float]], 
                                    metric_names: List[str]) -> str:
        """生成相关性与显著性一致性分析图"""
        correlations = []
        pvalues = []
        
        for i in range(len(metric_names)):
            for j in range(i + 1, len(metric_names)):
                correlations.append(abs(correlation_matrix[i][j]))
                pvalues.append(pvalue_matrix[i][j])
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        colors = []
        sizes = []
        for p in pvalues:
            if p < 0.001:
                colors.append('#FF0000')
                sizes.append(100)
            elif p < 0.01:
                colors.append('#FF8800')
                sizes.append(80)
            elif p < 0.05:
                colors.append('#FFDD00')
                sizes.append(60)
            else:
                colors.append('#CCCCCC')
                sizes.append(40)
        
        scatter = ax1.scatter(correlations, [-np.log10(p + 1e-100) for p in pvalues], 
                            c=colors, s=sizes, alpha=0.7, edgecolors='black', linewidth=0.5)
        
        ax1.set_xlabel('Correlation Strength (|r|)', fontsize=12)
        ax1.set_ylabel('-log10(p-value)', fontsize=12)
        ax1.set_title('Correlation Strength vs Statistical Significance', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        ax1.axhline(y=-np.log10(0.05), color='gray', linestyle='--', alpha=0.7, label='α = 0.05')
        ax1.axhline(y=-np.log10(0.01), color='gray', linestyle=':', alpha=0.7, label='α = 0.01')
        ax1.legend()
        
        sig_high = [r for r, p in zip(correlations, pvalues) if p < 0.01]
        sig_moderate = [r for r, p in zip(correlations, pvalues) if 0.01 <= p < 0.05]
        sig_low = [r for r, p in zip(correlations, pvalues) if p >= 0.05]
        
        bins = np.linspace(0, 1, 21)
        ax2.hist(sig_high, bins=bins, alpha=0.7, label=f'Highly Significant (p<0.01, n={len(sig_high)})', 
                color='red', density=True)
        ax2.hist(sig_moderate, bins=bins, alpha=0.7, label=f'Significant (0.01≤p<0.05, n={len(sig_moderate)})', 
                color='orange', density=True)
        ax2.hist(sig_low, bins=bins, alpha=0.7, label=f'Not Significant (p≥0.05, n={len(sig_low)})', 
                color='gray', density=True)
        
        ax2.set_xlabel('Correlation Strength (|r|)', fontsize=12)
        ax2.set_ylabel('Density', fontsize=12)
        ax2.set_title('Correlation Distribution by Significance Level', fontsize=14, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        image_b64 = self._fig_to_base64(fig)
        plt.close(fig)
        return image_b64
    
    def generate_spearman_clustering_comprehensive(self, spearman_data: Dict[str, Any], correlation_matrix: List[List[float]], metric_names: List[str]) -> str:
        """生成2x2布局的Spearman聚类综合分析图"""
        try:
            from scipy.cluster.hierarchy import dendrogram
            import numpy as np
            
            # 创建2x2布局
            fig, axes = plt.subplots(2, 2, figsize=(20, 16))
            
            # 转换metric名称为可读格式
            readable_labels = [self._convert_metric_name_to_readable(name).replace('\n', ' ') 
                              for name in metric_names]
            
            # 左上：Spearman相关性热力图
            ax1 = axes[0, 0]
            correlation_array = np.array(correlation_matrix)
            im1 = ax1.imshow(correlation_array, cmap='RdBu_r', aspect='equal', vmin=-1, vmax=1)
            
            # 设置热力图标签和标题
            ax1.set_xticks(range(len(readable_labels)))
            ax1.set_yticks(range(len(readable_labels)))
            ax1.set_xticklabels(readable_labels, rotation=45, ha='right', fontsize=10)
            ax1.set_yticklabels(readable_labels, fontsize=10)
            ax1.set_title('Spearman Correlation Heatmap', fontsize=14, fontweight='bold', pad=20)
            
            # 添加相关系数文本
            for i in range(len(readable_labels)):
                for j in range(len(readable_labels)):
                    corr_val = correlation_array[i, j]
                    color = 'white' if abs(corr_val) > 0.5 else 'black'
                    ax1.text(j, i, f'{corr_val:.2f}', ha='center', va='center', 
                            color=color, fontsize=8, fontweight='bold')
            
            # 添加颜色条
            cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.8)
            cbar1.set_label('Correlation Coefficient', fontsize=10)
            
            # 右上：聚类树状图
            ax2 = axes[0, 1]
            if spearman_data and 'linkage_matrix' in spearman_data:
                dendrogram_result = dendrogram(spearman_data['linkage_matrix'],
                                             labels=readable_labels,
                                             ax=ax2,
                                             orientation='top',
                                             distance_sort='descending',
                                             show_leaf_counts=False,
                                             color_threshold=0.7,
                                             leaf_rotation=45)
                ax2.set_title('Spearman Hierarchical Clustering\n(Distance: 1 - |ρ|)', 
                             fontsize=14, fontweight='bold', pad=20)
                ax2.set_ylabel('Distance (1 - |ρ|)', fontsize=12)
                ax2.tick_params(axis='x', labelsize=10)
            else:
                ax2.text(0.5, 0.5, 'No Clustering Data', ha='center', va='center', 
                        transform=ax2.transAxes, fontsize=16, color='gray')
                ax2.set_title('Spearman Hierarchical Clustering', fontsize=14, fontweight='bold')
                ax2.axis('off')
            
            # 左下：强相关对条形图
            ax3 = axes[1, 0]
            strong_correlations = []
            correlation_values = []
            
            for i in range(len(metric_names)):
                for j in range(i + 1, len(metric_names)):
                    corr_val = abs(correlation_array[i, j])
                    if corr_val >= 0.3:  # 显示中等以上相关性
                        pair_label = f"{readable_labels[i][:15]}...\n× {readable_labels[j][:15]}..."
                        strong_correlations.append(pair_label)
                        correlation_values.append(corr_val)
            
            # 按相关性强度排序
            if strong_correlations:
                sorted_pairs = sorted(zip(strong_correlations, correlation_values), 
                                    key=lambda x: x[1], reverse=True)
                strong_correlations, correlation_values = zip(*sorted_pairs[:10])  # 显示前10个
                
                colors = ['#d62728' if val >= 0.7 else '#ff7f0e' if val >= 0.5 else '#2ca02c' 
                         for val in correlation_values]
                bars = ax3.barh(range(len(strong_correlations)), correlation_values, color=colors, alpha=0.8)
                
                # 添加数值标签
                for i, (bar, val) in enumerate(zip(bars, correlation_values)):
                    ax3.text(val + 0.01, bar.get_y() + bar.get_height()/2, 
                            f'{val:.3f}', va='center', fontsize=9, fontweight='bold')
                
                ax3.set_yticks(range(len(strong_correlations)))
                ax3.set_yticklabels(strong_correlations, fontsize=9)
                ax3.set_xlabel('|Spearman ρ|', fontsize=12)
                ax3.set_title('Strong Correlations (|ρ| ≥ 0.3)', fontsize=14, fontweight='bold')
                ax3.grid(True, alpha=0.3, axis='x')
                ax3.set_xlim(0, 1)
            else:
                ax3.text(0.5, 0.5, 'No Strong Correlations Found', ha='center', va='center', 
                        transform=ax3.transAxes, fontsize=16, color='gray')
                ax3.set_title('Strong Correlations', fontsize=14, fontweight='bold')
            
            # 右下：相关性分布直方图
            ax4 = axes[1, 1]
            # 提取上三角矩阵的相关系数（排除对角线）
            upper_triangle = []
            for i in range(len(correlation_array)):
                for j in range(i + 1, len(correlation_array)):
                    upper_triangle.append(correlation_array[i, j])
            
            if upper_triangle:
                ax4.hist(upper_triangle, bins=20, alpha=0.7, color=self.colors['primary'], edgecolor='black')
                ax4.axvline(np.mean(upper_triangle), color='red', linestyle='--', 
                           label=f'Mean: {np.mean(upper_triangle):.3f}')
                ax4.axvline(0, color='black', linestyle='-', alpha=0.5)
                ax4.set_xlabel('Spearman Correlation Coefficient (ρ)', fontsize=12)
                ax4.set_ylabel('Frequency', fontsize=12)
                ax4.set_title('Distribution of Spearman Correlations', fontsize=14, fontweight='bold')
                ax4.legend()
                ax4.grid(True, alpha=0.3)
            else:
                ax4.text(0.5, 0.5, 'No Correlation Data', ha='center', va='center', 
                        transform=ax4.transAxes, fontsize=16, color='gray')
                ax4.set_title('Correlation Distribution', fontsize=14, fontweight='bold')
            
            plt.tight_layout(pad=3.0)
            
            image_b64 = self._fig_to_base64(fig)
            plt.close(fig)
            return image_b64
            
        except ImportError:
            # fallback to simple clustering analysis
            return self.generate_clustering_analysis(spearman_data)
    
    # ========== VIF分析图表 ==========
    
    def generate_vif_chart(self, vif_data: List[Dict[str, Any]]) -> str:
        """生成VIF分析图表"""
        if not vif_data:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No VIF Data Available', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=16, color='gray')
            ax.set_title('VIF Analysis', fontsize=16, fontweight='bold')
            ax.axis('off')
            
            image_b64 = self._fig_to_base64(fig)
            plt.close(fig)
            return image_b64
        
        features = [item['feature'] for item in vif_data]
        vif_values = [item['vif'] for item in vif_data]
        
        # 转换为更易读的标签
        readable_features = [self._convert_metric_name_to_readable(name) for name in features]
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        colors = []
        for vif in vif_values:
            if vif > 10:
                colors.append('#EF4444')  # 高多重共线性 - 红色
            elif vif > 5:
                colors.append('#F59E0B')  # 中等多重共线性 - 橙色
            else:
                colors.append(self.colors['success'])  # 低多重共线性 - 绿色
        
        bars = ax.bar(range(len(readable_features)), vif_values, color=colors, alpha=0.8, edgecolor='white')
        
        for i, (bar, vif) in enumerate(zip(bars, vif_values)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{vif:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        ax.axhline(y=5, color='orange', linestyle='--', alpha=0.7, label='Moderate Multicollinearity (VIF=5)')
        ax.axhline(y=10, color='red', linestyle='--', alpha=0.7, label='High Multicollinearity (VIF=10)')
        
        ax.set_title('Variance Inflation Factor (VIF) Analysis', fontsize=16, fontweight='bold')
        ax.set_ylabel('VIF Value', fontsize=12)
        ax.set_xlabel('Features', fontsize=12)
        
        ax.set_xticks(range(len(readable_features)))
        ax.set_xticklabels(readable_features, rotation=45, ha='right', fontsize=10)
        
        ax.grid(True, alpha=0.3, axis='y')
        ax.legend()
        
        plt.tight_layout()
        
        image_b64 = self._fig_to_base64(fig)
        plt.close(fig)
        return image_b64
    
    def generate_spearman_clustering_comprehensive(self, spearman_data: Dict[str, Any], correlation_matrix: List[List[float]], metric_names: List[str]) -> str:
        """生成2x2布局的Spearman聚类综合分析图"""
        try:
            from scipy.cluster.hierarchy import dendrogram
            import numpy as np
            
            # 创建2x2布局
            fig, axes = plt.subplots(2, 2, figsize=(20, 16))
            
            # 转换metric名称为可读格式
            readable_labels = [self._convert_metric_name_to_readable(name).replace('\n', ' ') 
                              for name in metric_names]
            
            # 左上：Spearman相关性热力图
            ax1 = axes[0, 0]
            correlation_array = np.array(correlation_matrix)
            im1 = ax1.imshow(correlation_array, cmap='RdBu_r', aspect='equal', vmin=-1, vmax=1)
            
            # 设置热力图标签和标题
            ax1.set_xticks(range(len(readable_labels)))
            ax1.set_yticks(range(len(readable_labels)))
            ax1.set_xticklabels(readable_labels, rotation=45, ha='right', fontsize=10)
            ax1.set_yticklabels(readable_labels, fontsize=10)
            ax1.set_title('Spearman Correlation Heatmap', fontsize=14, fontweight='bold', pad=20)
            
            # 添加相关系数文本
            for i in range(len(readable_labels)):
                for j in range(len(readable_labels)):
                    corr_val = correlation_array[i, j]
                    color = 'white' if abs(corr_val) > 0.5 else 'black'
                    ax1.text(j, i, f'{corr_val:.2f}', ha='center', va='center', 
                            color=color, fontsize=8, fontweight='bold')
            
            # 添加颜色条
            cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.8)
            cbar1.set_label('Correlation Coefficient', fontsize=10)
            
            # 右上：聚类树状图
            ax2 = axes[0, 1]
            if spearman_data and 'linkage_matrix' in spearman_data:
                dendrogram_result = dendrogram(spearman_data['linkage_matrix'],
                                             labels=readable_labels,
                                             ax=ax2,
                                             orientation='top',
                                             distance_sort='descending',
                                             show_leaf_counts=False,
                                             color_threshold=0.7,
                                             leaf_rotation=45)
                ax2.set_title('Spearman Hierarchical Clustering\n(Distance: 1 - |ρ|)', 
                             fontsize=14, fontweight='bold', pad=20)
                ax2.set_ylabel('Distance (1 - |ρ|)', fontsize=12)
                ax2.tick_params(axis='x', labelsize=10)
            else:
                ax2.text(0.5, 0.5, 'No Clustering Data', ha='center', va='center', 
                        transform=ax2.transAxes, fontsize=16, color='gray')
                ax2.set_title('Spearman Hierarchical Clustering', fontsize=14, fontweight='bold')
                ax2.axis('off')
            
            # 左下：强相关对条形图
            ax3 = axes[1, 0]
            strong_correlations = []
            correlation_values = []
            
            for i in range(len(metric_names)):
                for j in range(i + 1, len(metric_names)):
                    corr_val = abs(correlation_array[i, j])
                    if corr_val >= 0.3:  # 显示中等以上相关性
                        pair_label = f"{readable_labels[i][:15]}...\n× {readable_labels[j][:15]}..."
                        strong_correlations.append(pair_label)
                        correlation_values.append(corr_val)
            
            # 按相关性强度排序
            if strong_correlations:
                sorted_pairs = sorted(zip(strong_correlations, correlation_values), 
                                    key=lambda x: x[1], reverse=True)
                strong_correlations, correlation_values = zip(*sorted_pairs[:10])  # 显示前10个
                
                colors = ['#d62728' if val >= 0.7 else '#ff7f0e' if val >= 0.5 else '#2ca02c' 
                         for val in correlation_values]
                bars = ax3.barh(range(len(strong_correlations)), correlation_values, color=colors, alpha=0.8)
                
                # 添加数值标签
                for i, (bar, val) in enumerate(zip(bars, correlation_values)):
                    ax3.text(val + 0.01, bar.get_y() + bar.get_height()/2, 
                            f'{val:.3f}', va='center', fontsize=9, fontweight='bold')
                
                ax3.set_yticks(range(len(strong_correlations)))
                ax3.set_yticklabels(strong_correlations, fontsize=9)
                ax3.set_xlabel('|Spearman ρ|', fontsize=12)
                ax3.set_title('Strong Correlations (|ρ| ≥ 0.3)', fontsize=14, fontweight='bold')
                ax3.grid(True, alpha=0.3, axis='x')
                ax3.set_xlim(0, 1)
            else:
                ax3.text(0.5, 0.5, 'No Strong Correlations Found', ha='center', va='center', 
                        transform=ax3.transAxes, fontsize=16, color='gray')
                ax3.set_title('Strong Correlations', fontsize=14, fontweight='bold')
            
            # 右下：相关性分布直方图
            ax4 = axes[1, 1]
            # 提取上三角矩阵的相关系数（排除对角线）
            upper_triangle = []
            for i in range(len(correlation_array)):
                for j in range(i + 1, len(correlation_array)):
                    upper_triangle.append(correlation_array[i, j])
            
            if upper_triangle:
                ax4.hist(upper_triangle, bins=20, alpha=0.7, color=self.colors['primary'], edgecolor='black')
                ax4.axvline(np.mean(upper_triangle), color='red', linestyle='--', 
                           label=f'Mean: {np.mean(upper_triangle):.3f}')
                ax4.axvline(0, color='black', linestyle='-', alpha=0.5)
                ax4.set_xlabel('Spearman Correlation Coefficient (ρ)', fontsize=12)
                ax4.set_ylabel('Frequency', fontsize=12)
                ax4.set_title('Distribution of Spearman Correlations', fontsize=14, fontweight='bold')
                ax4.legend()
                ax4.grid(True, alpha=0.3)
            else:
                ax4.text(0.5, 0.5, 'No Correlation Data', ha='center', va='center', 
                        transform=ax4.transAxes, fontsize=16, color='gray')
                ax4.set_title('Correlation Distribution', fontsize=14, fontweight='bold')
            
            plt.tight_layout(pad=3.0)
            
            image_b64 = self._fig_to_base64(fig)
            plt.close(fig)
            return image_b64
            
        except ImportError:
            # fallback to simple clustering analysis
            return self.generate_clustering_analysis(spearman_data)
    
    # ========== PCA分析图表 ==========
    
    def generate_pca_analysis(self, pca_data: Dict[str, Any], feature_names: Optional[List[str]] = None) -> str:
        """生成PCA分析图表"""
        if not pca_data or 'explained_variance_ratio' not in pca_data:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No PCA Data Available', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=16, color='gray')
            ax.set_title('PCA Analysis', fontsize=16, fontweight='bold')
            ax.axis('off')
            
            image_b64 = self._fig_to_base64(fig)
            plt.close(fig)
            return image_b64
        
        explained_variance = pca_data['explained_variance_ratio']
        cumulative_variance = np.cumsum(explained_variance)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 左图：主成分方差解释比例（恢复原来的逻辑）
        components = range(1, len(explained_variance) + 1)
        bars = ax1.bar(components, explained_variance, alpha=0.8, color=self.colors['primary'])
        
        for i, (bar, var) in enumerate(zip(bars, explained_variance)):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.005,
                   f'{var:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax1.set_title('PCA Explained Variance by Component', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Principal Component', fontsize=12)
        ax1.set_ylabel('Explained Variance Ratio', fontsize=12)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # X轴使用标准的PC编号
        pc_labels = [f'PC{i}' for i in components]
        ax1.set_xticks(components)
        ax1.set_xticklabels(pc_labels, fontsize=10, rotation=0, ha='center')
        
        # 右图：累积方差解释比例
        components = range(1, len(explained_variance) + 1)
        
        # 右图：累积方差解释比例
        ax2.plot(components, cumulative_variance, marker='o', linewidth=2, 
                color=self.colors['primary'], markersize=6)
        ax2.fill_between(components, cumulative_variance, alpha=0.3, color=self.colors['primary'])
        
        # 添加重要的阈值线
        ax2.axhline(y=0.8, color='red', linestyle='--', alpha=0.7, label='80% Variance')
        ax2.axhline(y=0.9, color='orange', linestyle='--', alpha=0.7, label='90% Variance')
        
        for i, cum_var in enumerate(cumulative_variance):
            ax2.text(i + 1, cum_var + 0.02, f'{cum_var:.3f}', 
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax2.set_title('Cumulative Explained Variance', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Number of Components', fontsize=12)
        ax2.set_ylabel('Cumulative Explained Variance Ratio', fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        ax2.set_ylim(0, 1.05)
        
        # 右图也使用相同的PC编号标签
        ax2.set_xticks(components)
        ax2.set_xticklabels(pc_labels, fontsize=10, rotation=0, ha='center')
        
        # 调整布局，给底部标签留出足够空间
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.15)  # 增加底部边距
        
        image_b64 = self._fig_to_base64(fig)
        plt.close(fig)
        return image_b64
    
    def generate_spearman_clustering_comprehensive(self, spearman_data: Dict[str, Any], correlation_matrix: List[List[float]], metric_names: List[str]) -> str:
        """生成2x2布局的Spearman聚类综合分析图"""
        try:
            from scipy.cluster.hierarchy import dendrogram
            import numpy as np
            
            # 创建2x2布局
            fig, axes = plt.subplots(2, 2, figsize=(20, 16))
            
            # 转换metric名称为可读格式
            readable_labels = [self._convert_metric_name_to_readable(name).replace('\n', ' ') 
                              for name in metric_names]
            
            # 左上：Spearman相关性热力图
            ax1 = axes[0, 0]
            correlation_array = np.array(correlation_matrix)
            im1 = ax1.imshow(correlation_array, cmap='RdBu_r', aspect='equal', vmin=-1, vmax=1)
            
            # 设置热力图标签和标题
            ax1.set_xticks(range(len(readable_labels)))
            ax1.set_yticks(range(len(readable_labels)))
            ax1.set_xticklabels(readable_labels, rotation=45, ha='right', fontsize=10)
            ax1.set_yticklabels(readable_labels, fontsize=10)
            ax1.set_title('Spearman Correlation Heatmap', fontsize=14, fontweight='bold', pad=20)
            
            # 添加相关系数文本
            for i in range(len(readable_labels)):
                for j in range(len(readable_labels)):
                    corr_val = correlation_array[i, j]
                    color = 'white' if abs(corr_val) > 0.5 else 'black'
                    ax1.text(j, i, f'{corr_val:.2f}', ha='center', va='center', 
                            color=color, fontsize=8, fontweight='bold')
            
            # 添加颜色条
            cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.8)
            cbar1.set_label('Correlation Coefficient', fontsize=10)
            
            # 右上：聚类树状图
            ax2 = axes[0, 1]
            if spearman_data and 'linkage_matrix' in spearman_data:
                dendrogram_result = dendrogram(spearman_data['linkage_matrix'],
                                             labels=readable_labels,
                                             ax=ax2,
                                             orientation='top',
                                             distance_sort='descending',
                                             show_leaf_counts=False,
                                             color_threshold=0.7,
                                             leaf_rotation=45)
                ax2.set_title('Spearman Hierarchical Clustering\n(Distance: 1 - |ρ|)', 
                             fontsize=14, fontweight='bold', pad=20)
                ax2.set_ylabel('Distance (1 - |ρ|)', fontsize=12)
                ax2.tick_params(axis='x', labelsize=10)
            else:
                ax2.text(0.5, 0.5, 'No Clustering Data', ha='center', va='center', 
                        transform=ax2.transAxes, fontsize=16, color='gray')
                ax2.set_title('Spearman Hierarchical Clustering', fontsize=14, fontweight='bold')
                ax2.axis('off')
            
            # 左下：强相关对条形图
            ax3 = axes[1, 0]
            strong_correlations = []
            correlation_values = []
            
            for i in range(len(metric_names)):
                for j in range(i + 1, len(metric_names)):
                    corr_val = abs(correlation_array[i, j])
                    if corr_val >= 0.3:  # 显示中等以上相关性
                        pair_label = f"{readable_labels[i][:15]}...\n× {readable_labels[j][:15]}..."
                        strong_correlations.append(pair_label)
                        correlation_values.append(corr_val)
            
            # 按相关性强度排序
            if strong_correlations:
                sorted_pairs = sorted(zip(strong_correlations, correlation_values), 
                                    key=lambda x: x[1], reverse=True)
                strong_correlations, correlation_values = zip(*sorted_pairs[:10])  # 显示前10个
                
                colors = ['#d62728' if val >= 0.7 else '#ff7f0e' if val >= 0.5 else '#2ca02c' 
                         for val in correlation_values]
                bars = ax3.barh(range(len(strong_correlations)), correlation_values, color=colors, alpha=0.8)
                
                # 添加数值标签
                for i, (bar, val) in enumerate(zip(bars, correlation_values)):
                    ax3.text(val + 0.01, bar.get_y() + bar.get_height()/2, 
                            f'{val:.3f}', va='center', fontsize=9, fontweight='bold')
                
                ax3.set_yticks(range(len(strong_correlations)))
                ax3.set_yticklabels(strong_correlations, fontsize=9)
                ax3.set_xlabel('|Spearman ρ|', fontsize=12)
                ax3.set_title('Strong Correlations (|ρ| ≥ 0.3)', fontsize=14, fontweight='bold')
                ax3.grid(True, alpha=0.3, axis='x')
                ax3.set_xlim(0, 1)
            else:
                ax3.text(0.5, 0.5, 'No Strong Correlations Found', ha='center', va='center', 
                        transform=ax3.transAxes, fontsize=16, color='gray')
                ax3.set_title('Strong Correlations', fontsize=14, fontweight='bold')
            
            # 右下：相关性分布直方图
            ax4 = axes[1, 1]
            # 提取上三角矩阵的相关系数（排除对角线）
            upper_triangle = []
            for i in range(len(correlation_array)):
                for j in range(i + 1, len(correlation_array)):
                    upper_triangle.append(correlation_array[i, j])
            
            if upper_triangle:
                ax4.hist(upper_triangle, bins=20, alpha=0.7, color=self.colors['primary'], edgecolor='black')
                ax4.axvline(np.mean(upper_triangle), color='red', linestyle='--', 
                           label=f'Mean: {np.mean(upper_triangle):.3f}')
                ax4.axvline(0, color='black', linestyle='-', alpha=0.5)
                ax4.set_xlabel('Spearman Correlation Coefficient (ρ)', fontsize=12)
                ax4.set_ylabel('Frequency', fontsize=12)
                ax4.set_title('Distribution of Spearman Correlations', fontsize=14, fontweight='bold')
                ax4.legend()
                ax4.grid(True, alpha=0.3)
            else:
                ax4.text(0.5, 0.5, 'No Correlation Data', ha='center', va='center', 
                        transform=ax4.transAxes, fontsize=16, color='gray')
                ax4.set_title('Correlation Distribution', fontsize=14, fontweight='bold')
            
            plt.tight_layout(pad=3.0)
            
            image_b64 = self._fig_to_base64(fig)
            plt.close(fig)
            return image_b64
            
        except ImportError:
            # fallback to simple clustering analysis
            return self.generate_clustering_analysis(spearman_data)
    
    def generate_pca_components(self, components_data: Dict[str, Any], feature_names: List[str]) -> str:
        """生成PCA成分载荷图"""
        if not components_data or 'components' not in components_data:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No PCA Components Data Available', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=16, color='gray')
            ax.set_title('PCA Components', fontsize=16, fontweight='bold')
            ax.axis('off')
            
            image_b64 = self._fig_to_base64(fig)
            plt.close(fig)
            return image_b64
        
        # 转换为更易读的标签
        readable_feature_names = [self._convert_metric_name_to_readable(name) for name in feature_names]
        
        components = components_data['components']
        n_components = min(4, len(components))  # 最多显示前4个主成分
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        axes = axes.flatten()
        
        for i in range(n_components):
            loadings = components[i]
            
            # 创建载荷图
            colors = [self.colors['primary'] if x >= 0 else self.colors['danger'] for x in loadings]
            bars = axes[i].bar(range(len(readable_feature_names)), loadings, color=colors, alpha=0.8)
            
            # 添加数值标签
            for j, (bar, loading) in enumerate(zip(bars, loadings)):
                height = bar.get_height()
                label_y = height + 0.01 if height >= 0 else height - 0.03
                axes[i].text(bar.get_x() + bar.get_width()/2., label_y,
                           f'{loading:.3f}', ha='center', va='bottom' if height >= 0 else 'top',
                           fontsize=8, fontweight='bold')
            
            axes[i].set_title(f'PC{i+1} Component Loadings', fontsize=12, fontweight='bold')
            axes[i].set_xlabel('Features', fontsize=10)
            axes[i].set_ylabel('Loading Value', fontsize=10)
            axes[i].set_xticks(range(len(readable_feature_names)))
            axes[i].set_xticklabels(readable_feature_names, rotation=45, ha='right', fontsize=8)
            axes[i].grid(True, alpha=0.3, axis='y')
            axes[i].axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        # 隐藏多余的子图
        for i in range(n_components, 4):
            axes[i].axis('off')
        
        plt.suptitle('PCA Component Loadings Analysis', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        image_b64 = self._fig_to_base64(fig)
        plt.close(fig)
        return image_b64
    
    def generate_spearman_clustering_comprehensive(self, spearman_data: Dict[str, Any], correlation_matrix: List[List[float]], metric_names: List[str]) -> str:
        """生成2x2布局的Spearman聚类综合分析图"""
        try:
            from scipy.cluster.hierarchy import dendrogram
            import numpy as np
            
            # 创建2x2布局
            fig, axes = plt.subplots(2, 2, figsize=(20, 16))
            
            # 转换metric名称为可读格式
            readable_labels = [self._convert_metric_name_to_readable(name).replace('\n', ' ') 
                              for name in metric_names]
            
            # 左上：Spearman相关性热力图
            ax1 = axes[0, 0]
            correlation_array = np.array(correlation_matrix)
            im1 = ax1.imshow(correlation_array, cmap='RdBu_r', aspect='equal', vmin=-1, vmax=1)
            
            # 设置热力图标签和标题
            ax1.set_xticks(range(len(readable_labels)))
            ax1.set_yticks(range(len(readable_labels)))
            ax1.set_xticklabels(readable_labels, rotation=45, ha='right', fontsize=10)
            ax1.set_yticklabels(readable_labels, fontsize=10)
            ax1.set_title('Spearman Correlation Heatmap', fontsize=14, fontweight='bold', pad=20)
            
            # 添加相关系数文本
            for i in range(len(readable_labels)):
                for j in range(len(readable_labels)):
                    corr_val = correlation_array[i, j]
                    color = 'white' if abs(corr_val) > 0.5 else 'black'
                    ax1.text(j, i, f'{corr_val:.2f}', ha='center', va='center', 
                            color=color, fontsize=8, fontweight='bold')
            
            # 添加颜色条
            cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.8)
            cbar1.set_label('Correlation Coefficient', fontsize=10)
            
            # 右上：聚类树状图
            ax2 = axes[0, 1]
            if spearman_data and 'linkage_matrix' in spearman_data:
                dendrogram_result = dendrogram(spearman_data['linkage_matrix'],
                                             labels=readable_labels,
                                             ax=ax2,
                                             orientation='top',
                                             distance_sort='descending',
                                             show_leaf_counts=False,
                                             color_threshold=0.7,
                                             leaf_rotation=45)
                ax2.set_title('Spearman Hierarchical Clustering\n(Distance: 1 - |ρ|)', 
                             fontsize=14, fontweight='bold', pad=20)
                ax2.set_ylabel('Distance (1 - |ρ|)', fontsize=12)
                ax2.tick_params(axis='x', labelsize=10)
            else:
                ax2.text(0.5, 0.5, 'No Clustering Data', ha='center', va='center', 
                        transform=ax2.transAxes, fontsize=16, color='gray')
                ax2.set_title('Spearman Hierarchical Clustering', fontsize=14, fontweight='bold')
                ax2.axis('off')
            
            # 左下：强相关对条形图
            ax3 = axes[1, 0]
            strong_correlations = []
            correlation_values = []
            
            for i in range(len(metric_names)):
                for j in range(i + 1, len(metric_names)):
                    corr_val = abs(correlation_array[i, j])
                    if corr_val >= 0.3:  # 显示中等以上相关性
                        pair_label = f"{readable_labels[i][:15]}...\n× {readable_labels[j][:15]}..."
                        strong_correlations.append(pair_label)
                        correlation_values.append(corr_val)
            
            # 按相关性强度排序
            if strong_correlations:
                sorted_pairs = sorted(zip(strong_correlations, correlation_values), 
                                    key=lambda x: x[1], reverse=True)
                strong_correlations, correlation_values = zip(*sorted_pairs[:10])  # 显示前10个
                
                colors = ['#d62728' if val >= 0.7 else '#ff7f0e' if val >= 0.5 else '#2ca02c' 
                         for val in correlation_values]
                bars = ax3.barh(range(len(strong_correlations)), correlation_values, color=colors, alpha=0.8)
                
                # 添加数值标签
                for i, (bar, val) in enumerate(zip(bars, correlation_values)):
                    ax3.text(val + 0.01, bar.get_y() + bar.get_height()/2, 
                            f'{val:.3f}', va='center', fontsize=9, fontweight='bold')
                
                ax3.set_yticks(range(len(strong_correlations)))
                ax3.set_yticklabels(strong_correlations, fontsize=9)
                ax3.set_xlabel('|Spearman ρ|', fontsize=12)
                ax3.set_title('Strong Correlations (|ρ| ≥ 0.3)', fontsize=14, fontweight='bold')
                ax3.grid(True, alpha=0.3, axis='x')
                ax3.set_xlim(0, 1)
            else:
                ax3.text(0.5, 0.5, 'No Strong Correlations Found', ha='center', va='center', 
                        transform=ax3.transAxes, fontsize=16, color='gray')
                ax3.set_title('Strong Correlations', fontsize=14, fontweight='bold')
            
            # 右下：相关性分布直方图
            ax4 = axes[1, 1]
            # 提取上三角矩阵的相关系数（排除对角线）
            upper_triangle = []
            for i in range(len(correlation_array)):
                for j in range(i + 1, len(correlation_array)):
                    upper_triangle.append(correlation_array[i, j])
            
            if upper_triangle:
                ax4.hist(upper_triangle, bins=20, alpha=0.7, color=self.colors['primary'], edgecolor='black')
                ax4.axvline(np.mean(upper_triangle), color='red', linestyle='--', 
                           label=f'Mean: {np.mean(upper_triangle):.3f}')
                ax4.axvline(0, color='black', linestyle='-', alpha=0.5)
                ax4.set_xlabel('Spearman Correlation Coefficient (ρ)', fontsize=12)
                ax4.set_ylabel('Frequency', fontsize=12)
                ax4.set_title('Distribution of Spearman Correlations', fontsize=14, fontweight='bold')
                ax4.legend()
                ax4.grid(True, alpha=0.3)
            else:
                ax4.text(0.5, 0.5, 'No Correlation Data', ha='center', va='center', 
                        transform=ax4.transAxes, fontsize=16, color='gray')
                ax4.set_title('Correlation Distribution', fontsize=14, fontweight='bold')
            
            plt.tight_layout(pad=3.0)
            
            image_b64 = self._fig_to_base64(fig)
            plt.close(fig)
            return image_b64
            
        except ImportError:
            # fallback to simple clustering analysis
            return self.generate_clustering_analysis(spearman_data)
    
    # ========== 聚类分析图表 ==========
    
    def generate_clustering_analysis(self, clustering_data: Dict[str, Any]) -> str:
        """生成聚类分析图表"""
        if not clustering_data or 'silhouette_scores' not in clustering_data:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No Clustering Data Available', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=16, color='gray')
            ax.set_title('Clustering Analysis', fontsize=16, fontweight='bold')
            ax.axis('off')
            
            image_b64 = self._fig_to_base64(fig)
            plt.close(fig)
            return image_b64
        
        silhouette_scores = clustering_data['silhouette_scores']
        k_values = list(silhouette_scores.keys())
        scores = [silhouette_scores[str(k)]['average_score'] for k in k_values]
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 绘制轮廓系数曲线
        line = ax.plot(k_values, scores, marker='o', linewidth=3, markersize=8, 
                      color=self.colors['primary'], markerfacecolor=self.colors['accent'])
        
        # 添加数值标签
        for k, score in zip(k_values, scores):
            ax.text(k, score + 0.02, f'{score:.3f}', ha='center', va='bottom',
                   fontsize=10, fontweight='bold')
        
        # 找到最优k值
        best_k = k_values[np.argmax(scores)]
        best_score = max(scores)
        
        ax.axvline(x=best_k, color='red', linestyle='--', alpha=0.7, 
                  label=f'Optimal K = {best_k} (Score: {best_score:.3f})')
        ax.scatter([best_k], [best_score], color='red', s=100, zorder=5)
        
        # 添加评估标准线
        ax.axhline(y=0.5, color='green', linestyle=':', alpha=0.7, label='Good Clustering (>0.5)')
        ax.axhline(y=0.7, color='blue', linestyle=':', alpha=0.7, label='Strong Clustering (>0.7)')
        
        ax.set_title('Clustering Analysis - Silhouette Score by K', fontsize=16, fontweight='bold')
        ax.set_xlabel('Number of Clusters (K)', fontsize=12)
        ax.set_ylabel('Average Silhouette Score', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_ylim(0, 1)
        
        plt.tight_layout()
        
        image_b64 = self._fig_to_base64(fig)
        plt.close(fig)
        return image_b64
    
    def generate_spearman_clustering_comprehensive(self, spearman_data: Dict[str, Any], correlation_matrix: List[List[float]], metric_names: List[str]) -> str:
        """生成2x2布局的Spearman聚类综合分析图"""
        try:
            from scipy.cluster.hierarchy import dendrogram
            import numpy as np
            
            # 创建2x2布局
            fig, axes = plt.subplots(2, 2, figsize=(20, 16))
            
            # 转换metric名称为可读格式
            readable_labels = [self._convert_metric_name_to_readable(name).replace('\n', ' ') 
                              for name in metric_names]
            
            # 左上：Spearman相关性热力图
            ax1 = axes[0, 0]
            correlation_array = np.array(correlation_matrix)
            im1 = ax1.imshow(correlation_array, cmap='RdBu_r', aspect='equal', vmin=-1, vmax=1)
            
            # 设置热力图标签和标题
            ax1.set_xticks(range(len(readable_labels)))
            ax1.set_yticks(range(len(readable_labels)))
            ax1.set_xticklabels(readable_labels, rotation=45, ha='right', fontsize=10)
            ax1.set_yticklabels(readable_labels, fontsize=10)
            ax1.set_title('Spearman Correlation Heatmap', fontsize=14, fontweight='bold', pad=20)
            
            # 添加相关系数文本
            for i in range(len(readable_labels)):
                for j in range(len(readable_labels)):
                    corr_val = correlation_array[i, j]
                    color = 'white' if abs(corr_val) > 0.5 else 'black'
                    ax1.text(j, i, f'{corr_val:.2f}', ha='center', va='center', 
                            color=color, fontsize=8, fontweight='bold')
            
            # 添加颜色条
            cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.8)
            cbar1.set_label('Correlation Coefficient', fontsize=10)
            
            # 右上：聚类树状图
            ax2 = axes[0, 1]
            if spearman_data and 'linkage_matrix' in spearman_data:
                dendrogram_result = dendrogram(spearman_data['linkage_matrix'],
                                             labels=readable_labels,
                                             ax=ax2,
                                             orientation='top',
                                             distance_sort='descending',
                                             show_leaf_counts=False,
                                             color_threshold=0.7,
                                             leaf_rotation=45)
                ax2.set_title('Spearman Hierarchical Clustering\n(Distance: 1 - |ρ|)', 
                             fontsize=14, fontweight='bold', pad=20)
                ax2.set_ylabel('Distance (1 - |ρ|)', fontsize=12)
                ax2.tick_params(axis='x', labelsize=10)
            else:
                ax2.text(0.5, 0.5, 'No Clustering Data', ha='center', va='center', 
                        transform=ax2.transAxes, fontsize=16, color='gray')
                ax2.set_title('Spearman Hierarchical Clustering', fontsize=14, fontweight='bold')
                ax2.axis('off')
            
            # 左下：强相关对条形图
            ax3 = axes[1, 0]
            strong_correlations = []
            correlation_values = []
            
            for i in range(len(metric_names)):
                for j in range(i + 1, len(metric_names)):
                    corr_val = abs(correlation_array[i, j])
                    if corr_val >= 0.3:  # 显示中等以上相关性
                        pair_label = f"{readable_labels[i][:15]}...\n× {readable_labels[j][:15]}..."
                        strong_correlations.append(pair_label)
                        correlation_values.append(corr_val)
            
            # 按相关性强度排序
            if strong_correlations:
                sorted_pairs = sorted(zip(strong_correlations, correlation_values), 
                                    key=lambda x: x[1], reverse=True)
                strong_correlations, correlation_values = zip(*sorted_pairs[:10])  # 显示前10个
                
                colors = ['#d62728' if val >= 0.7 else '#ff7f0e' if val >= 0.5 else '#2ca02c' 
                         for val in correlation_values]
                bars = ax3.barh(range(len(strong_correlations)), correlation_values, color=colors, alpha=0.8)
                
                # 添加数值标签
                for i, (bar, val) in enumerate(zip(bars, correlation_values)):
                    ax3.text(val + 0.01, bar.get_y() + bar.get_height()/2, 
                            f'{val:.3f}', va='center', fontsize=9, fontweight='bold')
                
                ax3.set_yticks(range(len(strong_correlations)))
                ax3.set_yticklabels(strong_correlations, fontsize=9)
                ax3.set_xlabel('|Spearman ρ|', fontsize=12)
                ax3.set_title('Strong Correlations (|ρ| ≥ 0.3)', fontsize=14, fontweight='bold')
                ax3.grid(True, alpha=0.3, axis='x')
                ax3.set_xlim(0, 1)
            else:
                ax3.text(0.5, 0.5, 'No Strong Correlations Found', ha='center', va='center', 
                        transform=ax3.transAxes, fontsize=16, color='gray')
                ax3.set_title('Strong Correlations', fontsize=14, fontweight='bold')
            
            # 右下：相关性分布直方图
            ax4 = axes[1, 1]
            # 提取上三角矩阵的相关系数（排除对角线）
            upper_triangle = []
            for i in range(len(correlation_array)):
                for j in range(i + 1, len(correlation_array)):
                    upper_triangle.append(correlation_array[i, j])
            
            if upper_triangle:
                ax4.hist(upper_triangle, bins=20, alpha=0.7, color=self.colors['primary'], edgecolor='black')
                ax4.axvline(np.mean(upper_triangle), color='red', linestyle='--', 
                           label=f'Mean: {np.mean(upper_triangle):.3f}')
                ax4.axvline(0, color='black', linestyle='-', alpha=0.5)
                ax4.set_xlabel('Spearman Correlation Coefficient (ρ)', fontsize=12)
                ax4.set_ylabel('Frequency', fontsize=12)
                ax4.set_title('Distribution of Spearman Correlations', fontsize=14, fontweight='bold')
                ax4.legend()
                ax4.grid(True, alpha=0.3)
            else:
                ax4.text(0.5, 0.5, 'No Correlation Data', ha='center', va='center', 
                        transform=ax4.transAxes, fontsize=16, color='gray')
                ax4.set_title('Correlation Distribution', fontsize=14, fontweight='bold')
            
            plt.tight_layout(pad=3.0)
            
            image_b64 = self._fig_to_base64(fig)
            plt.close(fig)
            return image_b64
            
        except ImportError:
            # fallback to simple clustering analysis
            return self.generate_clustering_analysis(spearman_data)
    
    def generate_cluster_distribution(self, cluster_labels: List[int], feature_data: Optional[List[List[float]]] = None) -> str:
        """生成聚类分布图"""
        if not cluster_labels:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No Cluster Labels Available', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=16, color='gray')
            ax.set_title('Cluster Distribution', fontsize=16, fontweight='bold')
            ax.axis('off')
            
            image_b64 = self._fig_to_base64(fig)
            plt.close(fig)
            return image_b64
        
        unique_clusters = sorted(set(cluster_labels))
        cluster_counts = [cluster_labels.count(c) for c in unique_clusters]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 左图：聚类大小分布饼图
        colors = plt.cm.Set3(np.linspace(0, 1, len(unique_clusters)))
        wedges, texts, autotexts = ax1.pie(cluster_counts, labels=[f'Cluster {c}' for c in unique_clusters],
                                          autopct='%1.1f%%', colors=colors, startangle=90)
        
        ax1.set_title('Cluster Size Distribution', fontsize=14, fontweight='bold')
        
        # 右图：聚类大小柱状图
        bars = ax2.bar(range(len(unique_clusters)), cluster_counts, 
                      color=colors, alpha=0.8, edgecolor='white')
        
        for i, (bar, count) in enumerate(zip(bars, cluster_counts)):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   str(count), ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        ax2.set_title('Cluster Sizes', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Cluster ID', fontsize=12)
        ax2.set_ylabel('Number of Samples', fontsize=12)
        ax2.set_xticks(range(len(unique_clusters)))
        ax2.set_xticklabels([f'Cluster {c}' for c in unique_clusters])
        ax2.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        image_b64 = self._fig_to_base64(fig)
        plt.close(fig)
        return image_b64
    
    def generate_spearman_clustering_comprehensive(self, spearman_data: Dict[str, Any], correlation_matrix: List[List[float]], metric_names: List[str]) -> str:
        """生成2x2布局的Spearman聚类综合分析图"""
        try:
            from scipy.cluster.hierarchy import dendrogram
            import numpy as np
            
            # 创建2x2布局
            fig, axes = plt.subplots(2, 2, figsize=(20, 16))
            
            # 转换metric名称为可读格式
            readable_labels = [self._convert_metric_name_to_readable(name).replace('\n', ' ') 
                              for name in metric_names]
            
            # 左上：Spearman相关性热力图
            ax1 = axes[0, 0]
            correlation_array = np.array(correlation_matrix)
            im1 = ax1.imshow(correlation_array, cmap='RdBu_r', aspect='equal', vmin=-1, vmax=1)
            
            # 设置热力图标签和标题
            ax1.set_xticks(range(len(readable_labels)))
            ax1.set_yticks(range(len(readable_labels)))
            ax1.set_xticklabels(readable_labels, rotation=45, ha='right', fontsize=10)
            ax1.set_yticklabels(readable_labels, fontsize=10)
            ax1.set_title('Spearman Correlation Heatmap', fontsize=14, fontweight='bold', pad=20)
            
            # 添加相关系数文本
            for i in range(len(readable_labels)):
                for j in range(len(readable_labels)):
                    corr_val = correlation_array[i, j]
                    color = 'white' if abs(corr_val) > 0.5 else 'black'
                    ax1.text(j, i, f'{corr_val:.2f}', ha='center', va='center', 
                            color=color, fontsize=8, fontweight='bold')
            
            # 添加颜色条
            cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.8)
            cbar1.set_label('Correlation Coefficient', fontsize=10)
            
            # 右上：聚类树状图
            ax2 = axes[0, 1]
            if spearman_data and 'linkage_matrix' in spearman_data:
                dendrogram_result = dendrogram(spearman_data['linkage_matrix'],
                                             labels=readable_labels,
                                             ax=ax2,
                                             orientation='top',
                                             distance_sort='descending',
                                             show_leaf_counts=False,
                                             color_threshold=0.7,
                                             leaf_rotation=45)
                ax2.set_title('Spearman Hierarchical Clustering\n(Distance: 1 - |ρ|)', 
                             fontsize=14, fontweight='bold', pad=20)
                ax2.set_ylabel('Distance (1 - |ρ|)', fontsize=12)
                ax2.tick_params(axis='x', labelsize=10)
            else:
                ax2.text(0.5, 0.5, 'No Clustering Data', ha='center', va='center', 
                        transform=ax2.transAxes, fontsize=16, color='gray')
                ax2.set_title('Spearman Hierarchical Clustering', fontsize=14, fontweight='bold')
                ax2.axis('off')
            
            # 左下：强相关对条形图
            ax3 = axes[1, 0]
            strong_correlations = []
            correlation_values = []
            
            for i in range(len(metric_names)):
                for j in range(i + 1, len(metric_names)):
                    corr_val = abs(correlation_array[i, j])
                    if corr_val >= 0.3:  # 显示中等以上相关性
                        pair_label = f"{readable_labels[i][:15]}...\n× {readable_labels[j][:15]}..."
                        strong_correlations.append(pair_label)
                        correlation_values.append(corr_val)
            
            # 按相关性强度排序
            if strong_correlations:
                sorted_pairs = sorted(zip(strong_correlations, correlation_values), 
                                    key=lambda x: x[1], reverse=True)
                strong_correlations, correlation_values = zip(*sorted_pairs[:10])  # 显示前10个
                
                colors = ['#d62728' if val >= 0.7 else '#ff7f0e' if val >= 0.5 else '#2ca02c' 
                         for val in correlation_values]
                bars = ax3.barh(range(len(strong_correlations)), correlation_values, color=colors, alpha=0.8)
                
                # 添加数值标签
                for i, (bar, val) in enumerate(zip(bars, correlation_values)):
                    ax3.text(val + 0.01, bar.get_y() + bar.get_height()/2, 
                            f'{val:.3f}', va='center', fontsize=9, fontweight='bold')
                
                ax3.set_yticks(range(len(strong_correlations)))
                ax3.set_yticklabels(strong_correlations, fontsize=9)
                ax3.set_xlabel('|Spearman ρ|', fontsize=12)
                ax3.set_title('Strong Correlations (|ρ| ≥ 0.3)', fontsize=14, fontweight='bold')
                ax3.grid(True, alpha=0.3, axis='x')
                ax3.set_xlim(0, 1)
            else:
                ax3.text(0.5, 0.5, 'No Strong Correlations Found', ha='center', va='center', 
                        transform=ax3.transAxes, fontsize=16, color='gray')
                ax3.set_title('Strong Correlations', fontsize=14, fontweight='bold')
            
            # 右下：相关性分布直方图
            ax4 = axes[1, 1]
            # 提取上三角矩阵的相关系数（排除对角线）
            upper_triangle = []
            for i in range(len(correlation_array)):
                for j in range(i + 1, len(correlation_array)):
                    upper_triangle.append(correlation_array[i, j])
            
            if upper_triangle:
                ax4.hist(upper_triangle, bins=20, alpha=0.7, color=self.colors['primary'], edgecolor='black')
                ax4.axvline(np.mean(upper_triangle), color='red', linestyle='--', 
                           label=f'Mean: {np.mean(upper_triangle):.3f}')
                ax4.axvline(0, color='black', linestyle='-', alpha=0.5)
                ax4.set_xlabel('Spearman Correlation Coefficient (ρ)', fontsize=12)
                ax4.set_ylabel('Frequency', fontsize=12)
                ax4.set_title('Distribution of Spearman Correlations', fontsize=14, fontweight='bold')
                ax4.legend()
                ax4.grid(True, alpha=0.3)
            else:
                ax4.text(0.5, 0.5, 'No Correlation Data', ha='center', va='center', 
                        transform=ax4.transAxes, fontsize=16, color='gray')
                ax4.set_title('Correlation Distribution', fontsize=14, fontweight='bold')
            
            plt.tight_layout(pad=3.0)
            
            image_b64 = self._fig_to_base64(fig)
            plt.close(fig)
            return image_b64
            
        except ImportError:
            # fallback to simple clustering analysis
            return self.generate_clustering_analysis(spearman_data)