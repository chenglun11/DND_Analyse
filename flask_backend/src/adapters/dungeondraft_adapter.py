import logging
from typing import Dict, Any, Optional

from src.adapters.base import BaseAdapter
from src.schema import UnifiedDungeonFormat

logger = logging.getLogger(__name__)

class DungeonDraftAdapter(BaseAdapter):
    """适配 DungeonDraft 格式。"""

    @property
    def format_name(self) -> str:
        return "dungeondraft"

    def detect(self, data: Dict[str, Any]) -> bool:
        """检测是否为 DungeonDraft 格式。"""
        return 'version' in data and 'elements' in data

    def convert(self, data: Dict[str, Any]) -> Optional[UnifiedDungeonFormat]:
        """将 DungeonDraft 格式数据转换为统一格式。"""
        try:
            unified = UnifiedDungeonFormat(
                name=data.get('name', 'DungeonDraft Map'),
                author=data.get('author', 'DungeonDraft'),
                description=data.get('description', ''),
                grid={
                    "type": "square",
                    "size": data.get('grid_size', 5),
                    "unit": "ft"
                }
            )

            elements = data.get('elements', [])
            rooms, doors, corridors = [], [], []
            
            for element in elements:
                element_type = element.get('type')
                if element_type == 'room':
                    rooms.append(element)
                elif element_type == 'door':
                    doors.append(element)
                elif element_type == 'corridor':
                    corridors.append(element)
                    # 将走廊也作为房间处理
                    corridor_room = {
                        "id": element.get('id', ''),
                        "name": f"走廊 {element.get('id', '')}",
                        "description": "连接房间的走廊",
                        "shape": "corridor",
                        "position": element.get('path', [{}])[0] if element.get('path') else {},
                        "size": {
                            "width": element.get('width', 3),
                            "height": element.get('width', 3)
                        }
                    }
                    rooms.append(corridor_room)

            level = {
                "id": "level_1",
                "name": "主层",
                "map": {
                    "width": data.get('width', 50),
                    "height": data.get('height', 50)
                },
                "rooms": rooms,
                "doors": doors,
                "corridors": corridors,
                "connections": self._generate_connections(doors, corridors)
            }

            unified.levels.append(level)
            return unified
        except Exception as e:
            logger.error(f"转换 DungeonDraft 格式时出错: {e}")
            return None

    def _generate_connections(self, doors: list, corridors: list) -> list:
        """从doors和corridors生成connections"""
        connections = []
        
        # 从doors生成连接
        for door in doors:
            connects = door.get('connects', [])
            if len(connects) >= 2:
                # 找到两个房间之间的连接
                for i in range(len(connects)):
                    for j in range(i + 1, len(connects)):
                        room1 = connects[i]
                        room2 = connects[j]
                        connections.append({
                            "id": f"conn_{len(connections)}",
                            "from_room": room1,
                            "to_room": room2,
                            "type": "door",
                            "position": door.get('position', {})
                        })
        
        return connections 