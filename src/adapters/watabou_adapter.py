import logging
from typing import Dict, Any, Optional
import json
from typing import Optional
import click
from loguru import logger

from src.adapters.base import BaseAdapter
from src.schema import UnifiedDungeonFormat

logger = logging.getLogger(__name__)

class WatabouAdapter(BaseAdapter):
    """适配 Watabou 地牢生成器格式。"""
    
    @property
    def format_name(self) -> str:
        return "watabou_dungeon"

    def detect(self, data: Dict[str, Any]) -> bool:
        """检测是否为 Watabou 格式。"""
        # 新版 Watabou 格式
        if 'rects' in data and 'doors' in data and 'title' in data and 'version' in data:
            return True
        # 旧版 Watabou 格式 (为了兼容)
        if 'dungeon' in data and 'rooms' in data.get('dungeon', {}):
            return True
        return False

    def convert(self, data: Dict[str, Any]) -> Optional[UnifiedDungeonFormat]:
        """将 Watabou 格式数据转换为统一格式。"""
        try:
            unified = UnifiedDungeonFormat(
                name=data.get('title', 'Watabou Dungeon'),
                author='Watabou Generator',
                description=data.get('story', ''),
                grid={"type": "square", "size": 5, "unit": "ft"}
            )

            rects = data.get('rects', [])
            notes = data.get('notes', [])
            raw_doors = data.get('doors', [])

            if not rects:
                unified.levels = [{"id": "level_1", "name": "Main Level", "map": {"width": 0, "height": 0}, "rooms": [], "doors": []}]
                return unified

            min_x = min(r['x'] for r in rects)
            min_y = min(r['y'] for r in rects)
            max_x = max(r['x'] + r['w'] for r in rects)
            max_y = max(r['y'] + r['h'] for r in rects)

            # UNIFIED NODE CREATION
            all_nodes = []
            rect_to_notes = {idx: [] for idx in range(len(rects))}
            room_rect_indices = set()
            for note in notes:
                pos = note.get('pos')
                if not pos: continue
                for idx, rect in enumerate(rects):
                    if (rect['x'] <= pos.get('x', -999) < rect['x'] + rect['w'] and
                        rect['y'] <= pos.get('y', -999) < rect['y'] + rect['h']):
                        room_rect_indices.add(idx)
                        rect_to_notes[idx].append(note)
                        break

            for idx, rect in enumerate(rects):
                node = {
                    "id": f"rect_{idx}",
                    "shape": "rectangle",
                    "position": {"x": rect['x'], "y": rect['y']},
                    "size": {"width": rect['w'], "height": rect['h']},
                }
                if idx in room_rect_indices:
                    notes_in_room = rect_to_notes.get(idx, [])
                    description = "\\n".join([n['text'] for n in notes_in_room])
                    room_name = f"room_{notes_in_room[0]['ref']}" if notes_in_room and 'ref' in notes_in_room[0] else f"Area {idx}"
                    node.update({"name": room_name, "description": description, "is_room": True})
                else:
                    node.update({"name": f"Corridor {idx}", "is_corridor": True})
                all_nodes.append(node)

            doors = [{"id": f"door_{i}", "position": door_data} for i, door_data in enumerate(raw_doors)]
            
            # UNIFIED CONNECTION GENERATION
            connections = []
            for door in doors:
                door_pos = door['position']
                door_x, door_y = door_pos.get('x', 0), door_pos.get('y', 0)
                
                connected_nodes_ids = []
                for node in all_nodes:
                    pos, size = node['position'], node['size']
                    x, y, w, h = pos['x'], pos['y'], size['width'], size['height']

                    # 使用"膨胀矩形"法进行更鲁棒的检测
                    # 如果一个门的中心点在一个矩形的轻微膨胀区域内，
                    # 并且不在原始矩形内部，我们就认为它与该矩形相连。
                    padding = 0.1 # 膨胀量
                    
                    is_inside_original = (x < door_x < x + w) and (y < door_y < y + h)
                    is_inside_padded = (
                        (x - padding <= door_x <= x + w + padding) and
                        (y - padding <= door_y <= y + h + padding)
                    )

                    if is_inside_padded and not is_inside_original:
                        connected_nodes_ids.append(node['id'])

                # 移除重复项
                connected_nodes_ids = list(set(connected_nodes_ids))

                # 一个门通常只连接两个区域。如果检测到多于两个，
                # 我们只取前两个，这是一个简化处理，但在大多数情况下是有效的。
                # 或者，我们可以创建所有可能的配对，这取决于我们期望的地图复杂性。
                # 目前，我们维持之前的逻辑，连接所有检测到的节点对。
                if len(connected_nodes_ids) >= 2:
                    for j in range(len(connected_nodes_ids)):
                        for k in range(j + 1, len(connected_nodes_ids)):
                            connections.append({
                                "from_room": connected_nodes_ids[j],
                                "to_room": connected_nodes_ids[k],
                                "door_id": door['id']
                            })
            
            # 提取游戏元素
            game_elements = []
            
            # 从dungeon描述中提取游戏元素
            dungeon_description = data.get('story', '').lower()
            if dungeon_description:
                # 在dungeon中心放置游戏元素
                dungeon_center_x = (min_x + max_x) / 2
                dungeon_center_y = (min_y + max_y) / 2
                
                # 扩展的boss关键词，包含更多boss类型
                boss_keywords = ['boss', 'dragon', 'lich', 'king', 'queen', 'emperor', 'lord', 'master', 'commander', 'chieftain', 'leader', 'titan', 'general']
                monster_keywords = ['undead', 'monster', 'creature', 'wyrm', 'beast', 'fiend', 'demon', 'ghost', 'zombie', 'sphinx', 'ant', 'wolf']
                treasure_keywords = ['gold', 'treasure', 'chest', 'key', 'coin', 'gem', 'jewel', 'loot', 'wealth', 'valuable', 'artifacts']
                
                # 优先级判断：Boss > Monster > Treasure
                if any(keyword in dungeon_description for keyword in boss_keywords):
                    game_elements.append({
                        "id": f"boss_{len(game_elements)}",
                        "name": "Boss",
                        "type": "boss",
                        "position": {"x": dungeon_center_x, "y": dungeon_center_y},
                        "description": "Powerful enemy"
                    })
                elif any(keyword in dungeon_description for keyword in monster_keywords):
                    game_elements.append({
                        "id": f"monster_{len(game_elements)}",
                        "name": "Monster",
                        "type": "monster",
                        "position": {"x": dungeon_center_x, "y": dungeon_center_y},
                        "description": "Dangerous creature"
                    })
                elif any(keyword in dungeon_description for keyword in treasure_keywords):
                    game_elements.append({
                        "id": f"treasure_{len(game_elements)}",
                        "name": "Treasure",
                        "type": "treasure",
                        "position": {"x": dungeon_center_x, "y": dungeon_center_y},
                        "description": "Contains treasure"
                    })
            
            # 从notes中提取游戏元素 - 每个note都作为独立的game_element
            for i, note in enumerate(notes):
                note_text = note.get('text', '')
                note_pos = note.get('pos', {})
                note_ref = note.get('ref', '')
                if not note_pos:
                    continue
                
                # 更鲁棒的类型推断：基于note的语义和上下文
                note_lower = note_text.lower()
                
                # 1. 检查是否包含物品/宝藏相关词汇
                treasure_keywords = ['gold', 'treasure', 'chest', 'key', 'coin', 'gem', 'jewel', 'loot', 'wealth', 'valuable']
                is_treasure = any(keyword in note_lower for keyword in treasure_keywords)
                
                # 2. 检查是否包含生物/敌人相关词汇
                monster_keywords = ['undead', 'monster', 'creature', 'wyrm', 'dragon', 'beast', 'fiend', 'demon', 'ghost', 'zombie']
                is_monster = any(keyword in note_lower for keyword in monster_keywords)
                
                # 3. 检查是否包含boss相关词汇
                boss_keywords = ['boss', 'dragon', 'lich', 'king', 'queen', 'emperor', 'lord', 'master', 'commander', 'chieftain', 'leader', 'titan', 'general']
                is_boss = any(keyword in note_lower for keyword in boss_keywords)
                
                # 4. 检查是否包含陷阱/机关相关词汇
                trap_keywords = ['alarm', 'trap', 'trigger', 'pressure', 'switch', 'mechanism', 'device', 'sounds']
                is_trap = any(keyword in note_lower for keyword in trap_keywords)
                
                # 5. 检查是否包含尸体/死亡相关词汇
                corpse_keywords = ['corpse', 'body', 'dead', 'skeleton', 'remains', 'cadaver', 'corpse of']
                is_corpse = any(keyword in note_lower for keyword in corpse_keywords)
                
                # 6. 检查是否包含门/入口相关词汇
                gate_keywords = ['gate', 'door', 'entrance', 'portal', 'exit', 'passage', 'keyhole']
                is_gate = any(keyword in note_lower for keyword in gate_keywords)
                
                # 7. 检查是否包含书籍/知识相关词汇
                book_keywords = ['book', 'scroll', 'tome', 'grimoire', 'spellbook', 'lectern', 'legendary']
                is_book = any(keyword in note_lower for keyword in book_keywords)
                
                # 8. 动作词分析 - 更智能的推断
                action_words = {
                    'treasure': ['contains', 'holds', 'with', 'inside', 'basket'],
                    'trap': ['sounds', 'when opened', 'triggered', 'activated'],
                    'monster': ['made its home', 'lives', 'dwells', 'inhabits'],
                    'gate': ['on the wall', 'northern wall', 'southern wall', 'eastern wall', 'western wall']
                }
                
                # 检查动作词
                for action_type, action_list in action_words.items():
                    if any(action in note_lower for action in action_list):
                        if action_type == 'treasure':
                            is_treasure = True
                        elif action_type == 'trap':
                            is_trap = True
                        elif action_type == 'monster':
                            is_monster = True
                        elif action_type == 'gate':
                            is_gate = True
                
                # 优先级判断：Boss > Monster > Trap > Treasure > Special
                if is_boss:
                    elem_type = 'boss'
                    elem_name = 'Boss'
                elif is_monster:
                    elem_type = 'monster'
                    elem_name = 'Monster'
                elif is_trap:
                    elem_type = 'special'
                    elem_name = 'Trap'
                elif is_treasure:
                    elem_type = 'treasure'
                    elem_name = 'Treasure'
                elif is_corpse:
                    elem_type = 'special'
                    elem_name = 'Corpse'
                elif is_gate:
                    elem_type = 'special'
                    elem_name = 'Gate'
                elif is_book:
                    elem_type = 'special'
                    elem_name = 'Book'
                else:
                    # 默认作为特殊物品处理
                    elem_type = 'special'
                    elem_name = 'Special'
                
                # 使用原始note文本作为描述，保持完整性
                elem_desc = note_text
                
                game_elements.append({
                    "id": f"{elem_type}_{len(game_elements)}",
                    "name": elem_name,
                    "type": elem_type,
                    "position": {"x": note_pos.get('x', 0), "y": note_pos.get('y', 0)},
                    "description": elem_desc,
                    "ref": note_ref  # 保留原始引用信息
                })
            
            # FINAL STRUCTURE
            final_rooms = [node for node in all_nodes if node.get("is_room")]
            final_corridors = [node for node in all_nodes if node.get("is_corridor")]
            
            # 清理临时标志
            for node in final_rooms: del node['is_room']
            for node in final_corridors: del node['is_corridor']

            unified.levels.append({
                "id": "level_1", 
                "name": "Main Level",
                "map": {"width": max_x - min_x, "height": max_y - min_y},
                "rooms": final_rooms, 
                "doors": doors, 
                "corridors": final_corridors,
                "connections": connections,
                "game_elements": game_elements
            })
            
            return unified
        except Exception as e:
            logger.error(f"Error converting Watabou format: {e}", exc_info=True)
            return None 