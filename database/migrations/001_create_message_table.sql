-- ============================================================================
-- Migration: 001_create_message_table
-- Description: 创建消息提醒表 (message_table)
-- Author: System
-- Created: 2024-01-15
-- ============================================================================

-- ============================================================================
-- UPGRADE: 创建表和索引
-- ============================================================================

-- 创建消息表
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

-- 创建索引（幂等性：IF NOT EXISTS）
CREATE INDEX IF NOT EXISTS idx_rule_code ON message_table(rule_code);
CREATE INDEX IF NOT EXISTS idx_last_updated ON message_table(last_updated);
CREATE INDEX IF NOT EXISTS idx_status ON message_table(status);

-- 创建触发器函数（幂等性：OR REPLACE）
CREATE OR REPLACE FUNCTION update_message_table_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 删除旧触发器（如果存在）并创建新触发器
DROP TRIGGER IF EXISTS trigger_update_message_table_updated_at ON message_table;
CREATE TRIGGER trigger_update_message_table_updated_at
    BEFORE UPDATE ON message_table
    FOR EACH ROW
    EXECUTE FUNCTION update_message_table_updated_at();

-- 添加表和字段注释
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

-- ============================================================================
-- DOWNGRADE: 删除表和相关对象
-- ============================================================================

-- 使用以下SQL语句回滚此迁移：
-- 
-- -- 删除触发器
-- DROP TRIGGER IF EXISTS trigger_update_message_table_updated_at ON message_table;
-- 
-- -- 删除触发器函数
-- DROP FUNCTION IF EXISTS update_message_table_updated_at();
-- 
-- -- 删除表（CASCADE会自动删除索引）
-- DROP TABLE IF EXISTS message_table CASCADE;

-- ============================================================================
-- 验证脚本
-- ============================================================================

-- 验证表是否创建成功
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_name = 'message_table'
    ) THEN
        RAISE NOTICE '✓ 表 message_table 创建成功';
    ELSE
        RAISE EXCEPTION '✗ 表 message_table 创建失败';
    END IF;
END $$;

-- 验证索引是否创建成功
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE tablename = 'message_table' 
        AND indexname = 'idx_rule_code'
    ) THEN
        RAISE NOTICE '✓ 索引 idx_rule_code 创建成功';
    ELSE
        RAISE EXCEPTION '✗ 索引 idx_rule_code 创建失败';
    END IF;
    
    IF EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE tablename = 'message_table' 
        AND indexname = 'idx_last_updated'
    ) THEN
        RAISE NOTICE '✓ 索引 idx_last_updated 创建成功';
    ELSE
        RAISE EXCEPTION '✗ 索引 idx_last_updated 创建失败';
    END IF;
    
    IF EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE tablename = 'message_table' 
        AND indexname = 'idx_status'
    ) THEN
        RAISE NOTICE '✓ 索引 idx_status 创建成功';
    ELSE
        RAISE EXCEPTION '✗ 索引 idx_status 创建失败';
    END IF;
END $$;

-- 验证触发器是否创建成功
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM pg_trigger 
        WHERE tgname = 'trigger_update_message_table_updated_at'
    ) THEN
        RAISE NOTICE '✓ 触发器 trigger_update_message_table_updated_at 创建成功';
    ELSE
        RAISE EXCEPTION '✗ 触发器 trigger_update_message_table_updated_at 创建失败';
    END IF;
END $$;

-- ============================================================================
-- 迁移完成
-- ============================================================================
