from typing import Dict, Any, Optional, List
from src.adapters.base import BaseAdapter
from src.schema import UnifiedDungeonFormat
import math

class BspAdapter(BaseAdapter):
    """
    BSP地牢生成器格式的适配器
    处理来自BSP-Dungeon-Generator的JSON数据
    """
    
    @property
    def format_name(self) -> str:
        return "bsp_dungeon"
    
    def detect(self, data: Dict[str, Any]) -> bool:
        """
        检测是否为BSP格式数据
        BSP格式特征:
        方式1: 简化格式 - 包含 'rects' 和 'doors' 字段
        方式2: 完整格式 - 包含 'width', 'height', 'tree', 'layers' 字段 (实际网站生成)
        """
        # 检测简化格式
        simple_format = all(field in data for field in ['rects', 'doors'])
        
        # 检测完整格式 (实际BSP网站生成的格式)
        full_format = all(field in data for field in ['width', 'height', 'tree', 'layers'])
        
        return simple_format or full_format
    
    def convert(self, data: Dict[str, Any]) -> Optional[UnifiedDungeonFormat]:
        """
        将BSP格式转换为统一格式
        支持简化格式和完整格式
        """
        try:
            # 检测格式类型
            is_full_format = all(field in data for field in ['width', 'height', 'tree', 'layers'])
            
            if is_full_format:
                return self._convert_full_format(data)
            else:
                return self._convert_simple_format(data)
                
        except Exception as e:
            print(f"BSP转换错误: {e}")
            return None
    
    def _convert_simple_format(self, data: Dict[str, Any]) -> Optional[UnifiedDungeonFormat]:
        """
        转换简化格式（包含rects, doors等）
        """
        # 创建统一格式的基础结构
        unified_format = UnifiedDungeonFormat(
            name=data.get('title', 'BSP Generated Dungeon'),
            author='BSP-Dungeon-Generator',
            description=data.get('story', 'Generated using BSP algorithm')
        )
        
        # 创建第一层级
        level_data = {
            "id": "level_1",
            "name": "Ground Floor",
            "rooms": [],
            "connections": [],
            "game_elements": []
        }
        
        # 转换房间 (rects)
        rooms = self._convert_rooms(data.get('rects', []))
        level_data["rooms"] = rooms
        
        # 转换门为连接 (doors)
        connections = self._convert_doors_to_connections(data.get('doors', []), rooms)
        
        # 补充连接以确保所有房间都可达
        connections = self._ensure_connectivity(connections, rooms)
        
        level_data["connections"] = connections
        
        # 转换游戏元素 (notes, columns等)
        game_elements = self._convert_game_elements(data)
        level_data["game_elements"] = game_elements
        
        unified_format.levels = [level_data]
        
        return unified_format
    
    def _convert_full_format(self, data: Dict[str, Any]) -> Optional[UnifiedDungeonFormat]:
        """
        转换完整格式（包含width, height, tree, layers）- 实际网站生成格式
        """
        # 创建统一格式的基础结构
        unified_format = UnifiedDungeonFormat(
            name="BSP Generated Dungeon",
            author='BSP-Dungeon-Generator', 
            description='Generated using BSP algorithm from website'
        )
        
        # 创建第一层级
        level_data = {
            "id": "level_1",
            "name": "Ground Floor",
            "rooms": [],
            "connections": [],
            "game_elements": []
        }
        
        # 从BSP树提取房间信息
        rooms = self._extract_rooms_from_tree(data.get('tree', {}))
        level_data["rooms"] = rooms
        
        # 从BSP树提取连接信息
        connections = self._extract_connections_from_tree(data.get('tree', {}))
        
        # 补充连接以确保连通性
        connections = self._ensure_connectivity(connections, rooms)
        level_data["connections"] = connections
        
        # 从layers中提取游戏元素
        game_elements = self._extract_game_elements_from_layers(data.get('layers', {}))
        level_data["game_elements"] = game_elements
        
        unified_format.levels = [level_data]
        
        return unified_format
    
    def _convert_rooms(self, rects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        转换BSP的rects为统一格式的房间
        """
        rooms = []
        
        for i, rect in enumerate(rects):
            room_id = f"room_{i}"
            
            # 判断房间类型
            room_type = "room"  # 默认类型
            if rect.get('rotunda', False):
                room_type = "special"  # 圆形房间为特殊房间
            elif rect.get('ending', False):
                room_type = "boss"  # 结束房间为boss房间
            
            room_data = {
                "id": room_id,
                "name": f"Room {i+1}",
                "type": room_type,
                "position": {
                    "x": rect.get('x', 0),
                    "y": rect.get('y', 0)
                },
                "size": {
                    "width": rect.get('w', 1),
                    "height": rect.get('h', 1)
                },
                "properties": {}
            }
            
            # 添加特殊属性
            if rect.get('rotunda', False):
                room_data["properties"]["shape"] = "circular"
            if rect.get('ending', False):
                room_data["properties"]["is_ending"] = True
                room_data["is_exit"] = True
            
            # 第一个房间设为入口
            if i == 0:
                room_data["is_entrance"] = True
            
            rooms.append(room_data)
        
        return rooms
    
    def _convert_doors_to_connections(self, doors: List[Dict[str, Any]], rooms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        将BSP的门转换为房间连接
        """
        connections = []
        
        # 为每个门找到它连接的房间
        for i, door in enumerate(doors):
            door_x = door.get('x', 0)
            door_y = door.get('y', 0)
            
            # 找到门附近的房间
            connected_rooms = self._find_rooms_near_door(door_x, door_y, rooms)
            
            if len(connected_rooms) >= 2:
                # 创建连接
                connection = {
                    "id": f"connection_{i}",
                    "from_room": connected_rooms[0]["id"],
                    "to_room": connected_rooms[1]["id"],
                    "type": self._get_door_type(door.get('type', 0)),
                    "position": {
                        "x": door_x,
                        "y": door_y
                    }
                }
                connections.append(connection)
        
        return connections
    
    def _find_rooms_near_door(self, door_x: float, door_y: float, rooms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        找到门附近的房间
        """
        near_rooms = []
        
        for room in rooms:
            pos = room["position"]
            size = room["size"]
            
            # 检查门是否在房间边界上或附近
            room_left = pos["x"]
            room_right = pos["x"] + size["width"]
            room_top = pos["y"]
            room_bottom = pos["y"] + size["height"]
            
            # 门在房间边界附近的容差范围
            tolerance = 2.0  # 增加容差范围
            
            # 检查门是否在房间的扩展边界内
            extended_left = room_left - tolerance
            extended_right = room_right + tolerance
            extended_top = room_top - tolerance
            extended_bottom = room_bottom + tolerance
            
            if extended_left <= door_x <= extended_right and extended_top <= door_y <= extended_bottom:
                near_rooms.append(room)
        
        return near_rooms
    
    def _create_basic_connections(self, rooms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        为没有门数据的情况创建基础连接
        基于房间的空间位置创建邻接连接
        """
        connections = []
        
        # 按位置排序房间
        sorted_rooms = sorted(rooms, key=lambda r: (r["position"]["x"], r["position"]["y"]))
        
        # 为相邻房间创建连接
        for i in range(len(sorted_rooms) - 1):
            room1 = sorted_rooms[i]
            room2 = sorted_rooms[i + 1]
            
            connection = {
                "id": f"connection_{i}",
                "from_room": room1["id"],
                "to_room": room2["id"],
                "type": "corridor"
            }
            connections.append(connection)
        
        # 如果有boss房间，确保它有连接
        boss_rooms = [r for r in rooms if r.get("is_exit", False)]
        if boss_rooms and len(rooms) > 1:
            boss_room = boss_rooms[0]
            # 找到最近的非boss房间连接到boss房间
            other_rooms = [r for r in rooms if r["id"] != boss_room["id"]]
            if other_rooms:
                nearest_room = min(other_rooms, key=lambda r: 
                    abs(r["position"]["x"] - boss_room["position"]["x"]) + 
                    abs(r["position"]["y"] - boss_room["position"]["y"]))
                
                # 检查是否已有连接
                existing_connection = any(
                    (conn["from_room"] == nearest_room["id"] and conn["to_room"] == boss_room["id"]) or
                    (conn["from_room"] == boss_room["id"] and conn["to_room"] == nearest_room["id"])
                    for conn in connections
                )
                
                if not existing_connection:
                    connections.append({
                        "id": f"connection_to_boss",
                        "from_room": nearest_room["id"],
                        "to_room": boss_room["id"],
                        "type": "corridor"
                    })
        
        return connections
    
    def _ensure_connectivity(self, connections: List[Dict[str, Any]], rooms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        确保所有房间都有连接，特别是入口和出口之间有路径
        """
        if len(rooms) <= 1:
            return connections
        
        # 创建房间ID集合
        room_ids = {room["id"] for room in rooms}
        
        # 如果没有连接，创建基本连接
        if not connections:
            return self._create_basic_connections(rooms)
        
        # 检查连通性
        connected_rooms = set()
        for conn in connections:
            connected_rooms.add(conn["from_room"])
            connected_rooms.add(conn["to_room"])
        
        # 找到未连接的房间
        unconnected_rooms = room_ids - connected_rooms
        
        # 为未连接的房间添加连接
        connection_id_counter = len(connections)
        for unconnected_id in unconnected_rooms:
            # 找到最近的已连接房间
            unconnected_room = next(r for r in rooms if r["id"] == unconnected_id)
            if connected_rooms:
                connected_room_list = [r for r in rooms if r["id"] in connected_rooms]
                nearest_room = min(connected_room_list, key=lambda r: 
                    abs(r["position"]["x"] - unconnected_room["position"]["x"]) + 
                    abs(r["position"]["y"] - unconnected_room["position"]["y"]))
                
                connections.append({
                    "id": f"connection_auto_{connection_id_counter}",
                    "from_room": nearest_room["id"],
                    "to_room": unconnected_id,
                    "type": "corridor"
                })
                connected_rooms.add(unconnected_id)
                connection_id_counter += 1
        
        # 特别检查入口和出口的连通性
        entrance_rooms = [r for r in rooms if r.get("is_entrance", False)]
        exit_rooms = [r for r in rooms if r.get("is_exit", False)]
        
        if entrance_rooms and exit_rooms:
            entrance_id = entrance_rooms[0]["id"]
            exit_id = exit_rooms[0]["id"]
            
            # 检查是否存在从入口到出口的路径
            if not self._has_path(entrance_id, exit_id, connections):
                # 如果没有路径，创建直接连接或通过中间房间连接
                if len(rooms) == 2:
                    # 只有入口和出口，直接连接
                    connections.append({
                        "id": f"connection_entrance_exit",
                        "from_room": entrance_id,
                        "to_room": exit_id,
                        "type": "corridor"
                    })
                else:
                    # 确保出口房间至少有一个连接
                    exit_connected = any(
                        conn["from_room"] == exit_id or conn["to_room"] == exit_id
                        for conn in connections
                    )
                    if not exit_connected:
                        # 找到最近的房间连接到出口
                        other_rooms = [r for r in rooms if r["id"] != exit_id]
                        if other_rooms:
                            nearest_to_exit = min(other_rooms, key=lambda r: 
                                abs(r["position"]["x"] - exit_rooms[0]["position"]["x"]) + 
                                abs(r["position"]["y"] - exit_rooms[0]["position"]["y"]))
                            
                            connections.append({
                                "id": f"connection_to_exit_{connection_id_counter}",
                                "from_room": nearest_to_exit["id"],
                                "to_room": exit_id,
                                "type": "corridor"
                            })
        
        return connections
    
    def _has_path(self, start_id: str, end_id: str, connections: List[Dict[str, Any]]) -> bool:
        """
        检查两个房间之间是否存在路径（BFS）
        """
        if start_id == end_id:
            return True
        
        # 构建邻接表
        graph = {}
        for conn in connections:
            from_room = conn["from_room"]
            to_room = conn["to_room"]
            
            if from_room not in graph:
                graph[from_room] = []
            if to_room not in graph:
                graph[to_room] = []
            
            graph[from_room].append(to_room)
            graph[to_room].append(from_room)
        
        if start_id not in graph:
            return False
        
        # BFS搜索
        visited = set()
        queue = [start_id]
        visited.add(start_id)
        
        while queue:
            current = queue.pop(0)
            if current == end_id:
                return True
            
            for neighbor in graph.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        return False
    
    def _get_door_type(self, door_type_code: int) -> str:
        """
        将BSP的门类型代码转换为描述性类型
        """
        door_types = {
            0: "normal",
            1: "locked", 
            2: "secret",
            3: "entrance",
            4: "treasure",
            5: "trap",
            6: "magic",
            8: "portal",
            9: "open"
        }
        return door_types.get(door_type_code, "normal")
    
    def _convert_game_elements(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        转换游戏元素 (notes, columns等)
        """
        elements = []
        
        # 转换notes为物品/NPC
        notes = data.get('notes', [])
        for i, note in enumerate(notes):
            element = {
                "id": f"note_{i}",
                "type": self._classify_note(note.get('text', '')),
                "name": f"Item {i+1}",
                "description": note.get('text', ''),
                "position": note.get('pos', {})
            }
            elements.append(element)
        
        # 转换columns为环境元素
        columns = data.get('columns', [])
        for i, column in enumerate(columns):
            element = {
                "id": f"column_{i}",
                "type": "obstacle",
                "name": "Column",
                "description": "A structural column",
                "position": {
                    "x": column.get('x', 0),
                    "y": column.get('y', 0)
                }
            }
            elements.append(element)
        
        # 转换water为环境元素
        water_areas = data.get('water', [])
        for i, water in enumerate(water_areas):
            element = {
                "id": f"water_{i}",
                "type": "hazard",
                "name": "Water",
                "description": "A water area",
                "position": water
            }
            elements.append(element)
        
        return elements
    
    def _classify_note(self, text: str) -> str:
        """
        根据note文本分类元素类型
        """
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['key', 'unlock']):
            return 'key'
        elif any(word in text_lower for word in ['treasure', 'gold', 'gem', 'chest']):
            return 'treasure'
        elif any(word in text_lower for word in ['monster', 'enemy', 'creature']):
            return 'monster'
        elif any(word in text_lower for word in ['entrance', 'door', 'exit']):
            return 'entrance'
        elif any(word in text_lower for word in ['trap', 'danger']):
            return 'trap'
        else:
            return 'item'
    
    def _extract_rooms_from_tree(self, tree: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        从BSP树结构中提取房间信息
        """
        rooms = []
        
        def traverse_tree(node: Dict[str, Any], room_counter: List[int]):
            if not node:
                return
            
            leaf = node.get('leaf', {})
            
            # 检查当前节点是否包含房间
            if 'room' in leaf and leaf['room']:
                room_data = leaf['room']
                room_id = f"room_{room_counter[0]}"
                room_counter[0] += 1
                
                # 从template ID推断房间类型
                template_id = room_data.get('template', {}).get('id', '')
                inferred_type = self._infer_room_type_from_template(template_id)
                
                room = {
                    "id": room_id,
                    "name": f"{inferred_type.title()} Room",
                    "type": inferred_type,
                    "position": {
                        "x": room_data.get('x', 0),
                        "y": room_data.get('y', 0)
                    },
                    "size": {
                        "width": room_data.get('width', 0),
                        "height": room_data.get('height', 0)
                    },
                    "properties": {
                        "template_id": template_id
                    }
                }
                
                # 标记特殊房间类型
                if inferred_type == 'entrance':
                    room["is_entrance"] = True
                elif inferred_type == 'boss':
                    room["is_exit"] = True
                
                rooms.append(room)
            
            # 递归处理子树
            if 'left' in node and node['left']:
                traverse_tree(node['left'], room_counter)
            if 'right' in node and node['right']:
                traverse_tree(node['right'], room_counter)
        
        # 开始遍历，使用列表来保持计数器的引用
        counter = [0]
        traverse_tree(tree, counter)
        
        # 智能标记入口和出口
        if rooms:
            entrance_exists = any(r.get('is_entrance', False) for r in rooms)
            exit_exists = any(r.get('is_exit', False) for r in rooms)
            
            # 如果没有入口，选择entrance类型房间或第一个房间
            if not entrance_exists:
                entrance_candidates = [r for r in rooms if r['type'] == 'entrance']
                if entrance_candidates:
                    entrance_candidates[0]['is_entrance'] = True
                else:
                    rooms[0]["is_entrance"] = True
            
            # 如果没有出口，智能选择合适的出口房间
            if not exit_exists and len(rooms) > 1:
                # 优先级：boss > treasure > monsters房间中最远的
                exit_candidates = [r for r in rooms if r['type'] == 'boss']
                if not exit_candidates:
                    exit_candidates = [r for r in rooms if r['type'] == 'treasure']
                if not exit_candidates:
                    # 选择距离入口最远的怪物房间
                    entrance_room = next((r for r in rooms if r.get('is_entrance')), rooms[0])
                    entrance_pos = (entrance_room['position']['x'], entrance_room['position']['y'])
                    
                    monster_rooms = [r for r in rooms if r['type'] == 'monsters' and not r.get('is_entrance')]
                    if monster_rooms:
                        # 计算距离并选择最远的
                        def distance(room):
                            px, py = room['position']['x'], room['position']['y']
                            return ((px - entrance_pos[0]) ** 2 + (py - entrance_pos[1]) ** 2) ** 0.5
                        
                        farthest_room = max(monster_rooms, key=distance)
                        exit_candidates = [farthest_room]
                
                if exit_candidates:
                    exit_candidates[0]['is_exit'] = True
                    exit_candidates[0]['type'] = 'boss'  # 将出口房间类型改为boss
                else:
                    rooms[-1]['is_exit'] = True
        
        return rooms
    
    def _infer_room_type_from_template(self, template_id: str) -> str:
        """
        从template ID推断房间类型
        """
        if not template_id:
            return 'room'
        
        template_lower = template_id.lower()
        
        if template_lower.startswith('entrance'):
            return 'entrance'
        elif template_lower.startswith('boss'):
            return 'boss'
        elif template_lower.startswith('monster'):
            return 'monsters'
        elif template_lower.startswith('treasure'):
            return 'treasure'
        elif template_lower.startswith('heal'):
            return 'heal'
        else:
            return 'room'
    
    def _extract_connections_from_tree(self, tree: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        从BSP树结构中提取连接信息
        基于树结构中的corridor信息创建连接
        """
        connections = []
        room_map = {}  # 存储节点路径到房间ID的映射
        
        # 第一遍：收集所有房间节点，建立路径映射
        def collect_room_paths(node: Dict[str, Any], path: str, room_counter: List[int]):
            if not node:
                return
                
            leaf = node.get('leaf', {})
            
            # 如果当前节点有房间，记录路径到房间ID的映射
            if 'room' in leaf and leaf['room']:
                room_id = f"room_{room_counter[0]}"
                room_map[path] = room_id
                room_counter[0] += 1
            
            # 递归处理子树，扩展路径
            if 'left' in node and node['left']:
                collect_room_paths(node['left'], path + 'L', room_counter)
            if 'right' in node and node['right']:
                collect_room_paths(node['right'], path + 'R', room_counter)
        
        # 第二遍：基于BSP树结构创建连接
        def create_connections_by_paths(node: Dict[str, Any], path: str, connection_counter: List[int]):
            if not node:
                return
                
            leaf = node.get('leaf', {})
            
            # 如果有走廊且有左右子树，说明这里连接了两个子区域
            if 'corridor' in leaf and leaf['corridor'] and 'left' in node and 'right' in node:
                # 找到左右子树中的房间
                left_rooms = self._find_rooms_by_path_prefix(room_map, path + 'L')
                right_rooms = self._find_rooms_by_path_prefix(room_map, path + 'R')
                
                # 创建连接：每个子区域选择一个房间
                if left_rooms and right_rooms:
                    # 选择第一个房间进行连接
                    connection = {
                        "id": f"connection_auto_{connection_counter[0]}",
                        "from_room": left_rooms[0],
                        "to_room": right_rooms[0],
                        "type": "corridor"
                    }
                    connections.append(connection)
                    connection_counter[0] += 1
            
            # 递归处理子树
            if 'left' in node and node['left']:
                create_connections_by_paths(node['left'], path + 'L', connection_counter)
            if 'right' in node and node['right']:
                create_connections_by_paths(node['right'], path + 'R', connection_counter)
        
        # 收集所有房间节点
        room_counter = [0]
        collect_room_paths(tree, '', room_counter)
        
        # 基于树结构创建连接
        conn_counter = [15]  # Start from 15 to avoid conflict with existing connections
        create_connections_by_paths(tree, '', conn_counter)
        
        return connections
    
    def _find_rooms_by_path_prefix(self, room_map: Dict[str, str], prefix: str) -> List[str]:
        """
        根据路径前缀找到所有匹配的房间ID
        """
        rooms = []
        for path, room_id in room_map.items():
            if path.startswith(prefix):
                rooms.append(room_id)
        return rooms
    
    def _is_node_in_subtree(self, target_node: Dict[str, Any], subtree_root: Dict[str, Any]) -> bool:
        """
        检查目标节点是否在给定子树中
        """
        if not subtree_root or not target_node:
            return False
        
        if target_node is subtree_root:
            return True
        
        # 递归检查左右子树
        left_contains = False
        right_contains = False
        
        if 'left' in subtree_root and subtree_root['left']:
            left_contains = self._is_node_in_subtree(target_node, subtree_root['left'])
        
        if 'right' in subtree_root and subtree_root['right']:
            right_contains = self._is_node_in_subtree(target_node, subtree_root['right'])
        
        return left_contains or right_contains
    
    def _find_rooms_in_subtree(self, node: Dict[str, Any]) -> List[str]:
        """
        在子树中找到所有房间ID
        """
        rooms = []
        room_counter = [0]
        
        def traverse(n: Dict[str, Any]):
            if not n:
                return
                
            leaf = n.get('leaf', {})
            if 'room' in leaf and leaf['room']:
                rooms.append(f"room_{room_counter[0]}")
                room_counter[0] += 1
            
            if 'left' in n and n['left']:
                traverse(n['left'])
            if 'right' in n and n['right']:
                traverse(n['right'])
        
        # 需要重新计算房间计数，这里简化处理
        # 在实际实现中应该保持全局房间ID的一致性
        traverse(node)
        return rooms
    
    def _extract_game_elements_from_layers(self, layers: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        从BSP的layers中提取游戏元素
        """
        game_elements = []
        element_id_counter = 0
        
        # 从props层提取道具（过滤掉过于密集的装饰元素）
        props_layer = layers.get('props', [])
        if props_layer:
            prop_elements = self._extract_elements_from_layer_filtered(
                props_layer, 'prop', element_id_counter, self._get_prop_type
            )
            game_elements.extend(prop_elements)
            element_id_counter += len(prop_elements)
        
        # 从monsters层提取怪物（按房间聚合）
        monsters_layer = layers.get('monsters', [])
        if monsters_layer:
            monster_elements = self._extract_monsters_by_room(
                monsters_layer, element_id_counter
            )
            game_elements.extend(monster_elements)
        
        return game_elements
    
    def _extract_elements_from_layer(self, layer_data: List[List[int]], element_prefix: str, 
                                   start_counter: int, type_func) -> List[Dict[str, Any]]:
        """
        从单个layer中提取元素
        """
        elements = []
        counter = start_counter
        
        for y, row in enumerate(layer_data):
            for x, value in enumerate(row):
                if value > 0:
                    element_type, element_name, element_desc = type_func(value)
                    
                    element = {
                        "id": f"{element_prefix}_{counter}",
                        "type": element_type,
                        "name": element_name,
                        "description": element_desc,
                        "position": {
                            "x": x,
                            "y": y
                        },
                        "properties": {
                            "layer_value": value
                        }
                    }
                    elements.append(element)
                    counter += 1
        
        return elements
    
    def _get_prop_type(self, value: int) -> tuple:
        """
        根据props层的数值确定道具类型
        参考BSP项目的PropType枚举
        """
        prop_types = {
            1: ("obstacle", "Peak", "A rocky peak formation"),
            2: ("item", "Bone", "A bone remains"),  
            3: ("treasure", "Silver Crate", "A crate containing silver"),
            4: ("treasure", "Wood Crate", "A wooden crate"),
            5: ("decoration", "Flag", "A decorative flag"),
            6: ("item", "Handcuff 1", "Metal handcuffs"),
            7: ("item", "Handcuff 2", "Another set of handcuffs"),
            8: ("light", "Lamp", "A glowing lamp"),
            9: ("decoration", "Skull", "A warning skull"),
            10: ("obstacle", "Large Stones", "Large stone formation"),
            11: ("obstacle", "Small Stones", "Small stone pile"),
            12: ("light", "Torch", "A burning torch"),
            13: ("obstacle", "Web Left", "Spider web on the left"),
            14: ("obstacle", "Web Right", "Spider web on the right"),
            15: ("heal", "Large Health Potion", "A large healing potion"),
            16: ("heal", "Small Health Potion", "A small healing potion"),
            17: ("key", "Golden Key", "A precious golden key"),
            18: ("key", "Silver Key", "A silver key"),
            19: ("magic", "Large Mana Potion", "A large mana potion"),
            20: ("magic", "Small Mana Potion", "A small mana potion"),
            21: ("transport", "Ladder", "A ladder for climbing"),
            22: ("treasure", "Coin", "A valuable coin")
        }
        
        return prop_types.get(value, ("item", f"Unknown Prop {value}", f"Unknown prop type {value}"))
    
    def _get_monster_type(self, value: int) -> tuple:
        """
        根据monsters层的数值确定怪物类型
        参考BSP项目的MonsterType枚举
        """
        monster_types = {
            1: ("monster", "Bandit", "A dangerous bandit"),
            2: ("monster", "Centaur Female", "A female centaur warrior"),
            3: ("monster", "Centaur Male", "A male centaur warrior"), 
            4: ("monster", "Large Mushroom", "A large poisonous mushroom"),
            5: ("monster", "Small Mushroom", "A small but deadly mushroom"),
            6: ("monster", "Skeleton", "An undead skeleton warrior"),
            7: ("monster", "Troll", "A massive troll"),
            8: ("monster", "Wolf", "A fierce wolf")
        }
        
        return monster_types.get(value, ("monster", f"Unknown Monster {value}", f"Unknown monster type {value}"))
    
    def _extract_elements_from_layer_filtered(self, layer_data: List[List[int]], element_prefix: str, 
                                             start_counter: int, type_func) -> List[Dict[str, Any]]:
        """
        从layer中提取元素，过滤掉过于密集的装饰元素
        """
        elements = []
        counter = start_counter
        
        # 收集所有位置
        positions = []
        for y, row in enumerate(layer_data):
            for x, value in enumerate(row):
                if value > 0:
                    positions.append((x, y, value))
        
        # 对于某些类型，进行采样而不是全部提取
        for x, y, value in positions:
            element_type, element_name, element_desc = type_func(value)
            
            # 跳过过于密集的装饰元素（如Peak、Torch等）
            if element_type in ['obstacle', 'light'] and counter > start_counter + 20:
                # 每隔几个位置才提取一个
                if counter % 3 != 0:
                    counter += 1
                    continue
            
            element = {
                "id": f"{element_prefix}_{counter}",
                "type": element_type,
                "name": element_name,
                "description": element_desc,
                "position": {
                    "x": x,
                    "y": y
                },
                "properties": {
                    "layer_value": value
                }
            }
            elements.append(element)
            counter += 1
        
        return elements
    
    def _extract_monsters_clustered(self, monsters_layer: List[List[int]], start_counter: int) -> List[Dict[str, Any]]:
        """
        从monsters层提取怪物，对密集区域进行聚类处理
        """
        # 收集所有怪物位置
        monster_positions = []
        for y, row in enumerate(monsters_layer):
            for x, value in enumerate(row):
                if value > 0:
                    monster_positions.append((x, y, value))
        
        # 简单聚类：对于相邻的相同类型怪物，只保留代表性的
        clustered_monsters = []
        processed = set()
        
        for x, y, value in monster_positions:
            if (x, y) in processed:
                continue
            
            # 获取怪物信息
            element_type, element_name, element_desc = self._get_monster_type(value)
            
            # 查找相邻的相同类型怪物
            cluster = [(x, y)]
            self._find_adjacent_monsters(monsters_layer, x, y, value, cluster, processed)
            
            # 为这个集群创建一个代表性怪物
            # 使用集群中心位置
            avg_x = sum(pos[0] for pos in cluster) / len(cluster)
            avg_y = sum(pos[1] for pos in cluster) / len(cluster)
            
            monster = {
                "id": f"monster_{start_counter + len(clustered_monsters)}",
                "type": "monster",
                "name": element_name if len(cluster) == 1 else f"{element_name} Group ({len(cluster)})",
                "description": element_desc if len(cluster) == 1 else f"A group of {len(cluster)} {element_name.lower()}s",
                "position": {
                    "x": round(avg_x),
                    "y": round(avg_y)
                },
                "properties": {
                    "layer_value": value,
                    "cluster_size": len(cluster),
                    "cluster_positions": cluster
                }
            }
            clustered_monsters.append(monster)
            
            # 标记所有集群位置为已处理
            for pos in cluster:
                processed.add(pos)
        
        return clustered_monsters
    
    def _find_adjacent_monsters(self, layer: List[List[int]], start_x: int, start_y: int, 
                               target_value: int, cluster: List, processed: set, max_cluster_size: int = 8):
        """
        递归查找相邻的相同类型怪物
        """
        if len(cluster) >= max_cluster_size:
            return
            
        # 检查8个方向的相邻位置
        directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
        
        for dx, dy in directions:
            nx, ny = start_x + dx, start_y + dy
            
            # 边界检查
            if (0 <= ny < len(layer) and 0 <= nx < len(layer[0]) and 
                (nx, ny) not in processed and (nx, ny) not in cluster):
                
                if layer[ny][nx] == target_value:
                    cluster.append((nx, ny))
                    self._find_adjacent_monsters(layer, nx, ny, target_value, cluster, processed, max_cluster_size)
    
    def _extract_monsters_by_room(self, monsters_layer: List[List[int]], start_counter: int) -> List[Dict[str, Any]]:
        """
        按房间聚合怪物，每个房间最多1-2个怪物遭遇
        """
        # 收集所有怪物位置
        monster_positions = []
        for y, row in enumerate(monsters_layer):
            for x, value in enumerate(row):
                if value > 0:
                    monster_positions.append((x, y, value))
        
        # 需要房间信息来按房间分组
        # 这里我们需要访问已转换的房间数据
        # 为了简化，我们使用一个更激进的聚类策略
        
        monster_encounters = []
        processed = set()
        encounter_id = start_counter
        
        for x, y, value in monster_positions:
            if (x, y) in processed:
                continue
            
            # 收集这个区域的所有怪物（更大的聚类范围）
            encounter_monsters = []
            self._collect_encounter_monsters(monsters_layer, x, y, encounter_monsters, processed, max_range=5)
            
            if encounter_monsters:
                # 分析这个遭遇中的怪物类型
                monster_types = {}
                total_monsters = len(encounter_monsters)
                center_x = sum(pos[0] for pos in encounter_monsters) / total_monsters
                center_y = sum(pos[1] for pos in encounter_monsters) / total_monsters
                
                for mx, my, mvalue in encounter_monsters:
                    if mvalue not in monster_types:
                        monster_types[mvalue] = []
                    monster_types[mvalue].append((mx, my))
                
                # 为这个遭遇创建描述
                if len(monster_types) == 1:
                    # 单一类型怪物
                    monster_value = list(monster_types.keys())[0]
                    _, monster_name, _ = self._get_monster_type(monster_value)
                    if total_monsters == 1:
                        encounter_name = monster_name
                        encounter_desc = f"A {monster_name.lower()}"
                    else:
                        encounter_name = f"{monster_name} Pack"
                        encounter_desc = f"A pack of {total_monsters} {monster_name.lower()}s"
                else:
                    # 混合类型怪物
                    type_names = []
                    for mvalue, positions in monster_types.items():
                        _, name, _ = self._get_monster_type(mvalue)
                        count = len(positions)
                        if count == 1:
                            type_names.append(name.lower())
                        else:
                            type_names.append(f"{count} {name.lower()}s")
                    
                    encounter_name = "Mixed Encounter"
                    encounter_desc = f"An encounter with {' and '.join(type_names)}"
                
                encounter = {
                    "id": f"encounter_{encounter_id}",
                    "type": "encounter",
                    "name": encounter_name,
                    "description": encounter_desc,
                    "position": {
                        "x": round(center_x),
                        "y": round(center_y)
                    },
                    "properties": {
                        "total_monsters": total_monsters,
                        "monster_types": dict(monster_types),
                        "encounter_positions": encounter_monsters
                    }
                }
                
                monster_encounters.append(encounter)
                encounter_id += 1
        
        return monster_encounters
    
    def _collect_encounter_monsters(self, layer: List[List[int]], start_x: int, start_y: int, 
                                  encounter_monsters: List, processed: set, max_range: int = 5):
        """
        收集一个遭遇范围内的所有怪物
        """
        # 使用BFS在一定范围内收集怪物
        queue = [(start_x, start_y)]
        visited = set([(start_x, start_y)])
        
        while queue:
            x, y = queue.pop(0)
            
            if (x, y) not in processed and layer[y][x] > 0:
                encounter_monsters.append((x, y, layer[y][x]))
                processed.add((x, y))
            
            # 检查周围的位置
            for dx in range(-max_range, max_range + 1):
                for dy in range(-max_range, max_range + 1):
                    if dx == 0 and dy == 0:
                        continue
                    
                    nx, ny = x + dx, y + dy
                    
                    if (0 <= ny < len(layer) and 0 <= nx < len(layer[0]) and 
                        (nx, ny) not in visited and (nx, ny) not in processed):
                        
                        if layer[ny][nx] > 0:
                            # 计算距离，只有在合理范围内才加入队列
                            dist = ((nx - start_x) ** 2 + (ny - start_y) ** 2) ** 0.5
                            if dist <= max_range:
                                queue.append((nx, ny))
                                visited.add((nx, ny))