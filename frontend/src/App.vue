<template>
  <div id="app">
    <!-- 顶部导航栏 -->
    <header class="top-navbar">
      <div class="navbar-left">
        <div class="logo">
          <svg class="logo-icon" viewBox="0 0 24 24" width="24" height="24">
            <rect x="2" y="2" width="9" height="9" fill="#1890ff" rx="2"/>
            <rect x="13" y="2" width="9" height="9" fill="#f5222d" rx="2"/>
            <rect x="2" y="13" width="9" height="9" fill="#52c41a" rx="2"/>
            <rect x="13" y="13" width="9" height="9" fill="#faad14" rx="2"/>
          </svg>
          <span class="logo-text">RCS 5.0</span>
        </div>
        <nav class="main-nav">
          <a href="#" class="nav-item">
            <HomeFilled class="nav-icon-svg" style="width: 14px; height: 14px;" />
            <span>首页</span>
          </a>
          <a href="#" class="nav-item">
            <EditPen class="nav-icon-svg" style="width: 14px; height: 14px;" />
            <span>交易录入</span>
          </a>
          <a href="#" class="nav-item" :class="{ active: currentPage === 'bond-position' }">
            <DataLine class="nav-icon-svg" style="width: 14px; height: 14px;" />
            <span>头寸管理</span>
          </a>
          <a href="#" class="nav-item">
            <Wallet class="nav-icon-svg" style="width: 14px; height: 14px;" />
            <span>限额管理</span>
          </a>
          <a href="#" class="nav-item">
            <Management class="nav-icon-svg" style="width: 14px; height: 14px;" />
            <span>业务管理</span>
          </a>
          <a href="#" class="nav-item">
            <Search class="nav-icon-svg" style="width: 14px; height: 14px;" />
            <span>查询管理</span>
          </a>
          <a href="#" class="nav-item" :class="{ active: currentPage !== 'bond-position' && currentPage !== 'trade-review' }">
            <Monitor class="nav-icon-svg" style="width: 14px; height: 14px;" />
            <span>后线工作台</span>
          </a>
          <a href="#" class="nav-item">
            <FolderOpened class="nav-icon-svg" style="width: 14px; height: 14px;" />
            <span>基础数据</span>
          </a>
          <a href="#" class="nav-item">
            <TrendCharts class="nav-icon-svg" style="width: 14px; height: 14px;" />
            <span>查询统计</span>
          </a>
          <a href="#" class="nav-item">
            <Setting class="nav-icon-svg" style="width: 14px; height: 14px;" />
            <span>规则管理</span>
          </a>
        </nav>
      </div>
      <div class="navbar-right">
        <button class="icon-btn" title="刷新">
          <Refresh class="icon-svg" style="width: 14px; height: 14px;" />
        </button>
        <BellIcon 
          :refresh-interval="30000"
          :enable-web-socket="true"
          @toggle="handleToggle"
        />
        <div class="user-dropdown">
          <User class="user-icon-svg" style="width: 14px; height: 14px;" />
          <span class="user-name">admin</span>
          <ArrowDown class="dropdown-arrow-svg" style="width: 8px; height: 8px;" />
        </div>
      </div>
    </header>

    <!-- 多页签导航栏 (仅在债券头寸页面显示) -->
    <div v-if="currentPage === 'bond-position'" class="page-tabs">
      <div class="tab-item active">
        <span>债券头寸</span>
        <button class="tab-close">✕</button>
      </div>
    </div>

    <!-- 主容器 -->
    <div class="main-container" :class="{ 'sidebar-collapsed': currentPage === 'bond-position' }">
      <!-- 左侧侧边栏 -->
      <aside class="sidebar" :class="{ 'collapsed': currentPage === 'bond-position' }">
        <!-- 折叠状态的极简工具栏 -->
        <div v-if="currentPage === 'bond-position'" class="sidebar-mini-toolbar">
          <button class="mini-btn" title="固定">📌</button>
          <button class="mini-btn" title="添加">+</button>
        </div>
        
        <!-- 正常状态的侧边栏内容 -->
        <template v-else>
        <div class="sidebar-header">
          <Briefcase class="sidebar-icon-svg" style="width: 16px; height: 16px;" />
          <span class="sidebar-title">工作台</span>
        </div>
        
        <div class="search-container">
          <input type="text" placeholder="请搜索" class="sidebar-search" />
          <Search class="search-icon-svg" style="width: 12px; height: 12px;" />
        </div>

        <nav class="sidebar-nav">
          <div class="nav-group">
            <div class="nav-group-title">
              <DocumentChecked class="group-icon-svg" style="width: 12px; height: 12px;" />
              <span>流程审批</span>
            </div>
            <a href="#" class="nav-link" :class="{ active: currentPage === 'trade-review' }" @click.prevent="currentPage = 'trade-review'; filterStatus = 'all'">交易复核</a>
            <a href="#" class="nav-link" :class="{ active: currentPage === 'settlement-approval' }" @click.prevent="currentPage = 'settlement-approval'; settlementTab = 'message'">清算审批</a>
            <a href="#" class="nav-link">调账审核</a>
          </div>
          
          <div class="nav-group">
            <div class="nav-group-title">
              <Calendar class="group-icon-svg" style="width: 12px; height: 12px;" />
              <span>证实确认</span>
            </div>
            <a href="#" class="nav-link" :class="{ active: currentPage === 'confirm-match' }" @click.prevent="currentPage = 'confirm-match'; filterStatus = 'all'">证实匹配</a>
            <a href="#" class="nav-link">证实明细</a>
            <a href="#" class="nav-link" :class="{ active: currentPage === 'confirm-message' }" @click.prevent="currentPage = 'confirm-message'; filterStatus = 'all'; dataViewType = 'pending'">证实报文</a>
          </div>
          
          <div class="nav-group">
            <div class="nav-group-title">
              <CreditCard class="group-icon-svg" style="width: 12px; height: 12px;" />
              <span>清算结算</span>
            </div>
            <a href="#" class="nav-link">待轧差处理</a>
            <a href="#" class="nav-link">待发报处理</a>
            <a href="#" class="nav-link">来帐分拣</a>
            <a href="#" class="nav-link">支付假日调整</a>
            <a href="#" class="nav-link">收付撤销</a>
            <a href="#" class="nav-link" :class="{ active: currentPage === 'payment-message' }" @click.prevent="currentPage = 'payment-message'; dataViewType = 'pending'">收付报文</a>
            <a href="#" class="nav-link">结算路径</a>
          </div>
          
          <div class="nav-group">
            <div class="nav-group-title">
              <DataAnalysis class="group-icon-svg" style="width: 12px; height: 12px;" />
              <span>会计核算</span>
            </div>
            <a href="#" class="nav-link">计量跟踪处理</a>
            <a href="#" class="nav-link">送账异常处理</a>
            <a href="#" class="nav-link">余额初始</a>
            <a href="#" class="nav-link">手工指定</a>
          </div>
        </nav>
        </template>
      </aside>

      <!-- 主内容区 -->
      <main class="content-area">
        <!-- 交易复核页面 -->
        <div v-if="currentPage === 'trade-review'" class="content-card">
          <!-- 页面标题 -->
          <div class="page-header">
            <h2 class="page-title">交易复核</h2>
            <div class="page-actions">
              <button class="icon-btn-small" title="刷新">
                <Refresh class="icon-svg-small" style="width: 12px; height: 12px;" />
              </button>
              <button class="icon-btn-small" title="设置">
                <Setting class="icon-svg-small" style="width: 12px; height: 12px;" />
              </button>
            </div>
          </div>

          <!-- 查询条件和操作工具栏 -->
          <div class="query-toolbar">
            <!-- 文本标签页 Tabs -->
            <div class="text-tabs">
              <button class="text-tab active">审批</button>
              <button class="text-tab">补发</button>
              <button class="text-tab">交易事件</button>
            </div>

            <!-- 筛选徽章 -->
            <div v-if="filterStatus === 'pending'" class="filter-badge">
              <span class="badge-text">📋 仅显示待审批记录</span>
              <button class="clear-filter-btn" @click="filterStatus = 'all'" title="清除筛选">✕</button>
            </div>

            <!-- 查询表单 -->
            <div class="query-item">
              <label class="query-label">外部流水号</label>
              <input type="text" class="query-input" placeholder="请搜索" />
            </div>
            <div class="query-item">
              <label class="query-label">交易流水号</label>
              <input type="text" class="query-input" placeholder="请搜索" />
            </div>

            <!-- 操作按钮 -->
            <button class="btn-primary">批量审批</button>
          </div>

          <!-- 数据表格 -->
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th class="col-checkbox"><input type="checkbox" /></th>
                  <th>外部流水号</th>
                  <th>交易流水号</th>
                  <th>产品 <span class="filter-icon">🔽</span></th>
                  <th>动作 <span class="filter-icon">🔽</span></th>
                  <th>起息日 <span class="filter-icon">🔽</span></th>
                  <th>交易日</th>
                  <th>交易对手</th>
                  <th>标的</th>
                  <th class="col-action">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, index) in tableData" :key="index" :class="{ 'row-even': index % 2 === 1 }">
                  <td class="col-checkbox"><input type="checkbox" /></td>
                  <td><a href="#" class="link-blue">{{ row.externalNo }}</a></td>
                  <td>{{ row.tradeNo }}</td>
                  <td>{{ row.product }}</td>
                  <td>{{ row.action }}</td>
                  <td>{{ row.valueDate }}</td>
                  <td>{{ row.tradeDate }}</td>
                  <td class="text-orange">{{ row.counterparty }}</td>
                  <td>{{ row.underlying }}</td>
                  <td class="col-action"><a href="#" class="link-blue">审批</a></td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 分页器 -->
          <div class="pagination-bar">
            <span class="pagination-total">共 96 条</span>
            <div class="pagination-controls">
              <button class="page-btn">&lt;</button>
              <button class="page-btn active">1</button>
              <button class="page-btn">2</button>
              <button class="page-btn">3</button>
              <button class="page-btn">4</button>
              <button class="page-btn">5</button>
              <button class="page-btn">&gt;</button>
            </div>
            <select class="page-size-select">
              <option>20条/页</option>
              <option>50条/页</option>
              <option>100条/页</option>
            </select>
            <div class="page-jumper">
              <span>前往</span>
              <input type="number" class="page-jump-input" value="1" />
              <span>页</span>
            </div>
          </div>
        </div>

        <!-- 证实匹配页面 -->
        <div v-else-if="currentPage === 'confirm-match'" class="content-card">
          <!-- 页面标题 -->
          <div class="page-header">
            <h2 class="page-title">证实匹配</h2>
            <div class="page-actions">
              <button class="icon-btn-small" title="刷新">
                <Refresh class="icon-svg-small" style="width: 12px; height: 12px;" />
              </button>
              <button class="icon-btn-small" title="设置">
                <Setting class="icon-svg-small" style="width: 12px; height: 12px;" />
              </button>
            </div>
          </div>

          <!-- 查询条件 -->
          <div class="query-toolbar">
            <div v-if="filterStatus === 'pending'" class="filter-badge">
              <span class="badge-text">📋 仅显示待匹配记录</span>
              <button class="clear-filter-btn" @click="filterStatus = 'all'" title="清除筛选">✕</button>
            </div>
            <div class="query-item">
              <label class="query-label">外部流水号</label>
              <input type="text" class="query-input" placeholder="请搜索" />
            </div>
            <div class="query-item">
              <label class="query-label">证实编号</label>
              <input type="text" class="query-input" placeholder="请搜索" />
            </div>
            <div class="query-item">
              <label class="query-label">生成日期</label>
              <input type="text" class="query-input" placeholder="开始日期" style="width: 110px;" />
              <span style="margin: 0 4px; color: #8c8c8c;">-</span>
              <input type="text" class="query-input" placeholder="结束日期" style="width: 110px;" />
            </div>
            <button class="btn-primary">批量匹配</button>
          </div>

          <!-- 数据表格 -->
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th class="col-checkbox"><input type="checkbox" /></th>
                  <th>外部流水号</th>
                  <th>证实编号</th>
                  <th>交易对手 <span class="filter-icon">🔽</span></th>
                  <th>证实方式</th>
                  <th>报文类型 <span class="filter-icon">🔽</span></th>
                  <th>报文参考号</th>
                  <th>产品 <span class="filter-icon">🔽</span></th>
                  <th>交易日</th>
                  <th class="col-action-wide">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, index) in filteredConfirmMatchData" :key="index" :class="{ 'row-even': index % 2 === 1 }">
                  <td class="col-checkbox"><input type="checkbox" /></td>
                  <td><a href="#" class="link-blue">{{ row.externalNo }}</a></td>
                  <td>{{ row.confirmNo }}</td>
                  <td class="text-orange">{{ row.counterparty }}</td>
                  <td>{{ row.confirmMethod }}</td>
                  <td>{{ row.messageType }}</td>
                  <td>{{ row.messageRef }}</td>
                  <td>{{ row.product }}</td>
                  <td>{{ row.tradeDate }}</td>
                  <td class="col-action-wide">
                    <a href="#" class="link-blue">匹配</a>
                    <span class="action-divider">|</span>
                    <a href="#" class="link-blue">查看</a>
                    <span class="action-divider">|</span>
                    <a href="#" class="link-blue">催收</a>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 分页器 -->
          <div class="pagination-bar">
            <span class="pagination-total">共 38 条</span>
            <div class="pagination-controls">
              <button class="page-btn">&lt;</button>
              <button class="page-btn active">1</button>
              <button class="page-btn">2</button>
              <button class="page-btn">&gt;</button>
            </div>
            <select class="page-size-select">
              <option>20条/页</option>
              <option>50条/页</option>
              <option>100条/页</option>
            </select>
            <div class="page-jumper">
              <span>前往</span>
              <input type="number" class="page-jump-input" value="1" />
              <span>页</span>
            </div>
          </div>
        </div>

        <!-- 证实报文页面 -->
        <div v-else-if="currentPage === 'confirm-message'" class="content-card">
          <!-- 页面标题 -->
          <div class="page-header">
            <h2 class="page-title">证实报文</h2>
            <div class="page-actions">
              <button class="icon-btn-small" title="刷新">
                <Refresh class="icon-svg-small" style="width: 12px; height: 12px;" />
              </button>
              <button class="icon-btn-small" title="设置">
                <Setting class="icon-svg-small" style="width: 12px; height: 12px;" />
              </button>
            </div>
          </div>

          <!-- 查询条件和操作工具栏 -->
          <div class="query-toolbar">
            <!-- 数据视图切换 -->
            <div class="view-switcher">
              <button 
                class="view-btn" 
                :class="{ active: dataViewType === 'pending' }"
                @click="dataViewType = 'pending'"
              >
                待处理信息
              </button>
              <button 
                class="view-btn" 
                :class="{ active: dataViewType === 'history' }"
                @click="dataViewType = 'history'"
              >
                历史信息
              </button>
            </div>

            <!-- 查询表单 -->
            <div class="query-item">
              <label class="query-label">外部流水号</label>
              <input type="text" class="query-input" placeholder="请搜索" />
            </div>
            <div class="query-item">
              <label class="query-label">交易流水号</label>
              <input type="text" class="query-input" placeholder="请搜索" />
            </div>
            <div class="query-item">
              <label class="query-label">发送日期</label>
              <input type="text" class="query-input" placeholder="2025-06-11 - 2026-04-11" style="width: 220px;" />
            </div>

            <!-- 操作按钮组 -->
            <div class="action-buttons">
              <button class="btn-default">补发</button>
              <button class="btn-default">置为成功</button>
              <button class="btn-default">置为失败</button>
              <button class="btn-primary">无需发送</button>
            </div>
          </div>

          <!-- 数据表格 -->
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th class="col-checkbox"><input type="checkbox" /></th>
                  <th>外部流水号</th>
                  <th>证实编号</th>
                  <th>报文类别</th>
                  <th>报文类型 <span class="filter-icon">🔽</span></th>
                  <th>报文参考号 <span class="filter-icon">🔽</span></th>
                  <th>交易对手</th>
                  <th>产品 <span class="filter-icon">🔽</span></th>
                  <th>操作类型</th>
                  <th>发送次数</th>
                  <th>发送状态 <span class="filter-icon">🔽</span></th>
                  <th>发送时间</th>
                  <th class="col-action">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, index) in filteredConfirmMessageData" :key="index" :class="{ 'row-even': index % 2 === 1 }">
                  <td class="col-checkbox"><input type="checkbox" /></td>
                  <td><a href="#" class="link-blue">{{ row.externalNo }}</a></td>
                  <td>{{ row.confirmNo }}</td>
                  <td>{{ row.messageCategory }}</td>
                  <td>{{ row.messageType }}</td>
                  <td>{{ row.messageRef }}</td>
                  <td class="text-orange">{{ row.counterparty }}</td>
                  <td>{{ row.product }}</td>
                  <td>{{ row.operationType }}</td>
                  <td>{{ row.sendCount }}</td>
                  <td>{{ row.sendStatus }}</td>
                  <td>{{ row.sendTime }}</td>
                  <td class="col-action"><a href="#" class="link-blue">查看</a></td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 分页器 -->
          <div class="pagination-bar">
            <span class="pagination-total">共 {{ filteredConfirmMessageData.length }} 条</span>
            <div class="pagination-controls">
              <button class="page-btn" disabled>&lt;</button>
              <button class="page-btn active">1</button>
              <button class="page-btn" disabled>&gt;</button>
            </div>
            <select class="page-size-select">
              <option>20条/页</option>
              <option>50条/页</option>
              <option>100条/页</option>
            </select>
            <div class="page-jumper">
              <span>前往</span>
              <input type="number" class="page-jump-input" value="1" />
              <span>页</span>
            </div>
          </div>
        </div>

        <!-- 收付报文页面 -->
        <div v-else-if="currentPage === 'payment-message'" class="content-card">
          <!-- 页面标题 -->
          <div class="page-header">
            <h2 class="page-title">收付报文</h2>
            <div class="page-actions">
              <button class="icon-btn-small" title="刷新">
                <Refresh class="icon-svg-small" style="width: 12px; height: 12px;" />
              </button>
              <button class="icon-btn-small" title="设置">
                <Setting class="icon-svg-small" style="width: 12px; height: 12px;" />
              </button>
            </div>
          </div>

          <!-- 查询条件和操作工具栏 -->
          <div class="query-toolbar">
            <!-- 数据视图切换 -->
            <div class="view-switcher">
              <button 
                class="view-btn" 
                :class="{ active: dataViewType === 'pending' }"
                @click="dataViewType = 'pending'"
              >
                待处理信息
              </button>
              <button 
                class="view-btn" 
                :class="{ active: dataViewType === 'history' }"
                @click="dataViewType = 'history'"
              >
                历史信息
              </button>
            </div>

            <!-- 查询表单 -->
            <div class="query-item">
              <label class="query-label">外部流水号</label>
              <input type="text" class="query-input" placeholder="请搜索" />
            </div>
            <div class="query-item">
              <label class="query-label">发送日期</label>
              <input type="text" class="query-input" placeholder="2025-06-11 - 2026-04-11" style="width: 220px;" />
            </div>

            <!-- 操作按钮组 -->
            <div class="action-buttons">
              <button class="btn-default">补发</button>
              <button class="btn-default">置为成功</button>
              <button class="btn-default">置为失败</button>
              <button class="btn-primary">无需发送</button>
            </div>
          </div>

          <!-- 数据表格 -->
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th class="col-checkbox"><input type="checkbox" /></th>
                  <th>外部流水号</th>
                  <th>收付流水号 <span class="filter-icon">🔽</span></th>
                  <th>报文类别</th>
                  <th>报文类型 <span class="filter-icon">🔽</span></th>
                  <th>报文参考号</th>
                  <th>操作类型</th>
                  <th>交易对手</th>
                  <th>货币</th>
                  <th class="col-action">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, index) in filteredPaymentMessageData" :key="index" :class="{ 'row-even': index % 2 === 1 }">
                  <td class="col-checkbox"><input type="checkbox" /></td>
                  <td><a href="#" class="link-blue">{{ row.externalNo }}</a></td>
                  <td>{{ row.paymentNo }}</td>
                  <td>{{ row.messageCategory }}</td>
                  <td>{{ row.messageType }}</td>
                  <td>{{ row.messageRef }}</td>
                  <td>{{ row.operationType }}</td>
                  <td class="text-orange">{{ row.counterparty }}</td>
                  <td>{{ row.currency }}</td>
                  <td class="col-action"><a href="#" class="link-blue">查看</a></td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 分页器 -->
          <div class="pagination-bar">
            <span class="pagination-total">共 {{ filteredPaymentMessageData.length }} 条</span>
            <div class="pagination-controls">
              <button class="page-btn" disabled>&lt;</button>
              <button class="page-btn active">1</button>
              <button class="page-btn" disabled>&gt;</button>
            </div>
            <select class="page-size-select">
              <option>20条/页</option>
              <option>50条/页</option>
              <option>100条/页</option>
            </select>
            <div class="page-jumper">
              <span>前往</span>
              <input type="number" class="page-jump-input" value="1" />
              <span>页</span>
            </div>
          </div>
        </div>

        <!-- 清算审批页面 -->
        <div v-else-if="currentPage === 'settlement-approval'" class="content-card">
          <!-- 页面标题 -->
          <div class="page-header">
            <h2 class="page-title">清算审批</h2>
            <div class="page-actions">
              <button class="icon-btn-small" title="刷新">
                <Refresh class="icon-svg-small" style="width: 12px; height: 12px;" />
              </button>
              <button class="icon-btn-small" title="设置">
                <Setting class="icon-svg-small" style="width: 12px; height: 12px;" />
              </button>
            </div>
          </div>

          <!-- 查询条件和操作工具栏 -->
          <div class="query-toolbar">
            <!-- 文本标签页 Tabs -->
            <div class="text-tabs">
              <button 
                class="text-tab" 
                :class="{ active: settlementTab === 'message' }"
                @click="settlementTab = 'message'"
              >
                报文
              </button>
              <button 
                class="text-tab" 
                :class="{ active: settlementTab === 'settlement-path' }"
                @click="settlementTab = 'settlement-path'"
              >
                结算路径
              </button>
              <button 
                class="text-tab" 
                :class="{ active: settlementTab === 'cashflow' }"
                @click="settlementTab = 'cashflow'"
              >
                现金流
              </button>
              <button 
                class="text-tab" 
                :class="{ active: settlementTab === 'incoming-sort' }"
                @click="settlementTab = 'incoming-sort'"
              >
                来账分拣
              </button>
            </div>

            <!-- 查询表单 -->
            <div class="query-item">
              <label class="query-label">外部流水号</label>
              <input type="text" class="query-input" placeholder="请搜索" />
            </div>
            <div class="query-item">
              <label class="query-label">交易流水号</label>
              <input type="text" class="query-input" placeholder="请搜索" />
            </div>

            <!-- 操作按钮 -->
            <button class="btn-primary">批量审批</button>
          </div>

          <!-- 数据表格 -->
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th class="col-checkbox"><input type="checkbox" /></th>
                  <th>外部流水号</th>
                  <th>交易流水号</th>
                  <th>收付流水号 <span class="filter-icon">🔽</span></th>
                  <th>报文类型 <span class="filter-icon">🔽</span></th>
                  <th>起息日 <span class="filter-icon">🔽</span></th>
                  <th>交易对手</th>
                  <th>货币</th>
                  <th class="col-amount">金额</th>
                  <th>收付方向</th>
                  <th>审核</th>
                  <th class="col-action">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, index) in settlementApprovalData" :key="index" :class="{ 'row-even': index % 2 === 1 }">
                  <td class="col-checkbox"><input type="checkbox" /></td>
                  <td><a v-if="row.externalNo" href="#" class="link-blue">{{ row.externalNo }}</a></td>
                  <td>{{ row.tradeNo }}</td>
                  <td class="text-orange">{{ row.paymentNo }}</td>
                  <td>{{ row.messageType }}</td>
                  <td>{{ row.valueDate }}</td>
                  <td class="text-orange">{{ row.counterparty }}</td>
                  <td>{{ row.currency }}</td>
                  <td class="col-amount">{{ formatAmount(row.amount) }}</td>
                  <td :class="row.direction === '收' ? 'text-green' : 'text-red'">{{ row.direction }}</td>
                  <td>{{ row.review }}</td>
                  <td class="col-action"><a href="#" class="link-blue">审批</a></td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 分页器 -->
          <div class="pagination-bar">
            <span class="pagination-total">共 {{ settlementApprovalData.length }} 条</span>
            <div class="pagination-controls">
              <button class="page-btn" disabled>&lt;</button>
              <button class="page-btn active">1</button>
              <button class="page-btn" disabled>&gt;</button>
            </div>
            <select class="page-size-select">
              <option>20条/页</option>
              <option>50条/页</option>
              <option>100条/页</option>
            </select>
            <div class="page-jumper">
              <span>前往</span>
              <input type="number" class="page-jump-input" value="1" />
              <span>页</span>
            </div>
          </div>
        </div>

        <!-- 债券持仓页面 -->
        <div v-else-if="currentPage === 'bond-position'" class="content-card bond-position-page">
          <!-- 业务模式切换 Tabs -->
          <div class="business-tabs">
            <button class="business-tab active">实时头寸</button>
            <button class="business-tab">历史头寸</button>
          </div>

          <!-- 高级查询表单 -->
          <div class="advanced-search">
            <div class="search-row">
              <div class="search-field">
                <label class="search-label">账户</label>
                <select class="search-select">
                  <option>MasterBank</option>
                </select>
              </div>
              <div class="search-field">
                <label class="search-label">利息类型</label>
                <select class="search-select">
                  <option value="">请选择</option>
                </select>
              </div>
              <div class="search-field">
                <label class="search-label">债券分类</label>
                <select class="search-select">
                  <option value="">请选择</option>
                </select>
              </div>
              <div class="search-field">
                <label class="search-label">发行人</label>
                <input type="text" class="search-input" placeholder="请选择" />
              </div>
              <div class="search-actions">
                <button class="btn-expand">展开 ▼</button>
                <button class="btn-primary">查询</button>
                <button class="btn-default">重置</button>
              </div>
            </div>
          </div>

          <!-- 表格控制工具栏 -->
          <div class="table-toolbar">
            <div class="toolbar-left"></div>
            <div class="toolbar-right">
              <label class="auto-refresh">
                <span>自动刷新</span>
                <input type="checkbox" class="switch-input" />
                <span class="switch-slider"></span>
              </label>
              <button class="icon-btn-small" title="设置">
                <Setting class="icon-svg-small" style="width: 14px; height: 14px;" />
              </button>
            </div>
          </div>

          <!-- 数据表格 -->
          <div class="table-container bond-table-container">
            <table class="data-table bond-table">
              <thead>
                <tr>
                  <th>区域</th>
                  <th>债券分类</th>
                  <th>利息类型</th>
                  <th>债券</th>
                  <th>账户</th>
                  <th>到期日</th>
                  <th class="col-number">券面总额</th>
                  <th class="col-number">持仓数量(万)</th>
                  <th class="col-number">可用数量(万)</th>
                  <th>货币</th>
                  <th class="col-number">净价</th>
                  <th class="col-number">收益率(%)</th>
                  <th class="col-number">票面利率(%)</th>
                  <th class="col-number">PV</th>
                  <th class="col-action-wide">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, index) in bondPositionData" :key="index" :class="{ 'row-even': index % 2 === 1 }">
                  <td>{{ row.region }}</td>
                  <td>{{ row.bondCategory }}</td>
                  <td>{{ row.interestType }}</td>
                  <td><a href="#" class="link-blue">{{ row.bondCode }}</a></td>
                  <td><a href="#" class="link-blue">{{ row.account }}</a></td>
                  <td>{{ row.maturityDate }}</td>
                  <td class="col-number" :class="{ 'text-red': isNegative(row.faceValue) }">
                    {{ formatNumber(row.faceValue, 2) }}
                  </td>
                  <td class="col-number" :class="{ 'text-red': isNegative(row.holdingQty) }">
                    {{ formatNumber(row.holdingQty, 4) }}
                  </td>
                  <td class="col-number" :class="{ 'text-red': isNegative(row.availableQty) }">
                    {{ formatNumber(row.availableQty, 0) }}
                  </td>
                  <td>{{ row.currency || '-' }}</td>
                  <td class="col-number" :class="{ 'text-red': isNegative(row.netPrice) }">
                    {{ formatNumber(row.netPrice, 4) }}
                  </td>
                  <td class="col-number" :class="{ 'text-red': isNegative(row.yield) }">
                    {{ formatNumber(row.yield, 3) }}
                  </td>
                  <td class="col-number" :class="{ 'text-red': isNegative(row.couponRate) }">
                    {{ formatNumber(row.couponRate, 2) }}
                  </td>
                  <td class="col-number" :class="{ 'text-red': isNegative(row.pv) }">
                    {{ formatNumber(row.pv, 2) }}
                  </td>
                  <td class="col-action-wide">
                    <a href="#" class="link-blue">详情</a>
                    <span class="action-divider">|</span>
                    <a href="#" class="link-blue">违约</a>
                    <span class="action-divider">|</span>
                    <a href="#" class="link-blue">更多 ▼</a>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>

    <!-- 底部版权栏 -->
    <footer class="footer">
      <p>版权所有 © 2025 杭州时代银通软件股份有限公司 2026-04-16 14:10:06</p>
    </footer>
    
    <!-- 通知面板 -->
    <NotificationPanel 
      :is-visible="isPanelVisible"
      @close="isPanelVisible = false"
      @action="handleNotificationAction"
    />
    
    <!-- 风险预警弹窗 -->
    <RiskWarningModal
      :is-visible="isRiskWarningVisible"
      bond-code="CHK_SEC_003"
      timestamp="16:00:11"
      :abnormal-count="1"
      risk-amount="-50.00M"
      :bonds="[
        { code: '019547.SH', name: '20国债04', gap: '-50,000' }
      ]"
      @close="isRiskWarningVisible = false"
      @action="handleRiskWarningAction"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import BellIcon from './components/BellIcon.vue'
