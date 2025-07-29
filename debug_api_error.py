#!/usr/bin/env python3
"""
调试API错误
"""

import json
import requests
import time

def test_api_endpoints():
    """测试API端点"""
    print("测试API端点...")
    
    # 测试健康检查
    print("\n1. 测试健康检查...")
    try:
        response = requests.get('http://localhost:5001/api/health')
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ 健康检查通过")
        else:
            print(f"❌ 健康检查失败: {response.text}")
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
    
    # 测试文件上传
    print("\n2. 测试文件上传...")
    test_file = "samples/watabou_test/abandoned_hold_of_rhun-hakrax.json"
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': (test_file, f, 'application/json')}
            data = {'options': json.dumps({
                'show_connections': True,
                'show_room_ids': True,
                'show_grid': True,
                'show_game_elements': True
            })}
            
            print("发送可视化请求...")
            response = requests.post('http://localhost:5001/api/visualize', files=files, data=data)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ 可视化请求成功")
                    print(f"图像数据长度: {len(result.get('image_data', ''))}")
                else:
                    print(f"❌ 可视化请求失败: {result.get('error')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"错误详情: {error_data}")
                except:
                    print(f"响应内容: {response.text}")
                    
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    # 测试可视化数据API
    print("\n3. 测试可视化数据API...")
    try:
        with open(test_file, 'rb') as f:
            files = {'file': (test_file, f, 'application/json')}
            
            print("发送可视化数据请求...")
            response = requests.post('http://localhost:5001/api/visualize-data', files=files)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ 可视化数据请求成功")
                    vis_data = result.get('visualization_data', {})
                    print(f"房间数: {len(vis_data.get('rooms', []))}")
                    print(f"通道数: {len(vis_data.get('corridors', []))}")
                else:
                    print(f"❌ 可视化数据请求失败: {result.get('error')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"错误详情: {error_data}")
                except:
                    print(f"响应内容: {response.text}")
                    
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    test_api_endpoints() 