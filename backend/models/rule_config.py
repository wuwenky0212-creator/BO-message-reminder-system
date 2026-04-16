"""
RuleConfig Model - ORM映射规则配置表 (rule_config_table)

该模型类对应数据库中的rule_config_table表，用于存储提醒规则的配置信息。
"""

from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import BigInteger, Boolean, Column, Integer, String, Text, TIMESTAMP, JSON, Index
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class RuleConfig(Base):
    """
    规则配置模型类
    
    存储提醒规则的配置信息，包括规则代码、调度时间、目标角色、查询SQL等。
    
    Attributes:
        id: 主键，自增
        rule_code: 规则代码，如CHK_TRD_004，唯一
        rule_name: 规则名称
        scheduled_time: 执行时间（HH:MM格式）
        cron_expression: Cron表达式，用于定时任务调度
        target_roles: 接收人角色列表（JSON格式）
        enabled: 是否启用该规则
        description: 规则描述
        query_sql: 扫描SQL语句
        timeout_seconds: 查询超时时间（秒）
        created_at: 创建时间
        updated_at: 更新时间
        updated_by: 更新人
    """
    
    __tablename__ = 'rule_config_table'
    
    # 主键 - Use Integer for SQLite compatibility, BigInteger for PostgreSQL
    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True, comment='主键，自增')
    
    # 规则信息
    rule_code = Column(String(50), nullable=False, unique=True, comment='规则代码，如CHK_TRD_004，唯一')
    rule_name = Column(String(200), nullable=False, comment='规则名称')
    
    # 调度配置
    scheduled_time = Column(String(10), nullable=False, comment='执行时间（HH:MM格式）')
    cron_expression = Column(String(100), nullable=False, comment='Cron表达式，用于定时任务调度')
    
    # 目标接收人
    target_roles = Column(JSON, nullable=False, comment='接收人角色列表（JSON格式）')
    
    # 启用状态
    enabled = Column(Boolean, nullable=False, default=True, comment='是否启用该规则')
    
    # 规则描述和查询SQL
    description = Column(Text, nullable=True, comment='规则描述')
    query_sql = Column(Text, nullable=False, comment='扫描SQL语句')
    
    # 超时配置
    timeout_seconds = Column(Integer, nullable=False, default=10, comment='查询超时时间（秒）')
    
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
    updated_by = Column(String(100), nullable=True, comment='更新人')
    
    # 索引定义
    __table_args__ = (
        Index('uk_rule_code', 'rule_code', unique=True),
        Index('idx_enabled', 'enabled'),
        {'comment': '规则配置表，存储提醒规则的配置信息'}
    )
    
    def __repr__(self) -> str:
        """字符串表示"""
        return (
            f"<RuleConfig(id={self.id}, rule_code='{self.rule_code}', "
            f"rule_name='{self.rule_name}', enabled={self.enabled})>"
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
            'rule_name': self.rule_name,
            'scheduled_time': self.scheduled_time,
            'cron_expression': self.cron_expression,
            'target_roles': self.target_roles,
            'enabled': self.enabled,
            'description': self.description,
            'query_sql': self.query_sql,
            'timeout_seconds': self.timeout_seconds,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by,
        }
