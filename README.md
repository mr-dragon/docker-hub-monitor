# Docker Hub Monitor

一个用于监控 Docker Hub 镜像更新的自动化工具。通过 GitHub Actions 定期检查指定的 Docker 镜像是否有更新，并记录更新日志。

## 功能特点

- 🔄 自动检查 Docker Hub 镜像更新
- 📝 生成详细的更新日志
- ⏰ 支持自定义检查频率
- 🔌 支持手动触发检查
- 📦 支持监控多个镜像
- 🚀 完全基于 GitHub Actions，无需额外服务器

## 快速开始

### 1. 复制此仓库

点击 "Use this template" 按钮创建你自己的仓库，或者直接 fork 此仓库。

### 2. 配置 Personal Access Token

1. 访问 [GitHub Settings - Tokens](https://github.com/settings/tokens)
2. 点击 "Generate new token (classic)"
3. 设置 token 名称（如：DOCKER_HUB_MONITOR）
4. 选择权限范围：至少需要 `repo` 权限
5. 生成并复制 token
6. 在你的仓库中添加 Secret：
   - 进入仓库的 Settings -> Secrets and variables -> Actions
   - 点击 "New repository secret"
   - 名称：`PAT`
   - 值：刚才复制的 token

### 3. 配置要监控的镜像

编辑 `images.txt` 文件，每行添加一个要监控的镜像，例如：

## 配置通知（可选）

### 企业微信通知

1. 在企业微信群中添加机器人：
   - 进入群聊 -> 点击右上角设置图标
   - 选择"群机器人" -> "添加机器人"
   - 设置机器人名称并获取 Webhook 地址

2. 添加 Webhook 到仓库 Secrets：
   - 进入仓库的 Settings -> Secrets and variables -> Actions
   - 点击 "New repository secret"
   - 名称：`WEBHOOK_URL`
   - 值：复制的 Webhook 地址

### 邮件通知

支持通过 Gmail 发送更新通知邮件。需要配置以下 Secrets：

1. 配置发送邮箱（Gmail）：
   - 进入 [Google Account Security](https://myaccount.google.com/security)
   - 开启两步验证
   - 生成应用专用密码：Security -> 2-Step Verification -> App passwords
   - 选择 "Mail" 和设备类型，生成密码

2. 添加邮箱配置到仓库 Secrets：
   - `EMAIL_FROM`: 发送通知的 Gmail 邮箱地址
   - `EMAIL_PASSWORD`: Gmail 应用专用密码
   - `EMAIL_TO`: 接收通知的邮箱地址
