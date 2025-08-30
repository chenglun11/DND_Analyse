#!/usr/bin/env python3
"""
Dungeon map visualizer
Supports converting unified format dungeon data to visualization images
Supports polygon format output and game element visualization
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
from matplotlib.patches import Polygon, FancyBboxPatch, Path, PathPatch
import matplotlib.patheffects as PathEffects
import xml.etree.ElementTree as ET
import heapq

# Set Chinese font
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

logger = logging.getLogger(__name__)

class DungeonVisualizer:
    """Dungeon visualizer"""
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
            'exit': '#FFCDD2',       # Light red exit
            'exit_border': '#D32F2F', # Dark red borders
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
            'door': '●',          # Door as dot
            'entrance': 'IN',     # Entrance symbol
            'exit': 'OUT'         # Exit symbol
        }

    def visualize_dungeon(self, dungeon_data: Dict[str, Any], output_path: str, 
                         show_connections: bool = True, show_room_ids: bool = True,
                         show_grid: bool = True, show_game_elements: bool = True) -> bool:
        """
        Visualize dungeon data
        """
        try:
            # Detect if it's Edgar format, if so use Edgar-specific visualization
            if self._is_edgar_format(dungeon_data):
                return self._visualize_edgar_dungeon(dungeon_data, output_path, 
                                                   show_connections, show_room_ids, 
                                                   show_grid, show_game_elements)
            
            # Original visualization logic
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
            ax.set_aspect('equal', adjustable='box')
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
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir:  # 只有当目录不为空时才创建
                os.makedirs(output_dir, exist_ok=True)
            
            plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight', facecolor='white', edgecolor='none')
            plt.close()
            logger.info(f"Dungeon Saved To: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error visualizing dungeon: {e}")
            import traceback; traceback.print_exc()
            return False

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
                # 处理rooms
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
                
                # 处理corridors
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
                # 不再区分入口/出口，仅用普通房间样式
                face_color = self.colors['room']
                border_color = self.colors['room_border']
                border_width = 2.0
                if 'polygon' in room:
                    poly = np.array([[p['x']*scale, p['y']*scale] for p in room['polygon']]) if room['polygon'] else np.zeros((0,2))
                    if len(poly) >= 3:
                        patch = Polygon(
                            poly, closed=True,
                            facecolor=face_color,
                            edgecolor=border_color,
                            alpha=0.85,
                            linewidth=border_width,
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
                                centroid[0], centroid[1], label, ha='center', va='center', fontsize=12, color='#222',
                                bbox=dict(boxstyle="round,pad=0.28", facecolor='white', alpha=0.7, edgecolor='#888', linewidth=0.5),
                                zorder=20
                            )
                            txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground='white', alpha=0.7)])
                    elif show_room_ids and len(poly) > 0:
                        centroid = poly.mean(axis=0)
                        label = room.get('name', room.get('id', ''))
                        txt = ax.text(
                            centroid[0], centroid[1], label, ha='center', va='center', fontsize=12, color='#222',
                            bbox=dict(boxstyle="round,pad=0.28", facecolor='white', alpha=0.7, edgecolor='#888', linewidth=0.5),
                            zorder=20
                        )
                        txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground='white', alpha=0.7)])
                else:
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
                    patch = Polygon(poly_points, closed=True, facecolor=face_color, 
                                  edgecolor=border_color, alpha=0.85, linewidth=border_width, zorder=10)
                    patch.set_path_effects([
                        PathEffects.withStroke(linewidth=4, foreground='#1B263B', alpha=0.18),
                        PathEffects.SimpleLineShadow(offset=(2,-2), alpha=0.12),
                        PathEffects.Normal()
                    ])
                    ax.add_patch(patch)
                    if show_room_ids:
                        label = room.get('name', room.get('id', ''))
                        txt = ax.text(x + w/2, y + h/2, label, ha='center', va='center', fontsize=12, color='#222',
                                bbox=dict(boxstyle="round,pad=0.28", facecolor='white', alpha=0.7, edgecolor='#888', linewidth=0.5),
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
        """绘制房间之间的连接线"""
        levels = dungeon_data.get('levels', [])
        for level in levels:
            connections = level.get('connections', [])
            rooms = {room['id']: room for room in level.get('rooms', [])}
            
            for connection in connections:
                from_room_id = connection.get('from_room')
                to_room_id = connection.get('to_room')
                
                if from_room_id in rooms and to_room_id in rooms:
                    from_room = rooms[from_room_id]
                    to_room = rooms[to_room_id]
                    
                    # 获取房间中心点
                    if 'position' in from_room and 'size' in from_room:
                        from_x = (from_room['position'].get('x', 0) + from_room['size'].get('width', 0) / 2) * scale
                        from_y = (from_room['position'].get('y', 0) + from_room['size'].get('height', 0) / 2) * scale
                    else:
                        from_x = (from_room.get('x', 0) + from_room.get('width', 0) / 2) * scale
                        from_y = (from_room.get('y', 0) + from_room.get('height', 0) / 2) * scale
                    
                    if 'position' in to_room and 'size' in to_room:
                        to_x = (to_room['position'].get('x', 0) + to_room['size'].get('width', 0) / 2) * scale
                        to_y = (to_room['position'].get('y', 0) + to_room['size'].get('height', 0) / 2) * scale
                    else:
                        to_x = (to_room.get('x', 0) + to_room.get('width', 0) / 2) * scale
                        to_y = (to_room.get('y', 0) + to_room.get('height', 0) / 2) * scale
                    
                    # 绘制连接线
                    ax.plot([from_x, to_x], [from_y, to_y], 
                           color=self.colors['connection'], 
                           linewidth=3, 
                           alpha=0.8, 
                           zorder=5,
                           solid_capstyle='round')
                    
                    # 添加箭头指示方向
                    mid_x = (from_x + to_x) / 2
                    mid_y = (from_y + to_y) / 2
                    dx = to_x - from_x
                    dy = to_y - from_y
                    length = np.sqrt(dx*dx + dy*dy)
                    if length > 0:
                        # 归一化方向向量
                        dx, dy = dx/length, dy/length
                        # 箭头位置（稍微偏向目标房间）
                        arrow_x = mid_x + dx * 5
                        arrow_y = mid_y + dy * 5
                        # 绘制箭头
                        ax.arrow(arrow_x - dx*3, arrow_y - dy*3, dx*6, dy*6,
                               head_width=2, head_length=3, fc=self.colors['connection'], 
                               ec=self.colors['connection'], alpha=0.8, zorder=6)

    def _draw_doors(self, ax, dungeon_data: Dict[str, Any], scale: float = 1.0):
        levels = dungeon_data.get('levels', [])
        for level in levels:
            doors = level.get('doors', [])
            for door in doors:
                pos = door.get('position', {})
                x, y = pos.get('x', 0) * scale, pos.get('y', 0) * scale
                txt = ax.text(x, y, self.game_symbols['door'], fontsize=16, ha='center', va='center', 
                       color=self.colors['door'], weight='bold', zorder=20)
                txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground='white', alpha=0.8)])

    def _draw_game_elements(self, ax, dungeon_data: Dict[str, Any], scale: float = 1.0):
        levels = dungeon_data.get('levels', [])
        for level in levels:
            game_elements = level.get('game_elements', [])
            for element in game_elements:
                pos = element.get('position', {})
                x, y = pos.get('x', 0) * scale, pos.get('y', 0) * scale
                elem_type = element.get('type', 'unknown')
                elem_name = element.get('name', '')
                if elem_type == 'treasure':
                    color = self.colors['treasure']
                    symbol = self.game_symbols['treasure']
                    fontsize = 12
                elif elem_type == 'boss':
                    color = self.colors['boss']
                    symbol = self.game_symbols['boss']
                    fontsize = 14
                elif elem_type == 'monster':
                    color = self.colors['monster']
                    symbol = self.game_symbols['monster']
                    fontsize = 12
                elif elem_type == 'special':
                    color = '#FFD700'
                    symbol = self.game_symbols['special']
                    fontsize = 12
                else:
                    color = '#9E9E9E'
                    symbol = '?'
                    fontsize = 10
                txt = ax.text(x, y, symbol, fontsize=fontsize, ha='center', va='center', 
                       color=color, weight='bold', zorder=22,
                       bbox=dict(boxstyle="circle,pad=0.18", facecolor='white', alpha=0.9, 
                               edgecolor=color, linewidth=1.5))
                txt.set_path_effects([
                    PathEffects.withStroke(linewidth=2, foreground='white', alpha=0.9),
                    PathEffects.SimpleLineShadow(offset=(1,-1), alpha=0.3),
                    PathEffects.Normal()
                ])
                if elem_name:
                    label_txt = ax.text(x, y + 1.0 * scale, elem_name, fontsize=9, ha='center', va='bottom',
                           color='#333', weight='bold',
                           bbox=dict(boxstyle="round,pad=0.15", facecolor='white', alpha=0.9, 
                                   edgecolor=color, linewidth=1),
                           zorder=28)
                    label_txt.set_path_effects([PathEffects.withStroke(linewidth=1.5, foreground='white', alpha=0.7)])

    def _add_legend(self, ax, show_game_elements: bool = True):
        legend_elements = [
            Polygon([[0,0]], color=self.colors['room'], label='Room'),
            Polygon([[0,0]], color=self.colors['entrance'], label='Entrance'),
            Polygon([[0,0]], color=self.colors['exit'], label='Exit'),
            Polygon([[0,0]], color=self.colors['corridor'], label='Corridor'),
            Polygon([[0,0]], color=self.colors['wall'], label='Wall'),
        ]
        if show_game_elements:
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

    def _is_edgar_format(self, dungeon_data: Dict[str, Any]) -> bool:
        """检测是否为edgar格式"""
        # 检查header中的author字段
        header = dungeon_data.get('header', {})
        author = header.get('author', '')
        if 'Edgar' in author:
            return True
        
        # 检查description字段
        description = header.get('description', '')
        if 'Edgar' in description:
            return True
        
        # 检查房间描述
        levels = dungeon_data.get('levels', [])
        if levels:
            for level in levels:
                rooms = level.get('rooms', [])
                for room in rooms:
                    room_desc = room.get('description', '')
                    if 'Edgar' in room_desc:
                        return True
        
        return False

    def _visualize_edgar_dungeon(self, dungeon_data: Dict[str, Any], output_path: str,
                               show_connections: bool, show_room_ids: bool,
                               show_grid: bool, show_game_elements: bool) -> bool:
        """Edgar风格的地牢可视化"""
        try:
            # Edgar颜色方案
            colors = {
                'background': '#F8F8F4',  # Edgar默认背景色
                'room': '#F8F8F4',        # 房间背景色
                'border': '#323232',      # 房间边框色
                'grid': '#646464',        # 网格色
                'connection': '#FF5722',  # 连接线色（橙色）
                'corridor': '#E0E0E0',    # 走廊色
                'corridor_border': '#323232'  # 走廊边框色
            }
            
            # 计算边界
            bounds = self._calculate_bounds(dungeon_data)
            if not bounds:
                logger.error("unable to calculate the bround")
                return False
            
            # 创建图形
            fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
            ax.set_xlim(bounds['x_min'] - 10, bounds['x_max'] + 10)
            ax.set_ylim(bounds['y_min'] - 10, bounds['y_max'] + 10)
            ax.set_aspect('equal')
            ax.invert_yaxis()  # 反转Y轴以匹配游戏坐标系统
            
            # 设置背景色
            ax.set_facecolor(colors['background'])
            fig.patch.set_facecolor(colors['background'])
            
            # 绘制网格
            if show_grid:
                self._draw_edgar_grid(ax, bounds, colors['grid'])
            
            # 绘制房间（带门的开口）
            self._draw_edgar_rooms_with_doors(ax, dungeon_data, show_room_ids, colors)
            
            # 绘制连接线
            if show_connections:
                self._draw_edgar_connections(ax, dungeon_data, colors['connection'])
            
            # 设置标题和标签
            ax.set_title('Edgar Dungeon: ' + dungeon_data.get('header', {}).get('name', 'Edgar Dungeon'), 
                        fontsize=16, fontweight='bold', color='#323232', pad=20)
            ax.set_xlabel('X (tiles)', fontsize=12, color='#323232')
            ax.set_ylabel('Y (tiles)', fontsize=12, color='#323232')
            
            # 移除坐标轴刻度
            ax.set_xticks([])
            ax.set_yticks([])
            
            # 保存图像
            plt.tight_layout()
            plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight', 
                       facecolor=colors['background'], edgecolor='none')
            plt.close()
            
            logger.info(f"Edgar地牢已保存到: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Edgar地牢可视化失败: {e}")
            return False

    def _draw_edgar_grid(self, ax, bounds: Dict[str, float], grid_color: str):
        """绘制edgar风格的网格"""
        x_min, x_max = bounds['x_min'], bounds['x_max']
        y_min, y_max = bounds['y_min'], bounds['y_max']
        
        # 绘制虚线网格，类似edgar的网格样式
        for x in np.arange(x_min, x_max + 1, 1):
            ax.axvline(x=x, color=grid_color, alpha=0.3, linewidth=0.5, linestyle='--')
        for y in np.arange(y_min, y_max + 1, 1):
            ax.axhline(y=y, color=grid_color, alpha=0.3, linewidth=0.5, linestyle='--')

    def _draw_edgar_rooms_with_doors(self, ax, dungeon_data: Dict[str, Any], show_room_ids: bool, colors: Dict[str, str]):
        """绘制Edgar风格的房间，在门的位置创建开口"""
        levels = dungeon_data.get('levels', [])
        for level in levels:
            rooms = level.get('rooms', [])
            connections = level.get('connections', [])
            
            # 创建房间ID到房间的映射
            room_map = {room['id']: room for room in rooms}
            
            for room in rooms:
                if room.get('is_corridor', False):
                    continue  # 跳过走廊房间，只处理真正的房间
                
                # 获取房间位置和尺寸
                if 'position' in room and 'size' in room:
                    x = room['position'].get('x', 0)
                    y = room['position'].get('y', 0)
                    w = room['size'].get('width', 1)
                    h = room['size'].get('height', 1)
                else:
                    continue
                
                # 找到与此房间相关的门
                room_id = room['id']
                door_positions = []
                
                for connection in connections:
                    from_room_id = connection.get('from_room')
                    to_room_id = connection.get('to_room')
                    
                    if from_room_id == room_id and to_room_id in room_map:
                        # 计算门的位置（在房间边界上）
                        door_pos = self._calculate_door_position(room, room_map[to_room_id])
                        if door_pos:
                            door_positions.append(door_pos)
                    elif to_room_id == room_id and from_room_id in room_map:
                        # 计算门的位置（在房间边界上）
                        door_pos = self._calculate_door_position(room, room_map[from_room_id])
                        if door_pos:
                            door_positions.append(door_pos)
                
                # 绘制房间轮廓（带门的开口）
                self._draw_room_with_doors(ax, room, door_positions, colors, show_room_ids)

    def _calculate_door_position(self, room1: Dict[str, Any], room2: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """计算两个房间之间门的位置"""
        # 获取房间位置和尺寸
        x1 = room1['position'].get('x', 0)
        y1 = room1['position'].get('y', 0)
        w1 = room1['size'].get('width', 1)
        h1 = room1['size'].get('height', 1)
        
        x2 = room2['position'].get('x', 0)
        y2 = room2['position'].get('y', 0)
        w2 = room2['size'].get('width', 1)
        h2 = room2['size'].get('height', 1)
        
        # 计算房间中心
        center1_x = x1 + w1 / 2
        center1_y = y1 + h1 / 2
        center2_x = x2 + w2 / 2
        center2_y = y2 + h2 / 2
        
        # 门宽度
        door_width = 2
        
        # 确定门的位置（在房间1的边界上）
        if abs(center1_x - center2_x) > abs(center1_y - center2_y):
            # 水平连接
            if center1_x < center2_x:
                # 房间1在左边，门在右边
                door_x = x1 + w1
                door_y = center1_y - door_width / 2
                door_w = door_width
                door_h = door_width
                side = 'right'
            else:
                # 房间1在右边，门在左边
                door_x = x1
                door_y = center1_y - door_width / 2
                door_w = door_width
                door_h = door_width
                side = 'left'
        else:
            # 垂直连接
            if center1_y < center2_y:
                # 房间1在下边，门在上边
                door_x = center1_x - door_width / 2
                door_y = y1 + h1
                door_w = door_width
                door_h = door_width
                side = 'top'
            else:
                # 房间1在上边，门在下边
                door_x = center1_x - door_width / 2
                door_y = y1
                door_w = door_width
                door_h = door_width
                side = 'bottom'
        
        return {
            'x': door_x,
            'y': door_y,
            'width': door_w,
            'height': door_h,
            'side': side
        }

    def _draw_room_with_doors(self, ax, room: Dict[str, Any], door_positions: List[Dict[str, Any]], 
                            colors: Dict[str, str], show_room_ids: bool):
        """绘制带门开口的房间"""
        x = room['position'].get('x', 0)
        y = room['position'].get('y', 0)
        w = room['size'].get('width', 1)
        h = room['size'].get('height', 1)
        
        # 创建房间轮廓路径
        from matplotlib.patches import Path, PathPatch
        
        # 房间的四个角
        corners = [
            (x, y),           # 左下
            (x + w, y),       # 右下
            (x + w, y + h),   # 右上
            (x, y + h),       # 左上
            (x, y)            # 回到起点
        ]
        
        # 创建路径
        path_vertices = []
        path_codes = []
        
        # 从第一个角开始
        path_vertices.append(corners[0])
        path_codes.append(Path.MOVETO)
        
        # 处理每个边，检查是否有门
        for i in range(4):
            start_corner = corners[i]
            end_corner = corners[i + 1]
            
            # 检查这条边上是否有门
            door_on_edge = None
            for door in door_positions:
                if self._is_door_on_edge(start_corner, end_corner, door):
                    door_on_edge = door
                    break
            
            if door_on_edge:
                # 有门，创建开口
                door_x = door_on_edge['x']
                door_y = door_on_edge['y']
                door_w = door_on_edge['width']
                door_h = door_on_edge['height']
                
                # 根据边的方向确定门的位置
                if start_corner[0] == end_corner[0]:  # 垂直线
                    # 门在垂直边上
                    if start_corner[1] < end_corner[1]:  # 向上
                        # 从下到门
                        path_vertices.append((start_corner[0], door_y))
                        path_codes.append(Path.LINETO)
                        # 跳过门
                        path_vertices.append((start_corner[0], door_y + door_h))
                        path_codes.append(Path.MOVETO)
                        # 从门到上
                        path_vertices.append(end_corner)
                        path_codes.append(Path.LINETO)
                    else:  # 向下
                        # 从上到门
                        path_vertices.append((start_corner[0], door_y + door_h))
                        path_codes.append(Path.LINETO)
                        # 跳过门
                        path_vertices.append((start_corner[0], door_y))
                        path_codes.append(Path.MOVETO)
                        # 从门到下
                        path_vertices.append(end_corner)
                        path_codes.append(Path.LINETO)
                else:  # 水平线
                    # 门在水平边上
                    if start_corner[0] < end_corner[0]:  # 向右
                        # 从左到门
                        path_vertices.append((door_x, start_corner[1]))
                        path_codes.append(Path.LINETO)
                        # 跳过门
                        path_vertices.append((door_x + door_w, start_corner[1]))
                        path_codes.append(Path.MOVETO)
                        # 从门到右
                        path_vertices.append(end_corner)
                        path_codes.append(Path.LINETO)
                    else:  # 向左
                        # 从右到门
                        path_vertices.append((door_x + door_w, start_corner[1]))
                        path_codes.append(Path.LINETO)
                        # 跳过门
                        path_vertices.append((door_x, start_corner[1]))
                        path_codes.append(Path.MOVETO)
                        # 从门到左
                        path_vertices.append(end_corner)
                        path_codes.append(Path.LINETO)
            else:
                # 没有门，直接连线
                path_vertices.append(end_corner)
                path_codes.append(Path.LINETO)
        
        # 创建路径
        path = Path(path_vertices, path_codes)
        
        # 绘制房间填充
        patch = PathPatch(path, facecolor=colors['room'], edgecolor='none', alpha=0.85, zorder=10)
        ax.add_patch(patch)
        
        # 绘制房间边框
        border_patch = PathPatch(path, facecolor='none', edgecolor=colors['border'], 
                               linewidth=2, zorder=11)
        ax.add_patch(border_patch)
        
        # 添加房间标签
        if show_room_ids:
            label = room.get('name', room.get('id', ''))
            txt = ax.text(x + w/2, y + h/2, label, ha='center', va='center', 
                         fontsize=12, color='#222', weight='bold',
                         bbox=dict(boxstyle="round,pad=0.3", facecolor='white', 
                                 alpha=0.8, edgecolor='#888', linewidth=0.5),
                         zorder=20)
            txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground='white', alpha=0.8)])

    def _is_door_on_edge(self, start_corner: Tuple[float, float], end_corner: Tuple[float, float], 
                        door: Dict[str, Any]) -> bool:
        """检查门是否在指定的边上"""
        door_x = door['x']
        door_y = door['y']
        door_w = door['width']
        door_h = door['height']
        
        # 检查门是否与边重叠
        if start_corner[0] == end_corner[0]:  # 垂直线
            # 门应该在垂直边上
            return (abs(door_x - start_corner[0]) < 1 and 
                   door_y >= min(start_corner[1], end_corner[1]) and 
                   door_y + door_h <= max(start_corner[1], end_corner[1]))
        else:  # 水平线
            # 门应该在水平边上
            return (abs(door_y - start_corner[1]) < 1 and 
                   door_x >= min(start_corner[0], end_corner[0]) and 
                   door_x + door_w <= max(start_corner[0], end_corner[0]))

    def _draw_edgar_connections(self, ax, dungeon_data: Dict[str, Any], connection_color: str):
        """绘制Edgar风格的连接线"""
        levels = dungeon_data.get('levels', [])
        
        for level in levels:
            connections = level.get('connections', [])
            rooms = {room['id']: room for room in level.get('rooms', [])}
            
            for connection in connections:
                from_room_id = connection.get('from_room')
                to_room_id = connection.get('to_room')
                
                if from_room_id in rooms and to_room_id in rooms:
                    from_room = rooms[from_room_id]
                    to_room = rooms[to_room_id]
                    
                    # 获取房间中心点
                    if 'position' in from_room and 'size' in from_room:
                        from_x = (from_room['position'].get('x', 0) + from_room['size'].get('width', 0) / 2)
                        from_y = (from_room['position'].get('y', 0) + from_room['size'].get('height', 0) / 2)
                    else:
                        from_x = (from_room.get('x', 0) + from_room.get('width', 0) / 2)
                        from_y = (from_room.get('y', 0) + from_room.get('height', 0) / 2)
                    
                    if 'position' in to_room and 'size' in to_room:
                        to_x = (to_room['position'].get('x', 0) + to_room['size'].get('width', 0) / 2)
                        to_y = (to_room['position'].get('y', 0) + to_room['size'].get('height', 0) / 2)
                    else:
                        to_x = (to_room.get('x', 0) + to_room.get('width', 0) / 2)
                        to_y = (to_room.get('y', 0) + to_room.get('height', 0) / 2)
                    
                    # 绘制连接线
                    ax.plot([from_x, to_x], [from_y, to_y], 
                           color=connection_color, 
                           linewidth=2, 
                           alpha=0.8, 
                           zorder=5,
                           solid_capstyle='round')

    def _extract_visualization_data(self, dungeon_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取前端可用的可视化数据"""
        try:
            if not dungeon_data or 'levels' not in dungeon_data:
                return self._create_default_visualization_data()
            
            level = dungeon_data['levels'][0] if dungeon_data['levels'] else {}
            rooms = level.get('rooms', [])
            corridors = level.get('corridors', [])
            connections = level.get('connections', [])
            
            # 转换房间和通道数据
            frontend_rooms = []
            frontend_corridors = []
            
            # 处理房间数据
            for room in rooms:
                # 提取位置信息
                x = 0
                y = 0
                width = 50
                height = 50
                
                if room.get('position'):
                    x = room['position'].get('x', 0)
                    y = room['position'].get('y', 0)
                elif 'x' in room and 'y' in room:
                    x = room['x']
                    y = room['y']
                
                if room.get('size'):
                    width = room['size'].get('width', 50)
                    height = room['size'].get('height', 50)
                elif 'width' in room and 'height' in room:
                    width = room['width']
                    height = room['height']
                
                # 缩放坐标
                x = x * 5 + 400
                y = y * 5 + 300
                width = width * 5
                height = height * 5
                
                # 确定房间类型
                room_type = room.get('room_type', 'room')
                if room.get('is_entrance'):
                    room_type = 'entrance'
                elif 'boss' in room.get('name', '').lower() or 'boss' in room.get('description', '').lower():
                    room_type = 'boss'
                elif 'treasure' in room.get('name', '').lower() or 'treasure' in room.get('description', '').lower():
                    room_type = 'treasure'
                
                frontend_rooms.append({
                    'id': room.get('id', f'room_{len(frontend_rooms)}'),
                    'x': x,
                    'y': y,
                    'width': width,
                    'height': height,
                    'type': room_type,
                    'connections': room.get('connections', []),
                    'name': room.get('name', ''),
                    'description': room.get('description', '')
                })
            
            # 处理专门的通道数组（如果有的话，且包含path信息）
            corridors = level.get('corridors', [])
            for corridor in corridors:
                # 检查是否有path信息（Royal Flush格式）
                if 'path' in corridor and corridor['path']:
                    path = corridor['path']
                    if len(path) >= 2:
                        # 取路径的第一个和最后一个点
                        start_point = path[0]
                        end_point = path[-1]
                        
                        # 缩放坐标
                        start_x = start_point['x'] * 5 + 400
                        start_y = start_point['y'] * 5 + 300
                        end_x = end_point['x'] * 5 + 400
                        end_y = end_point['y'] * 5 + 300
                        
                        frontend_corridors.append({
                            'id': corridor.get('id', f'corridor_{len(frontend_corridors)}'),
                            'start': {'x': start_x, 'y': start_y},
                            'end': {'x': end_x, 'y': end_y},
                            'width': 8,
                            'name': corridor.get('name', f'Corridor {len(frontend_corridors)}'),
                            'connection_type': 'physical'
                        })
                else:
                    # 没有path信息，使用position/size信息（回退处理）
                    x = 0
                    y = 0
                    width = 50
                    height = 50
                    
                    if corridor.get('position'):
                        x = corridor['position'].get('x', 0)
                        y = corridor['position'].get('y', 0)
                    elif 'x' in corridor and 'y' in corridor:
                        x = corridor['x']
                        y = corridor['y']
                    
                    if corridor.get('size'):
                        width = corridor['size'].get('width', 50)
                        height = corridor['size'].get('height', 50)
                    elif 'width' in corridor and 'height' in corridor:
                        width = corridor['width']
                        height = corridor['height']
                    
                    # 缩放坐标
                    x = x * 5 + 400
                    y = y * 5 + 300
                    width = width * 5
                    height = height * 5
                    
                    # 转换为线段
                    if width > height:
                        # 水平通道
                        start_x = x
                        start_y = y + height / 2
                        end_x = x + width
                        end_y = y + height / 2
                    else:
                        # 垂直通道
                        start_x = x + width / 2
                        start_y = y
                        end_x = x + width / 2
                        end_y = y + height
                    
                    frontend_corridors.append({
                        'id': corridor.get('id', f'corridor_{len(frontend_corridors)}'),
                        'start': {'x': start_x, 'y': start_y},
                        'end': {'x': end_x, 'y': end_y},
                        'width': 8,
                        'name': corridor.get('name', f'Corridor {len(frontend_corridors)}'),
                        'connection_type': 'physical'
                    })
            
            # 基于连接关系生成通道
            for connection in connections:
                from_room_id = connection.get('from_room')
                to_room_id = connection.get('to_room')
                
                if from_room_id and to_room_id:
                    # 查找对应的房间
                    from_room = None
                    to_room = None
                    
                    # 在房间数组中查找
                    for room in rooms:
                        if room['id'] == from_room_id:
                            from_room = room
                        elif room['id'] == to_room_id:
                            to_room = room
                    
                    if from_room and to_room:
                        # 计算房间中心点
                        from_x = from_room.get('position', {}).get('x', 0) * 5 + 400
                        from_y = from_room.get('position', {}).get('y', 0) * 5 + 300
                        from_width = from_room.get('size', {}).get('width', 50) * 5
                        from_height = from_room.get('size', {}).get('height', 50) * 5
                        
                        to_x = to_room.get('position', {}).get('x', 0) * 5 + 400
                        to_y = to_room.get('position', {}).get('y', 0) * 5 + 300
                        to_width = to_room.get('size', {}).get('width', 50) * 5
                        to_height = to_room.get('size', {}).get('height', 50) * 5
                        
                        from_center_x = from_x + from_width / 2
                        from_center_y = from_y + from_height / 2
                        to_center_x = to_x + to_width / 2
                        to_center_y = to_y + to_height / 2
                        
                        # 创建连接通道
                        corridor_id = f'connection_{from_room_id}_{to_room_id}'
                        
                        # 检查是否已存在相同的连接
                        existing_connection = False
                        for existing_corridor in frontend_corridors:
                            if (existing_corridor['start']['x'] == from_center_x and 
                                existing_corridor['start']['y'] == from_center_y and
                                existing_corridor['end']['x'] == to_center_x and 
                                existing_corridor['end']['y'] == to_center_y):
                                existing_connection = True
                                break
                        
                        if not existing_connection:
                            frontend_corridors.append({
                                'id': corridor_id,
                                'start': {'x': from_center_x, 'y': from_center_y},
                                'end': {'x': to_center_x, 'y': to_center_y},
                                'width': 6,
                                'name': f'Connection {from_room_id} to {to_room_id}',
                                'connection_type': 'room_to_room'
                            })
            
            # 计算地图边界
            min_x = min([room['x'] for room in frontend_rooms]) if frontend_rooms else 0
            max_x = max([room['x'] + room['width'] for room in frontend_rooms]) if frontend_rooms else 800
            min_y = min([room['y'] for room in frontend_rooms]) if frontend_rooms else 0
            max_y = max([room['y'] + room['height'] for room in frontend_rooms]) if frontend_rooms else 600
            
            if frontend_corridors:
                corridor_xs = [c['start']['x'] for c in frontend_corridors] + [c['end']['x'] for c in frontend_corridors]
                corridor_ys = [c['start']['y'] for c in frontend_corridors] + [c['end']['y'] for c in frontend_corridors]
                min_x = min(min_x, min(corridor_xs))
                max_x = max(max_x, max(corridor_xs))
                min_y = min(min_y, min(corridor_ys))
                max_y = max(max_y, max(corridor_ys))
            
            return {
                'rooms': frontend_rooms,
                'corridors': frontend_corridors,
                'width': max(800, max_x - min_x + 100),
                'height': max(600, max_y - min_y + 100)
            }
            
        except Exception as e:
            logger.error(f"Error extracting visualization data: {e}")
            return self._create_default_visualization_data()
    
    def _create_default_visualization_data(self) -> Dict[str, Any]:
        """创建默认的可视化数据"""
        return {
            'rooms': [
                {
                    'id': 'entrance',
                    'x': 100,
                    'y': 100,
                    'width': 80,
                    'height': 60,
                    'type': 'room',
                    'connections': ['corridor1']
                },
                {
                    'id': 'chamber1',
                    'x': 300,
                    'y': 80,
                    'width': 100,
                    'height': 80,
                    'type': 'chamber',
                    'connections': ['corridor1', 'corridor2']
                }
            ],
            'corridors': [
                {
                    'id': 'corridor1',
                    'start': {'x': 180, 'y': 130},
                    'end': {'x': 300, 'y': 120},
                    'width': 8
                }
            ],
            'width': 800,
            'height': 600
        }

# ====== 便捷入口函数 ======
def visualize_dungeon(dungeon_data: Dict[str, Any], output_path: str, 
                     figsize: Tuple[int, int] = (12, 8), dpi: int = 100,
                     show_connections: bool = True, show_room_ids: bool = True,
                     show_grid: bool = True, show_game_elements: bool = True) -> bool:
    visualizer = DungeonVisualizer(figsize=figsize, dpi=dpi)
    return visualizer.visualize_dungeon(
        dungeon_data, output_path, show_connections, show_room_ids, show_grid, show_game_elements
    )
