#!/usr/bin/env python3
"""
地牢地图可视化器
支持将统一格式的地牢数据转换为可视化图像
支持polygon格式输出和游戏元素可视化
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import json
import os
from pathlib import Path
import logging
from matplotlib.patches import Polygon, FancyBboxPatch
import matplotlib.patheffects as PathEffects
import xml.etree.ElementTree as ET

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

logger = logging.getLogger(__name__)

class DungeonVisualizer:
    """地牢可视化器"""
    def __init__(self, figsize: Tuple[int, int] = (12, 8), dpi: int = 100):
        self.figsize = figsize
        self.dpi = dpi
        self.colors = {
            'room': '#E3F2FD',      # Softer light blue rooms
            'room_border': '#1976D2', # Modern blue borders
            'corridor': '#F3E5F5',   # Light purple corridors
            'corridor_border': '#7B1FA2', # Dark purple borders
            'connection': '#FF5722', # Orange-red connection lines
            'entrance': '#C8E6C9',   # Light green entrance
            'entrance_border': '#388E3C', # Dark green borders
            'wall': '#5D4037',       # Dark brown walls
            'background': '#FAFAFA', # Brighter background
            # Game element colors - new color scheme
            'treasure': '#FFC107',   # Amber treasure
            'boss': '#D32F2F',       # Bright red boss
            'monster': '#FF9800',    # Orange monster
            'door': '#795548'        # Brown door
        }
        
        # Game element symbols - optimized display
        self.game_symbols = {
            'treasure': 'T',      # Treasure
            'boss': 'B',          # Boss
            'monster': 'M',       # Monster
            'special': 'S',       # Special
            'door': '●'           # Door as dot
        }

    def visualize_dungeon(self, dungeon_data: Dict[str, Any], output_path: str, 
                         show_connections: bool = True, show_room_ids: bool = True,
                         show_grid: bool = True, show_game_elements: bool = True) -> bool:
        """
        可视化地牢数据
        """
        try:
            fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
            ax.set_facecolor(self.colors['background'])
            bounds = self._calculate_bounds(dungeon_data)
            if not bounds:
                logger.error("Unable to calculate dungeon bounds")
                return False
            margin_ratio = 0.10
            x_min, x_max = bounds['x_min'], bounds['x_max']
            y_min, y_max = bounds['y_min'], bounds['y_max']
            width = x_max - x_min
            height = y_max - y_min
            if width < 0.1:
                width = 1.0
                x_max = x_min + width
            if height < 0.1:
                height = 1.0
                y_max = y_min + height
            scale = 1
            if width < 5 or height < 5:
                scale = 50
            x_min, x_max = x_min * scale, x_max * scale
            y_min, y_max = y_min * scale, y_max * scale
            width = x_max - x_min
            height = y_max - y_min
            x_pad = width * margin_ratio
            y_pad = height * margin_ratio
            ax.set_xlim(x_min - x_pad, x_max + x_pad)
            ax.set_ylim(y_min - y_pad, y_max + y_pad)
            ax.set_aspect('equal', adjustable='datalim')
            if show_grid:
                self._draw_grid(ax, bounds, scale)
            self._draw_rooms(ax, dungeon_data, show_room_ids, scale)
            self._draw_corridors(ax, dungeon_data, scale)
            self._draw_walls(ax, dungeon_data, scale)
            self._draw_doors(ax, dungeon_data, scale)
            if show_game_elements:
                self._draw_game_elements(ax, dungeon_data, scale)
            if show_connections:
                self._draw_connections(ax, dungeon_data, scale)
            dungeon_name = dungeon_data.get('name', dungeon_data.get('header', {}).get('name', 'Unnamed Dungeon'))
            ax.set_title(f'Dungeon Map: {dungeon_name}', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('X (ft)', fontsize=12)
            ax.set_ylabel('Y (ft)', fontsize=12)
            self._add_legend(ax, show_game_elements)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight', facecolor='white', edgecolor='none')
            plt.close()
            logger.info(f"Dungeon Saved To: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error visualizing dungeon: {e}")
            import traceback; traceback.print_exc()
            return False

    def export_polygon_format(self, dungeon_data: Dict[str, Any], output_path: str) -> bool:
        """
        导出为polygon格式（PNG）
        """
        return self.visualize_dungeon(dungeon_data, output_path)

    def _calculate_bounds(self, dungeon_data: Dict[str, Any]) -> Optional[Dict[str, float]]:
        """计算地牢的边界"""
        x_coords, y_coords = [], []
        levels = dungeon_data.get('levels', [])
        if not levels:
            rooms = dungeon_data.get('rooms', [])
            if rooms:
                for room in rooms:
                    x_coords.extend([room.get('x', 0), room.get('x', 0) + room.get('width', 0)])
                    y_coords.extend([room.get('y', 0), room.get('y', 0) + room.get('height', 0)])
            else:
                return None
        else:
            for level in levels:
                rooms = level.get('rooms', [])
                for room in rooms:
                    if 'position' in room and 'size' in room:
                        x = room['position'].get('x', 0)
                        y = room['position'].get('y', 0)
                        width = room['size'].get('width', 1)
                        height = room['size'].get('height', 1)
                    else:
                        x = room.get('x', 0)
                        y = room.get('y', 0)
                        width = room.get('width', 1)
                        height = room.get('height', 1)
                    x_coords.extend([x, x + width])
                    y_coords.extend([y, y + height])
                corridors = level.get('corridors', [])
                for corridor in corridors:
                    if 'position' in corridor and 'size' in corridor:
                        x = corridor['position'].get('x', 0)
                        y = corridor['position'].get('y', 0)
                        width = corridor['size'].get('width', 1)
                        height = corridor['size'].get('height', 1)
                    else:
                        x = corridor.get('x', 0)
                        y = corridor.get('y', 0)
                        width = corridor.get('width', 1)
                        height = corridor.get('height', 1)
                    x_coords.extend([x, x + width])
                    y_coords.extend([y, y + height])
        if not x_coords or not y_coords:
            return None
        return {'x_min': min(x_coords), 'x_max': max(x_coords), 'y_min': min(y_coords), 'y_max': max(y_coords)}

    def _draw_grid(self, ax, bounds: Dict[str, float], scale: float = 1.0, grid_size: int = 5):
        x_min, x_max = bounds['x_min'] * scale, bounds['x_max'] * scale
        y_min, y_max = bounds['y_min'] * scale, bounds['y_max'] * scale
        for x in np.arange(x_min, x_max + grid_size, grid_size):
            ax.axvline(x=x, color='lightgray', alpha=0.3, linewidth=0.5)
        for y in np.arange(y_min, y_max + grid_size, grid_size):
            ax.axhline(y=y, color='lightgray', alpha=0.3, linewidth=0.5)

    def _draw_rooms(self, ax, dungeon_data: Dict[str, Any], show_room_ids: bool, scale: float = 1.0):
        levels = dungeon_data.get('levels', [])
        for level in levels:
            rooms = level.get('rooms', [])
            for room in rooms:
                if 'polygon' in room:
                    poly = np.array([[p['x']*scale, p['y']*scale] for p in room['polygon']]) if room['polygon'] else np.zeros((0,2))
                    if len(poly) >= 3:
                        # 优化：更美观的多边形显示
                        patch = Polygon(
                            poly, closed=True,
                            facecolor=self.colors['room'],
                            edgecolor=self.colors['room_border'],
                            alpha=0.85,
                            linewidth=2.5,
                            zorder=10,
                            joinstyle='round',
                        )
                        patch.set_path_effects([
                            PathEffects.withStroke(linewidth=4, foreground='#1B263B', alpha=0.18),
                            PathEffects.SimpleLineShadow(offset=(2,-2), alpha=0.12),
                            PathEffects.Normal()
                        ])
                        ax.add_patch(patch)
                        if show_room_ids:
                            centroid = poly.mean(axis=0)
                            label = room.get('name', room.get('id', ''))
                            txt = ax.text(
                                centroid[0], centroid[1], label, ha='center', va='center', fontsize=10, color='#222',
                                bbox=dict(boxstyle="round,pad=0.25", facecolor='white', alpha=0.7, edgecolor='#888', linewidth=0.5),
                                zorder=20
                            )
                            txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground='white', alpha=0.7)])
                    elif show_room_ids and len(poly) > 0:
                        centroid = poly.mean(axis=0)
                        label = room.get('name', room.get('id', ''))
                        txt = ax.text(
                            centroid[0], centroid[1], label, ha='center', va='center', fontsize=10, color='#222',
                            bbox=dict(boxstyle="round,pad=0.25", facecolor='white', alpha=0.7, edgecolor='#888', linewidth=0.5),
                            zorder=20
                        )
                        txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground='white', alpha=0.7)])
                else:
                    # 没有polygon字段才用矩形
                    if 'position' in room and 'size' in room:
                        x = room['position'].get('x', 0) * scale
                        y = room['position'].get('y', 0) * scale
                        w = room['size'].get('width', 1) * scale
                        h = room['size'].get('height', 1) * scale
                    else:
                        x = room.get('x', 0) * scale
                        y = room.get('y', 0) * scale
                        w = room.get('width', 1) * scale
                        h = room.get('height', 1) * scale
                    poly_points = np.array([
                        [x, y],
                        [x + w, y],
                        [x + w, y + h],
                        [x, y + h]
                    ])
                    patch = Polygon(poly_points, closed=True, facecolor=self.colors['room'], 
                                  edgecolor=self.colors['room_border'], alpha=0.85, linewidth=2.5, zorder=10)
                    patch.set_path_effects([
                        PathEffects.withStroke(linewidth=4, foreground='#1B263B', alpha=0.18),
                        PathEffects.SimpleLineShadow(offset=(2,-2), alpha=0.12),
                        PathEffects.Normal()
                    ])
                    ax.add_patch(patch)
                    if show_room_ids:
                        label = room.get('name', room.get('id', ''))
                        txt = ax.text(x + w/2, y + h/2, label, ha='center', va='center', fontsize=10, color='#222',
                                bbox=dict(boxstyle="round,pad=0.25", facecolor='white', alpha=0.7, edgecolor='#888', linewidth=0.5),
                                zorder=20)
                        txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground='white', alpha=0.7)])

    def _draw_corridors(self, ax, dungeon_data: Dict[str, Any], scale: float = 1.0):
        levels = dungeon_data.get('levels', [])
        for level in levels:
            corridors = level.get('corridors', [])
            for corridor in corridors:
                if 'polygon' in corridor:
                    poly = np.array([[p['x']*scale, p['y']*scale] for p in corridor['polygon']]) if corridor['polygon'] else np.zeros((0,2))
                    if len(poly) >= 3:
                        patch = Polygon(
                            poly, closed=True,
                            facecolor=self.colors['corridor'],
                            edgecolor=self.colors['corridor_border'],
                            alpha=0.55,
                            linewidth=2,
                            zorder=8,
                            joinstyle='round',
                        )
                        patch.set_path_effects([
                            PathEffects.withStroke(linewidth=3, foreground='#1B263B', alpha=0.10),
                            PathEffects.SimpleLineShadow(offset=(1,-1), alpha=0.10),
                            PathEffects.Normal()
                        ])
                        ax.add_patch(patch)
                else:
                    if 'position' in corridor and 'size' in corridor:
                        x = corridor['position'].get('x', 0) * scale
                        y = corridor['position'].get('y', 0) * scale
                        w = corridor['size'].get('width', 1) * scale
                        h = corridor['size'].get('height', 1) * scale
                    else:
                        x = corridor.get('x', 0) * scale
                        y = corridor.get('y', 0) * scale
                        w = corridor.get('width', 1) * scale
                        h = corridor.get('height', 1) * scale
                    poly_points = np.array([
                        [x, y],
                        [x + w, y],
                        [x + w, y + h],
                        [x, y + h]
                    ])
                    patch = Polygon(poly_points, closed=True, facecolor=self.colors['corridor'], 
                                  edgecolor=self.colors['corridor_border'], alpha=0.55, linewidth=2, zorder=8)
                    patch.set_path_effects([
                        PathEffects.withStroke(linewidth=3, foreground='#1B263B', alpha=0.10),
                        PathEffects.SimpleLineShadow(offset=(1,-1), alpha=0.10),
                        PathEffects.Normal()
                    ])
                    ax.add_patch(patch)

    def _draw_walls(self, ax, dungeon_data: Dict[str, Any], scale: float = 1.0):
        pass  # 可根据需要实现墙体绘制

    def _draw_connections(self, ax, dungeon_data: Dict[str, Any], scale: float = 1.0):
        pass  # 可根据需要实现连接线绘制

    def _draw_doors(self, ax, dungeon_data: Dict[str, Any], scale: float = 1.0):
        levels = dungeon_data.get('levels', [])
        for level in levels:
            doors = level.get('doors', [])
            for door in doors:
                pos = door.get('position', {})
                x, y = pos.get('x', 0) * scale, pos.get('y', 0) * scale
                # Draw door symbol - optimized display effect
                txt = ax.text(x, y, self.game_symbols['door'], fontsize=14, ha='center', va='center', 
                       color=self.colors['door'], weight='bold', zorder=25)
                # Add white stroke effect
                txt.set_path_effects([PathEffects.withStroke(linewidth=3, foreground='white', alpha=0.8)])

    def _draw_game_elements(self, ax, dungeon_data: Dict[str, Any], scale: float = 1.0):
        """Draw game elements (treasure, boss, monster, traps, etc.)"""
        levels = dungeon_data.get('levels', [])
        for level in levels:
            game_elements = level.get('game_elements', [])
            for element in game_elements:
                pos = element.get('position', {})
                x, y = pos.get('x', 0) * scale, pos.get('y', 0) * scale
                elem_type = element.get('type', 'unknown')
                elem_name = element.get('name', '')
                
                # Select color and symbol based on type
                if elem_type == 'treasure':
                    color = self.colors['treasure']
                    symbol = self.game_symbols['treasure']
                    fontsize = 16
                elif elem_type == 'boss':
                    color = self.colors['boss']
                    symbol = self.game_symbols['boss']
                    fontsize = 18
                elif elem_type == 'monster':
                    color = self.colors['monster']
                    symbol = self.game_symbols['monster']
                    fontsize = 16
                elif elem_type == 'special':
                    color = '#FFD700' # Gold for special elements
                    symbol = self.game_symbols['special']
                    fontsize = 16
                else:
                    color = '#9E9E9E'  # Gray
                    symbol = '?'
                    fontsize = 14
                
                # Draw symbol - optimized display effect
                txt = ax.text(x, y, symbol, fontsize=fontsize, ha='center', va='center', 
                       color=color, weight='bold', zorder=25,
                       bbox=dict(boxstyle="circle,pad=0.2", facecolor='white', alpha=0.9, 
                               edgecolor=color, linewidth=2))
                # Add white stroke and shadow effects
                txt.set_path_effects([
                    PathEffects.withStroke(linewidth=3, foreground='white', alpha=0.9),
                    PathEffects.SimpleLineShadow(offset=(1,-1), alpha=0.3),
                    PathEffects.Normal()
                ])
                
                # Add label - optimized display
                if elem_name:
                    label_txt = ax.text(x, y + 1.2 * scale, elem_name, fontsize=8, ha='center', va='bottom',
                           color='#333', weight='bold',
                           bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.9, 
                                   edgecolor=color, linewidth=1),
                           zorder=30)
                    label_txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground='white', alpha=0.7)])

    def _add_legend(self, ax, show_game_elements: bool = True):
        """添加图例"""
        legend_elements = [
            Polygon([[0,0]], color=self.colors['room'], label='Room'),
            Polygon([[0,0]], color=self.colors['corridor'], label='Corridor'),
            Polygon([[0,0]], color=self.colors['wall'], label='Wall'),
        ]
        
        if show_game_elements:
            # 添加游戏元素图例
            game_legend = [
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=self.colors['treasure'], 
                          markersize=10, label='Treasure'),
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=self.colors['boss'], 
                          markersize=10, label='Boss'),
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=self.colors['monster'], 
                          markersize=10, label='Monster'),
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=self.colors['door'], 
                          markersize=10, label='Door'),
            ]
            legend_elements.extend(game_legend)
        
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 1), fontsize=10)

# ====== 便捷入口函数 ======
def visualize_dungeon(dungeon_data: Dict[str, Any], output_path: str, 
                     figsize: Tuple[int, int] = (12, 8), dpi: int = 100,
                     show_connections: bool = True, show_room_ids: bool = True,
                     show_grid: bool = True, show_game_elements: bool = True) -> bool:
    visualizer = DungeonVisualizer(figsize=figsize, dpi=dpi)
    return visualizer.visualize_dungeon(
        dungeon_data, output_path, show_connections, show_room_ids, show_grid, show_game_elements
    )

def export_polygon_format(dungeon_data: Dict[str, Any], output_path: str) -> bool:
    """导出为polygon格式（PNG）"""
    visualizer = DungeonVisualizer()
    return visualizer.export_polygon_format(dungeon_data, output_path)

def export_polygon_from_file(input_path: str, output_path: str) -> bool:
    """从文件导出为polygon格式（PNG）"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            dungeon_data = json.load(f)
        return export_polygon_format(dungeon_data, output_path)
    except Exception as e:
        logger.error(f"Error exporting polygon from file: {e}")
        return False

