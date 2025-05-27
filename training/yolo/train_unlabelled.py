import os
from pathlib import Path
import cv2
import numpy as np
from ultralytics import YOLO


# Configuration
MODEL_PATH = "runs/segment/room-seg3/weights/best.pt"  # 训练好的模型路径
INPUT_DIR = Path("unlabelled")                    # 存放待测试 PNG 的文件夹
OUTPUT_DIR = Path("runs/predict/test")             # 推理结果保存目录
DEVICE = 0                                            # CUDA 设备号，如果无 GPU 可设为 'cpu'

def main():
    # 创建输出目录
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 加载模型
    model = YOLO(MODEL_PATH)
    
    # 遍历所有 PNG 文件
    for img_file in INPUT_DIR.glob("*.png"):
        print(f"Processing {img_file.name}...")
        
        # 运行分割推理
        results = model.predict(
            source=str(img_file),
            save=True,            # 保存可视化叠图
            #save_mask=True,       # 保存二值掩码
            project=str(OUTPUT_DIR.parent),
            name=str(OUTPUT_DIR.name),
            device=DEVICE
        )

        r = results[0]

    print("Done. Results saved in:", OUTPUT_DIR)

if __name__ == "__main__":
    main()

