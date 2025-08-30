<br />

<p align="center">
  <a href="https://github.com/chenglun11/DND_Analyse/">
    <img src="https://www.york.ac.uk/static/stable/img/logo.svg" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">DND_Analysis </h3>
  <p align="center">A professional D&D dungeon quality assessment tool. </p>
  <p align="center">
    <br />
    <a href="https://github.com/chenglun11/DND_Analyse/blob/frontend-ui/README.md"><strong>Explore this document »</strong></a>
    <br />
    <br />
    <a href="#demo">Demo</a>
    ·
    <a href="https://github.com/chenglun11/DND_Analyse/blob/frontend-ui/README_cn.md">简体中文[ZH-CN]</a>
    ·
    <a href="https://github.com/chenglun11/DND_Analyse/issues">Report Bug</a>
    ·
    <a href="https://github.com/chenglun11/DND_Analyse/issues">Commit a Feature</a>

</p>

</p>

## 项目依赖
```bash
numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.5.0
pillow>=8.3.0
networkx >=3.5

scipy>=1.7.0
scikit-learn>=1.0.0

tqdm>=4.62.0
click>=8.0.0
pathlib2>=2.3.0
loguru

PyQt5>=5.15.0

pytest>=6.2.0
black>=21.0.0
flake8>=3.9.0
mypy>=0.910

Flask==3.0.0
Flask-CORS==4.0.0
Werkzeug==3.0.1

OR use reqirement.txt
```

## 快速开始
1. Install requirements
```bash
pip install -r requirements.txt
```
2. Starting backend service
```bash
cd flask_backend & python run.py
```
Backend will start at `http://localhost:5001`

3. Starting frontend service
```bash
cd frontend & npm install #Install frontend requirement
npm run dev
```
Frontend will start at `http://localhost:5173`


---
1. CLI usage
```bash
cd src/

 # Convert single file (auto-detect format)
  python cli.py convert samples/onepage_example.json output/

  # Convert single file (specify format)
  python cli.py convert samples/onepage_example.json output/ --format onepage_dungeon

  # Convert entire directory (including subdirectories)
  python cli.py convert-dir samples/ output/

  # Detect file format
  python cli.py detect samples/onepage_example.json

  # List supported formats
  python cli.py list-formats

  # Generate visualization image for converted JSON file
  python cli.py visualize output/test_onepage_example.json

  # Assess single file quality
  python cli.py assess output/test_onepage_example.json

  # Batch assess directory quality (including subdirectories)
  python cli.py batch-assess output/watabou_test/ output/batch_reports/

  # Statistical analysis of batch results
  python cli.py statistical-analysis output/watabou_test_batch_report.json

  # Export validation data to CSV
  python cli.py export-csv --validation output/validation_report.json --output validation_data.csv

  # Export descriptive statistics to CSV
  python cli.py export-csv --descriptive output/statistical_analysis_report.json --output descriptive_stats.csv

  # Auto-export all data from directory to CSV
  python cli.py export-csv --auto-dir output/ --output-dir csv_exports/
```

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
- **宝藏怪物分布 (Treasure Monster Distribution)**: 分析宝藏和怪物的合理分布
- **几何平衡**: 客观评估地下城布局的几何平衡性

## 版本控制

该项目使用 Git 进行版本控制。你可以在版本库中看到当前可用的版本。

## Author

[chenglun11](https://github.com/chenglun11) 是该 repo 的作者


## License

Copyright (c) 2024 chenglun11 with [MIT License](/LICENSE)

