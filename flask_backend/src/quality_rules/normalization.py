"""
统一的归一化函数库

提供基于数学理论的标准化方法，避免无法解释的经验参数。
所有归一化函数都有明确的数学基础和理论依据。
"""

import math
import numpy as np
from typing import List, Union, Tuple

def sigmoid_normalize(x: float, center: float = 0.0, steepness: float = 1.0) -> float:
    """
    Sigmoid归一化函数
    
    理论基础：Sigmoid函数是生物学和机器学习中的标准激活函数
    特点：平滑、单调、有界，适合将任意实数映射到(0,1)区间
    
    参数：
    - x: 输入值
    - center: 中心点（sigmoid的对称中心）
    - steepness: 陡峭程度（越大越陡峭）
    
    返回：归一化到(0,1)的值
    """
    return 1.0 / (1.0 + math.exp(-steepness * (x - center)))

def min_max_normalize(x: float, min_val: float, max_val: float, 
                     target_min: float = 0.0, target_max: float = 1.0) -> float:
    """
    最小-最大归一化
    
    理论基础：线性变换的标准方法，保持数据的相对关系
    特点：线性、简单、直观
    
    参数：
    - x: 输入值
    - min_val: 数据的最小值
    - max_val: 数据的最大值
    - target_min: 目标最小值
    - target_max: 目标最大值
    
    返回：归一化到[target_min, target_max]的值
    """
    if max_val == min_val:
        return (target_min + target_max) / 2.0
    
    normalized = (x - min_val) / (max_val - min_val)
    return target_min + normalized * (target_max - target_min)

def z_score_normalize(x: float, mean: float, std: float) -> float:
    """
    Z-score归一化
    
    理论基础：统计学中的标准分数，基于正态分布
    特点：标准化到均值为0，标准差为1的分布
    
    参数：
    - x: 输入值
    - mean: 均值
    - std: 标准差
    
    返回：Z-score值
    """
    if std == 0:
        return 0.0
    return (x - mean) / std

def gaussian_normalize(x: float, mean: float, std: float) -> float:
    """
    高斯归一化（基于正态分布密度函数）
    
    理论基础：正态分布的概率密度函数
    特点：在均值处达到最大值1.0，向两侧递减
    
    参数：
    - x: 输入值
    - mean: 均值（最优值）
    - std: 标准差（容忍度）
    
    返回：基于正态分布的归一化分数[0,1]
    """
    if std == 0:
        return 1.0 if x == mean else 0.0
    
    return math.exp(-((x - mean) ** 2) / (2 * std ** 2))

def exponential_decay_normalize(x: float, optimal: float, decay_rate: float = 1.0) -> float:
    """
    指数衰减归一化
    
    理论基础：指数衰减函数，常用于距离或差异的惩罚
    特点：在最优值处为1.0，随距离指数衰减
    
    参数：
    - x: 输入值
    - optimal: 最优值
    - decay_rate: 衰减率（越大衰减越快）
    
    返回：基于指数衰减的归一化分数[0,1]
    """
    distance = abs(x - optimal)
    return math.exp(-decay_rate * distance)

def ratio_normalize(x: float, target: float, tolerance: float = 0.1) -> float:
    """
    比率归一化
    
    理论基础：基于目标比率的相对评估
    特点：当x/target接近1时得分最高
    
    参数：
    - x: 输入值
    - target: 目标值
    - tolerance: 容忍度（相对误差）
    
    返回：基于比率的归一化分数[0,1]
    """
    if target == 0:
        return 1.0 if x == 0 else 0.0
    
    ratio = x / target
    if abs(ratio - 1.0) <= tolerance:
        return 1.0
    else:
        # 使用指数衰减惩罚偏离
        deviation = abs(ratio - 1.0) - tolerance
        return max(0.0, math.exp(-deviation))

def percentile_normalize(x: float, values: List[float]) -> float:
    """
    百分位数归一化
    
    理论基础：基于数据分布的相对位置
    特点：不受异常值影响，反映在数据中的相对位置
    
    参数：
    - x: 输入值
    - values: 参考数据集
    
    返回：百分位数[0,1]
    """
    if not values:
        return 0.5
    
    sorted_values = sorted(values)
    count = len(sorted_values)
    
    # 找到x在排序数组中的位置
    position = 0
    for i, val in enumerate(sorted_values):
        if x <= val:
            position = i
            break
        position = i + 1
    
    return position / count

def bounded_normalize(x: float, lower_bound: float, upper_bound: float, 
                     penalty_factor: float = 2.0) -> float:
    """
    有界归一化
    
    理论基础：基于上下界的约束优化
    特点：在边界内为1.0，超出边界时指数衰减
    
    参数：
    - x: 输入值
    - lower_bound: 下界
    - upper_bound: 上界
    - penalty_factor: 惩罚因子
    
    返回：基于边界的归一化分数[0,1]
    """
    if lower_bound <= x <= upper_bound:
        return 1.0
    
    if x < lower_bound:
        distance = lower_bound - x
    else:
        distance = x - upper_bound
    
    return max(0.0, math.exp(-penalty_factor * distance))

def variance_normalize(values: List[float], target_variance: float = 1.0) -> float:
    """
    方差归一化
    
    理论基础：基于数据变异程度的评估
    特点：方差接近目标值时得分最高
    
    参数：
    - values: 数据列表
    - target_variance: 目标方差
    
    返回：基于方差的归一化分数[0,1]
    """
    if len(values) < 2:
        return 1.0
    
    actual_variance = np.var(values)
    return gaussian_normalize(actual_variance, target_variance, target_variance * 0.5)

