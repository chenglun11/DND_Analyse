#!/usr/bin/env python3
"""
测试运行脚本
用于运行项目的所有单元测试
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

def run_tests(test_type="all", coverage=False, verbose=False):
    """运行测试"""
    
    # 确保在项目根目录
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # 构建pytest命令
    cmd = ["python", "-m", "pytest"]
    
    # 添加测试类型过滤
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "performance":
        cmd.extend(["-m", "performance"])
    elif test_type == "fast":
        cmd.extend(["-m", "not slow"])
    
    # 添加覆盖率
    if coverage:
        cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term-missing"])
    
    # 添加详细输出
    if verbose:
        cmd.extend(["-v", "-s"])
    
    # 添加测试目录
    cmd.append("tests/")
    
    print(f"运行命令: {' '.join(cmd)}")
    print("=" * 60)
    
    # 运行测试
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode == 0
    except Exception as e:
        print(f"运行测试时出错: {e}")
        return False

def install_dependencies():
    """安装测试依赖"""
    print("安装测试依赖...")
    
    dependencies = [
        "pytest>=6.0.0",
        "pytest-cov>=2.10.0",
        "pytest-mock>=3.6.0",
        "pytest-xdist>=2.0.0"
    ]
    
    for dep in dependencies:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
            print(f"✓ 已安装 {dep}")
        except subprocess.CalledProcessError as e:
            print(f"✗ 安装 {dep} 失败: {e}")
            return False
    
    return True

def check_test_environment():
    """检查测试环境"""
    print("检查测试环境...")
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("✗ 需要Python 3.7或更高版本")
        return False
    
    print(f"✓ Python版本: {sys.version}")
    
    # 检查必要文件
    required_files = [
        "tests/",
        "src/",
        "requirements.txt"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"✗ 缺少必要文件: {file_path}")
            return False
        print(f"✓ 找到文件: {file_path}")
    
    return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="运行项目测试")
    parser.add_argument(
        "--type", "-t",
        choices=["all", "unit", "integration", "performance", "fast"],
        default="all",
        help="测试类型"
    )
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="生成覆盖率报告"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细输出"
    )
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="安装测试依赖"
    )
    parser.add_argument(
        "--check-env",
        action="store_true",
        help="检查测试环境"
    )
    
    args = parser.parse_args()
    
    print("🧪 地牢适配器测试套件")
    print("=" * 60)
    
    # 检查环境
    if args.check_env:
        if not check_test_environment():
            sys.exit(1)
        print("✓ 测试环境检查通过")
        return
    
    # 安装依赖
    if args.install_deps:
        if not install_dependencies():
            sys.exit(1)
        print("✓ 依赖安装完成")
        return
    
    # 运行测试
    print(f"开始运行 {args.type} 测试...")
    
    success = run_tests(
        test_type=args.type,
        coverage=args.coverage,
        verbose=args.verbose
    )
    
    if success:
        print("\n🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败")
        sys.exit(1)

if __name__ == "__main__":
    main() 