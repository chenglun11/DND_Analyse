from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from src.schema import UnifiedDungeonFormat
from src.spatial_inference import auto_infer_connections

class BaseAdapter(ABC):
    """
    所有适配器插件的抽象基类 (接口)。
    每个适配器都必须继承此类并实现其所有抽象方法。
    """
    
    @property
    @abstractmethod
    def format_name(self) -> str:
        """
        返回此适配器支持的格式的唯一名称 (例如 'watabou_dungeon')。
        """
        pass

    @abstractmethod
    def detect(self, data: Dict[str, Any]) -> bool:
        """
        检测给定的数据是否属于此适配器支持的格式。
        
        :param data: 解析后的JSON数据 (字典格式)。
        :return: 如果是此格式，返回 True，否则返回 False。
        """
        pass

    @abstractmethod
    def convert(self, data: Dict[str, Any]) -> Optional[UnifiedDungeonFormat]:
        """
        将源数据转换为统一的地牢格式 (UnifiedDungeonFormat)。
        
        :param data: 解析后的JSON数据 (字典格式)。
        :return: 一个 UnifiedDungeonFormat 数据对象，如果转换失败则返回 None。
        """
        pass
    
    def convert_with_inference(self, data: Dict[str, Any], enable_spatial_inference: bool = True, adjacency_threshold: float = 1.0) -> Optional[UnifiedDungeonFormat]:
        """
        转换数据并自动应用空间推断补全连接信息。
        
        :param data: 解析后的JSON数据 (字典格式)。
        :param enable_spatial_inference: 是否启用空间推断。
        :param adjacency_threshold: 邻接判定阈值。
        :return: 一个 UnifiedDungeonFormat 数据对象，如果转换失败则返回 None。
        """
        # 先进行基本转换
        unified_data = self.convert(data)
        if not unified_data:
            return None
        
        # 如果启用空间推断，则自动补全连接信息
        if enable_spatial_inference:
            enhanced_data = auto_infer_connections(unified_data.to_dict(), adjacency_threshold)
            # 将增强后的数据重新转换为UnifiedDungeonFormat
            return UnifiedDungeonFormat.from_dict(enhanced_data)
        
        return unified_data 