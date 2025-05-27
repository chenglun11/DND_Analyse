import cv2
import numpy as np
import random
import os

def draw_room(img, x, y, w, h, color=(0, 0, 0), thickness=-1):
    cv2.rectangle(img, (x, y), (x + w, y + h), color, thickness)

def draw_corridor(img, x1, y1, x2, y2, color=(0, 0, 0), thickness=4):
    cv2.line(img, (x1, y1), (x2, y2), color, thickness)

def generate_linear_dungeon(filename, num_rooms=5):
    img = 255 * np.ones((400, 800, 3), dtype=np.uint8)
    spacing = 120
    w, h = 60, 40

    coords = []
    for i in range(num_rooms):
        x = 50 + i * spacing
        y = 150
        draw_room(img, x, y, w, h)
        coords.append((x + w // 2, y + h // 2))

    for i in range(len(coords) - 1):
        draw_corridor(img, coords[i][0], coords[i][1], coords[i + 1][0], coords[i + 1][1])

    cv2.imwrite(filename, img)

def generate_star_dungeon(filename, center_x=400, center_y=200, num_branches=4):
    img = 255 * np.ones((400, 800, 3), dtype=np.uint8)
    w, h = 60, 40

    draw_room(img, center_x - w // 2, center_y - h // 2, w, h)
    center = (center_x, center_y)

    angles = np.linspace(0, 2 * np.pi, num_branches, endpoint=False)
    radius = 150

    for angle in angles:
        x = int(center_x + radius * np.cos(angle))
        y = int(center_y + radius * np.sin(angle))
        draw_room(img, x - w // 2, y - h // 2, w, h)
        draw_corridor(img, center_x, center_y, x, y)

    cv2.imwrite(filename, img)

def generate_grid_dungeon(filename, rows=2, cols=3):
    img = 255 * np.ones((400, 800, 3), dtype=np.uint8)
    w, h = 60, 40
    spacing_x = 120
    spacing_y = 100
    offset_x = 100
    offset_y = 80

    coords = []
    for i in range(rows):
        for j in range(cols):
            x = offset_x + j * spacing_x
            y = offset_y + i * spacing_y
            draw_room(img, x, y, w, h)
            coords.append((x + w // 2, y + h // 2))

    for i in range(rows):
        for j in range(cols):
            idx = i * cols + j
            if j < cols - 1:
                draw_corridor(img, coords[idx][0], coords[idx][1], coords[idx + 1][0], coords[idx + 1][1])
            if i < rows - 1:
                draw_corridor(img, coords[idx][0], coords[idx][1], coords[idx + cols][0], coords[idx + cols][1])

    cv2.imwrite(filename, img)


if __name__ == "__main__":
    os.makedirs("generated_maps", exist_ok=True)
    generate_linear_dungeon("generated_maps/linear_dungeon.png")
    generate_star_dungeon("generated_maps/star_dungeon.png")
    generate_grid_dungeon("generated_maps/grid_dungeon.png")
    print
