#!/usr/bin/env python3
"""
Flask Backend Startup Script
"""

from app import app

if __name__ == '__main__':
    print("Starting Dungeon Analyzer Flask Backend...")
    print("API Address: http://localhost:5001")
    print("Health Check: http://localhost:5001/api/health")
    app.run(debug=True, host='0.0.0.0', port=5001) 