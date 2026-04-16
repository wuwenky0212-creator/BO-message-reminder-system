"""
规则扫描器基类

提供规则扫描器的基础框架和通用功能。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any, Dict
import uuid
import logging

from sqlalchemy.orm import Session

from backend.models.task_execution_log import TaskExecutionLog
from backend.scanner.timeout_control import QueryTimeoutControl, TimeoutException


logger = logging.getLogger(__name__)


@dataclass
class ScanResult:
    """扫描结果数据类"""
    status: str  # success/timeout/error
    count: int  # 扫描到的记录数量，-1表示超时或错误
    error_message: Optional[str] = None
    data: Optional[Any] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseRuleScanner(ABC):
    """规则扫描器基类"""
    
    def __init__(
        self,
        rule_code: str,
        rule_name: str,
        timeout_seconds: int = 10
    ):
        """
        初始化规则扫描器
        
        Args:
            rule_code: 规则代码
            rule_name: 规则名称
            timeout_seconds: 查询超时时间（秒），默认10秒
        """
        self.rule_code = rule_code
        self.rule_name = rule_name
        self.timeout_seconds = timeout_seconds
        self.timeout_control = QueryTimeoutControl(timeout_seconds)
    
    @abstractmethod
    def execute_scan(self, db: Session) -> ScanResult:
        """
        执行扫描逻辑（子类必须实现）
        
        Args:
            db: 数据库会话
            
        Returns:
            ScanResult: 扫描结果
        """
        pass
    
    def scan(self, db: Session, scheduled_time: Optional[datetime] = None) -> ScanResult:
        """
        执行规则扫描（带超时控制和日志记录）
        
        Args:
            db: 数据库会话
            scheduled_time: 计划执行时间，默认为当前时间
            
        Returns:
            ScanResult: 扫描结果
        """
        if scheduled_time is None:
            scheduled_time = datetime.now()
        
        task_id = self._generate_task_id()
        actual_start_time = datetime.now()
        
        logger.info(f"Starting scan for rule {self.rule_code} (task_id: {task_id})")
        
        # 记录任务开始日志
        self._log_task_start(db, task_id, scheduled_time, actual_start_time)
        
        try:
            # 执行扫描（带超时控制）
            with self.timeout_control.timeout_context():
                result = self.execute_scan(db)
            
            # 记录任务成功日志
            actual_end_time = datetime.now()
            execution_duration = int((actual_end_time - actual_start_time).total_seconds() * 1000)
            
            self._log_task_completion(
                db=db,
                task_id=task_id,
                actual_end_time=actual_end_time,
                execution_duration=execution_duration,
                status=result.status,
                record_count=result.count,
                error_message=result.error_message
            )
            
            logger.info(
                f"Scan completed for rule {self.rule_code}: "
                f"status={result.status}, count={result.count}, "
                f"duration={execution_duration}ms"
            )
            
            return result
            
        except TimeoutException as e:
            # 处理超时异常
            actual_end_time = datetime.now()
            execution_duration = int((actual_end_time - actual_start_time).total_seconds() * 1000)
            error_message = str(e)
            
            logger.warning(f"Scan timeout for rule {self.rule_code}: {error_message}")
            
            result = ScanResult(
                status='timeout',
                count=-1,
                error_message=error_message
            )
            
            self._log_task_completion(
                db=db,
                task_id=task_id,
                actual_end_time=actual_end_time,
                execution_duration=execution_duration,
                status='timeout',
                record_count=-1,
                error_message=error_message
            )
            
            return result
            
        except Exception as e:
            # 处理其他异常
            actual_end_time = datetime.now()
            execution_duration = int((actual_end_time - actual_start_time).total_seconds() * 1000)
            error_message = f"{type(e).__name__}: {str(e)}"
            
            logger.error(f"Scan failed for rule {self.rule_code}: {error_message}", exc_info=True)
            
            result = ScanResult(
                status='error',
                count=-1,
                error_message=error_message
            )
            
            self._log_task_completion(
                db=db,
                task_id=task_id,
                actual_end_time=actual_end_time,
                execution_duration=execution_duration,
                status='failed',
                record_count=-1,
                error_message=error_message
            )
            
            return result
    
    def _generate_task_id(self) -> str:
        """
        生成任务唯一标识
        
        Returns:
            str: 任务ID，格式为 {rule_code}_{timestamp}_{uuid}
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        return f"{self.rule_code}_{timestamp}_{unique_id}"
    
    def _log_task_start(
        self,
        db: Session,
        task_id: str,
        scheduled_time: datetime,
        actual_start_time: datetime
    ) -> None:
        """
        记录任务开始日志
        
        Args:
            db: 数据库会话
            task_id: 任务ID
            scheduled_time: 计划执行时间
            actual_start_time: 实际开始时间
        """
        log_entry = TaskExecutionLog(
            task_id=task_id,
            rule_code=self.rule_code,
            rule_name=self.rule_name,
            scheduled_time=scheduled_time,
            actual_start_time=actual_start_time,
            status='running'
        )
        db.add(log_entry)
        db.commit()
    
    def _log_task_completion(
        self,
        db: Session,
        task_id: str,
        actual_end_time: datetime,
        execution_duration: int,
        status: str,
        record_count: int,
        error_message: Optional[str] = None
    ) -> None:
        """
        记录任务完成日志
        
        Args:
            db: 数据库会话
            task_id: 任务ID
            actual_end_time: 实际结束时间
            execution_duration: 执行时长（毫秒）
            status: 执行状态
            record_count: 记录数量
            error_message: 错误信息（可选）
        """
        log_entry = db.query(TaskExecutionLog).filter(
            TaskExecutionLog.task_id == task_id
        ).first()
        
        if log_entry:
            log_entry.actual_end_time = actual_end_time
            log_entry.execution_duration = execution_duration
            log_entry.status = status
            log_entry.record_count = record_count
            log_entry.error_message = error_message
            db.commit()
