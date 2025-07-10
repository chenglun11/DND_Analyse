import abc

class BaseQualityRule(abc.ABC):
    @abc.abstractmethod
    def evaluate(self, dungeon_data):
        """
        输入统一格式地图数据，返回分数（0-1）和详细分析
        """
        pass

    @property
    @abc.abstractmethod
    def name(self):
        pass

    @property
    @abc.abstractmethod
    def description(self):
        pass 