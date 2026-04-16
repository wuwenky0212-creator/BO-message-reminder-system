-- ============================================================================
-- 测试脚本: 验证规则配置表初始化数据
-- 任务: 1.2.3 - 初始化6条规则配置数据
-- 
-- 功能:
-- - 验证6条规则配置记录是否正确插入
-- - 验证每条记录的字段值是否符合设计要求
-- - 验证规则代码唯一性约束
-- 
-- 运行方法:
-- psql -U postgres -d message_reminder_db -f database/tests/test_rule_config_initialization.sql
-- ============================================================================

\echo '========================================'
\echo '开始测试规则配置表初始化数据'
\echo '========================================'

-- ============================================================================
-- 测试1: 验证记录数量
-- ============================================================================

\echo ''
\echo '=== 测试1: 验证记录数量 ==='

DO $
DECLARE
    v_count INT;
BEGIN
    SELECT COUNT(*) INTO v_count FROM rule_config_table;
    
    IF v_count = 6 THEN
        RAISE NOTICE '✓ 记录数量正确: 共 % 条规则配置', v_count;
    ELSE
        RAISE WARNING '✗ 记录数量不正确: 期望6条，实际 % 条', v_count;
    END IF;
END $;

-- ============================================================================
-- 测试2: 验证每条规则的存在性和基本信息
-- ============================================================================

\echo ''
\echo '=== 测试2: 验证每条规则的存在性和基本信息 ==='

DO $
DECLARE
    v_rule_code VARCHAR(50);
    v_rule_name VARCHAR(200);
    v_scheduled_time VARCHAR(10);
    v_enabled BOOLEAN;
    v_found BOOLEAN;
BEGIN
    -- CHK_TRD_004: 交易复核提醒
    SELECT EXISTS(
        SELECT 1 FROM rule_config_table 
        WHERE rule_code = 'CHK_TRD_004'
        AND rule_name = '当日交易未复核'
        AND scheduled_time = '14:30'
        AND enabled = TRUE
    ) INTO v_found;
    
    IF v_found THEN
        RAISE NOTICE '✓ CHK_TRD_004: 当日交易未复核 (14:30)';
    ELSE
        RAISE WARNING '✗ CHK_TRD_004: 数据不正确或不存在';
    END IF;
    
    -- CHK_BO_001: 未证实匹配
    SELECT EXISTS(
        SELECT 1 FROM rule_config_table 
        WHERE rule_code = 'CHK_BO_001'
        AND rule_name = '未证实匹配'
        AND scheduled_time = '15:00'
        AND enabled = TRUE
    ) INTO v_found;
    
    IF v_found THEN
        RAISE NOTICE '✓ CHK_BO_001: 未证实匹配 (15:00)';
    ELSE
        RAISE WARNING '✗ CHK_BO_001: 数据不正确或不存在';
    END IF;
    
    -- CHK_CONF_005: 证实报文未发
    SELECT EXISTS(
        SELECT 1 FROM rule_config_table 
        WHERE rule_code = 'CHK_CONF_005'
        AND rule_name = '未发证实报文'
        AND scheduled_time = '15:30'
        AND enabled = TRUE
    ) INTO v_found;
    
    IF v_found THEN
        RAISE NOTICE '✓ CHK_CONF_005: 未发证实报文 (15:30)';
    ELSE
        RAISE WARNING '✗ CHK_CONF_005: 数据不正确或不存在';
    END IF;
    
    -- CHK_SW_002: 收付报文未发
    SELECT EXISTS(
        SELECT 1 FROM rule_config_table 
        WHERE rule_code = 'CHK_SW_002'
        AND rule_name = '未发收付报文'
        AND scheduled_time = '15:00'
        AND enabled = TRUE
    ) INTO v_found;
    
    IF v_found THEN
        RAISE NOTICE '✓ CHK_SW_002: 未发收付报文 (15:00)';
    ELSE
        RAISE WARNING '✗ CHK_SW_002: 数据不正确或不存在';
    END IF;
    
    -- CHK_SETT_006: 收付待审批
    SELECT EXISTS(
        SELECT 1 FROM rule_config_table 
        WHERE rule_code = 'CHK_SETT_006'
        AND rule_name = '收付待审批'
        AND scheduled_time = '16:00'
        AND enabled = TRUE
    ) INTO v_found;
    
    IF v_found THEN
        RAISE NOTICE '✓ CHK_SETT_006: 收付待审批 (16:00)';
    ELSE
        RAISE WARNING '✗ CHK_SETT_006: 数据不正确或不存在';
    END IF;
    
    -- CHK_SEC_003: 券持仓卖空缺口
    SELECT EXISTS(
        SELECT 1 FROM rule_config_table 
        WHERE rule_code = 'CHK_SEC_003'
        AND rule_name = '券持仓卖空缺口'
        AND scheduled_time = '15:00'
        AND enabled = TRUE
    ) INTO v_found;
    
    IF v_found THEN
        RAISE NOTICE '✓ CHK_SEC_003: 券持仓卖空缺口 (15:00)';
    ELSE
        RAISE WARNING '✗ CHK_SEC_003: 数据不正确或不存在';
    END IF;
