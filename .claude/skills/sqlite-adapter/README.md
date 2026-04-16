# SQLite 数据库适配器 Skill

## 简介

这个 skill 提供了将 Node.js/TypeScript 后端应用从 PostgreSQL 迁移到 SQLite 的完整解决方案。适用于开发、测试或演示环境，无需安装 Docker 或 PostgreSQL。

## 特性

- ✅ 无缝切换 PostgreSQL 和 SQLite
- ✅ 保持代码兼容性（使用适配器模式）
- ✅ 自动转换 SQL 参数占位符（$1, $2 → ?）
- ✅ 支持数据不可变性保护（触发器）
- ✅ 完整的 schema 转换指南
- ✅ 延迟初始化模式解决启动顺序问题

## 快速开始

### 1. 安装依赖

```bash
npm install better-sqlite3 @types/better-sqlite3
```

### 2. 配置环境变量

创建或修改 `.env` 文件：

```env
DB_TYPE=sqlite
SQLITE_PATH=./database.db
```

### 3. 使用示例代码

参考 `examples/` 目录中的示例：

- `sqlite-pool-adapter.ts` - SQLite 池适配器实现
- `database-init.ts` - 数据库初始化模块
- `lazy-initialization.ts` - 延迟初始化模式
- `schema-conversion.md` - Schema 转换指南

## 文件结构

```
.claude/skills/sqlite-adapter/
├── SKILL.md                    # 完整技能文档
├── README.md                   # 本文件
└── examples/
    ├── sqlite-pool-adapter.ts  # SQLite 适配器实现
    ├── database-init.ts        # 数据库初始化
    ├── lazy-initialization.ts  # 延迟初始化示例
    ├── .env.example            # 环境变量示例
    └── schema-conversion.md    # Schema 转换指南
```

## 使用场景

### 场景 1：开发环境

开发者没有安装 Docker 或 PostgreSQL，需要快速启动项目：

```env
DB_TYPE=sqlite
SQLITE_PATH=./dev.db
```

### 场景 2：测试环境

每个测试使用独立的 SQLite 数据库：

```typescript
const testDb = `./test-${Date.now()}.db`;
createPool(testDb);
```

### 场景 3：演示环境

快速部署演示版本，无需配置数据库服务器：

```env
DB_TYPE=sqlite
SQLITE_PATH=./demo.db
```

### 场景 4：生产环境

切换回 PostgreSQL：

```env
DB_TYPE=postgresql
DB_HOST=production-db.example.com
DB_PORT=5432
DB_NAME=production_db
DB_USER=app_user
DB_PASSWORD=secure_password
```

## 核心概念

### 适配器模式

`SQLitePoolAdapter` 类实现了与 PostgreSQL `Pool` 相同的接口，使得应用代码无需修改即可切换数据库：

```typescript
// 应用代码保持不变
const result = await pool.query('SELECT * FROM users WHERE id = $1', [userId]);
```

适配器自动处理：
- 参数占位符转换（$1 → ?）
- 查询结果格式统一
- 连接管理

### 延迟初始化

解决模块加载顺序问题：

```typescript
// ❌ 错误：在数据库初始化前调用
const pool = getPool();

// ✅ 正确：延迟到首次使用时
function initializeServices() {
  if (!service) {
    const pool = getPool();
    service = createService(pool);
  }
}
```

## 限制和注意事项

### SQLite 限制

1. **并发写入**：同一时间只能有一个写操作
2. **网络访问**：不支持远程连接
3. **数据库大小**：建议不超过 1GB
4. **复杂查询**：某些高级 PostgreSQL 特性不支持

### 不建议使用的场景

- ❌ 高并发写入的生产环境
- ❌ 需要网络访问的分布式系统
- ❌ 大数据量（> 1GB）的应用
- ❌ 需要复杂事务的应用

### 建议使用的场景

- ✅ 本地开发环境
- ✅ 单元测试和集成测试
- ✅ 演示和原型开发
- ✅ 小型单机应用

## 性能优化

### 启用 WAL 模式

Write-Ahead Logging 提高并发性能：

```typescript
db.pragma('journal_mode = WAL');
```

### 启用外键约束

```typescript
db.pragma('foreign_keys = ON');
```

### 创建适当的索引

与 PostgreSQL 保持相同的索引策略：

```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_logs_time ON logs(created_at);
```

## 故障排查

### 问题：Database pool not initialized

**症状**：应用启动时报错

**原因**：在数据库初始化前调用了 `getPool()`

**解决**：使用延迟初始化模式

### 问题：SQL syntax error

**症状**：查询执行失败

**原因**：PostgreSQL 和 SQLite 的 SQL 语法差异

**解决**：参考 `schema-conversion.md` 转换 SQL 语句

### 问题：JSONB 数据丢失

**症状**：JSON 数据无法正确存储或读取

**原因**：SQLite 不支持 JSONB 类型

**解决**：
```typescript
// 存储时序列化
const jsonStr = JSON.stringify(data);
await pool.query('INSERT INTO table (data) VALUES (?)', [jsonStr]);

// 读取时反序列化
const result = await pool.query('SELECT data FROM table WHERE id = ?', [id]);
const data = JSON.parse(result.rows[0].data);
```

## 测试

### 单元测试

```typescript
import { createPool, initializeSchema } from './database/init';

describe('SQLite Adapter', () => {
  beforeEach(async () => {
    const testDb = `./test-${Date.now()}.db`;
    createPool(testDb);
    await initializeSchema();
  });

  it('should insert and query data', async () => {
    const pool = getPool();
    await pool.query('INSERT INTO users (id, name) VALUES (?, ?)', [1, 'Test']);
    const result = await pool.query('SELECT * FROM users WHERE id = ?', [1]);
    expect(result.rows[0].name).toBe('Test');
  });
});
```

### 集成测试

```bash
# 启动应用
npm run dev

# 测试 API
curl http://localhost:5000/health
curl -X POST http://localhost:5000/api/data -H "Content-Type: application/json" -d '{"test": "data"}'
```

## 贡献

欢迎提交问题和改进建议！

## 许可证

MIT License

## 相关资源

- [SQLite 官方文档](https://www.sqlite.org/docs.html)
- [better-sqlite3 文档](https://github.com/WiseLibs/better-sqlite3/wiki)
- [PostgreSQL 到 SQLite 迁移指南](https://www.sqlite.org/lang.html)