import NotificationPanel from './components/NotificationPanel.vue'
import RiskWarningModal from './components/RiskWarningModal.vue'
import { 
  HomeFilled, 
  EditPen, 
  DataLine, 
  Wallet, 
  Management, 
  Search, 
  Monitor, 
  FolderOpened, 
  TrendCharts, 
  Setting,
  Refresh,
  User,
  ArrowDown,
  Briefcase,
  DocumentChecked,
  Calendar,
  CreditCard,
  DataAnalysis
} from '@element-plus/icons-vue'

const isPanelVisible = ref(false)

const handleToggle = () => {
  isPanelVisible.value = !isPanelVisible.value
}

// 当前页面状态
const currentPage = ref<'trade-review' | 'confirm-match' | 'confirm-message' | 'payment-message' | 'settlement-approval' | 'bond-position'>('trade-review')

// 风险预警弹窗状态
const isRiskWarningVisible = ref(false)

// 筛选状态
const filterStatus = ref<string>('all') // 'all' | 'pending'

// 数据视图类型（用于证实报文页面）
const dataViewType = ref<'pending' | 'history'>('pending') // 'pending' | 'history'

// 清算审批 Tab 类型
const settlementTab = ref<'message' | 'settlement-path' | 'cashflow' | 'incoming-sort'>('message')

