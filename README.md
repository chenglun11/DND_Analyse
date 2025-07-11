# DnD 地牢地图格式适配器

本项目旨在提供一个工具，用于将各种来源的 DnD (Dungeons & Dragons) 地牢地图 JSON 文件转换为统一的、可分析的格式。

## 🏗️ 插件式架构

本项目采用模块化的插件式架构，使得添加新的地图格式支持变得非常简单。每个适配器都是独立的模块，可以轻松地添加、移除或修改，而不会影响其他功能。

### 架构概览

```
src/
├── adapter_manager.py    # 适配器管理器（核心）
├── schema.py            # 统一数据格式定义
├── visualizer.py        # 可视化工具
├── cli.py              # 命令行界面
└── adapters/           # 适配器插件目录
    ├── __init__.py
    ├── base.py         # 适配器基类（接口定义）
    ├── watabou_adapter.py
    ├── dungeondraft_adapter.py
    └── vtt_adapter.py
```

## 可视化功能

新增了可视化功能，可以将统一格式的 JSON 文件渲染成一张包含房间、走廊和门的俯瞰图，方便快速预览转换结果。

### 安装依赖

```bash
pip install -r requirements.txt
```

### 使用方法

在转换时自动生成预览图：
```bash
# 转换单个文件并生成预览图
python src/cli.py convert samples/source_format_1/watabou_example.json output/ --visualize

# 转换整个目录并为每个文件生成预览图
python src/cli.py convert-dir samples/source_format_1/ output/ --visualize
```
预览图将与转换后的 JSON 文件保存在同一目录，后缀为 `.png`。

直接对已有的统一格式 JSON 文件生成预览图：
```bash
python src/cli.py visualize output/test_watabou_example.json
```

## 功能特性

- 🔄 **多格式支持**: 支持 Watabou、DungeonDraft、Foundry VTT、Roll20 等多种格式
- 🤖 **自动格式检测**: 智能识别输入文件的格式类型
- 📊 **统一输出格式**: 所有转换结果都采用标准化的 JSON 格式
- 🛠️ **命令行工具**: 提供便捷的命令行界面
- 🧪 **完整测试**: 包含全面的测试套件
- 📝 **详细日志**: 提供转换过程的详细日志信息
- 🔌 **插件式架构**: 模块化设计，易于扩展新格式支持

### 📊 质量评估
- **可达性分析**: 评估房间间的连通性
- **度差分析**: 分析房间连接数的分布
- **路径多样性**: 计算可选路径的数量
- **回环率分析**: 评估地图的探索深度
- **门分布一致性**: 分析入口分布的合理性
- **综合评分**: 基于规则的质量评分系统

## 支持的格式

| 格式名称 | 描述 | 检测特征 |
|---------|------|----------|
| `watabou_dungeon` | Watabou 地牢生成器 | 包含 `rects`, `doors`, `title` 字段 |
| `dungeondraft` | DungeonDraft 地图 | 包含 `version` 和 `elements` 字段 |
| `vtt` | 通用VTT格式（Foundry VTT、Roll20等） | 包含 `scene.walls` 或 `map.tokens` 结构 |
| `generic_grid` | 通用网格格式 | 包含 `grid` 和 `cells` 字段 |

## 统一数据格式 (v1.0.0)

这是我们定义的地牢地图标准格式。

```json
{
  "header": {
    "schemaName": "dnd-dungeon-unified",
    "schemaVersion": "1.0.0",
    "name": "我的地牢",
    "author": "AI 助手",
    "description": "一个用于分析的地牢地图。",
    "grid": {
      "type": "square",
      "size": 5,
      "unit": "ft"
    }
  },
  "levels": [
    {
      "id": "level_1",
      "name": "第一层",
      "map": {
        "width": 50,
        "height": 50
      },
      "rooms": [
        {
          "id": "room_1",
          "shape": "rectangle",
          "position": { "x": 10, "y": 10 },
          "size": { "width": 10, "height": 8 },
          "name": "入口大厅",
          "description": "一个满是灰尘雕像的大厅。"
        }
      ],
      "doors": [
        {
          "id": "door_1",
          "position": { "x": 20, "y": 14 },
          "connects": ["room_1", "corridor_1"]
        }
      ],
      "corridors": [
        {
          "id": "corridor_1",
          "path": [
            { "x": 20, "y": 14 },
            { "x": 25, "y": 14 }
          ],
          "width": 2
        },
        {
          "id": "corridor_2",
          "shape": "rectangle",
          "position": { "x": 30, "y": 20 },
          "size": { "width": 5, "height": 10 }
        }
      ]
    }
  ]
}
```

