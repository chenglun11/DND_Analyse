# 统计学测试模块

此模块包含地牢质量评估系统的所有统计学测试和验证功能。

## 模块结构

### 1. 系统验证 (`validation.py`)
系统有效性验证的核心模块，包含7种验证方法：

- **交叉验证** - 检验评估结果的一致性
- **重测信度** - 测试系统稳定性
- **已知基准验证** - 使用人工标注数据验证
- **指标相关性验证** - 检查指标间相关性是否合理
- **敏感性分析** - 测试系统对变化的响应
- **统计有效性检验** - 检查分数分布和统计特性
- **综合验证** - 运行所有验证测试

### 2. 统计分析 (`statistical_analysis.py`)
基于批量评估结果的统计分析：

- Spearman相关性分析
- 高级统计分析集成
- 图表生成管理
- 批量结果处理

### 3. 高级分析 (`advanced_analytics.py`)
深度数据分析功能：

- **Spearman相关性** - 带FDR校正的等级相关分析
- **VIF分析** - 方差膨胀因子，检测多重共线性
- **PCA分析** - 主成分分析，降维和特征提取
- **聚类分析** - 层次聚类，发现指标分组模式

### 4. 图表生成 (`unified_chart_generator.py`)
统一的可视化生成器：

- 相关性热力图和散点图
- 网络关系图
- P值分析图表
- VIF、PCA、聚类分析图表
- 所有图表转base64编码

### 5. F_Q数据分析 (`f_q_data_statistics.py`)
专门针对F_Q_Report目录数据的统计分析：

- 描述性统计
- 跨数据集比较
- Spearman相关性分析
- 详细统计报告生成

## 使用示例

```python
from src.statistical_testing import SystemValidator, StatisticalAnalyzer

# 系统验证
validator = SystemValidator()
results = validator.comprehensive_validation("samples/test_data/")
validator.generate_validation_report(results, "output/validation_report.json")

# 统计分析
analyzer = StatisticalAnalyzer()
analyzer.analyze_batch_results("output/batch_summary.json", "output/analysis/")
```

## 主要特性

1. **全面的验证框架** - 7种不同角度的系统有效性验证
2. **统计学严谨性** - 使用scipy进行科学计算，支持FDR校正
3. **可视化丰富** - 生成多种类型的统计图表
4. **模块化设计** - 各功能独立，易于扩展和维护
5. **鲁棒性处理** - 完善的错误处理和边界情况处理

## 输出结果

- JSON格式的详细分析报告
- CSV格式的统计数据表
- PNG格式的统计图表
- 控制台输出的分析摘要

所有分析结果保存在`output/`目录下的相应子目录中。