// 模拟表格数据
const allTableData = ref([
  { externalNo: '260403001353645', tradeNo: '260403001353645', product: '当日外币对外汇', action: '卖进', valueDate: '2026-04-10', tradeDate: '2026-04-08', counterparty: 'ICBC-YGN', underlying: 'GBPHKD', approvalStatus: '待审批' },
  { externalNo: '260403001353617', tradeNo: '260403001353617', product: '当日外币对外汇', action: '卖进', valueDate: '2026-04-09', tradeDate: '2026-04-07', counterparty: 'BOCHK-HKG', underlying: 'USDHKD', approvalStatus: '待审批' },
  { externalNo: '260401001353579', tradeNo: '260401001353579', product: '美金银行间', action: '卖进', valueDate: '2026-04-30', tradeDate: '2026-02-28', counterparty: 'HSBC-HK', underlying: 'AUDCNY', approvalStatus: '待审批' },
  { externalNo: '260317001353400', tradeNo: '260317001353400', product: '五份中间', action: '卖进', valueDate: '2026-03-17', tradeDate: '2026-03-17', counterparty: 'CITI-NY', underlying: 'EURUSD', approvalStatus: '待审批' },
  { externalNo: '260317001353442', tradeNo: '260317001353442', product: '五份中间', action: '卖进', valueDate: '2026-03-18', tradeDate: '2026-03-17', counterparty: 'SCB-LDN', underlying: 'GBPUSD', approvalStatus: '待审批' },
  { externalNo: '260312001353440', tradeNo: '260312001353440', product: '外汇出国', action: '卖进', valueDate: '2026-03-13', tradeDate: '2026-03-11', counterparty: 'DBS-SG', underlying: 'USDCNY', approvalStatus: '待审批' },
  { externalNo: '260312001353431', tradeNo: '260312001353431', product: '五份中间', action: '卖进', valueDate: '2026-03-12', tradeDate: '2026-03-12', counterparty: 'BOC-SG', underlying: 'USDSGD', approvalStatus: '待审批' },
  { externalNo: '260302001353063', tradeNo: '260302001353063', product: '五份中间', action: '卖进', valueDate: '2026-01-30', tradeDate: '2026-01-28', counterparty: 'ICBC-YGN', underlying: 'EURUSD', approvalStatus: '待审批' },
  { externalNo: '260301001352311', tradeNo: '260301001352311', product: '外汇买卖间汇', action: '卖进', valueDate: '2026-02-24', tradeDate: '2026-02-23', counterparty: 'BOCHK-HKG', underlying: 'USDCNY', approvalStatus: '待审批' },
  { externalNo: '260216001352734', tradeNo: '260216001352734', product: '外汇出国', action: '卖进', valueDate: '2026-02-24', tradeDate: '2026-02-16', counterparty: 'HSBC-HK', underlying: 'USDHKD', approvalStatus: '待审批' },
])

