"""
AuditLog Model - ORM映射审计日志表 (audit_log)

该模型类对应数据库中的audit_log表，用于记录提醒处理闭环和敏感数据查询操作。
"""

from datetime import datetime
from typing import Dict, Optional

from sqlalchemy import BigInteger, Column, Integer, String, Text, TIMESTAMP, Index
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class AuditLog(Base):
    """
    审计日志模型类
    
    记录提醒处理闭环和敏感数据查询操作，包括事件类型、用户信息、操作信息、数量变化等。
    
    Attributes:
        id: 主键，自增
        log_id: 日志唯一标识
        event_type: 事件类型
        rule_code: 关联的规则代码
        user_id: 操作用户ID
        user_name: 操作用户姓名
        operation_type: 操作类型
        business_id: 业务单据ID
        count_before: 操作前的提醒数量
        count_after: 操作后的提醒数量
        ip_address: 用户IP地址
        user_agent: 用户浏览器信息
        timestamp: 操作时间戳
        created_at: 创建时间
    """
    
    __tablename__ = 'audit_log'
    
    # 主键 - Use Integer for SQLite compatibility, BigInteger for PostgreSQL
    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True, comment='主键，自增')
    
    # 日志标识
    log_id = Column(String(100), nullable=False, unique=True, comment='日志唯一标识')
    
    # 事件信息
    event_type = Column(String(50), nullable=False, comment='事件类型')
    rule_code = Column(String(50), nullable=True, comment='关联的规则代码')
    
    # 用户信息
    user_id = Column(String(100), nullable=False, comment='操作用户ID')
    user_name = Column(String(200), nullable=False, comment='操作用户姓名')
    
    # 操作信息
    operation_type = Column(String(50), nullable=True, comment='操作类型')
    business_id = Column(String(100), nullable=True, comment='业务单据ID')
    
    # 数量变化
    count_before = Column(Integer, nullable=True, comment='操作前的提醒数量')
    count_after = Column(Integer, nullable=True, comment='操作后的提醒数量')
    
    # 请求信息
    ip_address = Column(String(50), nullable=True, comment='用户IP地址')
    user_agent = Column(String(500), nullable=True, comment='用户浏览器信息')
    
    # 时间戳
    timestamp = Column(TIMESTAMP, nullable=False, comment='操作时间戳')
    created_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.current_timestamp(),
        comment='创建时间'
    )
    
    # 索引定义
    __table_args__ = (
        Index('uk_log_id', 'log_id', unique=True),
        Index('idx_event_type', 'event_type'),
        Index('idx_rule_code', 'rule_code'),
        Index('idx_user_id', 'user_id'),
        Index('idx_timestamp', 'timestamp'),
        {'comment': '审计日志表，记录提醒处理闭环和敏感数据查询操作'}
    )
    
    def __repr__(self) -> str:
        """字符串表示"""
        return (
            f"<AuditLog(id={self.id}, log_id='{self.log_id}', "
            f"event_type='{self.event_type}', user_id='{self.user_id}')>"
        )
    
    def to_dict(self) -> Dict:
        """
        转换为字典格式
        
        Returns:
            Dict: 包含所有字段的字典
        """
        return {
            'id': self.id,
            'log_id': self.log_id,
            'event_type': self.event_type,
            'rule_code': self.rule_code,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'operation_type': self.operation_type,
            'business_id': self.business_id,
            'count_before': self.count_before,
            'count_after': self.count_after,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
