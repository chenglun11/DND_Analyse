#!/usr/bin/env python3
"""
统计学测试统一运行脚本
提供便捷的命令行接口来运行各种统计测试功能
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_validation(args):
    """运行系统有效性验证"""
    try:
        from validation import SystemValidator
        
        logger.info("Starting system validation...")
        
        # 初始化验证器
        validator = SystemValidator()
        
        # 加载基准数据（如果提供）
        baseline_dungeons = None
        if args.baseline:
            import json
            try:
                with open(args.baseline, 'r', encoding='utf-8') as f:
                    baseline_dungeons = json.load(f)
                logger.info(f"Loaded baseline dungeons from {args.baseline}")
            except Exception as e:
                logger.warning(f"Failed to load baseline dungeons: {e}")
        
        # 运行验证
        if args.validation_type == 'comprehensive':
            logger.info("Running comprehensive validation...")
            results = validator.comprehensive_validation(args.dataset, baseline_dungeons)
        else:
            logger.info(f"Running {args.validation_type}...")
            
            # 运行特定验证
            if args.validation_type == 'cross_validation':
                result = validator.cross_validation(args.dataset)
            elif args.validation_type == 'inter_rater_reliability':
                result = validator.inter_rater_reliability(args.dataset)
            elif args.validation_type == 'known_baseline_validation':
                if not baseline_dungeons:
                    logger.error("Baseline validation requires --baseline parameter")
                    return False
                result = validator.known_baseline_validation(baseline_dungeons)
            elif args.validation_type == 'metric_correlation_validation':
                result = validator.metric_correlation_validation(args.dataset)
            elif args.validation_type == 'sensitivity_analysis':
                dungeons = validator._load_dataset(args.dataset)
                if not dungeons:
                    logger.error("No dungeons found in dataset")
                    return False
                result = validator.sensitivity_analysis(dungeons[0]['data'])
            elif args.validation_type == 'statistical_validation':
                result = validator.statistical_validation(args.dataset)
            else:
                logger.error(f"Unknown validation type: {args.validation_type}")
                return False
            
            results = {args.validation_type: result}
        
        # 生成报告
        output_path = args.output or "../../output/validation_report.json"
        validator.generate_validation_report(results, output_path)
        
        logger.info("System validation completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"System validation failed: {e}")
        return False

def run_statistical_analysis(args):
    """运行批量统计分析"""
    try:
        from statistical_analysis import StatisticalAnalyzer
        
        logger.info("Starting statistical analysis...")
        
        # 验证输入文件
        if not os.path.exists(args.input):
            logger.error(f"Input file not found: {args.input}")
            return False
        
        # 初始化分析器
        analyzer = StatisticalAnalyzer()
        
        # 执行分析
        output_dir = args.output or "../../output/analysis"
        success = analyzer.analyze_batch_results(args.input, output_dir)
        
        if success:
            logger.info("Statistical analysis completed successfully!")
            return True
        else:
            logger.error("Statistical analysis failed!")
            return False
            
    except Exception as e:
        logger.error(f"Statistical analysis failed: {e}")
        return False

def run_all_tests(args):
    """运行所有测试"""
    logger.info("Starting comprehensive testing suite...")
    
    success_count = 0
    total_tests = 0
    
    # 1. 系统验证（如果提供了数据集）
    if args.dataset:
        logger.info("=" * 60)
        logger.info("RUNNING SYSTEM VALIDATION")
        logger.info("=" * 60)
        
        validation_args = argparse.Namespace(
            dataset=args.dataset,
            validation_type='comprehensive',
            baseline=args.baseline,
            output=args.output and f"{args.output}/validation_report.json"
        )
        
        if run_validation(validation_args):
            success_count += 1
        total_tests += 1
    
    # 2. 统计分析（如果提供了输入文件）
    if args.input:
        logger.info("=" * 60)
        logger.info("RUNNING STATISTICAL ANALYSIS")
        logger.info("=" * 60)
        
        analysis_args = argparse.Namespace(
            input=args.input,
            output=args.output and f"{args.output}/analysis"
        )
        
        if run_statistical_analysis(analysis_args):
            success_count += 1
        total_tests += 1
    
    # 3. F_Q数据分析
    logger.info("=" * 60)
    logger.info("RUNNING F_Q DATA ANALYSIS")  
    logger.info("=" * 60)
    
    fq_args = argparse.Namespace(
        output=args.output and f"{args.output}/F_Q_SA"
    )
    
    total_tests += 1
    
    # 总结
    logger.info("=" * 60)
    logger.info("TESTING SUITE SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Tests completed: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        logger.info("🎉 All tests completed successfully!")
        return True
    else:
        logger.warning(f"⚠️  {total_tests - success_count} tests failed")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Statistical Testing Suite - Unified runner for dungeon quality assessment validation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run system validation (using converted data)
  python run.py --mode validation --dataset ../../output/finial_test/BSP/
  
  # Run statistical analysis  
  python run.py --mode analysis --input ../../output/batch_summary.json
  
  # Run F_Q data analysis
  python run.py --mode fq_analysis
  
  # Run all available tests
  python run.py --mode all --dataset ../../output/finial_test/BSP/ --input ../../output/batch_summary.json
        """
    )
    
    # 主要参数
    parser.add_argument('--mode', '-m', 
                       choices=['validation', 'analysis', 'fq_analysis', 'all'],
                       required=True,
                       help='Analysis mode to run')
    
    # 系统验证参数
    validation_group = parser.add_argument_group('System Validation Options')
    validation_group.add_argument('--dataset', '-d',
                                 help='Path to dataset directory or JSON file')
    validation_group.add_argument('--validation-type', '-v',
                                 choices=['comprehensive', 'cross_validation', 'inter_rater_reliability',
                                        'known_baseline_validation', 'metric_correlation_validation', 
                                        'sensitivity_analysis', 'statistical_validation'],
                                 default='comprehensive',
                                 help='Type of validation to run')
    validation_group.add_argument('--baseline', '-b',
                                 help='Path to baseline dungeons JSON file')
    
    # 统计分析参数
    analysis_group = parser.add_argument_group('Statistical Analysis Options')  
    analysis_group.add_argument('--input', '-i',
                               help='Path to batch summary JSON file for statistical analysis')
    
    # 通用参数
    parser.add_argument('--output', '-o',
                       help='Output directory for results')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 打印启动信息
    print("🔬 Dungeon Quality Assessment - Statistical Testing Suite")
    print("=" * 60)
    print(f"Mode: {args.mode}")
    if args.dataset:
        print(f"Dataset: {args.dataset}")
    if args.input:
        print(f"Input: {args.input}")
    if args.output:
        print(f"Output: {args.output}")
    print("=" * 60)
    
    # 根据模式运行相应功能
    success = False
    
    if args.mode == 'validation':
        if not args.dataset:
            logger.error("Validation mode requires --dataset parameter")
            return 1
        success = run_validation(args)
        
    elif args.mode == 'analysis':
        if not args.input:
            logger.error("Analysis mode requires --input parameter")
            return 1
        success = run_statistical_analysis(args)
        
    elif args.mode == 'all':
        success = run_all_tests(args)
    
    # 返回结果
    if success:
        print("\n✅ Testing completed successfully!")
        print(f"📁 Results saved to: {args.output or 'default output directories'}")
        return 0
    else:
        print("\n❌ Testing failed!")
        return 1

if __name__ == '__main__':
    sys.exit(main())