// 证实匹配表格数据
const confirmMatchData = ref([
  { externalNo: 'EXT20260416001', confirmNo: 'CNF2026041601', counterparty: '中国工商银行仰光分行', confirmMethod: 'SWIFT', messageType: 'MT300', messageRef: 'ICBCMM001', product: '外汇掉期', tradeDate: '2026-04-16', status: '待匹配' },
  { externalNo: 'EXT20260416002', confirmNo: 'CNF2026041602', counterparty: '中国银行新加坡分行', confirmMethod: 'SWIFT', messageType: 'MT300', messageRef: 'BOCSG002', product: '外汇远期', tradeDate: '2026-04-16', status: '待匹配' },
  { externalNo: 'EXT20260416003', confirmNo: 'CNF2026041603', counterparty: '汇丰银行香港分行', confirmMethod: 'Email', messageType: 'PDF', messageRef: 'HSBCHK003', product: '货币互换', tradeDate: '2026-04-15', status: '待匹配' },
  { externalNo: 'EXT20260416004', confirmNo: 'CNF2026041604', counterparty: '花旗银行纽约分行', confirmMethod: 'SWIFT', messageType: 'MT300', messageRef: 'CITINY004', product: '外汇即期', tradeDate: '2026-04-15', status: '待匹配' },
  { externalNo: 'EXT20260416005', confirmNo: 'CNF2026041605', counterparty: '渣打银行伦敦分行', confirmMethod: 'SWIFT', messageType: 'MT320', messageRef: 'SCBLDN005', product: '利率互换', tradeDate: '2026-04-14', status: '待匹配' },
])

