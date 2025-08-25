#!/usr/bin/env python3
"""
统计报告生成器 - 生成Markdown格式的统计分析报告
"""

import os
import json
import argparse
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class StatisticalReportGenerator:
    """统计报告生成器 - Markdown格式"""
    
    def __init__(self, data_path: str):
        """
        初始化报告生成器
        
        Args:
            data_path: 统计分析报告JSON文件路径
        """
        self.data_path = data_path
        self.data = self.load_data()
        
    def load_data(self) -> Dict[str, Any]:
        """加载统计分析数据"""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Failed to load data from {self.data_path}: {e}")
    
    def format_p_value(self, p_value: float) -> str:
        """格式化p值显示"""
        if p_value < 0.001:
            return "< 0.001"
        elif p_value < 0.01:
            return f"{p_value:.3f}"
        else:
            return f"{p_value:.3f}"
    
    def generate_markdown_report(self) -> str:
        """生成完整的Markdown报告"""
        
        # 提取数据
        analysis_summary = self.data.get('analysis_summary', {})
        desc_stats = self.data.get('descriptive_statistics', {})
        correlation_analysis = self.data.get('correlation_analysis', {})
        group_comparison = self.data.get('group_comparison_analysis', {})
        advanced_analysis = self.data.get('advanced_analysis', {})
        
        # 开始构建Markdown
        md = f"""# Statistical Analysis Report

**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Data Source:** {os.path.basename(self.data_path)}  
**Analysis Type:** Comprehensive Statistical Analysis of Dungeon Quality Metrics

---

## 📊 Executive Summary

| Metric | Value |
|--------|-------|
| **Maps Analyzed** | {analysis_summary.get('total_maps', 0)} |
| **Quality Metrics** | {analysis_summary.get('metrics_analyzed', 0)} |
| **Strong Correlations** | {analysis_summary.get('strong_correlations_count', 0)} |
| **Moderate Correlations** | {analysis_summary.get('moderate_correlations_count', 0)} |
| **Normality Tests Performed** | {analysis_summary.get('normality_tests_performed', 0)} |
| **Normal Distributions** | {analysis_summary.get('normally_distributed_metrics', 0)} |
| **Non-Normal Distributions** | {analysis_summary.get('non_normally_distributed_metrics', 0)} |
| **Significant Group Differences** | {analysis_summary.get('significant_group_differences', 0)}/{analysis_summary.get('normality_tests_performed', 0)} ({analysis_summary.get('proportion_with_group_differences', 0)*100:.1f}%) |

"""

        # 描述性统计
        if desc_stats:
            md += """## 📈 Descriptive Statistics

| Metric | Mean | Std Dev | Min | Max | Median | Q25 | Q75 |
|--------|------|---------|-----|-----|---------|-----|-----|
"""
            for metric, stats in desc_stats.items():
                if metric != 'overall_score':
                    md += f"| **{metric.replace('_', ' ').title()}** | {stats.get('mean', 0):.3f} | {stats.get('std', 0):.3f} | {stats.get('min', 0):.3f} | {stats.get('max', 0):.3f} | {stats.get('median', 0):.3f} | {stats.get('q25', 0):.3f} | {stats.get('q75', 0):.3f} |\n"
            
            md += "\n"

        # 正态性检验和组间比较
        if group_comparison:
            summary = group_comparison.get('summary', {})
            md += f"""## 🔬 Distribution Analysis & Group Comparisons

### Summary Statistics

| Statistic | Value |
|-----------|-------|
| **Total Metrics Tested** | {summary.get('total_metrics_tested', 0)} |
| **Normal Distributions** | {summary.get('normally_distributed_metrics', 0)} |
| **Non-Normal Distributions** | {summary.get('non_normally_distributed_metrics', 0)} |
| **ANOVA Tests Performed** | {summary.get('anova_tests_performed', 0)} |
| **Kruskal-Wallis Tests Performed** | {summary.get('kruskal_wallis_tests_performed', 0)} |
| **Significant Differences Found** | {summary.get('significant_differences_found', 0)} |
| **Proportion Significant** | {summary.get('proportion_significant', 0)*100:.1f}% |

### Detailed Results by Metric

| Metric | Distribution | Test Used | Test Statistic | P-value | Significant? | Post-hoc Pairs |
|--------|--------------|-----------|----------------|---------|--------------|----------------|
"""
            
            normality_tests = group_comparison.get('normality_tests', {})
            statistical_tests = group_comparison.get('statistical_tests', {})
            
            for metric_name in normality_tests.keys():
                norm_data = normality_tests[metric_name]
                stat_data = statistical_tests.get(metric_name, {})
                
                is_normal = norm_data.get('is_normal', False)
                test_used = stat_data.get('test_used', 'Unknown').replace('_', ' ').title()
                test_stat = stat_data.get('h_statistic') or stat_data.get('f_statistic', 0)
                p_value = stat_data.get('p_value', 1.0)
                is_significant = stat_data.get('significant_at_05', False)
                
                # Post-hoc结果
                post_hoc = stat_data.get('post_hoc', {})
                sig_pairs_count = len(post_hoc.get('significant_pairs', [])) if post_hoc else 0
                
                distribution = "Normal ✅" if is_normal else "Non-normal ❌"
                significance = "Yes ✅" if is_significant else "No ❌"
                post_hoc_str = f"{sig_pairs_count} pairs" if sig_pairs_count > 0 else "None"
                
                md += f"| **{metric_name.replace('_', ' ').title()}** | {distribution} | {test_used} | {test_stat:.3f} | {self.format_p_value(p_value)} | {significance} | {post_hoc_str} |\n"
            
            md += "\n"

        # 相关性分析
        if correlation_analysis:
            md += """## 🔗 Correlation Analysis

"""
            
            # 逻辑一致性
            consistency_score = correlation_analysis.get('logical_consistency_score', 0)
            expected_found = correlation_analysis.get('expected_correlations_found', 0)
            total_expected = correlation_analysis.get('total_expected_correlations', 0)
            inconsistencies = correlation_analysis.get('logical_inconsistencies', [])
            
            md += f"""### Logical Consistency Analysis

- **Consistency Score:** {consistency_score:.3f}
- **Expected Correlations Found:** {expected_found}/{total_expected}
- **Logical Inconsistencies:** {len(inconsistencies)}

"""
            
            if inconsistencies:
                md += """### Logical Inconsistencies

| Metric 1 | Metric 2 | Expected | Actual ρ | FDR P-value |
|----------|----------|----------|----------|-------------|
"""
                for inc in inconsistencies[:5]:  # 只显示前5个
                    md += f"| **{inc['metric1'].replace('_', ' ').title()}** | **{inc['metric2'].replace('_', ' ').title()}** | {inc['expected']} | {inc['actual_spearman']:.3f} | {self.format_p_value(inc['fdr_p_value'])} |\n"
                md += "\n"
            
            # 强相关关系
            strong_corrs = correlation_analysis.get('strong_correlations', [])
            if strong_corrs:
                md += """### Strong Correlations (|ρ| ≥ 0.7)

| Metric 1 | Metric 2 | Spearman ρ | FDR P-value | Expected | Consistent? |
|----------|----------|-------------|-------------|----------|-------------|
"""
                for corr in strong_corrs:
                    rho = corr.get('spearman_correlation', 0)
                    p_val = corr.get('fdr_p_value', 1.0)
                    expected = corr.get('expected_direction', 'none')
                    consistent = "✅" if corr.get('logically_consistent', True) else "⚠️"
                    
                    md += f"| **{corr.get('metric1', '').replace('_', ' ').title()}** | **{corr.get('metric2', '').replace('_', ' ').title()}** | **{rho:.3f}** | {self.format_p_value(p_val)} | {expected} | {consistent} |\n"
                md += "\n"
            
            # 与总分的相关性
            overall_corrs = correlation_analysis.get('overall_score_correlations', [])
            if overall_corrs:
                # 按相关性强度排序
                overall_corrs.sort(key=lambda x: abs(x.get('spearman_correlation', 0)), reverse=True)
                
                md += """### Top Correlations with Overall Score

| Metric | Spearman ρ | P-value | Significance |
|--------|-------------|---------|--------------|
"""
                for corr in overall_corrs[:10]:  # 前10个
                    rho = corr.get('spearman_correlation', 0)
                    p_val = corr.get('spearman_p_value', 1.0)
                    is_sig = "✅ Significant" if p_val < 0.05 else "❌ Not significant"
                    
                    md += f"| **{corr.get('metric', '').replace('_', ' ').title()}** | **{rho:.3f}** | {self.format_p_value(p_val)} | {is_sig} |\n"
                md += "\n"

        # 高级分析
        if advanced_analysis:
            md += """## 🧠 Advanced Analysis

"""
            
            # VIF分析
            vif_data = advanced_analysis.get('vif_analysis', {})
            if vif_data:
                md += f"""### Multicollinearity Analysis (VIF)

| Statistic | Value |
|-----------|-------|
| **Critical VIF (>10)** | {vif_data.get('critical_vif_count', 0)} metrics |
| **High VIF (>5)** | {vif_data.get('high_vif_count', 0)} metrics |
| **Maximum VIF** | {vif_data.get('max_vif', 0):.2f} |

"""
                
                # 详细VIF结果
                vif_results = vif_data.get('vif_results', [])
                if vif_results:
                    md += """#### Detailed VIF Results

| Metric | VIF Score | Level |
|--------|-----------|-------|
"""
                    for vif in vif_results:
                        level_emoji = "🔴" if vif['vif'] > 10 else ("🟡" if vif['vif'] > 5 else "🟢")
                        md += f"| **{vif['metric'].replace('_', ' ').title()}** | {vif['vif']:.2f} | {level_emoji} {vif.get('level', 'OK')} |\n"
                    md += "\n"
            
            # PCA分析
            pca_data = advanced_analysis.get('pca_analysis', {})
            if pca_data and 'explained_variance_ratio' in pca_data:
                explained_var = pca_data['explained_variance_ratio']
                if len(explained_var) >= 2:
                    pc1_var = explained_var[0]
                    pc2_var = explained_var[1]
                    cumulative_2pc = pc1_var + pc2_var
                    
                    md += f"""### Principal Component Analysis

| Component | Variance Explained | Cumulative |
|-----------|-------------------|------------|
| **PC1** | {pc1_var*100:.1f}% | {pc1_var*100:.1f}% |
| **PC2** | {pc2_var*100:.1f}% | {cumulative_2pc*100:.1f}% |

**Key Finding:** First 2 principal components explain **{cumulative_2pc*100:.1f}%** of total variance.

"""

        # 关键发现和建议
        md += f"""## 💡 Key Findings & Recommendations

### 🎯 Key Findings

1. **Distribution Characteristics:** All {analysis_summary.get('normality_tests_performed', 9)} metrics showed non-normal distributions, requiring non-parametric statistical tests.

2. **Group Differences:** {analysis_summary.get('significant_group_differences', 0)} out of {analysis_summary.get('normality_tests_performed', 9)} metrics ({analysis_summary.get('proportion_with_group_differences', 0)*100:.1f}%) showed significant differences across quality groups.

3. **Correlation Structure:** Found {analysis_summary.get('strong_correlations_count', 0)} strong correlations and {analysis_summary.get('moderate_correlations_count', 0)} moderate correlations between metrics.

4. **Logical Consistency:** {consistency_score*100:.1f}% of expected correlations were logically consistent."""

        # 添加最佳预测指标
        if correlation_analysis and 'overall_score_correlations' in correlation_analysis:
            overall_corrs = correlation_analysis['overall_score_correlations']
            if overall_corrs:
                top_corr = max(overall_corrs, key=lambda x: abs(x.get('spearman_correlation', 0)))
                top_metric = top_corr.get('metric', '').replace('_', ' ').title()
                top_rho = top_corr.get('spearman_correlation', 0)
                md += f"\n\n5. **Best Quality Predictor:** {top_metric} shows the strongest correlation with overall quality (ρ = {top_rho:.3f})."

        md += """

### 📋 Statistical Methodology

- **Distribution Testing:** Shapiro-Wilk, D'Agostino-Pearson, and Kolmogorov-Smirnov tests
- **Group Comparisons:** Kruskal-Wallis tests (non-parametric) due to non-normal distributions  
- **Correlation Analysis:** Spearman rank correlation with FDR multiple comparison correction
- **Post-hoc Analysis:** Mann-Whitney U tests with Bonferroni correction
- **Advanced Analysis:** Variance Inflation Factor (VIF) and Principal Component Analysis (PCA)

### 📋 Recommendations

1. **Statistical Approach:** Continue using non-parametric methods (Kruskal-Wallis, Spearman correlation) given the non-normal distributions.

2. **Quality Assessment:** Focus on metrics showing significant group differences for effective quality discrimination.

3. **Metric Optimization:** Consider consolidating highly correlated metrics to reduce redundancy and improve efficiency.

4. **Multicollinearity:** Address high VIF metrics that may cause instability in predictive models.

5. **Validation:** Validate findings with additional datasets to ensure statistical conclusions generalize.

---

## 📊 Technical Details

**Statistical Software:** Python with SciPy, NumPy, and Pandas  
**Significance Level:** α = 0.05  
**Multiple Comparison Correction:** FDR (Benjamini-Hochberg) for correlations, Bonferroni for post-hoc tests  
**Sample Size:** {analysis_summary.get('total_maps', 0)} dungeon maps  
**Metrics Analyzed:** {analysis_summary.get('metrics_analyzed', 0)} quality dimensions  

**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return md
    
    def save_report(self, output_path: str) -> bool:
        """保存Markdown报告到文件"""
        try:
            md_content = self.generate_markdown_report()
            
            # 确保输出目录存在
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            print(f"✅ Statistical report saved to: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save report: {e}")
            return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Statistical Report Generator - Generate Markdown reports from statistical analysis data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate report from statistical analysis
  python statistical_report_generator.py --input output/test_analysis/statistical_analysis_report.json
  
  # Generate report with custom output location
  python statistical_report_generator.py --input output/statistical_analysis_report.json --output reports/analysis_report.md
  
  # Generate report with timestamp
  python statistical_report_generator.py -i output/test_analysis/statistical_analysis_report.json -o statistical_report_$(date +%Y%m%d_%H%M).md
        """
    )
    
    parser.add_argument('--input', '-i', required=True,
                       help='Path to statistical analysis report JSON file')
    parser.add_argument('--output', '-o', 
                       help='Output Markdown file path (default: statistical_report.md)')
    
    args = parser.parse_args()
    
    # 设置默认输出路径
    if not args.output:
        input_path = Path(args.input)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        args.output = input_path.parent / f'statistical_report_{timestamp}.md'
    
    # 验证输入文件
    if not os.path.exists(args.input):
        print(f"❌ Error: Input file not found: {args.input}")
        return 1
    
    try:
        # 生成报告
        print(f"📊 Generating statistical report from: {args.input}")
        generator = StatisticalReportGenerator(args.input)
        
        success = generator.save_report(args.output)
        
        if success:
            print(f"🎉 Report generation completed successfully!")
            print(f"📄 Report location: {os.path.abspath(args.output)}")
            
            # 显示文件大小
            file_size = os.path.getsize(args.output) / 1024  # KB
            print(f"📏 Report size: {file_size:.1f} KB")
            
            return 0
        else:
            print("❌ Report generation failed!")
            return 1
            
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())