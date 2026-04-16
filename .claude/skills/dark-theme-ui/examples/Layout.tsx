/**
 * 主布局组件示例
 * 
 * 提供左侧导航栏 + 顶部栏 + 主内容区的经典布局
 */

import { ReactNode, useState } from 'react'

interface LayoutProps {
  children: ReactNode
}

export function Layout({ children }: LayoutProps) {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <div className="flex h-screen bg-[#141414]">
      {/* 左侧导航栏 */}
      <aside
        className={`bg-[#001529] text-white transition-all duration-300 ${
          collapsed ? 'w-20' : 'w-64'
        } flex flex-col`}
      >
        {/* Logo 区域 */}
        <div className="h-16 flex items-center justify-center border-b border-gray-700 px-4">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-500 rounded flex items-center justify-center flex-shrink-0">
              <span className="text-white font-bold">资</span>
            </div>
            {!collapsed && (
              <span className="text-base font-semibold whitespace-nowrap">
                资金风险管理系统
              </span>
            )}
          </div>
        </div>

        {/* 菜单项 */}
        <nav className="flex-1 py-4">
          <ul className="space-y-1">
            <li>
              <a
                href="#"
                className="flex items-center px-6 py-3 text-gray-300 hover:bg-blue-600 hover:text-white transition-colors"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
                  />
                </svg>
                {!collapsed && <span className="ml-3">后线工作台</span>}
              </a>
            </li>

            <li>
              <a
                href="#"
                className="flex items-center px-6 py-3 text-white bg-blue-600"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
                {!collapsed && <span className="ml-3">查询管理</span>}
              </a>
            </li>
          </ul>
        </nav>

        {/* 折叠按钮 */}
        <div className="border-t border-gray-700 p-4">
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="w-full flex items-center justify-center py-2 text-gray-300 hover:text-white transition-colors"
          >
            <svg
              className={`w-5 h-5 transition-transform ${
                collapsed ? 'rotate-180' : ''
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M11 19l-7-7 7-7m8 14l-7-7 7-7"
              />
            </svg>
          </button>
        </div>
      </aside>

      {/* 右侧内容区 */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* 顶部导航栏 */}
        <header className="h-16 bg-[#1f1f1f] border-b border-gray-700 flex items-center justify-between px-6">
          <div className="flex items-center space-x-4">
            <h2 className="text-lg font-semibold text-gray-200">查询表格</h2>
          </div>
          <div className="flex items-center space-x-4">
            <button className="text-gray-400 hover:text-gray-200">
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                />
              </svg>
            </button>
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                <span className="text-white text-sm">U</span>
              </div>
              <span className="text-sm text-gray-300">USER001</span>
            </div>
          </div>
        </header>

        {/* 主内容区 */}
        <main className="flex-1 overflow-auto bg-[#141414] p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
