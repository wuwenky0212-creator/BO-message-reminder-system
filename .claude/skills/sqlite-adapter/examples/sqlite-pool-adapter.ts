/**
 * SQLite Pool Adapter
 * 
 * 使 SQLite 数据库看起来像 PostgreSQL Pool，实现无缝切换
 */

import Database from 'better-sqlite3';

export class SQLitePoolAdapter {
  private db: Database.Database;

  constructor(db: Database.Database) {
    this.db = db;
  }

  /**
   * 执行 SQL 查询
   * 自动将 PostgreSQL 风格的参数占位符 ($1, $2) 转换为 SQLite 风格 (?)
   */
  async query(sql: string, params: any[] = []): Promise<{ rows: any[]; rowCount: number }> {
    // 转换参数占位符
    const sqliteSql = sql.replace(/\$(\d+)/g, '?');
    
    try {
      const stmt = this.db.prepare(sqliteSql);
      
      // 判断查询类型
      if (sqliteSql.trim().toUpperCase().startsWith('SELECT')) {
        const rows = stmt.all(...params);
        return {
          rows,
          rowCount: rows.length,
        };
      } else {
        // INSERT, UPDATE, DELETE
        const info = stmt.run(...params);
        return {
          rows: [],
          rowCount: info.changes,
        };
      }
    } catch (error) {
      console.error('SQLite query error:', error);
      console.error('SQL:', sqliteSql);
      console.error('Params:', params);
      throw error;
    }
  }

  /**
   * 关闭数据库连接
   */
  async end(): Promise<void> {
    this.db.close();
  }

  /**
   * 事件监听器（兼容性方法）
   * SQLite 不需要池事件，但提供此方法以保持接口兼容
   */
  on(event: string, handler: (err: Error) => void): void {
    // SQLite 不需要池事件处理
  }
}
