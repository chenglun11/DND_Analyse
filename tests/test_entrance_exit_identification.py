import pytest
import json
from src.schema import identify_entrance_exit

class TestEntranceExitIdentification:
    """测试入口出口识别功能"""
    
    def test_identification_by_name(self):
        """测试通过房间名称识别入口出口"""
        dungeon_data = {
            "levels": [{
                "rooms": [
                    {
                        "id": "room_1",
                        "name": "Entrance Hall",
                        "position": {"x": 0, "y": 0},
                        "size": {"width": 5, "height": 5}
                    },
                    {
                        "id": "room_2", 
                        "name": "Boss Room",
                        "position": {"x": 10, "y": 10},
                        "size": {"width": 5, "height": 5}
                    },
                    {
                        "id": "room_3",
                        "name": "Treasure Room", 
                        "position": {"x": 5, "y": 5},
                        "size": {"width": 5, "height": 5}
                    }
                ]
            }]
        }
        
        result = identify_entrance_exit(dungeon_data)
        rooms = result["levels"][0]["rooms"]
        
        # 检查入口识别
        entrance_room = next((r for r in rooms if r.get("is_entrance")), None)
        assert entrance_room is not None
        assert entrance_room["id"] == "room_1"
        
        # 检查出口识别
        exit_room = next((r for r in rooms if r.get("is_exit")), None)
        assert exit_room is not None
        assert exit_room["id"] == "room_2"
    
    def test_identification_by_description(self):
        """测试通过房间描述识别入口出口"""
        dungeon_data = {
            "levels": [{
                "rooms": [
                    {
                        "id": "room_1",
                        "name": "Hall",
                        "description": "A grand entrance with stone pillars",
                        "position": {"x": 0, "y": 0},
                        "size": {"width": 5, "height": 5}
                    },
                    {
                        "id": "room_2",
                        "name": "Chamber", 
                        "description": "The final exit leads to freedom",
                        "position": {"x": 10, "y": 10},
                        "size": {"width": 5, "height": 5}
                    }
                ]
            }]
        }
        
        result = identify_entrance_exit(dungeon_data)
        rooms = result["levels"][0]["rooms"]
        
        entrance_room = next((r for r in rooms if r.get("is_entrance")), None)
        assert entrance_room is not None
        assert entrance_room["id"] == "room_1"
        
        exit_room = next((r for r in rooms if r.get("is_exit")), None)
        assert exit_room is not None
        assert exit_room["id"] == "room_2"
    
    def test_identification_by_connectivity(self):
        """测试通过连接度识别入口出口"""
        dungeon_data = {
            "levels": [{
                "rooms": [
                    {
                        "id": "room_1",
                        "name": "Room 1",
                        "position": {"x": 0, "y": 0},
                        "size": {"width": 5, "height": 5}
                    },
                    {
                        "id": "room_2",
                        "name": "Room 2", 
                        "position": {"x": 5, "y": 0},
                        "size": {"width": 5, "height": 5}
                    },
                    {
                        "id": "room_3",
                        "name": "Room 3",
                        "position": {"x": 10, "y": 0},
                        "size": {"width": 5, "height": 5}
                    }
                ],
                "connections": [
                    {"from_room": "room_1", "to_room": "room_2"},
                    {"from_room": "room_2", "to_room": "room_3"}
                ]
            }]
        }
        
        result = identify_entrance_exit(dungeon_data)
        rooms = result["levels"][0]["rooms"]
        
        # 应该识别出连接度最低的房间作为入口和出口
        entrance_room = next((r for r in rooms if r.get("is_entrance")), None)
        exit_room = next((r for r in rooms if r.get("is_exit")), None)
        
        assert entrance_room is not None
        assert exit_room is not None
        assert entrance_room["id"] != exit_room["id"]
    
    def test_identification_by_coordinates(self):
        """测试通过坐标识别入口出口"""
        dungeon_data = {
            "levels": [{
                "rooms": [
                    {
                        "id": "room_1",
                        "name": "Room 1",
                        "position": {"x": 10, "y": 10},
                        "size": {"width": 5, "height": 5}
                    },
                    {
                        "id": "room_2",
                        "name": "Room 2",
                        "position": {"x": 0, "y": 0},
                        "size": {"width": 5, "height": 5}
                    },
                    {
                        "id": "room_3",
                        "name": "Room 3",
                        "position": {"x": 20, "y": 20},
                        "size": {"width": 5, "height": 5}
                    }
                ]
            }]
        }
        
        # 调试：计算每个房间的中心点
        def get_room_center(room):
            pos = room.get('position', {})
            size = room.get('size', {})
            x = pos.get('x', 0) + size.get('width', 0) / 2
            y = pos.get('y', 0) + size.get('height', 0) / 2
            return x, y
        
        for room in dungeon_data["levels"][0]["rooms"]:
            center = get_room_center(room)
            print(f"Room {room['id']}: center={center}, sum={center[0] + center[1]}")
        
        result = identify_entrance_exit(dungeon_data)
        rooms = result["levels"][0]["rooms"]
        
        # 应该选择最左下角的房间作为入口，最右上角的房间作为出口
        entrance_room = next((r for r in rooms if r.get("is_entrance")), None)
        exit_room = next((r for r in rooms if r.get("is_exit")), None)
        
        print(f"Identified entrance: {entrance_room['id'] if entrance_room else None}")
        print(f"Identified exit: {exit_room['id'] if exit_room else None}")
        
        assert entrance_room is not None
        assert exit_room is not None
        assert entrance_room["id"] == "room_2"  # 最左下角
        assert exit_room["id"] == "room_3"      # 最右上角
    
    def test_no_rooms(self):
        """测试没有房间的情况"""
        dungeon_data = {
            "levels": [{
                "rooms": []
            }]
        }
        
        result = identify_entrance_exit(dungeon_data)
        assert result == dungeon_data
    
    def test_no_levels(self):
        """测试没有层级的情况"""
        dungeon_data = {
            "levels": []
        }
        
        result = identify_entrance_exit(dungeon_data)
        assert result == dungeon_data 