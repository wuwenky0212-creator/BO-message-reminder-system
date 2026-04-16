/**
 * 数据表格组件示例
 * 
 * 功能完整的深色主题表格，支持自定义列、行点击、加载状态等
 */

import React from 'react'

export interface Column<T> {
  key: string
  header: string
  render?: (value: unknown, row: T, index: number) => React.ReactNode
  width?: string
  align?: 'left' | 'center' | 'right'
}

export interface TableProps<T> {
  columns: Column<T>[]
  data: T[]
  keyExtractor: (row: T, index: number) => string | number
  onRowClick?: (row: T, index: number) => void
  loading?: boolean
  emptyMessage?: string
}

export function Table<T>({
  columns,
  data,
  keyExtractor,
  onRowClick,
  loading = false,
  emptyMessage = '暂无数据',
}: TableProps<T>) {
  const getCellValue = (row: T, column: Column<T>) => {
    const keys = column.key.split('.')
    let value: unknown = row
    
    for (const key of keys) {
      if (value && typeof value === 'object' && key in value) {
        value = (value as Record<string, unknown>)[key]
      } else {
        return undefined
      }
    }
    
    return value
  }
  
  const renderCell = (row: T, column: Column<T>, rowIndex: number) => {
    const value = getCellValue(row, column)
    
    if (column.render) {
      return column.render(value, row, rowIndex)
    }
    
    if (value === null || value === undefined) {
      return <span className="text-gray-500">-</span>
    }
    
    return String(value)
  }
  
  const getAlignClass = (align?: 'left' | 'center' | 'right') => {
    switch (align) {
      case 'center':
        return 'text-center'
      case 'right':
        return 'text-right'
      default:
        return 'text-left'
    }
  }
  
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        <span className="ml-4 text-gray-400">加载中...</span>
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-400 text-lg">{emptyMessage}</div>
      </div>
    )
  }
  
  return (
    <div className="w-full overflow-hidden rounded-xl">
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-[#001529]">
              {columns.map((column) => (
                <th
                  key={column.key}
                  className={`px-6 py-4 text-left text-sm font-semibold text-white ${getAlignClass(column.align)}`}
                  style={{ width: column.width }}
                >
                  {column.header}
                </th>
              ))}
            </tr>
          </thead>
          
          <tbody className="bg-[#1f1f1f]">
            {data.map((row, rowIndex) => (
              <tr
                key={keyExtractor(row, rowIndex)}
                className="border-b border-gray-800 last:border-b-0 hover:bg-[#1a1a1a] cursor-pointer transition-colors"
                onClick={() => onRowClick?.(row, rowIndex)}
              >
                {columns.map((column) => (
                  <td
                    key={column.key}
                    className={`px-6 py-4 text-gray-200 text-sm ${getAlignClass(column.align)}`}
                  >
                    {renderCell(row, column, rowIndex) as React.ReactNode}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

// 使用示例
export function TableExample() {
  interface LogData {
    id: string
    time: string
    user: string
    action: string
    status: 'success' | 'failed'
  }

  const columns: Column<LogData>[] = [
    {
      key: 'time',
      header: '操作时间',
      width: '180px',
    },
    {
      key: 'user',
      header: '用户',
      width: '120px',
    },
    {
      key: 'action',
      header: '操作',
      width: '150px',
    },
    {
      key: 'status',
      header: '状态',
      width: '100px',
      align: 'center',
      render: (value) => (
        <span
          className={`inline-block px-2.5 py-0.5 rounded text-xs font-medium ${
            value === 'success'
              ? 'bg-green-600/30 text-green-300 border border-green-500/30'
              : 'bg-red-600/30 text-red-300 border border-red-500/30'
          }`}
        >
          {value === 'success' ? '成功' : '失败'}
        </span>
      ),
    },
  ]

  const data: LogData[] = [
    {
      id: '1',
      time: '2024-03-15 10:30:00',
      user: 'USER001',
      action: '查询数据',
      status: 'success',
    },
    {
      id: '2',
      time: '2024-03-15 10:31:00',
      user: 'USER002',
      action: '修改配置',
      status: 'failed',
    },
  ]

  return (
    <Table
      columns={columns}
      data={data}
      keyExtractor={(row) => row.id}
      onRowClick={(row) => console.log('点击行:', row)}
    />
  )
}
