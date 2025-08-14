from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import sys
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path

# 导入现有的地下城分析模块（使用本地复制的src）
from src.adapter_manager import AdapterManager
from src.quality_assessor import DungeonQualityAssessor
from src.batch_assess import assess_all_maps

# 定义项目根目录
project_root = Path(__file__).parent.parent

app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 配置日志
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# 初始化适配器管理器和质量评估器
adapter_manager = AdapterManager()
quality_assessor = DungeonQualityAssessor()

# 内存缓存系统
file_cache = {}

def cleanup_expired_cache():
    """清理过期的缓存文件"""
    current_time = datetime.now()
    expired_keys = []
    
    for file_id, cache_data in file_cache.items():
        # 文件过期时间：1小时
        if current_time - cache_data['timestamp'] > timedelta(hours=24):
            expired_keys.append(file_id)
    
    for key in expired_keys:
        del file_cache[key]
    
    if expired_keys:
        print(f"清理了 {len(expired_keys)} 个过期缓存文件")

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    # 清理过期缓存
    cleanup_expired_cache()
    
    return jsonify({
        'status': 'healthy',
        'message': 'Dungeon Analyzer API is running',
        'cache_info': {
            'cached_files': len(file_cache),
            'cache_size': sum(len(str(data.get('content', ''))) for data in file_cache.values())
        }
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_dungeon():
    """分析单个地下城文件"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        # 读取文件内容并生成文件ID
        file_content = file.read().decode('utf-8')
        file_id = hashlib.md5(file_content.encode()).hexdigest()
        
        # 存储到缓存
        file_cache[file_id] = {
            'filename': file.filename,
            'content': file_content,
            'timestamp': datetime.now(),
            'data': json.loads(file_content)
        }
        
        try:
            # 直接处理文件内容
            data = file_cache[file_id]['data']
            
            # 使用现有的适配器管理器处理文件
            unified_data = adapter_manager.convert(data)
            
            if unified_data is None:
                return jsonify({
                    'success': False,
                    'error': '无法识别或转换文件格式'
                }), 400
            
            # 使用质量评估器进行分析
            assessment_result = quality_assessor.assess_quality(unified_data)
            
            return jsonify({
                'success': True,
                'result': assessment_result,
                'unified_data': unified_data,
                'filename': file.filename,
                'file_id': file_id  # 返回文件ID供后续使用
            })
            
        except Exception as e:
            # 如果处理失败，从缓存中删除
            if file_id in file_cache:
                del file_cache[file_id]
            raise e
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyze-by-id', methods=['POST'])
def analyze_dungeon_by_id():
    """通过文件ID分析地下城"""
    try:
        file_id = request.form.get('file_id')
        if not file_id or file_id not in file_cache:
            return jsonify({'error': '文件ID无效或已过期'}), 404
        
        file_data = file_cache[file_id]
        
        # 检查文件是否过期（24小时后）
        if datetime.now() - file_data['timestamp'] > timedelta(hours=24):
            del file_cache[file_id]
            return jsonify({'error': '文件已过期，请重新上传'}), 410
        
        try:
            # 处理文件
            data = file_data['data']
            unified_data = adapter_manager.convert(data)
            
            if unified_data is None:
                return jsonify({
                    'success': False,
                    'error': '无法识别或转换文件格式'
                }), 400
            
            # 使用质量评估器进行分析
            assessment_result = quality_assessor.assess_quality(unified_data)
            
            return jsonify({
                'success': True,
                'result': assessment_result,
                'unified_data': unified_data,
                'filename': file_data['filename'],
                'file_id': file_id
            })
            
        except Exception as e:
            # 如果处理失败，从缓存中删除
            if file_id in file_cache:
                del file_cache[file_id]
            raise e
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/visualize-by-id', methods=['POST'])
def visualize_dungeon_by_id():
    """通过文件ID生成地下城可视化图像"""
    try:
        file_id = request.form.get('file_id')
        if not file_id or file_id not in file_cache:
            return jsonify({'error': '文件ID无效或已过期'}), 404
        
        file_data = file_cache[file_id]
        
        # 检查文件是否过期（24小时后）
        if datetime.now() - file_data['timestamp'] > timedelta(hours=24):
            del file_cache[file_id]
            return jsonify({'error': '文件已过期，请重新上传'}), 410
        
        # 获取可视化选项
        visualization_options = request.form.get('options', '{}')
        options = json.loads(visualization_options) if visualization_options else {}
        
        try:
            # 处理文件
            data = file_data['data']
            unified_data = adapter_manager.convert(data)
            
            if unified_data is None:
                return jsonify({
                    'success': False,
                    'error': '无法识别或转换文件格式'
                }), 400
            
            # 生成可视化图像
            from src.visualizer import visualize_dungeon
            upload_dir = Path(project_root) / 'temp_uploads'
            upload_dir.mkdir(exist_ok=True)
            output_path = upload_dir / f"{Path(file_data['filename']).stem}_visualization.png"
            
            success = visualize_dungeon(
                unified_data, 
                str(output_path),
                show_connections=options.get('show_connections', True),
                show_room_ids=options.get('show_room_ids', True),
                show_grid=options.get('show_grid', True),
                show_game_elements=options.get('show_game_elements', True)
            )
            
            if success and output_path.exists():
                # 读取生成的图像文件并转换为base64
                import base64
                with open(output_path, 'rb') as img_file:
                    img_data = base64.b64encode(img_file.read()).decode('utf-8')
                
                # 清理临时文件
                output_path.unlink()
                
                return jsonify({
                    'success': True,
                    'image_data': img_data,
                    'unified_data': unified_data,
                    'filename': file_data['filename'],
                    'file_id': file_id
                })
            else:
                return jsonify({
                    'success': False,
                    'error': '可视化生成失败'
                }), 500
            
        except Exception as e:
            # 如果处理失败，从缓存中删除
            if file_id in file_cache:
                del file_cache[file_id]
            raise e
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/visualize-data-by-id', methods=['POST'])
def get_visualization_data_by_id():
    """通过文件ID获取地下城可视化数据"""
    try:
        file_id = request.form.get('file_id')
        if not file_id or file_id not in file_cache:
            return jsonify({'error': '文件ID无效或已过期'}), 404
        
        file_data = file_cache[file_id]
        
        # 检查文件是否过期（1小时后）
        if datetime.now() - file_data['timestamp'] > timedelta(hours=24):
            del file_cache[file_id]
            return jsonify({'error': '文件已过期，请重新上传'}), 410
        
        try:
            # 处理文件
            data = file_data['data']
            unified_data = adapter_manager.convert(data)
            
            if unified_data is None:
                return jsonify({
                    'success': False,
                    'error': '无法识别或转换文件格式'
                }), 400
            
            # 转换为前端可用的格式
            from src.visualizer import DungeonVisualizer
            visualizer = DungeonVisualizer()
            
            # 提取可视化数据
            visualization_data = visualizer._extract_visualization_data(unified_data)
            
            return jsonify({
                'success': True,
                'visualization_data': visualization_data,
                'unified_data': unified_data,
                'filename': file_data['filename'],
                'file_id': file_id
            })
            
        except Exception as e:
            # 如果处理失败，从缓存中删除
            if file_id in file_cache:
                del file_cache[file_id]
            raise e
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/cache-info', methods=['GET'])
def get_cache_info():
    """获取缓存信息"""
    cleanup_expired_cache()
    
    cache_info = {
        'total_files': len(file_cache),
        'files': []
    }
    
    for file_id, data in file_cache.items():
        age = datetime.now() - data['timestamp']
        cache_info['files'].append({
            'file_id': file_id,
            'filename': data['filename'],
            'age_minutes': int(age.total_seconds() / 60),
            'size_bytes': len(data['content'])
        })
    
    return jsonify(cache_info)

@app.route('/api/clear-cache', methods=['POST'])
def clear_cache():
    """清理所有缓存"""
    global file_cache
    cleared_count = len(file_cache)
    file_cache = {}
    
    return jsonify({
        'success': True,
        'message': f'已清理 {cleared_count} 个缓存文件'
    })

@app.route('/api/analyze-by-filename', methods=['POST'])
def analyze_dungeon_by_filename():
    """通过文件名分析地下城文件（向后兼容）"""
    try:
        # 获取文件名
        filename = request.form.get('filename')
        if not filename:
            return jsonify({'error': '没有提供文件名'}), 400
        
        # 获取分析选项
        analysis_options = request.form.get('options', '{}')
        options = json.loads(analysis_options) if analysis_options else {}
        
        # 查找文件
        file_path = None
        
        # 首先在watabou_dungeons目录中查找
        watabou_dir = Path(project_root) / 'watabou_dungeons'
        test_path = watabou_dir / filename
        if test_path.exists():
            file_path = test_path
        
        # 如果不在watabou_dungeons中，尝试其他目录
        if not file_path:
            samples_dir = Path(project_root) / 'samples'
            for subdir in ['watabou_test', 'source_test_1', 'source_format_1', 'source_format_2']:
                test_path = samples_dir / subdir / filename
                if test_path.exists():
                    file_path = test_path
                    break
        
        # 如果还是找不到，尝试在temp_uploads目录中查找（用户上传的文件）
        if not file_path:
            temp_dir = Path(project_root) / 'temp_uploads'
            test_path = temp_dir / filename
            if test_path.exists():
                file_path = test_path
        
        # 如果还是找不到，尝试在output目录中查找
        if not file_path:
            output_dir = Path(project_root) / 'output'
            for subdir in ['watabou_reports', 'watabou_reports2', 'watabou_test', 'edger', 'chat_ana']:
                test_path = output_dir / subdir / filename
                if test_path.exists():
                    file_path = test_path
                    break
        
        if not file_path:
            return jsonify({
                'success': False,
                'error': f'找不到文件: {filename}'
            }), 404
        
        try:
            # 读取文件数据
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 使用现有的适配器管理器处理文件
            unified_data = adapter_manager.convert(data)
            
            if unified_data is None:
                return jsonify({
                    'success': False,
                    'error': '无法识别或转换文件格式'
                }), 400
            
            # 使用质量评估器进行分析
            assessment_result = quality_assessor.assess_quality(unified_data)
            
            return jsonify({
                'success': True,
                'result': assessment_result,
                'unified_data': unified_data,
                'filename': filename
            })
            
        except Exception as e:
            raise e
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/visualize-data-by-filename', methods=['POST'])
def get_visualization_data_by_filename():
    """通过文件名获取地下城可视化数据（向后兼容）"""
    try:
        # 获取文件名
        filename = request.form.get('filename')
        if not filename:
            return jsonify({'error': '没有提供文件名'}), 400
        
        # 查找文件
        file_path = None
        
        # 首先在watabou_dungeons目录中查找
        watabou_dir = Path(project_root) / 'watabou_dungeons'
        test_path = watabou_dir / filename
        if test_path.exists():
            file_path = test_path
        
        # 如果不在watabou_dungeons中，尝试其他目录
        if not file_path:
            samples_dir = Path(project_root) / 'samples'
            for subdir in ['watabou_test', 'source_test_1', 'source_format_1', 'source_format_2']:
                test_path = samples_dir / subdir / filename
                if test_path.exists():
                    file_path = test_path
                    break
        
        # 如果还是找不到，尝试在temp_uploads目录中查找（用户上传的文件）
        if not file_path:
            temp_dir = Path(project_root) / 'temp_uploads'
            test_path = temp_dir / filename
            if test_path.exists():
                file_path = test_path
        
        # 如果还是找不到，尝试在output目录中查找
        if not file_path:
            output_dir = Path(project_root) / 'output'
            for subdir in ['watabou_reports', 'watabou_reports2', 'watabou_test', 'edger', 'chat_ana']:
                test_path = output_dir / subdir / filename
                if test_path.exists():
                    file_path = test_path
                    break
        
        if not file_path:
            return jsonify({
                'success': False,
                'error': f'找不到文件: {filename}'
            }), 404
        
        try:
            # 读取文件数据
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 使用现有的适配器管理器处理文件
            unified_data = adapter_manager.convert(data)
            
            if unified_data is None:
                return jsonify({
                    'success': False,
                    'error': '无法识别或转换文件格式'
                }), 400
            
            # 转换为前端可用的格式
            from src.visualizer import DungeonVisualizer
            visualizer = DungeonVisualizer()
            
            # 提取可视化数据
            visualization_data = visualizer._extract_visualization_data(unified_data)
            
            return jsonify({
                'success': True,
                'visualization_data': visualization_data,
                'unified_data': unified_data,
                'filename': filename
            })
            
        except Exception as e:
            raise e
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/visualize-by-filename', methods=['POST'])
def visualize_dungeon_by_filename():
    """通过文件名生成地下城可视化图像（向后兼容）"""
    try:
        # 获取文件名
        filename = request.form.get('filename')
        if not filename:
            return jsonify({'error': '没有提供文件名'}), 400
        
        # 获取可视化选项
        visualization_options = request.form.get('options', '{}')
        options = json.loads(visualization_options) if visualization_options else {}
        
        # 查找文件
        file_path = None
        
        # 首先在watabou_dungeons目录中查找
        watabou_dir = Path(project_root) / 'watabou_dungeons'
        test_path = watabou_dir / filename
        if test_path.exists():
            file_path = test_path
        
        # 如果不在watabou_dungeons中，尝试其他目录
        if not file_path:
            samples_dir = Path(project_root) / 'samples'
            for subdir in ['watabou_test', 'source_test_1', 'source_format_1', 'source_format_2']:
                test_path = samples_dir / subdir / filename
                if test_path.exists():
                    file_path = test_path
                    break
        
        # 如果还是找不到，尝试在temp_uploads目录中查找（用户上传的文件）
        if not file_path:
            temp_dir = Path(project_root) / 'temp_uploads'
            test_path = temp_dir / filename
            if test_path.exists():
                file_path = test_path
        
        # 如果还是找不到，尝试在output目录中查找
        if not file_path:
            output_dir = Path(project_root) / 'output'
            for subdir in ['watabou_reports', 'watabou_reports2', 'watabou_test', 'edger', 'chat_ana']:
                test_path = output_dir / subdir / filename
                if test_path.exists():
                    file_path = test_path
                    break
        
        if not file_path:
            return jsonify({
                'success': False,
                'error': f'找不到文件: {filename}'
            }), 404
        
        try:
            # 读取文件数据
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 使用现有的适配器管理器处理文件
            unified_data = adapter_manager.convert(data)
            
            if unified_data is None:
                return jsonify({
                    'success': False,
                    'error': '无法识别或转换文件格式'
                }), 400
            
            # 生成可视化图像
            from src.visualizer import visualize_dungeon
            upload_dir = Path(project_root) / 'temp_uploads'
            upload_dir.mkdir(exist_ok=True)
            output_path = upload_dir / f"{Path(filename).stem}_visualization.png"
            
            success = visualize_dungeon(
                unified_data, 
                str(output_path),
                show_connections=options.get('show_connections', True),
                show_room_ids=options.get('show_room_ids', True),
                show_grid=options.get('show_grid', True),
                show_game_elements=options.get('show_game_elements', True)
            )
            
            if success and output_path.exists():
                # 读取生成的图像文件并转换为base64
                import base64
                with open(output_path, 'rb') as img_file:
                    img_data = base64.b64encode(img_file.read()).decode('utf-8')
                
                # 清理临时文件
                output_path.unlink()
                
                return jsonify({
                    'success': True,
                    'image_data': img_data,
                    'unified_data': unified_data,
                    'filename': filename
                })
            else:
                return jsonify({
                    'success': False,
                    'error': '可视化生成失败'
                }), 500
            
        except Exception as e:
            raise e
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyze-batch', methods=['POST'])
def analyze_batch():
    """批量分析地下城文件"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400
        
        files = request.files.getlist('files')
        if not files or files[0].filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        # 获取分析选项
        analysis_options = request.form.get('options', '{}')
        options = json.loads(analysis_options) if analysis_options else {}
        
        # 保存上传的文件
        upload_dir = Path(project_root) / 'temp_uploads'
        upload_dir.mkdir(exist_ok=True)
        
        file_paths = []
        try:
            for file in files:
                # 只使用文件名，不包含路径
                filename = Path(file.filename).name
                file_path = upload_dir / filename
                file.save(str(file_path))
                file_paths.append(file_path)
            
            # 使用批量评估函数
            # 创建临时目录结构
            temp_input_dir = Path(project_root) / 'temp_uploads'
            temp_output_dir = Path(project_root) / 'temp_reports'
            temp_output_dir.mkdir(exist_ok=True)
            
            # 调用批量评估函数
            results = assess_all_maps(
                input_dir=str(temp_input_dir),
                output_dir=str(temp_output_dir)
            )
            
            return jsonify({
                'success': True,
                'results': results
            })
            
        finally:
            # 清理临时文件
            for file_path in file_paths:
                if file_path.exists():
                    file_path.unlink()
                    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/supported-formats', methods=['GET'])
def get_supported_formats():
    """获取支持的文件格式"""
    return jsonify({
        'formats': [
            'JSON',
            'Watabou',
            'Donjon',
            'DungeonDraft',
            'Edgar'
        ]
    })

@app.route('/api/analysis-options', methods=['GET'])
def get_analysis_options():
    """获取可用的分析选项"""
    return jsonify({
        'options': {
            'accessibility': {
                'name': '可达性分析',
                'description': '分析地下城的可达性和路径设计',
                'enabled': True
            },
            'geometric_balance': {
                'name': '几何平衡',
                'description': '评估房间布局的几何平衡性',
                'enabled': True
            },
            'loop_ratio': {
                'name': '环路比例',
                'description': '分析环路设计，避免线性体验',
                'enabled': True
            },
            'dead_end_ratio': {
                'name': '死胡同比例',
                'description': '评估死胡同的数量和分布',
                'enabled': True
            },
            'treasure_distribution': {
                'name': '宝藏分布',
                'description': '分析宝藏的位置和分布合理性',
                'enabled': True
            },
            'monster_distribution': {
                'name': '怪物分布',
                'description': '评估怪物的分布和挑战平衡',
                'enabled': True
            }
        }
    })

@app.route('/api/convert-dungeon', methods=['POST'])
def convert_dungeon():
    """转换地下城格式"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400
        
        file = request.files['file']
        target_format = request.form.get('target_format', 'unified')
        
        # 保存上传的文件
        upload_dir = Path(project_root) / 'temp_uploads'
        upload_dir.mkdir(exist_ok=True)
        
        # 只使用文件名，不包含路径
        filename = Path(file.filename).name
        file_path = upload_dir / filename
        file.save(str(file_path))
        
        try:
            # 使用适配器管理器转换格式
            unified_data = adapter_manager.adapt_file(str(file_path))
            
            # 清理临时文件
            file_path.unlink()
            
            return jsonify({
                'success': True,
                'converted_data': unified_data,
                'original_format': file.filename.split('.')[-1],
                'target_format': target_format
            })
            
        except Exception as e:
            # 清理临时文件
            if file_path.exists():
                file_path.unlink()
            raise e
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/visualize', methods=['POST'])
def visualize_dungeon():
    """生成地下城可视化图像"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        # 获取可视化选项
        visualization_options = request.form.get('options', '{}')
        options = json.loads(visualization_options) if visualization_options else {}
        
        # 保存上传的文件
        upload_dir = Path(project_root) / 'temp_uploads'
        upload_dir.mkdir(exist_ok=True)
        
        # 只使用文件名，不包含路径
        filename = Path(file.filename).name
        file_path = upload_dir / filename
        file.save(str(file_path))
        
        try:
            # 读取文件数据
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 使用现有的适配器管理器处理文件
            unified_data = adapter_manager.convert(data)
            
            if unified_data is None:
                return jsonify({
                    'success': False,
                    'error': '无法识别或转换文件格式'
                }), 400
            
            # 生成可视化图像
            from src.visualizer import visualize_dungeon
            output_path = upload_dir / f"{Path(file.filename).stem}_visualization.png"
            
            success = visualize_dungeon(
                unified_data, 
                str(output_path),
                show_connections=options.get('show_connections', True),
                show_room_ids=options.get('show_room_ids', True),
                show_grid=options.get('show_grid', True),
                show_game_elements=options.get('show_game_elements', True)
            )
            
            if success and output_path.exists():
                # 读取生成的图像文件并转换为base64
                import base64
                with open(output_path, 'rb') as img_file:
                    img_data = base64.b64encode(img_file.read()).decode('utf-8')
                
                # 清理临时文件
                output_path.unlink()
                file_path.unlink()
                
                return jsonify({
                    'success': True,
                    'image_data': img_data,
                    'unified_data': unified_data,
                    'filename': file.filename
                })
            else:
                # 清理临时文件
                file_path.unlink()
                return jsonify({
                    'success': False,
                    'error': '可视化生成失败'
                }), 500
            
        except Exception as e:
            # 清理临时文件
            if file_path.exists():
                file_path.unlink()
            raise e
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/visualize-data', methods=['POST'])
def get_visualization_data():
    """获取地下城可视化数据（用于前端渲染）"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        # 保存上传的文件
        upload_dir = Path(project_root) / 'temp_uploads'
        upload_dir.mkdir(exist_ok=True)
        
        # 只使用文件名，不包含路径
        filename = Path(file.filename).name
        file_path = upload_dir / filename
        file.save(str(file_path))
        
        try:
            # 读取文件数据
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 使用现有的适配器管理器处理文件
            unified_data = adapter_manager.convert(data)
            
            if unified_data is None:
                return jsonify({
                    'success': False,
                    'error': '无法识别或转换文件格式'
                }), 400
            
            # 转换为前端可用的格式
            from src.visualizer import DungeonVisualizer
            visualizer = DungeonVisualizer()
            
            # 提取可视化数据
            visualization_data = visualizer._extract_visualization_data(unified_data)
            
            # 清理临时文件
            file_path.unlink()
            
            return jsonify({
                'success': True,
                'visualization_data': visualization_data,
                'unified_data': unified_data,
                'filename': file.filename
            })
            
        except Exception as e:
            # 清理临时文件
            if file_path.exists():
                file_path.unlink()
            raise e
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/batch-test', methods=['POST'])
def batch_test():
    """批量测试接口 - 评估多个地下城文件"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400
        
        files = request.files.getlist('files')
        if not files:
            return jsonify({'error': '没有选择文件'}), 400
        
        # 获取测试选项
        test_options = request.form.get('options', '{}')
        options = json.loads(test_options) if test_options else {}
        
        # 创建临时目录存储文件
        import tempfile
        import shutil
        
        temp_dir = tempfile.mkdtemp()
        output_dir = os.path.join(temp_dir, 'reports')
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            # 保存上传的文件到临时目录
            file_paths = []
            for file in files:
                if file.filename and file.filename.endswith('.json'):
                    file_path = os.path.join(temp_dir, file.filename)
                    file.save(file_path)
                    file_paths.append(file_path)
            
            if not file_paths:
                return jsonify({'error': '没有有效的JSON文件'}), 400
            
            # 执行批量评估
            from src.batch_assess import batch_assess_files
            results = batch_assess_files(file_paths, output_dir, timeout_per_file=30)
            
            # 读取生成的报告文件
            summary_file = os.path.join(output_dir, "batch_assessment_summary.json")
            summary_data = {}
            if os.path.exists(summary_file):
                with open(summary_file, 'r', encoding='utf-8') as f:
                    summary_data = json.load(f)
            
            # 清理临时文件
            shutil.rmtree(temp_dir)
            
            return jsonify({
                'success': True,
                'message': f'批量测试完成，共处理 {len(file_paths)} 个文件',
                'results': results,
                'summary': summary_data,
                'total_files': len(file_paths),
                'successful_files': len([r for r in results.values() if r.get('status') == 'success']),
                'failed_files': len([r for r in results.values() if r.get('status') != 'success'])
            })
            
        except Exception as e:
            # 清理临时文件
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            raise e
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'批量测试失败: {str(e)}'
        }), 500

