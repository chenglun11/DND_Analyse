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
    ·
    <a href="https://github.com/chenglun11/DND_Analyse/blob/frontend-ui/README_cn.md">简体中文[ZH-CN]</a>
    ·
    <a href="https://github.com/chenglun11/DND_Analyse/issues">Report Bug</a>
    ·
    <a href="https://github.com/chenglun11/DND_Analyse/issues">Commit a Feature</a>

</p>

</p>

## Requirements

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

## Getting Started
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


## Project Structure

```
dungeon-adapter/
├── frontend/                 # Vue.js frontend application
│   ├── src/
│   │   ├── components/      # Vue components
│   │   ├── views/          # Page views
│   │   ├── services/       # API services
│   │   └── router/         # Routing configuration
│   └── package.json
├── flask_backend/           # Flask backend API
│   ├── src/                # Copied analysis modules
│   ├── app.py              # Main Flask application file
│   ├── run.py              # Startup script
│   └── requirements.txt    # Python dependencies
├── src/                    # Original Python analysis modules
│   ├── adapters/           # Format adapters for different dungeon generators
│   │   ├── __init__.py
│   │   ├── base.py         # Base adapter class
│   │   ├── bsp_adapter.py  # BSP tree format adapter
│   │   ├── dd2vtt_adapter.py # DD2VTT format adapter
│   │   ├── donjon_adapter.py # Donjon format adapter
│   │   ├── dungeondraft_adapter.py # DungeonDraft format adapter
│   │   ├── edgar_adapter.py # Edgar format adapter
│   │   ├── fimap_elites_adapter.py # FIMAP Elites format adapter
│   │   └── watabou_adapter.py # Watabou format adapter
│   ├── quality_rules/      # Quality assessment rules
│   │   ├── __init__.py
│   │   ├── base.py         # Base quality rule class
│   │   ├── accessibility.py # Accessibility analysis
│   │   ├── dead_end_ratio.py # Dead-end ratio analysis
│   │   ├── degree_variance.py # Room connection variance analysis
│   │   ├── door_distribution.py # Door distribution analysis
│   │   ├── geometric_balance.py # Geometric balance analysis
│   │   ├── key_path_length.py # Critical path length analysis
│   │   ├── loop_ratio.py   # Loop ratio analysis
│   │   ├── normalization.py # Score normalization utilities
│   │   ├── path_diversity.py # Path diversity analysis
│   │   └── treasure_monster_distribution.py # Game element distribution
│   ├── statistical_testing/ # Statistical analysis and validation
│   │   ├── __init__.py
│   │   ├── advanced_analytics.py # Advanced statistical analytics
│   │   ├── png_chart_generator.py # PNG chart generation
│   │   ├── run.py          # Test runner
│   │   ├── statistical_analysis.py # Main statistical analysis
│   │   ├── summarize_validations.py # Validation summaries
│   │   ├── unified_chart_generator.py # Unified chart generation
│   │   └── validation.py   # Validation framework
│   ├── visualizers/        # Visualization tools
│   │   ├── __init__.py
│   │   ├── astar_visualizer.py # A* pathfinding visualizer
│   │   ├── bfs_visualizer.py # BFS visualizer
│   │   └── qt_bfs_visualizer.py # Qt-based BFS visualizer
│   ├── __init__.py
│   ├── adapter_manager.py  # Manages format adapters
│   ├── batch_assess.py     # Batch assessment functionality
│   ├── cli.py              # Command-line interface
│   ├── csv_exporter.py     # CSV export functionality
│   ├── quality_assessor.py # Main quality assessment engine
│   ├── schema.py           # Data schema definitions
│   ├── spatial_inference.py # Spatial connection inference
│   └── visualizer.py       # Main visualization module
└── README.md
```

## Supported File Formats

- **Watabou**: Watabou Dungeon Generator format
- **Edgar**: Edgar Dungeon Generator format
- **FI-Map-Elites**: EA Dungeon Generator format
- **DD2VTT**: (Beta) A General Dungeon format

## Analysis Metrics

### Structural Metrics
- **Accessibility**: Analyzes dungeon accessibility and path design
- **Degree Variance**: Evaluates room connection degree distribution
- **Door Distribution**: Analyzes door positioning and distribution
- **Dead End Ratio**: Evaluates dead-end quantity and distribution
- **Key Path Length**: Analyzes critical path design
- **Loop Ratio**: Analyzes loop design to avoid linear experience
- **Path Diversity**: Evaluates path selection diversity
- **Treasure Monster Distribution**: Analyzes reasonable distribution of treasures and monsters
- **Geometric Balance**: Objectively assessing the geometric balance of dungeon layouts

## API Endpoints
### Health Check
```
GET /api/health
```

### Get Supported Formats
```
GET /api/supported-formats
```

### Get Analysis Options
```
GET /api/analysis-options
```

### Analyze Single File
```
POST /api/analyze
Content-Type: multipart/form-data
```

### Batch Analysis
```
POST /api/analyze-batch
Content-Type: multipart/form-data
```

### Format Conversion
```
POST /api/convert-dungeon
Content-Type: multipart/form-data
```


## Version Control

The project uses Git for version control. You can see the currently available versions in the repository.

## Author

[chenglun11](https://github.com/chenglun11) is the coder of this repo

## License

Copyright (c) 2024 chenglun11 with [MIT License](/LICENSE)


