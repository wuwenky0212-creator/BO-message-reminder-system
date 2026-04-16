# 数据库迁移脚本

本目录包含消息提醒功能的数据库迁移脚本。

## 迁移脚本列表

### 001_create_message_table

**描述:** 创建消息提醒表 (message_table)

**包含内容:**
- 创建 `message_table` 表，包含所有字段（id, rule_code, title, count, last_updated, status, priority, target_roles, metadata, created_at, updated_at）
- 创建索引：
  - `idx_rule_code` - 规则代码索引
  - `idx_last_updated` - 最后更新时间索引
  - `idx_status` - 状态索引
- 创建触发器 `trigger_update_message_table_updated_at` - 自动更新 updated_at 字段
- 添加表和字段注释

**特性:**
- ✅ 幂等性：可以重复执行而不会出错
- ✅ 支持升级和降级操作
- ✅ 包含验证脚本，确认迁移成功

### 002_create_rule_config_table

**描述:** 创建规则配置表 (rule_config_table)

**包含内容:**
- 创建 `rule_config_table` 表，包含所有字段（id, rule_code, rule_name, scheduled_time, cron_expression, target_roles, enabled, description, query_sql, timeout_seconds, created_at, updated_at, updated_by）
- 创建索引：
  - `uk_rule_code` - 规则代码唯一索引（任务1.2.2）
  - `idx_enabled` - 启用状态索引
- 创建触发器 `trigger_update_rule_config_table_updated_at` - 自动更新 updated_at 字段
- 初始化6条预定义规则配置数据（CHK_TRD_004, CHK_BO_001, CHK_CONF_005, CHK_SW_002, CHK_SETT_006, CHK_SEC_003）
- 添加表和字段注释

**特性:**
- ✅ 幂等性：可以重复执行而不会出错
- ✅ 支持升级和降级操作
- ✅ 包含验证脚本，确认迁移成功
- ✅ 唯一索引确保 rule_code 不重复

## 使用方法

### 执行升级（创建表）

**消息表:**
```bash
psql -U <username> -d <database> -f 001_create_message_table.sql
```

**规则配置表:**
```bash
psql -U <username> -d <database> -f 002_create_rule_config_table.sql
```

**任务执行日志表:**
```bash
psql -U <username> -d <database> -f 003_create_task_execution_log.sql
```

### 执行降级（删除表）

**消息表:**
```bash
psql -U <username> -d <database> -f 001_create_message_table_downgrade.sql
```

**规则配置表:**
```bash
psql -U <username> -d <database> -f 002_create_rule_config_table_downgrade.sql
```

**任务执行日志表:**
```bash
psql -U <username> -d <database> -f 003_create_task_execution_log_downgrade.sql
```

### 验证迁移

升级和降级脚本都包含验证逻辑，执行后会输出验证结果：

**升级验证输出示例:**

**消息表 (001):**
```
NOTICE:  ✓ 表 message_table 创建成功
NOTICE:  ✓ 索引 idx_rule_code 创建成功
NOTICE:  ✓ 索引 idx_last_updated 创建成功
NOTICE:  ✓ 索引 idx_status 创建成功
NOTICE:  ✓ 触发器 trigger_update_message_table_updated_at 创建成功
```

**规则配置表 (002):**
```
NOTICE:  ✓ 表 rule_config_table 创建成功
NOTICE:  ✓ 唯一索引 uk_rule_code 创建成功
NOTICE:  ✓ 索引 idx_enabled 创建成功
NOTICE:  ✓ 触发器 trigger_update_rule_config_table_updated_at 创建成功
NOTICE:  ✓ 初始化数据插入成功，共 6 条记录
```

**降级验证输出示例:**

**消息表 (001):**
```
NOTICE:  ✓ 表 message_table 已成功删除
NOTICE:  ✓ 触发器函数 update_message_table_updated_at 已成功删除
```

**规则配置表 (002):**
```
NOTICE:  ✓ 表 rule_config_table 已成功删除
NOTICE:  ✓ 触发器函数 update_rule_config_table_updated_at 已成功删除
```

## 幂等性说明

所有迁移脚本都设计为幂等的，这意味着：

1. **升级脚本** 可以多次执行而不会出错：
   - 使用 `CREATE TABLE IF NOT EXISTS`
   - 使用 `CREATE INDEX IF NOT EXISTS`
   - 使用 `CREATE OR REPLACE FUNCTION`
   - 使用 `DROP TRIGGER IF EXISTS` 后再创建

2. **降级脚本** 可以多次执行而不会出错：
   - 使用 `DROP ... IF EXISTS`

## 注意事项