// 证实报文表格数据
const confirmMessageData = ref([
  { externalNo: 'EXT20260416001', confirmNo: 'CNF2026041601', messageCategory: '证实', messageType: 'MT300', messageRef: 'ICBCMM001', counterparty: '中国工商银行仰光分行', product: '外汇掉期', operationType: '新增', sendCount: 0, sendStatus: '待发送', sendTime: '-', status: 'pending' },
  { externalNo: 'EXT20260416002', confirmNo: 'CNF2026041602', messageCategory: '证实', messageType: 'MT300', messageRef: 'BOCSG002', counterparty: '中国银行新加坡分行', product: '外汇远期', operationType: '新增', sendCount: 1, sendStatus: '发送失败', sendTime: '2026-04-16 10:23:45', status: 'pending' },
  { externalNo: 'EXT20260416003', confirmNo: 'CNF2026041603', messageCategory: '证实', messageType: 'PDF', messageRef: 'HSBCHK003', counterparty: '汇丰银行香港分行', product: '货币互换', operationType: '修改', sendCount: 0, sendStatus: '待发送', sendTime: '-', status: 'pending' },
  { externalNo: 'EXT20260416004', confirmNo: 'CNF2026041604', messageCategory: '证实', messageType: 'MT300', messageRef: 'CITINY004', counterparty: '花旗银行纽约分行', product: '外汇即期', operationType: '新增', sendCount: 2, sendStatus: '发送失败', sendTime: '2026-04-16 11:15:22', status: 'pending' },
  { externalNo: 'EXT20260416005', confirmNo: 'CNF2026041605', messageCategory: '证实', messageType: 'MT320', messageRef: 'SCBLDN005', counterparty: '渣打银行伦敦分行', product: '利率互换', operationType: '新增', sendCount: 0, sendStatus: '待发送', sendTime: '-', status: 'pending' },
  { externalNo: 'EXT20260416006', confirmNo: 'CNF2026041606', messageCategory: '证实', messageType: 'MT300', messageRef: 'DBSSG006', counterparty: '星展银行新加坡分行', product: '外汇掉期', operationType: '取消', sendCount: 1, sendStatus: '发送失败', sendTime: '2026-04-16 09:45:12', status: 'pending' },
  { externalNo: 'EXT20260416007', confirmNo: 'CNF2026041607', messageCategory: '证实', messageType: 'MT300', messageRef: 'SCBHK007', counterparty: '渣打银行香港分行', product: '外汇远期', operationType: '新增', sendCount: 0, sendStatus: '待发送', sendTime: '-', status: 'pending' },
  { externalNo: 'EXT20260416008', confirmNo: 'CNF2026041608', messageCategory: '证实', messageType: 'MT320', messageRef: 'BOCHK008', counterparty: '中国银行香港分行', product: '利率互换', operationType: '修改', sendCount: 3, sendStatus: '发送失败', sendTime: '2026-04-16 14:32:18', status: 'pending' },
])

// 收付报文表格数据
const paymentMessageData = ref([
  { externalNo: 'EXT20260416001', paymentNo: 'PAY2026041601', messageCategory: '收款', messageType: 'MT103', messageRef: 'ICBCMM001', operationType: '新增', counterparty: '中国工商银行仰光分行', currency: 'USD', status: 'pending' },
  { externalNo: 'EXT20260416002', paymentNo: 'PAY2026041602', messageCategory: '付款', messageType: 'MT202', messageRef: 'BOCSG002', operationType: '新增', counterparty: '中国银行新加坡分行', currency: 'EUR', status: 'pending' },
  { externalNo: 'EXT20260416003', paymentNo: 'PAY2026041603', messageCategory: '收款', messageType: 'MT103', messageRef: 'HSBCHK003', operationType: '修改', counterparty: '汇丰银行香港分行', currency: 'GBP', status: 'pending' },
  { externalNo: 'EXT20260416004', paymentNo: 'PAY2026041604', messageCategory: '付款', messageType: 'MT202', messageRef: 'CITINY004', operationType: '新增', counterparty: '花旗银行纽约分行', currency: 'USD', status: 'pending' },
  { externalNo: 'EXT20260416005', paymentNo: 'PAY2026041605', messageCategory: '收款', messageType: 'MT103', messageRef: 'SCBLDN005', operationType: '新增', counterparty: '渣打银行伦敦分行', currency: 'GBP', status: 'pending' },
  { externalNo: 'EXT20260416006', paymentNo: 'PAY2026041606', messageCategory: '付款', messageType: 'MT202', messageRef: 'DBSSG006', operationType: '取消', counterparty: '星展银行新加坡分行', currency: 'SGD', status: 'pending' },
  { externalNo: 'EXT20260416007', paymentNo: 'PAY2026041607', messageCategory: '收款', messageType: 'MT103', messageRef: 'SCBHK007', operationType: '新增', counterparty: '渣打银行香港分行', currency: 'HKD', status: 'pending' },
  { externalNo: 'EXT20260416008', paymentNo: 'PAY2026041608', messageCategory: '付款', messageType: 'MT202', messageRef: 'BOCHK008', operationType: '修改', counterparty: '中国银行香港分行', currency: 'CNY', status: 'pending' },
  { externalNo: 'EXT20260416009', paymentNo: 'PAY2026041609', messageCategory: '收款', messageType: 'MT103', messageRef: 'BNPPAR009', operationType: '新增', counterparty: '法国巴黎银行', currency: 'EUR', status: 'pending' },
])

// 清算审批表格数据
const settlementApprovalData = ref([
  { externalNo: 'EXT20260416001', tradeNo: 'TRD2026041601', paymentNo: 'ST1000008017', messageType: 'MT103', valueDate: '2026-04-17', counterparty: 'ICBC-YGN', currency: 'USD', amount: 1000000.00, direction: '收', review: '待审批' },
  { externalNo: 'EXT20260416002', tradeNo: 'TRD2026041602', paymentNo: 'ST1000008018', messageType: 'MT202', valueDate: '2026-04-18', counterparty: 'BOC-SG', currency: 'EUR', amount: 500000.00, direction: '付', review: '待审批' },
  { externalNo: '', tradeNo: '', paymentNo: 'ST1000008019', messageType: 'MT103', valueDate: '2026-04-19', counterparty: 'HSBC-HK', currency: 'GBP', amount: 750000.00, direction: '收', review: '待审批' },
])

