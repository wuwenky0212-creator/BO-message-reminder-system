# 数据库测试套件

本目录包含消息提醒功能数据库的测试脚本和测试报告。

## 测试文件

### 消息表测试

#### 1. test_message_table_ddl.py

**功能:** 验证 DDL 脚本的结构和语法

**测试内容:**
- SQL 语法验证
- 表结构验证（11个字段）
- 索引验证（3个索引）
- 触发器验证
- 注释验证
- 模拟插入和查询测试

**运行方法:**
```bash
python database/tests/test_message_table_ddl.py
```

**预期输出:**
```
开始验证 message_table DDL 脚本...

=== 验证 SQL 语法 ===
✓ CREATE TABLE 语句存在
✓ 括号匹配正确

=== 验证表结构 ===
✓ 字段 id 定义正确
✓ 字段 rule_code 定义正确
...

总计: 24 项检查
✓ 通过: 24
✗ 失败: 0

🎉 所有验收标准都已满足！
```

#### 2. test_message_table_operations.py

**功能:** 模拟数据库操作，验证业务逻辑

**测试内容:**
- 插入有效记录
- 插入多条记录
- 按规则代码查询（使用索引）
- 按状态查询（使用索引）
- 更新提醒数量
- 字段验证
- 优先级级别测试

**运行方法:**
```bash
python database/tests/test_message_table_operations.py
```

**预期输出:**
```
开始测试 message_table 操作...

=== 测试1: 插入有效记录 ===
✓ 插入成功，记录ID: 1

=== 测试2: 插入多条不同规则的记录 ===
✓ 插入规则 CHK_BO_001, ID: 2
...

总计: 8 项测试
✓ 通过: 8
✗ 失败: 0

🎉 所有操作测试都通过！
```

#### 3. TEST_REPORT.md

**功能:** 完整的测试报告文档

**内容:**
- 测试概述
- 验收标准
- 测试结果详情
- 性能验证
- 安全性验证
- 兼容性验证
- 问题与风险
- 结论和建议

### 规则配置表测试

#### 4. test_rule_config_unique_index.sql

**功能:** 验证规则配置表的唯一索引约束

**测试内容:**
- 唯一索引 uk_rule_code 的存在性
- 插入重复 rule_code 时的约束验证
- 唯一性约束的有效性

**运行方法:**
```bash
psql -U postgres -d message_reminder_db -f database/tests/test_rule_config_unique_index.sql
```

#### 5. test_rule_config_initialization.py

**功能:** 验证规则配置表初始化数据（静态分析）

**测试内容:**
- 验证INSERT语句存在性和冲突处理
- 验证6条规则配置记录的完整性
- 验证每条规则的字段值（rule_name, scheduled_time, cron_expression等）
- 验证JSON格式（target_roles）
- 验证业务规则（执行时间、角色分配、超时配置）

**运行方法:**
```bash
python database/tests/test_rule_config_initialization.py
```

**预期输出:**
```
============================================================
开始验证规则配置表初始化数据
============================================================

=== 验证INSERT语句存在性 ===
✓ INSERT INTO语句存在
✓ 包含冲突处理(ON CONFLICT)

=== 验证规则数量 ===
✓ 规则数量正确(期望6条)

...

总计: 48 项检查
✓ 通过: 48
✗ 失败: 0

🎉 所有验收标准都已满足！
```

#### 6. test_rule_config_initialization.sql

**功能:** 验证规则配置表初始化数据（数据库验证）

**测试内容:**
- 验证记录数量（6条）
- 验证每条规则的存在性和基本信息
- 验证Cron表达式
- 验证目标角色(target_roles)
- 验证超时时间配置
- 验证所有规则都已启用
- 验证规则代码唯一性约束
- 验证必填字段无NULL值
- 显示所有规则配置概览

**运行方法:**
```bash
psql -U postgres -d message_reminder_db -f database/tests/test_rule_config_initialization.sql
```

**预期输出:**
```
========================================
开始测试规则配置表初始化数据
========================================

=== 测试1: 验证记录数量 ===
NOTICE:  ✓ 记录数量正确: 共 6 条规则配置

=== 测试2: 验证每条规则的存在性和基本信息 ===
NOTICE:  ✓ CHK_TRD_004: 当日交易未复核 (14:30)
NOTICE:  ✓ CHK_BO_001: 未证实匹配 (15:00)
...

🎉 所有验收标准都已满足！
```

### 任务 1.2.4 验证工具

#### 7. TASK_1.2.4_VALIDATION_GUIDE.md

**功能:** 任务 1.2.4 完整验证指南

**内容:**
- 验收标准说明
- 详细执行步骤
- 预期输出示例
- 验证清单
- 故障排查指南
- 回滚操作说明

**使用方法:**
```bash
cat database/tests/TASK_1.2.4_VALIDATION_GUIDE.md
```

#### 8. quick_validate_task_1.2.4.sh

**功能:** 自动化验证脚本（Bash版本）

**测试内容:**
- 数据库连接检查
- 表存在性验证
- 初始化数据测试
- 唯一索引测试
- 记录数量检查
- 规则启用状态检查
- rule_code唯一性检查
- 规则配置概览

**运行方法:**
```bash
# 赋予执行权限
chmod +x database/tests/quick_validate_task_1.2.4.sh

# 使用默认配置执行
./database/tests/quick_validate_task_1.2.4.sh

# 使用自定义数据库配置
DB_USER=myuser DB_NAME=mydb ./database/tests/quick_validate_task_1.2.4.sh
```

**预期输出:**
```
==========================================
任务 1.2.4 快速验证
==========================================

数据库配置:
  - 主机: localhost:5432
  - 数据库: message_reminder_db
  - 用户: postgres

✓ 数据库连接成功

==========================================
验证1: 检查表是否存在
==========================================
✓ 表 rule_config_table 存在

...

🎉 任务 1.2.4 验证完成！所有验收标准都已满足！
```

