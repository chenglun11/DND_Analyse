class BaseQualityRule:
    name = "base"
    description = "基础质量评估规则"

    def evaluate(self, dungeon_data):
        """
        输入统一格式地图数据，返回分数（0-1）和详细分析
        """
        raise NotImplementedError 