# 任务执行日志表 - 快速执行指南

## 快速开始

### 1. 执行迁移（创建表）

```bash
# PostgreSQL
psql -U postgres -d rcs_test -f database/migrations/003_create_task_execution_log.sql

# 或使用环境变量
PGPASSWORD=your_password psql -h localhost -U postgres -d rcs_test -f database/migrations/003_create_task_execution_log.sql
```

**预期输出:**
```
CREATE TABLE
CREATE INDEX
CREATE INDEX
CREATE INDEX
CREATE INDEX
COMMENT
COMMENT
...
NOTICE:  Table task_execution_log created successfully
```

### 2. 验证表结构

```bash
# 执行完整验证脚本
psql -U postgres -d rcs_test -f database/tests/validate_task_execution_log.sql
```

**预期输出:**
```
NOTICE:  ✓ Table task_execution_log exists
NOTICE:  ✓ All required columns exist
NOTICE:  ✓ All required indexes exist
NOTICE:  ✓ Unique constraint on task_id exists
NOTICE:  ✓ Test data inserted successfully
NOTICE:  ✓ Unique constraint on task_id is working
...
NOTICE:  ============================================================================
NOTICE:  Validation completed successfully!
NOTICE:  ============================================================================
```

### 3. 快速验证（手动）

```sql
-- 1. 检查表是否存在
SELECT EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_name = 'task_execution_log'
);

-- 2. 查看表结构
\d task_execution_log

-- 3. 查看索引
\di task_execution_log*

-- 4. 插入测试数据
INSERT INTO task_execution_log (
    task_id, rule_code, rule_name, 
    scheduled_time, actual_start_time, status
) VALUES (
    'TEST_001', 'CHK_TRD_004', '测试任务',
    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'completed'
);

-- 5. 查询测试数据
SELECT * FROM task_execution_log WHERE task_id = 'TEST_001';

-- 6. 清理测试数据
DELETE FROM task_execution_log WHERE task_id = 'TEST_001';
```

## 回滚操作

如果需要回滚（删除表）：

```bash
psql -U postgres -d rcs_test -f database/migrations/003_create_task_execution_log_downgrade.sql
```

**预期输出:**
```
DROP INDEX
DROP INDEX
DROP INDEX
DROP INDEX
DROP TABLE
NOTICE:  Table task_execution_log dropped successfully
```

## 常见问题

### Q1: 表已存在错误

**错误信息:** `ERROR: relation "task_execution_log" already exists`

**解决方案:**
```sql
-- 检查表是否存在
SELECT * FROM information_schema.tables WHERE table_name = 'task_execution_log';

-- 如果需要重建，先删除
DROP TABLE IF EXISTS task_execution_log CASCADE;

-- 然后重新执行迁移脚本
```

### Q2: 权限不足错误

**错误信息:** `ERROR: permission denied for schema public`

**解决方案:**
```sql
-- 授予权限
GRANT ALL ON SCHEMA public TO your_user;
GRANT ALL ON ALL TABLES IN SCHEMA public TO your_user;
```

### Q3: 索引创建失败

**错误信息:** `ERROR: could not create unique index "uk_task_id"`

**解决方案:**
```sql
-- 检查是否有重复数据
SELECT task_id, COUNT(*) 
FROM task_execution_log 
GROUP BY task_id 
HAVING COUNT(*) > 1;

-- 清理重复数据后重新创建索引
CREATE UNIQUE INDEX uk_task_id ON task_execution_log(task_id);
```

## 验收检查清单

- [ ] 表创建成功
- [ ] 12个字段全部存在
- [ ] 5个索引全部创建成功
- [ ] task_id唯一约束生效
- [ ] 可以正常插入数据
- [ ] 可以正常查询数据
- [ ] 可以正常更新数据
- [ ] 可以正常删除数据
- [ ] 索引正常使用（通过EXPLAIN验证）
- [ ] 表注释和字段注释存在

## 性能检查

```sql
-- 检查表大小
SELECT 
    pg_size_pretty(pg_total_relation_size('task_execution_log')) as total_size,
    pg_size_pretty(pg_relation_size('task_execution_log')) as table_size,
    pg_size_pretty(pg_indexes_size('task_execution_log')) as indexes_size;

-- 检查索引使用情况
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE tablename = 'task_execution_log';

-- 检查表统计信息
SELECT 
    schemaname,
    tablename,
    n_live_tup as live_tuples,
    n_dead_tup as dead_tuples,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE tablename = 'task_execution_log';
```

## 下一步

表创建和验证完成后，可以继续：

1. **任务1.4:** 创建审计日志表 (audit_log)
2. **任务2.1:** 实现数据库ORM模型
3. **任务3.1:** 实现规则扫描器基础框架

---

**提示:** 详细的验证文档请参考 `database/docs/task_execution_log_validation.md`