## 安装和使用

### 环境要求

- Python 3.7+
- 依赖包：matplotlib（用于可视化）

### 快速开始

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd dungeon-adapter
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **运行测试**
   ```bash
   python test_adapter.py
   ```

4. **使用命令行工具**
   ```bash
   # 转换单个文件
   python src/cli.py convert samples/source_format_1/onepage_example.json output/
   
   # 转换整个目录
   python src/cli.py convert-dir samples/source_format_1/ output/
   
   # 检测文件格式
   python src/cli.py detect samples/source_format_1/onepage_example.json
   
   # 列出支持的格式
   python src/cli.py list-formats
   ```

### 编程接口

```python
from src.adapter_manager import AdapterManager

# 创建适配器管理器
manager = AdapterManager()

# 加载源数据
with open('your_dungeon.json', 'r') as f:
    source_data = json.load(f)

# 自动检测格式并转换
unified_data = manager.convert(source_data)

# 或者指定格式
unified_data = manager.convert(source_data, 'onepage_dungeon')

# 保存结果
with open('output.json', 'w') as f:
    json.dump(unified_data, f, indent=2)
```

## 目录结构

```
dungeon-adapter/
├── src/                    # 源代码
│   ├── adapter_manager.py  # 适配器管理器
│   ├── schema.py          # 数据格式定义
│   ├── visualizer.py      # 可视化工具
│   ├── cli.py            # 命令行工具
│   └── adapters/         # 适配器插件目录
│       ├── __init__.py
│       ├── base.py       # 适配器基类
│       ├── watabou_adapter.py
│       ├── dungeondraft_adapter.py
│       └── vtt_adapter.py
├── samples/               # 示例文件
│   └── source_format_1/   # 各种格式的示例
│       ├── onepage_example.json
│       ├── watabou_example.json
│       ├── dungeondraft_example.json
│       └── vtt_example.json
├── output/                # 转换后的文件
├── test_adapter.py        # 测试脚本
└── README.md             # 项目说明
```

## 使用示例

### 示例 1: One Page Dungeon 格式

**输入文件** (`onepage_example.json`):
```json
{
  "name": "古老的地下墓穴",
  "author": "DM助手",
  "rooms": [
    {
      "id": "entrance",
      "name": "入口大厅",
      "position": {"x": 10, "y": 15},
      "size": {"width": 15, "height": 10}
    }
  ]
}
```

**转换命令**:
```bash
python src/cli.py convert samples/source_format_1/onepage_example.json output/
```

### 示例 2: Watabou 格式

**输入文件** (`watabou_example.json`):
```json
{
  "title": "随机生成的地牢",
  "rects": [
    {
      "x": 5,
      "y": 5,
      "w": 8,
      "h": 6
    }
  ],
  "doors": [],
  "notes": []
}
```

**转换命令**:
```bash
python src/cli.py convert samples/source_format_1/watabou_example.json output/
```

### 示例 3: VTT 格式

**输入文件** (`vtt_example.json`):
```json
{
  "scene": {
    "name": "Ancient Crypt",
    "walls": [
      {
        "id": "wall_1",
        "c": [100, 100, 300, 100],
        "ds": 0
      },
      {
        "id": "door_1",
        "c": [200, 100, 200, 100],
        "ds": 1,
        "door": true
      }
    ]
  }
}
```

**转换命令**:
```bash
python src/cli.py convert samples/source_format_1/vtt_example.json output/
```

## 🔧 开发新适配器

要添加对新地图格式的支持，请按照以下步骤操作：

### 1. 创建适配器文件

在 `src/adapters/` 目录下创建新的适配器文件，例如 `my_format_adapter.py`：

