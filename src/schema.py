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

def _analyze_room_semantics(room: Dict[str, Any]) -> Dict[str, float]:
    """
    分析房间的语义特征，返回入口/出口倾向性评分
    
    Args:
        room: 房间数据
        
    Returns:
        包含入口倾向性和出口倾向性的字典
    """
    room_name = room.get('name', '').lower()
    room_desc = room.get('description', '').lower()
    
    entrance_score = 0.0
    exit_score = 0.0
    
    # 入口特征分析
    entrance_features = {
        'gate': 0.8, 'door': 0.7, 'entrance': 1.0, 'entry': 1.0,
        'portal': 0.9, 'keyhole': 0.6, 'iron door': 0.8, 'great door': 0.8,
        '入口': 1.0, '进口': 1.0, '大门': 0.9, '门厅': 0.8, '大厅': 0.6
    }
    
    # 出口特征分析
    exit_features = {
        'exit': 1.0, '出口': 1.0, '终点': 0.9, 'boss': 0.8, 'boss room': 0.9,
        'final': 0.8, 'end': 0.7, 'treasure': 0.6, 'gold': 0.5, 'magic': 0.6,
        'legendary': 0.7, 'spellbook': 0.8, 'tome': 0.7, 'chest': 0.5,
        'corpse': 0.3, 'dead': 0.3, 'skeleton': 0.3  # 负面特征
    }
    
    # 计算入口分数
    for feature, weight in entrance_features.items():
        if feature in room_name or feature in room_desc:
            entrance_score += weight
    
    # 计算出口分数
    for feature, weight in exit_features.items():
        if feature in room_name or feature in room_desc:
            exit_score += weight
    
    # 特殊规则：如果房间描述包含"undead wyrm"或类似怪物，可能是出口
    monster_keywords = ['undead wyrm', 'dragon', 'boss', 'monster', 'creature']
    if any(keyword in room_desc for keyword in monster_keywords):
        exit_score += 0.5
    
    # 特殊规则：如果房间描述包含"key"或"pedestal"，可能是重要房间
    key_keywords = ['key', 'pedestal', 'altar', 'shrine']
    if any(keyword in room_desc for keyword in key_keywords):
        exit_score += 0.3
    
    return {'entrance_score': entrance_score, 'exit_score': exit_score}

def identify_entrance_exit(dungeon_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    （已禁用）入口/出口自动识别逻辑。直接返回原始数据，不做任何处理。
    """
    return dungeon_data 