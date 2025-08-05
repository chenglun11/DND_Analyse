import logging
import json
import os
import sys
import pkgutil
import importlib
from typing import Dict, Any, Optional, List
from pathlib import Path

from .schema import UnifiedDungeonFormat, identify_entrance_exit
from .spatial_inference import auto_infer_connections

logger = logging.getLogger(__name__)

class AdapterManager:
    """适配器管理器，负责加载和管理各种格式的适配器"""
    
    def __init__(self):
        self.adapters = {}
        self._load_adapters()
    
    def _load_adapters(self):
        """动态加载所有适配器"""
        adapters_dir = Path(__file__).parent / "adapters"
        
        try:
            for _, module_name, _ in pkgutil.iter_modules([str(adapters_dir)]):
                if module_name == "__init__":
                    continue
                    
                try:
                    module = importlib.import_module(f"src.adapters.{module_name}")
                    
                    # 查找适配器类
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (hasattr(attr, '__bases__') and 
                            any('BaseAdapter' in str(base) for base in attr.__bases__) and
                            attr_name != 'BaseAdapter'):
                            
                            adapter_instance = attr()
                            format_name = adapter_instance.format_name
                            self.adapters[format_name] = adapter_instance
                            logger.info(f"Loaded adapter: {format_name}")
                            
                except Exception as e:
                    logger.warning(f"Failed to load adapter {module_name}: {e}")
                    
        except Exception as e:
            logger.error(f"Error loading adapters: {e}")
    
    def get_supported_formats(self) -> List[str]:
        """获取所有支持的格式名称"""
        return list(self.adapters.keys())
    
    def detect_format(self, data: Dict[str, Any]) -> Optional[str]:
        """自动检测数据格式"""
        # 首先检查是否已经是统一格式
        if self._is_unified_format(data):
            return "unified"
        
        # 然后检查其他格式
        for format_name, adapter in self.adapters.items():
            try:
                if adapter.detect(data):
                    return format_name
            except Exception as e:
                logger.warning(f"Error detecting format {format_name}: {e}")
                continue
        return None
    
    def _is_unified_format(self, data: Dict[str, Any]) -> bool:
        """检查是否为统一格式"""
        # 统一格式的特征：包含header和levels
        if 'header' in data and 'levels' in data:
            header = data['header']
            if (isinstance(header, dict) and 
                'schemaName' in header and 
                header.get('schemaName') == 'dnd-dungeon-unified'):
                return True
        return False
    
    def convert(self, data: Dict[str, Any], format_name: Optional[str] = None, 
                enable_spatial_inference: bool = True, adjacency_threshold: float = 1.0) -> Optional[Dict[str, Any]]:
        """
        转换数据到统一格式
        
        Args:
            data: 源数据
            format_name: 指定格式名称，如果为None则自动检测
            enable_spatial_inference: 是否启用空间推断
            adjacency_threshold: 邻接判定阈值
            
        Returns:
            转换后的统一格式数据，如果转换失败返回None
        """
        try:
            # 1. 格式检测
            if format_name is None:
                format_name = self.detect_format(data)
                if format_name is None:
                    logger.error("Unable to detect data format")
                    return None
            
            # 2. 数据转换
            if format_name == "unified":
                # 如果已经是统一格式，直接使用
                unified_data = data
                logger.info("Data is already in unified format")
            elif format_name in self.adapters:
                # 使用适配器转换
                adapter = self.adapters[format_name]
                unified_data = adapter.convert(data)
                if unified_data is None:
                    logger.error(f"Failed to convert format {format_name}")
                    return None
            else:
                logger.error(f"Unsupported format: {format_name}")
                return None
            
            # 3. 空间推断（如果需要）
            if enable_spatial_inference:
                # 保证传递的是dict
                if isinstance(unified_data, UnifiedDungeonFormat):
                    enhanced_data = auto_infer_connections(unified_data.to_dict(), adjacency_threshold)
                else:
                    enhanced_data = auto_infer_connections(unified_data, adjacency_threshold)
                if enhanced_data != unified_data:
                    logger.info("Spatial inference completed, automatically complete connection information")
                    unified_data = enhanced_data
            
            # 4. 入口出口识别
            if isinstance(unified_data, UnifiedDungeonFormat):
                unified_data = identify_entrance_exit(unified_data.to_dict())
            else:
                unified_data = identify_entrance_exit(unified_data)
            
            # 5. 转换为字典格式
            if isinstance(unified_data, UnifiedDungeonFormat):
                return unified_data.to_dict()
            else:
                return unified_data
                
        except Exception as e:
            logger.error(f"Error occurred during conversion: {e}")
            return None 