# 深色主题企业级 UI 设计系统

一个专业的深色主题 UI 设计系统，适用于企业级管理后台、数据分析平台、金融系统等场景。

## 快速开始

### 1. 安装依赖

```bash
npm install react react-dom typescript
npm install -D tailwindcss postcss autoprefixer
npm install @tanstack/react-query
```

### 2. 配置 Tailwind CSS

```js
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#3b82f6',
          dark: '#2563eb',
        },
        surface: {
          dark: '#1f1f1f',
          darker: '#1a1a1a',
        },
        border: {
          dark: '#374151',
        },
        text: {
          dark: '#e5e7eb',
          muted: {
            dark: '#9ca3af',
          },
        },
      },
    },
  },
  plugins: [],
}
```

### 3. 创建基础布局

```tsx
// src/components/Layout.tsx
import { ReactNode, useState } from 'react'

interface LayoutProps {
  children: ReactNode
}

export function Layout({ children }: LayoutProps) {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <div className="flex h-screen bg-[#141414]">
      {/* 左侧导航栏 */}
      <aside className={`bg-[#001529] text-white transition-all duration-300 ${
        collapsed ? 'w-20' : 'w-64'
      }`}>
        {/* 导航内容 */}
      </aside>

      {/* 右侧内容区 */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* 顶部导航栏 */}
        <header className="h-16 bg-[#1f1f1f] border-b border-gray-700">
          {/* 顶部内容 */}
        </header>

        {/* 主内容区 */}
        <main className="flex-1 overflow-auto bg-[#141414] p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
```

### 4. 使用组件

```tsx
// src/App.tsx
import { Layout } from './components/Layout'
import { QueryForm } from './components/QueryForm'
import { Table } from './components/Table'

function App() {
  return (
    <Layout>
      <div className="space-y-6">
        <div className="bg-[#1f1f1f] rounded-lg shadow-lg p-6 border border-gray-800">
          <QueryForm onSubmit={handleSubmit} />
        </div>

        <div className="bg-[#1f1f1f] rounded-lg shadow-lg border border-gray-800">
          <div className="p-6">
            <Table columns={columns} data={data} />
          </div>
        </div>
      </div>
    </Layout>
  )
}
```

## 核心组件

### Layout - 主布局

提供左侧导航栏 + 顶部栏 + 主内容区的经典布局。

**特性**：
- 可折叠侧边栏
- 响应式设计
- 深色主题

### QueryForm - 查询表单

横向 4 列布局的查询表单组件。

**特性**：
- 日期选择器
- 下拉选择框
- 文本输入框
- 查询/重置按钮

### Table - 数据表格

功能完整的数据表格组件。

**特性**：
- 自定义列渲染
- 行点击事件
- 加载状态
- 空数据提示
- 悬停高亮

### Button - 按钮

多变体、多尺寸的按钮组件。

**变体**：
- primary: 主按钮
- outline: 边框按钮
- ghost: 透明按钮

## 配色方案

```css
/* 背景色 */
--bg-main: #141414;
--bg-card: #1f1f1f;
--bg-sidebar: #001529;

/* 文字色 */
--text-primary: #e5e7eb;
--text-secondary: #9ca3af;

/* 边框色 */
--border-color: #374151;

/* 主题色 */
--color-primary: #3b82f6;
--color-success: #22c55e;
--color-warning: #eab308;
--color-error: #ef4444;
```

## 组件示例

### 状态标签

```tsx
// 成功状态
<span className="inline-block px-2.5 py-0.5 rounded text-xs font-medium bg-green-600/30 text-green-300 border border-green-500/30">
  成功
</span>

// 失败状态
<span className="inline-block px-2.5 py-0.5 rounded text-xs font-medium bg-red-600/30 text-red-300 border border-red-500/30">
  失败
</span>
```

### 输入框

```tsx
<input
  type="text"
  placeholder="请输入"
  className="w-full px-3 py-2 bg-[#141414] border border-gray-700 rounded text-gray-200 text-sm
           placeholder-gray-600 focus:outline-none focus:border-blue-500 transition-colors"
/>
```

### 卡片

```tsx
<div className="bg-[#1f1f1f] rounded-lg shadow-lg p-6 border border-gray-800">
  {/* 卡片内容 */}
</div>
```

## 响应式设计

使用 Tailwind 的响应式类：

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
  {/* 移动端 1 列，平板 2 列，桌面 4 列 */}
</div>
```

## 最佳实践

1. **保持一致性**：使用统一的配色和间距
2. **响应式优先**：确保在不同设备上都能良好显示
3. **性能优化**：避免不必要的重渲染
4. **可访问性**：添加适当的 aria 标签

## 项目结构

```
src/
├── components/
│   ├── Layout.tsx          # 主布局
│   ├── QueryForm.tsx       # 查询表单
│   ├── Table.tsx           # 数据表格
│   ├── Button.tsx          # 按钮
│   └── index.ts            # 导出
├── pages/
│   └── QueryPage.tsx       # 查询页面
├── api/
│   └── client.ts           # API 客户端
└── App.tsx                 # 应用入口
```

## 常见问题

### Q: 如何自定义主题色？

A: 修改 `tailwind.config.js` 中的 `colors` 配置。

### Q: 如何添加新的组件？

A: 参考现有组件的结构，保持样式一致性。

### Q: 如何处理移动端适配？

A: 使用 Tailwind 的响应式类（sm:, md:, lg:）。

## 许可证

MIT
