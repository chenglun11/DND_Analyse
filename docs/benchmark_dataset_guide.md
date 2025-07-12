# 地牢质量评估标准测试集构建指南

## 🎯 目标

建立一个全面的标准测试集，用于：
1. **基准测试**：评估不同地牢生成方法的性能
2. **改进验证**：量化改进效果
3. **方法对比**：公平比较不同算法
4. **质量评估**：验证评估指标的有效性

## 📊 测试集结构

```
benchmark_dataset/
├── categories/                    # 按复杂度分类
│   ├── simple/                   # 简单地牢 (5-10房间)
│   ├── medium/                   # 中等复杂度 (10-20房间)
│   ├── complex/                  # 复杂地牢 (20-40房间)
│   └── extreme/                  # 极端复杂 (40+房间)
├── sources/                      # 按来源分类
│   ├── watabou/                  # Watabou生成器
│   ├── dungeondraft/             # DungeonDraft工具
│   ├── onepage/                  # One Page Dungeon
│   ├── manual/                   # 手动设计
│   └── classic/                  # 经典模块
├── reference/                    # 参考地牢
│   ├── tomb_of_horrors.json      # 经典恐怖地牢
│   ├── castle_ravenloft.json     # 哥特式城堡
│   └── waterdeep_dungeon.json    # 城市地下城
└── metadata/                     # 元数据
    ├── dataset_info.json         # 数据集信息
    ├── quality_baselines.json    # 质量基准
    └── evaluation_results.json   # 评估结果
```

## 🔍 数据收集策略

### 1. 多源数据收集

#### **程序生成地牢**
- **Watabou**: 收集100个样本
  - 来源：https://watabou.itch.io/one-page-dungeon
  - 特点：程序生成，风格多样
  - 收集方法：使用不同种子生成

- **DungeonDraft**: 收集50个样本
  - 来源：社区分享的地牢
  - 特点：手动设计，质量较高
  - 收集方法：从论坛、Reddit等平台收集

- **One Page Dungeon**: 收集30个样本
  - 来源：比赛作品
  - 特点：创意丰富，设计精良
  - 收集方法：从官方网站下载

#### **手动设计地牢**
- **经典RPG模块**: 收集20个样本
  - 来源：D&D官方模块
  - 特点：经过专业设计，质量保证
  - 收集方法：从官方资源提取

- **社区创作**: 收集50个样本
  - 来源：DM Guild、Reddit等
  - 特点：多样化设计风格
  - 收集方法：筛选高质量作品

### 2. 质量控制标准

#### **纳入标准**
- ✅ 完整的地牢结构（房间、走廊、门）
- ✅ 合理的空间布局
- ✅ 清晰的连接关系
- ✅ 可转换为统一格式

#### **排除标准**
- ❌ 结构不完整的地牢
- ❌ 明显设计缺陷的地牢
- ❌ 无法解析的格式
- ❌ 重复或相似度过高的地牢

### 3. 数据预处理

#### **格式统一**
```bash
# 转换所有地牢为统一格式
python src/cli.py convert-dir raw_data/ processed_data/ --visualize
```

#### **质量筛选**
```bash
# 使用质量评估筛选
python src/batch_assess.py --input processed_data/ --output quality_filtered/
```

#### **复杂度分类**
```python
# 根据房间数量自动分类
def classify_by_complexity(dungeon_data):
    room_count = len(dungeon_data['levels'][0]['rooms'])
    if room_count <= 10:
        return 'simple'
    elif room_count <= 20:
        return 'medium'
    elif room_count <= 40:
        return 'complex'
    else:
        return 'extreme'
```

## 📈 基准建立

### 1. 质量基准定义

#### **优秀基准 (Excellent)**
- 可达性 ≥ 0.9
- 死胡同比例 ≥ 0.8
- 路径多样性 ≥ 0.8
- 回环率 ≥ 0.4

#### **良好基准 (Good)**
- 可达性 ≥ 0.8
- 死胡同比例 ≥ 0.7
- 路径多样性 ≥ 0.6
- 回环率 ≥ 0.3

