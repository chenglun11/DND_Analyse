#!/usr/bin/env python3
"""
项目清理脚本
清理debug文件、临时文件和无用文件
"""

import os
import shutil
import glob
from pathlib import Path

def cleanup_python_cache():
    """清理Python缓存文件"""
    print("🧹 清理Python缓存文件...")
    
    # 删除__pycache__目录
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                cache_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(cache_path)
                    print(f"  ✓ 删除: {cache_path}")
                except Exception as e:
                    print(f"  ⚠️ 删除失败: {cache_path} - {e}")
    
    # 删除.pyc文件
    pyc_files = glob.glob('**/*.pyc', recursive=True)
    for pyc_file in pyc_files:
        try:
            os.remove(pyc_file)
            print(f"  ✓ 删除: {pyc_file}")
        except Exception as e:
            print(f"  ⚠️ 删除失败: {pyc_file} - {e}")

def cleanup_system_files():
    """清理系统文件"""
    print("\n🖥️ 清理系统文件...")
    
    # 删除.DS_Store文件
    ds_store_files = glob.glob('**/.DS_Store', recursive=True)
    for ds_file in ds_store_files:
        try:
            os.remove(ds_file)
            print(f"  ✓ 删除: {ds_file}")
        except Exception as e:
            print(f"  ⚠️ 删除失败: {ds_file} - {e}")
    
    # 删除Thumbs.db文件
    thumbs_files = glob.glob('**/Thumbs.db', recursive=True)
    for thumbs_file in thumbs_files:
        try:
            os.remove(thumbs_file)
            print(f"  ✓ 删除: {thumbs_file}")
        except Exception as e:
            print(f"  ⚠️ 删除失败: {thumbs_file} - {e}")

def cleanup_test_cache():
    """清理测试缓存"""
    print("\n🧪 清理测试缓存...")
    
    test_cache_dirs = ['.pytest_cache', '.coverage', 'htmlcov', '.tox']
    for cache_dir in test_cache_dirs:
        if os.path.exists(cache_dir):
            try:
                shutil.rmtree(cache_dir)
                print(f"  ✓ 删除: {cache_dir}")
            except Exception as e:
                print(f"  ⚠️ 删除失败: {cache_dir} - {e}")

def cleanup_temp_files():
    """清理临时文件"""
    print("\n📄 清理临时文件...")
    
    temp_patterns = ['*.log', '*.tmp', '*.bak', '*.orig']
    for pattern in temp_patterns:
        temp_files = glob.glob(f'**/{pattern}', recursive=True)
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
                print(f"  ✓ 删除: {temp_file}")
            except Exception as e:
                print(f"  ⚠️ 删除失败: {temp_file} - {e}")

def cleanup_demo_files():
    """清理演示文件"""
    print("\n🎭 清理演示文件...")
    
    demo_dirs = [
        'demo_data',
        'demo_results', 
        'demo_before',
        'demo_after',
        'comparison_results',
        'analysis_results'
    ]
    
    for demo_dir in demo_dirs:
        if os.path.exists(demo_dir):
            try:
                shutil.rmtree(demo_dir)
                print(f"  ✓ 删除: {demo_dir}")
            except Exception as e:
                print(f"  ⚠️ 删除失败: {demo_dir} - {e}")

def cleanup_output_images():
    """清理输出图片文件"""
    print("\n🖼️ 清理输出图片文件...")
    
    image_patterns = ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp', '*.tiff']
    for pattern in image_patterns:
        image_files = glob.glob(f'**/{pattern}', recursive=True)
        for image_file in image_files:
            # 跳过samples目录中的图片
            if 'samples' in image_file:
                continue
            try:
                os.remove(image_file)
                print(f"  ✓ 删除: {image_file}")
            except Exception as e:
                print(f"  ⚠️ 删除失败: {image_file} - {e}")

def cleanup_debug_scripts():
    """清理调试脚本"""
    print("\n🔧 清理调试脚本...")
    
    debug_scripts = [
        'statistical_test.py',
        'enhanced_statistical_test.py', 
        'demo_improvement_evaluation.py',
        'dungeon_quality_stats.csv'
    ]
    
    for script in debug_scripts:
        if os.path.exists(script):
            try:
                os.remove(script)
                print(f"  ✓ 删除: {script}")
            except Exception as e:
                print(f"  ⚠️ 删除失败: {script} - {e}")

def cleanup_histogram_files():
    """清理直方图文件"""
    print("\n📊 清理直方图文件...")
    
    hist_files = glob.glob('*_score_hist.png')
    for hist_file in hist_files:
        try:
            os.remove(hist_file)
            print(f"  ✓ 删除: {hist_file}")
        except Exception as e:
            print(f"  ⚠️ 删除失败: {hist_file} - {e}")

def main():
    """主函数"""
    print("🚀 开始项目清理...")
    print("="*50)
    
    # 执行各种清理操作
    cleanup_python_cache()
    cleanup_system_files()
    cleanup_test_cache()
    cleanup_temp_files()
    cleanup_demo_files()
    cleanup_output_images()
    cleanup_debug_scripts()
    cleanup_histogram_files()
    
    print("\n" + "="*50)
    print("✅ 项目清理完成！")
    print("\n📁 保留的重要文件:")
    print("  • src/ - 源代码目录")
    print("  • samples/ - 样本数据")
    print("  • output/ - 输出结果（保留JSON文件）")
    print("  • FI_MAP_Elites__PCG/ - 核心算法")
    print("  • README.md - 项目说明")
    print("  • requirements.txt - 依赖列表")
    print("  • .gitignore - Git忽略规则")
    print("  • benchmark_*.py - 基准测试工具")
    print("  • improvement_quantification.py - 改进量化工具")

if __name__ == '__main__':
    main() 