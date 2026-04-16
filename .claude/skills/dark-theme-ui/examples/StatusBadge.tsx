/**
 * 状态标签组件示例
 * 
 * 用于显示各种状态的彩色标签
 */

export type BadgeVariant = 
  | 'success' 
  | 'error' 
  | 'warning' 
  | 'info' 
  | 'primary'
  | 'secondary'

interface StatusBadgeProps {
  variant: BadgeVariant
  children: React.ReactNode
}

export function StatusBadge({ variant, children }: StatusBadgeProps) {
  const variantStyles = {
    success: 'bg-green-600/30 text-green-300 border border-green-500/30',
    error: 'bg-red-600/30 text-red-300 border border-red-500/30',
    warning: 'bg-yellow-600/30 text-yellow-300 border border-yellow-500/30',
    info: 'bg-blue-600/30 text-blue-300 border border-blue-500/30',
    primary: 'bg-purple-600/30 text-purple-300 border border-purple-500/30',
    secondary: 'bg-gray-600/30 text-gray-300 border border-gray-500/30',
  }

  return (
    <span className={`inline-block px-2.5 py-0.5 rounded text-xs font-medium ${variantStyles[variant]}`}>
      {children}
    </span>
  )
}

// 使用示例
export function StatusBadgeExample() {
  return (
    <div className="space-y-4 p-6 bg-[#141414]">
      <div className="space-x-2">
        <StatusBadge variant="success">成功</StatusBadge>
        <StatusBadge variant="error">失败</StatusBadge>
        <StatusBadge variant="warning">警告</StatusBadge>
        <StatusBadge variant="info">信息</StatusBadge>
        <StatusBadge variant="primary">主要</StatusBadge>
        <StatusBadge variant="secondary">次要</StatusBadge>
      </div>

      <div className="space-x-2">
        <StatusBadge variant="success">已完成</StatusBadge>
        <StatusBadge variant="info">进行中</StatusBadge>
        <StatusBadge variant="warning">待处理</StatusBadge>
        <StatusBadge variant="error">已取消</StatusBadge>
      </div>

      <div className="space-x-2">
        <StatusBadge variant="success">在线</StatusBadge>
        <StatusBadge variant="secondary">离线</StatusBadge>
        <StatusBadge variant="warning">忙碌</StatusBadge>
      </div>
    </div>
  )
}

// 操作类型标签
export function OperationTypeBadge({ type }: { type: string }) {
  const typeConfig: Record<string, { label: string; variant: BadgeVariant }> = {
    QUERY: { label: '查询', variant: 'info' },
    CREATE: { label: '创建', variant: 'success' },
    MODIFY: { label: '修改', variant: 'warning' },
    DELETE: { label: '删除', variant: 'error' },
    PROCESS: { label: '处理', variant: 'primary' },
    CANCEL: { label: '取消', variant: 'secondary' },
  }

  const config = typeConfig[type] || { label: type, variant: 'secondary' }

  return <StatusBadge variant={config.variant}>{config.label}</StatusBadge>
}
