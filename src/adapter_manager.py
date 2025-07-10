import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
import importlib

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.adapters.base import BaseAdapter

logger = logging.getLogger(__name__)

class AdapterManager:
    """
    自动发现、加载和管理所有适配器插件。
    """
    def __init__(self):
        self.adapters: Dict[str, BaseAdapter] = {}
        self._load_adapters()

    def _load_adapters(self):
        """动态加载所有适配器插件"""
        adapters_dir = Path(__file__).parent / "adapters"
        
        # 确保适配器目录存在
        if not adapters_dir.exists():
            logger.error(f"Adapters directory not found: {adapters_dir}")
            return
        
        # 遍历适配器目录
        for adapter_file in adapters_dir.glob("*.py"):
            if adapter_file.name in ["__init__.py", "base.py"]:
                continue
            
            try:
                # 动态导入适配器模块
                module_name = f"src.adapters.{adapter_file.stem}"
                module = importlib.import_module(module_name)
                
                # 查找适配器类
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, BaseAdapter) and 
                        attr != BaseAdapter):
                        # 实例化适配器
                        adapter = attr()
                        self.adapters[adapter.format_name] = adapter
                        logger.info(f"Loaded adapter: {adapter.format_name}")
                        break
                        
            except Exception as e:
                logger.error(f"Failed to load adapter from {adapter_file}: {e}")
        
        logger.info(f"Successfully Process {len(self.adapters)} Adapters: {list(self.adapters.keys())}")

    def detect_format(self, data: Dict[str, Any]) -> Optional[str]:
        """遍历所有适配器，找到第一个能成功检测格式的。"""
        for format_name, adapter in self.adapters.items():
            try:
                if adapter.detect(data):
                    logger.info(f"Auto Detect Format: {format_name}")
                    return format_name
            except Exception as e:
                logger.warning(f"Adapter {format_name} error when detecting: {e}")
        logger.warning("Failed to auto detect any known format.")
        return None

    def convert(self, data: Dict[str, Any], format_name: Optional[str] = None, enable_spatial_inference: bool = True, adjacency_threshold: float = 1.0) -> Optional[Dict[str, Any]]:
        """
        转换数据为统一格式
        
        Args:
            data: 源数据
            format_name: 指定格式名称（可选，会自动检测）
            enable_spatial_inference: 是否启用空间推断
            adjacency_threshold: 邻接判定阈值
            
        Returns:
            转换后的统一格式数据，失败返回None
        """
        try:
            # 确定格式
            if format_name is None:
                format_name = self.detect_format(data)
                if format_name is None:
                    logger.error("Unable to determine source file format.")
                    return None
            
            # 获取适配器
            adapter = self.adapters.get(format_name)
            if adapter is None:
                logger.error(f"Unsupported format: {format_name}")
                return None
            
            # 使用带空间推断的转换方法
            unified_data = adapter.convert_with_inference(data, enable_spatial_inference, adjacency_threshold)
            if unified_data is None:
                logger.error("Conversion failed")
                return None
            
            # 转换为字典格式
            result = unified_data.to_dict()
            
            # 记录空间推断使用情况
            if enable_spatial_inference:
                inference_used = any(level.get('connections_inferred', False) or level.get('doors_inferred', False) 
                                   for level in result.get('levels', []))
                if inference_used:
                    logger.info(f"Spatial inference applied to {format_name} format conversion")
            
            return result
            
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            return None

    def get_supported_formats(self) -> List[str]:
        """返回所有已加载的适配器格式名称列表。"""
        return list(self.adapters.keys()) 