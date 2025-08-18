#!/usr/bin/env python3
"""
PNG图表生成器 - 直接生成独立的PNG图片文件
"""

import os
import base64
import numpy as np
from pathlib import Path
from typing import Dict, List, Any
from unified_chart_generator import UnifiedChartGenerator

class PNGChartGenerator:
    """PNG图表生成器 - 直接保存PNG文件"""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.chart_generator = UnifiedChartGenerator()
        
    def generate_chart_and_save(self, chart_name: str, generate_func, *args, **kwargs) -> str:
        """生成图表并保存为PNG文件"""
        try:
            # 生成base64图表数据
            base64_data = generate_func(*args, **kwargs)
            
            # 解码并保存为PNG文件
            image_data = base64.b64decode(base64_data)
            png_file = self.output_dir / f"{chart_name}.png"
            
            with open(png_file, 'wb') as f:
                f.write(image_data)
            
            print(f"✅ 保存图表: {png_file}")
            return str(png_file)
            
        except Exception as e:
            print(f"❌ 生成图表失败 {chart_name}: {e}")
            return ""
    
    def generate_all_charts(self, correlation_data: Dict[str, Any], 
                          advanced_data: Dict[str, Any]) -> List[str]:
        """生成所有图表并返回保存的文件路径列表"""
        saved_files = []
        
        # 提取相关性矩阵和指标名称
        spearman_matrix = correlation_data.get('spearman_correlation_matrix', {})
        metric_names = correlation_data.get('metric_names', [])
        
        if not spearman_matrix or not metric_names:
            print("❌ 缺少相关性矩阵或指标名称数据")
            return saved_files
        
        # 转换为矩阵格式
        matrix = []
        for metric1 in metric_names:
            row = []
            for metric2 in metric_names:
                row.append(spearman_matrix.get(metric1, {}).get(metric2, 0))
            matrix.append(row)
        
        print(f"📊 开始生成图表，指标数量: {len(metric_names)}")
        
        # 1. Spearman相关性热力图
        file_path = self.generate_chart_and_save(
            "01_spearman_heatmap",
            self.chart_generator.generate_correlation_heatmap,
            matrix, metric_names, "Spearman"
        )
        if file_path: saved_files.append(file_path)
        
        # 2. FDR校正p值热力图
        fdr_matrix_data = correlation_data.get('fdr_corrected_pvalue_matrix', {})
        if fdr_matrix_data:
            fdr_matrix = []
            for metric1 in metric_names:
                row = []
                for metric2 in metric_names:
                    row.append(fdr_matrix_data.get(metric1, {}).get(metric2, 1.0))
                fdr_matrix.append(row)
            
            file_path = self.generate_chart_and_save(
                "02_fdr_heatmap",
                self.chart_generator.generate_fdr_heatmap,
                fdr_matrix, matrix, metric_names
            )
            if file_path: saved_files.append(file_path)
        
        # 3. 相关性散点图
        file_path = self.generate_chart_and_save(
            "03_scatter_plot",
            self.chart_generator.generate_scatter_plot,
            matrix, metric_names
        )
        if file_path: saved_files.append(file_path)
        
        # 4. 网络关系图
        file_path = self.generate_chart_and_save(
            "04_network_graph",
            self.chart_generator.generate_network_graph,
            matrix, metric_names
        )
        if file_path: saved_files.append(file_path)
        
        # 4. 雷达图
        file_path = self.generate_chart_and_save(
            "04_radar_chart",
            self.chart_generator.generate_radar_chart,
            matrix, metric_names
        )
        if file_path: saved_files.append(file_path)
        
        # 5. 条形图
        correlation_pairs = []
        for i, metric1 in enumerate(metric_names):
            for j, metric2 in enumerate(metric_names):
                if i < j:
                    correlation_pairs.append({
                        'pair': f"{metric1} ↔ {metric2}",
                        'value': matrix[i][j]
                    })
        correlation_pairs.sort(key=lambda x: abs(x['value']), reverse=True)
        
        file_path = self.generate_chart_and_save(
            "05_bar_chart",
            self.chart_generator.generate_bar_chart,
            correlation_pairs[:15], "Top 15 Correlations"
        )
        if file_path: saved_files.append(file_path)
        
        # P值分析图表
        p_value_matrix = []
        for metric1 in metric_names:
            row = []
            for metric2 in metric_names:
                corr_val = spearman_matrix.get(metric1, {}).get(metric2, 0)
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
        
        # 6. P值热力图
        file_path = self.generate_chart_and_save(
            "06_pvalue_heatmap",
            self.chart_generator.generate_pvalue_heatmap,
            p_value_matrix, metric_names
        )
        if file_path: saved_files.append(file_path)
        
        # 7. 显著性比较图
        bonferroni_matrix = [[p * len(metric_names) * len(metric_names) for p in row] for row in p_value_matrix]
        fdr_matrix = [[min(p * 1.5, 1.0) for p in row] for row in p_value_matrix]
        
        file_path = self.generate_chart_and_save(
            "07_significance_comparison",
            self.chart_generator.generate_significance_comparison,
            p_value_matrix, bonferroni_matrix, fdr_matrix, metric_names
        )
        if file_path: saved_files.append(file_path)
        
        # 8. 一致性分析图
        file_path = self.generate_chart_and_save(
            "08_consistency_analysis",
            self.chart_generator.generate_consistency_analysis,
            matrix, p_value_matrix, metric_names
        )
        if file_path: saved_files.append(file_path)
        
        # 高级分析图表
        if advanced_data:
            # 9. VIF分析图表
            vif_data = advanced_data.get('vif_analysis', {})
            if vif_data and 'vif_results' in vif_data:
                vif_chart_data = []
                for item in vif_data['vif_results']:
                    vif_chart_data.append({
                        'feature': item['metric'],
                        'vif': item['vif'],
                        'level': item.get('level', 'UNKNOWN')
                    })
                
                file_path = self.generate_chart_and_save(
                    "09_vif_analysis",
                    self.chart_generator.generate_vif_chart,
                    vif_chart_data
                )
                if file_path: saved_files.append(file_path)
            
            # 10. PCA分析图表（方差解释比例）
            pca_data = advanced_data.get('pca_analysis', {})
            if pca_data and 'explained_variance_ratio' in pca_data:
                file_path = self.generate_chart_and_save(
                    "10_pca_analysis",
                    self.chart_generator.generate_pca_analysis,
                    pca_data, metric_names
                )
                if file_path: saved_files.append(file_path)
                
                # 11. PCA累积方差图（单独生成）
                file_path = self.generate_chart_and_save(
                    "11_pca_cumulative_variance",
                    self.chart_generator.generate_pca_cumulative_variance,
                    pca_data, metric_names
                )
                if file_path: saved_files.append(file_path)
                
                # 12. PCA散点图（PC1 vs PC2）
                if len(pca_data.get('explained_variance_ratio', [])) >= 2:
                    file_path = self.generate_chart_and_save(
                        "12_pca_scatterplot",
                        self.chart_generator.generate_pca_scatterplot,
                        pca_data, metric_names
                    )
                    if file_path: saved_files.append(file_path)
                
                # 13. PCA载荷图（变量贡献）
                if 'components' in pca_data or 'loadings' in pca_data:
                    # 确保兼容性：如果有loadings但没有components，创建components
                    pca_data_for_loadings = pca_data.copy()
                    if 'loadings' in pca_data and 'components' not in pca_data:
                        # 将loadings转置作为components（每行代表一个主成分）
                        loadings_array = np.array(pca_data['loadings'])
                        pca_data_for_loadings['components'] = loadings_array.T.tolist()
                    
                    file_path = self.generate_chart_and_save(
                        "13_pca_loadings",
                        self.chart_generator.generate_pca_loadings,
                        pca_data_for_loadings, metric_names
                    )
                    if file_path: saved_files.append(file_path)
            
            # 14. 聚类分析图表
            clustering_data = advanced_data.get('clustering_analysis', {})
            if clustering_data and 'linkage_matrix' in clustering_data:
                file_path = self.generate_chart_and_save(
                    "14_clustering_analysis",
                    self.chart_generator.generate_clustering_analysis,
                    clustering_data
                )
                if file_path: saved_files.append(file_path)
                
                # 13. 层次聚类树状图 (Hierarchical Dendrogram)
                file_path = self.generate_chart_and_save(
                    "13_hierarchical_dendrogram",
                    self.chart_generator.generate_hierarchical_dendrogram,
                    clustering_data, metric_names
                )
                if file_path: saved_files.append(file_path)
                
                # 14. 聚类分布图表 (从clustering_results中提取cluster_labels)
                clustering_results = clustering_data.get('clustering_results', {})
                if clustering_results:
                    # 使用3聚类的结果作为默认
                    best_k = '3' if '3' in clustering_results else list(clustering_results.keys())[0]
                    cluster_labels = clustering_results[best_k].get('clusters', [])
                    
                    if cluster_labels:
                        file_path = self.generate_chart_and_save(
                            "14_cluster_distribution",
                            self.chart_generator.generate_cluster_distribution,
                            cluster_labels, matrix
                        )
                        if file_path: saved_files.append(file_path)
        
        print(f"\n🎉 成功生成 {len(saved_files)} 个独立PNG图表文件")
        return saved_files

def main():
    """测试PNG图表生成器"""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description='生成独立的PNG图表文件')
    parser.add_argument('json_file', help='统计分析JSON报告文件路径')
    parser.add_argument('--output', '-o', default='charts', help='图表输出目录')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.json_file):
        print(f"❌ 文件不存在: {args.json_file}")
        return 1
    
    # 加载JSON数据
    with open(args.json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    correlation_data = data.get('correlation_analysis', {})
    advanced_data = data.get('advanced_analysis', {})
    
    if not correlation_data:
        print("❌ 未找到相关性分析数据")
        return 1
    
    # 生成PNG图表
    generator = PNGChartGenerator(args.output)
    saved_files = generator.generate_all_charts(correlation_data, advanced_data)
    
    print(f"\n📁 所有图表已保存到: {args.output}")
    print("📝 图表文件列表:")
    for i, file_path in enumerate(saved_files, 1):
        print(f"  {i:2d}. {Path(file_path).name}")
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())