@app.route('/api/batch-test-directory', methods=['POST'])
def batch_test_directory():
    """批量测试目录接口 - 评估指定目录中的所有JSON文件"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '没有提供数据'}), 400
        
        input_dir = data.get('input_directory')
        if not input_dir:
            return jsonify({'error': '没有指定输入目录'}), 400
        
        if not os.path.exists(input_dir):
            return jsonify({'error': f'目录不存在: {input_dir}'}), 400
        
        # 获取测试选项
        options = data.get('options', {})
        timeout_per_file = options.get('timeout', 30)
        
        # 创建输出目录
        output_dir = data.get('output_directory', 'temp_reports')
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            # 执行批量评估
            from src.batch_assess import batch_assess_quality
            results = batch_assess_quality(
                input_dir=input_dir,
                output_dir=output_dir,
                timeout_per_file=timeout_per_file
            )
            
            # 读取生成的汇总报告
            summary_file = os.path.join(output_dir, "quality_summary_report.json")
            summary_data = {}
            if os.path.exists(summary_file):
                with open(summary_file, 'r', encoding='utf-8') as f:
                    summary_data = json.load(f)
            
            return jsonify({
                'success': True,
                'message': f'批量测试完成，目录: {input_dir}',
                'results': results,
                'summary': summary_data,
                'input_directory': input_dir,
                'output_directory': output_dir
            })
            
        except Exception as e:
            raise e
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'批量测试失败: {str(e)}'
        }), 500

@app.route('/api/batch-test-status', methods=['GET'])
def batch_test_status():
    """获取批量测试状态"""
    return jsonify({
        'success': True,
        'status': 'ready',
        'message': '批量测试服务正常运行',
        'supported_features': [
            'multiple_file_upload',
            'directory_processing',
            'timeout_control',
            'detailed_reports',
            'summary_statistics'
        ]
    })

@app.route('/api/generate-improvement-suggestions', methods=['POST'])
def generate_improvement_suggestions():
    """根据分析结果生成详细的改进建议"""
    try:
        file_id = request.form.get('file_id')
        scores_data = request.form.get('scores', '{}')
        
        if not file_id or file_id not in file_cache:
            return jsonify({'error': '文件ID无效或已过期'}), 404
        
        scores = json.loads(scores_data) if scores_data else {}
        
        # 生成改进建议
        suggestions = []
        
        # 分析各项指标并生成针对性建议
        for metric, score_data in scores.items():
            if isinstance(score_data, dict) and 'score' in score_data:
                score = score_data['score']
                detail = score_data.get('detail', {})
                
                if score < 0.6:  # 低分指标需要改进
                    suggestion = generate_metric_suggestion(metric, score, detail)
                    if suggestion:
                        suggestions.append(suggestion)
        
        # 按优先级排序
        suggestions.sort(key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x['priority']], reverse=True)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'total_count': len(suggestions),
            'high_priority_count': len([s for s in suggestions if s['priority'] == 'high']),
            'medium_priority_count': len([s for s in suggestions if s['priority'] == 'medium']),
            'low_priority_count': len([s for s in suggestions if s['priority'] == 'low'])
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def generate_metric_suggestion(metric, score, detail):
    """为特定指标生成改进建议"""
    suggestions_map = {
        'dead_end_ratio': {
            'title': '减少死胡同设计',
            'description': '当前地牢存在过多死胡同，可能导致玩家感到挫败或探索体验单调。',
            'priority': 'high' if score < 0.3 else 'medium',
            'category': '布局优化',
            'actions': [
                '将部分死胡同连接到其他区域',
                '在死胡同末端放置有价值的奖励',
                '创建循环路径替代直线通道',
                '增加隐藏通道或秘密房间'
            ],
            'expected_improvement': '提升探索流畅性，减少玩家挫败感'
        },
        'geometric_balance': {
            'title': '优化空间布局平衡',
            'description': '地牢的几何布局不够平衡，可能影响视觉美感和游戏体验。',
            'priority': 'medium' if score < 0.4 else 'low',
            'category': '视觉设计',
            'actions': [
                '调整房间大小比例，避免过大或过小的房间',
                '优化房间分布，创造更好的视觉平衡',
                '确保主要区域的对称性或有序性',
                '合理安排重要房间的位置'
            ],
            'expected_improvement': '提升地牢美观度和空间感'
        },
        'treasure_monster_distribution': {
            'title': '优化奖励分布策略',
            'description': '宝藏和怪物的分布可能不够合理，影响游戏平衡性和探索动机。',
            'priority': 'high',
            'category': '游戏平衡',
            'actions': [
                '确保高价值奖励伴随相应的挑战',
                '在探索路径上合理分布小奖励',
                '避免奖励过于集中或分散',
                '根据地牢深度调整奖励价值'
            ],
            'expected_improvement': '提升游戏平衡性和探索动机'
        },
        'accessibility': {
            'title': '改善区域连通性',
            'description': '部分区域的可达性存在问题，可能导致玩家无法到达某些重要位置。',
            'priority': 'high',
            'category': '连通性',
            'actions': [
                '检查并修复断开的连接',
                '增加备用路径到达重要区域',
                '确保所有房间都可以从入口到达',
                '考虑添加快捷通道或传送点'
            ],
            'expected_improvement': '确保完整的探索体验'
        },
        'path_diversity': {
            'title': '增加路径选择多样性',
            'description': '当前地牢的路径选择较为单一，缺乏探索的策略性和趣味性。',
            'priority': 'medium',
            'category': '探索体验',
            'actions': [
                '创建多条通往目标的路径',
                '设计分支路径和可选区域',
                '增加需要特殊钥匙或技能的路径',
                '平衡不同路径的风险和奖励'
            ],
            'expected_improvement': '提升探索策略性和重玩价值'
        },
        'loop_ratio': {
            'title': '增加循环路径设计',
            'description': '地牢缺乏足够的环路设计，可能导致线性化的探索体验。',
            'priority': 'medium',
            'category': '布局优化',
            'actions': [
                '连接现有的死胡同形成环路',
                '设计大型循环区域',
                '创建多层次的环路结构',
                '确保环路有明确的游戏目的'
            ],
            'expected_improvement': '提升探索流畅性和导航便利性'
        },
        'degree_variance': {
            'title': '优化连接度分布',
            'description': '房间连接度的变化不够丰富，可能影响地牢的复杂性和探索体验。',
            'priority': 'low',
            'category': '结构优化',
            'actions': [
                '创建具有不同连接数的房间',
                '设计中心枢纽房间',
                '平衡简单通道和复杂交叉点',
                '确保重要房间有多个入口'
            ],
            'expected_improvement': '增加地牢结构的复杂性和趣味性'
        }
    }
    
    if metric in suggestions_map:
        suggestion = suggestions_map[metric].copy()
        suggestion['metric'] = metric
        suggestion['current_score'] = score
        suggestion['target_score'] = 0.7 if score < 0.7 else 0.8
        
        # 根据详细信息调整建议
        if detail and isinstance(detail, dict):
            suggestion['detail_info'] = detail
        
        return suggestion
    
    return None



@app.route('/api/statistical-analysis-report', methods=['GET'])  
def statistical_analysis_report():
    """获取统计分析报告数据"""
    try:
        report_path = os.path.join(project_root, 'output', 'statistical_analysis_report.json')
        
        if os.path.exists(report_path):
            with open(report_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            
            return jsonify({
                'success': True,
                'data': report_data
            })
        else:
            return jsonify({
                'success': False,
                'error': '统计分析报告文件不存在'
            }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'读取统计分析报告失败: {str(e)}'
        }), 500

@app.route('/api/correlation-data', methods=['GET'])
def get_correlation_data():
    """获取相关性分析数据"""
    try:
        report_path = os.path.join(project_root, 'output', 'statistical_analysis_report.json')
        
        if os.path.exists(report_path):
            with open(report_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            
            correlation_analysis = report_data.get('correlation_analysis', {})
            analysis_summary = report_data.get('analysis_summary', {})
            
            # 构建前端需要的数据格式
            correlation_data = {
                'totalDungeons': analysis_summary.get('total_maps', 0),
                'totalMetrics': analysis_summary.get('metrics_analyzed', 0),
                'strongCorrelations': analysis_summary.get('strong_correlations_count', 0),
                'metrics': correlation_analysis.get('metric_names', []),
                'correlationMatrix': [],
                'strongPairs': [],
                'moderatePairs': [],
                'metricStats': {},
                'lastUpdate': report_data.get('timestamp', '')
            }
            
            # 转换相关性矩阵
            pearson_matrix = correlation_analysis.get('pearson_correlation_matrix', {})
            if pearson_matrix:
                metric_names = correlation_analysis.get('metric_names', [])
                correlation_matrix = []
                for metric1 in metric_names:
                    row = []
                    for metric2 in metric_names:
                        row.append(pearson_matrix.get(metric1, {}).get(metric2, 0))
                    correlation_matrix.append(row)
                correlation_data['correlationMatrix'] = correlation_matrix
            
            # 转换强相关和中等相关数据
            strong_correlations = correlation_analysis.get('strong_correlations', [])
            for corr in strong_correlations:
                correlation_data['strongPairs'].append({
                    'pair': f"{corr['metric1']} ↔ {corr['metric2']}",
                    'value': corr['pearson_correlation']
                })
            
            moderate_correlations = correlation_analysis.get('moderate_correlations', [])
            for corr in moderate_correlations:
                correlation_data['moderatePairs'].append({
                    'pair': f"{corr['metric1']} ↔ {corr['metric2']}",
                    'value': corr['pearson_correlation']
                })
            
            # 计算指标统计
            if correlation_matrix and metric_names:
                for i, metric in enumerate(metric_names):
                    row = correlation_matrix[i]
                    correlations = [abs(val) for j, val in enumerate(row) if i != j]
                    if correlations:
                        correlation_data['metricStats'][metric] = {
                            'avg_correlation': sum(correlations) / len(correlations),
                            'max_correlation': max(correlations),
                            'min_correlation': min([val for val in correlations if val > 0], default=0)
                        }
            
            return jsonify(correlation_data)
        else:
            return jsonify({
                'success': False,
                'error': '统计分析报告文件不存在'
            }), 404
    
    except Exception as e:
        logger.error(f"获取相关性数据失败: {e}")
        return jsonify({
            'success': False,
            'error': f'获取相关性数据失败: {str(e)}'
        }), 500

@app.route('/api/refresh-correlation', methods=['POST'])
def refresh_correlation():
    """刷新相关性分析数据"""
    try:
        # 这里可以触发重新生成统计分析报告的逻辑
        # 暂时返回成功状态
        return jsonify({
            'success': True,
            'message': '相关性分析数据刷新成功'
        })
    except Exception as e:
        logger.error(f"刷新相关性数据失败: {e}")
        return jsonify({
            'success': False,
            'error': f'刷新相关性数据失败: {str(e)}'
        }), 500

@app.route('/api/correlation-charts', methods=['GET'])
def get_correlation_charts():
    """获取相关性分析图表"""
    try:
        report_path = os.path.join(project_root, 'output', 'statistical_analysis_report.json')
        
        if os.path.exists(report_path):
            with open(report_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            
            charts = report_data.get('charts', {})
            
            if charts:
                return jsonify({
                    'success': True,
                    'charts': charts,
                    'data': report_data.get('correlation_analysis', {}),
                    'timestamp': report_data.get('timestamp', '')
                })
            else:
                return jsonify({
                    'success': False,
                    'error': '图表数据不可用'
                }), 404
        else:
            return jsonify({
                'success': False,
                'error': '统计分析报告文件不存在'
            }), 404
    
    except Exception as e:
        logger.error(f"获取图表失败: {e}")
        return jsonify({
            'success': False,
            'error': f'获取图表失败: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 