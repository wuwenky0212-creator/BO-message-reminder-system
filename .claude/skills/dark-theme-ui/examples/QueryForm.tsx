/**
 * 查询表单组件示例
 * 
 * 横向 4 列布局，适用于数据查询页面
 */

import { useState } from 'react'

export interface QueryFormData {
  dateFrom?: string
  dateTo?: string
  employeeId?: string
  moduleName?: string
  operationType?: string
  tradeReference?: string
}

interface QueryFormProps {
  onSubmit: (data: QueryFormData) => void
  loading?: boolean
}

export function QueryForm({ onSubmit, loading = false }: QueryFormProps) {
  const [formData, setFormData] = useState<QueryFormData>({
    dateFrom: '',
    dateTo: '',
    employeeId: '',
    moduleName: '',
    operationType: '',
    tradeReference: '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    // 过滤掉空值
    const filteredData: QueryFormData = {}
    Object.entries(formData).forEach(([key, value]) => {
      if (value !== '') {
        filteredData[key as keyof QueryFormData] = value
      }
    })
    
    onSubmit(filteredData)
  }

  const handleReset = () => {
    setFormData({
      dateFrom: '',
      dateTo: '',
      employeeId: '',
      moduleName: '',
      operationType: '',
      tradeReference: '',
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* 第一行：4 列布局 */}
      <div className="grid grid-cols-4 gap-4 items-end">
        <div>
          <label className="block text-sm text-gray-400 mb-2">
            开始日期
          </label>
          <input
            type="date"
            value={formData.dateFrom}
            onChange={(e) => setFormData({ ...formData, dateFrom: e.target.value })}
            className="w-full px-3 py-2 bg-[#141414] border border-gray-700 rounded text-gray-200 text-sm
                     focus:outline-none focus:border-blue-500 transition-colors"
          />
        </div>
        
        <div>
          <label className="block text-sm text-gray-400 mb-2">
            结束日期
          </label>
          <input
            type="date"
            value={formData.dateTo}
            onChange={(e) => setFormData({ ...formData, dateTo: e.target.value })}
            className="w-full px-3 py-2 bg-[#141414] border border-gray-700 rounded text-gray-200 text-sm
                     focus:outline-none focus:border-blue-500 transition-colors"
          />
        </div>

        <div>
          <label className="block text-sm text-gray-400 mb-2">
            员工编号
          </label>
          <input
            type="text"
            placeholder="请输入"
            value={formData.employeeId}
            onChange={(e) => setFormData({ ...formData, employeeId: e.target.value })}
            className="w-full px-3 py-2 bg-[#141414] border border-gray-700 rounded text-gray-200 text-sm
                     placeholder-gray-600 focus:outline-none focus:border-blue-500 transition-colors"
          />
        </div>

        <div>
          <label className="block text-sm text-gray-400 mb-2">
            模块
          </label>
          <select
            value={formData.moduleName}
            onChange={(e) => setFormData({ ...formData, moduleName: e.target.value })}
            className="w-full px-3 py-2 bg-[#141414] border border-gray-700 rounded text-gray-200 text-sm
                     focus:outline-none focus:border-blue-500 transition-colors"
          >
            <option value="">请选择</option>
            <option value="交易管理">交易管理</option>
            <option value="支付处理">支付处理</option>
            <option value="账户管理">账户管理</option>
            <option value="风险控制">风险控制</option>
          </select>
        </div>
      </div>

      {/* 第二行：2 个输入框 + 按钮 */}
      <div className="grid grid-cols-4 gap-4 items-end">
        <div>
          <label className="block text-sm text-gray-400 mb-2">
            交易编号
          </label>
          <input
            type="text"
            placeholder="请输入"
            value={formData.tradeReference}
            onChange={(e) => setFormData({ ...formData, tradeReference: e.target.value })}
            className="w-full px-3 py-2 bg-[#141414] border border-gray-700 rounded text-gray-200 text-sm
                     placeholder-gray-600 focus:outline-none focus:border-blue-500 transition-colors"
          />
        </div>

        <div>
          <label className="block text-sm text-gray-400 mb-2">
            状态
          </label>
          <select
            value={formData.operationType}
            onChange={(e) => setFormData({ ...formData, operationType: e.target.value })}
            className="w-full px-3 py-2 bg-[#141414] border border-gray-700 rounded text-gray-200 text-sm
                     focus:outline-none focus:border-blue-500 transition-colors"
          >
            <option value="">请选择</option>
            <option value="查询">查询</option>
            <option value="修改">修改</option>
            <option value="处理">处理</option>
            <option value="取消">取消</option>
          </select>
        </div>

        <div className="col-span-2 flex items-center gap-3">
          <button
            type="submit"
            className="bg-yellow-500 hover:bg-yellow-600 text-gray-900 px-8 py-2 rounded font-medium transition-colors"
            disabled={loading}
          >
            {loading ? '查询中...' : '查询'}
          </button>
          <button
            type="button"
            onClick={handleReset}
            disabled={loading}
            className="border border-blue-500 text-blue-500 hover:bg-blue-500 hover:text-white px-6 py-2 rounded transition-colors"
          >
            重置
          </button>
        </div>
      </div>
    </form>
  )
}
