-- ============================================================================
-- Test: 验证 rule_config_table 的唯一索引 uk_rule_code
-- Description: 测试 rule_code 字段的唯一性约束是否正常工作
-- Created: 2024-01-15
-- ============================================================================

-- 开始测试
DO $$
DECLARE
    v_test_passed BOOLEAN := TRUE;
    v_error_message TEXT;
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE '开始测试 rule_config_table 唯一索引';
    RAISE NOTICE '========================================';
    
    -- ========================================================================
    -- 测试1: 验证唯一索引存在
    -- ========================================================================
    RAISE NOTICE '';
    RAISE NOTICE '测试1: 验证唯一索引 uk_rule_code 是否存在';
    
    IF EXISTS (
        SELECT FROM pg_indexes 
        WHERE schemaname = 'public' 
        AND tablename = 'rule_config_table' 
        AND indexname = 'uk_rule_code'
    ) THEN
        RAISE NOTICE '✓ 测试1通过: 唯一索引 uk_rule_code 存在';
    ELSE
        RAISE NOTICE '✗ 测试1失败: 唯一索引 uk_rule_code 不存在';
        v_test_passed := FALSE;
    END IF;
    
    -- ========================================================================
    -- 测试2: 验证唯一索引是否为 UNIQUE 类型
    -- ========================================================================
    RAISE NOTICE '';
    RAISE NOTICE '测试2: 验证索引 uk_rule_code 是否为 UNIQUE 类型';
    
    IF EXISTS (
        SELECT FROM pg_indexes 
        WHERE schemaname = 'public' 
        AND tablename = 'rule_config_table' 
        AND indexname = 'uk_rule_code'
        AND indexdef LIKE '%UNIQUE%'
    ) THEN
        RAISE NOTICE '✓ 测试2通过: uk_rule_code 是 UNIQUE 索引';
    ELSE
        RAISE NOTICE '✗ 测试2失败: uk_rule_code 不是 UNIQUE 索引';
        v_test_passed := FALSE;
    END IF;
    
    -- ========================================================================
    -- 测试3: 验证唯一约束 - 尝试插入重复的 rule_code
    -- ========================================================================
    RAISE NOTICE '';
    RAISE NOTICE '测试3: 验证唯一约束 - 尝试插入重复的 rule_code';
    
    BEGIN
        -- 尝试插入一个已存在的 rule_code
        INSERT INTO rule_config_table (
            rule_code,
            rule_name,
            scheduled_time,
            cron_expression,
            target_roles,
            enabled,
            query_sql,
            timeout_seconds
        ) VALUES (
            'CHK_TRD_004',  -- 这个 rule_code 已经存在
            '测试重复规则',
            '14:30',
            '30 14 * * 1-5',
            '["Test"]'::JSON,
            TRUE,
            'SELECT 1',
            5
        );
        
        -- 如果执行到这里，说明插入成功了，测试失败
        RAISE NOTICE '✗ 测试3失败: 允许插入重复的 rule_code';
        v_test_passed := FALSE;
        
        -- 清理测试数据
        DELETE FROM rule_config_table WHERE rule_name = '测试重复规则';
        
    EXCEPTION
        WHEN unique_violation THEN
            -- 捕获到唯一性约束违反异常，说明测试通过
            RAISE NOTICE '✓ 测试3通过: 正确阻止了重复的 rule_code 插入';
            RAISE NOTICE '  错误信息: %', SQLERRM;
    END;
    
    -- ========================================================================
    -- 测试4: 验证可以插入新的唯一 rule_code
    -- ========================================================================
    RAISE NOTICE '';
    RAISE NOTICE '测试4: 验证可以插入新的唯一 rule_code';
    
    BEGIN
        -- 插入一个新的唯一 rule_code
        INSERT INTO rule_config_table (
            rule_code,
            rule_name,
            scheduled_time,
            cron_expression,
            target_roles,
            enabled,
            query_sql,
            timeout_seconds
        ) VALUES (
            'TEST_UNIQUE_001',
            '测试唯一规则',
            '14:30',
            '30 14 * * 1-5',
            '["Test"]'::JSON,
            TRUE,
            'SELECT 1',
            5
        );
        
        RAISE NOTICE '✓ 测试4通过: 成功插入新的唯一 rule_code';
        
        -- 清理测试数据
        DELETE FROM rule_config_table WHERE rule_code = 'TEST_UNIQUE_001';
        
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE '✗ 测试4失败: 无法插入新的唯一 rule_code';
            RAISE NOTICE '  错误信息: %', SQLERRM;
            v_test_passed := FALSE;
    END;
    
    -- ========================================================================
    -- 测试5: 验证更新操作不违反唯一约束
    -- ========================================================================
    RAISE NOTICE '';
    RAISE NOTICE '测试5: 验证更新操作不违反唯一约束';
    
    BEGIN
        -- 先插入一个测试记录
        INSERT INTO rule_config_table (
            rule_code,
            rule_name,
            scheduled_time,
            cron_expression,
            target_roles,
            enabled,
            query_sql,
            timeout_seconds
        ) VALUES (
            'TEST_UPDATE_001',
            '测试更新规则',
            '14:30',
            '30 14 * * 1-5',
            '["Test"]'::JSON,
            TRUE,
            'SELECT 1',
            5
        );
        
        -- 尝试更新为已存在的 rule_code
        UPDATE rule_config_table 
        SET rule_code = 'CHK_TRD_004' 
        WHERE rule_code = 'TEST_UPDATE_001';
        
        -- 如果执行到这里，说明更新成功了，测试失败
        RAISE NOTICE '✗ 测试5失败: 允许更新为重复的 rule_code';
        v_test_passed := FALSE;
        
        -- 清理测试数据
        DELETE FROM rule_config_table WHERE rule_code IN ('TEST_UPDATE_001', 'CHK_TRD_004');
        
    EXCEPTION
        WHEN unique_violation THEN
            -- 捕获到唯一性约束违反异常，说明测试通过
            RAISE NOTICE '✓ 测试5通过: 正确阻止了更新为重复的 rule_code';
            RAISE NOTICE '  错误信息: %', SQLERRM;
            
            -- 清理测试数据
            DELETE FROM rule_config_table WHERE rule_code = 'TEST_UPDATE_001';
    END;
    
    -- ========================================================================
    -- 测试6: 验证初始化数据的 rule_code 都是唯一的
    -- ========================================================================
    RAISE NOTICE '';
    RAISE NOTICE '测试6: 验证初始化数据的 rule_code 都是唯一的';
    
    DECLARE
        v_total_count INT;
        v_unique_count INT;
    BEGIN
        -- 统计总记录数
        SELECT COUNT(*) INTO v_total_count FROM rule_config_table;
        
        -- 统计唯一 rule_code 数量
        SELECT COUNT(DISTINCT rule_code) INTO v_unique_count FROM rule_config_table;
        
        IF v_total_count = v_unique_count THEN
            RAISE NOTICE '✓ 测试6通过: 所有 rule_code 都是唯一的 (总数: %, 唯一数: %)', v_total_count, v_unique_count;
        ELSE
            RAISE NOTICE '✗ 测试6失败: 存在重复的 rule_code (总数: %, 唯一数: %)', v_total_count, v_unique_count;
            v_test_passed := FALSE;
        END IF;
    END;
    
    -- ========================================================================
    -- 测试总结
    -- ========================================================================
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    IF v_test_passed THEN
        RAISE NOTICE '✓ 所有测试通过！';
        RAISE NOTICE '唯一索引 uk_rule_code 工作正常';
    ELSE
        RAISE NOTICE '✗ 部分测试失败！';
        RAISE NOTICE '请检查唯一索引 uk_rule_code 的配置';
    END IF;
    RAISE NOTICE '========================================';
    
END $$;
