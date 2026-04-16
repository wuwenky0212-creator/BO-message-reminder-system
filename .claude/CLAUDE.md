# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此代码仓库中工作时提供指导。

## 沟通语言

**与用户的所有交流、响应和解释必须使用中文。** 这是一个中文开发团队，所有沟通应使用中文进行。

## Documentation

- 编写 .md 文档时，也要用中文
- 正式文档写到项目的 docs/ 目录下
- 用于讨论和评审的计划、方案等文档，写到项目的 discuss/ 目录下

## 项目概述

**RCS 5.0** 是面向银行和金融机构的企业级金融风险控制系统。这是一个使用 Lerna 管理的 monorepo 项目，包含多个 Vue.js 应用和共享模块。

### 技术栈
- **框架**: Vue.js 2.7.14
- **UI 组件库**: Element UI 2.15.13
- **状态管理**: Vuex 3.6.2
- **路由**: Vue Router 3.6.5
- **构建工具**: Vue CLI 5.x + Webpack 5.x
- **包管理**: Lerna 3.22.1 + Yarn
- **CSS 预处理器**: Sass 1.63.4
- **HTTP 客户端**: Axios 0.27.2
- **图表**: ECharts 5.3.3
- **低代码**: @erayt/vue-dynamic

## 常用命令

```bash
# 安装依赖并初始化 monorepo
yarn install
yarn bootstrap

# 开发服务器（默认运行在 9527 端口）
yarn dev          # 主应用 (rcs5.0-web)
yarn dev:calc     # 计算器应用
yarn dev:trade    # 交易应用
yarn dev:pub      # 公共数据应用
yarn dev:pos      # 持仓管理应用
yarn dev:settle   # 结算应用
yarn dev:master   # 主数据管理应用
yarn dev:demo     # 演示应用

# 构建
yarn build        # 完整清理构建（执行 clean、bootstrap、build:libs）
yarn build:libs   # 构建所有库（module + web 包）
yarn build:web    # 仅构建 web 包
yarn build:module # 仅构建 module 包

# 开发监听模式
yarn build:web:watch    # web 包监听模式
yarn build:module:watch # module 包监听模式

# 代码检查
yarn lint

# 部署
yarn deploy           # 生产环境部署
yarn deploy:193.1     # 开发服务器 (192.168.193.1)
yarn deploy:test      # 测试环境
```

## Monorepo 结构

### Web 应用 (@rcs/*)
- `rcs5.0-web` - 主应用，包含所有业务模块
- `web-calc` - 计算器应用
- `web-trade` - 交易应用
- `web-pub` - 公共/基础数据管理
- `web-pos` - 持仓管理
- `web-settle6` - 结算系统
- `web-master` - 主数据管理
- `web-demo` - 演示应用
- `web-rsk` - 风险管理

### 共享模块 (@erayt/*)
- `module-lang-core` - 国际化/i18n
- `module-static-pub` - 静态公共数据组件
- `module-static-pos` - 静态持仓组件
- `module-biz-design` - 业务设计组件
- `module-components` - 共享组件
- `module-core-design` - 核心设计系统
- `module-dynamic` - 动态/低代码组件
- `module-element-design` - Element UI 设计扩展
- `module-plugins` - 插件
- `module-rcs-design` - RCS 专用设计组件
- `module-theme-chalk` - 主题样式
- `module-ui-design` - UI 设计系统
- `module-utils` - 工具函数

## 业务模块架构

主应用 (`rcs5.0-web`) 按业务模块组织，位于 `/src/` 目录下：

- **PUB** (`/pub/`) - 基础数据（币种、货币对、期限、交易对手、节假日）
- **DCS** (`/dcs/`) - 交易系统（产品创新、交易生命周期、现金流）
- **MDS** (`/mds/`) - 市场数据（数据源、曲线、评级）
- **POS** (`/pos/`) - 持仓管理（外汇、债券、货币市场）
- **PMS** (`/pms/`) - 定价管理和计算器
- **WKS** (`/wks/`) - 工作站（交易室、管理控制台）
- **RSK** (`/rsk/`) - 风险管理
- **SETTLE** (`/settle/`) - 结算系统

### 路由
- 模块化路由配置位于 `src/router/`
- 每个业务模块有自己的路由文件（如 `dcsRouter.js`、`pubRouter.js`）
- 路由使用动态导入实现懒加载

### API 层
- 按业务模块组织在 `src/api/`
- 全局 API 对象通过 `this.$apis` 访问
- 集成 titanOne 框架进行 API 调用

### 状态管理
- Vuex 模块化结构位于 `src/store/modules/`
- 模块自动导入
- 全局 getters 位于 `src/store/getters.js`

## 国际化

- 支持中文 (`zh_CN`) 和英文 (`en_US`)
- 语言文件位于 `src/lang/`
- 构建输出按语言区分 (`dist/zh_CN` 或 `dist/en`)
- 通过 `LocalesAggregatorPlugin` 动态生成语言包
- 通过环境变量 `process.env.LOCALE` 设置语言

## 开发配置

### 开发服务器
- 默认端口: 9527
- 主机: 0.0.0.0（可从网络访问）
- 在 `vue.config.js` 中配置了多个服务代理

### 代理端点
- `/dev` - 主后端服务
- `/dcs` - 交易服务
- `/pos` - 持仓服务
- `/pub` - 公共数据服务
- `/rsk` - 风险服务
- `/phoenix` - 低代码组件服务
- `/ecas` - ECAS 服务
- `/eflow` - 工作流服务

## 代码规范

基于 `.cursor/rules/my-rules.mdc`：

- **语言**: 所有注释和日志默认使用中文
- **代码注释**: 使用中文解释代码意图
- **金融准确性**: 这是一个金融系统，所有计算需要充分测试
- **设计理念**: 遵循 KISS、YAGNI、SOLID 原则

## 构建流程

构建流程：
1. 清理 node_modules 和 lock 文件
2. 初始化 Lerna 包
3. 构建 module 包
4. 构建 web 包
5. 生成特定语言的 index.html
6. 复制 Phoenix 和静态资源
7. 生成路由映射 mapping.json
