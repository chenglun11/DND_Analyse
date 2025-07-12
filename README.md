# Dungeon Adapter

一个基于科学理论的地牢设计质量评估和格式适配系统，将地牢设计从艺术创作转化为可量化、可评估、可改进的工程过程。

## 🎯 项目特色

- **科学化评估**: 基于学术理论的多维度质量评估体系
- **标准化格式**: 统一的地牢数据格式，支持多种格式转换
- **实用化工具**: 提供快速评估脚本和设计指导
- **可视化分析**: 支持地牢结构的可视化展示

## 📚 核心文档

### 方法论文档
- **[完整方法论](dungeon_adapter_methodology.md)**: 详细的技术架构、评估理论和算法实现
- **[实用指南](dungeon_design_practical_guide.md)**: 具体的设计原则、操作指导和最佳实践
- **[视觉平衡理论](aesthetic_balance_theory.md)**: 基于格式塔心理学的美学评估理论

### 评估指标
- **[质量指标总结](quality_metrics_summary.md)**: 7个核心评估指标的详细说明
- **[基准测试标准](benchmark_standards.py)**: 标准测试集和基准定义

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 快速评估
```bash
# 基本评估
python quick_assess.py dungeon.json

# 详细评估
python quick_assess.py dungeon.json --detailed

# 生成可视化
python quick_assess.py dungeon.json --visualize
```

### 批量评估
```bash
python src/batch_assess.py --input input_dir/ --output results/
```

## 📊 评估体系

### 三维评估框架
- **结构类 (40%)**: 可达性、门分布、度方差、环路比例
- **游戏性类 (40%)**: 路径多样性、宝藏怪物分布、死胡同比例
- **美术类 (20%)**: 视觉平衡

### 理论基础
- **游戏设计理论**: Schell (2008), Fullerton (2014)
- **空间认知理论**: Lynch (1960), Kaplan & Kaplan (1982)
- **格式塔心理学**: Wertheimer (1923), Arnheim (1954)
- **网络科学**: Newman (2010), Barabási (2016)

## 🛠️ 主要功能

### 格式适配
- **Watabou**: 程序生成地牢格式
- **DungeonDraft**: 手动设计工具格式
- **One Page Dungeon**: 创意地牢格式
- **FiMapElites**: 进化算法生成格式

### 质量评估
- **可达性分析**: 基于图论的连通性评估
- **门分布评估**: 基于空间拓扑学的合理性分析
- **路径多样性**: 基于选择理论的探索性评估
- **视觉平衡**: 基于格式塔原则的美学评估

### 空间推断
- **自动连接推断**: 基于空间邻接关系的连接补全
- **门位置推断**: 基于建筑空间设计原则的位置确定

## 📈 使用示例

### 评估结果示例
```
📊 地牢质量评估报告
文件: dungeon.json
总体评分: 0.750 (B)

📈 分类评分:
  结构类: 0.840
  游戏性类: 0.720
  美术类: 0.650

💡 改进建议:
  1. 增加路径多样性，提供更多探索选择
  2. 优化宝藏和怪物分布，确保平衡密度
  3. 减少死胡同，改善探索流程
```

### 设计指导
```python
# 检查可达性
def check_accessibility(dungeon):
    reachable = bfs_from_entrance(dungeon)
    accessibility = len(reachable) / total_rooms
    
    if accessibility < 0.6:
        add_missing_connections(dungeon)
    elif accessibility > 0.95:
        add_exploration_branches(dungeon)

# 优化门分布
def optimize_door_distribution(dungeon):
    door_counts = count_doors_per_room(dungeon)
    mean_doors = np.mean(door_counts)
    
    if mean_doors < 1.5:
        add_connections(dungeon)
    elif mean_doors > 3.0:
        simplify_connections(dungeon)
```

## 🎮 设计原则

### 平衡性原则
- **探索与挑战**: 在自由探索和适度挑战间找到平衡
- **复杂度与可理解性**: 保持足够的复杂度但确保玩家能够理解
- **奖励与风险**: 高风险区域提供高回报，低风险区域提供基础资源

### 连通性原则
- **避免孤立**: 确保所有房间都可以到达
- **适度连接**: 每个房间1.5-3个门
- **层次结构**: 主要路径清晰，次要路径提供探索选择

### 美学原则
- **视觉平衡**: 房间大小和位置分布均匀
- **主题一致**: 保持设计风格的一致性
- **焦点突出**: 重要区域（如Boss房间）位置突出

## 📋 项目结构

```
dungeon-adapter/
├── src/                          # 核心源代码
│   ├── adapters/                 # 格式适配器
│   ├── quality_rules/            # 质量评估规则
│   ├── quality_assessor.py       # 质量评估器
│   ├── spatial_inference.py      # 空间推断引擎
│   └── visualizer.py             # 可视化引擎
├── tests/                        # 测试文件
├── output/                       # 输出结果
├── samples/                      # 样例数据
├── docs/                         # 文档
└── scripts/                      # 实用脚本
```

## 🔬 基准测试

### 标准测试集
- **程序生成地牢**: Watabou (100个), DungeonDraft (50个)
- **手动设计地牢**: One Page Dungeon (30个), 经典模块 (20个)
- **社区创作**: 高质量社区作品 (50个)

### 质量基准
- **A级 (0.8-1.0)**: 优秀设计
- **B级 (0.6-0.8)**: 良好设计
- **C级 (0.4-0.6)**: 一般设计
- **D级 (0.2-0.4)**: 较差设计
- **F级 (0.0-0.2)**: 需要改进

## 🤝 贡献指南

### 代码贡献
1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

### 文档贡献
- 改进现有文档
- 添加新的使用示例
- 翻译文档内容

### 测试贡献
- 提供测试用例
- 报告问题和Bug
- 提供反馈和建议

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢以下理论基础的贡献者：
- **游戏设计理论**: Jesse Schell, Tracy Fullerton
- **空间认知理论**: Kevin Lynch, Stephen Kaplan
- **格式塔心理学**: Max Wertheimer, Rudolf Arnheim
- **网络科学**: Mark Newman, Albert-László Barabási

## 📞 联系方式

- **GitHub Issues**: 报告问题和请求功能
- **Discord社区**: 实时讨论和帮助
- **邮件支持**: 技术问题咨询

---

*Dungeon Adapter - 让地牢设计更科学、更高效、更有趣* 