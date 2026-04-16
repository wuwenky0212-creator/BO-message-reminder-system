# 设计文档 - 消息提醒功能

## 1. 系统架构设计

### 1.1 整体架构

RCS消息提醒系统采用前后端分离架构，由以下核心模块组成：

```
┌─────────────────────────────────────────────────────────────┐
│                        前端层 (Vue 3)                        │
├─────────────────────────────────────────────────────────────┤
│  BellIcon组件  │  NotificationPanel组件  │  GlobalDialog组件 │
└─────────────────────────────────────────────────────────────┘
                            ↕ HTTP/WebSocket
┌─────────────────────────────────────────────────────────────┐
│                      后端层 (Python)                         │
├─────────────────────────────────────────────────────────────┤
│  API服务层    │  提醒引擎    │  规则扫描器  │  路由处理器   │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                    定时任务调度器 (APScheduler)              │
├─────────────────────────────────────────────────────────────┤
│  CHK_TRD_004  │  CHK_BO_001  │  CHK_CONF_005  │  CHK_SW_002 │
│  CHK_SETT_006 │  CHK_SEC_003 (15:00 & 16:00)                │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                      数据层 (PostgreSQL)                     │
├─────────────────────────────────────────────────────────────┤
│  Message_Table  │  Rule_Config_Table  │  Task_Execution_Log │
│  Trade_Table    │  Position_Table     │  Confirmation_Table │
│  Payment_Table  │  Settlement_Table   │  Audit_Log          │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 技术栈

**前端技术栈：**
- Vue 3.3+ (Composition API)
- TypeScript 5.0+
- Pinia (状态管理)
- Axios (HTTP客户端)
- Socket.IO Client (WebSocket)
- Element Plus (UI组件库)

**后端技术栈：**
- Python 3.10+
- FastAPI 0.100+ (Web框架)
- SQLAlchemy 2.0+ (ORM)
- APScheduler 3.10+ (定时任务)
- Socket.IO (WebSocket服务)
- Redis 7.0+ (缓存)
- PostgreSQL 14+ (数据库)

### 1.3 模块划分

**1.3.1 提醒引擎 (Notification Engine)**
- 职责：生成提醒消息，写入Message_Table
- 输入：规则扫描结果
- 输出：提醒消息记录

**1.3.2 规则扫描器 (Rule Scanner)**
- 职责：执行定时扫描任务，查询业务数据
- 输入：规则配置、定时触发
- 输出：扫描结果（待处理记录数量）

**1.3.3 路由处理器 (Routing Handler)**
- 职责：处理穿透跳转逻辑
- 输入：规则代码、用户点击事件
- 输出：目标页面路径和过滤参数

**1.3.4 权限过滤器 (Permission Filter)**
- 职责：根据用户权限过滤数据
- 输入：用户ID、机构树权限
- 输出：过滤后的数据查询条件

## 2. 数据库设计

### 2.1 消息表 (message_table)

存储所有提醒消息记录。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| rule_code | VARCHAR(50) | NOT NULL, INDEX | 规则代码 |
| title | VARCHAR(200) | NOT NULL | 提醒标题 |
| count | INT | NOT NULL | 待处理数量 |
| last_updated | TIMESTAMP | NOT NULL | 最后更新时间 |
| status | VARCHAR(20) | NOT NULL | 扫描状态(success/timeout/error) |
| priority | VARCHAR(20) | NOT NULL | 优先级(normal/high/critical) |
| target_roles | JSON | NOT NULL | 目标接收人角色列表 |
| metadata | JSON | NULL | 扩展元数据 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP ON UPDATE | 更新时间 |

**索引设计：**
- PRIMARY KEY (id)
- INDEX idx_rule_code (rule_code)
- INDEX idx_last_updated (last_updated)
- INDEX idx_status (status)

### 2.2 规则配置表 (rule_config_table)

存储提醒规则的配置信息。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| rule_code | VARCHAR(50) | NOT NULL, UNIQUE | 规则代码 |
| rule_name | VARCHAR(200) | NOT NULL | 规则名称 |
| scheduled_time | VARCHAR(10) | NOT NULL | 执行时间(HH:MM) |
| cron_expression | VARCHAR(100) | NOT NULL | Cron表达式 |
| target_roles | JSON | NOT NULL | 接收人角色列表 |
| enabled | BOOLEAN | NOT NULL, DEFAULT TRUE | 是否启用 |
| description | TEXT | NULL | 规则描述 |
| query_sql | TEXT | NOT NULL | 扫描SQL语句 |
| timeout_seconds | INT | NOT NULL, DEFAULT 10 | 查询超时时间(秒) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP ON UPDATE | 更新时间 |
| updated_by | VARCHAR(100) | NULL | 更新人 |

**索引设计：**
- PRIMARY KEY (id)
- UNIQUE INDEX uk_rule_code (rule_code)
- INDEX idx_enabled (enabled)

### 2.3 任务执行日志表 (task_execution_log)

记录每次定时任务的执行情况。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| task_id | VARCHAR(100) | NOT NULL, UNIQUE | 任务唯一标识 |
| rule_code | VARCHAR(50) | NOT NULL, INDEX | 规则代码 |
| rule_name | VARCHAR(200) | NOT NULL | 规则名称 |
| scheduled_time | TIMESTAMP | NOT NULL | 计划执行时间 |
| actual_start_time | TIMESTAMP | NOT NULL | 实际开始时间 |
| actual_end_time | TIMESTAMP | NULL | 实际结束时间 |
| execution_duration | INT | NULL | 执行时长(毫秒) |
| status | VARCHAR(20) | NOT NULL | 执行状态(completed/failed/timeout) |
| record_count | INT | NULL | 扫描到的记录数量 |
| error_message | TEXT | NULL | 错误信息 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 创建时间 |

**索引设计：**
- PRIMARY KEY (id)
- UNIQUE INDEX uk_task_id (task_id)
- INDEX idx_rule_code (rule_code)
- INDEX idx_scheduled_time (scheduled_time)
- INDEX idx_status (status)

### 2.4 审计日志表 (audit_log)

记录提醒处理闭环和敏感数据查询操作。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| log_id | VARCHAR(100) | NOT NULL, UNIQUE | 日志唯一标识 |
| event_type | VARCHAR(50) | NOT NULL, INDEX | 事件类型 |
| rule_code | VARCHAR(50) | NULL, INDEX | 关联的规则代码 |
| user_id | VARCHAR(100) | NOT NULL, INDEX | 操作用户ID |
| user_name | VARCHAR(200) | NOT NULL | 操作用户姓名 |
| operation_type | VARCHAR(50) | NULL | 操作类型 |
| business_id | VARCHAR(100) | NULL | 业务单据ID |
| count_before | INT | NULL | 操作前的提醒数量 |
| count_after | INT | NULL | 操作后的提醒数量 |
| ip_address | VARCHAR(50) | NULL | 用户IP地址 |
| user_agent | VARCHAR(500) | NULL | 用户浏览器信息 |
| timestamp | TIMESTAMP | NOT NULL, INDEX | 操作时间戳 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 创建时间 |

**索引设计：**
- PRIMARY KEY (id)
- UNIQUE INDEX uk_log_id (log_id)
- INDEX idx_event_type (event_type)
- INDEX idx_rule_code (rule_code)
- INDEX idx_user_id (user_id)
- INDEX idx_timestamp (timestamp)

## 3. 后端API设计

### 3.1 提醒总览聚合接口

**接口路径：** `GET /api/v1/notifications/summary`

**请求参数：**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| tab | String | 否 | 标签页类型(message/exception/all)，默认all |
| includeRead | Boolean | 否 | 是否包含已读提醒，默认false |

**请求头：**
```
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**响应格式（成功）：**
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

