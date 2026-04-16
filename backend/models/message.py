"""
Message Model - ORM映射消息提醒表 (message_table)

该模型类对应数据库中的message_table表，用于存储所有提醒消息记录。
"""

from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import BigInteger, Column, Integer, String, TIMESTAMP, JSON, Index
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Message(Base):
    """
    消息提醒模型类
    
    存储所有提醒消息记录，包括规则代码、标题、待处理数量、状态等信息。
    
    Attributes:
        id: 主键，自增
        rule_code: 规则代码，如CHK_TRD_004
        title: 提醒标题
        count: 待处理数量
        last_updated: 最后更新时间
        status: 扫描状态（success/timeout/error）
        priority: 优先级（normal/high/critical）
        target_roles: 目标接收人角色列表（JSON格式）
        metadata_: 扩展元数据（JSON格式，数据库列名为metadata）
        created_at: 创建时间
        updated_at: 更新时间
    """
    
    __tablename__ = 'message_table'
    
    # 主键 - Use Integer for SQLite compatibility, BigInteger for PostgreSQL
    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True, comment='主键，自增')
    
    # 规则信息
    rule_code = Column(String(50), nullable=False, comment='规则代码，如CHK_TRD_004')
    title = Column(String(200), nullable=False, comment='提醒标题')
    
    # 统计信息
    count = Column(Integer, nullable=False, comment='待处理数量')
    last_updated = Column(TIMESTAMP, nullable=False, comment='最后更新时间')
    
    # 状态信息
    status = Column(String(20), nullable=False, comment='扫描状态：success/timeout/error')
    priority = Column(String(20), nullable=False, comment='优先级：normal/high/critical')
    
    # 目标接收人和扩展信息
    target_roles = Column(JSON, nullable=False, comment='目标接收人角色列表（JSON格式）')
    metadata_ = Column('metadata', JSON, nullable=True, comment='扩展元数据（JSON格式）')
    
    # 审计字段
    created_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.current_timestamp(),
        comment='创建时间'
    )
    updated_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        comment='更新时间'
    )
    
    # 索引定义
    __table_args__ = (
        Index('idx_rule_code', 'rule_code'),
        Index('idx_last_updated', 'last_updated'),
        Index('idx_status', 'status'),
        {'comment': '消息提醒表，存储所有提醒消息记录'}
    )
    
    def __repr__(self) -> str:
        """字符串表示"""
        return (
            f"<Message(id={self.id}, rule_code='{self.rule_code}', "
            f"title='{self.title}', count={self.count}, status='{self.status}')>"
        )
    
    def to_dict(self) -> Dict:
        """
        转换为字典格式
        
        Returns:
            Dict: 包含所有字段的字典
        """
        return {
            'id': self.id,
            'rule_code': self.rule_code,
            'title': self.title,
            'count': self.count,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'status': self.status,
            'priority': self.priority,
            'target_roles': self.target_roles,
            'metadata': self.metadata_,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
