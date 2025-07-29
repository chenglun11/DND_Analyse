#!/usr/bin/env python3
"""
Watabou格式可视化测试脚本
专门测试Watabou格式的地牢数据可视化
"""

import json
import os
import sys
import requests
from pathlib import Path

def test_watabou_visualization():
    """测试Watabou格式的可视化"""
    print("测试Watabou格式可视化...")
    
    # 测试文件
    test_file = "samples/watabou_test/abandoned_hold_of_rhun-hakrax.json"
    if not os.path.exists(test_file):
        print(f"测试文件不存在: {test_file}")
        return False
    
    try:
        # 读取原始数据
        with open(test_file, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
        
        print(f"原始Watabou数据:")
        print(f"  - 标题: {original_data.get('title', 'Unknown')}")
        print(f"  - 房间数: {len(original_data.get('rects', []))}")
        print(f"  - 门数: {len(original_data.get('doors', []))}")
        print(f"  - 注释数: {len(original_data.get('notes', []))}")
        
        # 准备文件上传
        with open(test_file, 'rb') as f:
            files = {'file': (os.path.basename(test_file), f, 'application/json')}
            
            # 测试可视化数据API
            print("\n测试 /api/visualize-data 接口...")
            response = requests.post('http://localhost:5001/api/visualize-data', files=files)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ 可视化数据API测试成功")
                    vis_data = result.get('visualization_data', {})
                    print(f"  - 前端房间数: {len(vis_data.get('rooms', []))}")
                    print(f"  - 前端通道数: {len(vis_data.get('corridors', []))}")
                    print(f"  - 地图尺寸: {vis_data.get('width', 0)} x {vis_data.get('height', 0)}")
                    
                    # 显示房间详情
                    rooms = vis_data.get('rooms', [])
                    print(f"\n房间详情:")
                    for i, room in enumerate(rooms[:5]):  # 只显示前5个
                        print(f"  {i+1}. {room.get('name', 'Unknown')} - 类型: {room.get('type', 'room')} - 位置: ({room['x']:.0f}, {room['y']:.0f}) - 尺寸: {room['width']:.0f}x{room['height']:.0f}")
                    
                    # 显示通道详情
                    corridors = vis_data.get('corridors', [])
                    print(f"\n通道详情:")
                    for i, corridor in enumerate(corridors[:5]):  # 只显示前5个
                        start = corridor['start']
                        end = corridor['end']
                        print(f"  {i+1}. {corridor.get('name', 'Unknown')} - 从 ({start['x']:.0f}, {start['y']:.0f}) 到 ({end['x']:.0f}, {end['y']:.0f})")
                    
                else:
                    print(f"❌ 可视化数据API失败: {result.get('error')}")
                    return False
            else:
                print(f"❌ 可视化数据API请求失败: {response.status_code}")
                return False
            
            # 测试图像生成API
            print("\n测试 /api/visualize 接口...")
            f.seek(0)  # 重置文件指针
            options = {
                'show_connections': True,
                'show_room_ids': True,
                'show_grid': True,
                'show_game_elements': True
            }
            data = {'options': json.dumps(options)}
            response = requests.post('http://localhost:5001/api/visualize', files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ 图像生成API测试成功")
                    image_data = result.get('image_data')
                    if image_data:
                        print(f"  - 图像数据长度: {len(image_data)} 字符")
                        # 保存测试图像
                        with open('test_watabou_visualization.png', 'wb') as img_file:
                            import base64
                            img_file.write(base64.b64decode(image_data))
                        print("  - 图像已保存为 test_watabou_visualization.png")
                        
                        # 检查文件大小
                        file_size = os.path.getsize('test_watabou_visualization.png')
                        print(f"  - 文件大小: {file_size} bytes")
                        
                        if file_size > 50000:  # 大于50KB认为是合理的图像
                            print("  ✅ 图像质量良好")
                        else:
                            print("  ⚠️ 图像文件较小，可能质量不佳")
                    else:
                        print("  - 警告: 没有返回图像数据")
                else:
                    print(f"❌ 图像生成API失败: {result.get('error')}")
                    return False
            else:
                print(f"❌ 图像生成API请求失败: {response.status_code}")
                return False
                
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Flask服务器，请确保服务器正在运行")
        return False
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        return False
    
    return True

def main():
    """主测试函数"""
    print("开始Watabou格式可视化测试...\n")
    
    if test_watabou_visualization():
        print("\n✅ Watabou格式可视化测试通过！")
    else:
        print("\n❌ Watabou格式可视化测试失败")

if __name__ == "__main__":
    main() 