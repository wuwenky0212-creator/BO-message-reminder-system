-- ============================================================================
-- Migration Downgrade: 002_create_rule_config_table
-- Description: 删除规则配置表 (rule_config_table)
-- Created: 2024-01-15
-- ============================================================================

-- ============================================================================
-- 1. 删除触发器
-- ============================================================================

DROP TRIGGER IF EXISTS trigger_update_rule_config_table_updated_at ON rule_config_table;

-- ============================================================================
-- 2. 删除触发器函数
-- ============================================================================

DROP FUNCTION IF EXISTS update_rule_config_table_updated_at();

-- ============================================================================
-- 3. 删除表（索引会自动删除）
-- ============================================================================

DROP TABLE IF EXISTS rule_config_table;

-- ============================================================================
-- 4. 验证降级
-- ============================================================================

DO $$
DECLARE
    v_table_exists BOOLEAN;
    v_function_exists BOOLEAN;
BEGIN
    -- 检查表是否已删除
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'rule_config_table'
    ) INTO v_table_exists;
    
    IF NOT v_table_exists THEN
        RAISE NOTICE '✓ 表 rule_config_table 已成功删除';
    ELSE
        RAISE EXCEPTION '✗ 表 rule_config_table 删除失败';
    END IF;
    
    -- 检查触发器函数是否已删除
    SELECT EXISTS (
        SELECT FROM pg_proc 
        WHERE proname = 'update_rule_config_table_updated_at'
    ) INTO v_function_exists;
    
    IF NOT v_function_exists THEN
        RAISE NOTICE '✓ 触发器函数 update_rule_config_table_updated_at 已成功删除';
    ELSE
        RAISE EXCEPTION '✗ 触发器函数 update_rule_config_table_updated_at 删除失败';
    END IF;
    
    RAISE NOTICE '========================================';
    RAISE NOTICE '降级 002_create_rule_config_table 执行成功';
    RAISE NOTICE '========================================';
END $$;
