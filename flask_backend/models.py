from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class AnalysisRecord(db.Model):
    """分析记录表"""
    __tablename__ = 'analysis_records'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_format = db.Column(db.String(50), nullable=False)
    overall_score = db.Column(db.Float, nullable=False)
    detailed_scores = db.Column(db.Text, nullable=False)  # JSON格式存储详细评分
    analysis_time = db.Column(db.Float, nullable=False)  # 分析耗时(秒)
    status = db.Column(db.String(20), default='success')  # success, failed
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'filename': self.filename,
            'file_size': self.file_size,
            'file_format': self.file_format,
            'overall_score': self.overall_score,
            'detailed_scores': json.loads(self.detailed_scores) if self.detailed_scores else {},
            'analysis_time': self.analysis_time,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SystemStats(db.Model):
    """系统统计表"""
    __tablename__ = 'system_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    total_analyses = db.Column(db.Integer, default=0)
    successful_analyses = db.Column(db.Integer, default=0)
    failed_analyses = db.Column(db.Integer, default=0)
    total_files_processed = db.Column(db.Integer, default=0)
    total_file_size = db.Column(db.BigInteger, default=0)  # 总文件大小(字节)
    average_analysis_time = db.Column(db.Float, default=0.0)
    average_score = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'total_analyses': self.total_analyses,
            'successful_analyses': self.successful_analyses,
            'failed_analyses': self.failed_analyses,
            'total_files_processed': self.total_files_processed,
            'total_file_size': self.total_file_size,
            'average_analysis_time': self.average_analysis_time,
            'average_score': self.average_score,
            'success_rate': (self.successful_analyses / self.total_analyses * 100) if self.total_analyses > 0 else 0,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }

class FileFormatStats(db.Model):
    """文件格式统计表"""
    __tablename__ = 'file_format_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    format_name = db.Column(db.String(50), nullable=False, unique=True)
    count = db.Column(db.Integer, default=0)
    average_score = db.Column(db.Float, default=0.0)
    last_used = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'format_name': self.format_name,
            'count': self.count,
            'average_score': self.average_score,
            'last_used': self.last_used.isoformat() if self.last_used else None
        } 