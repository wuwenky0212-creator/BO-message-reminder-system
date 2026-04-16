---
name: sqlite-adapter
description: 将 Node.js/TypeScript 后端从 PostgreSQL 迁移到 SQLite 数据库，用于开发和测试环境。当用户需要在没有 Docker 或 PostgreSQL 的情况下运行项目时使用此技能。
---

# SQLite 数据库适配器技能

## 概述

此技能提供将基于 PostgreSQL 的 Node.js/TypeScript 后端应用迁移到 SQLite 的完整解决方案。适用于开发、测试或演示环境，无需安装 Docker 或 PostgreSQL。

## 使用场景

- 用户没有安装 Docker 或 PostgreSQL
- 需要快速启动项目进行演示
- 开发环境需要轻量级数据库
- 测试环境需要独立的数据库实例

## 实施步骤

### 1. 安装 SQLite 依赖

```bash
npm install better-sqlite3 @types/better-sqlite3
```

### 2. 创建 SQLite 兼容的 Schema

将 PostgreSQL schema 转换为 SQLite 格式：

**主要差异：**
- `VARCHAR` → `TEXT`
- `TIMESTAMP` → `TEXT`
- `JSONB` → `TEXT`
- `BOOLEAN` → `INTEGER` (0/1)
- `SERIAL` → `INTEGER PRIMARY KEY AUTOINCREMENT`
- `datetime('now')` 替代 `CURRENT_TIMESTAMP`

**示例转换：**

PostgreSQL:
```sql
CREATE TABLE IF NOT EXISTS operation_logs (
  log_id VARCHAR(50) PRIMARY KEY,
  employee_id VARCHAR(20) NOT NULL,
  operation_time TIMESTAMP NOT NULL,
  data_changes JSONB,
  abnormal_flag BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

SQLite:
```sql
CREATE TABLE IF NOT EXISTS operation_logs (
  log_id TEXT PRIMARY KEY,
  employee_id TEXT NOT NULL,
  operation_time TEXT NOT NULL,
  data_changes TEXT,
  abnormal_flag INTEGER DEFAULT 0,
  created_at TEXT DEFAULT (datetime('now'))
);
```

### 3. 创建数据库适配器

修改现有的数据库初始化模块以支持两种数据库：

```typescript
import { Pool } from 'pg';
import Database from 'better-sqlite3';

// SQLite Pool 适配器类
class SQLitePoolAdapter {
  private db: Database.Database;

  constructor(db: Database.Database) {
    this.db = db;
  }

  async query(sql: string, params: any[] = []): Promise<{ rows: any[]; rowCount: number }> {
    // 将 PostgreSQL 风格的 $1, $2 转换为 SQLite 风格的 ?
    const sqliteSql = sql.replace(/\$(\d+)/g, '?');
    
    try {
      const stmt = this.db.prepare(sqliteSql);
      
      if (sqliteSql.trim().toUpperCase().startsWith('SELECT')) {
        const rows = stmt.all(...params);
        return { rows, rowCount: rows.length };
      } else {
        const info = stmt.run(...params);
        return { rows: [], rowCount: info.changes };
      }
    } catch (error) {
      console.error('SQLite query error:', error);
      throw error;
    }
  }

  async end(): Promise<void> {
    this.db.close();
  }

  on(event: string, handler: (err: Error) => void): void {
    // 兼容性方法
  }
}

// 修改 createPool 函数支持两种模式
export function createPool(config: DatabaseConfig | string): Pool | SQLitePoolAdapter {
  if (typeof config === 'string') {
    // SQLite 模式
    const db = new Database(config);
    db.pragma('foreign_keys = ON');
    db.pragma('journal_mode = WAL');
    return new SQLitePoolAdapter(db);
  } else {
    // PostgreSQL 模式
    return new Pool(config);
  }
}
```

### 4. 更新环境配置

在 `.env` 文件中添加数据库类型配置：

```env
# 数据库配置
DB_TYPE=sqlite
SQLITE_PATH=./audit-trail.db

# PostgreSQL 配置（当 DB_TYPE=postgresql 时使用）
DB_HOST=localhost
DB_PORT=5432
DB_NAME=database_name
DB_USER=postgres
DB_PASSWORD=password
```

### 5. 修改应用入口

```typescript
import { createPool, initializeSchema, testConnection } from './database/init.js';

const DB_TYPE = process.env.DB_TYPE || 'sqlite';
const SQLITE_PATH = process.env.SQLITE_PATH || './database.db';

