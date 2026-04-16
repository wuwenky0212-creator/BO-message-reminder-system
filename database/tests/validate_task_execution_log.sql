-- ============================================================================
-- Validation Script: task_execution_log
-- Description: 验证任务执行日志表的结构、索引和功能
-- Date: 2024-01-15
-- ============================================================================

-- ============================================================================
-- 1. 验证表是否存在
-- ============================================================================
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'task_execution_log') THEN
        RAISE NOTICE '✓ Table task_execution_log exists';
    ELSE
        RAISE EXCEPTION '✗ Table task_execution_log does not exist';
    END IF;
END $$;

-- ============================================================================
-- 2. 验证表结构
-- ============================================================================
SELECT 
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'task_execution_log'
ORDER BY ordinal_position;

-- 验证必需字段
DO $$
DECLARE
    required_columns TEXT[] := ARRAY[
        'id', 'task_id', 'rule_code', 'rule_name', 
        'scheduled_time', 'actual_start_time', 'actual_end_time',
        'execution_duration', 'status', 'record_count', 
        'error_message', 'created_at'
    ];
    col TEXT;
    missing_columns TEXT[] := ARRAY[]::TEXT[];
BEGIN
    FOREACH col IN ARRAY required_columns
    LOOP
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'task_execution_log' AND column_name = col
        ) THEN
            missing_columns := array_append(missing_columns, col);
        END IF;
    END LOOP;
    
    IF array_length(missing_columns, 1) IS NULL THEN
        RAISE NOTICE '✓ All required columns exist';
    ELSE
        RAISE EXCEPTION '✗ Missing columns: %', array_to_string(missing_columns, ', ');
    END IF;
END $$;

-- ============================================================================
-- 3. 验证索引
-- ============================================================================
SELECT 
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'task_execution_log'
ORDER BY indexname;

-- 验证必需索引
DO $$
DECLARE
    required_indexes TEXT[] := ARRAY[
        'uk_task_id',
        'idx_rule_code',
        'idx_scheduled_time',
        'idx_status'
    ];
    idx TEXT;
    missing_indexes TEXT[] := ARRAY[]::TEXT[];
BEGIN
    FOREACH idx IN ARRAY required_indexes
    LOOP
        IF NOT EXISTS (
            SELECT 1 FROM pg_indexes 
            WHERE tablename = 'task_execution_log' AND indexname = idx
        ) THEN
            missing_indexes := array_append(missing_indexes, idx);
        END IF;
    END LOOP;
    
    IF array_length(missing_indexes, 1) IS NULL THEN
        RAISE NOTICE '✓ All required indexes exist';
    ELSE
        RAISE EXCEPTION '✗ Missing indexes: %', array_to_string(missing_indexes, ', ');
    END IF;
END $$;

-- ============================================================================
-- 4. 验证唯一约束
-- ============================================================================
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'task_execution_log' 
        AND indexname = 'uk_task_id'
        AND indexdef LIKE '%UNIQUE%'
    ) THEN
        RAISE NOTICE '✓ Unique constraint on task_id exists';
    ELSE
        RAISE EXCEPTION '✗ Unique constraint on task_id does not exist';
    END IF;
END $$;

-- ============================================================================
-- 5. 测试数据插入
-- ============================================================================
-- 插入测试数据
INSERT INTO task_execution_log (
    task_id,
    rule_code,
    rule_name,
    scheduled_time,
    actual_start_time,
    actual_end_time,
    execution_duration,
    status,
    record_count,
    error_message
) VALUES (
    'TEST_TASK_001',
    'CHK_TRD_004',
    '交易复核提醒',
    '2024-01-15 14:30:00',
    '2024-01-15 14:30:01',
    '2024-01-15 14:30:05',
    4000,
    'completed',
    15,
    NULL
);

-- 验证插入成功
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM task_execution_log WHERE task_id = 'TEST_TASK_001') THEN
        RAISE NOTICE '✓ Test data inserted successfully';
    ELSE
        RAISE EXCEPTION '✗ Failed to insert test data';
    END IF;
END $$;

-- ============================================================================
-- 6. 测试唯一约束
-- ============================================================================
-- 尝试插入重复的task_id（应该失败）
DO $$
BEGIN
    BEGIN
        INSERT INTO task_execution_log (
            task_id,
            rule_code,
            rule_name,
            scheduled_time,
            actual_start_time,
            status
        ) VALUES (
            'TEST_TASK_001',
            'CHK_BO_001',
            '未证实匹配',
            '2024-01-15 15:00:00',
            '2024-01-15 15:00:01',
            'completed'
        );
        RAISE EXCEPTION '✗ Unique constraint on task_id is not working';
    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE '✓ Unique constraint on task_id is working';
    END;
END $$;

-- ============================================================================
-- 7. 测试查询功能
-- ============================================================================
-- 按rule_code查询
SELECT 
    task_id,
    rule_code,
    rule_name,
    status,
    record_count
FROM task_execution_log
WHERE rule_code = 'CHK_TRD_004';

-- 按status查询
SELECT 
    task_id,
    rule_code,
    status,
    execution_duration
