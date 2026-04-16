# 任务 1.2.4 验证指南

## 概述

本文档提供任务 1.2.4 的完整验证指南，用于在测试环境中执行规则配置表迁移脚本并验证结果。

## 验收标准

根据任务定义，需要验证以下三个标准：

1. ✅ **表结构符合设计文档定义**
2. ✅ **6条规则配置数据插入成功**
3. ✅ **rule_code唯一约束生效**

## 前置条件

- PostgreSQL 数据库已安装并运行
- 已创建测试数据库（如 `message_reminder_db`）
- 具有数据库访问权限
- 已完成任务 1.2.1、1.2.2、1.2.3（迁移脚本已创建）

## 执行步骤

### 步骤 1: 执行迁移脚本

在测试环境中执行规则配置表迁移脚本：

```bash
# 方式1: 使用 psql 命令行工具
psql -U postgres -d message_reminder_db -f database/migrations/002_create_rule_config_table.sql

# 方式2: 使用 psql 交互模式
psql -U postgres -d message_reminder_db
\i database/migrations/002_create_rule_config_table.sql
```

**预期输出：**
```
NOTICE:  ✓ 表 rule_config_table 创建成功
NOTICE:  ✓ 唯一索引 uk_rule_code 创建成功
NOTICE:  ✓ 索引 idx_enabled 创建成功
NOTICE:  ✓ 触发器 trigger_update_rule_config_table_updated_at 创建成功
NOTICE:  ✓ 初始化数据插入成功，共 6 条记录
NOTICE:  ========================================
NOTICE:  迁移 002_create_rule_config_table 执行成功
NOTICE:  ========================================
```

### 步骤 2: 验证表结构

执行以下 SQL 查询验证表结构：

```sql
-- 查看表结构
\d rule_config_table

-- 查看表的所有索引
\di rule_config_table*

-- 查看表的触发器
SELECT tgname, tgtype, tgenabled 
FROM pg_trigger 
WHERE tgrelid = 'rule_config_table'::regclass;
```

**预期结果：**

表应包含以下字段：
- `id` (BIGSERIAL, PRIMARY KEY)
- `rule_code` (VARCHAR(50), NOT NULL)
- `rule_name` (VARCHAR(200), NOT NULL)
- `scheduled_time` (VARCHAR(10), NOT NULL)
- `cron_expression` (VARCHAR(100), NOT NULL)
- `target_roles` (JSON, NOT NULL)
- `enabled` (BOOLEAN, NOT NULL, DEFAULT TRUE)
- `description` (TEXT, NULL)
- `query_sql` (TEXT, NOT NULL)
- `timeout_seconds` (INT, NOT NULL, DEFAULT 10)
- `created_at` (TIMESTAMP, NOT NULL, DEFAULT CURRENT_TIMESTAMP)
- `updated_at` (TIMESTAMP, NOT NULL, DEFAULT CURRENT_TIMESTAMP)
- `updated_by` (VARCHAR(100), NULL)

索引应包括：
- `uk_rule_code` (UNIQUE INDEX on rule_code)
- `idx_enabled` (INDEX on enabled)

### 步骤 3: 验证初始化数据

执行测试脚本验证6条规则配置数据：

```bash
psql -U postgres -d message_reminder_db -f database/tests/test_rule_config_initialization.sql
```

**预期输出：**
```
=== 测试1: 验证记录数量 ===
NOTICE:  ✓ 记录数量正确: 共 6 条规则配置

=== 测试2: 验证每条规则的存在性和基本信息 ===
NOTICE:  ✓ CHK_TRD_004: 当日交易未复核 (14:30)
NOTICE:  ✓ CHK_BO_001: 未证实匹配 (15:00)
NOTICE:  ✓ CHK_CONF_005: 未发证实报文 (15:30)
NOTICE:  ✓ CHK_SW_002: 未发收付报文 (15:00)
NOTICE:  ✓ CHK_SETT_006: 收付待审批 (16:00)
NOTICE:  ✓ CHK_SEC_003: 券持仓卖空缺口 (15:00)

=== 测试3: 验证Cron表达式 ===
NOTICE:  ✓ CHK_TRD_004: Cron表达式正确 (30 14 * * 1-5)
NOTICE:  ✓ CHK_BO_001: Cron表达式正确 (0 15 * * 1-5)
NOTICE:  ✓ CHK_CONF_005: Cron表达式正确 (30 15 * * 1-5)
NOTICE:  ✓ CHK_SW_002: Cron表达式正确 (0 15 * * 1-5)
NOTICE:  ✓ CHK_SETT_006: Cron表达式正确 (0 16 * * 1-5)
NOTICE:  ✓ CHK_SEC_003: Cron表达式正确 (0 15,16 * * 1-5) - 每日执行两次

🎉 所有验收标准都已满足！
```

