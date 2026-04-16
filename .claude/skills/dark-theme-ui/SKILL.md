# 深色主题企业级 UI 设计系统

## 概述

这是一个专业的深色主题 UI 设计系统，适用于企业级管理后台、数据分析平台、金融系统等场景。设计风格参考 Ant Design Pro，提供完整的布局、组件和交互模式。

## 核心特性

- **深色主题配色**：专业的深色背景，减少视觉疲劳
- **左侧导航布局**：经典的侧边栏 + 主内容区布局
- **响应式设计**：支持桌面端和移动端
- **完整组件库**：表格、表单、按钮、卡片等常用组件
- **交互友好**：悬停效果、过渡动画、加载状态

## 设计规范

### 配色方案

```
主背景色：#141414 (深灰黑)
卡片背景：#1f1f1f (浅灰黑)
侧边栏背景：#001529 (深蓝黑)
边框颜色：#374151 (gray-700)
主文字：#e5e7eb (gray-200)
次要文字：#9ca3af (gray-400)
主题色：#3b82f6 (blue-500)
强调色：#eab308 (yellow-500)
成功色：#22c55e (green-500)
错误色：#ef4444 (red-500)
```

### 间距规范

```
卡片内边距：24px (p-6)
表单间距：16px (gap-4)
组件间距：24px (space-y-6)
按钮内边距：8px 32px (px-8 py-2)
```

### 圆角规范

```
卡片圆角：8px (rounded-lg)
按钮圆角：6px (rounded)
输入框圆角：4px (rounded)
表格圆角：12px (rounded-xl)
```

## 布局结构

### 主布局

```
┌─────────────────────────────────────────┐
│  左侧导航栏  │      顶部导航栏          │
│  (侧边栏)    │                          │
│             ├──────────────────────────┤
│             │                          │
│             │      主内容区            │
│             │                          │
│             │                          │
└─────────────────────────────────────────┘
```

### 左侧导航栏

- 宽度：256px (展开) / 80px (折叠)
- 背景色：#001529
- Logo 区域：64px 高度
- 菜单项：48px 高度
- 悬停效果：蓝色背景 (#3b82f6)
- 当前选中：蓝色背景 + 白色文字

### 顶部导航栏

- 高度：64px
- 背景色：#1f1f1f
- 左侧：页面标题
- 右侧：通知、用户信息

### 主内容区

- 背景色：#141414
- 内边距：24px
- 卡片间距：24px

## 核心组件

### 1. 查询表单 (QueryForm)

**特点**：
- 横向 4 列布局
- 深色输入框背景 (#141414)
- 灰色边框 (border-gray-700)
- 蓝色聚焦边框
- 黄色查询按钮
- 蓝色边框重置按钮

**使用场景**：
- 数据查询页面
- 筛选条件表单
- 高级搜索

### 2. 数据表格 (Table)

**特点**：
- 深色表头背景
- 悬停行高亮
- 状态标签（带边框的彩色标签）
- 分页组件
- 响应式设计

**列配置**：
```typescript
{
  key: 'fieldName',
  header: '列标题',
  width: '120px',
  align: 'center',
  render: (value) => <CustomComponent />
}
```

### 3. 按钮 (Button)

**变体**：
- `primary`: 蓝色主按钮
- `outline`: 边框按钮
- `ghost`: 透明按钮

**尺寸**：
- `sm`: 小按钮
- `md`: 中等按钮
- `lg`: 大按钮

### 4. 卡片 (Card)

**特点**：
- 背景色：#1f1f1f
- 边框：border-gray-800
- 圆角：rounded-lg
- 阴影：shadow-lg

## 状态标签设计

### 样式规范

```typescript
// 带边框的半透明背景
bg-{color}-600/30 text-{color}-300 border border-{color}-500/30
```

### 颜色映射

```
查询：蓝色 (blue)
创建：绿色 (green)
修改：黄色 (yellow)
删除：红色 (red)
处理：紫色 (purple)
取消：灰色 (gray)
成功：绿色 (green)
失败：红色 (red)
```

## 交互规范

### 悬停效果

- 按钮：背景色加深 + 阴影增强
- 表格行：背景色变为 #1a1a1a
- 菜单项：背景色变为蓝色

### 过渡动画

```css
transition-colors duration-200
transition-all duration-300
```

### 加载状态

- 旋转图标
- 禁用交互
- 文字提示

## 响应式设计

### 断点

```
sm: 640px
md: 768px
lg: 1024px
xl: 1280px
```

### 移动端适配

- 表格转为卡片视图
- 导航栏可折叠
- 表单改为单列布局

## 使用示例

### 完整页面结构

```tsx
import { Layout } from './components/Layout'
import { QueryForm } from './components/QueryForm'
import { Table } from './components/Table'

function Page() {
  return (
    <Layout>
      <div className="space-y-6">
        {/* 查询表单卡片 */}
        <div className="bg-[#1f1f1f] rounded-lg shadow-lg p-6 border border-gray-800">
          <QueryForm onSubmit={handleSubmit} />
        </div>

        {/* 结果表格卡片 */}
        <div className="bg-[#1f1f1f] rounded-lg shadow-lg border border-gray-800">
          <div className="p-6">
            <Table
              columns={columns}
              data={data}
              keyExtractor={(row) => row.id}
              onRowClick={handleRowClick}
            />
          </div>
        </div>
      </div>
    </Layout>
  )
}
```

### 表单输入框

```tsx
<input
  type="text"
  placeholder="请输入"
  className="w-full px-3 py-2 bg-[#141414] border border-gray-700 rounded text-gray-200 text-sm
           placeholder-gray-600 focus:outline-none focus:border-blue-500 transition-colors"
/>
```

### 下拉选择框

```tsx
<select
  className="w-full px-3 py-2 bg-[#141414] border border-gray-700 rounded text-gray-200 text-sm
           focus:outline-none focus:border-blue-500 transition-colors"
>
  <option value="">请选择</option>
  <option value="option1">选项1</option>
</select>
```

### 状态标签

```tsx
<span className="inline-block px-2.5 py-0.5 rounded text-xs font-medium bg-green-600/30 text-green-300 border border-green-500/30">
  成功
</span>
```

## 最佳实践

### 1. 保持一致性

- 使用统一的配色方案
- 遵循间距规范
- 保持组件样式一致

### 2. 注重可访问性

- 提供足够的颜色对比度
- 添加 aria 标签
- 支持键盘导航

### 3. 性能优化

- 使用 CSS 变量
- 避免过度动画
- 懒加载大型组件

### 4. 响应式优先

- 移动端优先设计
- 使用 Tailwind 响应式类
- 测试不同屏幕尺寸

## 常见场景

### 数据查询页面

1. 顶部查询表单（横向布局）
2. 中间结果表格（带分页）
3. 底部操作按钮（导出等）

### 详情页面

1. 顶部面包屑导航
2. 信息卡片（分组展示）
3. 底部操作按钮

### 表单页面

1. 分步表单（多步骤）
2. 表单验证提示
3. 提交/取消按钮

## 技术栈

- React 18+
- TypeScript
- Tailwind CSS 3+
- React Query (数据获取)

## 浏览器支持

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 相关资源

- [Ant Design Pro](https://pro.ant.design/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Headless UI](https://headlessui.com/)
