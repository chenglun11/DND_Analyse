# Dungeon Analyzer - Complete User Guide

A comprehensive guide for using the Dungeon Quality Evaluation System, including BSP integration, statistical testing, and advanced analysis features.

## Table of Contents

- [Quick Start](#quick-start)
- [BSP Dungeon Generator Integration](#bsp-dungeon-generator-integration)
- [Data Format Requirements](#data-format-requirements)
- [Advanced Directory Management](#advanced-directory-management)
- [Statistical Testing](#statistical-testing)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### System Overview

The Dungeon Analyzer consists of three main components:
1. **BSP Dungeon Generator** - Web-based interactive dungeon generation tool
2. **Evaluation Backend** - Python Flask API for quality assessment
3. **Frontend Interface** - Vue.js web interface for analysis and visualization

### Basic Setup

#### 1. Start BSP Dungeon Generator

```bash
# Navigate to BSP project directory
cd bsp-dungeon-generator-main

# Start development server
npm start
```

**After startup:**
- Open browser and visit: `http://localhost:3000`
- Use the left panel to adjust generation parameters
- Click "Generate" to create new dungeons
- Click "Download for Evaluation" to get evaluation-compatible format

#### 2. Start Evaluation Backend

```bash
# Return to project root directory
cd ..

# Install Python dependencies (if not installed)
pip install -r requirements.txt

# Start Flask backend
cd flask_backend
python run.py
```

Backend service runs on: `http://localhost:5000`

#### 3. Start Frontend Interface

```bash
# Start Vue frontend
cd ../frontend
npm install  # if dependencies not installed
npm run dev
```

Frontend interface runs on: `http://localhost:5173`

### Basic Workflow

1. **Generate Dungeon**: Use BSP generator to create dungeons
2. **Download**: Get evaluation-compatible JSON format
3. **Upload**: Use frontend interface to upload and analyze
4. **Review**: View detailed evaluation reports and metrics

---

## BSP Dungeon Generator Integration

### Frontend Adaptation Status

The frontend is fully adapted for BSP format with no additional modifications needed. The BSP adapter is integrated into the backend API, allowing direct processing of BSP-generated JSON files.

**Integration Test Results:**
- BSP adapter successfully loaded into backend
- Supports automatic BSP format detection and conversion
- Test results: 16 rooms, 17 connections, 133 game elements
- Evaluation score: 0.708 (Good level)

### BSP Interface Features

#### Parameter Settings
- **Map width/height**: Map dimensions
- **Iterations**: BSP splitting iteration count
- **Container minimum size**: Minimum room container size
- **Corridor width**: Corridor width
- **Tile width**: Tile width for rendering

#### Generation Controls
- **Manual seed**: Optional fixed seed selection
- **Debug**: Display debug information
- **Generate**: Generate new dungeon

#### Export Functions
- **Download dungeon JSON**: Original BSP format
- **Download for Evaluation**: Evaluation system compatible format ⭐

### Supported BSP Formats

The frontend supports the following formats through the BSP adapter:
- ✅ **Complete Format**: BSP website generated format (includes width, height, tree, layers)
- ✅ **Simplified Format**: Basic format containing rects, doors
- ✅ **Automatic Format Detection**: No need to manually specify format type

### Evaluation Metrics for BSP Dungeons

BSP dungeons are evaluated on 9 key metrics:

1. **Key Path Length** - Path efficiency from entrance to exit
2. **Accessibility** - Connectivity of all rooms
3. **Dead End Ratio** - Avoiding excessive dead ends
4. **Loop Ratio** - Circular path design
5. **Geometric Balance** - Spatial layout balance
6. **Treasure Monster Distribution** - Game element distribution
7. **Path Diversity** - Exploration path variety
8. **Degree Variance** - Room connection complexity
9. **Door Distribution** - Door placement reasonableness

### Sample Evaluation Results

```
Overall Score: 0.708 (Good)
- Room Count: 16
- Connection Count: 17 (includes 2 auto-inferred connections)
- Game Elements: 133 (includes 22 monster encounters, 21 treasures, etc.)
- Supported Metrics: All 9 metrics
```

**Individual Metric Performance:**
- Accessibility: High score (all rooms reachable)
- Geometric Balance: Good (naturally balanced BSP algorithm)
- Monster/Treasure Distribution: Reasonable (template-based distribution)
- Path Diversity: Medium (BSP tree structure characteristics)
- Loop Ratio: Medium (improved after connection enhancement)

---

## Data Format Requirements

### ⚠️ Critical: Data Format Requirements

All statistical tests **must use converted unified format data**, not raw format data directly!

### Correct Data Paths

#### ✅ Converted Data (For Statistical Testing)
```
output/finial_test/
├── BSP/           # BSP algorithm converted data
├── FI/            # FI algorithm converted data  
├── ODPC/          # ODPC algorithm converted data
└── Watabou/       # Watabou algorithm converted data
```

#### ❌ Raw Data (Not Compatible with Statistical Testing)
```
samples/test/
├── BSP/           # BSP raw format - Incompatible!
├── FI/            # FI raw format - Incompatible!
├── ODPC/          # ODPC raw format - Incompatible!
└── Watabou/       # Watabou raw format - Incompatible!
```

### Data Conversion Workflow

1. **Raw Data** → Various format dungeon data
2. **Format Conversion** → Unified dungeon format (UnifiedDungeonFormat)
3. **Quality Assessment** → Evaluation using unified format
4. **Statistical Testing** → Validation based on evaluation results

### Format Examples

**BSP Raw Format:**
```json
{
  "width": 64,
  "height": 48,
  "tree": {...},
  "layers": {...}
}
```

**Unified Format:**
```json
{
  "header": {
    "schemaName": "dnd-dungeon-unified",
    "version": "1.0"
  },
  "levels": [{
    "rooms": [...],
    "connections": [...],
    "entities": [...]
  }]
}
```

### Usage Guidelines

#### When Running Statistical Tests
```bash
# ✅ Correct
python run.py --mode validation --dataset ../../output/finial_test/BSP/

# ❌ Incorrect  
python run.py --mode validation --dataset ../../samples/test/BSP/
```

#### Verify Data is Converted
```bash
# View converted data example
head output/finial_test/BSP/bsp_dungeon-1.json

# Should see structure like:
# {"header": {"schemaName": "dnd-dungeon-unified", ...}, "levels": [...]}
```

#### Convert Missing Data
```bash
# Run converter to transform raw data to unified format
python src/batch_assess.py --input samples/test/ --output output/finial_test/
```

---

## Advanced Directory Management

### Paper_Test Directory Structure

```
output/Paper_Test/
├── covnert/           # Converted unified format data
│   ├── BSP/           # 🔹 For system validation
│   ├── FI/            # 🔹 For system validation
│   ├── ODPC/          # 🔹 For system validation
│   └── Watabou/       # 🔹 For system validation
└── assess/            # Quality evaluation reports
    ├── BSP/           # 📊 For statistical analysis
    ├── FI/            # 📊 For statistical analysis
    ├── ODPC/          # 📊 For statistical analysis
    ├── Watabou/       # 📊 For statistical analysis
    ├── covnert_batch_report.json
    ├── quality_summary_report.json
    └── result.md
```

### Different Tests Use Different Subdirectories

#### 1. System Validity Validation → Use `covnert/` Directory

```bash
cd src/statistical_testing

# Validate BSP data
python run.py --mode validation --dataset ../../output/Paper_Test/covnert/BSP/

# Validate all algorithms (run separately)
python run.py --mode validation --dataset ../../output/Paper_Test/covnert/FI/
python run.py --mode validation --dataset ../../output/Paper_Test/covnert/ODPC/
python run.py --mode validation --dataset ../../output/Paper_Test/covnert/Watabou/
```

#### 2. Statistical Analysis → Use `assess/` Directory Summary Reports

```bash
cd src/statistical_testing

# Use quality summary report for statistical analysis
python run.py --mode analysis --input ../../output/Paper_Test/assess/quality_summary_report.json

# Or use conversion batch report
python run.py --mode analysis --input ../../output/Paper_Test/assess/covnert_batch_report.json
```

### Batch Processing Script

Create a unified Paper_Test analysis script:

```bash
#!/bin/bash
# paper_test_runner.sh

echo "🔬 Paper Test Data Analysis Suite"
echo "=================================="

BASE_DIR="../../output/Paper_Test"
OUTPUT_DIR="../../output/Paper_Test_Analysis"

# 1. System validation - use converted data
echo "📊 Running System Validation..."
python run.py --mode validation --dataset "$BASE_DIR/covnert/BSP/" --output "$OUTPUT_DIR/validation_BSP.json"
python run.py --mode validation --dataset "$BASE_DIR/covnert/FI/" --output "$OUTPUT_DIR/validation_FI.json"
python run.py --mode validation --dataset "$BASE_DIR/covnert/ODPC/" --output "$OUTPUT_DIR/validation_ODPC.json" 
python run.py --mode validation --dataset "$BASE_DIR/covnert/Watabou/" --output "$OUTPUT_DIR/validation_Watabou.json"

# 2. Statistical analysis - use quality reports
echo "📈 Running Statistical Analysis..."
python run.py --mode analysis --input "$BASE_DIR/assess/quality_summary_report.json" --output "$OUTPUT_DIR/statistics/"

echo "✅ Paper Test Analysis Completed!"
echo "📁 Results in: $OUTPUT_DIR"
```

### Data Integrity Verification

```bash
# Check converted data
ls output/Paper_Test/covnert/BSP/*.json | wc -l
ls output/Paper_Test/covnert/FI/*.json | wc -l  
ls output/Paper_Test/covnert/ODPC/*.json | wc -l
ls output/Paper_Test/covnert/Watabou/*.json | wc -l

# Check evaluation reports
ls output/Paper_Test/assess/BSP/*.json | wc -l
ls output/Paper_Test/assess/FI/*.json | wc -l
ls output/Paper_Test/assess/ODPC/*.json | wc -l
ls output/Paper_Test/assess/Watabou/*.json | wc -l
```

---

## Statistical Testing

### Feature Overview

The system provides a complete statistical validation framework:

- **System Validity Validation** - 7 validation methods for comprehensive system reliability assessment
- **Batch Statistical Analysis** - Deep statistical analysis based on evaluation results
- **Advanced Analysis** - PCA, clustering, multicollinearity detection
- **Visualization Generation** - Automatic generation of various statistical charts

### Quick Start Commands

#### Run System Validation

```bash
# Run validation script directly (using converted data)
cd src/statistical_testing
python run.py --mode validation --dataset ../../output/finial_test/BSP/

# Or use original validation.py
python validation.py --dataset ../../output/finial_test/BSP/ --output ../../output/validation/
```

#### Run Statistical Analysis

```bash
# Batch statistical analysis
cd src/statistical_testing
python run.py --mode analysis --input ../../output/batch_summary.json

# Or use original script
python statistical_analysis.py ../../output/batch_summary.json --output ../../output/analysis/
```

### System Validity Validation

Validates system effectiveness across 7 dimensions:

1. **Cross Validation** - Data split consistency testing
2. **Test-Retest Reliability** - Multi-run stability testing
3. **Metric Correlation Validation** - Logical relationship checking between metrics
4. **Sensitivity Analysis** - System response to change testing
5. **Statistical Validity** - Score distribution statistical properties testing
6. **Known Baseline Validation** - Manual annotation data comparison
7. **Comprehensive Validation** - Integrated assessment of all validation methods

**Output Results:**
- Overall validity score (0-1)
- Detailed results for each validation
- System improvement recommendations
- Complete report in JSON format

### Batch Statistical Analysis

Deep statistical analysis features:

- **Spearman Correlation Analysis** - Rank correlation relationships between metrics
- **VIF Multicollinearity Detection** - Identify redundant metrics
- **PCA Principal Component Analysis** - Dimensionality reduction and feature extraction
- **Hierarchical Cluster Analysis** - Discover metric grouping patterns

**Output Results:**
- Correlation heatmaps and network relationship diagrams
- VIF analysis charts
- PCA scree plots and loading plots
- Cluster dendrograms
- Detailed statistical analysis reports

### Output File Structure

```
output/
├── validation/                    # System validation results
│   ├── validation_report.json    # Comprehensive validation report
│   └── individual_validations/   # Detailed results for each validation
├── analysis/                      # Statistical analysis results
│   ├── statistical_analysis_report.json
│   └── charts/                    # Statistical charts
│       ├── spearman_heatmap.png
│       ├── vif_analysis.png
│       └── pca_analysis.png
└── F_Q_Report/
    └── SA/                        # F_Q specialized analysis
        ├── f_q_statistical_summary.json
        └── *_detailed_statistics.csv
```

### Result Interpretation

#### Validation Score Meaning
- **0.8-1.0**: Highly effective system, ready for production use
- **0.6-0.8**: Moderately effective system, recommended for use after improvements
- **0.4-0.6**: Limited system effectiveness, major improvements needed
- **0.0-0.4**: Low system effectiveness, requires redesign

#### Statistical Significance
- **p < 0.001**: Highly significant (***)
- **p < 0.01**: Significant (**)
- **p < 0.05**: Marginally significant (*)
- **p ≥ 0.05**: Not significant

#### VIF Multicollinearity Assessment
- **VIF < 2.5**: No multicollinearity issues
- **2.5 ≤ VIF < 5**: Moderate multicollinearity
- **5 ≤ VIF < 10**: High multicollinearity
- **VIF ≥ 10**: Severe multicollinearity, recommend variable removal

---

## Troubleshooting

### BSP Generator Issues

#### Startup Failed
```bash
# Reinstall dependencies
cd bsp-dungeon-generator-main
npm install
npm start
```

#### Upload Failed
- Ensure file is valid JSON format
- Check file size doesn't exceed limits
- Verify BSP format meets requirements

#### Score is 0
- Check if BSP file contains necessary room and connection information
- Ensure entrance and exit rooms are properly marked
- Verify game element data integrity

### Evaluation System Issues

#### Backend Startup Failed
```bash
# Check Python version and dependencies
python --version
pip install -r requirements.txt

# Ensure PYTHONPATH is correctly set
export PYTHONPATH=.
```

#### Connection Issues
- Ensure backend API is running properly (http://localhost:5001)
- Check CORS settings
- Verify network connection

### Statistical Testing Issues

#### Data Format Errors
- Verify using converted unified format data (not raw data)
- Check file paths are correct
- Ensure data conversion was completed successfully

#### Analysis Failures
- Confirm sufficient data samples for statistical analysis
- Check output directory permissions
- Verify all required Python packages are installed

### Port Conflicts

Default ports used:
- BSP project: 3000
- Flask backend: 5000/5001
- Vue frontend: 5173

If port conflicts occur, modify the port settings in corresponding configuration files.

### File Format Issues

#### Data Usage by Module

| Module | Input Data | Format Requirement |
|--------|------------|-------------------|
| Quality Evaluation Rules | Unified Format | ✅ Required |
| System Validation | Unified Format | ✅ Required |
| Statistical Analysis | Evaluation Results | ✅ Automatic |
| Raw Conversion | Raw Format | ✅ Applicable |

### Important Notes

1. **Directory Name Spelling**: Note that `covnert` is not `convert` (maintain consistency)
2. **File Correspondence**: Ensure converted data and evaluation reports correspond one-to-one
3. **Path Handling**: Use absolute paths to avoid confusion
4. **Dependencies**: Install all required packages: `pip install numpy pandas scipy matplotlib seaborn networkx scikit-learn statsmodels`

---

**Remember: Statistical Testing = Converted Data. This is key to ensuring result validity!**

For additional support, refer to individual module documentation or create an issue in the project repository.