// 债券持仓表格数据
const bondPositionData = ref([
  { region: '上海', bondCategory: '国债', interestType: '固定', bondCode: '019547.SH', bondName: '20国债04', account: 'MasterBank', maturityDate: '2030-06-15', faceValue: 50000000.00, holdingQty: -50000.0000, availableQty: -50000, currency: 'CNY', netPrice: 98.5234, yield: 2.856, couponRate: 3.25, pv: -49261700.00 },
  { region: '深圳', bondCategory: '企业债', interestType: '浮动', bondCode: '250003.IB', bondName: '25企债03', account: 'liujin', maturityDate: '2028-12-20', faceValue: 30000000.00, holdingQty: 30000.0000, availableQty: 30000, currency: 'CNY', netPrice: 102.3456, yield: 3.245, couponRate: 4.15, pv: 30703680.00 },
  { region: '上海', bondCategory: '金融债', interestType: '固定', bondCode: '180205.IB', bondName: '18金融05', account: 'BANKCXF_BOND', maturityDate: '2025-08-30', faceValue: 20000000.00, holdingQty: 20000.0000, availableQty: 20000, currency: null, netPrice: 99.8765, yield: 2.134, couponRate: 2.85, pv: 19975300.00 },
])

// 根据筛选状态计算显示的证实匹配数据
const filteredConfirmMatchData = computed(() => {
  if (filterStatus.value === 'pending') {
    return confirmMatchData.value.filter(row => row.status === '待匹配')
  }
  return confirmMatchData.value
})

// 根据数据视图类型计算显示的证实报文数据
const filteredConfirmMessageData = computed(() => {
  if (dataViewType.value === 'pending') {
    return confirmMessageData.value.filter(row => row.status === 'pending')
  }
  // 历史信息暂时返回空数组
  return []
})

// 根据数据视图类型计算显示的收付报文数据
const filteredPaymentMessageData = computed(() => {
  if (dataViewType.value === 'pending') {
    return paymentMessageData.value.filter(row => row.status === 'pending')
  }
  // 历史信息暂时返回空数组
  return []
})

// 根据筛选状态计算显示的表格数据
const tableData = computed(() => {
  if (filterStatus.value === 'pending') {
    return allTableData.value.filter(row => row.approvalStatus === '待审批')
  }
  return allTableData.value
})

// 处理通知面板的跳转
const handleNotificationAction = (ruleCode: string) => {
  isPanelVisible.value = false
  
  // 根据规则代码执行不同的跳转逻辑
  if (ruleCode === 'TRADE_REVIEW_001') {
    // 未交易复核 - 切换到交易复核页面并筛选待审批记录
    currentPage.value = 'trade-review'
    filterStatus.value = 'pending'
    setTimeout(() => {
      const tableContainer = document.querySelector('.table-container')
      if (tableContainer) {
        tableContainer.scrollTop = 0
      }
    }, 100)
  } else if (ruleCode === 'CONFIRM_MATCH_002') {
    // 未证实匹配 - 切换到证实匹配页面并筛选待匹配记录
    currentPage.value = 'confirm-match'
    filterStatus.value = 'pending'
    setTimeout(() => {
      const tableContainer = document.querySelector('.table-container')
      if (tableContainer) {
        tableContainer.scrollTop = 0
      }
    }, 100)
  } else if (ruleCode === 'CONFIRM_MSG_003') {
    // 证实报文未发送 - 切换到证实报文页面并显示待处理信息
    currentPage.value = 'confirm-message'
    dataViewType.value = 'pending'
    setTimeout(() => {
      const tableContainer = document.querySelector('.table-container')
      if (tableContainer) {
        tableContainer.scrollTop = 0
      }
    }, 100)
  } else if (ruleCode === 'PAYMENT_MSG_004') {
    // 收付报文未发送 - 切换到收付报文页面并显示待处理信息
    currentPage.value = 'payment-message'
    dataViewType.value = 'pending'
    setTimeout(() => {
      const tableContainer = document.querySelector('.table-container')
      if (tableContainer) {
        tableContainer.scrollTop = 0
      }
    }, 100)
  } else if (ruleCode === 'PAYMENT_APPROVAL_005') {
    // 收付报文清算审批 - 切换到清算审批页面
    currentPage.value = 'settlement-approval'
    settlementTab.value = 'message'
    setTimeout(() => {
      const tableContainer = document.querySelector('.table-container')
      if (tableContainer) {
        tableContainer.scrollTop = 0
      }
    }, 100)
  } else if (ruleCode === 'BOND_SHORT_006') {
    // 债券持仓卖空预警 - 显示风险预警弹窗
    isRiskWarningVisible.value = true
  }
  // TODO: 其他规则的跳转逻辑
}

// 处理风险预警弹窗的"立即处理"按钮
const handleRiskWarningAction = () => {
  isRiskWarningVisible.value = false
  currentPage.value = 'bond-position'
  setTimeout(() => {
    const tableContainer = document.querySelector('.table-container')
    if (tableContainer) {
      tableContainer.scrollTop = 0
    }
  }, 100)
}

