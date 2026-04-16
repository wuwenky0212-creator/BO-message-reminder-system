"""
Unit tests for TaskExecutionLog model

测试TaskExecutionLog模型类的所有功能，包括字段定义、索引、方法等。
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.task_execution_log import TaskExecutionLog, Base


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


class TestTaskExecutionLogModel:
    """TaskExecutionLog模型测试类"""
    
    def test_table_name(self):
        """测试表名是否正确"""
        assert TaskExecutionLog.__tablename__ == 'task_execution_log'
    
    def test_columns_exist(self, engine):
        """测试所有列是否存在"""
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('task_execution_log')]
        
        expected_columns = [
            'id', 'task_id', 'rule_code', 'rule_name',
            'scheduled_time', 'actual_start_time', 'actual_end_time',
            'execution_duration', 'status', 'record_count',
            'error_message', 'created_at'
        ]
        
        for col in expected_columns:
            assert col in columns, f"Column {col} not found in table"
    
    def test_primary_key(self, engine):
        """测试主键定义"""
        inspector = inspect(engine)
        pk = inspector.get_pk_constraint('task_execution_log')
        assert 'id' in pk['constrained_columns']
    
    def test_indexes_exist(self, engine):
        """测试索引是否存在"""
        inspector = inspect(engine)
        indexes = inspector.get_indexes('task_execution_log')
        index_names = [idx['name'] for idx in indexes]
        
        expected_indexes = ['uk_task_id', 'idx_rule_code', 'idx_scheduled_time', 'idx_status']
        
        for idx_name in expected_indexes:
            assert idx_name in index_names, f"Index {idx_name} not found"
    
    def test_task_id_unique_constraint(self, engine):
        """测试task_id唯一约束"""
        inspector = inspect(engine)
        indexes = inspector.get_indexes('task_execution_log')
        
        # Find the uk_task_id index
        uk_task_id = next((idx for idx in indexes if idx['name'] == 'uk_task_id'), None)
        assert uk_task_id is not None
        # SQLite returns 1 for unique, which is truthy
        assert uk_task_id['unique'] == 1 or uk_task_id['unique'] is True
        assert 'task_id' in uk_task_id['column_names']
    
    def test_create_task_execution_log(self, session):
        """测试创建任务执行日志记录"""
        now = datetime.now()
        log = TaskExecutionLog(
            task_id='CHK_TRD_004_20240115_143000',
            rule_code='CHK_TRD_004',
            rule_name='交易复核提醒',
            scheduled_time=now,
            actual_start_time=now,
            actual_end_time=now + timedelta(seconds=2),
            execution_duration=2000,
            status='completed',
            record_count=15,
            error_message=None
        )
        
        session.add(log)
        session.commit()
        
        assert log.id is not None
        assert log.task_id == 'CHK_TRD_004_20240115_143000'
        assert log.rule_code == 'CHK_TRD_004'
        assert log.rule_name == '交易复核提醒'
        assert log.status == 'completed'
        assert log.record_count == 15
        assert log.execution_duration == 2000
    
    def test_query_by_rule_code(self, session):
        """测试按规则代码查询"""
        now = datetime.now()
        log1 = TaskExecutionLog(
            task_id='CHK_TRD_004_20240115_143000',
            rule_code='CHK_TRD_004',
            rule_name='交易复核提醒',
            scheduled_time=now,
            actual_start_time=now,
            status='completed',
            record_count=15
        )
        log2 = TaskExecutionLog(
            task_id='CHK_BO_001_20240115_150000',
            rule_code='CHK_BO_001',
            rule_name='未证实匹配',
            scheduled_time=now,
            actual_start_time=now,
            status='completed',
            record_count=12
        )
        
        session.add_all([log1, log2])
        session.commit()
        
        result = session.query(TaskExecutionLog).filter_by(rule_code='CHK_TRD_004').first()
        assert result is not None
        assert result.rule_code == 'CHK_TRD_004'
        assert result.rule_name == '交易复核提醒'
    
    def test_query_by_status(self, session):
        """测试按状态查询"""
        now = datetime.now()
        log1 = TaskExecutionLog(
            task_id='CHK_TRD_004_20240115_143000',
            rule_code='CHK_TRD_004',
            rule_name='交易复核提醒',
            scheduled_time=now,
            actual_start_time=now,
            status='completed',
            record_count=15
        )
        log2 = TaskExecutionLog(
            task_id='CHK_BO_001_20240115_150000',
            rule_code='CHK_BO_001',
            rule_name='未证实匹配',
            scheduled_time=now,
            actual_start_time=now,
            status='failed',
            error_message='Database connection timeout'
        )
        
        session.add_all([log1, log2])
        session.commit()
        
        completed_logs = session.query(TaskExecutionLog).filter_by(status='completed').all()
        assert len(completed_logs) == 1
        assert completed_logs[0].status == 'completed'
        
        failed_logs = session.query(TaskExecutionLog).filter_by(status='failed').all()
        assert len(failed_logs) == 1
        assert failed_logs[0].status == 'failed'
    
    def test_query_by_scheduled_time(self, session):
        """测试按计划执行时间查询"""
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        
        log1 = TaskExecutionLog(
            task_id='CHK_TRD_004_20240114_143000',
            rule_code='CHK_TRD_004',
            rule_name='交易复核提醒',
            scheduled_time=yesterday,
            actual_start_time=yesterday,
            status='completed',
            record_count=10
        )
        log2 = TaskExecutionLog(
            task_id='CHK_TRD_004_20240115_143000',
            rule_code='CHK_TRD_004',
            rule_name='交易复核提醒',
            scheduled_time=now,
            actual_start_time=now,
            status='completed',
            record_count=15
        )
        
        session.add_all([log1, log2])
        session.commit()
        
        # Query logs from today
        today_logs = session.query(TaskExecutionLog).filter(
            TaskExecutionLog.scheduled_time >= now.replace(hour=0, minute=0, second=0, microsecond=0)
        ).all()
        assert len(today_logs) == 1
        assert today_logs[0].record_count == 15
    
    def test_to_dict_method(self, session):
        """测试to_dict方法"""
        now = datetime.now()
        log = TaskExecutionLog(
            task_id='CHK_TRD_004_20240115_143000',
            rule_code='CHK_TRD_004',
            rule_name='交易复核提醒',
            scheduled_time=now,
            actual_start_time=now,
            actual_end_time=now + timedelta(seconds=2),
            execution_duration=2000,
            status='completed',
            record_count=15,
            error_message=None
        )
        
        session.add(log)
        session.commit()
        
        log_dict = log.to_dict()
        
        assert isinstance(log_dict, dict)
        assert log_dict['task_id'] == 'CHK_TRD_004_20240115_143000'
        assert log_dict['rule_code'] == 'CHK_TRD_004'
        assert log_dict['rule_name'] == '交易复核提醒'
        assert log_dict['status'] == 'completed'
        assert log_dict['record_count'] == 15
        assert log_dict['execution_duration'] == 2000
        assert log_dict['error_message'] is None
        assert 'id' in log_dict
        assert 'scheduled_time' in log_dict
        assert 'actual_start_time' in log_dict
        assert 'actual_end_time' in log_dict
        assert 'created_at' in log_dict
    
    def test_repr_method(self, session):
        """测试__repr__方法"""
        now = datetime.now()
        log = TaskExecutionLog(
            task_id='CHK_TRD_004_20240115_143000',
            rule_code='CHK_TRD_004',
            rule_name='交易复核提醒',
            scheduled_time=now,
            actual_start_time=now,
            status='completed',
            record_count=15
        )
        
        session.add(log)
        session.commit()
        
        repr_str = repr(log)
        assert 'TaskExecutionLog' in repr_str
        assert 'CHK_TRD_004_20240115_143000' in repr_str
        assert 'CHK_TRD_004' in repr_str
        assert 'completed' in repr_str
    
    def test_nullable_fields(self, session):
        """测试可为空的字段"""
        now = datetime.now()
        log = TaskExecutionLog(
            task_id='CHK_TRD_004_20240115_143000',
            rule_code='CHK_TRD_004',
            rule_name='交易复核提醒',
            scheduled_time=now,
            actual_start_time=now,
            actual_end_time=None,
            execution_duration=None,
            status='completed',
            record_count=None,
            error_message=None
        )
        
        session.add(log)
        session.commit()
        
        assert log.actual_end_time is None
        assert log.execution_duration is None
        assert log.record_count is None
        assert log.error_message is None
    
    def test_status_values(self, session):
        """测试不同的status值"""
        now = datetime.now()
        statuses = ['completed', 'failed', 'timeout']
        
        for idx, status in enumerate(statuses):
            log = TaskExecutionLog(
                task_id=f'TEST_{status}_{idx}',
                rule_code='TEST_RULE',
                rule_name='Test Rule',
                scheduled_time=now,
                actual_start_time=now,
                status=status,
                record_count=0
            )
            session.add(log)
        
        session.commit()
        
        for status in statuses:
            result = session.query(TaskExecutionLog).filter_by(status=status).first()
            assert result is not None
            assert result.status == status
    
    def test_failed_task_with_error_message(self, session):
        """测试失败任务记录错误信息"""
        now = datetime.now()
        error_msg = 'Database connection timeout after 10 seconds'
        
        log = TaskExecutionLog(
            task_id='CHK_TRD_004_20240115_143000',
            rule_code='CHK_TRD_004',
            rule_name='交易复核提醒',
            scheduled_time=now,
            actual_start_time=now,
            actual_end_time=now + timedelta(seconds=10),
            execution_duration=10000,
            status='failed',
            record_count=None,
            error_message=error_msg
        )
        
        session.add(log)
        session.commit()
        
        retrieved_log = session.query(TaskExecutionLog).filter_by(task_id=log.task_id).first()
        assert retrieved_log.status == 'failed'
        assert retrieved_log.error_message == error_msg
        assert retrieved_log.record_count is None
    
    def test_timeout_task(self, session):
        """测试超时任务"""
        now = datetime.now()
        
        log = TaskExecutionLog(
            task_id='CHK_SEC_003_20240115_150000',
            rule_code='CHK_SEC_003',
            rule_name='券持仓卖空预警',
            scheduled_time=now,
            actual_start_time=now,
            actual_end_time=now + timedelta(seconds=10),
            execution_duration=10000,
            status='timeout',
            record_count=None,
            error_message='Query execution timeout'
        )
        
        session.add(log)
        session.commit()
        
        retrieved_log = session.query(TaskExecutionLog).filter_by(status='timeout').first()
        assert retrieved_log is not None
        assert retrieved_log.status == 'timeout'
        assert 'timeout' in retrieved_log.error_message.lower()
    
    def test_execution_duration_calculation(self, session):
        """测试执行时长计算"""
        now = datetime.now()
        start_time = now
        end_time = now + timedelta(seconds=3, milliseconds=500)
        duration_ms = 3500
        
        log = TaskExecutionLog(
            task_id='CHK_TRD_004_20240115_143000',
            rule_code='CHK_TRD_004',
            rule_name='交易复核提醒',
            scheduled_time=now,
            actual_start_time=start_time,
            actual_end_time=end_time,
            execution_duration=duration_ms,
            status='completed',
            record_count=15
        )
        
        session.add(log)
        session.commit()
        
        assert log.execution_duration == 3500
        assert log.actual_end_time > log.actual_start_time
    
    def test_query_recent_logs(self, session):
        """测试查询最近的执行日志"""
        now = datetime.now()
        
        # Create logs for the past 5 days
        for i in range(5):
            log_time = now - timedelta(days=i)
            log = TaskExecutionLog(
                task_id=f'CHK_TRD_004_2024011{5-i}_143000',
                rule_code='CHK_TRD_004',
                rule_name='交易复核提醒',
                scheduled_time=log_time,
                actual_start_time=log_time,
                status='completed',
                record_count=10 + i
            )
            session.add(log)
        
        session.commit()
        
        # Query logs from the last 2 days (not including 3 days ago)
        two_days_ago = now - timedelta(days=2)
        recent_logs = session.query(TaskExecutionLog).filter(
            TaskExecutionLog.scheduled_time > two_days_ago
        ).order_by(TaskExecutionLog.scheduled_time.desc()).all()
        
        assert len(recent_logs) == 2
        # Most recent log should be first
        assert recent_logs[0].record_count == 10
    
    def test_unique_task_id_constraint(self, session):
        """测试task_id唯一约束"""
        now = datetime.now()
        
        log1 = TaskExecutionLog(
            task_id='CHK_TRD_004_20240115_143000',
            rule_code='CHK_TRD_004',
            rule_name='交易复核提醒',
            scheduled_time=now,
            actual_start_time=now,
            status='completed',
            record_count=15
        )
        
        session.add(log1)
        session.commit()
        
        # Try to create another log with the same task_id
        log2 = TaskExecutionLog(
            task_id='CHK_TRD_004_20240115_143000',  # Same task_id
            rule_code='CHK_TRD_004',
            rule_name='交易复核提醒',
            scheduled_time=now,
            actual_start_time=now,
            status='completed',
            record_count=20
        )
        
        session.add(log2)
        
        # Should raise an IntegrityError due to unique constraint
        with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
            session.commit()
