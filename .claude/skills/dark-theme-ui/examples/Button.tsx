/**
 * 按钮组件示例
 * 
 * 支持多种变体和尺寸的按钮组件
 */

import React from 'react'

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  fullWidth?: boolean
  loading?: boolean
  children: React.ReactNode
}

export function Button({
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  loading = false,
  disabled,
  className = '',
  children,
  ...props
}: ButtonProps) {
  // 基础样式
  const baseStyles = 'inline-flex items-center justify-center font-medium rounded transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[#141414] disabled:opacity-50 disabled:cursor-not-allowed'
  
  // 尺寸样式
  const sizeStyles = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  }
  
  // 变体样式
  const variantStyles = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500',
    outline: 'bg-transparent border-2 border-blue-500 text-blue-500 hover:bg-blue-500 hover:text-white focus:ring-blue-500',
    ghost: 'bg-transparent text-gray-300 hover:bg-gray-700 focus:ring-gray-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
  }
  
  // 宽度样式
  const widthStyles = fullWidth ? 'w-full' : ''
  
  const combinedClassName = `${baseStyles} ${sizeStyles[size]} ${variantStyles[variant]} ${widthStyles} ${className}`
  
  return (
    <button
      className={combinedClassName}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <svg
          className="animate-spin -ml-1 mr-2 h-4 w-4"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      )}
      {children}
    </button>
  )
}

// 使用示例
export function ButtonExample() {
  return (
    <div className="space-y-6 p-6 bg-[#141414]">
      {/* 不同变体 */}
      <div className="space-x-4">
        <Button variant="primary">主要按钮</Button>
        <Button variant="secondary">次要按钮</Button>
        <Button variant="outline">边框按钮</Button>
        <Button variant="ghost">透明按钮</Button>
        <Button variant="danger">危险按钮</Button>
      </div>

      {/* 不同尺寸 */}
      <div className="space-x-4 flex items-center">
        <Button size="sm">小按钮</Button>
        <Button size="md">中等按钮</Button>
        <Button size="lg">大按钮</Button>
      </div>

      {/* 加载状态 */}
      <div className="space-x-4">
        <Button loading>加载中...</Button>
        <Button variant="outline" loading>
          处理中...
        </Button>
      </div>

      {/* 禁用状态 */}
      <div className="space-x-4">
        <Button disabled>禁用按钮</Button>
        <Button variant="outline" disabled>
          禁用边框按钮
        </Button>
      </div>

      {/* 全宽按钮 */}
      <div>
        <Button fullWidth>全宽按钮</Button>
      </div>

      {/* 带图标的按钮 */}
      <div className="space-x-4">
        <Button>
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          添加
        </Button>
        <Button variant="outline">
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          搜索
        </Button>
      </div>
    </div>
  )
}

// 特殊按钮组合
export function ActionButtons() {
  return (
    <div className="flex items-center gap-3">
      <Button 
        className="bg-yellow-500 hover:bg-yellow-600 text-gray-900"
        size="md"
      >
        查询
      </Button>
      <Button variant="outline" className="border-blue-500 text-blue-500 hover:bg-blue-500 hover:text-white">
        重置
      </Button>
    </div>
  )
}