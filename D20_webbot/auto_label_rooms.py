import cv2
import os
import numpy as np
from pathlib import Path

def detect_rooms_precise(image_path, min_area=5000, min_aspect=0.3):
    """
    使用连通域分析检测房间区域，更好地区分走廊与房间.
    返回YOLO格式bounding boxes列表.
    """
    img = cv2.imread(str(image_path))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 阈值：白色(通行区)为1，黑色(墙)为0
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    binary = binary // 255  # 0 or 1

    # 形态学闭运算填补小黑洞
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    binary = cv2.morphologyEx(binary.astype(np.uint8), cv2.MORPH_CLOSE, kernel)

    # 连通域标记
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary, connectivity=8)

    h, w = binary.shape
    bboxes = []
    for i in range(1, num_labels):
        x, y, bw, bh, area = stats[i]
        # 面积阈值 & 宽高比例过滤 (走廊通常很窄)
        if area >= min_area and (bw/float(bh) > min_aspect and bh/float(bw) > min_aspect):
            xc = (x + bw/2)/w
            yc = (y + bh/2)/h
            nw = bw/w
            nh = bh/h
            bboxes.append((0, xc, yc, nw, nh))
    return bboxes

def batch_label_folder(image_dir, label_dir, min_area=3000):
    """
    批量处理 image_dir 下所有 .png 文件，检测房间并保存对应 .txt 标签到 label_dir.
    """
    image_dir = Path(image_dir)
    label_dir = Path(label_dir)
    label_dir.mkdir(parents=True, exist_ok=True)

    stats = {}
    for image_path in sorted(image_dir.glob("*.png")):
        bboxes = detect_rooms_precise(image_path, min_area)
        label_path = label_dir / f"{image_path.stem}.txt"
        with open(label_path, 'w') as f:
            for box in bboxes:
                f.write(" ".join(f"{v:.6f}" for v in box) + "\n")
        stats[image_path.name] = len(bboxes)
        print(f"🖼️ {image_path.name}: {len(bboxes)} rooms")

    # 保存统计信息
    stats_file = label_dir / "detection_stats.txt"
    with open(stats_file, 'w') as f:
        for img_name, count in stats.items():
            f.write(f"{img_name}: {count}\n")
    print(f"\n✅ 批量标注完成，统计文件已保存至 {stats_file}")

    return stats

if __name__ == "__main__":
    # === 配置区域：请根据实际修改 ===
    IMAGE_DIR = "dataset_donjon/images/training"       # 地牢地图图片所在文件夹
    LABEL_DIR = "dataset_donjon/labels/cv_training"     # YOLO 标签输出文件夹
    MIN_AREA = 3000                        # 最小房间轮廓面积阈值

    # 执行批量标注
    batch_label_folder(IMAGE_DIR, LABEL_DIR, MIN_AREA)
