# 部署指南 - Vercel + Render

本指南将帮助您将应用部署到 Vercel（前端）和 Render（后端）。

## 📋 前置准备

1. **GitHub 账号**（用于代码托管）
2. **Vercel 账号**（https://vercel.com - 可用 GitHub 登录）
3. **Render 账号**（https://render.com - 可用 GitHub 登录）

---

## 🚀 部署步骤

### 第一步：准备 GitHub 仓库

1. **初始化 Git 仓库**（如果还没有）
   ```bash
   git init
   git add .
   git commit -m "Initial commit for deployment"
   ```

2. **创建 GitHub 仓库**
   - 访问 https://github.com/new
   - 创建新仓库（例如：`message-reminder-system`）
   - 选择 Public 或 Private（都可以）

3. **推送代码到 GitHub**
   ```bash
   git remote add origin https://github.com/你的用户名/message-reminder-system.git
   git branch -M main
   git push -u origin main
   ```

---

### 第二步：部署后端到 Render

1. **登录 Render**
   - 访问 https://render.com
   - 使用 GitHub 账号登录

2. **创建新的 Web Service**
   - 点击 "New +" → "Web Service"
   - 选择 "Build and deploy from a Git repository"
   - 点击 "Connect" 连接你的 GitHub 仓库

3. **配置 Web Service**
   ```
   Name: message-reminder-api
   Region: Singapore (或选择离你最近的区域)
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn demo_server:app --host 0.0.0.0 --port $PORT
   ```

4. **选择免费套餐**
   - Instance Type: Free
   - 点击 "Create Web Service"

5. **等待部署完成**（约 3-5 分钟）
   - 部署成功后，你会看到一个 URL，例如：
   - `https://message-reminder-api.onrender.com`
   - **复制这个 URL，后面会用到！**

6. **测试后端 API**
   - 访问：`https://你的后端URL.onrender.com/docs`
   - 应该能看到 FastAPI 的 API 文档页面

---

### 第三步：部署前端到 Vercel

1. **更新前端配置**
   
   编辑 `frontend/.env.production` 文件：
   ```env
   VITE_API_BASE_URL=https://你的后端URL.onrender.com
   ```
   
   将 `你的后端URL.onrender.com` 替换为第二步中获得的 Render URL。

2. **提交配置更改**
   ```bash
   git add frontend/.env.production
   git commit -m "Update production API URL"
   git push
   ```

3. **登录 Vercel**
   - 访问 https://vercel.com
   - 使用 GitHub 账号登录

4. **导入项目**
   - 点击 "Add New..." → "Project"
   - 选择你的 GitHub 仓库
   - 点击 "Import"

5. **配置项目**
   ```
   Framework Preset: Vite
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm install
   ```

6. **添加环境变量**
   - 在 "Environment Variables" 部分添加：
   ```
   Name: VITE_API_BASE_URL
   Value: https://你的后端URL.onrender.com
   ```

7. **部署**
   - 点击 "Deploy"
   - 等待部署完成（约 2-3 分钟）

8. **获取前端 URL**
   - 部署成功后，Vercel 会提供一个 URL，例如：
   - `https://message-reminder-system.vercel.app`

---

### 第四步：更新 CORS 配置（重要！）

由于前端和后端在不同域名，需要确保 CORS 配置正确。

编辑 `backend/demo_server.py`，确认 CORS 配置：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议改为具体的 Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**生产环境建议**（更安全）：
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://message-reminder-system.vercel.app",  # 你的 Vercel URL
        "http://localhost:5173"  # 本地开发
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

提交并推送更改：
```bash
git add backend/demo_server.py
git commit -m "Update CORS for production"
git push
```

Render 会自动重新部署后端。

---

## ✅ 验证部署

1. **访问前端 URL**
   - 打开 `https://你的项目名.vercel.app`
   - 应该能看到完整的界面

2. **测试功能**
   - 点击右上角的铃铛图标
   - 应该能看到 6 条异常提醒
   - 点击"去处理"测试页面跳转

3. **检查 API 连接**
   - 打开浏览器开发者工具（F12）
   - 查看 Network 标签
   - 应该能看到对 Render 后端的 API 请求

---

## 🔄 后续更新

每次修改代码后：

1. **提交并推送到 GitHub**
   ```bash
   git add .
   git commit -m "你的更新说明"
   git push
   ```

2. **自动部署**
   - Vercel 和 Render 会自动检测到更新
   - 自动重新部署（约 2-5 分钟）

---

## 🎯 自定义域名（可选）

### Vercel 自定义域名
1. 在 Vercel 项目设置中点击 "Domains"
2. 添加你的域名
3. 按照提示配置 DNS 记录

### Render 自定义域名
1. 在 Render 服务设置中点击 "Custom Domain"
2. 添加你的域名
3. 按照提示配置 DNS 记录

---

## 📊 免费额度说明

### Vercel 免费套餐
- ✅ 无限部署
- ✅ 100GB 带宽/月
- ✅ 自动 HTTPS
- ✅ 全球 CDN

### Render 免费套餐
- ✅ 750 小时/月（足够一个应用全天运行）
- ⚠️ 15 分钟无活动后会休眠
- ⚠️ 首次访问可能需要 30 秒唤醒
- ✅ 自动 HTTPS

**注意**：Render 免费套餐会在无活动时休眠。如果需要保持常驻，可以：
1. 升级到付费套餐（$7/月）
2. 使用定时任务每 10 分钟访问一次 API

---

## 🐛 常见问题

### 问题 1：前端无法连接后端
- 检查 `frontend/.env.production` 中的 URL 是否正确
- 检查 Vercel 环境变量是否配置
- 检查后端 CORS 配置

### 问题 2：Render 部署失败
- 检查 `backend/requirements.txt` 是否存在
- 检查 Python 版本是否兼容
- 查看 Render 部署日志

### 问题 3：首次访问很慢
- Render 免费套餐会休眠，首次访问需要唤醒（30秒）
- 后续访问会很快

### 问题 4：Vercel 构建失败
- 检查 `frontend/package.json` 中的依赖
- 确保 Node.js 版本兼容（建议 18.x）
- 查看 Vercel 构建日志

---

## 📞 获取帮助

- Vercel 文档：https://vercel.com/docs
- Render 文档：https://render.com/docs
- GitHub Issues：在你的仓库中创建 Issue

---

## 🎉 完成！

现在你的应用已经部署成功，可以分享给任何人访问了！

**前端地址**：`https://你的项目名.vercel.app`
**后端 API**：`https://你的后端名.onrender.com`

享受你的在线应用吧！ 🚀
