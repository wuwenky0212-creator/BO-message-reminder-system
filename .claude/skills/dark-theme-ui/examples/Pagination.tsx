/**
 * 分页组件示例
 * 
 * 深色主题的分页导航组件
 */

import React from 'react'

interface PaginationProps {
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
  showQuickJumper?: boolean
  showSizeChanger?: boolean
  pageSize?: number
  onPageSizeChange?: (size: number) => void
  totalCount?: number
}

export function Pagination({
  currentPage,
  totalPages,
  onPageChange,
  showQuickJumper = false,
  showSizeChanger = false,
  pageSize = 20,
  onPageSizeChange,
  totalCount,
}: PaginationProps) {
  const generatePageNumbers = () => {
    const pages: (number | string)[] = []
    const maxVisible = 7

    if (totalPages <= maxVisible) {
      // 如果总页数小于等于最大显示数，显示所有页码
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i)
      }
    } else {
      // 复杂分页逻辑
      if (currentPage <= 4) {
        // 当前页在前面
        for (let i = 1; i <= 5; i++) {
          pages.push(i)
        }
        pages.push('...')
        pages.push(totalPages)
      } else if (currentPage >= totalPages - 3) {
        // 当前页在后面
        pages.push(1)
        pages.push('...')
        for (let i = totalPages - 4; i <= totalPages; i++) {
          pages.push(i)
        }
      } else {
        // 当前页在中间
        pages.push(1)
        pages.push('...')
        for (let i = currentPage - 1; i <= currentPage + 1; i++) {
          pages.push(i)
        }
        pages.push('...')
        pages.push(totalPages)
      }
    }

    return pages
  }

  const pageNumbers = generatePageNumbers()

  return (
    <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4">
      {/* 统计信息 */}
      {totalCount && (
        <div className="text-sm text-gray-400">
          共 <span className="text-blue-400 font-semibold">{totalCount}</span> 条记录，
          第 <span className="text-blue-400 font-semibold">{currentPage}</span> / {totalPages} 页
        </div>
      )}

      {/* 分页控件 */}
      <div className="flex items-center gap-2">
        {/* 上一页 */}
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className="px-3 py-2 text-sm bg-[#1f1f1f] text-gray-300 border border-gray-700 rounded hover:bg-[#2a2a2a] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          上一页
        </button>

        {/* 页码 */}
        <div className="hidden sm:flex items-center gap-1">
          {pageNumbers.map((page, index) => (
            <React.Fragment key={index}>
              {page === '...' ? (
                <span className="px-2 text-gray-500">...</span>
              ) : (
                <button
                  onClick={() => onPageChange(page as number)}
                  className={`min-w-[40px] h-10 px-3 rounded text-sm font-medium transition-all duration-200 ${
                    currentPage === page
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'bg-[#1f1f1f] text-gray-300 border border-gray-700 hover:bg-[#2a2a2a] hover:border-gray-600'
                  }`}
                >
                  {page}
                </button>
              )}
            </React.Fragment>
          ))}
        </div>

        {/* 移动端页码显示 */}
        <div className="sm:hidden">
          <span className="px-4 py-2 bg-[#1f1f1f] text-gray-300 rounded border border-gray-700 text-sm">
            {currentPage} / {totalPages}
          </span>
        </div>

        {/* 下一页 */}
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className="px-3 py-2 text-sm bg-[#1f1f1f] text-gray-300 border border-gray-700 rounded hover:bg-[#2a2a2a] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          下一页
        </button>

        {/* 快速跳转 */}
        {showQuickJumper && (
          <div className="flex items-center gap-2 ml-4">
            <span className="text-sm text-gray-400">跳至</span>
            <input
              type="number"
              min={1}
              max={totalPages}
              className="w-16 px-2 py-1 text-sm bg-[#141414] border border-gray-700 rounded text-gray-200 focus:outline-none focus:border-blue-500"
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  const page = parseInt((e.target as HTMLInputElement).value)
                  if (page >= 1 && page <= totalPages) {
                    onPageChange(page)
                  }
                }
              }}
            />
            <span className="text-sm text-gray-400">页</span>
          </div>
        )}

        {/* 页面大小选择器 */}
        {showSizeChanger && onPageSizeChange && (
          <div className="flex items-center gap-2 ml-4">
            <span className="text-sm text-gray-400">每页</span>
            <select
              value={pageSize}
              onChange={(e) => onPageSizeChange(parseInt(e.target.value))}
              className="px-2 py-1 text-sm bg-[#141414] border border-gray-700 rounded text-gray-200 focus:outline-none focus:border-blue-500"
            >
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
            <span className="text-sm text-gray-400">条</span>
          </div>
        )}
      </div>
    </div>
  )
}

// 简化版分页组件
interface SimplePaginationProps {
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
}

export function SimplePagination({ currentPage, totalPages, onPageChange }: SimplePaginationProps) {
  return (
    <div className="flex items-center justify-center gap-2 pt-4">
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className="px-4 py-2 text-sm bg-[#1f1f1f] text-gray-300 border border-gray-700 rounded hover:bg-[#2a2a2a] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        上一页
      </button>

      <span className="px-4 py-2 bg-[#1f1f1f] text-gray-300 rounded border border-gray-700 text-sm">
        {currentPage} / {totalPages}
      </span>

      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        className="px-4 py-2 text-sm bg-[#1f1f1f] text-gray-300 border border-gray-700 rounded hover:bg-[#2a2a2a] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        下一页
      </button>
    </div>
  )
}

// 使用示例
export function PaginationExample() {
  const [currentPage, setCurrentPage] = React.useState(1)
  const [pageSize, setPageSize] = React.useState(20)
  const totalCount = 1234
  const totalPages = Math.ceil(totalCount / pageSize)

  return (
    <div className="space-y-8 p-6 bg-[#141414]">
      <div className="bg-[#1f1f1f] rounded-lg p-6 border border-gray-800">
        <h3 className="text-lg font-semibold text-gray-200 mb-4">完整分页组件</h3>
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={setCurrentPage}
          totalCount={totalCount}
          pageSize={pageSize}
          onPageSizeChange={setPageSize}
          showQuickJumper
          showSizeChanger
        />
      </div>

      <div className="bg-[#1f1f1f] rounded-lg p-6 border border-gray-800">
        <h3 className="text-lg font-semibold text-gray-200 mb-4">简化分页组件</h3>
        <SimplePagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={setCurrentPage}
        />
      </div>

      <div className="bg-[#1f1f1f] rounded-lg p-6 border border-gray-800">
        <h3 className="text-lg font-semibold text-gray-200 mb-4">基础分页组件</h3>
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={setCurrentPage}
          totalCount={totalCount}
        />
      </div>
    </div>
  )
}