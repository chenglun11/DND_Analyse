# TreasureMonsterDistributionRule 文档

## 概述

TreasureMonsterDistributionRule 是一个客观评估地下城地图中宝藏与怪物空间和数量分布质量的规则。该规则使用纯数学方法，不依赖主观权重，通过几何平均融合多个子指标来产生最终评分。

## 设计原理

### 核心思想
- **客观性**：所有评分基于数据统计特性，无主观权重
- **适应性**：能够处理只有宝藏或同时有宝藏和怪物的情况
- **融合性**：使用几何平均融合多个子指标，确保平衡性

### 理论基础
- **变异系数（CV）**：衡量数量分布的相对离散程度
- **理论最大CV**：基于房间数量的理论最大变异系数
- **欧氏距离**：计算空间位置间的几何距离
- **几何平均**：融合多个指标，避免单一指标主导

## 子指标

### 1. 宝藏数量均匀度 (treasure_uniformity)
- **计算**：统计每个房间的宝藏数量，计算变异系数
- **归一化**：使用理论最大CV = √(n-1) 归一化
- **评分**：1 - min(CV_treasure / CV_max, 1.0)
- **含义**：宝藏分布越均匀，得分越高

### 2. 怪物数量均匀度 (monster_uniformity)
- **计算**：统计每个房间的怪物/首领数量，计算变异系数
- **归一化**：使用理论最大CV = √(n-1) 归一化
- **评分**：1 - min(CV_monster / CV_max, 1.0)
- **含义**：怪物分布越均匀，得分越高

### 3. 宝藏-怪物接近度 (proximity_score)
- **计算**：对每个宝藏位置，计算到最近怪物位置的欧氏距离
- **归一化**：使用地图对角线长度归一化
- **评分**：1 - min(avg_distance / D_map, 1.0)
- **含义**：宝藏与怪物越接近，得分越高

## 融合方法

### 几何平均融合
```python
factors = [f for f in [uni_t, uni_m, prox_score] if f > 0]
score = exp(sum(log(f) for f in factors) / len(factors)) if factors else 0.0
```

### 特点
- **排除零值**：只使用非零因子进行计算
- **平衡性**：几何平均确保所有因子都有影响
- **鲁棒性**：即使某个因子为0，其他因子仍能产生有效评分

## 适应性处理

### 只有宝藏的情况
- 只计算宝藏数量均匀度
- 怪物相关指标设为0
- 添加备注说明评估范围

### 有宝藏和怪物的情况
- 计算所有三个子指标
- 进行完整的几何平均融合

## 实现细节

### 数据结构处理
- 从`game_elements`中提取treasure和monster/boss类型
- 将元素位置映射到最近的房间
- 处理房间坐标和元素位置的关系

### 边界情况处理
- 空数据：返回0分
- 无宝藏：返回0分
- 无怪物：只评估宝藏分布
- 单一房间：使用默认CV值

## 使用示例

```python
from src.quality_rules.treasure_monster_distribution import TreasureMonsterDistributionRule

rule = TreasureMonsterDistributionRule()
score, detail = rule.evaluate(dungeon_data)

print(f"评分: {score}")
print(f"宝藏均匀度: {detail['uniformity_treasure']}")
print(f"怪物均匀度: {detail['uniformity_monster']}")
print(f"接近度评分: {detail['proximity_score']}")
```

## 评分解释

### 高分情况 (0.7-1.0)
- 宝藏和怪物分布都很均匀
- 宝藏与怪物位置适中，不会太远也不会太近
- 整体布局平衡

### 中等分数 (0.4-0.7)
- 部分指标表现良好
- 分布有一定的不均匀性
- 空间关系需要优化

### 低分情况 (0.0-0.4)
- 分布极不均匀
- 宝藏与怪物距离过远或过近
- 布局需要重新设计

## 集成信息

- **规则名称**: `treasure_monster_distribution`
- **权重**: 0.2 (在质量评估器中)
- **类型**: 客观评分规则
- **依赖**: 房间数据、游戏元素数据

## 测试结果

### 测试案例
1. **eternal_lair_of_uadjit.json**: 只有宝藏
   - 评分: 0.3876
   - 备注: "Only treasure distribution evaluated (no monsters found)"

2. **hold_of_the_leper_queen.json**: 宝藏+首领
   - 评分: 0.4598
   - 完整评估

3. **abandoned_sanctum_of_the_lich_lady.json**: 宝藏+首领
   - 评分: 0.4560
   - 完整评估

## 总结

TreasureMonsterDistributionRule 提供了一个客观、数学化的方法来评估地下城地图中宝藏与怪物的分布质量。通过适应性的设计，它能够处理各种数据情况，并通过几何平均融合确保评分的平衡性和可靠性。 