/**
 * 数据库初始化模块
 * 
 * 支持 PostgreSQL 和 SQLite 双模式
 */

import { Pool, PoolConfig } from 'pg';
import Database from 'better-sqlite3';
import { SQLitePoolAdapter } from './sqlite-pool-adapter.js';

let pool: Pool | SQLitePoolAdapter | null = null;
let dbType: 'postgresql' | 'sqlite' = 'postgresql';

/**
 * 创建数据库连接池
 * 
 * @param config - PostgreSQL 配置对象或 SQLite 文件路径
 */
export function createPool(config: PoolConfig | string): Pool | SQLitePoolAdapter {
  if (typeof config === 'string') {
    // SQLite 模式
    dbType = 'sqlite';
    const db = new Database(config);
    
    // 启用外键约束
    db.pragma('foreign_keys = ON');
    
    // 启用 WAL 模式以提高并发性能
    db.pragma('journal_mode = WAL');
    
    console.log(`SQLite database created: ${config}`);
    
    pool = new SQLitePoolAdapter(db);
    return pool;
  } else {
    // PostgreSQL 模式
    dbType = 'postgresql';
    pool = new Pool(config);

    pool.on('error', (err) => {
      console.error('Unexpected error on idle client', err);
    });

    return pool;
  }
}

/**
 * 获取数据库连接池
 */
export function getPool(): Pool | SQLitePoolAdapter {
  if (!pool) {
    throw new Error('Database pool not initialized. Call createPool() first.');
  }
  return pool;
}

/**
 * 初始化数据库 Schema
 */
export async function initializeSchema(): Promise<void> {
  if (!pool) {
    throw new Error('Database pool not initialized. Call createPool() first.');
  }

  try {
    // 根据数据库类型选择不同的 schema 文件
    const schemaFile = dbType === 'sqlite' ? 'schema-sqlite.sql' : 'schema.sql';
    const schemaSql = readFileSync(join(__dirname, schemaFile), 'utf-8');

    if (dbType === 'sqlite') {
      // SQLite 需要逐条执行语句
      const statements = schemaSql
        .split(';')
        .map(s => s.trim())
        .filter(s => s.length > 0);

      for (const statement of statements) {
        await pool.query(statement + ';', []);
      }
    } else {
      // PostgreSQL 可以一次执行整个 schema
      await pool.query(schemaSql, []);
    }

    console.log(`${dbType === 'sqlite' ? 'SQLite' : 'PostgreSQL'} schema initialized`);
  } catch (error) {
    console.error('Failed to initialize schema:', error);
    throw error;
  }
}

/**
 * 测试数据库连接
 */
export async function testConnection(): Promise<boolean> {
  if (!pool) {
    throw new Error('Database pool not initialized. Call createPool() first.');
  }

  try {
    const sql = dbType === 'sqlite' ? "SELECT datetime('now') as now" : 'SELECT NOW()';
    const result = await pool.query(sql, []);
    console.log('Database connection successful:', result.rows[0]);
    return true;
  } catch (error) {
    console.error('Database connection failed:', error);
    return false;
  }
}

/**
 * 关闭数据库连接
 */
export async function closePool(): Promise<void> {
  if (pool) {
    await pool.end();
    pool = null;
    console.log('Database pool closed');
  }
}
