-- ============================================================================
-- Table: audit_log
-- Description: 记录提醒处理闭环和敏感数据查询操作
-- Created: 2024-01-15
-- ============================================================================

CREATE TABLE IF NOT EXISTS audit_log (
    -- 主键
    id BIGSERIAL PRIMARY KEY,
    
    -- 日志标识
    log_id VARCHAR(100) NOT NULL UNIQUE,
    
    -- 事件信息
    event_type VARCHAR(50) NOT NULL,
    rule_code VARCHAR(50) NULL,
    
    -- 用户信息
    user_id VARCHAR(100) NOT NULL,
    user_name VARCHAR(200) NOT NULL,
    
    -- 操作信息
    operation_type VARCHAR(50) NULL,
    business_id VARCHAR(100) NULL,
    
    -- 数量变化
    count_before INT NULL,
    count_after INT NULL,
    
    -- 请求信息
    ip_address VARCHAR(50) NULL,
    user_agent VARCHAR(500) NULL,
    
    -- 时间戳
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 索引设计
-- ============================================================================

-- 日志ID唯一索引（用于防止重复记录）
CREATE UNIQUE INDEX IF NOT EXISTS uk_log_id ON audit_log(log_id);

-- 事件类型索引（用于按事件类型查询）
CREATE INDEX IF NOT EXISTS idx_event_type ON audit_log(event_type);

-- 规则代码索引（用于按规则查询审计日志）
CREATE INDEX IF NOT EXISTS idx_rule_code ON audit_log(rule_code);

-- 用户ID索引（用于按用户查询操作记录）
CREATE INDEX IF NOT EXISTS idx_user_id ON audit_log(user_id);

-- 时间戳索引（用于按时间范围查询）
CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_log(timestamp);

-- ============================================================================
-- 注释说明
-- ============================================================================

COMMENT ON TABLE audit_log IS '审计日志表，记录提醒处理闭环和敏感数据查询操作';
COMMENT ON COLUMN audit_log.id IS '主键，自增';
COMMENT ON COLUMN audit_log.log_id IS '日志唯一标识';
COMMENT ON COLUMN audit_log.event_type IS '事件类型';
COMMENT ON COLUMN audit_log.rule_code IS '关联的规则代码';
COMMENT ON COLUMN audit_log.user_id IS '操作用户ID';
COMMENT ON COLUMN audit_log.user_name IS '操作用户姓名';
COMMENT ON COLUMN audit_log.operation_type IS '操作类型';
COMMENT ON COLUMN audit_log.business_id IS '业务单据ID';
COMMENT ON COLUMN audit_log.count_before IS '操作前的提醒数量';
COMMENT ON COLUMN audit_log.count_after IS '操作后的提醒数量';
COMMENT ON COLUMN audit_log.ip_address IS '用户IP地址';
COMMENT ON COLUMN audit_log.user_agent IS '用户浏览器信息';
COMMENT ON COLUMN audit_log.timestamp IS '操作时间戳';
COMMENT ON COLUMN audit_log.created_at IS '创建时间';