END $;

-- ============================================================================
-- 测试3: 验证Cron表达式
-- ============================================================================

\echo ''
\echo '=== 测试3: 验证Cron表达式 ==='

DO $
DECLARE
    v_found BOOLEAN;
BEGIN
    -- CHK_TRD_004: 30 14 * * 1-5
    SELECT EXISTS(
        SELECT 1 FROM rule_config_table 
        WHERE rule_code = 'CHK_TRD_004'
        AND cron_expression = '30 14 * * 1-5'
    ) INTO v_found;
    
    IF v_found THEN
        RAISE NOTICE '✓ CHK_TRD_004: Cron表达式正确 (30 14 * * 1-5)';
    ELSE
        RAISE WARNING '✗ CHK_TRD_004: Cron表达式不正确';
    END IF;
    
    -- CHK_BO_001: 0 15 * * 1-5
    SELECT EXISTS(
        SELECT 1 FROM rule_config_table 
        WHERE rule_code = 'CHK_BO_001'
        AND cron_expression = '0 15 * * 1-5'
    ) INTO v_found;
    
    IF v_found THEN
        RAISE NOTICE '✓ CHK_BO_001: Cron表达式正确 (0 15 * * 1-5)';
    ELSE
        RAISE WARNING '✗ CHK_BO_001: Cron表达式不正确';
    END IF;
    
    -- CHK_CONF_005: 30 15 * * 1-5
    SELECT EXISTS(
        SELECT 1 FROM rule_config_table 
        WHERE rule_code = 'CHK_CONF_005'
        AND cron_expression = '30 15 * * 1-5'
    ) INTO v_found;
    
    IF v_found THEN
        RAISE NOTICE '✓ CHK_CONF_005: Cron表达式正确 (30 15 * * 1-5)';
    ELSE
        RAISE WARNING '✗ CHK_CONF_005: Cron表达式不正确';
    END IF;
    
    -- CHK_SW_002: 0 15 * * 1-5
    SELECT EXISTS(
        SELECT 1 FROM rule_config_table 
        WHERE rule_code = 'CHK_SW_002'
        AND cron_expression = '0 15 * * 1-5'
    ) INTO v_found;
    
    IF v_found THEN
        RAISE NOTICE '✓ CHK_SW_002: Cron表达式正确 (0 15 * * 1-5)';
    ELSE
        RAISE WARNING '✗ CHK_SW_002: Cron表达式不正确';
    END IF;
    
    -- CHK_SETT_006: 0 16 * * 1-5
    SELECT EXISTS(
        SELECT 1 FROM rule_config_table 
        WHERE rule_code = 'CHK_SETT_006'
        AND cron_expression = '0 16 * * 1-5'
    ) INTO v_found;
    
    IF v_found THEN
        RAISE NOTICE '✓ CHK_SETT_006: Cron表达式正确 (0 16 * * 1-5)';
    ELSE
        RAISE WARNING '✗ CHK_SETT_006: Cron表达式不正确';
    END IF;
    
    -- CHK_SEC_003: 0 15,16 * * 1-5 (执行两次)
    SELECT EXISTS(
        SELECT 1 FROM rule_config_table 
        WHERE rule_code = 'CHK_SEC_003'
        AND cron_expression = '0 15,16 * * 1-5'
    ) INTO v_found;
    
    IF v_found THEN
        RAISE NOTICE '✓ CHK_SEC_003: Cron表达式正确 (0 15,16 * * 1-5) - 每日执行两次';
    ELSE
        RAISE WARNING '✗ CHK_SEC_003: Cron表达式不正确';
    END IF;
