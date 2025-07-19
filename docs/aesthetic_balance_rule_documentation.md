# AestheticBalanceRule 文档

## 概述

AestheticBalanceRule 是一个客观评估地下城地图视觉平衡性的规则。该规则使用纯数学方法，不依赖主观权重，通过几何平均融合三个子指标来评估地牢布局的美学质量。

## 设计原理

### 核心思想
- **客观性**：所有评分基于数据统计特性，无主观权重
- **对称性**：评估布局的左右对称程度
- **均匀性**：评估房间面积和间距的分布均匀度
- **融合性**：使用几何平均融合多个子指标，确保平衡性

### 理论基础
- **对称性理论**：视觉平衡中的对称性原则
- **变异系数（CV）**：衡量分布的相对离散程度
- **理论最大CV**：基于样本数量的理论最大变异系数
- **几何平均**：融合多个指标，避免单一指标主导

## 子指标

### 1. 对称度 (symmetry_ratio)
- **计算**：基于房间中心位置的左右对称匹配
- **方法**：
  1. 计算所有房间中心的x坐标范围
  2. 确定对称轴（中点）
  3. 对每个房间，寻找其镜像位置是否有房间
  4. 使用容差（1%的范围）进行匹配
- **评分**：匹配的房间数 / 总房间数
- **含义**：对称度越高，视觉平衡性越好

### 2. 面积均匀度 (uniformity_area)
- **计算**：房间面积的变异系数归一化
- **方法**：
  1. 计算每个房间的面积（宽 × 高）
  2. 计算面积的变异系数 CV = σ/μ
  3. 使用理论最大CV = √(n-1) 归一化
  4. 评分 = 1 - min(CV / CV_max, 1.0)
- **含义**：面积分布越均匀，得分越高

### 3. 间距均匀度 (uniformity_spacing)
- **计算**：相邻房间中心距离的变异系数归一化
- **方法**：
  1. 如果有有效连接，使用连接房间之间的距离
  2. 如果没有有效连接，使用所有房间对之间的距离
  3. 计算距离的变异系数 CV = σ/μ
  4. 使用理论最大CV = √(n-1) 归一化
  5. 评分 = 1 - min(CV / CV_max, 1.0)
- **含义**：间距分布越均匀，得分越高

## 融合方法

### 几何平均融合
```python
factors = [f for f in [symmetry_ratio, uni_area, uni_spacing] if f > 0]
score = exp(sum(log(f) for f in factors) / len(factors)) if factors else 0.0
```

### 特点
- **排除零值**：只使用非零因子进行计算
- **平衡性**：几何平均确保所有因子都有影响
- **鲁棒性**：即使某个因子为0，其他因子仍能产生有效评分

## 实现细节

### 数据结构处理
- 从`rooms`中提取房间位置和尺寸信息
- 从`connections`中提取房间连接关系
- 处理房间ID不匹配的情况

### 对称性计算
```python
# 计算房间中心坐标
xs = [r['position']['x'] + r.get('size', {}).get('width',0)/2 for r in rooms]
ys = [r['position']['y'] + r.get('size', {}).get('height',0)/2 for r in rooms]

# 确定对称轴
min_x, max_x = min(xs), max(xs)
mid_x = (min_x + max_x) / 2

# 匹配镜像位置
for x,y in coords:
    mirror = (2*mid_x - x, y)
    # 查找是否有近似坐标
    for xx,yy in coords:
        if abs(xx - mirror[0])<=tol and abs(yy - mirror[1])<=tol:
            matched += 1
            break
```

### 均匀度计算
```python
def _uniformity_from_values(self, values: List[float]) -> float:
    n = len(values)
    if n==0:
        return 0.0
    mean = sum(values)/n
    var = sum((v-mean)**2 for v in values)/n
    cv = math.sqrt(var)/mean if mean>0 else 0.0
    max_cv = math.sqrt(n-1) if n>1 else 1.0
    uni = max(0.0, 1.0 - min(cv/max_cv, 1.0))
    return uni
```

### 连接处理
- 优先使用有效的房间连接计算间距
- 如果没有有效连接，使用所有房间对之间的距离
- 处理房间ID不匹配的边界情况

## 使用示例

```python
from src.quality_rules.aesthetic_balance import AestheticBalanceRule

rule = AestheticBalanceRule()
score, detail = rule.evaluate(dungeon_data)

print(f"评分: {score}")
print(f"对称度: {detail['symmetry_ratio']}")
print(f"面积均匀度: {detail['uniformity_area']}")
print(f"间距均匀度: {detail['uniformity_spacing']}")
```

## 评分解释

### 高分情况 (0.7-1.0)
- 布局具有良好的对称性
- 房间面积分布均匀
- 房间间距分布均匀
- 整体视觉平衡

### 中等分数 (0.4-0.7)
- 部分指标表现良好
- 有一定的对称性或均匀性
- 布局需要优化

### 低分情况 (0.0-0.4)
- 对称性差
- 面积或间距分布极不均匀
- 布局需要重新设计

## 集成信息

- **规则名称**: `aesthetic_balance`
- **权重**: 0.15 (在质量评估器中)
- **类型**: 客观评分规则
- **依赖**: 房间数据、连接数据

## 测试结果

### 测试案例
1. **hold_of_the_leper_queen.json**
   - 评分: 0.6546
   - 对称度: 0.5000
   - 面积均匀度: 0.7080
   - 间距均匀度: 0.7923

2. **eternal_lair_of_uadjit.json**
   - 评分: 0.8346
   - 对称度: 0.0000
   - 面积均匀度: 0.7860
   - 间距均匀度: 0.8862

3. **abandoned_sanctum_of_the_lich_lady.json**
   - 评分: 0.7659
   - 对称度: 0.0000
   - 面积均匀度: 0.7354
   - 间距均匀度: 0.7977

## 边界情况处理

### 无房间数据
- 返回0分，原因："No rooms"

### 无连接数据
- 使用所有房间对之间的距离计算间距均匀度

### 房间ID不匹配
- 只处理在房间列表中的有效连接
- 如果没有有效连接，使用所有房间对

### 单一房间
- 对称度为0（无法对称）
- 面积和间距均匀度为默认值

## 总结

AestheticBalanceRule 提供了一个客观、数学化的方法来评估地下城地图的视觉平衡性。通过对称性、面积均匀度和间距均匀度三个子指标，它能够全面评估地牢布局的美学质量，并通过几何平均融合确保评分的平衡性和可靠性。 