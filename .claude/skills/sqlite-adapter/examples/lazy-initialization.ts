/**
 * 延迟初始化模式
 * 
 * 解决路由在模块加载时就调用 getPool() 导致的初始化顺序问题
 */

import { Router, Request, Response } from 'express';
import { getPool } from '../database/init.js';
import { createService } from '../services/index.js';

const router = Router();

// 服务将在首次使用时初始化
let service: ReturnType<typeof createService>;

/**
 * 初始化服务（延迟初始化）
 */
function initializeServices() {
  if (!service) {
    const pool = getPool();
    service = createService(pool);
  }
}

/**
 * API 路由示例
 */
router.post('/api/data', async (req: Request, res: Response) => {
  try {
    // 在第一次使用时初始化服务
    initializeServices();
    
    // 使用服务处理请求
    const result = await service.processData(req.body);
    
    res.status(200).json(result);
  } catch (error) {
    res.status(500).json({
      status: 'ERROR',
      message: error instanceof Error ? error.message : String(error),
    });
  }
});

export default router;
