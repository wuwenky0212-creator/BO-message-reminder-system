# 快速开始指南 - 消息提醒功能数据库

本指南帮助开发者快速设置消息提醒功能的数据库。

## 前置条件

- PostgreSQL 14+ 已安装
- 具有数据库创建和管理权限的用户账号
- psql 命令行工具可用

## 快速部署

### 1. 创建数据库（如果还没有）

```bash
createdb -U postgres message_reminder_db
```

### 2. 执行迁移脚本

按顺序执行以下迁移脚本：

```bash
# 进入迁移目录
cd database/migrations

# 创建消息表
psql -U postgres -d message_reminder_db -f 001_create_message_table.sql

# 创建规则配置表（包含唯一索引 uk_rule_code）
psql -U postgres -d message_reminder_db -f 002_create_rule_config_table.sql
```

### 3. 验证部署

```bash
# 运行测试脚本
cd ../tests
psql -U postgres -d message_reminder_db -f test_rule_config_unique_index.sql
```

## 预期结果

### 迁移成功输出

**001_create_message_table.sql:**
```
NOTICE:  ✓ 表 message_table 创建成功
NOTICE:  ✓ 索引 idx_rule_code 创建成功
NOTICE:  ✓ 索引 idx_last_updated 创建成功
NOTICE:  ✓ 索引 idx_status 创建成功
NOTICE:  ✓ 触发器 trigger_update_message_table_updated_at 创建成功
NOTICE:  ========================================
NOTICE:  迁移 001_create_message_table 执行成功
NOTICE:  ========================================
```

**002_create_rule_config_table.sql:**
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

### 测试成功输出

```
========================================
开始测试 rule_config_table 唯一索引
========================================
...
✓ 所有测试通过！
唯一索引 uk_rule_code 工作正常
========================================
```

## 验证数据

### 查看已创建的表

```sql
-- 连接数据库
psql -U postgres -d message_reminder_db

-- 查看所有表
\dt

-- 预期输出:
--              List of relations
--  Schema |       Name        | Type  |  Owner   
-- --------+-------------------+-------+----------
--  public | message_table     | table | postgres
--  public | rule_config_table | table | postgres
```

### 查看索引

```sql
-- 查看 rule_config_table 的索引
\d rule_config_table

-- 预期输出包含:
-- Indexes:
--     "rule_config_table_pkey" PRIMARY KEY, btree (id)
--     "uk_rule_code" UNIQUE, btree (rule_code)
--     "idx_enabled" btree (enabled)
```

### 查看初始化数据

```sql
-- 查看规则配置数据
SELECT rule_code, rule_name, scheduled_time, enabled 
FROM rule_config_table 
ORDER BY rule_code;

-- 预期输出:
--   rule_code   |      rule_name      | scheduled_time | enabled 
-- --------------+---------------------+----------------+---------
--  CHK_BO_001   | 未证实匹配          | 15:00          | t
--  CHK_CONF_005 | 未发证实报文        | 15:30          | t
--  CHK_SEC_003  | 券持仓卖空缺口      | 15:00          | t
--  CHK_SETT_006 | 收付待审批          | 16:00          | t
--  CHK_SW_002   | 未发收付报文        | 15:00          | t
--  CHK_TRD_004  | 当日交易未复核      | 14:30          | t
```

## 常见问题

### Q1: 迁移脚本执行失败，提示表已存在

**解决方法:**

```bash
# 先执行降级脚本删除表
psql -U postgres -d message_reminder_db -f 002_create_rule_config_table_downgrade.sql

# 再重新执行升级脚本
psql -U postgres -d message_reminder_db -f 002_create_rule_config_table.sql
```

### Q2: 如何重置数据库到初始状态

**解决方法:**

```bash
# 按相反顺序执行降级脚本
psql -U postgres -d message_reminder_db -f 002_create_rule_config_table_downgrade.sql
psql -U postgres -d message_reminder_db -f 001_create_message_table_downgrade.sql

# 然后重新执行升级脚本
psql -U postgres -d message_reminder_db -f 001_create_message_table.sql
psql -U postgres -d message_reminder_db -f 002_create_rule_config_table.sql
```

### Q3: 测试脚本报错

**可能原因:**
1. 表还没有创建
2. 数据库连接失败
3. 权限不足

**解决方法:**
1. 确保先执行迁移脚本创建表
2. 检查数据库连接参数
3. 确认用户具有足够的权限

## 下一步

1. **开发后端API:** 参考 [设计文档](../../.kiro/specs/message-reminder/design.md) 第3节
2. **实现定时任务:** 参考 [设计文档](../../.kiro/specs/message-reminder/design.md) 第5节
3. **开发前端组件:** 参考 [设计文档](../../.kiro/specs/message-reminder/design.md) 第4节

## 相关文档

- [迁移脚本README](../migrations/README.md) - 详细的迁移脚本说明
- [任务1.2.2实现文档](task_1.2.2_unique_index_implementation.md) - 唯一索引实现细节
- [设计文档](../../.kiro/specs/message-reminder/design.md) - 完整的系统设计
- [需求文档](../../.kiro/specs/message-reminder/requirements.md) - 业务需求说明

## 技术支持

如有问题，请参考：
1. [故障排查指南](../migrations/README.md#故障排查)
2. [PostgreSQL官方文档](https://www.postgresql.org/docs/)
3. 项目Issue跟踪系统