async function initializeDatabase() {
  try {
    if (DB_TYPE === 'sqlite') {
      console.log('Initializing SQLite database...');
      createPool(SQLITE_PATH);
    } else {
      console.log('Initializing PostgreSQL database...');
      createPool({
        host: process.env.DB_HOST || 'localhost',
        port: parseInt(process.env.DB_PORT || '5432'),
        database: process.env.DB_NAME || 'database',
        user: process.env.DB_USER || 'postgres',
        password: process.env.DB_PASSWORD || '',
      });
    }
    
    await initializeSchema();
    await testConnection();
    
    console.log('Database initialized successfully');
  } catch (error) {
    console.error('Failed to initialize database:', error);
    process.exit(1);
  }
}

await initializeDatabase();
```

### 6. 处理延迟初始化

如果路由在模块加载时就调用 `getPool()`，需要延迟服务初始化：

```typescript
// 错误方式：
const pool = getPool(); // 此时数据库可能还未初始化
const service = createService(pool);

// 正确方式：
let service: ReturnType<typeof createService>;

function initializeServices() {
  if (!service) {
    const pool = getPool();
    service = createService(pool);
  }
}

router.post('/api/endpoint', async (req, res) => {
  initializeServices(); // 在第一次使用时初始化
  // ... 使用 service
});
```

### 7. 实现不可变性保护

SQLite 使用触发器实现记录不可变：

```typescript
async function applyImmutabilityProtection(): Promise<void> {
  const tables = ['operation_logs', 'message_trails', 'query_logs', 'export_logs'];
  
  for (const table of tables) {
    // 防止 UPDATE
    await pool.query(`
      CREATE TRIGGER IF NOT EXISTS prevent_${table}_update
      BEFORE UPDATE ON ${table}
      BEGIN
        SELECT RAISE(ABORT, 'Updates are not allowed on ${table} table');
      END;
    `, []);

    // 防止 DELETE
    await pool.query(`
      CREATE TRIGGER IF NOT EXISTS prevent_${table}_delete
      BEFORE DELETE ON ${table}
      BEGIN
        SELECT RAISE(ABORT, 'Deletes are not allowed on ${table} table');
      END;
    `, []);
  }
}
```

## 关键注意事项

### SQL 查询兼容性

1. **参数占位符**：适配器自动将 `$1, $2` 转换为 `?`
2. **日期时间**：SQLite 使用 TEXT 存储，使用 `datetime('now')` 获取当前时间
3. **JSON 数据**：需要手动序列化/反序列化
4. **布尔值**：使用 INTEGER (0/1)

### 性能考虑

1. **WAL 模式**：启用 Write-Ahead Logging 提高并发性能
2. **外键约束**：需要显式启用 `PRAGMA foreign_keys = ON`
3. **索引**：保持与 PostgreSQL 相同的索引策略

### 限制

1. **并发写入**：SQLite 的并发写入能力有限
2. **网络访问**：SQLite 是文件数据库，不支持网络访问
3. **生产环境**：不建议在高负载生产环境使用

## 测试验证

启动应用后验证：

```bash
# 启动后端
npm run dev

# 检查数据库文件
ls -la *.db

# 测试 API 端点
curl http://localhost:5000/health
```

## 切换回 PostgreSQL

只需修改 `.env` 文件：

```env
DB_TYPE=postgresql
```

然后重启应用即可。

## 故障排查

### 问题：Database pool not initialized

**原因**：在数据库初始化前调用了 `getPool()`

**解决**：使用延迟初始化模式（见步骤 6）

### 问题：SQL syntax error

**原因**：PostgreSQL 和 SQLite 的 SQL 语法差异

**解决**：检查并转换不兼容的 SQL 语句

### 问题：JSONB 数据丢失

**原因**：SQLite 不支持 JSONB 类型

**解决**：使用 TEXT 类型，手动进行 JSON 序列化

## 文件清单

创建或修改以下文件：

1. `src/database/schema-sqlite.sql` - SQLite schema 定义
2. `src/database/init.ts` - 修改以支持双数据库
3. `.env` - 添加 DB_TYPE 和 SQLITE_PATH 配置
4. `src/index.ts` - 修改数据库初始化逻辑
5. `src/routes/*.ts` - 实现延迟服务初始化

## 总结

此技能提供了一个完整的解决方案，让基于 PostgreSQL 的应用可以无缝切换到 SQLite，适用于开发、测试和演示场景。通过适配器模式，保持了代码的兼容性，可以随时切换回 PostgreSQL。
