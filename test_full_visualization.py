#!/usr/bin/env python3
"""
完整可视化功能测试脚本
测试从文件上传到图像生成的整个流程
"""

import json
import os
import sys
import requests
from pathlib import Path

def test_flask_visualization_api():
    """测试Flask后端的可视化API"""
    print("测试Flask后端可视化API...")
    
    # 测试文件
    test_file = "samples/edger/1.json"
    if not os.path.exists(test_file):
        print(f"测试文件不存在: {test_file}")
        return False
    
    try:
        # 准备文件上传
        with open(test_file, 'rb') as f:
            files = {'file': (os.path.basename(test_file), f, 'application/json')}
            
            # 测试可视化数据API
            print("测试 /api/visualize-data 接口...")
            response = requests.post('http://localhost:5001/api/visualize-data', files=files)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ 可视化数据API测试成功")
                    vis_data = result.get('visualization_data', {})
                    print(f"  - 房间数: {len(vis_data.get('rooms', []))}")
                    print(f"  - 通道数: {len(vis_data.get('corridors', []))}")
                    print(f"  - 地图尺寸: {vis_data.get('width', 0)} x {vis_data.get('height', 0)}")
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
                        with open('test_generated_image.png', 'wb') as img_file:
                            import base64
                            img_file.write(base64.b64decode(image_data))
                        print("  - 图像已保存为 test_generated_image.png")
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

def test_health_check():
    """测试健康检查接口"""
    print("测试健康检查接口...")
    
    try:
        response = requests.get('http://localhost:5001/api/health')
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 健康检查成功: {result.get('message', '')}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Flask服务器")
        return False
    except Exception as e:
        print(f"❌ 健康检查出错: {e}")
        return False

def main():
    """主测试函数"""
    print("开始完整可视化功能测试...\n")
    
    # 测试健康检查
    if not test_health_check():
        print("\n❌ 健康检查失败，停止测试")
        return
    
    # 测试可视化API
    if test_flask_visualization_api():
        print("\n✅ 所有测试通过！可视化功能正常工作")
    else:
        print("\n❌ 部分测试失败，请检查错误信息")

if __name__ == "__main__":
    main() 