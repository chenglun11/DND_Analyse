#!/usr/bin/env python3
"""
A*算法可视化器
用于可视化地牢的智能路径搜索和可达性分析
支持实时显示A*搜索过程和最优路径计算
"""

import matplotlib
matplotlib.use('TkAgg')  # 使用TkAgg后端支持交互式窗口
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Polygon, FancyBboxPatch, Circle
import matplotlib.patheffects as PathEffects
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set
import json
import os
from pathlib import Path
import logging
from collections import deque
import heapq
import time
import threading
from queue import Queue
import tkinter as tk
from tkinter import simpledialog

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

logger = logging.getLogger(__name__)

class AStarVisualizer:
    """A*算法可视化器"""
    
    def __init__(self, figsize: Tuple[int, int] = (16, 10), dpi: int = 100):
        self.figsize = figsize
        self.dpi = dpi
        self.colors = {
            'room': '#E3F2FD',           # 房间
            'room_border': '#1976D2',     # 房间边框
            'corridor': '#F3E5F5',        # 走廊
            'corridor_border': '#7B1FA2', # 走廊边框
            'connection': '#FF5722',      # 连接线
            'unvisited': '#E0E0E0',       # 未访问节点
            'visited': '#4CAF50',         # 已访问节点
            'current': '#FF9800',         # 当前节点
            'open_set': '#2196F3',        # 开放集合中的节点
            'path': '#F44336',            # 路径
            'start': '#4CAF50',           # 起始节点
            'end': '#F44336',             # 目标节点
            'background': '#FAFAFA',      # 背景
            'text': '#212121'             # 文字
        }
        
        self.fig = None
        self.ax = None
        self.dungeon_data = None
        self.graph = None
        self.node_positions = {}
        self.animation_running = False
        self.animation_speed = 0.3  # 动画速度（秒）
        
    def setup_visualization(self, dungeon_data: Dict[str, Any]) -> bool:
        """设置可视化环境"""
        try:
            self.dungeon_data = dungeon_data
            self.graph = self._build_graph(dungeon_data)
            self.node_positions = self._calculate_node_positions(dungeon_data)
            
            # 创建图形和轴
            self.fig, self.ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
            self.ax.set_facecolor(self.colors['background'])
            
            # 设置边界
            bounds = self._calculate_bounds(dungeon_data)
            if bounds:
                margin_ratio = 0.1
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
                
                x_pad = width * margin_ratio
                y_pad = height * margin_ratio
                self.ax.set_xlim(x_min - x_pad, x_max + x_pad)
                self.ax.set_ylim(y_min - y_pad, y_max + y_pad)
                self.ax.set_aspect('equal', adjustable='datalim')
            
            return True
        except Exception as e:
            logger.error(f"Error setting up visualization: {e}")
            return False
    
    def _build_graph(self, dungeon_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """构建图结构"""
        graph = {}
        
        # 尝试不同的数据格式
        levels = dungeon_data.get('levels', [])
        if levels:
            # 统一格式
            level = levels[0]
            rooms = level.get('rooms', [])
            corridors = level.get('corridors', [])
            connections = level.get('connections', [])
            
            all_nodes = rooms + corridors
            for node in all_nodes:
                graph[node['id']] = []
                
            for conn in connections:
                if conn['from_room'] in graph and conn['to_room'] in graph:
                    graph[conn['from_room']].append(conn['to_room'])
                    graph[conn['to_room']].append(conn['from_room'])
        
        elif 'plan_graph' in dungeon_data:
            # FiMap Elites格式
            plan_graph = dungeon_data.get('plan_graph', {})
            graph_data = plan_graph.get('graph', {})
            weight_data = graph_data.get('weight_per_neighbor_per_vertex', {})
            
            for vertex, neighbors in weight_data.items():
                if vertex not in graph:
                    graph[vertex] = []
                for neighbor in neighbors.keys():
                    if neighbor not in graph:
                        graph[neighbor] = []
                    graph[vertex].append(neighbor)
                    graph[neighbor].append(vertex)
        
        return graph
    
    def _calculate_node_positions(self, dungeon_data: Dict[str, Any]) -> Dict[str, Tuple[float, float]]:
        """计算节点位置"""
        positions = {}
        
        # 尝试不同的数据格式
        levels = dungeon_data.get('levels', [])
        if levels:
            # 统一格式
            level = levels[0]
            rooms = level.get('rooms', [])
            corridors = level.get('corridors', [])
            
            all_nodes = rooms + corridors
            for node in all_nodes:
                if 'position' in node and 'size' in node:
                    x = node['position'].get('x', 0)
                    y = node['position'].get('y', 0)
                    w = node['size'].get('width', 1)
                    h = node['size'].get('height', 1)
                    positions[node['id']] = (x + w/2, y + h/2)
                else:
                    x = node.get('x', 0)
                    y = node.get('y', 0)
                    positions[node['id']] = (x, y)
        
        elif 'plan_graph' in dungeon_data:
            # FiMap Elites格式 - 使用简单的网格布局
            plan_graph = dungeon_data.get('plan_graph', {})
            graph_data = plan_graph.get('graph', {})
            weight_data = graph_data.get('weight_per_neighbor_per_vertex', {})
            
            # 为每个节点分配网格位置
            nodes = list(weight_data.keys())
            grid_size = int(len(nodes) ** 0.5) + 1
            
            for i, node_id in enumerate(nodes):
                row = i // grid_size
                col = i % grid_size
                positions[node_id] = (col * 2, row * 2)
                
        return positions
    
    def _calculate_bounds(self, dungeon_data: Dict[str, Any]) -> Optional[Dict[str, float]]:
        """计算地牢边界"""
        x_coords, y_coords = [], []
        
        # 尝试不同的数据格式
        levels = dungeon_data.get('levels', [])
        if levels:
            # 统一格式
            for level in levels:
                rooms = level.get('rooms', [])
                corridors = level.get('corridors', [])
                
                for room in rooms + corridors:
                    if 'position' in room:
                        x = room['position'].get('x', 0)
                        y = room['position'].get('y', 0)
                    else:
                        x = room.get('x', 0)
                        y = room.get('y', 0)
                    x_coords.append(x)
                    y_coords.append(y)
        
        if x_coords and y_coords:
            return {
                'x_min': min(x_coords),
                'x_max': max(x_coords),
                'y_min': min(y_coords),
                'y_max': max(y_coords)
            }
        return None
    
    def _heuristic(self, node1: str, node2: str) -> float:
        """启发式函数：计算两个节点间的欧几里得距离"""
        pos1 = self.node_positions.get(node1)
        pos2 = self.node_positions.get(node2)
        
        if pos1 and pos2:
            return np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
        return 0.0
    
    def _get_edge_cost(self, node1: str, node2: str) -> float:
        """获取边的代价（这里使用欧几里得距离）"""
        return self._heuristic(node1, node2)
    
    def draw_dungeon_base(self):
        """绘制地牢基础结构（与BFS一致）"""
        if not self.dungeon_data:
            return
        
        levels = self.dungeon_data.get('levels', [])
        if levels:
            # 统一格式
            level = levels[0]
            rooms = level.get('rooms', [])
            corridors = level.get('corridors', [])
            connections = level.get('connections', [])
            
            # 绘制房间
            for room in rooms:
                self._draw_node(room, self.colors['room'], self.colors['room_border'], 'room')
            
            # 绘制走廊
            for corridor in corridors:
                self._draw_node(corridor, self.colors['corridor'], self.colors['corridor_border'], 'corridor')
            
            # 绘制连接
            for conn in connections:
                self._draw_connection(conn)
        
        elif 'plan_graph' in self.dungeon_data:
            # FiMap Elites格式 - 绘制简单的节点
            plan_graph = self.dungeon_data.get('plan_graph', {})
            graph_data = plan_graph.get('graph', {})
            weight_data = graph_data.get('weight_per_neighbor_per_vertex', {})
            
            for node_id in weight_data.keys():
                pos = self.node_positions.get(node_id)
                if pos:
                    # 绘制简单的圆形节点
                    circle = Circle(pos, 0.5, color=self.colors['room'], 
                                  edgecolor=self.colors['room_border'], linewidth=2, alpha=0.8)
                    self.ax.add_patch(circle)
                    
                    # 添加标签
                    self.ax.text(pos[0], pos[1], node_id, 
                                ha='center', va='center', fontsize=8, 
                                color=self.colors['text'],
                                bbox=dict(boxstyle="round,pad=0.1", facecolor='white', alpha=0.8))
            
            # 绘制连接
            for node_id, neighbors in weight_data.items():
                from_pos = self.node_positions.get(node_id)
                if from_pos:
                    for neighbor_id in neighbors.keys():
                        to_pos = self.node_positions.get(neighbor_id)
                        if to_pos:
                            self.ax.plot([from_pos[0], to_pos[0]], [from_pos[1], to_pos[1]], 
                                        color=self.colors['connection'], linewidth=1, alpha=0.6)

    def _draw_node(self, node: Dict[str, Any], face_color: str, border_color: str, node_type: str):
        """绘制节点（与BFS一致，支持FancyBboxPatch）"""
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
        
        # 绘制矩形
        rect = FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.1",
            facecolor=face_color,
            edgecolor=border_color,
            linewidth=2,
            alpha=0.8
        )
        self.ax.add_patch(rect)
        
        # 添加标签
        node_id = node.get('id', '')
        self.ax.text(x + w/2, y + h/2, node_id, 
                    ha='center', va='center', fontsize=10, 
                    color=self.colors['text'],
                    bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))

    def _draw_connection(self, connection: Dict[str, Any]):
        """绘制连接（与BFS一致）"""
        from_pos = self.node_positions.get(connection['from_room'])
        to_pos = self.node_positions.get(connection['to_room'])
        
        if from_pos and to_pos:
            self.ax.plot([from_pos[0], to_pos[0]], [from_pos[1], to_pos[1]], 
                        color=self.colors['connection'], linewidth=2, alpha=0.6)
    
    def visualize_astar(self, start_node: str, target_node: Optional[str] = None):
        """可视化A*算法"""
        if not self.graph or start_node not in self.graph:
            logger.error(f"Invalid start node: {start_node}")
            return
            
        # 清除之前的可视化
        self.ax.clear()
        self.ax.set_facecolor(self.colors['background'])
        
        # 重新绘制基础结构
        self.draw_dungeon_base()
        
        # 标记起始节点
        self._highlight_node(start_node, self.colors['start'], 'START')
        
        if target_node:
            # 标记目标节点
            self._highlight_node(target_node, self.colors['end'], 'GOAL')
        
        # 执行A*算法并可视化
        path, visited, open_set_history = self._astar_search(start_node, target_node)
        
        # 显示统计信息
        self._show_astar_stats(visited, path, target_node)
        
        title = f'A*搜索: 从 {start_node} 开始'
        if target_node:
            title += f' 到 {target_node}'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.show()
    
    def _astar_search(self, start: str, goal: Optional[str] = None) -> Tuple[List[str], Set[str], List[Set[str]]]:
        """A*搜索算法"""
        if goal and goal not in self.graph:
            return [], set(), []
        
        # 初始化
        open_set = [(0, start)]  # (f_score, node)
        came_from = {}
        g_score = {start: 0}  # 从起点到当前节点的实际代价
        f_score = {start: 0}  # g_score + 启发式
        
        visited = set()
        open_set_history = []
        
        while open_set:
            current_f, current = heapq.heappop(open_set)
            
            if current in visited:
                continue
                
            visited.add(current)
            
            # 高亮当前节点
            if goal and current == goal:
                self._highlight_node(current, '#FFD600', 'GOAL', size=0.6, bold=True)
            else:
                self._highlight_node(current, self.colors['current'], f'F={current_f:.1f}')
            
            # 更新显示
            plt.pause(self.animation_speed)
            
            # 如果找到目标，重建路径
            if goal and current == goal:
                path = self._reconstruct_path(came_from, start, goal)
                self._highlight_path(path)
                break
            
            # 处理邻居节点
            for neighbor in self.graph[current]:
                if neighbor in visited:
                    continue
                
                # 计算从起点经过当前节点到邻居的代价
                tentative_g_score = g_score[current] + self._get_edge_cost(current, neighbor)
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    # 这是一条更好的路径
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    
                    if goal:
                        f_score[neighbor] = g_score[neighbor] + self._heuristic(neighbor, goal)
                    else:
                        f_score[neighbor] = g_score[neighbor]
                    
                    # 添加到开放集合
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
                    
                    # 高亮开放集合中的节点
                    self._highlight_node(neighbor, self.colors['open_set'], f'F={f_score[neighbor]:.1f}')
            
            # 将当前节点标记为已访问
            if goal and current != goal:
                self._highlight_node(current, self.colors['visited'], f'V({g_score[current]:.1f})')
            
            # 更新显示
            plt.pause(self.animation_speed)
        
        # 如果没有目标节点，返回访问过的所有节点
        if not goal:
            return [], visited, []
        
        # 重建路径
        if goal in came_from:
            path = self._reconstruct_path(came_from, start, goal)
        else:
            path = []
        
        return path, visited, open_set_history
    
    def _highlight_node(self, node_id: str, color: str, label: str, size: float = 0.3, bold: bool = False):
        """高亮节点，支持自定义大小和加粗"""
        pos = self.node_positions.get(node_id)
        if pos:
            circle = Circle(pos, size, color=color, alpha=0.85 if bold else 0.7, zorder=15 if bold else 10)
            self.ax.add_patch(circle)
            
            # 添加标签
            fontweight = 'bold' if bold else 'normal'
            self.ax.text(pos[0], pos[1] + size + 0.1, label, 
                        ha='center', va='center', fontsize=10 if bold else 8, 
                        color=self.colors['text'], fontweight=fontweight,
                        bbox=dict(boxstyle="round,pad=0.1", facecolor='white', alpha=0.95 if bold else 0.9))
    
    def _highlight_path(self, path: List[str]):
        """高亮路径"""
        for i in range(len(path) - 1):
            from_pos = self.node_positions.get(path[i])
            to_pos = self.node_positions.get(path[i + 1])
            
            if from_pos and to_pos:
                self.ax.plot([from_pos[0], to_pos[0]], [from_pos[1], to_pos[1]], 
                            color=self.colors['path'], linewidth=4, alpha=0.8, zorder=5)
    
    def _reconstruct_path(self, came_from: Dict[str, str], start: str, end: str) -> List[str]:
        """重建路径"""
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = came_from.get(current)
        path.reverse()
        return path
    
    def _show_astar_stats(self, visited: Set[str], path: List[str], target_node: Optional[str]):
        """显示A*统计信息"""
        total_nodes = len(self.graph)
        visited_count = len(visited)
        coverage = visited_count / total_nodes if total_nodes > 0 else 0
        
        stats_text = f'访问节点数: {visited_count}/{total_nodes} ({coverage:.1%})'
        if target_node and path:
            stats_text += f'\n路径长度: {len(path)} 步'
            if len(path) > 1:
                total_cost = sum(self._get_edge_cost(path[i], path[i+1]) for i in range(len(path)-1))
                stats_text += f'\n总代价: {total_cost:.2f}'
        elif target_node:
            stats_text += f'\n未找到路径到 {target_node}'
            
        self.ax.text(0.02, 0.98, stats_text, transform=self.ax.transAxes,
                    fontsize=10, verticalalignment='top',
                    bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.8))
    
    def visualize_accessibility_analysis(self):
        """可视化可达性分析（使用A*）"""
        if not self.graph:
            logger.error("No graph available")
            return
            
        # 计算每个节点的可达性
        accessibility_scores = {}
        for node in self.graph.keys():
            _, visited, _ = self._astar_search(node)
            accessibility = len(visited) / len(self.graph)
            accessibility_scores[node] = accessibility
        
        # 可视化可达性
        self.ax.clear()
        self.ax.set_facecolor(self.colors['background'])
        self.draw_dungeon_base()
        
        # 根据可达性着色
        for node_id, score in accessibility_scores.items():
            pos = self.node_positions.get(node_id)
            if pos:
                # 根据可达性选择颜色
                if score >= 0.8:
                    color = '#4CAF50'  # 绿色 - 高可达性
                elif score >= 0.6:
                    color = '#FF9800'  # 橙色 - 中等可达性
                else:
                    color = '#F44336'  # 红色 - 低可达性
                
                circle = Circle(pos, 0.4, color=color, alpha=0.6, zorder=10)
                self.ax.add_patch(circle)
                
                # 显示可达性分数
                self.ax.text(pos[0], pos[1] + 0.5, f'{score:.2f}', 
                            ha='center', va='center', fontsize=8, 
                            color=self.colors['text'],
                            bbox=dict(boxstyle="round,pad=0.1", facecolor='white', alpha=0.9))
        
        # 显示整体统计
        avg_accessibility = np.mean(list(accessibility_scores.values()))
        stats_text = f'平均可达性: {avg_accessibility:.3f}\n'
        stats_text += f'高可达性(≥0.8): {sum(1 for s in accessibility_scores.values() if s >= 0.8)}\n'
        stats_text += f'中等可达性(0.6-0.8): {sum(1 for s in accessibility_scores.values() if 0.6 <= s < 0.8)}\n'
        stats_text += f'低可达性(<0.6): {sum(1 for s in accessibility_scores.values() if s < 0.6)}'
        
        self.ax.text(0.02, 0.98, stats_text, transform=self.ax.transAxes,
                    fontsize=10, verticalalignment='top',
                    bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.8))
        
        plt.title('A*可达性分析', fontsize=14, fontweight='bold')
        plt.show()
    
    def create_interactive_window(self):
        """创建交互式窗口"""
        if not self.dungeon_data:
            logger.error("No dungeon data available")
            return
        
        # 创建主窗口
        self.fig, self.ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        self.ax.set_facecolor(self.colors['background'])
        
        # 设置边界
        bounds = self._calculate_bounds(self.dungeon_data)
        if bounds:
            margin_ratio = 0.1
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
            
            x_pad = width * margin_ratio
            y_pad = height * margin_ratio
            self.ax.set_xlim(x_min - x_pad, x_max + x_pad)
            self.ax.set_ylim(y_min - y_pad, y_max + y_pad)
            self.ax.set_aspect('equal', adjustable='datalim')
        
        # 绘制基础结构
        self.draw_dungeon_base()
        
        # 添加按钮
        from matplotlib.widgets import Button
        
        # 可达性分析按钮
        ax_btn1 = plt.axes([0.1, 0.05, 0.2, 0.04])
        btn1 = Button(ax_btn1, '可达性分析')
        btn1.on_clicked(lambda event: self.visualize_accessibility_analysis())
        
        # A*搜索按钮
        ax_btn2 = plt.axes([0.35, 0.05, 0.2, 0.04])
        btn2 = Button(ax_btn2, 'A*搜索')
        btn2.on_clicked(lambda event: self._start_astar_interactive())
        
        plt.title('地牢A*算法可视化器', fontsize=16, fontweight='bold')
        plt.show()
    
    def _start_astar_interactive(self):
        """启动交互式A*搜索（弹窗输入）"""
        if not self.graph:
            return
        
        # 获取Tk主窗口
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        
        # 弹窗输入起点
        start_node = simpledialog.askstring("输入起始节点", "请输入起始节点ID：", parent=root)
        if not start_node or start_node not in self.graph:
            print(f"无效的起始节点: {start_node}")
            return
        
        # 弹窗输入终点
        target_node = simpledialog.askstring("输入目标节点", "请输入目标节点ID（可选）：", parent=root)
        if target_node and target_node not in self.graph:
            print(f"无效的目标节点: {target_node}")
            return
        
        if not target_node:
            target_node = None
        
        self.visualize_astar(start_node, target_node)


def create_astar_visualizer(dungeon_data: Dict[str, Any]) -> AStarVisualizer:
    """创建A*可视化器实例"""
    visualizer = AStarVisualizer()
    if visualizer.setup_visualization(dungeon_data):
        return visualizer
    else:
        raise ValueError("Failed to setup A* visualizer")


def visualize_astar_from_file(input_path: str):
    """从文件创建A*可视化"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            dungeon_data = json.load(f)
        
        visualizer = create_astar_visualizer(dungeon_data)
        visualizer.create_interactive_window()
        
    except Exception as e:
        logger.error(f"Error loading dungeon data: {e}")
        raise 