### 步骤 4: 验证唯一约束

执行唯一索引测试脚本：

```bash
psql -U postgres -d message_reminder_db -f database/tests/test_rule_config_unique_index.sql
```

**预期输出：**
```
========================================
开始测试 rule_config_table 唯一索引
========================================

测试1: 验证唯一索引 uk_rule_code 是否存在
NOTICE:  ✓ 测试1通过: 唯一索引 uk_rule_code 存在

测试2: 验证索引 uk_rule_code 是否为 UNIQUE 类型
NOTICE:  ✓ 测试2通过: uk_rule_code 是 UNIQUE 索引

测试3: 验证唯一约束 - 尝试插入重复的 rule_code
NOTICE:  ✓ 测试3通过: 正确阻止了重复的 rule_code 插入

测试4: 验证可以插入新的唯一 rule_code
NOTICE:  ✓ 测试4通过: 成功插入新的唯一 rule_code

测试5: 验证更新操作不违反唯一约束
NOTICE:  ✓ 测试5通过: 正确阻止了更新为重复的 rule_code

测试6: 验证初始化数据的 rule_code 都是唯一的
NOTICE:  ✓ 测试6通过: 所有 rule_code 都是唯一的 (总数: 6, 唯一数: 6)

========================================
✓ 所有测试通过！
唯一索引 uk_rule_code 工作正常
========================================
```

### 步骤 5: 手动验证数据完整性

执行以下查询手动检查数据：

```sql
-- 查看所有规则配置
SELECT 
    rule_code,
    rule_name,
    scheduled_time,
    cron_expression,
    target_roles,
    enabled,
    timeout_seconds
FROM rule_config_table
ORDER BY rule_code;

-- 验证记录数量
SELECT COUNT(*) as total_count FROM rule_config_table;

-- 验证所有规则都已启用
SELECT COUNT(*) as enabled_count 
FROM rule_config_table 
WHERE enabled = TRUE;

-- 验证唯一性
SELECT 
    COUNT(*) as total,
    COUNT(DISTINCT rule_code) as unique_codes
FROM rule_config_table;
```

**预期结果：**

| rule_code | rule_name | scheduled_time | cron_expression | target_roles | enabled | timeout_seconds |
|-----------|-----------|----------------|-----------------|--------------|---------|-----------------|
| CHK_BO_001 | 未证实匹配 | 15:00 | 0 15 * * 1-5 | ["BO_Operator"] | true | 5 |
| CHK_CONF_005 | 未发证实报文 | 15:30 | 30 15 * * 1-5 | ["BO_Operator"] | true | 5 |
| CHK_SEC_003 | 券持仓卖空缺口 | 15:00 | 0 15,16 * * 1-5 | ["BO_Supervisor"] | true | 10 |
| CHK_SETT_006 | 收付待审批 | 16:00 | 0 16 * * 1-5 | ["BO_Supervisor"] | true | 10 |
| CHK_SW_002 | 未发收付报文 | 15:00 | 0 15 * * 1-5 | ["BO_Operator"] | true | 5 |
| CHK_TRD_004 | 当日交易未复核 | 14:30 | 30 14 * * 1-5 | ["BO_Supervisor"] | true | 5 |

- total_count: 6
- enabled_count: 6
- total: 6, unique_codes: 6

## 验证清单

使用以下清单确认所有验收标准已满足：

### ✅ 验收标准 1: 表结构符合设计文档定义

- [ ] 表 `rule_config_table` 已创建
- [ ] 所有13个字段都存在且类型正确
- [ ] 主键 `id` 为 BIGSERIAL 类型
- [ ] 必填字段都设置了 NOT NULL 约束
- [ ] 默认值字段（enabled, timeout_seconds）设置正确
- [ ] 时间戳字段（created_at, updated_at）有默认值
- [ ] 触发器 `trigger_update_rule_config_table_updated_at` 已创建

