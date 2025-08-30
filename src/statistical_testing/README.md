# Statistical Testing Module

This module contains all statistical testing and validation functions for the dungeon quality assessment system.

## Module Structure

### 1. System Validation (`validation.py`)
Core module for system validity validation, containing 7 validation methods:

- **Cross Validation** - Verify consistency of assessment results
- **Test-Retest Reliability** - Test system stability
- **Known Benchmark Validation** - Validate using manually annotated data
- **Metric Correlation Validation** - Check if inter-metric correlations are reasonable
- **Sensitivity Analysis** - Test system response to changes
- **Statistical Validity Testing** - Check score distributions and statistical properties
- **Comprehensive Validation** - Run all validation tests

### 2. Statistical Analysis (`statistical_analysis.py`)
Statistical analysis based on batch evaluation results:

- Spearman correlation analysis
- Advanced statistical analysis integration
- Chart generation management
- Batch result processing

### 3. Advanced Analytics (`advanced_analytics.py`)
Deep data analysis functions:

- **Spearman Correlation** - Rank correlation analysis with FDR correction
- **VIF Analysis** - Variance Inflation Factor, detecting multicollinearity
- **PCA Analysis** - Principal Component Analysis, dimensionality reduction and feature extraction
- **Clustering Analysis** - Hierarchical clustering, discovering metric grouping patterns

### 4. Chart Generation (`unified_chart_generator.py`)
Unified visualization generator:

- Correlation heatmaps and scatter plots
- Network relationship diagrams
- P-value analysis charts
- VIF, PCA, clustering analysis charts
- All charts converted to base64 encoding

### 5. F_Q Data Analysis (`f_q_data_statistics.py`)
Statistical analysis specifically for F_Q_Report directory data:

- Descriptive statistics
- Cross-dataset comparison
- Spearman correlation analysis
- Detailed statistical report generation

## Usage Examples

```python
from src.statistical_testing import SystemValidator, StatisticalAnalyzer

# System validation
validator = SystemValidator()
results = validator.comprehensive_validation("samples/test_data/")
validator.generate_validation_report(results, "output/validation_report.json")

# Statistical analysis
analyzer = StatisticalAnalyzer()
analyzer.analyze_batch_results("output/batch_summary.json", "output/analysis/")
```

## Key Features

1. **Comprehensive Validation Framework** - 7 different perspectives of system validity validation
2. **Statistical Rigor** - Using scipy for scientific computing, supporting FDR correction
3. **Rich Visualization** - Generate multiple types of statistical charts
4. **Modular Design** - Independent functions, easy to extend and maintain
5. **Robust Handling** - Comprehensive error handling and edge case processing

## Output Results

- Detailed analysis reports in JSON format
- Statistical data tables in CSV format
- Statistical charts in PNG format
- Analysis summaries in console output

All analysis results are saved in corresponding subdirectories under the `output/` directory.