def visualize_from_file(input_path: str, output_path: str, **kwargs) -> bool:
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            dungeon_data = json.load(f)
        return visualize_dungeon(dungeon_data, output_path, **kwargs)
    except Exception as e:
        logger.error(f"Error visualizing from file: {e}")
        return False

def visualize_dungeon_outline(dungeon_data: Dict[str, Any], output_path: str, 
                             figsize: Tuple[int, int] = (12, 8), dpi: int = 100,
                             show_grid: bool = True, show_room_ids: bool = True, show_corridor_ids: bool = False) -> bool:
    try:
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
        ax.set_facecolor('#F5F5F5')
        xs, ys = [], []
        levels = dungeon_data.get('levels', [])
        # 画房间轮廓
        for level in levels:
            rooms = level.get('rooms', [])
            for room in rooms:
                if 'position' in room and 'size' in room:
                    x = room['position'].get('x', 0)
                    y = room['position'].get('y', 0)
                    w = room['size'].get('width', 1)
                    h = room['size'].get('height', 1)
                else:
                    x = room.get('x', 0)
                    y = room.get('y', 0)
                    w = room.get('width', 1)
                    h = room.get('height', 1)
                xs.extend([x, x + w])
                ys.extend([y, y + h])
                rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                                     facecolor='#E8F4FD', edgecolor='#2E86AB', linewidth=2, alpha=0.7)
                ax.add_patch(rect)
                if show_room_ids:
                    label = room.get('name', room.get('id', ''))
                    ax.text(x + w/2, y + h/2, label, ha='center', va='center', fontsize=8, color='black',
                            bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.5))
        # 画走廊
        for level in levels:
            corridors = level.get('corridors', [])
            for corridor in corridors:
                if 'position' in corridor and 'size' in corridor:
                    x = corridor['position'].get('x', 0)
                    y = corridor['position'].get('y', 0)
                    w = corridor['size'].get('width', 1)
                    h = corridor['size'].get('height', 1)
                else:
                    x = corridor.get('x', 0)
                    y = corridor.get('y', 0)
                    w = corridor.get('width', 1)
                    h = corridor.get('height', 1)
                xs.extend([x, x + w])
                ys.extend([y, y + h])
                rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                                     facecolor='#CCCCCC', edgecolor='#888888', linewidth=1, alpha=0.5)
                ax.add_patch(rect)
                if show_corridor_ids:
                    label = corridor.get('name', corridor.get('id', ''))
                    ax.text(x + w/2, y + h/2, label, ha='center', va='center', fontsize=7, color='gray',
                            bbox=dict(boxstyle="round,pad=0.1", facecolor='white', alpha=0.3))
        # 统计所有房间和走廊的边界
        for level in levels:
            for node_list in [level.get('rooms', []), level.get('corridors', [])]:
                for node in node_list:
                    if 'position' in node and 'size' in node:
                        x = node['position'].get('x', 0)
                        y = node['position'].get('y', 0)
                        w = node['size'].get('width', 1)
                        h = node['size'].get('height', 1)
                    else:
                        x = node.get('x', 0)
                        y = node.get('y', 0)
                        w = node.get('width', 1)
                        h = node.get('height', 1)
                    xs.extend([x, x + w])
                    ys.extend([y, y + h])
        if not xs or not ys:
            print("❌ No room or corridor data, cannot draw bounding box")
            return False
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        rect = plt.Rectangle((x_min, y_min), x_max - x_min, y_max - y_min,
                             linewidth=3, edgecolor='red', facecolor='none', linestyle='--', alpha=0.7)
        ax.add_patch(rect)
        # 画中心点
        centers_x, centers_y = [], []
        for level in levels:
            for node_list in [level.get('rooms', []), level.get('corridors', [])]:
                for node in node_list:
                    if 'position' in node and 'size' in node:
                        x = node['position'].get('x', 0)
                        y = node['position'].get('y', 0)
                        w = node['size'].get('width', 1)
                        h = node['size'].get('height', 1)
                    else:
                        x = node.get('x', 0)
                        y = node.get('y', 0)
                        w = node.get('width', 1)
                        h = node.get('height', 1)
                    centers_x.append(x + w/2)
                    centers_y.append(y + h/2)
        ax.scatter(centers_x, centers_y, c='blue', s=30, alpha=0.7, label='Center')
        # 画门
        for level in levels:
            doors = level.get('doors', [])
            for door in doors:
                pos = door.get('position', {})
                x, y = pos.get('x', 0), pos.get('y', 0)
                ax.scatter(x, y, c='red', s=30,alpha=0.7, linewidths=1.5, label='door' if 'door' not in ax.get_legend_handles_labels()[1] else "")
        if show_grid:
            grid_size = 5
            for x in np.arange(x_min, x_max + grid_size, grid_size):
                ax.axvline(x=x, color='lightgray', alpha=0.3, linewidth=0.5)
            for y in np.arange(y_min, y_max + grid_size, grid_size):
                ax.axhline(y=y, color='lightgray', alpha=0.3, linewidth=0.5)
        margin_ratio = 0.10
        width = x_max - x_min
        height = y_max - y_min
        if width < 1e-3:
            x_max = x_min + 1
            width = 1
        if height < 1e-3:
            y_max = y_min + 1
            height = 1
        x_pad = width * margin_ratio
        y_pad = height * margin_ratio
        ax.set_xlim(x_min - x_pad, x_max + x_pad)
        ax.set_ylim(y_min - y_pad, y_max + y_pad)
        ax.set_aspect('equal', adjustable='datalim')
        ax.set_title('Dungeon Structure', fontsize=16, fontweight='bold')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.legend()
        plt.tight_layout()
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()
        print(f"Saved Map to: {output_path}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