### ✅ 验收标准 2: 6条规则配置数据插入成功

- [ ] CHK_TRD_004 - 当日交易未复核（14:30）
- [ ] CHK_BO_001 - 未证实匹配（15:00）
- [ ] CHK_CONF_005 - 未发证实报文（15:30）
- [ ] CHK_SW_002 - 未发收付报文（15:00）
- [ ] CHK_SETT_006 - 收付待审批（16:00）
- [ ] CHK_SEC_003 - 券持仓卖空缺口（15:00 和 16:00）
- [ ] 所有规则的 Cron 表达式正确
- [ ] 所有规则的 target_roles 正确分配
- [ ] 所有规则的 timeout_seconds 正确配置
- [ ] 所有规则都已启用（enabled = TRUE）

### ✅ 验收标准 3: rule_code唯一约束生效

- [ ] 唯一索引 `uk_rule_code` 已创建
- [ ] 索引类型为 UNIQUE
- [ ] 尝试插入重复 rule_code 时抛出异常
- [ ] 尝试更新为重复 rule_code 时抛出异常
- [ ] 现有6条记录的 rule_code 都是唯一的

## 故障排查

### 问题 1: 迁移脚本执行失败

**可能原因：**
- 数据库连接失败
- 权限不足
- 表已存在

**解决方案：**
```sql
-- 检查表是否已存在
SELECT tablename FROM pg_tables WHERE tablename = 'rule_config_table';

-- 如果需要重新创建，先执行降级脚本
\i database/migrations/002_create_rule_config_table_downgrade.sql

-- 然后重新执行迁移脚本
\i database/migrations/002_create_rule_config_table.sql
```

### 问题 2: 初始化数据插入失败

**可能原因：**
- rule_code 重复（如果多次执行）
- JSON 格式错误

**解决方案：**
```sql
-- 检查现有记录
SELECT rule_code FROM rule_config_table;

-- 删除重复记录
DELETE FROM rule_config_table WHERE rule_code = 'CHK_TRD_004';

-- 重新插入（迁移脚本使用 ON CONFLICT DO NOTHING，所以可以安全重新执行）
```

### 问题 3: 唯一索引未生效

**可能原因：**
- 索引创建失败
- 索引类型不正确

**解决方案：**
```sql
-- 检查索引
\di rule_config_table*

-- 重新创建唯一索引
DROP INDEX IF EXISTS uk_rule_code;
CREATE UNIQUE INDEX uk_rule_code ON rule_config_table(rule_code);
```

## 回滚操作

如果需要回滚迁移，执行降级脚本：

```bash
psql -U postgres -d message_reminder_db -f database/migrations/002_create_rule_config_table_downgrade.sql
```

## 验证完成标志

当以下所有条件都满足时，任务 1.2.4 验证完成：

1. ✅ 迁移脚本执行成功，无错误
2. ✅ 表结构验证通过（\d rule_config_table 输出正确）
3. ✅ 初始化数据测试通过（test_rule_config_initialization.sql 全部通过）
4. ✅ 唯一索引测试通过（test_rule_config_unique_index.sql 全部通过）
5. ✅ 手动查询验证数据完整性
6. ✅ 验证清单所有项目都已勾选

## 下一步

任务 1.2.4 完成后，可以继续执行：
- 任务 1.3: 创建任务执行日志表 (task_execution_log)
- 任务 1.4: 创建审计日志表 (audit_log)

## 附录：快速验证脚本

创建一个快速验证脚本，一次性执行所有验证：

```bash
#!/bin/bash
# 文件: database/tests/quick_validate_task_1.2.4.sh

echo "=========================================="
echo "任务 1.2.4 快速验证"
echo "=========================================="

# 执行初始化数据测试
echo ""
echo "1. 验证初始化数据..."
psql -U postgres -d message_reminder_db -f database/tests/test_rule_config_initialization.sql

# 执行唯一索引测试
echo ""
echo "2. 验证唯一索引..."
psql -U postgres -d message_reminder_db -f database/tests/test_rule_config_unique_index.sql

echo ""
echo "=========================================="
echo "验证完成！"
echo "=========================================="
```

使用方法：
```bash
chmod +x database/tests/quick_validate_task_1.2.4.sh
./database/tests/quick_validate_task_1.2.4.sh
```
