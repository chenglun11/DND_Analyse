#!/usr/bin/env python3
"""
批量测试所有样例地图的可视化效果
"""
import os
import sys
import json
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.adapter_manager import AdapterManager
from src.visualizer import visualize_from_file

def find_all_json_files(dirs):
    files = []
    for d in dirs:
        for root, _, filenames in os.walk(d):
            for f in filenames:
                if f.endswith('.json'):
                    files.append(os.path.join(root, f))
    return files

def batch_test_visualization():
    print("=== 批量测试所有样例地图可视化 ===\n")
    sample_dirs = [
        "samples/source_format_1",
        "samples/source_format_2"
    ]
    adapter_manager = AdapterManager()
    all_json_files = find_all_json_files(sample_dirs)
    os.makedirs("output/batch_test", exist_ok=True)
    
    summary = []
    for idx, src_file in enumerate(all_json_files):
        print(f"[{idx+1}/{len(all_json_files)}] 处理: {src_file}")
        try:
            with open(src_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # 检测格式
            fmt = adapter_manager.detect_format(data)
            print(f"   - 检测到格式: {fmt}")
            # 转换
            unified = adapter_manager.convert(data)
            if not unified:
                print("   ❌ 转换失败")
                summary.append((src_file, False, "转换失败"))
                continue
            # 保存统一格式
            out_json = f"output/batch_test/{Path(src_file).stem}_unified.json"
            with open(out_json, 'w', encoding='utf-8') as f:
                json.dump(unified, f, ensure_ascii=False, indent=2)
            # 可视化
            out_png = out_json.replace('.json', '.png')
            vis_ok = visualize_from_file(out_json, out_png)
            if vis_ok:
                print(f"   ✓ 可视化成功: {out_png}")
                summary.append((src_file, True, out_png))
            else:
                print(f"   ❌ 可视化失败")
                summary.append((src_file, False, "可视化失败"))
        except Exception as e:
            print(f"   ❌ 处理异常: {e}")
            summary.append((src_file, False, str(e)))
    print("\n=== 测试汇总 ===")
    for src, ok, info in summary:
        if ok:
            print(f"[OK] {src} -> {info}")
        else:
            print(f"[FAIL] {src} -> {info}")
    print("\n全部完成！请查看 output/batch_test/ 目录下的PNG文件。")

if __name__ == "__main__":
    batch_test_visualization() 