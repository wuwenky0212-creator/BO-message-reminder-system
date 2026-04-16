"""
查询超时控制模块

提供数据库查询超时控制功能。
"""

import sys
import threading
from typing import Optional
from contextlib import contextmanager


class TimeoutException(Exception):
    """查询超时异常"""
    pass


class QueryTimeoutControl:
    """查询超时控制器（跨平台实现）"""
    
    def __init__(self, timeout_seconds: int):
        """
        初始化超时控制器
        
        Args:
            timeout_seconds: 超时时间（秒）
        """
        self.timeout_seconds = timeout_seconds
        self._timer = None
    
    @contextmanager
    def timeout_context(self):
        """
        超时上下文管理器（使用线程定时器实现，支持Windows）
        
        Raises:
            TimeoutException: 当查询执行超时时抛出
        """
        timeout_occurred = threading.Event()
        
        def timeout_handler():
            timeout_occurred.set()
        
        # 启动定时器
        self._timer = threading.Timer(self.timeout_seconds, timeout_handler)
        self._timer.daemon = True
        self._timer.start()
        
        try:
            yield
            # 检查是否超时
            if timeout_occurred.is_set():
                raise TimeoutException(f"Query execution timeout after {self.timeout_seconds} seconds")
        finally:
            # 取消定时器
            if self._timer:
                self._timer.cancel()
                self._timer = None
