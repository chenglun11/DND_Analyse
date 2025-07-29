#!/usr/bin/env python3
"""
测试图像生成功能
"""

import json
import os
import sys
import requests
from pathlib import Path

def test_image_generation():
    """测试图像生成功能"""
    print("测试图像生成功能...")
    
    # 测试文件
    test_file = "samples/watabou_test/abandoned_hold_of_rhun-hakrax.json"
    if not os.path.exists(test_file):
        print(f"测试文件不存在: {test_file}")
        return False
    
    try:
        # 准备文件上传
        with open(test_file, 'rb') as f:
            files = {'file': (os.path.basename(test_file), f, 'application/json')}
            
            # 测试图像生成API
            print("测试 /api/visualize 接口...")
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
                        output_file = 'test_generated_image_detailed.png'
                        with open(output_file, 'wb') as img_file:
                            import base64
                            img_file.write(base64.b64decode(image_data))
                        
                        # 检查文件大小
                        file_size = os.path.getsize(output_file)
                        print(f"  - 图像已保存为 {output_file}")
                        print(f"  - 文件大小: {file_size} bytes")
                        
                        if file_size > 50000:  # 大于50KB认为是合理的图像
                            print("  ✅ 图像质量良好")
                        else:
                            print("  ⚠️ 图像文件较小，可能质量不佳")
                        
                        # 显示图像信息
                        print(f"  - 文件名: {result.get('filename', 'Unknown')}")
                        if result.get('unified_data'):
                            unified_data = result['unified_data']
                            if unified_data.get('levels'):
                                level = unified_data['levels'][0]
                                print(f"  - 房间数: {len(level.get('rooms', []))}")
                                print(f"  - 通道数: {len(level.get('corridors', []))}")
                                print(f"  - 连接数: {len(level.get('connections', []))}")
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
    print("开始图像生成功能测试...\n")
    
    if test_image_generation():
        print("\n✅ 图像生成功能测试通过！")
        print("现在可以在前端页面中查看生成的图像了。")
    else:
        print("\n❌ 图像生成功能测试失败")

if __name__ == "__main__":
    main() 