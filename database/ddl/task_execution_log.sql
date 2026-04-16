-- ============================================================================
-- Table: task_execution_log
-- Description: 记录每次定时任务的执行情况
-- Created: 2024-01-15
-- ============================================================================

CREATE TABLE IF NOT EXISTS task_execution_log (
    -- 主键
    id BIGSERIAL PRIMARY KEY,
    
    -- 任务标识
    task_id VARCHAR(100) NOT NULL UNIQUE,
    
    -- 规则信息
    rule_code VARCHAR(50) NOT NULL,
    rule_name VARCHAR(200) NOT NULL,
    
    -- 时间信息
    scheduled_time TIMESTAMP NOT NULL,
    actual_start_time TIMESTAMP NOT NULL,
    actual_end_time TIMESTAMP NULL,
    execution_duration INT NULL,
    
    -- 执行结果
    status VARCHAR(20) NOT NULL,
    record_count INT NULL,
    error_message TEXT NULL,
    
    -- 审计字段
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 索引设计
-- ============================================================================

-- 任务ID唯一索引
CREATE UNIQUE INDEX IF NOT EXISTS uk_task_id ON task_execution_log(task_id);

-- 规则代码索引（用于按规则查询执行日志）
CREATE INDEX IF NOT EXISTS idx_rule_code ON task_execution_log(rule_code);

-- 计划执行时间索引（用于按时间查询）
CREATE INDEX IF NOT EXISTS idx_scheduled_time ON task_execution_log(scheduled_time);

-- 状态索引（用于按状态过滤）
CREATE INDEX IF NOT EXISTS idx_status ON task_execution_log(status);

-- ============================================================================
-- 注释说明
-- ============================================================================

COMMENT ON TABLE task_execution_log IS '任务执行日志表，记录每次定时任务的执行情况';
COMMENT ON COLUMN task_execution_log.id IS '主键，自增';
COMMENT ON COLUMN task_execution_log.task_id IS '任务唯一标识';
COMMENT ON COLUMN task_execution_log.rule_code IS '规则代码，如CHK_TRD_004';
COMMENT ON COLUMN task_execution_log.rule_name IS '规则名称';
COMMENT ON COLUMN task_execution_log.scheduled_time IS '计划执行时间';
COMMENT ON COLUMN task_execution_log.actual_start_time IS '实际开始时间';
COMMENT ON COLUMN task_execution_log.actual_end_time IS '实际结束时间';
COMMENT ON COLUMN task_execution_log.execution_duration IS '执行时长（毫秒）';
COMMENT ON COLUMN task_execution_log.status IS '执行状态：completed/failed/timeout';
COMMENT ON COLUMN task_execution_log.record_count IS '扫描到的记录数量';
COMMENT ON COLUMN task_execution_log.error_message IS '错误信息';
COMMENT ON COLUMN task_execution_log.created_at IS '创建时间';
