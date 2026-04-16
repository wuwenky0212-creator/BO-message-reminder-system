/**
 * 完整页面示例
 * 
 * 展示如何组合所有组件创建一个完整的深色主题页面
 */

import React, { useState } from 'react'
import { Layout } from './Layout'
import { QueryForm, QueryFormData } from './QueryForm'
import { Table, Column } from './Table'
import { Card, CardWithHeader, StatCard } from './Card'
import { Button } from './Button'
import { StatusBadge } from './StatusBadge'
import { Pagination } from './Pagination'

// 模拟数据类型
interface LogRecord {
  id: string
  operationTime: string
  employeeId: string
  moduleName: string
  operationType: string
  tradeReference?: string
  operationResult: 'SUCCESS' | 'FAILED'
  abnormalFlag: boolean
}

// 模拟数据
const mockData: LogRecord[] = [
  {
    id: '1',
    operationTime: '2024-03-15 10:30:00',
    employeeId: 'EMP001',
    moduleName: '交易管理',
    operationType: 'QUERY',
    tradeReference: 'TXN20240315001',
    operationResult: 'SUCCESS',
    abnormalFlag: false,
  },
  {
    id: '2',
    operationTime: '2024-03-15 10:31:15',
    employeeId: 'EMP002',
    moduleName: '支付处理',
    operationType: 'PROCESS',
    tradeReference: 'TXN20240315002',
    operationResult: 'FAILED',
    abnormalFlag: true,
  },
  {
    id: '3',
    operationTime: '2024-03-15 10:32:30',
    employeeId: 'EMP001',
    moduleName: '账户管理',
    operationType: 'MODIFY',
    tradeReference: 'TXN20240315003',
    operationResult: 'SUCCESS',
    abnormalFlag: false,
  },
  {
    id: '4',
    operationTime: '2024-03-15 10:33:45',
    employeeId: 'EMP003',
    moduleName: '风险控制',
    operationType: 'CREATE',
    operationResult: 'SUCCESS',
    abnormalFlag: false,
  },
  {
    id: '5',
    operationTime: '2024-03-15 10:35:00',
    employeeId: 'EMP002',
    moduleName: '交易管理',
    operationType: 'DELETE',
    tradeReference: 'TXN20240315005',
    operationResult: 'FAILED',
    abnormalFlag: true,
  },
]

