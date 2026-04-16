-- ============================================================================
-- Migration: 004_create_audit_log
-- Description: 创建审计日志表 (audit_log)
-- Author: System
-- Created: 2024-01-15
-- ============================================================================

-- ============================================================================
-- UPGRADE: 创建表和索引
-- ============================================================================

-- 创建审计日志表
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

-- 创建索引（幂等性：IF NOT EXISTS）
CREATE UNIQUE INDEX IF NOT EXISTS uk_log_id ON audit_log(log_id);
CREATE INDEX IF NOT EXISTS idx_event_type ON audit_log(event_type);
CREATE INDEX IF NOT EXISTS idx_rule_code ON audit_log(rule_code);
CREATE INDEX IF NOT EXISTS idx_user_id ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_log(timestamp);

-- 添加表和字段注释
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

-- ============================================================================
-- DOWNGRADE: 删除表和相关对象
-- ============================================================================

-- 使用以下SQL语句回滚此迁移：
-- 
-- -- 删除表（CASCADE会自动删除索引）
-- DROP TABLE IF EXISTS audit_log CASCADE;

-- ============================================================================
-- 验证脚本
-- ============================================================================

-- 验证表是否创建成功
DO $
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_name = 'audit_log'
    ) THEN
        RAISE NOTICE '✓ 表 audit_log 创建成功';
    ELSE
        RAISE EXCEPTION '✗ 表 audit_log 创建失败';
    END IF;
END $;

-- 验证索引是否创建成功
DO $
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE tablename = 'audit_log' 
        AND indexname = 'uk_log_id'
    ) THEN
        RAISE NOTICE '✓ 唯一索引 uk_log_id 创建成功';
    ELSE
        RAISE EXCEPTION '✗ 唯一索引 uk_log_id 创建失败';
    END IF;
    
    IF EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE tablename = 'audit_log' 
        AND indexname = 'idx_event_type'
    ) THEN
        RAISE NOTICE '✓ 索引 idx_event_type 创建成功';
    ELSE
        RAISE EXCEPTION '✗ 索引 idx_event_type 创建失败';
    END IF;
    
    IF EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE tablename = 'audit_log' 
        AND indexname = 'idx_rule_code'
    ) THEN
        RAISE NOTICE '✓ 索引 idx_rule_code 创建成功';
    ELSE
        RAISE EXCEPTION '✗ 索引 idx_rule_code 创建失败';
    END IF;
    
    IF EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE tablename = 'audit_log' 
        AND indexname = 'idx_user_id'
    ) THEN
        RAISE NOTICE '✓ 索引 idx_user_id 创建成功';
    ELSE
        RAISE EXCEPTION '✗ 索引 idx_user_id 创建失败';
    END IF;
    
    IF EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE tablename = 'audit_log' 
        AND indexname = 'idx_timestamp'
    ) THEN
        RAISE NOTICE '✓ 索引 idx_timestamp 创建成功';
    ELSE
        RAISE EXCEPTION '✗ 索引 idx_timestamp 创建失败';
    END IF;
END $;

-- ============================================================================
-- 迁移完成
-- ============================================================================
