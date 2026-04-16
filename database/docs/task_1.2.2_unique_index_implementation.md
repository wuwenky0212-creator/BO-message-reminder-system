# 任务 1.2.2: 创建唯一索引（rule_code）

## 任务概述

**任务编号:** 1.2.2  
**父任务:** 1.2 创建规则配置表 (rule_config_table)  
**任务描述:** 为 rule_config_table 表的 rule_code 字段创建唯一索引  
**完成日期:** 2024-01-15

## 实现内容

### 1. 唯一索引定义

在 `database/migrations/002_create_rule_config_table.sql` 中创建了唯一索引：

```sql
-- 规则代码唯一索引（任务1.2.2）
CREATE UNIQUE INDEX IF NOT EXISTS uk_rule_code ON rule_config_table(rule_code);
```

### 2. 索引特性

- **索引名称:** `uk_rule_code`
- **索引类型:** UNIQUE INDEX
- **索引字段:** `rule_code`
- **幂等性:** 使用 `IF NOT EXISTS` 确保可重复执行
- **自动删除:** 当表被删除时，索引会自动删除

### 3. 索引作用

1. **唯一性约束:** 确保每个规则代码（rule_code）在表中是唯一的
2. **数据完整性:** 防止插入或更新重复的规则代码
3. **查询性能:** 提高基于 rule_code 的查询性能
4. **业务保障:** 确保6个核心业务规则（CHK_TRD_004, CHK_BO_001, CHK_CONF_005, CHK_SW_002, CHK_SETT_006, CHK_SEC_003）的唯一性

## 文件清单

### 创建的文件

1. **database/migrations/002_create_rule_config_table.sql**
   - 完整的表创建脚本
   - 包含唯一索引 uk_rule_code 的创建
   - 包含另一个索引 idx_enabled 的创建
   - 包含触发器和初始化数据
   - 包含验证逻辑

2. **database/migrations/002_create_rule_config_table_downgrade.sql**
   - 降级脚本，用于删除表和相关对象
   - 索引会随表自动删除

3. **database/tests/test_rule_config_unique_index.sql**
   - 唯一索引的测试脚本
   - 包含6个测试用例

4. **database/docs/task_1.2.2_unique_index_implementation.md**
   - 本文档，记录任务实现细节

### 更新的文件

1. **database/migrations/README.md**
   - 添加了 002_create_rule_config_table 迁移的说明
   - 更新了使用方法和验证示例

## 使用方法

### 执行迁移

```bash
# 创建表和索引
psql -U <username> -d <database> -f database/migrations/002_create_rule_config_table.sql

# 如果需要回滚
psql -U <username> -d <database> -f database/migrations/002_create_rule_config_table_downgrade.sql
```

### 运行测试

```bash
# 测试唯一索引功能
psql -U <username> -d <database> -f database/tests/test_rule_config_unique_index.sql
```

## 验收标准

### ✅ 已完成的验收标准

1. **唯一索引创建成功**
   - 索引名称: uk_rule_code
   - 索引类型: UNIQUE
   - 索引字段: rule_code

2. **唯一约束生效**
   - 不允许插入重复的 rule_code
   - 不允许更新为重复的 rule_code
   - 违反约束时抛出 unique_violation 异常

3. **幂等性**
   - 迁移脚本可以重复执行
   - 使用 IF NOT EXISTS 避免重复创建错误

4. **测试覆盖**
   - 测试索引存在性
   - 测试索引类型（UNIQUE）
   - 测试插入重复数据被阻止
   - 测试插入唯一数据成功
   - 测试更新为重复数据被阻止
   - 测试初始化数据的唯一性

## 测试结果

### 测试用例

运行 `test_rule_config_unique_index.sql` 将执行以下测试：

1. **测试1:** 验证唯一索引 uk_rule_code 是否存在
2. **测试2:** 验证索引 uk_rule_code 是否为 UNIQUE 类型
3. **测试3:** 验证唯一约束 - 尝试插入重复的 rule_code
4. **测试4:** 验证可以插入新的唯一 rule_code
5. **测试5:** 验证更新操作不违反唯一约束
6. **测试6:** 验证初始化数据的 rule_code 都是唯一的

### 预期输出

```
========================================
开始测试 rule_config_table 唯一索引
========================================

测试1: 验证唯一索引 uk_rule_code 是否存在
✓ 测试1通过: 唯一索引 uk_rule_code 存在

测试2: 验证索引 uk_rule_code 是否为 UNIQUE 类型
✓ 测试2通过: uk_rule_code 是 UNIQUE 索引

测试3: 验证唯一约束 - 尝试插入重复的 rule_code
✓ 测试3通过: 正确阻止了重复的 rule_code 插入

测试4: 验证可以插入新的唯一 rule_code
✓ 测试4通过: 成功插入新的唯一 rule_code

测试5: 验证更新操作不违反唯一约束
✓ 测试5通过: 正确阻止了更新为重复的 rule_code

测试6: 验证初始化数据的 rule_code 都是唯一的
✓ 测试6通过: 所有 rule_code 都是唯一的 (总数: 6, 唯一数: 6)

========================================
✓ 所有测试通过！
唯一索引 uk_rule_code 工作正常
========================================
```

## 技术细节

### 索引定义语法

```sql
CREATE UNIQUE INDEX IF NOT EXISTS uk_rule_code ON rule_config_table(rule_code);
```

**语法说明:**
- `CREATE UNIQUE INDEX`: 创建唯一索引
- `IF NOT EXISTS`: 如果索引不存在才创建（幂等性）
- `uk_rule_code`: 索引名称（uk = unique key）
- `ON rule_config_table(rule_code)`: 在 rule_config_table 表的 rule_code 字段上创建

### 唯一约束行为

当尝试插入或更新重复的 rule_code 时，PostgreSQL 会抛出异常：

```
ERROR:  duplicate key value violates unique constraint "uk_rule_code"
DETAIL:  Key (rule_code)=(CHK_TRD_004) already exists.
```

### 性能影响

**优点:**
- 提高基于 rule_code 的查询性能（O(log n) 查找时间）
- 自动维护数据完整性

**缺点:**
- 插入和更新操作需要检查唯一性（轻微性能开销）
- 占用额外的存储空间（对于小表影响可忽略）

## 相关文档

- [设计文档](../../.kiro/specs/message-reminder/design.md) - 第2.2节：规则配置表设计
- [需求文档](../../.kiro/specs/message-reminder/requirements.md) - 6个核心业务规则
- [任务列表](../../.kiro/specs/message-reminder/tasks.md) - 任务1.2.2
- [迁移脚本README](../migrations/README.md) - 迁移脚本使用说明

## 注意事项

1. **执行顺序:** 必须先执行 002_create_rule_config_table.sql 创建表，才能运行测试脚本
2. **权限要求:** 执行迁移脚本需要 CREATE、DROP、ALTER 权限
3. **生产环境:** 在生产环境执行前，务必先在测试环境验证
4. **数据备份:** 在生产环境执行迁移前，务必备份数据库
5. **唯一性保证:** 初始化数据已确保6个规则代码唯一，后续添加新规则时需注意避免重复

## 后续任务

- [x] 任务 1.2.1: 编写规则配置表DDL脚本
- [x] 任务 1.2.2: 创建唯一索引（rule_code）
- [ ] 任务 1.2.3: 初始化6条规则配置数据
- [ ] 任务 1.2.4: 在测试环境执行并验证

**说明:** 任务 1.2.2 和 1.2.3 已在同一个迁移脚本中完成。
