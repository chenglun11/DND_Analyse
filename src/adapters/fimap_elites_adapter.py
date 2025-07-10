import logging
from typing import Dict, Any, Optional, List
from src.adapters.base import BaseAdapter
from src.schema import UnifiedDungeonFormat

logger = logging.getLogger(__name__)

def convex_hull(points):
    # Andrew's monotone chain convex hull algorithm
    points = sorted(set((p['x'], p['y']) for p in points))
    if len(points) <= 1:
        return points
    def cross(o, a, b):
        return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return [ {'x':x, 'y':y} for (x, y) in lower[:-1] + upper[:-1] ]

class FimapElitesAdapter(BaseAdapter):
    """适配 FI-MAP Elites 生成的地牢格式，输出多边形边界。"""

    @property
    def format_name(self) -> str:
        return "fimap_elites"

    def detect(self, data: Dict[str, Any]) -> bool:
        # 关键字段判断
        return (
            "plan_graph" in data and
            "connection_doors" in data and
            "prescription" in data and
            "voronoi_tessellation" in data
        )

    def convert(self, data: Dict[str, Any]) -> Optional[UnifiedDungeonFormat]:
        try:
            # 1. 基本信息
            prescription = data.get("prescription", {})
            voronoi = data.get("voronoi_tessellation", {})
            name = prescription.get("name", "FI-MAP Elites Dungeon")
            author = "FI-MAP Elites Generator"
            description = f"Converted from FI-MAP Elites: {name}"
            grid = {"type": "square", "size": 1, "unit": "cell"}
            # 2. 空间单元（房间/走廊）
            # type__per__space_unit: 1=房间, 0=走廊
            type_per_space_unit = prescription.get("type__per__space_unit", {})
            name_per_space_unit = prescription.get("name__per__space_unit", {})
            area_per_space_unit = prescription.get("area__per__space_unit", {})
            color_per_space_unit = prescription.get("color__per__space_unit", {})
            # 位置推断：用voronoi_tessellation.generator_points
            generator_points = voronoi.get("generator_points", [])
            cell_assignment = data.get("cell_space_unit_assignment", {})
            cell_assignment = {int(k):v for k,v in cell_assignment.items()} if isinstance(cell_assignment, dict) else cell_assignment
            cell_assignment_list = cell_assignment if isinstance(cell_assignment, list) else [cell_assignment.get(i, -1) for i in range(len(generator_points))]
            cell_locations = data.get("plan_graph", {}).get("location__per__vertex", {})
            cell_locations = {int(k):v for k,v in cell_locations.items()}
            # 统计每个space_unit包含的cell索引
            su_to_cells = {}
            for idx, su in enumerate(cell_assignment_list):
                if su == -1:
                    continue
                su_to_cells.setdefault(su, []).append(idx)
            # 生成房间和走廊节点
            rooms = []
            corridors = []
            for su_id, su_type in type_per_space_unit.items():
                idx = int(su_id)
                pos = generator_points[idx] if idx < len(generator_points) else {"x": 0, "y": 0}
                node = {
                    "id": f"space_{su_id}",
                    "shape": "rectangle",  # 近似
                    "position": {"x": pos.get("x", 0), "y": pos.get("y", 0)},
                    "size": {"width": area_per_space_unit.get(su_id, 1), "height": area_per_space_unit.get(su_id, 1)},
                    "name": name_per_space_unit.get(su_id, f"Space {su_id}"),
                    "description": f"Color: {color_per_space_unit.get(su_id, {})}",
                }
                # 多边形边界
                cell_ids = su_to_cells.get(idx, [])
                poly_points = [cell_locations.get(cid) for cid in cell_ids if cid in cell_locations]
                if len(poly_points) >= 3:
                    node["polygon"] = convex_hull(poly_points)
                elif len(poly_points) > 0:
                    node["polygon"] = poly_points
                if su_type == 1:
                    rooms.append(node)
                else:
                    corridors.append(node)
            # 4. 门（doors）
            doors = []
            for i, door in enumerate(data.get("connection_doors", [])):
                su_conn = door.get("space_units_connection", {})
                cells_conn = door.get("cells_connection", {})
                door_obj = {
                    "id": f"door_{i}",
                    "position": {},
                    "connects": [f"space_{su_conn.get('v1')}", f"space_{su_conn.get('v2')}"]
                }
                # 尝试推断门的坐标（用cell的中心点）
                cell_locs = data.get("plan_graph", {}).get("location__per__vertex", {})
                v1, v2 = cells_conn.get("v1"), cells_conn.get("v2")
                if cell_locs and v1 is not None and v2 is not None:
                    p1, p2 = cell_locs.get(str(v1)), cell_locs.get(str(v2))
                    if p1 and p2:
                        door_obj["position"] = {
                            "x": (p1["x"] + p2["x"]) / 2,
                            "y": (p1["y"] + p2["y"]) / 2
                        }
                doors.append(door_obj)
            # 5. 走廊（corridors）可选：如有需要可用type=0的space_unit
            # 6. 地图尺寸
            bounding = voronoi.get("bounding_rectangle", {})
            map_width = bounding.get("width", 16)
            map_height = bounding.get("height", 16)
            # 7. 组装level
            level = {
                "id": "level_1",
                "name": "Main Level",
                "map": {"width": map_width, "height": map_height},
                "rooms": rooms,
                "doors": doors,
                "corridors": corridors
            }
            unified = UnifiedDungeonFormat(
                name=name,
                author=author,
                description=description,
                grid=grid,
                levels=[level]
            )
            return unified
        except Exception as e:
            logger.error(f"FI-MAP Elites 适配失败: {e}", exc_info=True)
            return None
