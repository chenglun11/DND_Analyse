#!/usr/bin/env python3
"""
验证结果汇总脚本
汇总多个算法的验证结果，生成总体报告
"""

import json
import sys
from pathlib import Path
import numpy as np

def is_validation_file(data):
    """检查文件是否为验证结果文件"""
    return (isinstance(data, dict) and 
            'validation_summary' in data and 
            'detailed_results' in data)

def load_validation_result(file_path):
    """加载单个验证结果文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if is_validation_file(data):
                return data
            else:
                return None
    except Exception as e:
        print(f"Failed to load {file_path}: {e}")
        return None

def extract_algorithm_name(file_path):
    """从文件路径或内容中提取算法名称"""
    file_name = Path(file_path).stem
    
    # 尝试从文件名中提取算法名
    if 'validation_' in file_name:
        return file_name.replace('validation_', '').upper()
    elif '_validation' in file_name:
        return file_name.replace('_validation', '').upper()
    else:
        # 使用文件名作为算法名
        return file_name.upper().replace('_', ' ')

def summarize_validations(validation_files, output_path=None):
    """汇总多个验证结果"""
    
    results = {}
    all_scores = []
    
    print("="*80)
    print("MULTI-ALGORITHM VALIDATION SUMMARY")
    print("="*80)
    
    for algo, file_path in validation_files.items():
        print(f"\n📊 {algo} Algorithm:")
        print("-" * 40)
        
        result = load_validation_result(file_path)
        if result is None:
            print(f"  [ERROR] Could not load results")
            continue
            
        summary = result['validation_summary']
        overall_score = summary['overall_effectiveness_score']
        success_rate = summary['success_rate']
        
        print(f"  Overall Score: {overall_score:.3f} ({overall_score*100:.1f}%)")
        print(f"  Success Rate: {success_rate:.1%}")
        print(f"  Validations Passed: {summary['validations_passed']}/{summary['total_validations']}")
        
        # 显示各项分数
        for validation_type, details in result['detailed_results'].items():
            score = details['score']
            status = "PASS" if details['success'] else "FAIL"
            print(f"    [{status}] {validation_type.replace('_', ' ').title()}: {score:.3f}")
        
        results[algo] = {
            'overall_score': overall_score,
            'success_rate': success_rate,
            'details': result['detailed_results']
        }
        
        if overall_score > 0:
            all_scores.append(overall_score)
    
    # 计算总体统计
    if all_scores:
        mean_score = np.mean(all_scores)
        std_score = np.std(all_scores)
        
        print("\n" + "="*80)
        print("OVERALL SUMMARY ACROSS ALL ALGORITHMS")
        print("="*80)
        print(f"Algorithms Tested: {len(results)}")
        print(f"Mean Effectiveness Score: {mean_score:.3f} ({mean_score*100:.1f}%)")
        print(f"Standard Deviation: {std_score:.3f}")
        print(f"Score Range: {min(all_scores):.3f} - {max(all_scores):.3f}")
        
        # 等级分布
        grades = {}
        for score in all_scores:
            if score >= 0.8:
                grade = "Excellent"
            elif score >= 0.6:
                grade = "Good"
            elif score >= 0.4:
                grade = "Fair"
            else:
                grade = "Poor"
            grades[grade] = grades.get(grade, 0) + 1
        
        print(f"\nGrade Distribution:")
        for grade, count in grades.items():
            percentage = (count / len(all_scores)) * 100
            print(f"  {grade}: {count} algorithms ({percentage:.1f}%)")
        
        # 最佳和最差算法
        best_algo = max(results.keys(), key=lambda k: results[k]['overall_score'])
        worst_algo = min(results.keys(), key=lambda k: results[k]['overall_score'])
        
        print(f"\nBest Performing Algorithm: {best_algo} ({results[best_algo]['overall_score']:.3f})")
        print(f"Worst Performing Algorithm: {worst_algo} ({results[worst_algo]['overall_score']:.3f})")
        
        # 保存汇总结果
        if output_path:
            summary_data = {
                'summary_stats': {
                    'mean_score': mean_score,
                    'std_score': std_score,
                    'min_score': min(all_scores),
                    'max_score': max(all_scores),
                    'algorithms_tested': len(results)
                },
                'algorithm_results': results,
                'grade_distribution': grades,
                'best_algorithm': best_algo,
                'worst_algorithm': worst_algo
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n📁 Summary saved to: {output_path}")
    
    print("="*80)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Summarize validation results from multiple algorithms',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default Paper_Test directory
  python summarize_validations.py
  
  # Specify custom input directory and output file
  python summarize_validations.py --input /path/to/validations --output summary.json
  python summarize_validations.py -i /path/to/validations -o summary.json
  
  # Specify individual files
  python summarize_validations.py --files BSP:validation_BSP.json FI:validation_FI.json
  python summarize_validations.py -f BSP:validation_BSP.json FI:validation_FI.json
        """
    )
    
    parser.add_argument('--input', '-i', 
                       help='Directory containing validation_*.json files')
    parser.add_argument('--output', '-o', 
                       help='Output summary file path')
    parser.add_argument('--files', '-f', nargs='*',
                       help='Individual validation files in format: ALGO:file.json')
    
    args = parser.parse_args()
    
    validation_files = {}
    
    if args.files:
        # 处理指定的文件
        for file_spec in args.files:
            if ':' not in file_spec:
                print(f"Error: Invalid file spec '{file_spec}'. Use format: ALGO:file.json")
                return 1
            algo, file_path = file_spec.split(':', 1)
            if Path(file_path).exists():
                validation_files[algo] = file_path
            else:
                print(f"Warning: File not found: {file_path}")
    
    elif args.input:
        # 搜索指定目录中的所有JSON文件
        input_dir = Path(args.input)
        if not input_dir.exists():
            print(f"Error: Input directory not found: {input_dir}")
            return 1
        
        print(f"Scanning directory: {input_dir}")
        for json_file in input_dir.glob("*.json"):
            # 尝试加载文件看是否为验证文件
            test_data = load_validation_result(json_file)
            if test_data is not None:
                algo_name = extract_algorithm_name(json_file)
                validation_files[algo_name] = str(json_file)
                print(f"  Found validation file: {json_file.name} -> {algo_name}")
    
    else:
        # 默认路径
        base_dir = Path("../../output/Paper_Test")
        default_files = {
            'BSP': base_dir / "validation_BSP.json",
            'FI': base_dir / "validation_FI.json", 
            'ODPC': base_dir / "validation_ODPC.json",
            'Watabou': base_dir / "validation_Watabou.json"
        }
        
        for algo, file_path in default_files.items():
            if file_path.exists():
                validation_files[algo] = str(file_path)
            else:
                print(f"Warning: {algo} validation file not found: {file_path}")
    
    if not validation_files:
        print("Error: No validation result files found!")
        print("\nPlease run individual validations first:")
        print("  python run.py --mode validation --dataset DATA_DIR -o validation_ALGO.json")
        print("\nOr specify files manually:")
        print("  python summarize_validations.py --files BSP:file1.json FI:file2.json")
        print("  python summarize_validations.py -f BSP:file1.json FI:file2.json")
        return 1
    
    print(f"Found {len(validation_files)} validation files:")
    for algo, file_path in validation_files.items():
        print(f"  {algo}: {file_path}")
    print()
    
    # 确定输出路径
    if args.output:
        output_path = Path(args.output)
    elif args.input:
        output_path = Path(args.input) / "validation_summary.json"
    else:
        output_path = Path("../../output/Paper_Test/validation_summary.json")
    
    # 生成汇总
    summarize_validations(validation_files, output_path)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())