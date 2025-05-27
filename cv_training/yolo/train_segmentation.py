# train_segmentation.py
import torch
from ultralytics import YOLO
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

def main():
    if torch.cuda.is_available():
        print("CUDA available")
    # 加载轻量预训练分割模型
    model = YOLO("yolov8n-seg.pt")

    # 训练
    model.train(
        data="C:/Users/lchna/Desktop/traningdata/seg.yaml",
        epochs=100,
        imgsz=640,
        device="0",        # 指定使用 GPU 0（CUDA）
        name="room-seg",
        workers=4
    )

    # 推理
    model.predict(
        source="C:/Users/lchna/Desktop/traningdata/images/train/",
        save=True,
        device="0"
    )

if __name__ == "__main__":
    main()
