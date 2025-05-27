import cv2
import numpy as np
import json
import os

def extract_rooms_and_edges(image_path, debug=False, use_cuda=False):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 自动阈值处理（Otsu 二值化）
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    if use_cuda and hasattr(cv2, "cuda") and cv2.cuda.getCudaEnabledDeviceCount() > 0:
        print("✅ CUDA detected, using GPU for preprocessing...")
        gpu_mat = cv2.cuda_GpuMat()
        gpu_mat.upload(binary)
        blur_filter = cv2.cuda.createGaussianFilter(cv2.CV_8UC1, cv2.CV_8UC1, (5, 5), 1.5)
        gpu_blurred = blur_filter.apply(gpu_mat)
        binary = gpu_blurred.download()

    # 查找轮廓
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    rooms = []
    centers = []
    i = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 300 or area > 20000:
            continue  # 忽略太小或太大的区域（如背景）
        x, y, w, h = cv2.boundingRect(cnt)
        cx, cy = x + w // 2, y + h // 2
        rooms.append({"id": i, "x": int(cx), "y": int(cy), "w": w, "h": h})
        centers.append((cx, cy))
        i += 1

    print(f"✅ Detected {len(rooms)} rooms.")

    edges = []
    threshold = 160
    for i in range(len(centers)):
        for j in range(i + 1, len(centers)):
            d = np.linalg.norm(np.array(centers[i]) - np.array(centers[j]))
            if d < threshold:
                edges.append({"from": i, "to": j})

    if debug:
        debug_img = img.copy()
        for room in rooms:
            cv2.rectangle(debug_img, (room["x"] - room["w"] // 2, room["y"] - room["h"] // 2),
                          (room["x"] + room["w"] // 2, room["y"] + room["h"] // 2), (0, 255, 0), 2)
        for edge in edges:
            pt1 = centers[edge["from"]]
            pt2 = centers[edge["to"]]
            cv2.line(debug_img, pt1, pt2, (255, 0, 0), 2)

        cv2.imshow("Detected Rooms and Edges", debug_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return rooms, edges


def save_dungeon_json(rooms, edges, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump({"rooms": rooms, "edges": edges}, f, indent=2)


if __name__ == "__main__":
    image_path = "./generated_maps/grid_dungeon.png"
    output_path = "./generated_maps/grid_dungeon.json"
    rooms, edges = extract_rooms_and_edges(image_path, debug=True, use_cuda=True)
    save_dungeon_json(rooms, edges, output_path)
    print(f"Saved to {output_path}")
