#!/usr/bin/env python3
"""
地牢质量基准测试标准
定义标准测试集和评估基准
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
import json

@dataclass
class BenchmarkCategory:
    """基准测试类别"""
    name: str
    description: str
    min_rooms: int
    max_rooms: int
    target_metrics: Dict[str, float]
    weight: float

@dataclass
class QualityBenchmark:
    """质量基准"""
    category: str
    metric: str
    excellent_threshold: float
    good_threshold: float
    acceptable_threshold: float
    poor_threshold: float

class DungeonBenchmarkStandards:
    """地牢基准测试标准"""
    
    def __init__(self):
        self.categories = self._define_categories()
        self.benchmarks = self._define_benchmarks()
        self.reference_dungeons = self._define_reference_dungeons()
    
    def _define_categories(self) -> List[BenchmarkCategory]:
        """定义测试类别"""
        return [
            BenchmarkCategory(
                name="simple_dungeon",
                description="简单地牢 - 适合新手玩家",
                min_rooms=5,
                max_rooms=10,
                target_metrics={
                    "accessibility": 0.8,
                    "dead_end_ratio": 0.7,
                    "path_diversity": 0.6,
                    "loop_ratio": 0.3
                },
                weight=0.2
            ),
            BenchmarkCategory(
                name="medium_dungeon", 
                description="中等复杂度地牢 - 平衡探索与挑战",
                min_rooms=10,
                max_rooms=20,
                target_metrics={
                    "accessibility": 0.85,
                    "dead_end_ratio": 0.75,
                    "path_diversity": 0.7,
                    "loop_ratio": 0.35
                },
                weight=0.4
            ),
            BenchmarkCategory(
                name="complex_dungeon",
                description="复杂地牢 - 深度探索体验",
                min_rooms=20,
                max_rooms=40,
                target_metrics={
                    "accessibility": 0.9,
                    "dead_end_ratio": 0.8,
                    "path_diversity": 0.8,
                    "loop_ratio": 0.4
                },
                weight=0.3
            ),
            BenchmarkCategory(
                name="extreme_dungeon",
                description="极端复杂地牢 - 高级玩家挑战",
                min_rooms=40,
                max_rooms=100,
                target_metrics={
                    "accessibility": 0.95,
                    "dead_end_ratio": 0.85,
                    "path_diversity": 0.9,
                    "loop_ratio": 0.45
                },
                weight=0.1
            )
        ]
    
    def _define_benchmarks(self) -> List[QualityBenchmark]:
        """定义质量基准"""
        return [
            # 可达性基准
            QualityBenchmark("all", "accessibility", 0.9, 0.8, 0.6, 0.4),
            QualityBenchmark("all", "dead_end_ratio", 0.8, 0.7, 0.5, 0.3),
            QualityBenchmark("all", "path_diversity", 0.8, 0.6, 0.4, 0.2),
            QualityBenchmark("all", "loop_ratio", 0.4, 0.3, 0.2, 0.1),
            QualityBenchmark("all", "degree_variance", 0.7, 0.5, 0.3, 0.1),
            QualityBenchmark("all", "door_distribution", 0.8, 0.6, 0.4, 0.2),
            QualityBenchmark("all", "key_path_length", 0.8, 0.6, 0.4, 0.2),
        ]
    
    def _define_reference_dungeons(self) -> Dict[str, Dict]:
        """定义参考地牢"""
        return {
            "classic_examples": {
                "tomb_of_horrors": {
                    "source": "D&D Classic Module",
                    "description": "经典恐怖地牢，复杂的陷阱和谜题",
                    "target_metrics": {
                        "accessibility": 0.6,  # 故意设计得难以导航
                        "path_diversity": 0.3,  # 线性设计
                        "loop_ratio": 0.1,      # 很少回路
                        "dead_end_ratio": 0.4   # 很多死胡同
                    }
                },
                "castle_ravenloft": {
                    "source": "D&D Classic Module", 
                    "description": "哥特式城堡，多层次探索",
                    "target_metrics": {
                        "accessibility": 0.8,
                        "path_diversity": 0.7,
                        "loop_ratio": 0.3,
                        "dead_end_ratio": 0.7
                    }
                },
                "waterdeep_dungeon": {
                    "source": "D&D 5e Module",
                    "description": "城市地下城，实用主义设计",
                    "target_metrics": {
                        "accessibility": 0.85,
                        "path_diversity": 0.8,
                        "loop_ratio": 0.35,
                        "dead_end_ratio": 0.75
                    }
                }
            },
            "modern_examples": {
                "watabou_baseline": {
                    "source": "Watabou Generator",
                    "description": "程序生成地牢的基准表现",
                    "target_metrics": {
                        "accessibility": 0.75,
                        "path_diversity": 0.6,
                        "loop_ratio": 0.25,
                        "dead_end_ratio": 0.65
                    }
                },
                "dungeondraft_baseline": {
                    "source": "DungeonDraft Tool",
                    "description": "手动设计工具的基准表现", 
                    "target_metrics": {
                        "accessibility": 0.8,
                        "path_diversity": 0.7,
                        "loop_ratio": 0.3,
                        "dead_end_ratio": 0.7
                    }
                }
            }
        }
    
    def get_benchmark_for_metric(self, metric: str) -> QualityBenchmark:
        """获取指定指标的基准"""
        for benchmark in self.benchmarks:
            if benchmark.metric == metric:
                return benchmark
        return None
    
    def evaluate_against_benchmark(self, score: float, metric: str) -> Tuple[str, float]:
        """评估分数相对于基准的表现"""
        benchmark = self.get_benchmark_for_metric(metric)
        if not benchmark:
            return "unknown", 0.0
        
        if score >= benchmark.excellent_threshold:
            return "excellent", 1.0
        elif score >= benchmark.good_threshold:
            return "good", 0.8
        elif score >= benchmark.acceptable_threshold:
            return "acceptable", 0.6
        elif score >= benchmark.poor_threshold:
            return "poor", 0.4
        else:
            return "very_poor", 0.2
    
    def calculate_overall_benchmark_score(self, scores: Dict[str, float]) -> Dict:
        """计算总体基准分数"""
        results = {}
        total_score = 0.0
        total_weight = 0.0
        
        for metric, score in scores.items():
            grade, normalized_score = self.evaluate_against_benchmark(score, metric)
            results[metric] = {
                "score": score,
                "grade": grade,
                "normalized_score": normalized_score
            }
            total_score += normalized_score
            total_weight += 1.0
        
        overall_score = total_score / total_weight if total_weight > 0 else 0.0
        
        # 确定总体等级
        if overall_score >= 0.8:
            overall_grade = "excellent"
        elif overall_score >= 0.6:
            overall_grade = "good"
        elif overall_score >= 0.4:
            overall_grade = "acceptable"
        elif overall_score >= 0.2:
            overall_grade = "poor"
        else:
            overall_grade = "very_poor"
        
        return {
            "overall_score": overall_score,
            "overall_grade": overall_grade,
            "metric_results": results
        }

# 使用示例
if __name__ == "__main__":
    standards = DungeonBenchmarkStandards()
    
    # 测试评估
    test_scores = {
        "accessibility": 0.85,
        "dead_end_ratio": 0.75,
        "path_diversity": 0.7,
        "loop_ratio": 0.3,
        "degree_variance": 0.6,
        "door_distribution": 0.7,
        "key_path_length": 0.6
    }
    
    result = standards.calculate_overall_benchmark_score(test_scores)
    print("基准评估结果:")
    print(f"总体分数: {result['overall_score']:.3f}")
    print(f"总体等级: {result['overall_grade']}")
    
    print("\n各指标详细结果:")
    for metric, details in result['metric_results'].items():
        print(f"  {metric}: {details['score']:.3f} ({details['grade']})") 