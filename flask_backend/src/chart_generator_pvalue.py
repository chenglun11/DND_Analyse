"""
P值分析相关的图表生成扩展模块
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
import warnings
warnings.filterwarnings('ignore')

# 继承ChartGenerator类
from .chart_generator import ChartGenerator

class PValueChartGenerator(ChartGenerator):
    """P值分析图表生成器"""
    
    def generate_pvalue_heatmap(self, pvalue_matrix: List[List[float]], 
                               metric_names: List[str], title: str = "Statistical Significance Analysis") -> str:
        """生成P值热力图显示统计显著性"""
        # 转换为pandas DataFrame
        df_pval = pd.DataFrame(pvalue_matrix, 
                             index=metric_names, 
                             columns=metric_names)
        
        # 创建显著性标记矩阵
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
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # 使用log变换处理P值，避免数值过小的问题
        log_pvals = -np.log10(df_pval + 1e-100)  # 添加小常数避免log(0)
        
        # 创建mask只显示下三角
        mask = np.triu(np.ones_like(df_pval, dtype=bool), k=1)
        
        # 生成热力图
        heatmap = sns.heatmap(log_pvals, 
                            mask=mask,
                            annot=significance_labels,
                            cmap='viridis',
                            square=True, 
                            fmt='',
                            cbar_kws={"shrink": .8, "label": "-log10(p-value)"},
                            annot_kws={'size': 10, 'fontweight': 'bold', 'color': 'white'},
                            ax=ax)
        
        # 美化图表
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('')
        ax.set_ylabel('')
        
        # 旋转标签以提高可读性
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        
        # 添加显著性说明
        legend_text = "Significance levels:\n*** p < 0.001\n** p < 0.01\n* p < 0.05"
        ax.text(1.02, 0.5, legend_text, transform=ax.transAxes, 
               fontsize=10, verticalalignment='center',
               bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        
        plt.tight_layout()
        
        # 转换为base64
        image_b64 = self._fig_to_base64(fig)
        plt.close(fig)
        
        return image_b64
    
    def generate_significance_comparison(self, pvalue_matrix: List[List[float]], 
                                       bonferroni_matrix: List[List[float]], 
                                       fdr_matrix: List[List[float]], 
                                       metric_names: List[str]) -> str:
        """生成多重校正比较图"""
        # 提取上三角的P值（排除对角线）
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
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # 散点图比较原始P值与校正P值
        indices = np.arange(len(pair_labels))
        
        # 上图：P值比较
        ax1.scatter(indices, [-np.log10(p + 1e-100) for p in raw_pvals], 
                   alpha=0.7, label='Raw p-values', color='blue', s=50)
        ax1.scatter(indices, [-np.log10(p + 1e-100) for p in bonferroni_pvals], 
                   alpha=0.7, label='Bonferroni corrected', color='red', s=50)
        ax1.scatter(indices, [-np.log10(p + 1e-100) for p in fdr_pvals], 
                   alpha=0.7, label='FDR corrected', color='green', s=50)
        
        # 添加显著性阈值线
        ax1.axhline(y=-np.log10(0.05), color='gray', linestyle='--', alpha=0.5, label='α = 0.05')
        ax1.axhline(y=-np.log10(0.01), color='gray', linestyle=':', alpha=0.5, label='α = 0.01')
        
        ax1.set_title('Multiple Testing Correction Comparison', fontsize=16, fontweight='bold')
        ax1.set_ylabel('-log10(p-value)', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 下图：显著性计数
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
        
        # 在柱子上添加数值标签
        for i, (raw, bonf, fdr) in enumerate(zip(raw_counts, bonf_counts, fdr_counts)):
            ax2.text(i - width, raw + 0.1, str(raw), ha='center', va='bottom', fontweight='bold')
            ax2.text(i, bonf + 0.1, str(bonf), ha='center', va='bottom', fontweight='bold')
            ax2.text(i + width, fdr + 0.1, str(fdr), ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        # 转换为base64
        image_b64 = self._fig_to_base64(fig)
        plt.close(fig)
        
        return image_b64
    
    def generate_consistency_analysis(self, correlation_matrix: List[List[float]], 
                                    pvalue_matrix: List[List[float]], 
                                    metric_names: List[str]) -> str:
        """生成相关性与显著性一致性分析图"""
        # 提取上三角的数据
        correlations = []
        pvalues = []
        
        for i in range(len(metric_names)):
            for j in range(i + 1, len(metric_names)):
                correlations.append(abs(correlation_matrix[i][j]))
                pvalues.append(pvalue_matrix[i][j])
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 左图：相关性强度 vs P值散点图
        colors = []
        sizes = []
        for p in pvalues:
            if p < 0.001:
                colors.append('#FF0000')  # 红色 - 极显著
                sizes.append(100)
            elif p < 0.01:
                colors.append('#FF8800')  # 橙色 - 高显著
                sizes.append(80)
            elif p < 0.05:
                colors.append('#FFDD00')  # 黄色 - 显著
                sizes.append(60)
            else:
                colors.append('#CCCCCC')  # 灰色 - 不显著
                sizes.append(40)
        
        scatter = ax1.scatter(correlations, [-np.log10(p + 1e-100) for p in pvalues], 
                            c=colors, s=sizes, alpha=0.7, edgecolors='black', linewidth=0.5)
        
        ax1.set_xlabel('Correlation Strength (|r|)', fontsize=12)
        ax1.set_ylabel('-log10(p-value)', fontsize=12)
        ax1.set_title('Correlation Strength vs Statistical Significance', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # 添加显著性阈值线
        ax1.axhline(y=-np.log10(0.05), color='gray', linestyle='--', alpha=0.7, label='α = 0.05')
        ax1.axhline(y=-np.log10(0.01), color='gray', linestyle=':', alpha=0.7, label='α = 0.01')
        ax1.legend()
        
        # 右图：相关性强度分布按显著性水平分组
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
        
        # 转换为base64
        image_b64 = self._fig_to_base64(fig)
        plt.close(fig)
        
        return image_b64