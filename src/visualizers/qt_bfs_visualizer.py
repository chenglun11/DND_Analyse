#!/usr/bin/env python3
"""
Qt版本的BFS算法可视化器
用于可视化地牢的可达性分析和路径多样性分析
支持实时显示BFS遍历过程和路径计算
"""

import sys
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import deque
import time
import threading
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QSlider, QSpinBox, QTextEdit,
    QFileDialog, QMessageBox, QGroupBox, QGridLayout, QSplitter,
    QFrame, QProgressBar, QCheckBox
)
from PyQt5.QtCore import (
    Qt, QTimer, pyqtSignal, QThread, QPropertyAnimation, QEasingCurve,
    QRect, QPoint, QSize
)
from PyQt5.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QPixmap, QPainterPath,
    QLinearGradient, QRadialGradient
)

logger = logging.getLogger(__name__)

class DungeonCanvas(QWidget):
    """地牢绘制画布"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dungeon_data = None
        self.graph = {}
        self.node_positions = {}
        self.node_sizes = {}
        self.node_types = {}
        
        # 可视化状态
        self.visited_nodes = set()
        self.current_node = None
        self.queue_nodes = set()
        self.path_nodes = []
        self.start_node = None
        self.end_node = None
        
        # 颜色配置
        self.colors = {
            'room': QColor(227, 242, 253),           # 房间
            'room_border': QColor(25, 118, 210),     # 房间边框
            'corridor': QColor(243, 229, 245),       # 走廊
            'corridor_border': QColor(123, 31, 162), # 走廊边框
            'connection': QColor(255, 87, 34),       # 连接线
            'unvisited': QColor(224, 224, 224),      # 未访问节点
            'visited': QColor(76, 175, 80),          # 已访问节点
            'current': QColor(255, 152, 0),          # 当前节点
            'queue': QColor(33, 150, 243),           # 队列中的节点
            'path': QColor(244, 67, 54),             # 路径
            'start': QColor(76, 175, 80),            # 起始节点
            'end': QColor(244, 67, 54),              # 目标节点
            'background': QColor(250, 250, 250),     # 背景
            'text': QColor(33, 33, 33)               # 文字
        }
        
        # 缩放和平移
        self.scale_factor = 1.0
        self.pan_offset = QPoint(0, 0)
        self.last_pan_point = None
        
        # 设置画布属性
        self.setMinimumSize(600, 400)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        
    def load_dungeon_data(self, dungeon_data: Dict[str, Any]) -> bool:
        """加载地牢数据"""
        try:
            self.dungeon_data = dungeon_data
            self.graph = self._build_graph(dungeon_data)
            self.node_positions = self._calculate_node_positions(dungeon_data)
            self.node_sizes = self._calculate_node_sizes(dungeon_data)
            self.node_types = self._get_node_types(dungeon_data)
            
            # 重置可视化状态
            self.visited_nodes.clear()
            self.current_node = None
            self.queue_nodes.clear()
            self.path_nodes.clear()
            self.start_node = None
            self.end_node = None
            
            # 自动调整视图
            self._auto_fit_view()
            self.update()
            return True
        except Exception as e:
            logger.error(f"Error loading dungeon data: {e}")
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
    
    def _calculate_node_positions(self, dungeon_data: Dict[str, Any]) -> Dict[str, QPoint]:
        """计算节点位置（归一化到画布范围，避免重叠）"""
        positions = {}
        raw_positions = {}
        # 尝试不同的数据格式
        levels = dungeon_data.get('levels', [])
        if levels:
            level = levels[0]
            rooms = level.get('rooms', [])
            corridors = level.get('corridors', [])
            all_nodes = rooms + corridors
            for node in all_nodes:
                if 'position' in node and 'size' in node:
                    x = node['position'].get('x', 0)
                    y = node['position'].get('y', 0)
                else:
                    x = node.get('x', 0)
                    y = node.get('y', 0)
                raw_positions[node['id']] = (x, y)
        elif 'plan_graph' in dungeon_data:
            plan_graph = dungeon_data.get('plan_graph', {})
            graph_data = plan_graph.get('graph', {})
            weight_data = graph_data.get('weight_per_neighbor_per_vertex', {})
            nodes = list(weight_data.keys())
            grid_size = int(len(nodes) ** 0.5) + 1
            for i, node_id in enumerate(nodes):
                row = i // grid_size
                col = i % grid_size
                raw_positions[node_id] = (col, row)
        # 归一化到画布范围
        if not raw_positions:
            return positions
        xs = [p[0] for p in raw_positions.values()]
        ys = [p[1] for p in raw_positions.values()]
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        # 防止除零
        x_span = x_max - x_min if x_max > x_min else 1
        y_span = y_max - y_min if y_max > y_min else 1
        margin = 60
        canvas_width = max(self.width(), 600)
        canvas_height = max(self.height(), 400)
        for node_id, (x, y) in raw_positions.items():
            norm_x = (x - x_min) / x_span
            norm_y = (y - y_min) / y_span
            canvas_x = margin + norm_x * (canvas_width - 2 * margin)
            canvas_y = margin + norm_y * (canvas_height - 2 * margin)
            positions[node_id] = QPoint(int(canvas_x), int(canvas_y))
        return positions
    
    def _calculate_node_sizes(self, dungeon_data: Dict[str, Any]) -> Dict[str, QSize]:
        """节点大小自适应，节点多时变小，少时变大"""
        sizes = {}
        levels = dungeon_data.get('levels', [])
        node_count = 0
        if levels:
            level = levels[0]
            rooms = level.get('rooms', [])
            corridors = level.get('corridors', [])
            all_nodes = rooms + corridors
            node_count = len(all_nodes)
            for node in all_nodes:
                sizes[node['id']] = QSize( max(12, 40 - node_count//10), max(12, 40 - node_count//10) )
        elif 'plan_graph' in dungeon_data:
            plan_graph = dungeon_data.get('plan_graph', {})
            graph_data = plan_graph.get('graph', {})
            weight_data = graph_data.get('weight_per_neighbor_per_vertex', {})
            node_count = len(weight_data)
            for node_id in weight_data.keys():
                sizes[node_id] = QSize( max(12, 40 - node_count//10), max(12, 40 - node_count//10) )
        return sizes
    
    def _get_node_types(self, dungeon_data: Dict[str, Any]) -> Dict[str, str]:
        """获取节点类型"""
        types = {}
        
        levels = dungeon_data.get('levels', [])
        if levels:
            level = levels[0]
            rooms = level.get('rooms', [])
            corridors = level.get('corridors', [])
            
            for room in rooms:
                types[room['id']] = 'room'
            for corridor in corridors:
                types[corridor['id']] = 'corridor'
        
        elif 'plan_graph' in dungeon_data:
            # FiMap Elites格式 - 默认为房间
            plan_graph = dungeon_data.get('plan_graph', {})
            graph_data = plan_graph.get('graph', {})
            weight_data = graph_data.get('weight_per_neighbor_per_vertex', {})
            
            for node_id in weight_data.keys():
                types[node_id] = 'room'
                
        return types
    
    def _auto_fit_view(self):
        """自动调整视图以适应所有节点"""
        if not self.node_positions:
            return
            
        points = list(self.node_positions.values())
        if not points:
            return
            
        x_coords = [p.x() for p in points]
        y_coords = [p.y() for p in points]
        
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        
        # 添加边距
        margin = 50
        x_min -= margin
        x_max += margin
        y_min -= margin
        y_max += margin
        
        # 计算合适的缩放因子
        canvas_width = self.width()
        canvas_height = self.height()
        
        if canvas_width > 0 and canvas_height > 0:
            scale_x = canvas_width / (x_max - x_min) if x_max > x_min else 1
            scale_y = canvas_height / (y_max - y_min) if y_max > y_min else 1
            self.scale_factor = min(scale_x, scale_y) * 0.8  # 留一些边距
            
            # 计算平移偏移
            center_x = (x_min + x_max) / 2
            center_y = (y_min + y_max) / 2
            canvas_center_x = canvas_width / 2
            canvas_center_y = canvas_height / 2
            
            self.pan_offset = QPoint(
                int(canvas_center_x - center_x * self.scale_factor),
                int(canvas_center_y - center_y * self.scale_factor)
            )
    
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        
        # 绘制背景
        painter.fillRect(self.rect(), self.colors['background'])
        
        if not self.dungeon_data:
            # 绘制提示信息
            painter.setPen(self.colors['text'])
            painter.setFont(QFont('Arial', 14))
            painter.drawText(self.rect(), Qt.AlignCenter, "请加载地牢数据")
            return
        
        # 应用变换
        painter.translate(self.pan_offset)
        painter.scale(self.scale_factor, self.scale_factor)
        
        # 绘制连接线
        self._draw_connections(painter)
        
        # 绘制节点
        self._draw_nodes(painter)
        
        # 绘制节点标签
        self._draw_node_labels(painter)
    
    def _draw_connections(self, painter: QPainter):
        """绘制连接线"""
        if not self.dungeon_data:
            return
            
        levels = self.dungeon_data.get('levels', [])
        if levels:
            level = levels[0]
            connections = level.get('connections', [])
            
            pen = QPen(self.colors['connection'])
            pen.setWidth(2)
            painter.setPen(pen)
            
            for conn in connections:
                from_id = conn['from_room']
                to_id = conn['to_room']
                
                if from_id in self.node_positions and to_id in self.node_positions:
                    from_pos = self.node_positions[from_id]
                    to_pos = self.node_positions[to_id]
                    painter.drawLine(from_pos, to_pos)
    
    def _draw_nodes(self, painter: QPainter):
        """绘制节点"""
        for node_id, pos in self.node_positions.items():
            # 确定节点颜色
            color = self._get_node_color(node_id)
            
            # 确定节点大小
            size = self.node_sizes.get(node_id, QSize(20, 20))
            node_type = self.node_types.get(node_id, 'room')
            
            # 绘制节点
            if node_type == 'room':
                self._draw_room(painter, pos, size, color)
            else:
                self._draw_corridor(painter, pos, size, color)
    
    def _get_node_color(self, node_id: str) -> QColor:
        """获取节点颜色"""
        if node_id == self.start_node:
            return self.colors['start']
        elif node_id == self.end_node:
            return self.colors['end']
        elif node_id == self.current_node:
            return self.colors['current']
        elif node_id in self.path_nodes:
            return self.colors['path']
        elif node_id in self.visited_nodes:
            return self.colors['visited']
        elif node_id in self.queue_nodes:
            return self.colors['queue']
        else:
            return self.colors['unvisited']
    
    def _draw_room(self, painter: QPainter, pos: QPoint, size: QSize, color: QColor):
        """绘制房间"""
        rect = QRect(pos.x() - size.width()//2, pos.y() - size.height()//2, 
                    size.width(), size.height())
        
        # 绘制填充
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(self.colors['room_border'], 2))
        painter.drawRect(rect)
    
    def _draw_corridor(self, painter: QPainter, pos: QPoint, size: QSize, color: QColor):
        """绘制走廊"""
        rect = QRect(pos.x() - size.width()//2, pos.y() - size.height()//2, 
                    size.width(), size.height())
        
        # 绘制填充
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(self.colors['corridor_border'], 2))
        painter.drawEllipse(rect)
    
    def _draw_node_labels(self, painter: QPainter):
        """所有节点仅在节点中心绘制数字（无rect背景），关键节点高亮，数字居中"""
        for node_id, pos in self.node_positions.items():
            size = self.node_sizes.get(node_id, QSize(20, 20))
            label = node_id[-3:] if len(node_id) > 3 else node_id
            font_size = max(8, min(size.width(), size.height()) // 2)
            font = QFont('Arial', font_size)
            if node_id == self.start_node:
                font.setBold(True)
                painter.setPen(self.colors['start'])
            elif node_id == self.end_node:
                font.setBold(True)
                painter.setPen(self.colors['end'])
            elif node_id == self.current_node:
                font.setBold(True)
                painter.setPen(self.colors['current'])
            else:
                font.setBold(False)
                painter.setPen(self.colors['text'])
            painter.setFont(font)
            # 用QRect居中显示数字，无rect背景
            rect = QRect(pos.x() - size.width()//2, pos.y() - size.height()//2, size.width(), size.height())
            painter.drawText(rect, Qt.AlignCenter, label)
    
    def set_visualization_state(self, visited: Set[str], current: Optional[str], 
                               queue: Set[str], path: List[str], 
                               start: Optional[str], end: Optional[str]):
        """设置可视化状态"""
        self.visited_nodes = visited.copy()
        self.current_node = current
        self.queue_nodes = queue.copy()
        self.path_nodes = path.copy()
        self.start_node = start
        self.end_node = end
        self.update()
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.last_pan_point = event.pos()
        event.accept()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if event.buttons() & Qt.LeftButton and self.last_pan_point:
            delta = event.pos() - self.last_pan_point
            self.pan_offset += delta
            self.last_pan_point = event.pos()
            self.update()
        event.accept()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.last_pan_point = None
        event.accept()
    
    def wheelEvent(self, event):
        """鼠标滚轮事件 - 缩放"""
        delta = event.angleDelta().y()
        scale_factor = 1.1 if delta > 0 else 0.9
        
        # 以鼠标位置为中心进行缩放
        mouse_pos = event.pos()
        old_scale = self.scale_factor
        self.scale_factor *= scale_factor
        self.scale_factor = max(0.1, min(5.0, self.scale_factor))  # 限制缩放范围
        
        # 调整平移偏移以保持鼠标位置不变
        scale_ratio = self.scale_factor / old_scale
        self.pan_offset = mouse_pos - (mouse_pos - self.pan_offset) * scale_ratio
        
        self.update()
        event.accept()


class BFSWorker(QThread):
    """BFS算法工作线程"""
    
    # 信号定义
    state_updated = pyqtSignal(set, str, set, list, str, str)  # visited, current, queue, path, start, end
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, graph: Dict[str, List[str]], start_node: str, target_node: Optional[str] = None):
        super().__init__()
        self.graph = graph
        self.start_node = start_node
        self.target_node = target_node
        self.delay_ms = 500  # 动画延迟
    
    def set_delay(self, delay_ms: int):
        """设置动画延迟"""
        self.delay_ms = delay_ms
    
    def run(self):
        """运行BFS算法"""
        try:
            if self.start_node not in self.graph:
                self.error.emit(f"起始节点 {self.start_node} 不存在")
                return
            
            if self.target_node and self.target_node not in self.graph:
                self.error.emit(f"目标节点 {self.target_node} 不存在")
                return
            
            # BFS算法
            visited = set()
            queue = deque([(self.start_node, [self.start_node])])
            parent = {}
            
            while queue:
                current, path = queue.popleft()
                
                if current in visited:
                    continue
                
                visited.add(current)
                
                # 发送状态更新
                current_queue = {node for node, _ in queue}
                self.state_updated.emit(
                    visited.copy(), current, current_queue, 
                    path, self.start_node, self.target_node
                )
                
                # 如果找到目标节点
                if self.target_node and current == self.target_node:
                    break
                
                # 添加邻居节点
                for neighbor in self.graph[current]:
                    if neighbor not in visited:
                        parent[neighbor] = current
                        new_path = path + [neighbor]
                        queue.append((neighbor, new_path))
                
                # 延迟
                self.msleep(self.delay_ms)
            
            self.finished.emit()
            
        except Exception as e:
            self.error.emit(str(e))


class QtBFSVisualizer(QMainWindow):
    """Qt BFS可视化器主窗口"""
    
    def __init__(self):
        super().__init__()
        self.graph = {}
        self.dungeon_data = None  # 添加dungeon_data属性
        self.bfs_worker = None
        
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("地牢BFS可视化器")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧控制面板
        control_panel = self.create_control_panel()
        splitter.addWidget(control_panel)
        
        # 右侧画布
        self.canvas = DungeonCanvas()
        splitter.addWidget(self.canvas)
        
        # 设置分割器比例
        splitter.setSizes([300, 900])
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建状态栏
        self.statusBar().showMessage("就绪")
        
    def create_control_panel(self) -> QWidget:
        """创建控制面板"""
        panel = QWidget()
        panel.setMaximumWidth(300)
        layout = QVBoxLayout(panel)
        
        # 文件加载组
        file_group = QGroupBox("文件操作")
        file_layout = QVBoxLayout(file_group)
        
        load_btn = QPushButton("加载地牢数据")
        load_btn.clicked.connect(self.load_dungeon_file)
        file_layout.addWidget(load_btn)
        
        layout.addWidget(file_group)
        
        # BFS控制组
        bfs_group = QGroupBox("BFS控制")
        bfs_layout = QGridLayout(bfs_group)
        
        # 起始节点选择
        bfs_layout.addWidget(QLabel("起始节点:"), 0, 0)
        self.start_node_combo = QComboBox()
        self.start_node_combo.setEditable(True)
        bfs_layout.addWidget(self.start_node_combo, 0, 1)
        
        # 目标节点选择
        bfs_layout.addWidget(QLabel("目标节点:"), 1, 0)
        self.target_node_combo = QComboBox()
        self.target_node_combo.setEditable(True)
        self.target_node_combo.addItem("无")
        bfs_layout.addWidget(self.target_node_combo, 1, 1)
        
        # 动画速度
        bfs_layout.addWidget(QLabel("动画速度:"), 2, 0)
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(100, 2000)
        self.speed_slider.setValue(500)
        self.speed_slider.setTickPosition(QSlider.TicksBelow)
        self.speed_slider.setTickInterval(500)
        bfs_layout.addWidget(self.speed_slider, 2, 1)
        
        self.speed_label = QLabel("500ms")
        self.speed_slider.valueChanged.connect(
            lambda v: self.speed_label.setText(f"{v}ms")
        )
        bfs_layout.addWidget(self.speed_label, 2, 2)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("开始BFS")
        self.start_btn.clicked.connect(self.start_bfs)
        self.start_btn.setEnabled(False)
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("停止")
        self.stop_btn.clicked.connect(self.stop_bfs)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        self.reset_btn = QPushButton("重置")
        self.reset_btn.clicked.connect(self.reset_visualization)
        button_layout.addWidget(self.reset_btn)
        
        bfs_layout.addLayout(button_layout, 3, 0, 1, 3)
        
        layout.addWidget(bfs_group)
        
        # 分析组
        analysis_group = QGroupBox("分析功能")
        analysis_layout = QVBoxLayout(analysis_group)
        
        accessibility_btn = QPushButton("可达性分析")
        accessibility_btn.clicked.connect(self.analyze_accessibility)
        analysis_layout.addWidget(accessibility_btn)
        
        path_diversity_btn = QPushButton("路径多样性分析")
        path_diversity_btn.clicked.connect(self.analyze_path_diversity)
        analysis_layout.addWidget(path_diversity_btn)
        
        # 添加查看特定路径详情的功能
        self.view_path_details_btn = QPushButton("查看路径详情")
        self.view_path_details_btn.clicked.connect(self.view_path_details)
        analysis_layout.addWidget(self.view_path_details_btn)
        
        analysis_group.setLayout(analysis_layout)
        layout.addWidget(analysis_group)
        
        # 信息显示组
        info_group = QGroupBox("信息显示")
        info_layout = QVBoxLayout(info_group)
        
        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(150)
        self.info_text.setReadOnly(True)
        info_layout.addWidget(self.info_text)
        
        layout.addWidget(info_group)
        
        # 添加弹性空间
        layout.addStretch()
        
        return panel
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        load_action = file_menu.addAction('打开')
        load_action.triggered.connect(self.load_dungeon_file)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction('退出')
        exit_action.triggered.connect(self.close)
        
        # 视图菜单
        view_menu = menubar.addMenu('视图')
        
        fit_view_action = view_menu.addAction('适应视图')
        fit_view_action.triggered.connect(self.canvas._auto_fit_view)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助')
        
        about_action = help_menu.addAction('关于')
        about_action.triggered.connect(self.show_about)
    
    def load_dungeon_file(self):
        """加载地牢文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择地牢文件", "", "JSON文件 (*.json);;所有文件 (*)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    dungeon_data = json.load(f)
                
                # 保存dungeon_data到实例变量
                self.dungeon_data = dungeon_data
                
                # 构建图结构
                self.graph = self.canvas._build_graph(dungeon_data)
                
                # 加载到画布
                if self.canvas.load_dungeon_data(dungeon_data):
                    self.update_node_combos()
                    self.start_btn.setEnabled(True)  # 启用BFS开始按钮
                    self.statusBar().showMessage(f"已加载文件: {Path(file_path).name}")
                else:
                    QMessageBox.warning(self, "错误", "无法加载地牢数据")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载文件失败: {e}")
    
    def update_node_combos(self):
        """更新节点选择下拉框"""
        self.start_node_combo.clear()
        self.target_node_combo.clear()
        self.target_node_combo.addItem("无")
        
        if self.graph:
            nodes = sorted(self.graph.keys())
            self.start_node_combo.addItems(nodes)
            self.target_node_combo.addItems(nodes)
    
    def start_bfs(self):
        """开始BFS算法"""
        start_node = self.start_node_combo.currentText()
        target_node = self.target_node_combo.currentText()
        
        if target_node == "无":
            target_node = None
        
        if not start_node:
            QMessageBox.warning(self, "警告", "请选择起始节点")
            return
        
        # 创建并启动BFS工作线程
        self.bfs_worker = BFSWorker(self.graph, start_node, target_node)
        self.bfs_worker.state_updated.connect(self.update_visualization)
        self.bfs_worker.finished.connect(self.bfs_finished)
        self.bfs_worker.error.connect(self.bfs_error)
        
        # 设置动画速度
        delay = self.speed_slider.value()
        self.bfs_worker.set_delay(delay)
        
        # 更新UI状态
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.statusBar().showMessage("BFS算法运行中...")
        
        # 启动线程
        self.bfs_worker.start()
    
    def stop_bfs(self):
        """停止BFS算法"""
        if self.bfs_worker and self.bfs_worker.isRunning():
            self.bfs_worker.terminate()
            self.bfs_worker.wait()
            self.bfs_finished()
    
    def bfs_finished(self):
        """BFS算法完成"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.statusBar().showMessage("BFS算法完成")
        # 显示最短路径
        start_node = self.start_node_combo.currentText()
        target_node = self.target_node_combo.currentText()
        if start_node and target_node and target_node != "无":
            path = self._find_shortest_path(start_node, target_node)
            if path:
                path_str = " → ".join(path)
                self.info_text.append(f"\n最短路径：\n{path_str}")
            else:
                self.info_text.append("\n未找到最短路径")
        else:
            self.info_text.append("\n未指定终点，未显示路径")
    
    def bfs_error(self, error_msg: str):
        """BFS算法错误"""
        QMessageBox.critical(self, "错误", f"BFS算法错误: {error_msg}")
        self.bfs_finished()
    
    def update_visualization(self, visited: Set[str], current: str, 
                           queue: Set[str], path: List[str], 
                           start: str, end: str):
        """更新可视化状态"""
        self.canvas.set_visualization_state(visited, current, queue, path, start, end)
        
        # 更新信息显示
        info = f"当前节点: {current}\n"
        info += f"已访问: {len(visited)} 个节点\n"
        info += f"队列中: {len(queue)} 个节点\n"
        info += f"路径长度: {len(path)}"
        
        self.info_text.setText(info)
    
    def reset_visualization(self):
        """重置可视化"""
        self.canvas.set_visualization_state(set(), None, set(), [], None, None)
        self.info_text.clear()
        self.statusBar().showMessage("可视化已重置")
    
    def analyze_accessibility(self):
        """分析可达性"""
        if not self.graph:
            QMessageBox.warning(self, "警告", "请先加载地牢数据")
            return
        
        # 简单的可达性分析
        all_nodes = set(self.graph.keys())
        reachable_from_start = set()
        
        if self.start_node_combo.currentText():
            start_node = self.start_node_combo.currentText()
            # 使用BFS计算可达节点
            visited = set()
            queue = deque([start_node])
            
            while queue:
                current = queue.popleft()
                if current in visited:
                    continue
                visited.add(current)
                reachable_from_start.add(current)
                
                for neighbor in self.graph[current]:
                    if neighbor not in visited:
                        queue.append(neighbor)
            
            unreachable = all_nodes - reachable_from_start
            
            info = f"可达性分析结果:\n"
            info += f"总节点数: {len(all_nodes)}\n"
            info += f"可达节点数: {len(reachable_from_start)}\n"
            info += f"不可达节点数: {len(unreachable)}\n"
            info += f"可达性比例: {len(reachable_from_start)/len(all_nodes)*100:.1f}%\n"
            
            if unreachable:
                info += f"不可达节点: {', '.join(sorted(unreachable))}"
            
            self.info_text.setText(info)
        else:
            QMessageBox.warning(self, "警告", "请选择起始节点")
    
    def analyze_path_diversity(self):
        """分析路径多样性"""
        if not self.graph:
            QMessageBox.warning(self, "警告", "请先加载地牢数据")
            return
        
        # 获取所有房间节点
        room_nodes = []
        if self.dungeon_data and 'levels' in self.dungeon_data:
            level = self.dungeon_data['levels'][0]
            rooms = level.get('rooms', [])
            room_nodes = [room['id'] for room in rooms]
        
        if not room_nodes:
            QMessageBox.warning(self, "警告", "未找到房间数据")
            return
        
        # 分析所有房间对之间的路径
        path_counts = []
        path_distribution = {}  # 统计路径数量分布
        
        for i in range(len(room_nodes)):
            for j in range(i+1, len(room_nodes)):
                room1, room2 = room_nodes[i], room_nodes[j]
                count, _ = self._find_all_shortest_paths(room1, room2)
                if count > 0:
                    path_counts.append(count)
                    # 统计路径数量分布
                    if count not in path_distribution:
                        path_distribution[count] = []
                    path_distribution[count].append(f"{room1}->{room2}")
        
        if not path_counts:
            self.info_text.setText("路径多样性分析:\n没有找到可达的房间对")
            return
        
        # 计算统计信息
        avg_paths = sum(path_counts) / len(path_counts)
        max_paths = max(path_counts)
        min_paths = min(path_counts)
        
        # 生成简洁的报告
        info = f"路径多样性分析报告:\n"
        info += f"分析房间对数量: {len(path_counts)}\n"
        info += f"平均路径数: {avg_paths:.2f}\n"
        info += f"最大路径数: {max_paths}\n"
        info += f"最小路径数: {min_paths}\n\n"
        
        info += f"路径数量分布:\n"
        for count in sorted(path_distribution.keys()):
            room_pairs = path_distribution[count]
            info += f"  {count}条路径: {len(room_pairs)}对房间\n"
            # 只显示前3个房间对作为示例
            if len(room_pairs) <= 3:
                for pair in room_pairs:
                    info += f"    {pair}\n"
            else:
                for pair in room_pairs[:2]:
                    info += f"    {pair}\n"
                info += f"    ... 还有{len(room_pairs)-2}对\n"
        
        # 添加评分信息
        max_diversity = 5.0
        score = min(1.0, avg_paths / max_diversity)
        info += f"\n路径多样性评分: {score:.3f}"
        
        self.info_text.setText(info)

    def view_path_details(self):
        """查看特定房间对的路径详情"""
        if not self.graph:
            QMessageBox.warning(self, "警告", "请先加载地牢数据")
            return
        
        # 获取所有房间节点
        room_nodes = []
        if self.dungeon_data and 'levels' in self.dungeon_data:
            level = self.dungeon_data['levels'][0]
            rooms = level.get('rooms', [])
            room_nodes = [room['id'] for room in rooms]
        
        if not room_nodes:
            QMessageBox.warning(self, "警告", "未找到房间数据")
            return
        
        # 创建房间选择对话框
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QTextEdit
        
        dialog = QDialog(self)
        dialog.setWindowTitle("查看路径详情")
        dialog.setModal(True)
        dialog.resize(600, 400)
        
        layout = QVBoxLayout()
        
        # 房间选择
        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("起始房间:"))
        start_combo = QComboBox()
        start_combo.addItems(room_nodes)
        select_layout.addWidget(start_combo)
        
        select_layout.addWidget(QLabel("目标房间:"))
        end_combo = QComboBox()
        end_combo.addItems(room_nodes)
        select_layout.addWidget(end_combo)
        
        layout.addLayout(select_layout)
        
        # 查看按钮
        view_btn = QPushButton("查看路径")
        layout.addWidget(view_btn)
        
        # 结果显示
        result_text = QTextEdit()
        result_text.setReadOnly(True)
        layout.addWidget(result_text)
        
        def show_paths():
            start = start_combo.currentText()
            end = end_combo.currentText()
            
            if start == end:
                result_text.setText("起始房间和目标房间相同")
                return
            
            count, paths = self._find_all_shortest_paths(start, end)
            
            if count == 0:
                result_text.setText(f"从 {start} 到 {end} 没有可达路径")
                return
            
            info = f"从 {start} 到 {end} 的路径详情:\n"
            info += f"总路径数: {count}\n\n"
            
            for idx, path in enumerate(paths):
                path_str = " -> ".join(path)
                info += f"路径{idx+1}: {path_str}\n"
            
            result_text.setText(info)
        
        view_btn.clicked.connect(show_paths)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def _find_all_shortest_paths(self, start: str, end: str) -> Tuple[int, List[List[str]]]:
        """计算两个节点之间的所有最短路径"""
        if start == end:
            return 1, [[start]]
        
        # 使用BFS找到最短路径长度
        visited = set()
        queue = deque([(start, 0)])
        visited.add(start)
        shortest_length = None
        
        while queue:
            curr, length = queue.popleft()
            if curr == end:
                shortest_length = length
                break
            for nb in self.graph[curr]:
                if nb not in visited:
                    visited.add(nb)
                    queue.append((nb, length + 1))
        
        if shortest_length is None:
            return 0, []  # 不可达
        
        # 计算所有最短路径
        def find_paths_with_length(curr, target, remaining_length, visited, current_path):
            if remaining_length == 0:
                if curr == target:
                    return [current_path + [curr]]
                return []
            if remaining_length < 0:
                return []
            
            paths = []
            for nb in self.graph[curr]:
                if nb not in visited:
                    new_paths = find_paths_with_length(nb, target, remaining_length - 1, 
                                                     visited | {curr}, current_path + [curr])
                    paths.extend(new_paths)
            return paths
        
        all_paths = find_paths_with_length(start, end, shortest_length, set(), [])
        return len(all_paths), all_paths
    
    def _find_shortest_path(self, start: str, end: str):
        """BFS找最短路径，返回节点序列"""
        if start == end:
            return [start]
        visited = set()
        queue = deque([[start]])
        while queue:
            path = queue.popleft()
            node = path[-1]
            if node == end:
                return path
            if node not in visited:
                visited.add(node)
                for neighbor in self.graph.get(node, []):
                    if neighbor not in visited:
                        queue.append(path + [neighbor])
        return None
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于", 
                         "地牢BFS可视化器\n\n"
                         "基于Qt的BFS算法可视化工具\n"
                         "用于分析地牢的可达性和路径多样性")


def create_qt_bfs_visualizer() -> QtBFSVisualizer:
    """创建Qt BFS可视化器实例"""
    return QtBFSVisualizer()


def run_qt_bfs_visualizer():
    """运行Qt BFS可视化器"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("地牢BFS可视化器")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Dungeon Adapter")
    
    # 创建主窗口
    window = create_qt_bfs_visualizer()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_qt_bfs_visualizer()
