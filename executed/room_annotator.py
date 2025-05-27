import cv2
import json
import os
import sys

rooms = []
start_point = None

def mouse_callback(event, x, y, flags, param):
    global start_point, rooms, img_copy

    if event == cv2.EVENT_LBUTTONDOWN:
        if start_point is None:
            start_point = (x, y)
        else:
            end_point = (x, y)
            x0, y0 = min(start_point[0], end_point[0]), min(start_point[1], end_point[1])
            w, h = abs(start_point[0] - end_point[0]), abs(start_point[1] - end_point[1])
            cx, cy = x0 + w // 2, y0 + h // 2
            rooms.append({"id": len(rooms), "x": cx, "y": cy, "w": w, "h": h})
            print(f"Room {len(rooms)-1}: center=({cx},{cy}), size=({w},{h})")
            cv2.rectangle(img_copy, (x0, y0), (x0 + w, y0 + h), (0, 255, 0), 2)
            start_point = None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python room_annotator.py <image_path>")
        sys.exit(1)

    path = sys.argv[1]
    # path = './generated_maps/grid_dungeon.png'
    img = cv2.imread(path)
    img_copy = img.copy()

    cv2.namedWindow("Annotator")
    cv2.setMouseCallback("Annotator", mouse_callback)

    while True:
        cv2.imshow("Annotator", img_copy)
        key = cv2.waitKey(1) & 0xFF

        if key == 27:  # ESC
            break
        elif key == ord('s'):
            json_path = os.path.splitext(path)[0] + ".json"
            with open(json_path, 'w') as f:
                json.dump({"rooms": rooms, "edges": []}, f, indent=2)
            print(f"✅ Saved to {json_path}")
        elif key == ord('u') and rooms:
            rooms.pop()
            img_copy = img.copy()
            for r in rooms:
                cv2.rectangle(img_copy, (r["x"] - r["w"]//2, r["y"] - r["h"]//2),
                              (r["x"] + r["w"]//2, r["y"] + r["h"]//2), (0, 255, 0), 2)

    cv2.destroyAllWindows()