```python
import logging
from typing import Dict, Any, Optional

from src.adapters.base import BaseAdapter
from src.schema import UnifiedDungeonFormat

logger = logging.getLogger(__name__)

class MyFormatAdapter(BaseAdapter):
    """适配 MyFormat 地图格式。"""
    
    @property
    def format_name(self) -> str:
        return "my_format"

    def detect(self, data: Dict[str, Any]) -> bool:
        """检测是否为 MyFormat 格式。"""
        # 根据你的格式特征进行检测
        # 例如：检查特定的字段或结构
        return 'my_format_signature' in data

    def convert(self, data: Dict[str, Any]) -> Optional[UnifiedDungeonFormat]:
        """将 MyFormat 格式数据转换为统一格式。"""
        try:
            # 创建统一格式对象
            unified = UnifiedDungeonFormat(
                name=data.get('name', 'My Format Dungeon'),
                author=data.get('author', 'Unknown'),
                description=data.get('description', ''),
                grid={"type": "square", "size": 5, "unit": "ft"}
            )

            # 转换房间
            rooms = []
            for room_data in data.get('my_rooms', []):
                rooms.append({
                    "id": f"room_{room_data.get('id', len(rooms)+1)}",
                    "shape": "rectangle",
                    "position": {"x": room_data['x'], "y": room_data['y']},
                    "size": {"width": room_data['width'], "height": room_data['height']},
                    "name": room_data.get('name', f"房间 {len(rooms)+1}"),
                    "description": room_data.get('description', '')
                })

            # 转换门
            doors = []
            for door_data in data.get('my_doors', []):
                doors.append({
                    "id": f"door_{len(doors)+1}",
                    "position": {"x": door_data['x'], "y": door_data['y']},
                    "connects": door_data.get('connects', [])
                })

            # 转换走廊
            corridors = []
            for corridor_data in data.get('my_corridors', []):
                corridors.append({
                    "id": f"corridor_{len(corridors)+1}",
                    "shape": "rectangle",
                    "position": {"x": corridor_data['x'], "y": corridor_data['y']},
                    "size": {"width": corridor_data['width'], "height": corridor_data['height']}
                })

            # 添加层级
            unified.levels.append({
                "id": "level_1",
                "name": "主层",
                "map": {"width": data.get('width', 100), "height": data.get('height', 100)},
                "rooms": rooms,
                "doors": doors,
                "corridors": corridors
            })
            
            return unified
        except Exception as e:
            logger.error(f"转换 MyFormat 格式时出错: {e}")
            return None
```

### 2. 注册适配器

适配器会自动被 `AdapterManager` 发现和加载，无需手动注册。只要你的适配器类继承自 `BaseAdapter` 并放在 `src/adapters/` 目录下，就会被自动识别。

### 3. 测试适配器

创建测试用例来验证你的适配器：

```python
# 在 test_adapter.py 中添加测试
def test_my_format_adapter():
    adapter = MyFormatAdapter()
    
    # 测试检测功能
    test_data = {
        'my_format_signature': True,
        'name': '测试地牢',
        'my_rooms': [
            {'id': 1, 'x': 10, 'y': 10, 'width': 5, 'height': 5, 'name': '测试房间'}
        ]
    }
    
    assert adapter.detect(test_data) == True
    
    # 测试转换功能
    result = adapter.convert(test_data)
    assert result is not None
    assert result.name == '测试地牢'
    assert len(result.levels[0]['rooms']) == 1
```

### 4. 更新文档

在 `README.md` 的"支持的格式"表格中添加你的新格式：

```markdown
| `my_format` | My Format 地图 | 包含 `my_format_signature` 字段 |
```

### 适配器开发最佳实践

1. **继承基类**: 确保你的适配器继承自 `BaseAdapter`
2. **实现必需方法**: 必须实现 `format_name`、`detect` 和 `convert` 方法
3. **错误处理**: 在 `convert` 方法中使用 try-catch 处理异常
4. **日志记录**: 使用 logger 记录重要的转换步骤和错误
5. **数据验证**: 验证输入数据的完整性和有效性
6. **测试覆盖**: 为你的适配器编写完整的测试用例

## 测试

运行完整的测试套件：

```bash
python test_adapter.py
```

测试包括：
- 格式检测功能
- 数据转换功能
- 示例文件处理
- 统一格式完整性验证
- 适配器插件加载测试

## 贡献

欢迎提交 Issue 和 Pull Request！

### 开发指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 贡献新适配器

1. 在 `src/adapters/` 目录下创建新的适配器文件
2. 继承 `BaseAdapter` 并实现必需的方法
3. 添加相应的测试用例
4. 更新文档
5. 提交 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 更新日志

### v2.0.0
- 🏗️ **重构为插件式架构**: 采用模块化设计，支持动态加载适配器
- 🔌 **新增适配器基类**: 统一的适配器接口，便于扩展
- 📦 **适配器管理器**: 自动发现和加载所有适配器插件
- 🧹 **代码清理**: 移除调试代码，优化代码结构
- 📚 **完善文档**: 添加详细的适配器开发指南

### v1.0.0
- 初始版本发布
- 支持 6 种主要格式
- 提供命令行工具
- 完整的测试套件 