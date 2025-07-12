# BFS算法可视化器使用指南

## 概述

BFS算法可视化器是一个专门用于可视化地牢可达性和路径多样性分析的交互式工具。它可以帮助您：

- **实时观察BFS算法执行过程**：看到算法如何遍历地牢节点
- **分析可达性**：查看每个节点的可达性分数
- **评估路径多样性**：了解房间对之间的可选路径数量
- **支持交互式操作**：通过图形界面进行各种分析

## 功能特性

### 1. BFS遍历可视化
- 实时显示BFS算法的执行过程
- 用不同颜色标识节点状态：
  - 🟢 绿色：起始节点
  - 🟠 橙色：当前访问节点
  - 🔵 蓝色：队列中的节点
  - 🟢 绿色：已访问节点
  - 🔴 红色：目标节点和路径

### 2. 可达性分析
- 计算每个节点能够到达的其他节点比例
- 用颜色编码显示可达性：
  - 🟢 绿色：高可达性 (≥0.8)
  - 🟠 橙色：中等可达性 (0.6-0.8)
  - 🔴 红色：低可达性 (<0.6)
- 显示整体统计信息

### 3. 路径多样性分析
- 计算所有房间对之间的最短路径数量
- 高亮显示路径数量最多的房间对
- 显示平均路径多样性分数

### 4. 交互式窗口
- 提供图形按钮界面
- 支持多种分析模式
- 实时交互操作

## 安装要求

### 系统要求
- Python 3.7+
- 支持图形界面的操作系统

### 依赖包
```bash
pip install matplotlib numpy
```

### macOS用户额外要求
如果您在macOS上遇到tkinter相关错误，请安装：
```bash
brew install python-tk
```

## 使用方法

### 方法1：使用演示脚本（推荐）

```bash
python demo_bfs_visualizer.py
```

这个脚本会：
1. 自动查找可用的地牢文件
2. 显示地牢基本信息
3. 提供交互式菜单选择功能

### 方法2：使用命令行工具

```bash
# 启动交互式窗口
python bfs_visualizer_cli.py samples/population_eval_524288/feasible_pop/ind_101.json

# 执行可达性分析
python bfs_visualizer_cli.py samples/population_eval_524288/feasible_pop/ind_101.json --analysis-type accessibility

# 执行路径多样性分析
python bfs_visualizer_cli.py samples/population_eval_524288/feasible_pop/ind_101.json --analysis-type path-diversity

# 执行BFS遍历
python bfs_visualizer_cli.py samples/population_eval_524288/feasible_pop/ind_101.json --analysis-type bfs --start-node room_1 --target-node room_5
```

### 方法3：在代码中使用

```python
import sys
import os
sys.path.append('src')

from bfs_visualizer import create_bfs_visualizer

# 加载地牢数据
with open('your_dungeon.json', 'r') as f:
    dungeon_data = json.load(f)

# 创建可视化器
visualizer = create_bfs_visualizer(dungeon_data)

# 执行可达性分析
visualizer.visualize_accessibility_analysis()

# 执行路径多样性分析
visualizer.visualize_path_diversity()

# 执行BFS遍历
visualizer.visualize_bfs('room_1', 'room_5')

# 启动交互式窗口
visualizer.create_interactive_window()
```

## 支持的输入格式

可视化器支持统一地牢数据格式，包含以下结构：

```json
{
  "levels": [
    {
      "rooms": [
        {
          "id": "room_1",
          "position": {"x": 0, "y": 0},
          "size": {"width": 5, "height": 5}
        }
      ],
      "corridors": [
        {
          "id": "corridor_1", 
          "position": {"x": 5, "y": 2},
          "size": {"width": 3, "height": 1}
        }
      ],
      "connections": [
        {
          "from_room": "room_1",
          "to_room": "corridor_1"
        }
      ]
    }
  ]
}
```

## 算法说明

### BFS算法
- 使用广度优先搜索遍历地牢图
- 实时显示访问顺序和距离
- 支持路径重建和最短路径查找

### 可达性计算
- 对每个节点执行BFS遍历
- 计算可达节点比例：`可达性 = 可达节点数 / 总节点数`
- 考虑地牢的连通性质量

### 路径多样性计算
- 计算所有房间对之间的最短路径数量
- 使用递归方法统计等长路径
- 评估地牢的探索性和选择多样性

## 输出说明

### 可达性分析输出
- **节点颜色**：根据可达性分数着色
- **分数显示**：每个节点显示可达性分数
- **统计信息**：显示平均可达性和分布情况

### 路径多样性分析输出
- **连接线**：显示路径数量最多的房间对
- **数字标签**：显示路径数量
- **统计信息**：显示平均路径多样性

### BFS遍历输出
- **节点状态**：实时显示节点访问状态
- **距离信息**：显示从起始节点的距离
- **路径高亮**：如果指定目标节点，高亮显示最短路径

## 故障排除

### 常见问题

1. **导入错误**
   ```
   错误: 无法导入BFS可视化器模块
   ```
   **解决方案**：确保已安装matplotlib和numpy
   ```bash
   pip install matplotlib numpy
   ```

2. **图形界面无法显示**
   ```
   TclError: no display name and no $DISPLAY environment variable
   ```
   **解决方案**：
   - 确保在有图形界面的环境中运行
   - 在macOS上安装python-tk：`brew install python-tk`

3. **文件不存在错误**
   ```
   错误: 输入文件不存在
   ```
   **解决方案**：检查文件路径是否正确，确保地牢JSON文件存在

4. **节点ID错误**
   ```
   错误: 无效的起始节点
   ```
   **解决方案**：检查节点ID是否正确，使用演示脚本查看可用的节点ID

### 性能优化

- 对于大型地牢（>50个节点），动画速度可能较慢
- 可以通过修改`animation_speed`参数调整动画速度
- 路径多样性分析在大型地牢上可能耗时较长

## 扩展功能

### 自定义颜色方案
可以修改`BFSVisualizer`类中的`colors`字典来自定义颜色：

```python
self.colors = {
    'room': '#E3F2FD',           # 房间颜色
    'visited': '#4CAF50',        # 已访问节点颜色
    'current': '#FF9800',        # 当前节点颜色
    # ... 其他颜色
}
```

### 自定义动画速度
```python
visualizer.animation_speed = 0.3  # 更快的动画
```

### 添加新的分析类型
可以通过继承`BFSVisualizer`类来添加新的分析功能。

## 联系和支持

如果您在使用过程中遇到问题或有改进建议，请：

1. 检查本文档的故障排除部分
2. 查看项目的README.md文件
3. 提交Issue或Pull Request

---

**注意**：BFS可视化器需要图形界面支持，在服务器环境中可能无法正常工作。建议在本地开发环境中使用。 