FROM task_execution_log
WHERE status = 'completed';

-- 按scheduled_time查询
SELECT 
    task_id,
    rule_code,
    scheduled_time,
    actual_start_time
FROM task_execution_log
WHERE scheduled_time >= '2024-01-15 00:00:00'
ORDER BY scheduled_time DESC;

-- ============================================================================
-- 8. 测试更新功能
-- ============================================================================
UPDATE task_execution_log
SET 
    actual_end_time = '2024-01-15 14:30:06',
    execution_duration = 5000,
    record_count = 20
WHERE task_id = 'TEST_TASK_001';

-- 验证更新成功
DO $$
DECLARE
    updated_count INT;
BEGIN
    SELECT record_count INTO updated_count
    FROM task_execution_log
    WHERE task_id = 'TEST_TASK_001';
    
    IF updated_count = 20 THEN
        RAISE NOTICE '✓ Update operation successful';
    ELSE
        RAISE EXCEPTION '✗ Update operation failed';
    END IF;
END $$;

-- ============================================================================
-- 9. 测试删除功能
-- ============================================================================
DELETE FROM task_execution_log WHERE task_id = 'TEST_TASK_001';

-- 验证删除成功
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM task_execution_log WHERE task_id = 'TEST_TASK_001') THEN
        RAISE NOTICE '✓ Delete operation successful';
    ELSE
        RAISE EXCEPTION '✗ Delete operation failed';
    END IF;
END $$;

-- ============================================================================
-- 10. 性能测试 - 批量插入
-- ============================================================================
-- 插入100条测试数据
INSERT INTO task_execution_log (
    task_id,
    rule_code,
    rule_name,
    scheduled_time,
    actual_start_time,
    actual_end_time,
    execution_duration,
    status,
    record_count
)
SELECT 
    'PERF_TEST_' || generate_series,
    CASE (generate_series % 6)
        WHEN 0 THEN 'CHK_TRD_004'
        WHEN 1 THEN 'CHK_BO_001'
        WHEN 2 THEN 'CHK_CONF_005'
        WHEN 3 THEN 'CHK_SW_002'
        WHEN 4 THEN 'CHK_SETT_006'
        ELSE 'CHK_SEC_003'
    END,
    '测试规则',
    CURRENT_TIMESTAMP - (generate_series || ' hours')::INTERVAL,
    CURRENT_TIMESTAMP - (generate_series || ' hours')::INTERVAL + INTERVAL '1 second',
    CURRENT_TIMESTAMP - (generate_series || ' hours')::INTERVAL + INTERVAL '5 seconds',
    FLOOR(RANDOM() * 10000)::INT,
    CASE (generate_series % 3)
        WHEN 0 THEN 'completed'
        WHEN 1 THEN 'failed'
        ELSE 'timeout'
    END,
    FLOOR(RANDOM() * 100)::INT
FROM generate_series(1, 100);

-- 验证批量插入
DO $$
DECLARE
    inserted_count INT;
BEGIN
    SELECT COUNT(*) INTO inserted_count
    FROM task_execution_log
    WHERE task_id LIKE 'PERF_TEST_%';
    
    IF inserted_count = 100 THEN
        RAISE NOTICE '✓ Batch insert successful: % records', inserted_count;
    ELSE
        RAISE EXCEPTION '✗ Batch insert failed: expected 100, got %', inserted_count;
    END IF;
END $$;

-- ============================================================================
-- 11. 索引性能验证
-- ============================================================================
-- 使用EXPLAIN ANALYZE验证索引使用
EXPLAIN ANALYZE
SELECT * FROM task_execution_log WHERE rule_code = 'CHK_TRD_004';

EXPLAIN ANALYZE
SELECT * FROM task_execution_log WHERE status = 'completed';

EXPLAIN ANALYZE
SELECT * FROM task_execution_log 
WHERE scheduled_time >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
ORDER BY scheduled_time DESC;

-- ============================================================================
-- 12. 清理测试数据
-- ============================================================================
DELETE FROM task_execution_log WHERE task_id LIKE 'PERF_TEST_%';

-- 验证清理成功
DO $$
DECLARE
    remaining_count INT;
BEGIN
    SELECT COUNT(*) INTO remaining_count
    FROM task_execution_log
    WHERE task_id LIKE 'PERF_TEST_%';
    
    IF remaining_count = 0 THEN
        RAISE NOTICE '✓ Test data cleaned up successfully';
    ELSE
        RAISE EXCEPTION '✗ Failed to clean up test data: % records remaining', remaining_count;
    END IF;
END $$;

-- ============================================================================
-- 验证总结
-- ============================================================================
SELECT 
    'task_execution_log' AS table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'task_execution_log') AS column_count,
    (SELECT COUNT(*) FROM pg_indexes WHERE tablename = 'task_execution_log') AS index_count,
    (SELECT COUNT(*) FROM task_execution_log) AS record_count;

RAISE NOTICE '============================================================================';
RAISE NOTICE 'Validation completed successfully!';
RAISE NOTICE '============================================================================';