export function CompleteExample() {
  const [data, setData] = useState<LogRecord[]>(mockData)
  const [filteredData, setFilteredData] = useState<LogRecord[]>(mockData)
  const [loading, setLoading] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [selectedRecord, setSelectedRecord] = useState<LogRecord | null>(null)

  // 表格列配置
  const columns: Column<LogRecord>[] = [
    {
      key: 'operationTime',
      header: '操作时间',
      width: '160px',
      render: (value) => (
        <span className="font-mono text-sm text-gray-300">{String(value)}</span>
      ),
    },
    {
      key: 'employeeId',
      header: '员工编号',
      width: '110px',
      render: (value) => (
        <span className="font-mono text-sm text-gray-300">{String(value)}</span>
      ),
    },
    {
      key: 'moduleName',
      header: '操作模块',
      width: '130px',
      render: (value) => (
        <span className="text-sm text-gray-200">{String(value)}</span>
      ),
    },
    {
      key: 'operationType',
      header: '操作类型',
      width: '110px',
      align: 'center',
      render: (value) => {
        const typeConfig: Record<string, { label: string; variant: any }> = {
          QUERY: { label: '查询', variant: 'info' },
          CREATE: { label: '创建', variant: 'success' },
          MODIFY: { label: '修改', variant: 'warning' },
          DELETE: { label: '删除', variant: 'error' },
          PROCESS: { label: '处理', variant: 'primary' },
        }
        
        const config = typeConfig[value as string] || { label: String(value), variant: 'secondary' }
        
        return <StatusBadge variant={config.variant}>{config.label}</StatusBadge>
      },
    },
    {
      key: 'tradeReference',
      header: '交易编号',
      width: '130px',
      render: (value) => (
        <span className="font-mono text-sm text-gray-300">{value ? String(value) : '-'}</span>
      ),
    },
    {
      key: 'operationResult',
      header: '操作结果',
      width: '100px',
      align: 'center',
      render: (value) => (
        <StatusBadge variant={value === 'SUCCESS' ? 'success' : 'error'}>
          {value === 'SUCCESS' ? '成功' : '失败'}
        </StatusBadge>
      ),
    },
    {
      key: 'abnormalFlag',
      header: '异常',
      width: '70px',
      align: 'center',
      render: (value) =>
        value ? (
          <span className="text-yellow-400 text-lg" title="异常操作">
            ⚠
          </span>
        ) : (
          <span className="text-gray-600">-</span>
        ),
    },
  ]

  // 处理查询
  const handleQuery = async (formData: QueryFormData) => {
    setLoading(true)
    
    // 模拟 API 调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 简单的过滤逻辑
    let filtered = mockData
    
    if (formData.employeeId) {
      filtered = filtered.filter(item => 
        item.employeeId.toLowerCase().includes(formData.employeeId!.toLowerCase())
      )
    }
    
    if (formData.moduleName) {
      filtered = filtered.filter(item => item.moduleName === formData.moduleName)
    }
    
    if (formData.operationType) {
      filtered = filtered.filter(item => item.operationType === formData.operationType)
    }
    
    setFilteredData(filtered)
    setCurrentPage(1)
    setLoading(false)
  }

  // 处理行点击
  const handleRowClick = (record: LogRecord) => {
    setSelectedRecord(record)
    console.log('选中记录:', record)
  }

  // 计算统计数据
  const totalRecords = filteredData.length
  const successCount = filteredData.filter(item => item.operationResult === 'SUCCESS').length
  const failedCount = filteredData.filter(item => item.operationResult === 'FAILED').length
  const abnormalCount = filteredData.filter(item => item.abnormalFlag).length
  const successRate = totalRecords > 0 ? ((successCount / totalRecords) * 100).toFixed(1) : '0'

  // 分页数据
  const totalPages = Math.ceil(totalRecords / pageSize)
  const startIndex = (currentPage - 1) * pageSize
  const endIndex = startIndex + pageSize
  const currentData = filteredData.slice(startIndex, endIndex)

  return (
    <Layout>
      <div className="space-y-6">
        {/* 统计卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="总记录数"
            value={totalRecords}
            change={{ value: "+12%", type: "increase" }}
            icon={
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            }
          />
          <StatCard
            title="成功操作"
            value={successCount}
            change={{ value: `${successRate}%`, type: "neutral" }}
            icon={
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            }
          />
          <StatCard
            title="失败操作"
            value={failedCount}
            change={{ value: "-5%", type: "decrease" }}
            icon={
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            }
          />
          <StatCard
            title="异常操作"
            value={abnormalCount}
            change={{ value: "警告", type: "increase" }}
            icon={
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            }
          />
        </div>

        {/* 查询表单 */}
        <Card>
          <QueryForm onSubmit={handleQuery} loading={loading} />
        </Card>

        {/* 数据表格 */}
        <CardWithHeader
          title="查询结果"
          subtitle={`共找到 ${totalRecords} 条记录`}
          action={
            <div className="flex gap-2">
              <Button variant="outline" size="sm">
                导出 Excel
              </Button>
              <Button variant="outline" size="sm">
                导出 CSV
              </Button>
            </div>
          }
        >
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
              <span className="ml-4 text-gray-400">加载中...</span>
            </div>
          ) : (
            <>
              <Table
                columns={columns}
                data={currentData}
                keyExtractor={(row) => row.id}
                onRowClick={handleRowClick}
              />
              
              {totalPages > 1 && (
                <Pagination
                  currentPage={currentPage}
                  totalPages={totalPages}
                  onPageChange={setCurrentPage}
                  totalCount={totalRecords}
                  pageSize={pageSize}
                  onPageSizeChange={setPageSize}
                  showSizeChanger
                />
              )}
            </>
          )}
        </CardWithHeader>

        {/* 选中记录详情 */}
        {selectedRecord && (
          <Card>
            <h3 className="text-lg font-semibold text-gray-200 mb-4">记录详情</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-400">记录ID:</span>
                <span className="ml-2 text-gray-200 font-mono">{selectedRecord.id}</span>
              </div>
              <div>
                <span className="text-gray-400">操作时间:</span>
                <span className="ml-2 text-gray-200 font-mono">{selectedRecord.operationTime}</span>
              </div>
              <div>
                <span className="text-gray-400">员工编号:</span>
                <span className="ml-2 text-gray-200 font-mono">{selectedRecord.employeeId}</span>
              </div>
              <div>
                <span className="text-gray-400">操作模块:</span>
                <span className="ml-2 text-gray-200">{selectedRecord.moduleName}</span>
              </div>
              <div>
                <span className="text-gray-400">操作类型:</span>
                <span className="ml-2">
                  <StatusBadge variant="info">{selectedRecord.operationType}</StatusBadge>
                </span>
              </div>
              <div>
                <span className="text-gray-400">操作结果:</span>
                <span className="ml-2">
                  <StatusBadge variant={selectedRecord.operationResult === 'SUCCESS' ? 'success' : 'error'}>
                    {selectedRecord.operationResult === 'SUCCESS' ? '成功' : '失败'}
                  </StatusBadge>
                </span>
              </div>
              {selectedRecord.tradeReference && (
                <div className="col-span-2">
                  <span className="text-gray-400">交易编号:</span>
                  <span className="ml-2 text-gray-200 font-mono">{selectedRecord.tradeReference}</span>
                </div>
              )}
            </div>
          </Card>
        )}
      </div>
    </Layout>
  )
}

export default CompleteExample