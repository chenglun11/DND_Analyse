# FI Test Dataset Selection

This directory contains 25 carefully selected samples from the FI (Feature-based Individual) populations for testing purposes.

## Selection Criteria

The samples were chosen to ensure:
- **Population Diversity**: Samples from all 3 available populations (262143, 262144, 524288)
- **Feasibility Mix**: Both feasible and infeasible individuals included
- **Quality Range**: Different fitness levels and feature characteristics
- **Constraint Patterns**: Various constraint violation patterns for infeasible samples

## Sample Distribution

### Population 262143 (9 samples)
- **Feasible (6)**: ind_65, ind_80, ind_90, ind_100, ind_130, ind_170
  - High fitness range (~0.81-0.94)
  - Various feature value combinations
- **Infeasible (3)**: ind_48, ind_64, ind_100  
  - Constraint violations (mainly narrow passages)
  - High raw fitness but constraint penalties

### Population 262144 (8 samples)
- **Feasible (6)**: ind_65, ind_75, ind_90, ind_105, ind_140, ind_180
  - Moderate fitness (~0.69)
  - Different feature characteristics
- **Infeasible (2)**: ind_65, ind_100
  - Area margin constraint violations mainly
  - Lower fitness due to penalties

### Population 524288 (8 samples)  
- **Feasible (6)**: ind_65, ind_85, ind_90, ind_105, ind_120, ind_150
  - Unknown fitness distribution (no stats file)
  - Diverse individual IDs for coverage
- **Infeasible (2)**: ind_70, ind_100
  - Various constraint patterns

## Usage

These 25 samples provide a representative test set for:
- Algorithm validation across different population characteristics
- Constraint handling evaluation
- Feature space coverage assessment
- Quality metric testing

**Total: 25 samples (18 feasible, 7 infeasible)**
- **Ratio**: ~72% feasible, ~28% infeasible
- **Coverage**: All 3 FI populations represented
- **Quality**: Mixed fitness levels and feature characteristics