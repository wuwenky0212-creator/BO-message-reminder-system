"""
规则扫描器基础框架单元测试

测试规则扫描器基类、查询超时控制、扫描结果处理和任务执行日志记录。
"""

import pytest
import time
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from backend.scanner.base_scanner import BaseRuleScanner, ScanResult
from backend.scanner.timeout_control import QueryTimeoutControl, TimeoutException
from backend.models.task_execution_log import TaskExecutionLog


# ============================================================================
# 测试夹具 (Fixtures)
# ============================================================================

@pytest.fixture
def mock_db_session():
    """模拟数据库会话"""
    session = Mock(spec=Session)
    session.add = Mock()
    session.commit = Mock()
    session.query = Mock()
    return session


@pytest.fixture
def concrete_scanner():
    """创建具体的扫描器实现用于测试"""
    class ConcreteScanner(BaseRuleScanner):
        def __init__(self, rule_code='TEST_001', rule_name='测试规则', timeout_seconds=10):
            super().__init__(rule_code, rule_name, timeout_seconds)
            self.scan_result = None
        
        def execute_scan(self, db: Session) -> ScanResult:
            if self.scan_result:
                return self.scan_result
            return ScanResult(status='success', count=5)
    
    return ConcreteScanner()


# ============================================================================
# 测试 QueryTimeoutControl - 查询超时控制
# ============================================================================

class TestQueryTimeoutControl:
    """测试查询超时控制功能"""
    
    def test_timeout_control_initialization(self):
        """测试超时控制器初始化"""
        timeout_control = QueryTimeoutControl(timeout_seconds=5)
        assert timeout_control.timeout_seconds == 5
    
    def test_timeout_context_normal_execution(self):
        """测试正常执行（不超时）"""
        timeout_control = QueryTimeoutControl(timeout_seconds=2)
        
        result = None
        with timeout_control.timeout_context():
            result = "completed"
        
        assert result == "completed"
    
    def test_timeout_context_raises_exception_on_timeout(self):
        """测试超时时抛出异常"""
        timeout_control = QueryTimeoutControl(timeout_seconds=1)
        
        with pytest.raises(TimeoutException) as exc_info:
            with timeout_control.timeout_context():
                time.sleep(1.5)  # 睡眠超过超时时间
        
        assert "Query execution timeout" in str(exc_info.value)
        assert "1 seconds" in str(exc_info.value)
    
    def test_timeout_context_cleans_up_alarm(self):
        """测试超时上下文正确清理定时器"""
        timeout_control = QueryTimeoutControl(timeout_seconds=5)
        
        # 执行上下文
        with timeout_control.timeout_context():
            pass
        
        # 验证定时器已被取消
        assert timeout_control._timer is None or not timeout_control._timer.is_alive()
        
        # 后续代码应该不会被中断
        time.sleep(0.1)
    
    def test_timeout_context_restores_signal_handler(self):
        """测试超时上下文清理资源"""
        timeout_control = QueryTimeoutControl(timeout_seconds=1)
        
        # 执行上下文
        with timeout_control.timeout_context():
            # 验证定时器已启动
            assert timeout_control._timer is not None
            assert timeout_control._timer.is_alive()
        
        # 验证定时器已清理
        assert timeout_control._timer is None or not timeout_control._timer.is_alive()


# ============================================================================
# 测试 ScanResult - 扫描结果数据类
# ============================================================================