#### **可接受基准 (Acceptable)**
- 可达性 ≥ 0.6
- 死胡同比例 ≥ 0.5
- 路径多样性 ≥ 0.4
- 回环率 ≥ 0.2

### 2. 参考地牢建立

#### **经典地牢分析**
```json
{
  "tomb_of_horrors": {
    "description": "经典恐怖地牢，故意设计得难以导航",
    "target_metrics": {
      "accessibility": 0.6,
      "path_diversity": 0.3,
      "loop_ratio": 0.1,
      "dead_end_ratio": 0.4
    },
    "design_philosophy": "挑战性设计，强调恐怖氛围"
  }
}
```

#### **现代地牢分析**
```json
{
  "waterdeep_dungeon": {
    "description": "城市地下城，实用主义设计",
    "target_metrics": {
      "accessibility": 0.85,
      "path_diversity": 0.8,
      "loop_ratio": 0.35,
      "dead_end_ratio": 0.75
    },
    "design_philosophy": "平衡探索与实用性"
  }
}
```

## 🧪 实验设计

### 1. 对比实验框架

#### **基线方法**
- **Watabou**: 程序生成基线
- **DungeonDraft**: 手动设计基线
- **随机生成**: 随机算法基线

#### **改进方法**
- **空间推断增强**: 自动补全连接
- **质量优化**: 基于评估指标的优化
- **混合方法**: 结合多种技术

### 2. 评估指标

#### **主要指标**
- 总体质量分数
- 各维度指标分数
- 基准等级分布

#### **统计指标**
- 均值、标准差
- 效应量 (Cohen's d)
- 统计显著性 (p值)

#### **改进指标**
- 改进百分比
- 等级提升数量
- 显著改进指标数量

### 3. 实验流程

```bash
# 1. 建立基线
python src/batch_assess.py --input benchmark_dataset/baseline/ --output baseline_results/

# 2. 测试改进方法
python src/batch_assess.py --input benchmark_dataset/improved/ --output improved_results/

# 3. 量化改进效果
python improvement_quantification.py --before baseline_results/ --after improved_results/ --output improvement_report.json

# 4. 生成对比报告
python enhanced_statistical_test.py --before baseline_results/ --after improved_results/ --output comparison_report/
```

## 📋 实施计划

### 阶段1: 数据收集 (2-3周)
- [ ] 收集Watabou样本 (100个)
- [ ] 收集DungeonDraft样本 (50个)
- [ ] 收集One Page Dungeon样本 (30个)
- [ ] 收集经典模块样本 (20个)
- [ ] 收集社区创作样本 (50个)

### 阶段2: 数据预处理 (1-2周)
- [ ] 格式转换和统一
- [ ] 质量筛选和分类
- [ ] 元数据建立
- [ ] 基准测试运行

### 阶段3: 基准建立 (1周)
- [ ] 分析参考地牢
- [ ] 建立质量基准
- [ ] 验证基准合理性
- [ ] 生成基准报告

### 阶段4: 实验验证 (2-3周)
- [ ] 设计对比实验
- [ ] 运行基线测试
- [ ] 测试改进方法
- [ ] 量化改进效果

## 🎯 预期成果

### 1. 标准测试集
- 250个高质量地牢样本
- 完整的元数据和分类
- 可重现的评估流程

### 2. 质量基准
- 基于经典地牢的质量标准
- 多层次的评估体系
- 可量化的改进目标

### 3. 评估工具
- 自动化的对比分析
- 统计显著性检验
- 可视化报告生成

### 4. 改进验证
- 量化的改进效果
- 统计可靠的结论
- 可复现的实验结果

## 💡 创新点

### 1. 多维度评估
- 不仅关注单一指标
- 综合考虑多个质量维度
- 平衡不同设计目标

### 2. 基准驱动
- 基于经典地牢建立基准
- 提供明确的改进目标
- 确保评估的合理性

### 3. 统计严谨
- 使用效应量评估改进
- 进行统计显著性检验
- 提供置信区间分析

### 4. 实用导向
- 关注实际游戏体验
- 考虑不同玩家群体
- 平衡挑战性与可玩性

这个标准测试集将为地牢生成研究提供坚实的实验基础，确保改进效果的评估是科学、可靠和可重现的。 