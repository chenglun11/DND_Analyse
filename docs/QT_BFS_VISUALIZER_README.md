# Qt BFS可视化器使用指南

## 概述

Qt BFS可视化器是一个基于PyQt5的图形界面工具，用于可视化地牢的BFS（广度优先搜索）算法执行过程。它提供了比matplotlib版本更好的交互性和用户体验。

## 主要特性

- **实时可视化**: 实时显示BFS算法的执行过程
- **交互式界面**: 支持鼠标缩放、平移等操作
- **多格式支持**: 支持多种地牢数据格式
- **分析功能**: 提供可达性分析和路径多样性分析
- **可调节速度**: 可以调节动画速度
- **状态显示**: 实时显示算法执行状态

## 安装依赖

```bash
pip install PyQt5
```

或者更新项目依赖：

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 直接运行

```bash
python demo_qt_bfs_visualizer.py
```

### 2. 在代码中使用

```python
from src.visualizers.qt_bfs_visualizer import run_qt_bfs_visualizer

# 运行Qt BFS可视化器
run_qt_bfs_visualizer()
```

### 3. 创建自定义实例

```python
from src.visualizers.qt_bfs_visualizer import QtBFSVisualizer
from PyQt5.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
visualizer = QtBFSVisualizer()
visualizer.show()
sys.exit(app.exec_())
```

## 界面说明

### 主窗口布局

- **左侧控制面板**: 包含文件操作、BFS控制、分析功能等信息显示
- **右侧画布**: 显示地牢结构和BFS执行过程

### 控制面板功能

#### 文件操作
- **加载地牢数据**: 选择并加载JSON格式的地牢数据文件

#### BFS控制
- **起始节点**: 选择BFS算法的起始节点
- **目标节点**: 选择BFS算法的目标节点（可选）
- **动画速度**: 调节BFS动画的执行速度（100-2000ms）
- **开始BFS**: 开始执行BFS算法
- **停止**: 停止当前执行的BFS算法
- **重置**: 重置可视化状态

#### 分析功能
- **可达性分析**: 分析从起始节点可达的所有节点
- **路径多样性分析**: 分析从起始节点到目标节点的路径多样性

#### 信息显示
- 显示当前算法执行状态
- 显示已访问节点数量
- 显示队列中的节点数量
- 显示当前路径长度

### 画布操作

- **鼠标左键拖拽**: 平移视图
- **鼠标滚轮**: 缩放视图
- **自动适应**: 通过菜单"视图 -> 适应视图"自动调整视图

## 支持的数据格式

### 1. 统一格式

```json
{
  "levels": [
    {
      "rooms": [
        {
          "id": "room1",
          "position": {"x": 100, "y": 100},
          "size": {"width": 50, "height": 50}
        }
      ],
      "corridors": [
        {
          "id": "corridor1", 
          "position": {"x": 200, "y": 200},
          "size": {"width": 30, "height": 30}
        }
      ],
      "connections": [
        {
          "from_room": "room1",
          "to_room": "corridor1"
        }
      ]
    }
  ]
}
```

### 2. FiMap Elites格式

```json
{
  "plan_graph": {
    "graph": {
      "weight_per_neighbor_per_vertex": {
        "vertex1": {"vertex2": 1.0},
        "vertex2": {"vertex1": 1.0}
      }
    }
  }
}
```

## 颜色说明

- **灰色**: 未访问的节点
- **绿色**: 已访问的节点
- **橙色**: 当前正在访问的节点
- **蓝色**: 队列中的节点
- **红色**: 路径上的节点
- **深绿色**: 起始节点
- **深红色**: 目标节点

## 与matplotlib版本的区别

| 特性 | Qt版本 | matplotlib版本 |
|------|--------|----------------|
| 交互性 | 支持鼠标缩放、平移 | 有限的交互性 |
| 实时更新 | 流畅的实时更新 | 动画更新 |
| 界面布局 | 现代化的GUI界面 | 简单的图形窗口 |
| 控制面板 | 集成控制面板 | 需要外部控制 |
| 性能 | 更好的性能 | 相对较慢 |
| 依赖 | PyQt5 | matplotlib + tkinter |

## 故障排除

### 1. PyQt5导入错误

```
ImportError: No module named 'PyQt5'
```

**解决方案**: 安装PyQt5
```bash
pip install PyQt5
```

### 2. 图形界面无法显示

**解决方案**: 
- 确保有图形界面支持
- 在服务器环境中使用X11转发
- 或者使用虚拟显示

### 3. 数据加载失败

**解决方案**:
- 检查JSON文件格式是否正确
- 确保文件编码为UTF-8
- 验证数据格式是否支持

### 4. 性能问题

**解决方案**:
- 减少动画速度
- 使用较小的地牢数据
- 关闭不必要的视觉效果

## 开发说明

### 主要类

- `QtBFSVisualizer`: 主窗口类
- `DungeonCanvas`: 地牢绘制画布
- `BFSWorker`: BFS算法工作线程

### 扩展功能

可以通过继承这些类来添加新功能：

```python
class CustomBFSVisualizer(QtBFSVisualizer):
    def __init__(self):
        super().__init__()
        # 添加自定义功能
        self.add_custom_features()
    
    def add_custom_features(self):
        # 实现自定义功能
        pass
```

## 许可证

本项目遵循与主项目相同的许可证。 