def connectivity_normalize(connected_components: int, total_nodes: int) -> float:
    """
    连通性归一化
    
    理论基础：图论中的连通性概念
    特点：连通分量越少（越连通）得分越高
    
    参数：
    - connected_components: 连通分量数
    - total_nodes: 总节点数
    
    返回：基于连通性的归一化分数[0,1]
    """
    if total_nodes == 0:
        return 0.0
    
    # 完全连通时连通分量为1，完全分离时连通分量为节点数
    max_components = total_nodes
    min_components = 1
    
    # 归一化：连通分量越少越好
    normalized = (max_components - connected_components) / (max_components - min_components)
    return max(0.0, min(1.0, normalized))

def density_normalize(actual_density: float, theoretical_density: float) -> float:
    """
    密度归一化
    
    理论基础：基于理论密度的相对评估
    特点：实际密度接近理论密度时得分最高
    
    参数：
    - actual_density: 实际密度
    - theoretical_density: 理论密度
    
    返回：基于密度的归一化分数[0,1]
    """
    return ratio_normalize(actual_density, theoretical_density, 0.2)

# ========== 新增：基于数据统计特性的客观归一化函数 ==========

def statistical_normalize(x: float, values: List[float]) -> float:
    """
    统计归一化 - 基于数据本身的统计特性
    
    理论基础：统计学中的标准化方法
    特点：使用数据的均值、标准差等统计量，不依赖主观参数
    
    参数：
    - x: 输入值
    - values: 参考数据集
    
    返回：基于统计特性的归一化分数[0,1]
    """
    if not values or len(values) < 2:
        return 0.5
    
    mean_val = np.mean(values)
    std_val = np.std(values)
    
    if std_val == 0:
        return 1.0 if x == mean_val else 0.0
    
    # 使用Z-score，然后通过sigmoid映射到[0,1]
    z_score = (x - mean_val) / std_val
    return sigmoid_normalize(z_score, center=0.0, steepness=0.5)

def quantile_normalize(x: float, values: List[float]) -> float:
    """
    分位数归一化 - 基于数据分布的分位数
    
    理论基础：非参数统计方法
    特点：不受异常值影响，反映在数据分布中的相对位置
    
    参数：
    - x: 输入值
    - values: 参考数据集
    
    返回：基于分位数的归一化分数[0,1]
    """
    if not values:
        return 0.5
    
    # 计算x在数据中的分位数位置
    count_less = sum(1 for val in values if val < x)
    count_equal = sum(1 for val in values if val == x)
    
    # 使用线性插值计算精确分位数
    total = len(values)
    quantile = (count_less + 0.5 * count_equal) / total
    
    return quantile

def entropy_normalize(values: List[float]) -> float:
    """
    熵归一化 - 基于数据的信息熵
    
    理论基础：信息论中的熵概念
    特点：熵越高表示数据越均匀分布，熵越低表示数据越集中
    
    参数：
    - values: 数据列表
    
    返回：基于熵的归一化分数[0,1]
    """
    if not values or len(values) < 2:
        return 0.0
    
    # 计算数据的熵
    unique_values, counts = np.unique(values, return_counts=True)
    probabilities = counts / len(values)
    
    # 计算信息熵
    entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
    
    # 最大熵（均匀分布）
    max_entropy = np.log2(len(unique_values))
    
    if max_entropy == 0:
        return 0.0
    
    # 归一化熵
    normalized_entropy = entropy / max_entropy
    return normalized_entropy

def coefficient_of_variation_normalize(values: List[float]) -> float:
    """
    变异系数归一化 - 基于数据的相对变异程度
    
    理论基础：统计学中的变异系数
    特点：CV = 标准差/均值，反映数据的相对变异程度
    
    参数：
    - values: 数据列表
    
    返回：基于变异系数的归一化分数[0,1]
    """
    if not values or len(values) < 2:
        return 0.0
    
    mean_val = np.mean(values)
    if mean_val == 0:
        return 0.0
    
    std_val = np.std(values)
    cv = std_val / abs(mean_val)
    
    # 使用sigmoid函数将CV映射到[0,1]
    # CV越大表示变异越大，这里我们假设适中的CV更好
    return sigmoid_normalize(cv, center=0.5, steepness=2.0)

def gini_normalize(values: List[float]) -> float:
    """
    基尼系数归一化 - 基于数据的不平等程度
    
    理论基础：经济学中的基尼系数
    特点：基尼系数越小表示数据越均匀分布
    
    参数：
    - values: 数据列表
    
    返回：基于基尼系数的归一化分数[0,1]
    """
    if not values or len(values) < 2:
        return 0.0
    
    # 计算基尼系数
    sorted_values = sorted(values)
    n = len(sorted_values)
    cumsum = np.cumsum(sorted_values)
    
    # 基尼系数公式
    gini = (n + 1 - 2 * np.sum(cumsum) / cumsum[-1]) / n if cumsum[-1] != 0 else 0
    
    # 基尼系数越小越好，所以用1减去
    return 1.0 - gini

def range_normalize(x: float, values: List[float]) -> float:
    """
    范围归一化 - 基于数据范围的位置
    
    理论基础：数据在值域中的相对位置
    特点：简单直观，反映数据在整体分布中的位置
    
    参数：
    - x: 输入值
    - values: 参考数据集
    
    返回：基于范围的归一化分数[0,1]
    """
    if not values:
        return 0.5
    
    min_val = min(values)
    max_val = max(values)
    
    if max_val == min_val:
        return 0.5
    
    return (x - min_val) / (max_val - min_val) 