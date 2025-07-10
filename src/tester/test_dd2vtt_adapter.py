import sys
import os
import json
from src.adapters.dd2vtt_adapter import DD2VTTAdapter
from src.visualizer import visualize_dungeon

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python test_dd2vtt_adapter.py <dd2vtt_json路径>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_json = os.path.join("output", os.path.basename(input_path).replace(".json", "_unified.json"))
    output_img = os.path.join("output", os.path.basename(input_path).replace(".json", ".png"))

    # 读取源文件
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 转换
    adapter = DD2VTTAdapter()
    if not adapter.detect(data):
        print("文件格式不是dd2vtt！")
        sys.exit(2)
    unified = adapter.convert_with_inference(data)
    if not unified:
        print("转换失败！")
        sys.exit(3)

    # 保存统一格式
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(unified.to_dict(), f, ensure_ascii=False, indent=2)
    print(f"已保存统一格式到: {output_json}")

    # 可视化
    try:
        visualize_dungeon(unified.to_dict(), output_img)
        print(f"已保存可视化图片到: {output_img}")
    except Exception as e:
        print(f"可视化失败: {e}") 