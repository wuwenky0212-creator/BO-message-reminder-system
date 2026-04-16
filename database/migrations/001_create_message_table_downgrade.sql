-- ============================================================================
-- Migration Downgrade: 001_create_message_table
-- Description: 回滚消息提醒表 (message_table) 的创建
-- Author: System
-- Created: 2024-01-15
-- ============================================================================

-- ============================================================================
-- DOWNGRADE: 删除表和相关对象
-- ============================================================================

-- 删除触发器
DROP TRIGGER IF EXISTS trigger_update_message_table_updated_at ON message_table;

-- 删除触发器函数
DROP FUNCTION IF EXISTS update_message_table_updated_at();

-- 删除表（CASCADE会自动删除索引和约束）
DROP TABLE IF EXISTS message_table CASCADE;

-- ============================================================================
-- 验证回滚
-- ============================================================================

-- 验证表是否已删除
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_name = 'message_table'
    ) THEN
        RAISE NOTICE '✓ 表 message_table 已成功删除';
    ELSE
        RAISE EXCEPTION '✗ 表 message_table 删除失败';
    END IF;
END $$;

-- 验证触发器函数是否已删除
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_proc 
        WHERE proname = 'update_message_table_updated_at'
    ) THEN
        RAISE NOTICE '✓ 触发器函数 update_message_table_updated_at 已成功删除';
    ELSE
        RAISE EXCEPTION '✗ 触发器函数 update_message_table_updated_at 删除失败';
    END IF;
END $$;

-- ============================================================================
-- 回滚完成
-- ============================================================================
