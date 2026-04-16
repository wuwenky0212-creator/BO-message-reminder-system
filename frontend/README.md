# 消息提醒功能 - 前端

## 项目结构

```
frontend/
├── src/
│   ├── components/
│   │   ├── BellIcon.vue           # 铃铛图标组件
│   │   └── __tests__/
│   │       └── BellIcon.test.ts   # 单元测试
│   ├── types/
│   │   └── notification.ts        # 类型定义
│   ├── App.vue                    # 主应用组件
│   └── main.ts                    # 应用入口
├── package.json
├── tsconfig.json
├── vite.config.ts
└── vitest.config.ts
```

## 安装依赖

```bash
cd frontend
npm install
```

## 开发

```bash
npm run dev
```

## 构建

```bash
npm run build
```

## 测试

```bash
# 运行测试
npm run test

# 监听模式
npm run test:watch
```

## BellIcon 组件

### 功能特性

1. **红点标识显示**
   - 未读消息数量 > 0 时显示红点
   - 数量 > 99 时显示 "99+"
   - 数量 = 0 时不显示红点

2. **WebSocket 实时推送**
   - 自动连接 WebSocket 服务器
   - 接收实时通知更新
   - 自动重连机制

3. **轮询降级**
   - WebSocket 连接失败时自动降级为轮询
   - 可配置轮询间隔（默认 30 秒）
   - WebSocket 恢复后停止轮询

4. **交互功能**
   - 点击铃铛图标触发 toggle 事件
   - 加载状态时禁用点击
   - 暴露 refresh 方法供外部调用

### Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| refreshInterval | number | 30000 | 轮询间隔（毫秒） |
| enableWebSocket | boolean | true | 是否启用 WebSocket |

### Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| toggle | - | 点击铃铛图标时触发 |
| refresh | - | 手动刷新时触发 |

### 暴露的方法和属性

| 名称 | 类型 | 说明 |
|------|------|------|
| totalUnread | Ref<number> | 未读消息总数 |
| isOpen | Ref<boolean> | 面板是否打开 |
| isLoading | Ref<boolean> | 是否正在加载 |
| wsConnected | Ref<boolean> | WebSocket 是否连接 |
| refresh | Function | 手动刷新通知 |

### 使用示例

```vue
<template>
  <BellIcon 
    :refresh-interval="30000"
    :enable-web-socket="true"
    @toggle="handleToggle"
  />
</template>

<script setup lang="ts">
import BellIcon from '@/components/BellIcon.vue'

const handleToggle = () => {
  console.log('Notification panel toggled')
}
</script>
```

## API 接口

### 获取通知摘要

```
GET /api/v1/notifications/summary
```

**响应示例：**

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
          "lastUpdated": "2024-01-15T14:30:00Z",
          "status": "success",
          "priority": "normal"
        }
      ]
    },
    "totalUnread": 15,
    "lastRefreshTime": "2024-01-15T15:05:00Z"
  }
}
```

## WebSocket 事件

### 连接

```javascript
socket.connect()
```

### 接收通知更新

```javascript
socket.on('notification_update', (data) => {
  console.log('Total unread:', data.totalUnread)
})
```

## 测试覆盖

- ✅ 组件基础结构渲染
- ✅ 红点标识显示逻辑
- ✅ WebSocket 连接和事件处理
- ✅ 轮询降级逻辑
- ✅ 用户交互（点击、禁用状态）
- ✅ 错误处理

## 技术栈

- Vue 3.3+ (Composition API)
- TypeScript 5.0+
- Vite 5.0+
- Vitest 1.0+
- Socket.IO Client 4.7+
- Axios 1.6+