class TestScanResult:
    """测试扫描结果数据类"""
    
    def test_scan_result_success(self):
        """测试成功的扫描结果"""
        result = ScanResult(status='success', count=10)
        
        assert result.status == 'success'
        assert result.count == 10
        assert result.error_message is None
        assert result.data is None
        assert result.metadata is None
    
    def test_scan_result_timeout(self):
        """测试超时的扫描结果"""
        result = ScanResult(
            status='timeout',
            count=-1,
            error_message='Query execution timeout'
        )
        
        assert result.status == 'timeout'
        assert result.count == -1
        assert result.error_message == 'Query execution timeout'
    
    def test_scan_result_error(self):
        """测试错误的扫描结果"""
        result = ScanResult(
            status='error',
            count=-1,
            error_message='Database connection failed'
        )
        
        assert result.status == 'error'
        assert result.count == -1
        assert result.error_message == 'Database connection failed'
    
    def test_scan_result_with_data_and_metadata(self):
        """测试带数据和元数据的扫描结果"""
        data = [{'id': 1, 'name': 'test'}]
        metadata = {'query_time': 100, 'source': 'trade_table'}
        
        result = ScanResult(
            status='success',
            count=1,
            data=data,
            metadata=metadata
        )
        
        assert result.status == 'success'
        assert result.count == 1
        assert result.data == data
        assert result.metadata == metadata


# ============================================================================
# 测试 BaseRuleScanner - 规则扫描器基类
# ============================================================================

class TestBaseRuleScanner:
    """测试规则扫描器基类"""
    
    def test_scanner_initialization(self, concrete_scanner):
        """测试扫描器初始化"""
        assert concrete_scanner.rule_code == 'TEST_001'
        assert concrete_scanner.rule_name == '测试规则'
        assert concrete_scanner.timeout_seconds == 10
        assert isinstance(concrete_scanner.timeout_control, QueryTimeoutControl)
    
    def test_scanner_custom_timeout(self):
        """测试自定义超时时间"""
        class CustomScanner(BaseRuleScanner):
            def execute_scan(self, db: Session) -> ScanResult:
                return ScanResult(status='success', count=0)
        
        scanner = CustomScanner('TEST_002', '自定义超时', timeout_seconds=20)
        assert scanner.timeout_seconds == 20
        assert scanner.timeout_control.timeout_seconds == 20
    
    def test_generate_task_id(self, concrete_scanner):
        """测试任务ID生成"""
        task_id = concrete_scanner._generate_task_id()
        
        # 验证格式：{rule_code}_{timestamp}_{uuid}
        parts = task_id.split('_')
        assert parts[0] == 'TEST'
        assert parts[1] == '001'
        assert len(parts[2]) == 14  # YYYYMMDDHHMMSS
        assert len(parts[3]) == 8   # UUID前8位
    
    def test_generate_task_id_uniqueness(self, concrete_scanner):
        """测试任务ID唯一性"""
        task_id_1 = concrete_scanner._generate_task_id()
        task_id_2 = concrete_scanner._generate_task_id()
        
        assert task_id_1 != task_id_2


# ============================================================================
# 测试任务执行日志记录
# ============================================================================

