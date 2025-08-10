"""
图表生成模块 - 使用matplotlib和seaborn生成美观的相关性分析图表
"""

import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import io
import base64
from typing import List, Dict, Tuple, Optional
import matplotlib.font_manager as fm
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体支持
try:
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'SimHei', 'Arial Unicode MS', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False
except:
    # 如果字体设置失败，使用默认字体
    pass

# 设置现代化的样式
try:
    plt.style.use('seaborn-v0_8')
except:
    # 如果seaborn样式不可用，使用默认样式
    pass
    
sns.set_palette("husl")

class ChartGenerator:
    """图表生成器"""
    
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
    
    def generate_correlation_heatmap(self, correlation_matrix: List[List[float]], 
                                   metric_names: List[str]) -> str:
        """生成相关性热力图"""
        # 转换为pandas DataFrame
        df_corr = pd.DataFrame(correlation_matrix, 
                             index=metric_names, 
                             columns=metric_names)
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 生成热力图，使用更美观的配色
        mask = np.triu(np.ones_like(df_corr, dtype=bool), k=1)  # 只显示下三角
        heatmap = sns.heatmap(df_corr, 
                            mask=mask,
                            annot=True, 
                            cmap='RdYlBu_r', 
                            center=0,
                            square=True, 
                            fmt='.3f',
                            cbar_kws={"shrink": .8, "label": "Correlation Coefficient"},
                            annot_kws={'size': 9},
                            ax=ax)
        
        # 美化图表
        ax.set_title('Dungeon Quality Metrics Correlation Analysis', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('')
        ax.set_ylabel('')
        
        # 旋转标签以提高可读性
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        
        # 调整布局
        plt.tight_layout()
        
        # 转换为base64
        image_b64 = self._fig_to_base64(fig)
        plt.close(fig)
        
        return image_b64
    
    def generate_scatter_plot(self, correlation_matrix: List[List[float]], 
                            metric_names: List[str]) -> str:
        """生成相关性散点图"""
        # 提取所有相关系数对
        correlations = []
        pairs = []
        
        for i in range(len(metric_names)):
            for j in range(i + 1, len(metric_names)):
                correlations.append(correlation_matrix[i][j])
                pairs.append(f"{metric_names[i]} × {metric_names[j]}")
        
        # 创建散点图
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 根据相关性强度设置颜色和大小
        colors = []
        sizes = []
        for corr in correlations:
            abs_corr = abs(corr)
            if abs_corr > 0.7:
                colors.append('#EF4444')  # 强相关 - 红色
                sizes.append(100 + abs_corr * 100)
            elif abs_corr > 0.3:
                colors.append('#F59E0B')  # 中等相关 - 橙色
                sizes.append(80 + abs_corr * 80)
            else:
                colors.append('#6B7280')  # 弱相关 - 灰色
                sizes.append(50 + abs_corr * 50)
        
        # 绘制散点
        scatter = ax.scatter(range(len(correlations)), correlations, 
                           c=colors, s=sizes, alpha=0.7, edgecolors='white', linewidth=1)
        
        # 添加水平参考线
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax.axhline(y=0.7, color='red', linestyle='--', alpha=0.5, label='Strong Correlation (r=0.7)')
        ax.axhline(y=0.3, color='orange', linestyle='--', alpha=0.5, label='Moderate Correlation (r=0.3)')
        ax.axhline(y=-0.3, color='orange', linestyle='--', alpha=0.5)
        ax.axhline(y=-0.7, color='red', linestyle='--', alpha=0.5)
        
        # 美化图表
        ax.set_title('Metric Correlation Distribution', fontsize=16, fontweight='bold')
        ax.set_xlabel('Metric Pairs', fontsize=12)
        ax.set_ylabel('Correlation Coefficient', fontsize=12)
        ax.set_ylim(-1.1, 1.1)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # 设置x轴标签（只显示部分，避免过于拥挤）
        step = max(1, len(pairs) // 10)
        selected_indices = range(0, len(pairs), step)
        ax.set_xticks(selected_indices)
        ax.set_xticklabels([pairs[i][:20] + '...' if len(pairs[i]) > 20 else pairs[i] 
                           for i in selected_indices], rotation=45, ha='right')
        
        plt.tight_layout()
        
        # 转换为base64
        image_b64 = self._fig_to_base64(fig)
        plt.close(fig)
        
        return image_b64
    
    def generate_network_graph(self, correlation_matrix: List[List[float]], 
                             metric_names: List[str]) -> str:
        """生成网络关系图"""
        try:
            import networkx as nx
        except ImportError:
            # 如果没有networkx，生成一个简单的雷达图
            return self.generate_radar_chart(correlation_matrix, metric_names)
        
        # 创建网络图
        G = nx.Graph()
        
        # 添加节点
        for name in metric_names:
            G.add_node(name)
        
        # 添加边（只添加强相关和中等相关）
        for i in range(len(metric_names)):
            for j in range(i + 1, len(metric_names)):
                corr = abs(correlation_matrix[i][j])
                if corr > 0.3:  # 只显示中等以上相关
                    G.add_edge(metric_names[i], metric_names[j], weight=corr)
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # 设置布局
        pos = nx.spring_layout(G, k=3, iterations=50)
        
        # 绘制边
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
        
        # 绘制节点
        nx.draw_networkx_nodes(G, pos, node_color=self.colors['primary'], 
                             node_size=1000, alpha=0.8, ax=ax)
        
        # 绘制标签
        nx.draw_networkx_labels(G, pos, font_size=8, font_color='white', 
                              font_weight='bold', ax=ax)
        
        ax.set_title('Metric Relationship Network', fontsize=16, fontweight='bold')
        ax.axis('off')
        
        # 添加图例
        legend_elements = [
            plt.Line2D([0], [0], color='#EF4444', lw=3, label='Strong Correlation (r>0.7)'),
            plt.Line2D([0], [0], color='#F59E0B', lw=2, label='Moderate-Strong (r>0.5)'),
            plt.Line2D([0], [0], color='#6B7280', lw=1, label='Moderate Correlation (r>0.3)')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        
        # 转换为base64
        image_b64 = self._fig_to_base64(fig)
        plt.close(fig)
        
        return image_b64
    
    def generate_radar_chart(self, correlation_matrix: List[List[float]], 
                           metric_names: List[str]) -> str:
        """生成雷达图（作为网络图的替代）"""
        # 计算每个指标的平均相关度
        avg_correlations = []
        for i in range(len(metric_names)):
            correlations = [abs(correlation_matrix[i][j]) for j in range(len(metric_names)) if i != j]
            avg_correlations.append(np.mean(correlations))
        
        # 创建雷达图
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        # 计算角度
        angles = np.linspace(0, 2 * np.pi, len(metric_names), endpoint=False).tolist()
        angles += angles[:1]  # 闭合图形
        
        # 数据闭合
        values = avg_correlations + avg_correlations[:1]
        
        # 绘制雷达图
        ax.plot(angles, values, color=self.colors['primary'], linewidth=2)
        ax.fill(angles, values, color=self.colors['primary'], alpha=0.3)
        
        # 设置标签
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metric_names, fontsize=10)
        
        # 设置径向轴
        ax.set_ylim(0, 1)
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=8)
        ax.grid(True)
        
        ax.set_title('Metric Average Correlation Radar Chart', fontsize=16, fontweight='bold', pad=30)
        
        plt.tight_layout()
        
        # 转换为base64
        image_b64 = self._fig_to_base64(fig)
        plt.close(fig)
        
        return image_b64
    
    def generate_bar_chart(self, correlation_pairs: List[Dict], title: str) -> str:
        """生成相关性柱状图"""
        if not correlation_pairs:
            # 生成空图表
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No Data Available', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=16, color='gray')
            ax.set_title(title, fontsize=16, fontweight='bold')
            ax.axis('off')
            
            image_b64 = self._fig_to_base64(fig)
            plt.close(fig)
            return image_b64
        
        # 准备数据
        pairs = [pair['pair'] for pair in correlation_pairs]
        values = [pair['value'] for pair in correlation_pairs]
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 根据值设置颜色
        colors = []
        for val in values:
            if abs(val) > 0.7:
                colors.append('#EF4444')  # 强相关 - 红色
            elif abs(val) > 0.5:
                colors.append('#F59E0B')  # 中强相关 - 橙色  
            else:
                colors.append(self.colors['primary'])  # 其他 - 主色
        
        # 绘制柱状图
        bars = ax.bar(range(len(pairs)), values, color=colors, alpha=0.8, edgecolor='white')
        
        # 在柱子上添加数值标签
        for i, (bar, val) in enumerate(zip(bars, values)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f'{val:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # 美化图表
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_ylabel('Correlation Coefficient', fontsize=12)
        ax.set_xlabel('Metric Pairs', fontsize=12)
        
        # 设置x轴标签
        ax.set_xticks(range(len(pairs)))
        ax.set_xticklabels([pair.replace(' ↔ ', '\n×\n') for pair in pairs], 
                          rotation=45, ha='right', fontsize=9)
        
        # 添加网格
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_axisbelow(True)
        
        # 设置y轴范围
        ax.set_ylim(0, max(values) * 1.1)
        
        plt.tight_layout()
        
        # 转换为base64
        image_b64 = self._fig_to_base64(fig)
        plt.close(fig)
        
        return image_b64