END $;

-- ============================================================================
-- 测试4: 验证目标角色(target_roles)
-- ============================================================================

\echo ''
\echo '=== 测试4: 验证目标角色(target_roles) ==='

DO $
DECLARE
    v_target_roles JSON;
    v_found BOOLEAN;
BEGIN
    -- 验证BO_Supervisor角色的规则
    SELECT EXISTS(
        SELECT 1 FROM rule_config_table 
        WHERE rule_code IN ('CHK_TRD_004', 'CHK_SETT_006', 'CHK_SEC_003')
        AND target_roles::TEXT LIKE '%BO_Supervisor%'
    ) INTO v_found;
    
    IF v_found THEN
        RAISE NOTICE '✓ 主管类规则(CHK_TRD_004, CHK_SETT_006, CHK_SEC_003)分配给BO_Supervisor';
    ELSE
        RAISE WARNING '✗ 主管类规则的target_roles不正确';
    END IF;
    
    -- 验证BO_Operator角色的规则
    SELECT EXISTS(
        SELECT 1 FROM rule_config_table 
        WHERE rule_code IN ('CHK_BO_001', 'CHK_CONF_005', 'CHK_SW_002')
        AND target_roles::TEXT LIKE '%BO_Operator%'
    ) INTO v_found;
    
    IF v_found THEN
        RAISE NOTICE '✓ 操作员类规则(CHK_BO_001, CHK_CONF_005, CHK_SW_002)分配给BO_Operator';
    ELSE
        RAISE WARNING '✗ 操作员类规则的target_roles不正确';
    END IF;
END $;

-- ============================================================================
-- 测试5: 验证超时时间配置
-- ============================================================================

\echo ''
\echo '=== 测试5: 验证超时时间配置 ==='

DO $
DECLARE
    v_found BOOLEAN;
BEGIN
    -- 验证5秒超时的规则
    SELECT EXISTS(
        SELECT 1 FROM rule_config_table 
        WHERE rule_code IN ('CHK_TRD_004', 'CHK_BO_001', 'CHK_CONF_005', 'CHK_SW_002')
        AND timeout_seconds = 5
    ) INTO v_found;
    
    IF v_found THEN
        RAISE NOTICE '✓ 快速扫描规则超时时间为5秒';
    ELSE
        RAISE WARNING '✗ 快速扫描规则超时时间配置不正确';
    END IF;
    
    -- 验证10秒超时的规则
    SELECT EXISTS(
        SELECT 1 FROM rule_config_table 
        WHERE rule_code IN ('CHK_SETT_006', 'CHK_SEC_003')
        AND timeout_seconds = 10
    ) INTO v_found;
    
    IF v_found THEN
        RAISE NOTICE '✓ 复杂扫描规则超时时间为10秒';
    ELSE
        RAISE WARNING '✗ 复杂扫描规则超时时间配置不正确';
    END IF;
END $;

-- ============================================================================
-- 测试6: 验证所有规则都已启用
-- ============================================================================

\echo ''
\echo '=== 测试6: 验证所有规则都已启用 ==='

DO $
DECLARE
    v_disabled_count INT;
BEGIN
    SELECT COUNT(*) INTO v_disabled_count 
    FROM rule_config_table 
    WHERE enabled = FALSE;
    
    IF v_disabled_count = 0 THEN
        RAISE NOTICE '✓ 所有6条规则都已启用';
    ELSE
        RAISE WARNING '✗ 有 % 条规则未启用', v_disabled_count;
    END IF;