**错误码：**
- 401: 未授权，Token无效或已过期
- 403: 禁止访问，用户无权限
- 500: 服务器内部错误

### 3.2 预计交收头寸查询接口

**接口路径：** `GET /api/v1/positions/projected_shortfall`

**请求参数：**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| date | String | 是 | 交收日期(T/T+1) |
| portfolio | String | 否 | 投资组合代码 |
| securityType | String | 否 | 证券类型(Stock/Bond/Fund) |
| page | Integer | 否 | 页码，默认1 |
| pageSize | Integer | 否 | 每页记录数，默认50，最大100 |

**响应格式（成功）：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "securityCode": "600000.SH",
        "securityName": "浦发银行",
        "availableBalance": -5000,
        "settlementDate": "T+1",
        "portfolioCode": "PF001",
        "portfolioName": "自营组合1",
        "securityType": "Stock",
        "marketValue": -50000.00,
        "currency": "CNY"
      }
    ],
    "pagination": {
      "page": 1,
      "pageSize": 50,
      "total": 2,
      "totalPages": 1
    },
    "summary": {
      "totalShortfallCount": 2,
      "totalShortfallValue": -80000.00,
      "queryDate": "T+1"
    }
  }
}
```

**错误码：**
- 400: 参数错误，date参数必须为T或T+1
- 401: 未授权
- 403: 禁止访问
- 500: 服务器内部错误

### 3.3 规则配置保存接口

**接口路径：** `POST /api/v1/admin/rules/config`

**请求参数：**
```json
{
  "ruleCode": "CHK_TRD_004",
  "scheduledTime": "14:30",
  "targetRoles": ["BO_Operator", "BO_Supervisor"],
  "enabled": true,
  "description": "交易复核提醒，每日14:30执行"
}
```

**响应格式（成功）：**
```json
{
  "code": 0,
  "message": "配置保存成功，将在下一个定时任务周期生效",
  "data": {
    "ruleCode": "CHK_TRD_004",
    "scheduledTime": "14:30",
    "targetRoles": ["BO_Operator", "BO_Supervisor"],
    "enabled": true,
    "updatedAt": "2024-01-15T15:30:00Z",
    "updatedBy": "admin"
  }
}
```

**错误码：**
- 400: 配置验证失败
- 401: 未授权
- 403: 禁止访问，需要System_Admin权限
- 500: 服务器内部错误

## 4. 前端组件设计

### 4.1 铃铛图标组件 (BellIcon.vue)

**组件职责：**
- 显示铃铛图标和红点标识
- 轮询或接收WebSocket推送更新提醒数量
- 点击展开/收起提醒下拉面板

**组件属性 (Props)：**
```typescript
interface BellIconProps {
  refreshInterval?: number; // 轮询间隔(毫秒)，默认30000
  enableWebSocket?: boolean; // 是否启用WebSocket，默认true
}
```

**组件状态 (State)：**
```typescript
interface BellIconState {
  totalUnread: number; // 未读提醒总数
  isOpen: boolean; // 下拉面板是否打开
  isLoading: boolean; // 是否正在加载
  wsConnected: boolean; // WebSocket是否连接
}
```

**组件事件 (Emits)：**
- `toggle`: 下拉面板打开/关闭事件
- `refresh`: 手动刷新事件

### 4.2 提醒下拉面板组件 (NotificationPanel.vue)

**组件职责：**
- 展示提醒列表（按标签页分类）
- 处理"去处理"按钮点击事件
- 显示超时标识和提示

**组件属性 (Props)：**
```typescript
interface NotificationPanelProps {
  visible: boolean; // 是否显示
  notifications: NotificationItem[]; // 提醒列表
}

