from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

@dataclass
class UnifiedDungeonFormat:
    """统一的地牢格式数据类 (数据模型)"""
    schema_name: str = "dnd-dungeon-unified"
    schema_version: str = "1.0.0"
    name: str = "Unnamed Dungeon"
    author: str = "Adapter"
    description: str = "Converted from other formats"
    grid: Dict[str, Any] = field(default_factory=lambda: {"type": "square", "size": 5, "unit": "ft"})
    levels: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """将数据对象转换为字典，以便序列化（例如存为JSON）"""
        return {
            "header": {
                "schemaName": self.schema_name,
                "schemaVersion": self.schema_version,
                "name": self.name,
                "author": self.author,
                "description": self.description,
                "grid": self.grid
            },
            "levels": self.levels
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UnifiedDungeonFormat':
        """从字典创建UnifiedDungeonFormat对象"""
        header = data.get('header', {})
        return cls(
            schema_name=header.get('schemaName', 'dnd-dungeon-unified'),
            schema_version=header.get('schemaVersion', '1.0.0'),
            name=header.get('name', 'Unnamed Dungeon'),
            author=header.get('author', 'Adapter'),
            description=header.get('description', 'Converted from other formats'),
            grid=header.get('grid', {"type": "square", "size": 5, "unit": "ft"}),
            levels=data.get('levels', [])
        ) 