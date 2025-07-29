#!/usr/bin/env python3
"""
Flask后端启动脚本
"""

from app import app

if __name__ == '__main__':
    print("启动地下城分析器Flask后端...")
    print("API地址: http://localhost:5001")
    print("健康检查: http://localhost:5001/api/health")
    app.run(debug=True, host='0.0.0.0', port=5001) 