interface NotificationItem {
  ruleCode: string;
  title: string;
  count: number;
  lastUpdated: string;
  status: 'success' | 'timeout' | 'error';
  priority: 'normal' | 'high' | 'critical';
}
```

**组件事件 (Emits)：**
- `close`: 关闭面板事件
- `handle`: 点击"去处理"按钮事件，携带ruleCode

### 4.3 全局强制弹窗组件 (GlobalDialog.vue)

**组件职责：**
- 显示券持仓卖空缺口的强制提醒
- 阻断用户当前操作
- 跳转到风险监控看板

**组件属性 (Props)：**
```typescript
interface GlobalDialogProps {
  visible: boolean; // 是否显示
  shortfallData: ShortfallData; // 卖空缺口数据
}

interface ShortfallData {
  totalCount: number; // 总缺口标的数量
  totalValue: number; // 总缺口市值
  topSecurities: Array<{
    securityCode: string;
    securityName: string;
    availableBalance: number;
  }>; // 缺口最大的前3个标的
}
```

**组件事件 (Emits)：**
- `handle`: 点击"去处理"按钮事件

## 5. 定时任务设计

### 5.1 任务配置

使用APScheduler配置6个规则扫描任务：

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = BackgroundScheduler()

# CHK_TRD_004 - 交易复核提醒
scheduler.add_job(
    func=scan_trade_approval,
    trigger=CronTrigger(hour=14, minute=30, day_of_week='mon-fri'),
    id='CHK_TRD_004',
    name='交易复核提醒',
    replace_existing=True
)

# CHK_BO_001 - 未证实匹配
scheduler.add_job(
    func=scan_confirmation_matching,
    trigger=CronTrigger(hour=15, minute=0, day_of_week='mon-fri'),
    id='CHK_BO_001',
    name='未证实匹配',
    replace_existing=True
)

# CHK_CONF_005 - 证实报文未发
scheduler.add_job(
    func=scan_confirmation_message,
    trigger=CronTrigger(hour=15, minute=30, day_of_week='mon-fri'),
    id='CHK_CONF_005',
    name='证实报文未发',
    replace_existing=True
)

# CHK_SW_002 - 收付报文未发（动态计算）
scheduler.add_job(
    func=scan_payment_message,
    trigger=CronTrigger(hour=16, minute=0, day_of_week='mon-fri'),
    id='CHK_SW_002',
    name='收付报文未发',
    replace_existing=True
)

# CHK_SETT_006 - 收付报文清算审批
scheduler.add_job(
    func=scan_settlement_approval,
    trigger=CronTrigger(hour=16, minute=0, day_of_week='mon-fri'),
    id='CHK_SETT_006',
    name='收付报文清算审批',
    replace_existing=True
)

# CHK_SEC_003 - 券持仓卖空预警（15:00）
scheduler.add_job(
    func=scan_position_shortfall,
    trigger=CronTrigger(hour=15, minute=0, day_of_week='mon-fri'),
    id='CHK_SEC_003_15',
    name='券持仓卖空预警(15:00)',
    replace_existing=True
)

# CHK_SEC_003 - 券持仓卖空预警（16:00，触发弹窗）
scheduler.add_job(
    func=scan_position_shortfall_with_popup,
    trigger=CronTrigger(hour=16, minute=0, day_of_week='mon-fri'),
    id='CHK_SEC_003_16',
    name='券持仓卖空预警(16:00)',
    replace_existing=True
)

scheduler.start()
```

