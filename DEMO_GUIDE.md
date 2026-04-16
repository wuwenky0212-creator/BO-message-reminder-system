# RCS 消息提醒系统 - 演示指南

## 🎉 服务已启动

### 后端服务 (Demo Mode)
- **URL**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **状态**: ✅ 运行中

### 前端服务
- **URL**: http://localhost:5173
- **状态**: ✅ 运行中

---

## 📱 功能预览

### 1. 铃铛图标 (BellIcon)
访问 http://localhost:5173 可以看到：
- 右上角的铃铛图标
- 红色数字徽章显示未读通知数量
- 每 30 秒自动刷新通知数据
- 点击铃铛可触发面板切换事件

### 2. 实时数据更新
- 后端模拟数据会随机变化，模拟真实场景
- 前端自动轮询获取最新数据
- WebSocket 连接失败时自动降级到轮询模式

### 3. 可用的 API 端点

#### 获取通知摘要
```bash
GET http://localhost:8000/api/v1/notifications/summary
```

**查询参数**:
- `tab`: message/exception/all (默认: all)
- `includeRead`: true/false (默认: false)

**示例响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "tabs": {
      "message": [],
      "exception": [
        {
          "ruleCode": "CHK_TRD_004",
          "title": "当日交易未复核",
          "count": 15,
          "lastUpdated": "2026-04-16T13:30:00Z",
          "status": "success",
          "priority": "high"
        }
      ]
    },
    "totalUnread": 28,
    "lastRefreshTime": "2026-04-16T13:30:00Z"
  }
}
```

#### 查询预计交收缺口
```bash
GET http://localhost:8000/api/v1/positions/projected_shortfall?date=T+1
```

**查询参数**:
- `date`: T/T+1 (必填)
- `portfolio`: 组合代码 (可选)
- `securityType`: Stock/Bond/Fund (可选)
- `page`: 页码 (默认: 1)
- `pageSize`: 每页大小 (默认: 50)

---

## 🔧 技术特性

### 前端
- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **HTTP 客户端**: Axios
- **WebSocket**: Socket.IO Client
- **自动降级**: WebSocket 失败时自动切换到轮询

### 后端 (Demo Mode)
- **框架**: FastAPI
- **CORS**: 已配置允许跨域
- **模拟数据**: 随机变化的通知数据
- **无依赖**: 不需要数据库或 Redis

---

## 🎨 UI 特性

### 铃铛图标
- SVG 矢量图标，清晰锐利
- 红色徽章显示未读数量
- 超过 99 显示为 "99+"
- 加载状态时禁用点击
- Hover 效果

### 响应式设计
- 适配不同屏幕尺寸
- 流畅的动画效果
- 无障碍支持 (aria-label)

---

## 📊 模拟数据

### 通知类型
1. **CHK_TRD_004**: 当日交易未复核 (高优先级)
2. **CHK_POS_001**: 预计交收缺口 (严重)
3. **CHK_RISK_002**: 风险指标超限 (普通)
4. **CHK_SETTLE_003**: 交收失败记录 (高优先级)

### 持仓缺口
- 浦发银行 (600000.SH): -5000 股
- 平安银行 (000001.SZ): -3000 股
- 中国平安 (601318.SH): -2000 股

---

## 🛑 停止服务

如需停止服务，在终端中按 `Ctrl+C`

---

## 📝 注意事项

1. **Demo 模式**: 当前使用模拟数据，不连接真实数据库
2. **WebSocket**: Demo 服务器未实现 WebSocket，前端会自动降级到轮询
3. **数据变化**: 每次请求通知数据时，数量会随机变化 ±2，模拟真实场景
4. **端口占用**: 确保 8000 和 5173 端口未被占用

---

## 🚀 下一步

要使用完整功能（包括数据库、Redis、WebSocket 推送），需要：
1. 安装 PostgreSQL 数据库
2. 安装 Redis 缓存服务
3. 配置环境变量
4. 运行数据库迁移
5. 使用 `python backend/main.py` 启动完整后端

当前 Demo 模式已足够预览前端效果和 API 交互。
