-- ============================================================================
-- Migration Downgrade: 003_create_task_execution_log
-- Description: 回滚任务执行日志表 (task_execution_log)
-- Author: System
-- Date: 2024-01-15
-- ============================================================================

-- 删除索引
DROP INDEX IF EXISTS idx_status;
DROP INDEX IF EXISTS idx_scheduled_time;
DROP INDEX IF EXISTS idx_rule_code;
DROP INDEX IF EXISTS uk_task_id;

-- 删除表
DROP TABLE IF EXISTS task_execution_log;

-- 验证表删除成功
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'task_execution_log') THEN
        RAISE NOTICE 'Table task_execution_log dropped successfully';
    ELSE
        RAISE EXCEPTION 'Failed to drop table task_execution_log';
    END IF;
END $$;