### 5.2 任务执行流程

```
开始
  ↓
读取规则配置
  ↓
生成任务ID
  ↓
记录任务开始日志
  ↓
执行数据库查询（带超时控制）
  ↓
查询成功？
  ├─ 是 → 统计记录数量
  │        ↓
  │      生成提醒消息
  │        ↓
  │      写入Message_Table
  │        ↓
  │      WebSocket推送
  │        ↓
  │      记录成功日志
  │
  └─ 否 → 记录错误日志
           ↓
         重试机制（下一周期）
           ↓
         发送告警（连续3次失败）
  ↓
结束
```

## 6. 核心算法设计

### 6.1 规则扫描算法

```python
def scan_rule(rule_code: str, user_context: UserContext) -> ScanResult:
    """
    执行规则扫描
    
    Args:
        rule_code: 规则代码
        user_context: 用户上下文（权限信息）
    
    Returns:
        ScanResult: 扫描结果
    """
    # 1. 读取规则配置
    rule_config = get_rule_config(rule_code)
    
    # 2. 构建查询条件（包含权限过滤）
    query_conditions = build_query_conditions(
        rule_config.query_sql,
        user_context.org_ids
    )
    
    # 3. 执行查询（带超时控制）
    try:
        with timeout(rule_config.timeout_seconds):
            result = execute_query(query_conditions)
            record_count = result.count()
    except TimeoutException:
        return ScanResult(
            status='timeout',
            count=-1,
            error_message='Query execution timeout'
        )
    
    # 4. 返回扫描结果
    return ScanResult(
        status='success',
        count=record_count,
        data=result
    )
```

### 6.2 权限过滤算法

```python
def apply_permission_filter(
    query: Query,
    user_context: UserContext,
    table_name: str
) -> Query:
    """
    应用权限过滤
    
    Args:
        query: 原始查询
        user_context: 用户上下文
        table_name: 表名
    
    Returns:
        Query: 过滤后的查询
    """
    # 1. 获取用户有权访问的机构ID列表
    authorized_org_ids = user_context.org_ids
    
    # 2. 添加机构ID过滤条件
    query = query.filter(
        getattr(table_name, 'org_id').in_(authorized_org_ids)
    )
    
    # 3. 如果是投资组合相关表，添加组合权限过滤
    if hasattr(table_name, 'portfolio_id'):
        authorized_portfolio_ids = user_context.portfolio_ids
        query = query.filter(
            getattr(table_name, 'portfolio_id').in_(authorized_portfolio_ids)
        )
    
    return query
```

