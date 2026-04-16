"""
TaskExecutionLog Model - ORM映射任务执行日志表 (task_execution_log)

该模型类对应数据库中的task_execution_log表，用于记录每次定时任务的执行情况。
"""

from datetime import datetime
from typing import Dict, Optional

from sqlalchemy import BigInteger, Column, Integer, String, Text, TIMESTAMP, Index
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class TaskExecutionLog(Base):
    """
    任务执行日志模型类
    
    记录每次定时任务的执行情况，包括任务标识、规则信息、执行时间、执行结果等。
    
    Attributes:
        id: 主键，自增
        task_id: 任务唯一标识
        rule_code: 规则代码，如CHK_TRD_004
        rule_name: 规则名称
        scheduled_time: 计划执行时间
        actual_start_time: 实际开始时间
        actual_end_time: 实际结束时间
        execution_duration: 执行时长（毫秒）
        status: 执行状态（completed/failed/timeout）
        record_count: 扫描到的记录数量
        error_message: 错误信息
        created_at: 创建时间
    """
    
    __tablename__ = 'task_execution_log'
    
    # 主键 - Use Integer for SQLite compatibility, BigInteger for PostgreSQL
    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True, comment='主键，自增')
    
    # 任务标识
    task_id = Column(String(100), nullable=False, unique=True, comment='任务唯一标识')
    
    # 规则信息
    rule_code = Column(String(50), nullable=False, comment='规则代码，如CHK_TRD_004')
    rule_name = Column(String(200), nullable=False, comment='规则名称')
    
    # 时间信息
    scheduled_time = Column(TIMESTAMP, nullable=False, comment='计划执行时间')
    actual_start_time = Column(TIMESTAMP, nullable=False, comment='实际开始时间')
    actual_end_time = Column(TIMESTAMP, nullable=True, comment='实际结束时间')
    execution_duration = Column(Integer, nullable=True, comment='执行时长（毫秒）')
    
    # 执行结果
    status = Column(String(20), nullable=False, comment='执行状态：completed/failed/timeout')
    record_count = Column(Integer, nullable=True, comment='扫描到的记录数量')
    error_message = Column(Text, nullable=True, comment='错误信息')
    
    # 审计字段
    created_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.current_timestamp(),
        comment='创建时间'
    )
    
    # 索引定义
    __table_args__ = (
        Index('uk_task_id', 'task_id', unique=True),
        Index('idx_rule_code', 'rule_code'),
        Index('idx_scheduled_time', 'scheduled_time'),
        Index('idx_status', 'status'),
        {'comment': '任务执行日志表，记录每次定时任务的执行情况'}
    )
    
    def __repr__(self) -> str:
        """字符串表示"""
        return (
            f"<TaskExecutionLog(id={self.id}, task_id='{self.task_id}', "
            f"rule_code='{self.rule_code}', status='{self.status}')>"
        )
    
    def to_dict(self) -> Dict:
        """
        转换为字典格式
        
        Returns:
            Dict: 包含所有字段的字典
        """
        return {
            'id': self.id,
            'task_id': self.task_id,
            'rule_code': self.rule_code,
            'rule_name': self.rule_name,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'actual_start_time': self.actual_start_time.isoformat() if self.actual_start_time else None,
            'actual_end_time': self.actual_end_time.isoformat() if self.actual_end_time else None,
            'execution_duration': self.execution_duration,
            'status': self.status,
            'record_count': self.record_count,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
