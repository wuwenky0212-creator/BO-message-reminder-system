"""
Unit tests for AuditLog model

测试AuditLog模型类的所有功能，包括字段定义、索引、方法等。
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.audit_log import AuditLog, Base


@pytest.fixture
def engine():
    """创建内存数据库引擎"""
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    """创建数据库会话"""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestAuditLogModel:
    """AuditLog模型测试类"""
    
    def test_table_name(self):
        """测试表名是否正确"""
        assert AuditLog.__tablename__ == 'audit_log'
    
    def test_columns_exist(self, engine):
        """测试所有列是否存在"""
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('audit_log')]
        
        expected_columns = [
            'id', 'log_id', 'event_type', 'rule_code', 'user_id', 'user_name',
            'operation_type', 'business_id', 'count_before', 'count_after',
            'ip_address', 'user_agent', 'timestamp', 'created_at'
        ]
        
        for col in expected_columns:
            assert col in columns, f"Column {col} not found in table"
    
    def test_primary_key(self, engine):
        """测试主键定义"""
        inspector = inspect(engine)
        pk = inspector.get_pk_constraint('audit_log')
        assert 'id' in pk['constrained_columns']
    
    def test_indexes_exist(self, engine):
        """测试索引是否存在"""
        inspector = inspect(engine)
        indexes = inspector.get_indexes('audit_log')
        index_names = [idx['name'] for idx in indexes]
        
        expected_indexes = ['uk_log_id', 'idx_event_type', 'idx_rule_code', 'idx_user_id', 'idx_timestamp']
        
        for idx_name in expected_indexes:
            assert idx_name in index_names, f"Index {idx_name} not found"
    
    def test_unique_log_id(self, engine):
        """测试log_id唯一约束"""
        inspector = inspect(engine)
        indexes = inspector.get_indexes('audit_log')
        
        # Find the uk_log_id index
        uk_log_id_index = next((idx for idx in indexes if idx['name'] == 'uk_log_id'), None)
        assert uk_log_id_index is not None
        # SQLite returns 1 for unique, PostgreSQL returns True
        assert uk_log_id_index['unique'] in (True, 1)
    
    def test_create_audit_log(self, session):
        """测试创建审计日志记录"""
        now = datetime.now()
        audit_log = AuditLog(
            log_id='LOG_20240115_001',
            event_type='approval_completed',
            rule_code='CHK_TRD_004',
            user_id='user123',
            user_name='张三',
            operation_type='approval',
            business_id='TRD_001',
            count_before=15,
            count_after=14,
            ip_address='192.168.1.100',
            user_agent='Mozilla/5.0',
            timestamp=now
        )
        
        session.add(audit_log)
        session.commit()
        
        assert audit_log.id is not None
        assert audit_log.log_id == 'LOG_20240115_001'
        assert audit_log.event_type == 'approval_completed'
        assert audit_log.rule_code == 'CHK_TRD_004'
        assert audit_log.user_id == 'user123'
        assert audit_log.user_name == '张三'
        assert audit_log.count_before == 15
        assert audit_log.count_after == 14
    
    def test_query_by_event_type(self, session):
        """测试按事件类型查询"""
        now = datetime.now()
        log1 = AuditLog(
            log_id='LOG_001',
            event_type='approval_completed',
            user_id='user1',
            user_name='User 1',
            timestamp=now
        )
        log2 = AuditLog(
            log_id='LOG_002',
            event_type='matching_completed',
            user_id='user2',
            user_name='User 2',
            timestamp=now
        )
        
        session.add_all([log1, log2])
        session.commit()
        
        result = session.query(AuditLog).filter_by(event_type='approval_completed').first()
        assert result is not None
        assert result.event_type == 'approval_completed'
        assert result.log_id == 'LOG_001'
    
    def test_query_by_rule_code(self, session):
        """测试按规则代码查询"""
        now = datetime.now()
        log1 = AuditLog(
            log_id='LOG_001',
            event_type='approval_completed',
            rule_code='CHK_TRD_004',
            user_id='user1',
            user_name='User 1',
            timestamp=now
        )
        log2 = AuditLog(
            log_id='LOG_002',
            event_type='matching_completed',
            rule_code='CHK_BO_001',
            user_id='user2',
            user_name='User 2',
            timestamp=now
        )
        
        session.add_all([log1, log2])
        session.commit()
        
        results = session.query(AuditLog).filter_by(rule_code='CHK_TRD_004').all()
        assert len(results) == 1
        assert results[0].rule_code == 'CHK_TRD_004'
    
    def test_query_by_user_id(self, session):
        """测试按用户ID查询"""
        now = datetime.now()
        log1 = AuditLog(
            log_id='LOG_001',
            event_type='approval_completed',
            user_id='user123',
            user_name='User 1',
            timestamp=now
        )
        log2 = AuditLog(
            log_id='LOG_002',
            event_type='matching_completed',
            user_id='user123',
            user_name='User 1',
            timestamp=now
        )
        log3 = AuditLog(
            log_id='LOG_003',
            event_type='approval_completed',
            user_id='user456',
            user_name='User 2',
            timestamp=now
        )
        
        session.add_all([log1, log2, log3])
        session.commit()
        
        results = session.query(AuditLog).filter_by(user_id='user123').all()
        assert len(results) == 2
        for result in results:
            assert result.user_id == 'user123'
    
    def test_query_by_timestamp_range(self, session):
        """测试按时间范围查询"""
        from datetime import timedelta
        
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)
        
        log1 = AuditLog(
            log_id='LOG_001',
            event_type='approval_completed',
            user_id='user1',
            user_name='User 1',
            timestamp=yesterday
        )
        log2 = AuditLog(
            log_id='LOG_002',
            event_type='matching_completed',
            user_id='user2',
            user_name='User 2',
            timestamp=now
        )
        log3 = AuditLog(
            log_id='LOG_003',
            event_type='approval_completed',
            user_id='user3',
            user_name='User 3',
            timestamp=tomorrow
        )
        
        session.add_all([log1, log2, log3])
        session.commit()
        
        # Query logs from yesterday to now
        results = session.query(AuditLog).filter(
            AuditLog.timestamp >= yesterday,
            AuditLog.timestamp <= now
        ).all()
        
        assert len(results) == 2
    
    def test_nullable_fields(self, session):
        """测试可为空的字段"""
        now = datetime.now()
        audit_log = AuditLog(
            log_id='LOG_001',
            event_type='system_event',
            user_id='system',
            user_name='System',
            timestamp=now,
            rule_code=None,
            operation_type=None,
            business_id=None,
            count_before=None,
            count_after=None,
            ip_address=None,
            user_agent=None
        )
        
        session.add(audit_log)
        session.commit()
        
        assert audit_log.rule_code is None
        assert audit_log.operation_type is None
        assert audit_log.business_id is None
        assert audit_log.count_before is None
        assert audit_log.count_after is None
        assert audit_log.ip_address is None
        assert audit_log.user_agent is None
    
    def test_to_dict_method(self, session):
        """测试to_dict方法"""
        now = datetime.now()
        audit_log = AuditLog(
            log_id='LOG_20240115_001',
            event_type='approval_completed',
            rule_code='CHK_TRD_004',
            user_id='user123',
            user_name='张三',
            operation_type='approval',
            business_id='TRD_001',
            count_before=15,
            count_after=14,
            ip_address='192.168.1.100',
            user_agent='Mozilla/5.0',
            timestamp=now
        )
        
        session.add(audit_log)
        session.commit()
        
        log_dict = audit_log.to_dict()
        
        assert isinstance(log_dict, dict)
        assert log_dict['log_id'] == 'LOG_20240115_001'
        assert log_dict['event_type'] == 'approval_completed'
        assert log_dict['rule_code'] == 'CHK_TRD_004'
        assert log_dict['user_id'] == 'user123'
        assert log_dict['user_name'] == '张三'
        assert log_dict['operation_type'] == 'approval'
        assert log_dict['business_id'] == 'TRD_001'
        assert log_dict['count_before'] == 15
        assert log_dict['count_after'] == 14
        assert log_dict['ip_address'] == '192.168.1.100'
        assert log_dict['user_agent'] == 'Mozilla/5.0'
        assert 'id' in log_dict
        assert 'timestamp' in log_dict
        assert 'created_at' in log_dict
    
    def test_repr_method(self, session):
        """测试__repr__方法"""
        now = datetime.now()
        audit_log = AuditLog(
            log_id='LOG_001',
            event_type='approval_completed',
            user_id='user123',
            user_name='张三',
            timestamp=now
        )
        
        session.add(audit_log)
        session.commit()
        
        repr_str = repr(audit_log)
        assert 'AuditLog' in repr_str
        assert 'LOG_001' in repr_str
        assert 'approval_completed' in repr_str
        assert 'user123' in repr_str
    
    def test_count_change_tracking(self, session):
        """测试提醒数量变化追踪"""
        now = datetime.now()
        
        # 模拟处理前后的数量变化
        audit_log = AuditLog(
            log_id='LOG_001',
            event_type='approval_completed',
            rule_code='CHK_TRD_004',
            user_id='user123',
            user_name='张三',
            operation_type='approval',
            business_id='TRD_001',
            count_before=15,
            count_after=14,
            timestamp=now
        )
        
        session.add(audit_log)
        session.commit()
        
        # 验证数量变化
        assert audit_log.count_before == 15
        assert audit_log.count_after == 14
        assert audit_log.count_before - audit_log.count_after == 1
    
    def test_multiple_operations_same_user(self, session):
        """测试同一用户的多次操作记录"""
        now = datetime.now()
        
        operations = [
            ('LOG_001', 'approval_completed', 'CHK_TRD_004', 15, 14),
            ('LOG_002', 'matching_completed', 'CHK_BO_001', 12, 11),
            ('LOG_003', 'sending_completed', 'CHK_CONF_005', 4, 3),
        ]
        
        for log_id, event_type, rule_code, count_before, count_after in operations:
            audit_log = AuditLog(
                log_id=log_id,
                event_type=event_type,
                rule_code=rule_code,
                user_id='user123',
                user_name='张三',
                count_before=count_before,
                count_after=count_after,
                timestamp=now
            )
            session.add(audit_log)
        
        session.commit()
        
        # 查询该用户的所有操作
        user_logs = session.query(AuditLog).filter_by(user_id='user123').all()
        assert len(user_logs) == 3
        
        # 验证每条记录
        for log in user_logs:
            assert log.user_id == 'user123'
            assert log.user_name == '张三'
    
    def test_ip_address_and_user_agent(self, session):
        """测试IP地址和User Agent记录"""
        now = datetime.now()
        audit_log = AuditLog(
            log_id='LOG_001',
            event_type='sensitive_query',
            user_id='user123',
            user_name='张三',
            ip_address='192.168.1.100',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            timestamp=now
        )
        
        session.add(audit_log)
        session.commit()
        
        retrieved_log = session.query(AuditLog).filter_by(log_id='LOG_001').first()
        assert retrieved_log.ip_address == '192.168.1.100'
        assert 'Mozilla/5.0' in retrieved_log.user_agent
        assert 'Windows NT 10.0' in retrieved_log.user_agent
    
    def test_event_types(self, session):
        """测试不同的事件类型"""
        now = datetime.now()
        event_types = [
            'approval_completed',
            'matching_completed',
            'sending_completed',
            'sensitive_query',
            'config_changed'
        ]
        
        for i, event_type in enumerate(event_types):
            audit_log = AuditLog(
                log_id=f'LOG_{i:03d}',
                event_type=event_type,
                user_id='user123',
                user_name='张三',
                timestamp=now
            )
            session.add(audit_log)
        
        session.commit()
        
        # 验证每种事件类型都被正确记录
        for event_type in event_types:
            result = session.query(AuditLog).filter_by(event_type=event_type).first()
            assert result is not None
            assert result.event_type == event_type
