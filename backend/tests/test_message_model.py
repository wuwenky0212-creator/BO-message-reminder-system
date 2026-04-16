"""
Unit tests for Message model

测试Message模型类的所有功能，包括字段定义、索引、方法等。
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.message import Message, Base


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


class TestMessageModel:
    """Message模型测试类"""
    
    def test_table_name(self):
        """测试表名是否正确"""
        assert Message.__tablename__ == 'message_table'
    
    def test_columns_exist(self, engine):
        """测试所有列是否存在"""
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('message_table')]
        
        expected_columns = [
            'id', 'rule_code', 'title', 'count', 'last_updated',
            'status', 'priority', 'target_roles', 'metadata',
            'created_at', 'updated_at'
        ]
        
        for col in expected_columns:
            assert col in columns, f"Column {col} not found in table"
    
    def test_primary_key(self, engine):
        """测试主键定义"""
        inspector = inspect(engine)
        pk = inspector.get_pk_constraint('message_table')
        assert 'id' in pk['constrained_columns']
    
    def test_indexes_exist(self, engine):
        """测试索引是否存在"""
        inspector = inspect(engine)
        indexes = inspector.get_indexes('message_table')
        index_names = [idx['name'] for idx in indexes]
        
        expected_indexes = ['idx_rule_code', 'idx_last_updated', 'idx_status']
        
        for idx_name in expected_indexes:
            assert idx_name in index_names, f"Index {idx_name} not found"
    
    def test_create_message(self, session):
        """测试创建消息记录"""
        message = Message(
            rule_code='CHK_TRD_004',
            title='当日交易未复核',
            count=15,
            last_updated=datetime.now(),
            status='success',
            priority='normal',
            target_roles=['BO_Operator', 'BO_Supervisor'],
            metadata_={'additional_info': 'test'}
        )
        
        session.add(message)
        session.commit()
        
        assert message.id is not None
        assert message.rule_code == 'CHK_TRD_004'
        assert message.title == '当日交易未复核'
        assert message.count == 15
        assert message.status == 'success'
        assert message.priority == 'normal'
    
    def test_query_by_rule_code(self, session):
        """测试按规则代码查询"""
        message1 = Message(
            rule_code='CHK_TRD_004',
            title='当日交易未复核',
            count=15,
            last_updated=datetime.now(),
            status='success',
            priority='normal',
            target_roles=['BO_Operator'],
        )
        message2 = Message(
            rule_code='CHK_BO_001',
            title='未证实匹配',
            count=12,
            last_updated=datetime.now(),
            status='success',
            priority='normal',
            target_roles=['BO_Operator'],
        )
        
        session.add_all([message1, message2])
        session.commit()
        
        result = session.query(Message).filter_by(rule_code='CHK_TRD_004').first()
        assert result is not None
        assert result.rule_code == 'CHK_TRD_004'
        assert result.title == '当日交易未复核'
    
    def test_query_by_status(self, session):
        """测试按状态查询"""
        message1 = Message(
            rule_code='CHK_TRD_004',
            title='当日交易未复核',
            count=15,
            last_updated=datetime.now(),
            status='success',
            priority='normal',
            target_roles=['BO_Operator'],
        )
        message2 = Message(
            rule_code='CHK_BO_001',
            title='未证实匹配',
            count=12,
            last_updated=datetime.now(),
            status='timeout',
            priority='high',
            target_roles=['BO_Operator'],
        )
        
        session.add_all([message1, message2])
        session.commit()
        
        success_messages = session.query(Message).filter_by(status='success').all()
        assert len(success_messages) == 1
        assert success_messages[0].status == 'success'
        
        timeout_messages = session.query(Message).filter_by(status='timeout').all()
        assert len(timeout_messages) == 1
        assert timeout_messages[0].status == 'timeout'
    
    def test_update_message_count(self, session):
        """测试更新消息数量"""
        message = Message(
            rule_code='CHK_TRD_004',
            title='当日交易未复核',
            count=15,
            last_updated=datetime.now(),
            status='success',
            priority='normal',
            target_roles=['BO_Operator'],
        )
        
        session.add(message)
        session.commit()
        
        original_count = message.count
        message.count = 14
        session.commit()
        
        updated_message = session.query(Message).filter_by(id=message.id).first()
        assert updated_message.count == 14
        assert updated_message.count != original_count
    
    def test_to_dict_method(self, session):
        """测试to_dict方法"""
        now = datetime.now()
        message = Message(
            rule_code='CHK_TRD_004',
            title='当日交易未复核',
            count=15,
            last_updated=now,
            status='success',
            priority='normal',
            target_roles=['BO_Operator', 'BO_Supervisor'],
            metadata_={'key': 'value'}
        )
        
        session.add(message)
        session.commit()
        
        message_dict = message.to_dict()
        
        assert isinstance(message_dict, dict)
        assert message_dict['rule_code'] == 'CHK_TRD_004'
        assert message_dict['title'] == '当日交易未复核'
        assert message_dict['count'] == 15
        assert message_dict['status'] == 'success'
        assert message_dict['priority'] == 'normal'
        assert message_dict['target_roles'] == ['BO_Operator', 'BO_Supervisor']
        assert message_dict['metadata'] == {'key': 'value'}
        assert 'id' in message_dict
        assert 'created_at' in message_dict
        assert 'updated_at' in message_dict
    
    def test_repr_method(self, session):
        """测试__repr__方法"""
        message = Message(
            rule_code='CHK_TRD_004',
            title='当日交易未复核',
            count=15,
            last_updated=datetime.now(),
            status='success',
            priority='normal',
            target_roles=['BO_Operator'],
        )
        
        session.add(message)
        session.commit()
        
        repr_str = repr(message)
        assert 'Message' in repr_str
        assert 'CHK_TRD_004' in repr_str
        assert '当日交易未复核' in repr_str
        assert 'success' in repr_str
    
    def test_nullable_metadata(self, session):
        """测试metadata字段可为空"""
        message = Message(
            rule_code='CHK_TRD_004',
            title='当日交易未复核',
            count=15,
            last_updated=datetime.now(),
            status='success',
            priority='normal',
            target_roles=['BO_Operator'],
            metadata_=None
        )
        
        session.add(message)
        session.commit()
        
        assert message.metadata_ is None
    
    def test_json_field_target_roles(self, session):
        """测试target_roles JSON字段"""
        roles = ['BO_Operator', 'BO_Supervisor', 'System_Admin']
        message = Message(
            rule_code='CHK_TRD_004',
            title='当日交易未复核',
            count=15,
            last_updated=datetime.now(),
            status='success',
            priority='normal',
            target_roles=roles,
        )
        
        session.add(message)
        session.commit()
        
        retrieved_message = session.query(Message).filter_by(id=message.id).first()
        assert retrieved_message.target_roles == roles
    
    def test_status_values(self, session):
        """测试不同的status值"""
        statuses = ['success', 'timeout', 'error']
        
        for status in statuses:
            message = Message(
                rule_code=f'TEST_{status}',
                title=f'Test {status}',
                count=1,
                last_updated=datetime.now(),
                status=status,
                priority='normal',
                target_roles=['BO_Operator'],
            )
            session.add(message)
        
        session.commit()
        
        for status in statuses:
            result = session.query(Message).filter_by(status=status).first()
            assert result is not None
            assert result.status == status
    
    def test_priority_values(self, session):
        """测试不同的priority值"""
        priorities = ['normal', 'high', 'critical']
        
        for priority in priorities:
            message = Message(
                rule_code=f'TEST_{priority}',
                title=f'Test {priority}',
                count=1,
                last_updated=datetime.now(),
                status='success',
                priority=priority,
                target_roles=['BO_Operator'],
            )
            session.add(message)
        
        session.commit()
        
        for priority in priorities:
            result = session.query(Message).filter_by(priority=priority).first()
            assert result is not None
            assert result.priority == priority
