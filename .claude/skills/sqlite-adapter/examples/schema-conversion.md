# PostgreSQL 到 SQLite Schema 转换指南

## 数据类型映射

| PostgreSQL | SQLite | 说明 |
|-----------|--------|------|
| `VARCHAR(n)` | `TEXT` | SQLite 的 TEXT 没有长度限制 |
| `TEXT` | `TEXT` | 直接对应 |
| `INTEGER` | `INTEGER` | 直接对应 |
| `BIGINT` | `INTEGER` | SQLite 的 INTEGER 可存储 64 位整数 |
| `SERIAL` | `INTEGER PRIMARY KEY AUTOINCREMENT` | 自增主键 |
| `BOOLEAN` | `INTEGER` | 使用 0 (false) 和 1 (true) |
| `TIMESTAMP` | `TEXT` | 使用 ISO 8601 格式字符串 |
| `DATE` | `TEXT` | 使用 ISO 8601 格式字符串 |
| `JSONB` | `TEXT` | 需要手动序列化/反序列化 |
| `JSON` | `TEXT` | 需要手动序列化/反序列化 |
| `DECIMAL(p,s)` | `REAL` | 或使用 TEXT 存储精确值 |
| `REAL` | `REAL` | 直接对应 |
| `DOUBLE PRECISION` | `REAL` | 直接对应 |

## 函数和表达式转换

| PostgreSQL | SQLite | 说明 |
|-----------|--------|------|
| `NOW()` | `datetime('now')` | 当前时间戳 |
| `CURRENT_TIMESTAMP` | `datetime('now')` | 当前时间戳 |
| `CURRENT_DATE` | `date('now')` | 当前日期 |
| `CURRENT_TIME` | `time('now')` | 当前时间 |
| `EXTRACT(YEAR FROM date)` | `strftime('%Y', date)` | 提取年份 |
| `EXTRACT(MONTH FROM date)` | `strftime('%m', date)` | 提取月份 |
| `EXTRACT(DAY FROM date)` | `strftime('%d', date)` | 提取日期 |
| `CONCAT(a, b)` | `a || b` | 字符串连接 |
| `COALESCE(a, b)` | `COALESCE(a, b)` | 直接对应 |

## 约束转换

### CHECK 约束

PostgreSQL:
```sql
direction VARCHAR(10) NOT NULL CHECK (direction IN ('SEND', 'RECEIVE'))
```

SQLite:
```sql
direction TEXT NOT NULL CHECK (direction IN ('SEND', 'RECEIVE'))
```

### 外键约束

PostgreSQL:
```sql
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
```

SQLite:
```sql
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
```

注意：SQLite 需要显式启用外键约束：
```sql
PRAGMA foreign_keys = ON;
```

## 默认值转换

PostgreSQL:
```sql
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

SQLite:
```sql
created_at TEXT DEFAULT (datetime('now'))
```

## 索引转换

PostgreSQL:
```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_logs_time ON logs(created_at DESC);
```

SQLite:
```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_logs_time ON logs(created_at DESC);
```

索引语法基本相同。

## 触发器转换

### PostgreSQL 触发器

```sql
CREATE OR REPLACE FUNCTION prevent_update()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'Updates are not allowed';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER prevent_logs_update
BEFORE UPDATE ON logs
FOR EACH ROW
EXECUTE FUNCTION prevent_update();
```

### SQLite 触发器

```sql
CREATE TRIGGER prevent_logs_update
BEFORE UPDATE ON logs
BEGIN
  SELECT RAISE(ABORT, 'Updates are not allowed');
END;
```

## 完整示例

### PostgreSQL Schema

```sql
CREATE TABLE IF NOT EXISTS operation_logs (
  log_id VARCHAR(50) PRIMARY KEY,
  employee_id VARCHAR(20) NOT NULL,
  operation_time TIMESTAMP NOT NULL,
  module_name VARCHAR(50) NOT NULL,
  operation_type VARCHAR(30) NOT NULL,
  trade_reference VARCHAR(50),
  before_snapshot JSONB,
  after_snapshot JSONB,
  data_changes JSONB,
  operation_result VARCHAR(20) NOT NULL,
  error_message TEXT,
  comment TEXT,
  abnormal_flag BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_operation_logs_employee_time 
  ON operation_logs(employee_id, operation_time);
```

### SQLite Schema

```sql
CREATE TABLE IF NOT EXISTS operation_logs (
  log_id TEXT PRIMARY KEY,
  employee_id TEXT NOT NULL,
  operation_time TEXT NOT NULL,
  module_name TEXT NOT NULL,
  operation_type TEXT NOT NULL,
  trade_reference TEXT,
  before_snapshot TEXT,
  after_snapshot TEXT,
  data_changes TEXT,
  operation_result TEXT NOT NULL,
  error_message TEXT,
  comment TEXT,
  abnormal_flag INTEGER DEFAULT 0,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_operation_logs_employee_time 
  ON operation_logs(employee_id, operation_time);
```

## 注意事项

1. **JSONB 处理**：SQLite 不支持 JSONB，需要在应用层进行 JSON 序列化/反序列化
2. **布尔值**：使用 INTEGER (0/1) 代替 BOOLEAN
3. **时间戳**：使用 TEXT 存储 ISO 8601 格式的时间字符串
4. **外键**：需要显式启用 `PRAGMA foreign_keys = ON`
5. **事务**：SQLite 默认自动提交，需要显式开启事务
6. **并发**：SQLite 的并发写入能力有限，建议启用 WAL 模式

## 自动转换脚本

可以创建一个简单的脚本来自动转换 schema：

```javascript
function convertSchema(postgresqlSchema) {
  return postgresqlSchema
    .replace(/VARCHAR\(\d+\)/g, 'TEXT')
    .replace(/TIMESTAMP/g, 'TEXT')
    .replace(/JSONB/g, 'TEXT')
    .replace(/BOOLEAN/g, 'INTEGER')
    .replace(/CURRENT_TIMESTAMP/g, "(datetime('now'))")
    .replace(/NOW\(\)/g, "datetime('now')")
    .replace(/DEFAULT FALSE/g, 'DEFAULT 0')
    .replace(/DEFAULT TRUE/g, 'DEFAULT 1');
}
```