const formatAmount = (amount: number) => {
  return amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// 格式化数字（带精度控制）
const formatNumber = (value: number | null, decimals: number = 2) => {
  if (value === null || value === undefined) return '-'
  return value.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
}

// 判断是否为负数
const isNegative = (value: number | null) => {
  return value !== null && value < 0
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body, html {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(to bottom, #f5f7fa 0%, #f0f2f5 100%);
}

/* 顶部导航栏 */
.top-navbar {
  height: 50px;
  background: linear-gradient(135deg, #001529 0%, #002140 100%);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  color: white;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08), 0 1px 3px rgba(0, 0, 0, 0.12);
  flex-shrink: 0;
  position: relative;
  z-index: 100;
}

/* 多页签导航栏 */
.page-tabs {
  height: 42px;
  background: linear-gradient(to bottom, #f5f7fa 0%, #f0f2f5 100%);
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  padding: 0 20px;
  gap: 6px;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
}

.page-tabs .tab-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 18px;
  background: white;
  border: 1px solid #d9d9d9;
  border-bottom: none;
  border-radius: 8px 8px 0 0;
  font-size: 13px;
  color: #262626;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  font-weight: 500;
  letter-spacing: 0.3px;
  box-shadow: 0 -2px 6px rgba(0, 0, 0, 0.05);
}

.page-tabs .tab-item::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #1890ff 0%, #40a9ff 100%);
  transform: scaleX(0);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-tabs .tab-item.active {
  background: white;
  color: #1890ff;
  border-color: #e8e8e8;
  font-weight: 600;
  box-shadow: 0 -3px 10px rgba(24, 144, 255, 0.1);
}

.page-tabs .tab-item.active::after {
  transform: scaleX(1);
}

.page-tabs .tab-close {
  background: none;
  border: none;
  color: #8c8c8c;
  cursor: pointer;
  padding: 0;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 3px;
  font-size: 12px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-tabs .tab-close:hover {
  background: linear-gradient(135deg, #f5f5f5 0%, #fafafa 100%);
  color: #262626;
  transform: scale(1.1);
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 30px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: bold;
}

.logo-icon {
  width: 16px;
  height: 16px;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
}

.logo-text {
  letter-spacing: 0.5px;
}

.main-nav {
  display: flex;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  color: rgba(255, 255, 255, 0.75);
  text-decoration: none;
  font-size: 14px;
  border-radius: 6px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  font-weight: 500;
  letter-spacing: 0.3px;
}

.nav-icon {
  font-size: 16px;
  opacity: 0.9;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.12);
  color: white;
  transform: translateY(-1px);
}

.nav-item.active {
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.3);
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.icon-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.85);
  font-size: 18px;
  cursor: pointer;
  padding: 5px;
  transition: color 0.3s;
}

.icon-btn:hover {
  color: white;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 6px;
  transition: background 0.3s;
}

.user-dropdown:hover {
  background: rgba(255, 255, 255, 0.1);
}

/* 主容器 */
.main-container {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 左侧侧边栏 */
.sidebar {
  width: 220px;
  background: white;
  border-right: 1px solid #e8e8e8;
  overflow-y: auto;
  flex-shrink: 0;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.03);
  transition: width 0.3s;
}

.sidebar.collapsed {
  width: 48px;
  overflow: hidden;
}

/* 折叠状态的极简工具栏 */
.sidebar-mini-toolbar {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 0;
  gap: 16px;
}

.mini-btn {
  width: 32px;
  height: 32px;
  background: none;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  color: #595959;
}

.mini-btn:hover {
  background: #f5f5f5;
  border-color: #1890ff;
  color: #1890ff;
}

.sidebar-header {
  padding: 16px;
  font-size: 15px;
  font-weight: 600;
  color: #262626;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  gap: 8px;
  letter-spacing: 0.3px;
}

.search-container {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  position: relative;
  display: flex;
  align-items: center;
}

.sidebar-search {
  width: 100%;
  padding: 6px 12px 6px 32px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 13px;
  transition: all 0.25s;
  background: #fafafa;
  flex: 1;
}

.sidebar-search:focus {
  outline: none;
  border-color: #1890ff;
  background: white;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

.sidebar-search::placeholder {
  color: #bfbfbf;
}

.search-icon-svg {
  position: absolute;
  left: 24px;
  top: 50%;
  transform: translateY(-50%);
  flex-shrink: 0;
  pointer-events: none;
}

.sidebar-nav {
  padding: 8px 0;
}

.nav-group {
  margin-bottom: 4px;
}

.nav-group-title {
  padding: 10px 16px;
  font-size: 13px;
  color: #666;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fafafa;
}

.nav-link {
  display: block;
  padding: 10px 16px 10px 40px;
  color: #595959;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  font-weight: 450;
}

.nav-link:hover {
  background: linear-gradient(90deg, #f0f5ff 0%, #fafafa 100%);
  color: #1890ff;
  padding-left: 44px;
}

.nav-link.active {
  background: linear-gradient(90deg, #e6f7ff 0%, #f0f9ff 100%);
  color: #1890ff;
  font-weight: 600;
}

.nav-link.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: linear-gradient(180deg, #1890ff 0%, #40a9ff 100%);
  box-shadow: 2px 0 4px rgba(24, 144, 255, 0.3);
}

.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #f0f2f5;
  padding: 16px;
}

.content-card {
  flex: 1;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

/* Tab 切换 */
.tabs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 16px;
  border-bottom: 1px solid #e8e8e8;
}

.tabs {
  display: flex;
}

.tab-item {
  padding: 12px 20px;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-size: 14px;
  color: #595959;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 500;
  letter-spacing: 0.3px;
}

.tab-item:hover {
  color: #1890ff;
  background: rgba(24, 144, 255, 0.04);
}

.tab-item.active {
  color: #1890ff;
  border-bottom-color: #1890ff;
  font-weight: 600;
  background: linear-gradient(to bottom, rgba(24, 144, 255, 0.02) 0%, transparent 100%);
}

.tabs-actions {
  display: flex;
  gap: 8px;
}

.icon-btn-small {
  background: none;
  border: none;
  color: #666;
  font-size: 16px;
  cursor: pointer;
  padding: 4px;
  transition: color 0.3s;
}

.icon-btn-small:hover {
  color: #1890ff;
}

/* 查询条件 */
.query-toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-bottom: 1px solid #e8e8e8;
  flex-wrap: wrap;
}

/* 文本标签页 Tabs */
.text-tabs {
  display: flex;
  gap: 24px;
}

.text-tab {
  padding: 8px 0;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  color: #8c8c8c;
  transition: all 0.25s;
  font-weight: 400;
  position: relative;
}

.text-tab:hover {
  color: #262626;
}

.text-tab.active {
  color: #262626;
  font-weight: 600;
}

/* 数据视图切换器 */
.view-switcher {
  display: flex;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  overflow: hidden;
  background: white;
}

.view-btn {
  padding: 6px 16px;
  background: white;
  border: none;
  cursor: pointer;
  font-size: 14px;
  color: #595959;
  transition: all 0.25s;
  font-weight: 500;
  border-right: 1px solid #d9d9d9;
}

.view-btn:last-child {
  border-right: none;
}

.view-btn:hover {
  color: #1890ff;
  background: #f0f9ff;
}

.view-btn.active {
  background: #f5f5f5;
  color: #262626;
  font-weight: 600;
}

/* 操作按钮组 */
.action-buttons {
  display: flex;
  gap: 8px;
  margin-left: auto;
}

.btn-default {
  padding: 6px 16px;
  background: white;
  color: #595959;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-default:hover {
  color: #1890ff;
  border-color: #1890ff;
  background: #f0f9ff;
}

.btn-default:active {
  transform: translateY(1px);
}

.filter-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  border: 1px solid #91d5ff;
  border-radius: 6px;
  font-size: 13px;
  color: #0050b3;
  font-weight: 500;
}

.badge-text {
  display: flex;
  align-items: center;
  gap: 4px;
}

.clear-filter-btn {
  background: rgba(0, 80, 179, 0.1);
  border: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #0050b3;
  transition: all 0.2s;
  padding: 0;
  line-height: 1;
}

.clear-filter-btn:hover {
  background: rgba(0, 80, 179, 0.2);
  transform: scale(1.1);
}

.query-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.query-label {
  font-size: 14px;
  color: #666;
  white-space: nowrap;
}

.query-input {
  padding: 6px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  width: 180px;
  transition: all 0.25s;
  background: #fafafa;
}

.query-input:focus {
  outline: none;
  border-color: #1890ff;
  background: white;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

.query-input::placeholder {
  color: #bfbfbf;
}

.btn-primary {
  padding: 6px 20px;
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  margin-left: auto;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 6px rgba(24, 144, 255, 0.25);
  letter-spacing: 0.3px;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #40a9ff 0%, #69c0ff 100%);
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.35);
  transform: translateY(-1px);
}

.btn-primary:active {
  transform: translateY(0);
}

/* 数据表格 */
.table-container {
  flex: 1;
  overflow: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.data-table thead {
  background: linear-gradient(to bottom, #fafafa 0%, #f5f5f5 100%);
  position: sticky;
  top: 0;
  z-index: 1;
}

.data-table th {
  padding: 12px 12px;
  text-align: left;
  font-weight: 600;
  color: #262626;
  border-bottom: 2px solid #e8e8e8;
  white-space: nowrap;
  font-size: 13px;
  letter-spacing: 0.3px;
}

.data-table td {
  padding: 12px 12px;
  border-bottom: 1px solid #f5f5f5;
  color: #595959;
  font-size: 13px;
  transition: background 0.2s;
}

.data-table tbody tr:hover {
  background: linear-gradient(90deg, #fafafa 0%, #fcfcfc 100%);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.data-table tbody tr.row-even {
  background: #fafafa;
}

.data-table tbody tr.row-even:hover {
  background: linear-gradient(90deg, #f5f5f5 0%, #f8f8f8 100%);
}

.col-checkbox {
  width: 40px;
  text-align: center;
}

.col-checkbox input[type="checkbox"] {
  cursor: pointer;
}

.col-amount {
  text-align: right;
}

.col-action {
  width: 80px;
  text-align: center;
}

.link-blue {
  color: #1890ff;
  text-decoration: none;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.link-blue:hover {
  color: #40a9ff;
  text-decoration: underline;
}

.text-orange {
  color: #fa8c16;
  font-weight: 600;
  background: linear-gradient(135deg, #fa8c16 0%, #ffa940 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.text-red {
  color: #f5222d;
  font-weight: 600;
}

.text-green {
  color: #52c41a;
  font-weight: 600;
}

.filter-icon {
  font-size: 10px;
  color: #999;
  margin-left: 4px;
}

/* 分页器 */
.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 16px;
  padding: 16px;
  border-top: 1px solid #e8e8e8;
}

.pagination-total {
  font-size: 14px;
  color: #666;
  margin-right: auto;
}

.pagination-controls {
  display: flex;
  gap: 4px;
  align-items: center;
}

.page-btn {
  min-width: 32px;
  height: 32px;
  padding: 0 8px;
  border: 1px solid #d9d9d9;
  background: white;
  cursor: pointer;
  border-radius: 6px;
  font-size: 14px;
  color: #595959;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 500;
}

.page-btn:hover {
  color: #1890ff;
  border-color: #1890ff;
  background: linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%);
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(24, 144, 255, 0.15);
}

.page-btn.active {
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  color: white;
  border-color: #1890ff;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.3);
  font-weight: 600;
}

.page-btn:disabled {
  cursor: not-allowed;
  opacity: 0.4;
  background: #f5f5f5;
  color: #bfbfbf;
  border-color: #d9d9d9;
}

.page-btn:disabled:hover {
  transform: none;
  box-shadow: none;
  border-color: #d9d9d9;
  background: #f5f5f5;
}

.page-ellipsis {
  padding: 0 8px;
  color: #999;
}

.page-size-select {
  padding: 6px 8px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  background: white;
}

.page-jumper {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #666;
}

.page-jump-input {
  width: 50px;
  padding: 6px 8px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  text-align: center;
}

/* 页面标题区 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e8e8e8;
}

.page-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  letter-spacing: 0.3px;
}

.page-actions {
  display: flex;
  gap: 8px;
}

/* 债券持仓页面特殊样式 */
.bond-position-page {
  padding: 0;
  background: linear-gradient(to bottom, #fafafa 0%, #f5f5f5 100%);
}

/* 业务模式切换 Tabs */
.business-tabs {
  display: flex;
  gap: 32px;
  padding: 24px 32px 0 32px;
  border-bottom: 2px solid #f0f0f0;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
}

.business-tab {
  padding: 14px 0;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 17px;
  color: #8c8c8c;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 400;
  position: relative;
  border-bottom: 3px solid transparent;
  margin-bottom: -2px;
  letter-spacing: 0.5px;
}

.business-tab::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #1890ff 0%, #40a9ff 100%);
  transform: scaleX(0);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.business-tab:hover {
  color: #1890ff;
}

.business-tab.active {
  color: #1890ff;
  font-weight: 600;
}

.business-tab.active::after {
  transform: scaleX(1);
}

/* 高级查询表单 */
.advanced-search {
  padding: 24px 32px;
  background: white;
  border-bottom: 1px solid #e8e8e8;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
}

.search-row {
  display: flex;
  align-items: flex-end;
  gap: 20px;
  flex-wrap: wrap;
}

.search-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.search-label {
  font-size: 13px;
  color: #595959;
  font-weight: 500;
  letter-spacing: 0.3px;
}

.search-select,
.search-input {
  padding: 8px 14px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  font-size: 14px;
  min-width: 180px;
  background: white;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.search-select:hover,
.search-input:hover {
  border-color: #40a9ff;
  box-shadow: 0 2px 6px rgba(24, 144, 255, 0.1);
}

.search-select:focus,
.search-input:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.12), 0 2px 8px rgba(24, 144, 255, 0.15);
  transform: translateY(-1px);
}

.search-actions {
  display: flex;
  gap: 12px;
  margin-left: auto;
}

.btn-expand {
  padding: 8px 18px;
  background: white;
  color: #595959;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 500;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.btn-expand:hover {
  color: #1890ff;
  border-color: #1890ff;
  background: linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%);
  box-shadow: 0 2px 6px rgba(24, 144, 255, 0.15);
  transform: translateY(-1px);
}

.btn-expand:active {
  transform: translateY(0);
}

/* 表格控制工具栏 */
.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 32px;
  background: white;
  border-bottom: 1px solid #f0f0f0;
}

.toolbar-left {
  flex: 1;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.auto-refresh {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: #595959;
  cursor: pointer;
  font-weight: 500;
  letter-spacing: 0.3px;
}

.switch-input {
  display: none;
}

.switch-slider {
  position: relative;
  width: 44px;
  height: 22px;
  background: linear-gradient(135deg, #bfbfbf 0%, #d9d9d9 100%);
  border-radius: 11px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
}

.switch-slider::before {
  content: '';
  position: absolute;
  width: 18px;
  height: 18px;
  background: white;
  border-radius: 50%;
  top: 2px;
  left: 2px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
}

.switch-input:checked + .switch-slider {
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  box-shadow: 0 2px 6px rgba(24, 144, 255, 0.3);
}

.switch-input:checked + .switch-slider::before {
  left: 24px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

/* 债券表格特殊样式 */
.bond-table-container {
  overflow-x: auto;
  background: white;
  margin: 0;
  padding: 0 32px 24px 32px;
}

.bond-table {
  min-width: 1600px;
  border-collapse: separate;
  border-spacing: 0;
}

.bond-table thead {
  background: linear-gradient(to bottom, #fafafa 0%, #f5f5f5 100%);
  position: sticky;
  top: 0;
  z-index: 10;
}

.bond-table th {
  padding: 14px 16px;
  text-align: left;
  font-weight: 600;
  color: #262626;
  border-bottom: 2px solid #e8e8e8;
  white-space: nowrap;
  font-size: 13px;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  font-size: 12px;
}

.bond-table td {
  padding: 14px 16px;
  border-bottom: 1px solid #f5f5f5;
  color: #595959;
  font-size: 13px;
  transition: all 0.2s;
}

.bond-table tbody tr {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.bond-table tbody tr:hover {
  background: linear-gradient(90deg, #f0f9ff 0%, #e6f7ff 50%, #f0f9ff 100%);
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.08);
  transform: translateY(-1px);
}

.bond-table tbody tr.row-even {
  background: #fafafa;
}

.bond-table tbody tr.row-even:hover {
  background: linear-gradient(90deg, #f0f9ff 0%, #e6f7ff 50%, #f0f9ff 100%);
}

.col-number {
  text-align: right;
  font-family: 'Courier New', 'Consolas', monospace;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.text-red {
  color: #f5222d !important;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(245, 34, 45, 0.1);
}

/* 证实匹配表格操作列 */
.col-action-wide {
  width: 140px;
  text-align: center;
}

.action-divider {
  color: #d9d9d9;
  margin: 0 8px;
  font-weight: 300;
}

/* 底部版权栏 */
.footer {
  height: 40px;
  background: linear-gradient(to right, #ffffff 0%, #fafafa 100%);
  border-top: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 -1px 4px rgba(0, 0, 0, 0.02);
}

.footer p {
  font-size: 12px;
  color: #8c8c8c;
  letter-spacing: 0.3px;
  font-weight: 450;
}

/* 滚动条美化 */
.sidebar::-webkit-scrollbar,
.table-container::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.sidebar::-webkit-scrollbar-track,
.table-container::-webkit-scrollbar-track {
  background: #f5f5f5;
}

.sidebar::-webkit-scrollbar-thumb,
.table-container::-webkit-scrollbar-thumb {
  background: #d9d9d9;
  border-radius: 3px;
  transition: background 0.2s;
}

.sidebar::-webkit-scrollbar-thumb:hover,
.table-container::-webkit-scrollbar-thumb:hover {
  background: #bfbfbf;
}

/* 输入框和选择框美化 */
input[type="checkbox"] {
  cursor: pointer;
  width: 16px;
  height: 16px;
  accent-color: #1890ff;
}

.page-size-select,
.page-jump-input {
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  transition: all 0.25s;
  background: white;
}

.page-size-select:focus,
.page-jump-input:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

/* 图标按钮增强 */
.icon-btn,
.icon-btn-small {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.icon-btn:hover,
.icon-btn-small:hover {
  transform: scale(1.1);
}

.icon-btn:active,
.icon-btn-small:active {
  transform: scale(0.95);
}
</style>


/* SVG图标样式 */
.nav-icon-svg,
.icon-svg,
.icon-svg-small,
.user-icon-svg,
.dropdown-arrow-svg,
.sidebar-icon-svg,
.search-icon-svg,
.group-icon-svg {
  flex-shrink: 0;
}

.nav-icon-svg {
  width: 12px;
  height: 12px;
}

.icon-svg {
  width: 14px;
  height: 14px;
}

.icon-svg-small {
  width: 12px;
  height: 12px;
}

.user-icon-svg {
  width: 14px;
  height: 14px;
}

.dropdown-arrow-svg {
  width: 8px;
  height: 8px;
  opacity: 0.65;
}

.sidebar-icon-svg {
  width: 16px;
  height: 16px;
  color: #1890ff;
}

.search-icon-svg {
  position: absolute;
  left: 24px;
  top: 50%;
  transform: translateY(-50%);
  width: 12px;
  height: 12px;
  color: #8c8c8c;
}

.group-icon-svg {
  width: 12px;
  height: 12px;
  color: #595959;
}


.sidebar-search {
  width: 100%;
  padding: 6px 12px 6px 32px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 13px;
  transition: all 0.25s;
  background: #fafafa;
}

.sidebar-search:focus {
  outline: none;
  border-color: #1890ff;
  background: white;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

.sidebar-search::placeholder {
  color: #bfbfbf;
}


.user-name {
  color: rgba(255, 255, 255, 0.85);
  font-size: 14px;
  font-weight: 500;
}