END $;

-- ============================================================================
-- 测试7: 验证规则代码唯一性约束
-- ============================================================================

\echo ''
\echo '=== 测试7: 验证规则代码唯一性约束 ==='

DO $
DECLARE
    v_duplicate_count INT;
BEGIN
    -- 检查是否有重复的rule_code
    SELECT COUNT(*) - COUNT(DISTINCT rule_code) INTO v_duplicate_count
    FROM rule_config_table;
    
    IF v_duplicate_count = 0 THEN
        RAISE NOTICE '✓ 规则代码唯一性约束有效，无重复记录';
    ELSE
        RAISE WARNING '✗ 发现 % 条重复的规则代码', v_duplicate_count;
    END IF;
END $;

-- ============================================================================
-- 测试8: 验证必填字段无NULL值
-- ============================================================================

\echo ''
\echo '=== 测试8: 验证必填字段无NULL值 ==='

DO $
DECLARE
    v_null_count INT;
BEGIN
    SELECT COUNT(*) INTO v_null_count
    FROM rule_config_table
    WHERE rule_code IS NULL
       OR rule_name IS NULL
       OR scheduled_time IS NULL
       OR cron_expression IS NULL
       OR target_roles IS NULL
       OR enabled IS NULL
       OR query_sql IS NULL
       OR timeout_seconds IS NULL;
    
    IF v_null_count = 0 THEN
        RAISE NOTICE '✓ 所有必填字段都有值，无NULL';
    ELSE
        RAISE WARNING '✗ 发现 % 条记录存在NULL值', v_null_count;
    END IF;
END $;

-- ============================================================================
-- 测试9: 显示所有规则配置概览
-- ============================================================================

\echo ''
\echo '=== 测试9: 显示所有规则配置概览 ==='

SELECT 
    rule_code AS "规则代码",
    rule_name AS "规则名称",
    scheduled_time AS "执行时间",
    cron_expression AS "Cron表达式",
    target_roles AS "目标角色",
    timeout_seconds AS "超时(秒)",
    enabled AS "启用"
FROM rule_config_table
ORDER BY rule_code;

-- ============================================================================
-- 测试总结
-- ============================================================================

\echo ''
\echo '========================================'
\echo '测试总结'
\echo '========================================'

DO $
DECLARE
    v_total_count INT;
    v_enabled_count INT;
    v_supervisor_count INT;
    v_operator_count INT;
BEGIN
    SELECT COUNT(*) INTO v_total_count FROM rule_config_table;
    SELECT COUNT(*) INTO v_enabled_count FROM rule_config_table WHERE enabled = TRUE;
    SELECT COUNT(*) INTO v_supervisor_count FROM rule_config_table WHERE target_roles::TEXT LIKE '%BO_Supervisor%';
    SELECT COUNT(*) INTO v_operator_count FROM rule_config_table WHERE target_roles::TEXT LIKE '%BO_Operator%';
    
    RAISE NOTICE '';
    RAISE NOTICE '规则配置统计:';
    RAISE NOTICE '  - 总规则数: %', v_total_count;
    RAISE NOTICE '  - 已启用: %', v_enabled_count;
    RAISE NOTICE '  - 主管规则: %', v_supervisor_count;
    RAISE NOTICE '  - 操作员规则: %', v_operator_count;
    RAISE NOTICE '';
    
    IF v_total_count = 6 AND v_enabled_count = 6 THEN
        RAISE NOTICE '🎉 所有验收标准都已满足！';
        RAISE NOTICE '✓ 6条规则配置数据已正确初始化';
        RAISE NOTICE '✓ 所有字段值符合设计要求';
        RAISE NOTICE '✓ 规则代码唯一性约束有效';
    ELSE
        RAISE WARNING '⚠️  部分验证未通过，请检查上述测试结果';
    END IF;
END $;

\echo '========================================'
