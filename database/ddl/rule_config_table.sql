-- ============================================================================
-- Table: rule_config_table
-- Description: 存储提醒规则的配置信息
-- Created: 2024-01-15
-- ============================================================================

CREATE TABLE IF NOT EXISTS rule_config_table (
    -- 主键
    id BIGSERIAL PRIMARY KEY,
    
    -- 规则信息
    rule_code VARCHAR(50) NOT NULL UNIQUE,
    rule_name VARCHAR(200) NOT NULL,
    
    -- 调度配置
    scheduled_time VARCHAR(10) NOT NULL,
    cron_expression VARCHAR(100) NOT NULL,
    
    -- 目标接收人
    target_roles JSON NOT NULL,
    
    -- 启用状态
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    
    -- 规则描述和查询SQL
    description TEXT NULL,
    query_sql TEXT NOT NULL,
    
    -- 超时配置
    timeout_seconds INT NOT NULL DEFAULT 10,
    
    -- 审计字段
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100) NULL
);

-- ============================================================================
-- 索引设计
-- ============================================================================

-- 规则代码唯一索引
CREATE UNIQUE INDEX IF NOT EXISTS uk_rule_code ON rule_config_table(rule_code);

-- 启用状态索引（用于查询启用的规则）
CREATE INDEX IF NOT EXISTS idx_enabled ON rule_config_table(enabled);

-- ============================================================================
-- 触发器：自动更新 updated_at 字段
-- ============================================================================

CREATE OR REPLACE FUNCTION update_rule_config_table_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_rule_config_table_updated_at
    BEFORE UPDATE ON rule_config_table
    FOR EACH ROW
    EXECUTE FUNCTION update_rule_config_table_updated_at();

-- ============================================================================
-- 初始化数据：插入6条预定义规则配置
-- ============================================================================

INSERT INTO rule_config_table (
    rule_code,
    rule_name,
    scheduled_time,
    cron_expression,
    target_roles,
    enabled,
    description,
    query_sql,
    timeout_seconds
) VALUES
-- CHK_TRD_004: 交易复核提醒
(
    'CHK_TRD_004',
    '当日交易未复核',
    '14:30',
    '30 14 * * 1-5',
    '["BO_Supervisor"]'::JSON,
    TRUE,
    '每日下午14:30自动扫描所有处于"待审批/待复核"状态的交易记录',
    'SELECT COUNT(*) FROM trade_table WHERE approval_status IN (''待审批'', ''待复核'')',
    5
),
-- CHK_BO_001: 未证实匹配提醒
(
    'CHK_BO_001',
    '未证实匹配',
    '15:00',
    '0 15 * * 1-5',
    '["BO_Operator"]'::JSON,
    TRUE,
    '每日下午15:00自动扫描当日所有前台已确认但后台尚未完成证实匹配的交易记录',
    'SELECT COUNT(*) FROM confirmation_table WHERE back_office_status = ''复核通过'' AND matching_status IN (''未匹配'', ''待处理'')',
    5
),
-- CHK_CONF_005: 证实报文未发提醒
(
    'CHK_CONF_005',
    '未发证实报文',
    '15:30',
    '30 15 * * 1-5',
    '["BO_Operator"]'::JSON,
    TRUE,
    '每日下午15:30自动扫描所有已复核通过但证实报文仍处于"待发报"状态的交易记录',
    'SELECT COUNT(*) FROM confirmation_table WHERE message_status = ''待发报'' AND message_type = ''证实报文''',
    5
),
-- CHK_SW_002: 收付报文未发提醒
(
    'CHK_SW_002',
    '未发收付报文',
    '15:00',
    '0 15 * * 1-5',
    '["BO_Operator"]'::JSON,
    TRUE,
    '每个工作日15:00自动扫描所有处于"待发报"状态的资金收付报文',
    'SELECT COUNT(*) FROM payment_table WHERE message_status = ''待发报'' AND message_type IN (''收款'', ''付款'')',
    5
),
-- CHK_SETT_006: 收付报文清算审批提醒
(
    'CHK_SETT_006',
    '收付待审批',
    '16:00',
    '0 16 * * 1-5',
    '["BO_Supervisor"]'::JSON,
    TRUE,
    '每日下午16:00自动扫描所有已进入清算审批流但处于"待审批"状态的资金收付报文',
    'SELECT COUNT(*) FROM settlement_table WHERE approval_status = ''待审批''',
    10
),
-- CHK_SEC_003: 券持仓卖空预警
(
    'CHK_SEC_003',
    '券持仓卖空缺口',
    '15:00',
    '0 15,16 * * 1-5',
    '["BO_Supervisor"]'::JSON,
    TRUE,
    '每日下午15:00和16:00扫描T日和T+1日的债券持仓，检查可用数量是否小于0（卖空）',
    'SELECT COUNT(*) FROM position_table WHERE available_quantity < 0 AND settlement_date IN (''T'', ''T+1'')',
    10
)
ON CONFLICT (rule_code) DO NOTHING;

-- ============================================================================
-- 注释说明
-- ============================================================================

COMMENT ON TABLE rule_config_table IS '规则配置表，存储提醒规则的配置信息';
COMMENT ON COLUMN rule_config_table.id IS '主键，自增';
COMMENT ON COLUMN rule_config_table.rule_code IS '规则代码，如CHK_TRD_004，唯一';
COMMENT ON COLUMN rule_config_table.rule_name IS '规则名称';
COMMENT ON COLUMN rule_config_table.scheduled_time IS '执行时间（HH:MM格式）';
COMMENT ON COLUMN rule_config_table.cron_expression IS 'Cron表达式，用于定时任务调度';
COMMENT ON COLUMN rule_config_table.target_roles IS '接收人角色列表（JSON格式）';
COMMENT ON COLUMN rule_config_table.enabled IS '是否启用该规则';
COMMENT ON COLUMN rule_config_table.description IS '规则描述';
COMMENT ON COLUMN rule_config_table.query_sql IS '扫描SQL语句';
COMMENT ON COLUMN rule_config_table.timeout_seconds IS '查询超时时间（秒）';
COMMENT ON COLUMN rule_config_table.created_at IS '创建时间';
COMMENT ON COLUMN rule_config_table.updated_at IS '更新时间';
COMMENT ON COLUMN rule_config_table.updated_by IS '更新人';

