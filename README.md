# Dungeon Analyzer

[中文版本 (Chinese Version)](./README_CN.md) | [English Version](./README.md)

A professional D&D dungeon quality assessment tool featuring a Vue.js frontend interface and Flask backend API.

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

## Quick Start - Web

### 1. Start Flask Backend

```bash
cd flask_backend
pip install -r requirements.txt
python app.py
```

Backend will start at `http://localhost:5001`

### 2. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will start at `http://localhost:5173`

### 3. Using the Application

1. Open browser and visit `http://localhost:5173`
2. Upload dungeon JSON files
3. Select analysis options
4. Click "Start Analysis"
5. View analysis results


## Quick Start - Cli
### Overview
```bash
    cd src/
```
```bash
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

  # Cross-dataset analysis for F_Q dataset
  python cli.py cross-dataset-analysis --input output/F_Q_Report --output output/F_Q_Report/SA

  # Export validation data to CSV
  python cli.py export-csv --validation output/validation_report.json --output validation_data.csv

  # Export descriptive statistics to CSV
  python cli.py export-csv --descriptive output/statistical_analysis_report.json --output descriptive_stats.csv

  # Auto-export all data from directory to CSV
  python cli.py export-csv --auto-dir output/ --output-dir csv_exports/
```


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

### Playability Metrics
- **Treasure Monster Distribution**: Analyzes reasonable distribution of treasures and monsters


## Technology Stack

### Frontend
- Vue 3 + TypeScript
- Vite
- Phaser.js (Game engine)
- Vue Router
- Pinia (State management)

### Backend
- Flask
- Flask-CORS
- Python 3.x

## Development

### Frontend Development
```bash
cd frontend
npm run dev          # Development mode
npm run build        # Build production version
npm run preview      # Preview build results
```

### Backend Development
```bash
cd flask_backend
python app.py        # Development mode
```

## Contributing
Author: MAX LI- Chenglun11

## License
MIT License 