1. **执行顺序:** 按照迁移脚本的编号顺序执行（001, 002, 003...）
2. **备份数据:** 在生产环境执行迁移前，务必备份数据库
3. **测试环境:** 先在测试环境验证迁移脚本，确认无误后再在生产环境执行
4. **权限要求:** 执行迁移脚本需要数据库的 CREATE、DROP、ALTER 权限
5. **回滚计划:** 执行升级前，确保了解如何执行降级回滚

## 表结构说明

### message_table

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGSERIAL | PK | 主键，自增 |
| rule_code | VARCHAR(50) | NOT NULL | 规则代码 |
| title | VARCHAR(200) | NOT NULL | 提醒标题 |
| count | INT | NOT NULL | 待处理数量 |
| last_updated | TIMESTAMP | NOT NULL | 最后更新时间 |
| status | VARCHAR(20) | NOT NULL | 扫描状态(success/timeout/error) |
| priority | VARCHAR(20) | NOT NULL | 优先级(normal/high/critical) |
| target_roles | JSON | NOT NULL | 目标接收人角色列表 |
| metadata | JSON | NULL | 扩展元数据 |
| created_at | TIMESTAMP | NOT NULL | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL | 更新时间 |

**索引:**
- PRIMARY KEY (id)
- INDEX idx_rule_code (rule_code)
- INDEX idx_last_updated (last_updated)
- INDEX idx_status (status)

**触发器:**
- trigger_update_message_table_updated_at: 在 UPDATE 操作前自动更新 updated_at 字段

### rule_config_table

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGSERIAL | PK | 主键，自增 |
| rule_code | VARCHAR(50) | NOT NULL, UNIQUE | 规则代码 |
| rule_name | VARCHAR(200) | NOT NULL | 规则名称 |
| scheduled_time | VARCHAR(10) | NOT NULL | 执行时间(HH:MM) |
| cron_expression | VARCHAR(100) | NOT NULL | Cron表达式 |
| target_roles | JSON | NOT NULL | 接收人角色列表 |
| enabled | BOOLEAN | NOT NULL | 是否启用 |
| description | TEXT | NULL | 规则描述 |
| query_sql | TEXT | NOT NULL | 扫描SQL语句 |
| timeout_seconds | INT | NOT NULL | 查询超时时间(秒) |
| created_at | TIMESTAMP | NOT NULL | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL | 更新时间 |
| updated_by | VARCHAR(100) | NULL | 更新人 |

**索引:**
- PRIMARY KEY (id)
- UNIQUE INDEX uk_rule_code (rule_code)
- INDEX idx_enabled (enabled)

**触发器:**
- trigger_update_rule_config_table_updated_at: 在 UPDATE 操作前自动更新 updated_at 字段

**初始化数据:**
- CHK_TRD_004: 当日交易未复核
- CHK_BO_001: 未证实匹配
- CHK_CONF_005: 未发证实报文
- CHK_SW_002: 未发收付报文
- CHK_SETT_006: 收付待审批
- CHK_SEC_003: 券持仓卖空缺口

### 003_create_task_execution_log

**描述:** 创建任务执行日志表 (task_execution_log)

**包含内容:**
- 创建 `task_execution_log` 表，包含所有字段（id, task_id, rule_code, rule_name, scheduled_time, actual_start_time, actual_end_time, execution_duration, status, record_count, error_message, created_at）
- 创建索引：
  - `uk_task_id` - 任务ID唯一索引
  - `idx_rule_code` - 规则代码索引
  - `idx_scheduled_time` - 计划执行时间索引
  - `idx_status` - 状态索引
- 添加表和字段注释

**特性:**
- ✅ 幂等性：可以重复执行而不会出错
- ✅ 支持升级和降级操作
- ✅ 包含验证脚本，确认迁移成功
- ✅ 唯一索引确保 task_id 不重复
- ✅ 完整的自动化验证脚本（12个验证模块）

**验证文档:**
- [详细验证文档](../docs/task_execution_log_validation.md)
- [快速执行指南](../docs/task_execution_log_quick_guide.md)
- [执行总结](../docs/task_1.3.3_execution_summary.md)

## 故障排查

### 问题：迁移脚本执行失败

**可能原因:**
1. 数据库连接失败
2. 权限不足
3. 表已存在但结构不匹配

**解决方法:**
1. 检查数据库连接参数
2. 确认用户具有足够的权限
3. 如果表已存在，先执行降级脚本删除表，再执行升级脚本

### 问题：验证脚本报错

**可能原因:**
1. 迁移未完全执行
2. 数据库版本不兼容

**解决方法:**
1. 检查迁移脚本的输出日志
2. 确认 PostgreSQL 版本 >= 14

## 相关文档

- [设计文档](../../.kiro/specs/message-reminder/design.md) - 查看完整的数据库设计
- [需求文档](../../.kiro/specs/message-reminder/requirements.md) - 了解业务需求
- [任务列表](../../.kiro/specs/message-reminder/tasks.md) - 查看开发任务
