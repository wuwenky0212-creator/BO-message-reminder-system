"""
Position Model - ORM映射持仓表 (position_table)

该模型类对应数据库中的position_table表，用于存储债券持仓头寸数据。
"""

from datetime import datetime
from typing import Dict, Optional

from sqlalchemy import BigInteger, Column, Integer, String, TIMESTAMP, Numeric, Index
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Position(Base):
    """
    持仓模型类
    
    存储债券持仓头寸数据，包括证券代码、可用数量、交收日期等信息。
    
    Attributes:
        id: 主键，自增
        security_code: 证券代码
        security_name: 证券名称
        available_balance: 可用数量（负数表示卖空）
        settlement_date: 交收日期（T/T+1）
        portfolio_code: 投资组合代码
        portfolio_name: 投资组合名称
        security_type: 证券类型（Stock/Bond/Fund）
        market_value: 市值
        currency: 币种
        org_id: 机构ID
        created_at: 创建时间
        updated_at: 更新时间
    """
    
    __tablename__ = 'position_table'
    
    # 主键 - Use Integer for SQLite compatibility, BigInteger for PostgreSQL
    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True, comment='主键，自增')
    
    # 证券信息
    security_code = Column(String(50), nullable=False, comment='证券代码')
    security_name = Column(String(200), nullable=False, comment='证券名称')
    security_type = Column(String(50), nullable=False, comment='证券类型：Stock/Bond/Fund')
    
    # 持仓信息
    available_balance = Column(Numeric(20, 2), nullable=False, comment='可用数量（负数表示卖空）')
    market_value = Column(Numeric(20, 2), nullable=False, comment='市值')
    currency = Column(String(10), nullable=False, default='CNY', comment='币种')
    
    # 交收信息
    settlement_date = Column(String(10), nullable=False, comment='交收日期：T/T+1')
    
    # 投资组合信息
    portfolio_code = Column(String(50), nullable=False, comment='投资组合代码')
    portfolio_name = Column(String(200), nullable=False, comment='投资组合名称')
    
    # 机构信息
    org_id = Column(String(50), nullable=False, comment='机构ID')
    
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
        Index('idx_security_code', 'security_code'),
        Index('idx_settlement_date', 'settlement_date'),
        Index('idx_portfolio_code', 'portfolio_code'),
        Index('idx_org_id', 'org_id'),
        Index('idx_available_balance', 'available_balance'),
        {'comment': '持仓表，存储债券持仓头寸数据'}
    )
    
    def __repr__(self) -> str:
        """字符串表示"""
        return (
            f"<Position(id={self.id}, security_code='{self.security_code}', "
            f"available_balance={self.available_balance}, settlement_date='{self.settlement_date}')>"
        )
    
    def to_dict(self) -> Dict:
        """
        转换为字典格式
        
        Returns:
            Dict: 包含所有字段的字典
        """
        return {
            'id': self.id,
            'security_code': self.security_code,
            'security_name': self.security_name,
            'security_type': self.security_type,
            'available_balance': float(self.available_balance) if self.available_balance else 0.0,
            'market_value': float(self.market_value) if self.market_value else 0.0,
            'currency': self.currency,
            'settlement_date': self.settlement_date,
            'portfolio_code': self.portfolio_code,
            'portfolio_name': self.portfolio_name,
            'org_id': self.org_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
