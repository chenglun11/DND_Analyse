from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import sys
from pathlib import Path

# 导入现有的地下城分析模块（使用本地复制的src）
from src.adapter_manager import AdapterManager
from src.quality_assessor import DungeonQualityAssessor
from src.batch_assess import assess_all_maps

# 定义项目根目录
project_root = Path(__file__).parent.parent

app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 初始化适配器管理器和质量评估器
adapter_manager = AdapterManager()
quality_assessor = DungeonQualityAssessor()

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'message': 'Dungeon Analyzer API is running'
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
        
        # 获取分析选项
        analysis_options = request.form.get('options', '{}')
        options = json.loads(analysis_options) if analysis_options else {}
        
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
            
            # 使用质量评估器进行分析
            assessment_result = quality_assessor.assess_quality(unified_data)
            
            # 清理临时文件
            file_path.unlink()
            
            return jsonify({
                'success': True,
                'result': assessment_result,
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

@app.route('/api/analyze-by-filename', methods=['POST'])
def analyze_dungeon_by_filename():
    """通过文件名分析地下城文件"""
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
            for subdir in ['watabou_reports', 'watabou_reports2', 'watabou_test']:
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
            'aesthetic_balance': {
                'name': '美学平衡',
                'description': '评估房间布局的美观性和平衡性',
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

@app.route('/api/visualize-data-by-filename', methods=['POST'])
def get_visualization_data_by_filename():
    """通过文件名获取地下城可视化数据"""
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
            for subdir in ['watabou_reports', 'watabou_reports2', 'watabou_test']:
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
    """通过文件名生成地下城可视化图像"""
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
            for subdir in ['watabou_reports', 'watabou_reports2', 'watabou_test']:
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 