### 6.3 提醒数量实时更新算法

```python
def update_notification_count(
    rule_code: str,
    operation: str,
    business_id: str,
    user_id: str
) -> None:
    """
    更新提醒数量
    
    Args:
        rule_code: 规则代码
        operation: 操作类型（approval/matching/sending等）
        business_id: 业务单据ID
        user_id: 操作用户ID
    """
    # 1. 查询当前提醒记录
    notification = get_notification_by_rule_code(rule_code)
    
    # 2. 记录操作前的数量
    count_before = notification.count
    
    # 3. 更新数量（原子操作）
    with db.transaction():
        notification.count = max(0, notification.count - 1)
        notification.last_updated = datetime.now()
        db.session.commit()
    
    # 4. 记录审计日志
    create_audit_log(
        event_type=f'{operation}_completed',
        rule_code=rule_code,
        user_id=user_id,
        business_id=business_id,
        count_before=count_before,
        count_after=notification.count
    )
    
    # 5. WebSocket推送更新
    push_notification_update(
        rule_code=rule_code,
        count=notification.count,
        last_updated=notification.last_updated
    )
```

## 7. 安全设计

### 7.1 权限控制

**机构树权限模型：**
- 用户登录时，从JWT Token解析用户所属机构ID列表
- 机构树支持继承关系，上级机构可查看下级机构数据
- 所有数据查询必须在SQL层面应用机构ID过滤

**审批权限控制：**
- 清算审批功能需要验证用户是否具有审批权限
- 权限验证在API层面进行，返回403错误如果无权限

### 7.2 数据脱敏规则

**敏感字段识别：**
- 金额字段：amount, balance, market_value
- 账号字段：account_no, bank_account
- 客户信息：client_name, client_id

**脱敏策略：**
- 金额：显示为"***"
- 账号：只显示后4位，如"622202******7890"
- 客户名称：只显示姓氏，如"张*"

### 7.3 审计日志记录

**记录范围：**
- 所有提醒处理操作（复核、匹配、发报、审批）
- 所有敏感数据查询操作
- 所有规则配置变更操作

**日志内容：**
- 操作时间、操作用户、操作类型
- 业务单据ID、操作前后状态
- IP地址、User Agent

## 8. 性能优化设计

### 8.1 数据库查询优化

**索引设计原则：**
- 为所有WHERE条件字段创建索引
- 为JOIN关联字段创建索引
- 为ORDER BY排序字段创建索引
- 避免在索引字段上使用函数

**查询优化策略：**
- 使用EXPLAIN分析查询计划
- 避免SELECT *，只查询需要的字段
- 使用分页查询，避免一次性加载大量数据
- 使用COUNT(1)代替COUNT(*)

### 8.2 缓存策略

**Redis缓存设计：**
- 缓存提醒总览数据，TTL=30秒
- 缓存规则配置数据，TTL=5分钟
- 缓存用户权限数据，TTL=10分钟

**缓存更新策略：**
- 提醒数量变化时，主动失效缓存
- 规则配置变更时，主动失效缓存
- 使用Redis Pub/Sub通知所有节点更新缓存

### 8.3 WebSocket连接管理

**连接池设计：**
- 每个用户维护一个WebSocket连接
- 连接空闲超过5分钟自动断开
- 断开后前端自动重连

**消息推送优化：**
- 批量推送：合并多个提醒更新为一条消息
- 按用户权限过滤：只推送用户有权查看的提醒
- 消息压缩：使用MessagePack压缩消息体

### 8.4 降级策略

**WebSocket降级：**
- WebSocket连接失败时，自动切换为HTTP轮询
- 轮询间隔：30秒
- 前端显示提示："实时推送已断开，切换为定时刷新模式"

**查询超时降级：**
- 查询超时时，显示超时标识"(!)"
- 提示用户："统计超时，请进入对应管理页面手动刷新"
- 下一个周期自动重试

**数据库连接池耗尽降级：**
- 返回503错误
- 前端显示友好提示："系统繁忙，请稍后重试"
- 记录错误日志，发送告警
