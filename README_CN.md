# 地牢分析器

[中文版本 (Chinese Version)](./README_CN.md) | [English Version](./README.md)

一个专业的D&D地牢质量评估工具，具有Vue.js前端界面和Flask后端API。

## 项目结构

```
dungeon-adapter/
├── frontend/                 # Vue.js前端应用程序
│   ├── src/
│   │   ├── components/      # Vue组件
│   │   ├── views/          # 页面视图
│   │   ├── services/       # API服务
│   │   └── router/         # 路由配置
│   └── package.json
├── flask_backend/           # Flask后端API
│   ├── src/                # 复制的分析模块
│   ├── app.py              # 主Flask应用文件
│   ├── run.py              # 启动脚本
│   └── requirements.txt    # Python依赖
├── src/                    # 原始Python分析模块
│   ├── adapters/           # 不同地牢生成器的格式适配器
│   │   ├── __init__.py
│   │   ├── base.py         # 基础适配器类
│   │   ├── bsp_adapter.py  # BSP树格式适配器
│   │   ├── dd2vtt_adapter.py # DD2VTT格式适配器
│   │   ├── donjon_adapter.py # Donjon格式适配器
│   │   ├── dungeondraft_adapter.py # DungeonDraft格式适配器
│   │   ├── edgar_adapter.py # Edgar格式适配器
│   │   ├── fimap_elites_adapter.py # FIMAP Elites格式适配器
│   │   └── watabou_adapter.py # Watabou格式适配器
│   ├── quality_rules/      # 质量评估规则
│   │   ├── __init__.py
│   │   ├── base.py         # 基础质量规则类
│   │   ├── accessibility.py # 可达性分析
│   │   ├── dead_end_ratio.py # 死路比例分析
│   │   ├── degree_variance.py # 房间连接方差分析
│   │   ├── door_distribution.py # 门分布分析
│   │   ├── geometric_balance.py # 几何平衡分析
│   │   ├── key_path_length.py # 关键路径长度分析
│   │   ├── loop_ratio.py   # 循环比例分析
│   │   ├── normalization.py # 分数归一化工具
│   │   ├── path_diversity.py # 路径多样性分析
│   │   └── treasure_monster_distribution.py # 游戏元素分布
│   ├── statistical_testing/ # 统计分析和验证
│   │   ├── __init__.py
│   │   ├── advanced_analytics.py # 高级统计分析
│   │   ├── png_chart_generator.py # PNG图表生成
│   │   ├── run.py          # 测试运行器
│   │   ├── statistical_analysis.py # 主要统计分析
│   │   ├── summarize_validations.py # 验证摘要
│   │   ├── unified_chart_generator.py # 统一图表生成
│   │   └── validation.py   # 验证框架
│   ├── visualizers/        # 可视化工具
│   │   ├── __init__.py
│   │   ├── astar_visualizer.py # A*寻路可视化器
│   │   ├── bfs_visualizer.py # BFS可视化器
│   │   └── qt_bfs_visualizer.py # Qt版BFS可视化器
│   ├── __init__.py
│   ├── adapter_manager.py  # 格式适配器管理器
│   ├── batch_assess.py     # 批量评估功能
│   ├── cli.py              # 命令行接口
│   ├── csv_exporter.py     # CSV导出功能
│   ├── quality_assessor.py # 主要质量评估引擎
│   ├── schema.py           # 数据模式定义
│   ├── spatial_inference.py # 空间连接推断
│   └── visualizer.py       # 主可视化模块
└── README.md
```

## 快速开始

### 1. 启动Flask后端

```bash
cd flask_backend
pip install -r requirements.txt
python app.py
```

后端将在 `http://localhost:5001` 启动

### 2. 启动Vue前端

```bash
cd frontend
npm install
npm run dev
```

前端将在 `http://localhost:5173` 启动

### 3. 使用应用程序

1. 打开浏览器访问 `http://localhost:5173`
2. 上传地牢JSON文件
3. 选择分析选项
4. 点击"开始分析"
5. 查看分析结果

## API接口

### 健康检查
```
GET /api/health
```

### 获取支持的格式
```
GET /api/supported-formats
```

### 获取分析选项
```
GET /api/analysis-options
```

### 分析单个文件
```
POST /api/analyze
Content-Type: multipart/form-data
```

### 批量分析
```
POST /api/analyze-batch
Content-Type: multipart/form-data
```

### 格式转换
```
POST /api/convert-dungeon
Content-Type: multipart/form-data
```

## 支持的文件格式

- **Watabou**: Watabou地牢生成器格式
- **Donjon**: Donjon地牢生成器格式
- **DungeonDraft**: DungeonDraft导出格式
- **Edgar**: Edgar地牢生成器格式
- **JSON**: 通用JSON格式

## 分析指标

### 结构性指标
- **可达性 (Accessibility)**: 分析地牢可达性和路径设计
- **度方差 (Degree Variance)**: 评估房间连接度分布
- **门分布 (Door Distribution)**: 分析门的位置和分布
- **死路比例 (Dead End Ratio)**: 评估死路数量和分布
- **关键路径长度 (Key Path Length)**: 分析关键路径设计
- **循环比例 (Loop Ratio)**: 分析循环设计以避免线性体验
- **路径多样性 (Path Diversity)**: 评估路径选择多样性

### 可玩性指标
- **宝藏怪物分布 (Treasure Monster Distribution)**: 分析宝藏和怪物的合理分布

### 视觉指标
- **美学平衡 (Aesthetic Balance)**: 评估房间布局美学和平衡性

## 技术栈

### 前端
- Vue 3 + TypeScript
- Vite
- Phaser.js (游戏引擎)
- Vue Router
- Pinia (状态管理)

### 后端
- Flask
- Flask-CORS
- Python 3.x

## 开发

### 前端开发
```bash
cd frontend
npm run dev          # 开发模式
npm run build        # 构建生产版本
npm run preview      # 预览构建结果
```

### 后端开发
```bash
cd flask_backend
python app.py        # 开发模式
```

## 贡献者
作者: MAX LI- Chenglun11

## 许可证
MIT License