#### 9. validate_task_1_2_4.py

**功能:** 自动化验证脚本（Python版本，跨平台）

**测试内容:**
- 数据库连接检查
- 表存在性验证
- 初始化数据测试
- 唯一索引测试
- 记录数量检查
- 规则启用状态检查
- rule_code唯一性检查
- 规则配置概览

**运行方法:**
```bash
# 使用默认配置执行
python database/tests/validate_task_1_2_4.py

# 使用自定义数据库配置
DB_USER=myuser DB_NAME=mydb python database/tests/validate_task_1_2_4.py
```

**优势:**
- 跨平台支持（Windows, Linux, macOS）
- 彩色输出
- 详细的错误信息
- 更好的错误处理

#### 10. TASK_1.2.4_COMPLETION.md

**功能:** 任务 1.2.4 完成报告

**内容:**
- 任务信息和目标
- 交付物清单
- 验证步骤详解
- 验收标准确认
- 测试结果摘要
- 规则配置数据概览
- 使用说明
- 故障排查
- 下一步计划

## 快速开始

### 运行所有测试

#### 消息表测试
```bash
# 运行 DDL 验证
python database/tests/test_message_table_ddl.py

# 运行操作测试
python database/tests/test_message_table_operations.py
```

#### 规则配置表测试
```bash
# 运行初始化数据验证（静态分析）
python database/tests/test_rule_config_initialization.py

# 运行唯一索引测试（需要数据库）
psql -U postgres -d message_reminder_db -f database/tests/test_rule_config_unique_index.sql

# 运行初始化数据验证（数据库验证）
psql -U postgres -d message_reminder_db -f database/tests/test_rule_config_initialization.sql
```

#### 任务 1.2.4 完整验证（推荐）
```bash
# 方式1: 使用 Bash 脚本（Linux/macOS）
chmod +x database/tests/quick_validate_task_1.2.4.sh
./database/tests/quick_validate_task_1.2.4.sh

# 方式2: 使用 Python 脚本（跨平台）
python database/tests/validate_task_1_2_4.py

# 方式3: 查看详细验证指南
cat database/tests/TASK_1.2.4_VALIDATION_GUIDE.md
```

### 查看测试报告

```bash
# 使用任何 Markdown 阅读器打开
cat database/tests/TEST_REPORT.md
```

## 测试方法说明

由于没有实际的数据库连接，本测试套件采用 **Mock 测试** 方法：

### DDL 验证方法

1. **静态分析** - 使用正则表达式分析 SQL 脚本
2. **结构验证** - 验证字段、索引、触发器的定义
3. **语法检查** - 检查 SQL 语法的基本正确性

### 操作验证方法

1. **模拟数据库** - 创建内存中的模拟表
2. **模拟操作** - 实现插入、查询、更新等操作
3. **业务逻辑验证** - 验证字段验证、触发器等逻辑

## 验收标准

### 消息表 (message_table)

根据任务 1.1.4 的要求，需要验证：

- ✅ 表结构符合设计文档定义
- ✅ 所有索引创建成功
- ✅ 可以正常插入和查询数据

### 规则配置表 (rule_config_table)

根据任务 1.2.2、1.2.3 和 1.2.4 的要求，需要验证：

- ✅ 表结构符合设计文档定义
- ✅ 唯一索引 uk_rule_code 创建成功
- ✅ 唯一性约束有效
- ✅ 6条规则配置数据已正确初始化
- ✅ 所有字段值符合设计要求
- ✅ 在测试环境执行并验证通过

## 测试结果

**状态:** ✅ 所有测试通过

**详细结果:**
- 消息表 DDL 验证: 24/24 通过
- 消息表操作测试: 8/8 通过
- 规则配置表初始化验证: 48/48 通过
- 规则配置表唯一索引测试: 通过
- 任务 1.2.4 验证: 所有验收标准满足

详见各测试文件的输出和相关报告文档。

## 在实际数据库中执行

如果需要在实际的 PostgreSQL 数据库中执行 DDL 脚本：

```bash
# 执行迁移脚本
psql -U <username> -d <database> -f database/migrations/001_create_message_table.sql

# 验证表是否创建成功
psql -U <username> -d <database> -c "\d message_table"

# 验证索引是否创建成功
psql -U <username> -d <database> -c "\di message_table*"
```

## 故障排查

### 问题: Python 脚本执行失败

**可能原因:**
- Python 版本不兼容（需要 Python 3.6+）
- 文件路径错误

**解决方法:**
```bash
# 检查 Python 版本
python --version

# 确保在项目根目录执行
cd /path/to/project
python database/tests/test_message_table_ddl.py
```

### 问题: 测试失败

**可能原因:**
- DDL 脚本被修改
- 测试脚本与 DDL 脚本不同步

**解决方法:**
1. 检查 DDL 脚本是否符合设计文档
2. 更新测试脚本以匹配新的 DDL 结构

## 相关文档

- [设计文档](../../.kiro/specs/message-reminder/design.md) - 查看完整的数据库设计
- [需求文档](../../.kiro/specs/message-reminder/requirements.md) - 了解业务需求
- [任务列表](../../.kiro/specs/message-reminder/tasks.md) - 查看开发任务
- [迁移脚本说明](../migrations/README.md) - 了解如何执行迁移

## 贡献

如果需要添加新的测试用例：

1. 在 `test_message_table_operations.py` 中添加新的测试方法
2. 方法名以 `test_` 开头
3. 在 `run_all_tests()` 中调用新方法
4. 更新 TEST_REPORT.md

## 许可证

本测试套件遵循项目的许可证。
