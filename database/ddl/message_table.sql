-- ============================================================================
-- Table: message_table
-- Description: 存储所有提醒消息记录
-- Created: 2024-01-15
-- ============================================================================

CREATE TABLE IF NOT EXISTS message_table (
    -- 主键
    id BIGSERIAL PRIMARY KEY,
    
    -- 规则信息
    rule_code VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    
    -- 统计信息
    count INT NOT NULL,
    last_updated TIMESTAMP NOT NULL,
    
    -- 状态信息
    status VARCHAR(20) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    
    -- 目标接收人和扩展信息
    target_roles JSON NOT NULL,
    metadata JSON NULL,
    
    -- 审计字段
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 索引设计
-- ============================================================================

-- 规则代码索引（用于按规则查询提醒）
CREATE INDEX IF NOT EXISTS idx_rule_code ON message_table(rule_code);

-- 最后更新时间索引（用于按时间排序）
CREATE INDEX IF NOT EXISTS idx_last_updated ON message_table(last_updated);

-- 状态索引（用于按状态过滤）
CREATE INDEX IF NOT EXISTS idx_status ON message_table(status);

-- ============================================================================
-- 触发器：自动更新 updated_at 字段
-- ============================================================================

CREATE OR REPLACE FUNCTION update_message_table_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_message_table_updated_at
    BEFORE UPDATE ON message_table
    FOR EACH ROW
    EXECUTE FUNCTION update_message_table_updated_at();

-- ============================================================================
-- 注释说明
-- ============================================================================

COMMENT ON TABLE message_table IS '消息提醒表，存储所有提醒消息记录';
COMMENT ON COLUMN message_table.id IS '主键，自增';
COMMENT ON COLUMN message_table.rule_code IS '规则代码，如CHK_TRD_004';
COMMENT ON COLUMN message_table.title IS '提醒标题';
COMMENT ON COLUMN message_table.count IS '待处理数量';
COMMENT ON COLUMN message_table.last_updated IS '最后更新时间';
COMMENT ON COLUMN message_table.status IS '扫描状态：success/timeout/error';
COMMENT ON COLUMN message_table.priority IS '优先级：normal/high/critical';
COMMENT ON COLUMN message_table.target_roles IS '目标接收人角色列表（JSON格式）';
COMMENT ON COLUMN message_table.metadata IS '扩展元数据（JSON格式）';
COMMENT ON COLUMN message_table.created_at IS '创建时间';
COMMENT ON COLUMN message_table.updated_at IS '更新时间';
