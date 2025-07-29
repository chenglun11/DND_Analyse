#!/usr/bin/env python3
"""
测试前端API调用
"""

import json
import requests
import base64

def test_frontend_api_calls():
    """测试前端API调用"""
    print("测试前端API调用...")
    
    # 模拟前端调用
    test_file = "samples/watabou_test/abandoned_hold_of_rhun-hakrax.json"
    
    try:
        # 1. 测试图像生成（模拟DetailView的调用）
        print("\n1. 测试图像生成...")
        with open(test_file, 'rb') as f:
            files = {'file': ('abandoned_hold_of_rhun-hakrax.json', f, 'application/json')}
            data = {'options': json.dumps({
                'show_connections': True,
                'show_room_ids': True,
                'show_grid': True,
                'show_game_elements': True
            })}
            
            response = requests.post('http://localhost:5001/api/visualize', files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ 图像生成成功")
                    image_data = result.get('image_data', '')
                    print(f"图像数据长度: {len(image_data)}")
                    
                    # 保存图像用于验证
                    with open('test_frontend_image.png', 'wb') as img_file:
                        img_file.write(base64.b64decode(image_data))
                    print("图像已保存为 test_frontend_image.png")
                    
                    # 检查文件大小
                    import os
                    file_size = os.path.getsize('test_frontend_image.png')
                    print(f"文件大小: {file_size} bytes")
                    
                    if file_size > 50000:
                        print("✅ 图像质量良好")
                    else:
                        print("⚠️ 图像文件较小")
                else:
                    print(f"❌ 图像生成失败: {result.get('error')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                print(f"错误详情: {response.text}")
        
        # 2. 测试可视化数据获取
        print("\n2. 测试可视化数据获取...")
        with open(test_file, 'rb') as f:
            files = {'file': ('abandoned_hold_of_rhun-hakrax.json', f, 'application/json')}
            
            response = requests.post('http://localhost:5001/api/visualize-data', files=files)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ 可视化数据获取成功")
                    vis_data = result.get('visualization_data', {})
                    print(f"房间数: {len(vis_data.get('rooms', []))}")
                    print(f"通道数: {len(vis_data.get('corridors', []))}")
                    print(f"地图尺寸: {vis_data.get('width', 0)} x {vis_data.get('height', 0)}")
                else:
                    print(f"❌ 可视化数据获取失败: {result.get('error')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                print(f"错误详情: {response.text}")
        
        # 3. 测试分析API
        print("\n3. 测试分析API...")
        with open(test_file, 'rb') as f:
            files = {'file': ('abandoned_hold_of_rhun-hakrax.json', f, 'application/json')}
            
            response = requests.post('http://localhost:5001/api/analyze', files=files)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ 分析API调用成功")
                    analysis_result = result.get('result', {})
                    print(f"总体评分: {analysis_result.get('overall_score', 0)}")
                    print(f"详细评分数量: {len(analysis_result.get('detailed_scores', {}))}")
                else:
                    print(f"❌ 分析API调用失败: {result.get('error')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                print(f"错误详情: {response.text}")
                
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_frontend_api_calls() 