class TestTaskExecutionLogging:
    """测试任务执行日志记录功能"""
    
    def test_log_task_start(self, concrete_scanner, mock_db_session):
        """测试记录任务开始日志"""
        task_id = 'TEST_001_20240115120000_abc123'
        scheduled_time = datetime(2024, 1, 15, 12, 0, 0)
        actual_start_time = datetime(2024, 1, 15, 12, 0, 1)
        
        concrete_scanner._log_task_start(
            db=mock_db_session,
            task_id=task_id,
            scheduled_time=scheduled_time,
            actual_start_time=actual_start_time
        )
        
        # 验证日志记录被添加
        mock_db_session.add.assert_called_once()
        log_entry = mock_db_session.add.call_args[0][0]
        
        assert isinstance(log_entry, TaskExecutionLog)
        assert log_entry.task_id == task_id
        assert log_entry.rule_code == 'TEST_001'
        assert log_entry.rule_name == '测试规则'
        assert log_entry.scheduled_time == scheduled_time
        assert log_entry.actual_start_time == actual_start_time
        assert log_entry.status == 'running'
        
        # 验证提交
        mock_db_session.commit.assert_called_once()
    
    def test_log_task_completion_success(self, concrete_scanner, mock_db_session):
        """测试记录任务成功完成日志"""
        task_id = 'TEST_001_20240115120000_abc123'
        actual_end_time = datetime(2024, 1, 15, 12, 0, 5)
        execution_duration = 5000
        
        # 模拟查询返回日志记录
        mock_log_entry = Mock(spec=TaskExecutionLog)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_log_entry
        mock_db_session.query.return_value = mock_query
        
        concrete_scanner._log_task_completion(
            db=mock_db_session,
            task_id=task_id,
            actual_end_time=actual_end_time,
            execution_duration=execution_duration,
            status='completed',
            record_count=10,
            error_message=None
        )
        
        # 验证日志记录被更新
        assert mock_log_entry.actual_end_time == actual_end_time
        assert mock_log_entry.execution_duration == execution_duration
        assert mock_log_entry.status == 'completed'
        assert mock_log_entry.record_count == 10
        assert mock_log_entry.error_message is None
        
        # 验证提交
        mock_db_session.commit.assert_called_once()
    
    def test_log_task_completion_with_error(self, concrete_scanner, mock_db_session):
        """测试记录任务失败日志"""
        task_id = 'TEST_001_20240115120000_abc123'
        actual_end_time = datetime(2024, 1, 15, 12, 0, 3)
        execution_duration = 3000
        error_message = 'Database connection failed'
        
        # 模拟查询返回日志记录
        mock_log_entry = Mock(spec=TaskExecutionLog)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_log_entry
        mock_db_session.query.return_value = mock_query
        
        concrete_scanner._log_task_completion(
            db=mock_db_session,
            task_id=task_id,
            actual_end_time=actual_end_time,
            execution_duration=execution_duration,
            status='failed',
            record_count=-1,
            error_message=error_message
        )
        
        # 验证日志记录被更新
        assert mock_log_entry.status == 'failed'
        assert mock_log_entry.record_count == -1
        assert mock_log_entry.error_message == error_message


# ============================================================================
# 测试扫描执行流程
# ============================================================================

class TestScanExecution:
    """测试扫描执行流程"""
    
    def test_scan_success(self, concrete_scanner, mock_db_session):
        """测试成功的扫描执行"""
        # 设置扫描结果
        concrete_scanner.scan_result = ScanResult(status='success', count=15)
        
        # 模拟日志查询
        mock_log_entry = Mock(spec=TaskExecutionLog)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_log_entry
        mock_db_session.query.return_value = mock_query
        
        # 执行扫描
        result = concrete_scanner.scan(mock_db_session)
        
        # 验证结果
        assert result.status == 'success'
        assert result.count == 15
        assert result.error_message is None
        
        # 验证日志记录被调用
        assert mock_db_session.add.call_count == 1  # 开始日志
        assert mock_db_session.commit.call_count >= 2  # 开始和完成日志
    
    def test_scan_with_scheduled_time(self, concrete_scanner, mock_db_session):
        """测试带计划时间的扫描"""
        scheduled_time = datetime(2024, 1, 15, 14, 30, 0)
        
        # 模拟日志查询
        mock_log_entry = Mock(spec=TaskExecutionLog)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_log_entry
        mock_db_session.query.return_value = mock_query
        
        result = concrete_scanner.scan(mock_db_session, scheduled_time=scheduled_time)
        
        # 验证开始日志使用了指定的计划时间
        log_entry = mock_db_session.add.call_args[0][0]
        assert log_entry.scheduled_time == scheduled_time
    
    @patch('backend.scanner.base_scanner.QueryTimeoutControl.timeout_context')
    def test_scan_timeout_handling(self, mock_timeout_context, concrete_scanner, mock_db_session):
        """测试扫描超时处理"""
        # 模拟超时异常
        mock_timeout_context.return_value.__enter__.side_effect = TimeoutException(
            "Query execution timeout after 10 seconds"
        )
        
        # 模拟日志查询
        mock_log_entry = Mock(spec=TaskExecutionLog)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_log_entry
        mock_db_session.query.return_value = mock_query
        
        # 执行扫描
        result = concrete_scanner.scan(mock_db_session)
        
        # 验证结果
        assert result.status == 'timeout'
        assert result.count == -1
        assert 'timeout' in result.error_message.lower()
        
        # 验证日志记录状态
        assert mock_log_entry.status == 'timeout'
        assert mock_log_entry.record_count == -1
    
    def test_scan_error_handling(self, concrete_scanner, mock_db_session):
        """测试扫描错误处理"""
        # 设置扫描抛出异常
        class ErrorScanner(BaseRuleScanner):
            def execute_scan(self, db: Session) -> ScanResult:
                raise ValueError("Invalid data format")
        
        error_scanner = ErrorScanner('TEST_ERR', '错误测试')
        
        # 模拟日志查询
        mock_log_entry = Mock(spec=TaskExecutionLog)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_log_entry
        mock_db_session.query.return_value = mock_query
        
        # 执行扫描
        result = error_scanner.scan(mock_db_session)
        
        # 验证结果
        assert result.status == 'error'
        assert result.count == -1
        assert 'ValueError' in result.error_message
        assert 'Invalid data format' in result.error_message
        
        # 验证日志记录状态
        assert mock_log_entry.status == 'failed'
        assert mock_log_entry.record_count == -1
        assert mock_log_entry.error_message is not None
    
    def test_scan_execution_duration_calculation(self, concrete_scanner, mock_db_session):
        """测试执行时长计算"""
        # 设置扫描延迟
        class SlowScanner(BaseRuleScanner):
            def execute_scan(self, db: Session) -> ScanResult:
                time.sleep(0.1)  # 睡眠100毫秒
                return ScanResult(status='success', count=5)
        
        slow_scanner = SlowScanner('TEST_SLOW', '慢速扫描')
        
        # 模拟日志查询
        mock_log_entry = Mock(spec=TaskExecutionLog)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_log_entry
        mock_db_session.query.return_value = mock_query
        
        # 执行扫描
        result = slow_scanner.scan(mock_db_session)
        
        # 验证执行时长被记录（应该大于100毫秒）
        assert mock_log_entry.execution_duration >= 100
        assert result.status == 'success'


