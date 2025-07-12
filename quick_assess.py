#!/usr/bin/env python3
"""
快速地牢质量评估脚本
使用方法: python quick_assess.py <dungeon_file.json> [--detailed] [--visualize]
"""

import sys
import json
import argparse
from pathlib import Path
from src.quality_assessor import DungeonQualityAssessor

def quick_assess(dungeon_file, detailed=False, visualize=False):
    """快速地牢质量评估"""
    
    # 检查文件是否存在
    if not Path(dungeon_file).exists():
        print(f"错误: 文件 {dungeon_file} 不存在")
        return
    
    try:
        # 加载地牢数据
        with open(dungeon_file, 'r', encoding='utf-8') as f:
            dungeon_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"错误: JSON格式错误 - {e}")
        return
    except Exception as e:
        print(f"错误: 无法读取文件 - {e}")
        return
    
    # 创建评估器
    assessor = DungeonQualityAssessor()
    
    # 评估质量
    try:
        results = assessor.assess_quality(dungeon_data)
    except Exception as e:
        print(f"错误: 评估过程中出现错误 - {e}")
        return
    
    # 输出基本信息
    print(f"📊 地牢质量评估报告")
    print(f"文件: {dungeon_file}")
    print(f"总体评分: {results['overall_score']:.3f} ({results['grade']})")
    
    # 输出分类评分
    print(f"\n📈 分类评分:")
    for category, score in results['category_scores'].items():
        category_name = {
            'structural': '结构类',
            'gameplay': '游戏性类', 
            'aesthetic': '美术类'
        }.get(category, category)
        print(f"  {category_name}: {score:.3f}")
    
    # 详细指标
    if detailed:
        print(f"\n🔍 详细指标:")
        for rule_name, rule_result in results['scores'].items():
            rule_name_cn = {
                'accessibility': '可达性',
                'door_distribution': '门分布',
                'path_diversity': '路径多样性',
                'treasure_monster_distribution': '宝藏怪物分布',
                'aesthetic_balance': '视觉平衡',
                'dead_end_ratio': '死胡同比例',
                'loop_ratio': '环路比例',
                'degree_variance': '度方差'
            }.get(rule_name, rule_name)
            print(f"  {rule_name_cn}: {rule_result['score']:.3f}")
    
    # 提供建议
    if results['recommendations']:
        print(f"\n💡 改进建议:")
        for i, recommendation in enumerate(results['recommendations'], 1):
            print(f"  {i}. {recommendation}")
    
    # 空间推断信息
    if results.get('spatial_inference_used', False):
        print(f"\n⚠️  注意: 使用了空间推断来补全连接信息")
    
    # 可视化
    if visualize:
        try:
            from src.visualizer import visualize_dungeon
            output_file = f"{Path(dungeon_file).stem}_visualization.png"
            visualize_dungeon(dungeon_data, output_file)
            print(f"\n🎨 可视化已保存到: {output_file}")
        except ImportError:
            print(f"\n⚠️  可视化功能不可用，请安装matplotlib")
        except Exception as e:
            print(f"\n⚠️  可视化失败: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="快速地牢质量评估工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python quick_assess.py dungeon.json                    # 基本评估
  python quick_assess.py dungeon.json --detailed         # 详细评估
  python quick_assess.py dungeon.json --visualize        # 生成可视化
  python quick_assess.py dungeon.json --detailed --visualize  # 完整评估
        """
    )
    
    parser.add_argument('dungeon_file', help='地牢JSON文件路径')
    parser.add_argument('--detailed', action='store_true', help='显示详细指标')
    parser.add_argument('--visualize', action='store_true', help='生成可视化图像')
    
    args = parser.parse_args()
    
    quick_assess(args.dungeon_file, args.detailed, args.visualize)

if __name__ == "__main__":
    main() 