# ============================================================================
# 集成测试
# ============================================================================

class TestScannerIntegration:
    """测试扫描器集成场景"""
    
    def test_complete_scan_workflow(self, concrete_scanner, mock_db_session):
        """测试完整的扫描工作流"""
        # 设置扫描结果
        concrete_scanner.scan_result = ScanResult(
            status='success',
            count=20,
            metadata={'source': 'trade_table'}
        )
        
        # 模拟日志查询
        mock_log_entry = Mock(spec=TaskExecutionLog)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_log_entry
        mock_db_session.query.return_value = mock_query
        
        scheduled_time = datetime(2024, 1, 15, 14, 30, 0)
        
        # 执行扫描
        result = concrete_scanner.scan(mock_db_session, scheduled_time=scheduled_time)
        
        # 验证完整流程
        # 1. 任务开始日志被记录
        assert mock_db_session.add.call_count == 1
        start_log = mock_db_session.add.call_args[0][0]
        assert start_log.task_id.startswith('TEST_001_')
        assert start_log.scheduled_time == scheduled_time
        assert start_log.status == 'running'
        
        # 2. 扫描执行成功
        assert result.status == 'success'
        assert result.count == 20
        
        # 3. 任务完成日志被更新
        assert mock_log_entry.status == 'success'
        assert mock_log_entry.record_count == 20
        assert mock_log_entry.actual_end_time is not None
        assert mock_log_entry.execution_duration >= 0  # 执行时长应该被设置
    
    def test_multiple_scans_generate_unique_task_ids(self, concrete_scanner, mock_db_session):
        """测试多次扫描生成唯一任务ID"""
        # 模拟日志查询
        mock_log_entry = Mock(spec=TaskExecutionLog)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_log_entry
        mock_db_session.query.return_value = mock_query
        
        # 执行多次扫描
        task_ids = []
        for _ in range(3):
            concrete_scanner.scan(mock_db_session)
            log_entry = mock_db_session.add.call_args[0][0]
            task_ids.append(log_entry.task_id)
        
        # 验证所有任务ID唯一
        assert len(task_ids) == len(set(task_ids))
