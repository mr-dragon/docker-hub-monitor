# Docker Hub Monitor

一个用于监控 Docker Hub 镜像更新的自动化工具。通过 GitHub Actions 定期检查指定的 Docker 镜像是否有更新，并记录更新日志。

> 一直以来 Github自带版本更新提醒的功能，但 DockerHub 没有，于是有了本项目：DockerHub镜像更新提醒。

## 功能特点

- 🔄 自动检查 Docker Hub 镜像更新
- 📝 生成详细的更新日志
- ⏰ 支持自定义检查频率
- 🔌 支持手动触发检查
- 📦 支持监控多个镜像
- 🚀 完全基于 GitHub Actions，无需额外服务器

## 快速开始

### 1. 复制此仓库

直接 fork 此仓库，设置环境变量后，运行 action 即可。

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

```txt
6053537/portainer-ce
linuxserver/transmission:4.0.5
nevinee/qbittorrent:4.3.9
jxxghp/moviepilot-v2
imaliang/cloud-media-sync
iyuucn/iyuuplus-dev:latest
advplyr/audiobookshelf:latest
hslr/sun-panel:latest
0nlylty/dockercopilot:UGREEN

```

如果没有:版本，默认用latest，格式如下：

1. nginx
2. cloudnas/clouddrive2
3. linuxserver/transmission:4.0.5
4. linuxserver/transmission:UGREEN
5. linuxserver/transmission:latest

他们的版本更新信息链接分别如下：

1. https://hub.docker.com/v2/repositories/library/nginx/tags/latest
2. https://hub.docker.com/v2/repositories/linuxserver/transmission/tags/4.0.5
3. https://hub.docker.com/v2/repositories/0nlylty/dockercopilot/tags/UGREEN
4. https://hub.docker.com/v2/repositories/linuxserver/transmission/tags/latest

## 更新日志

📋 [点击查看最新的镜像更新记录](logs/changelog.md)

更新日志记录了所有镜像的检查结果，包括：
- 检查执行时间
- 每个镜像的当前更新时间
- 上次检查时间
- 更新状态

## 配置通知（可选）

### 企业微信机器人通知(其他机器人通用)

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

### 通知内容示例

#### 企业微信通知

```text
## 检查结果

### nginx
- 当前更新时间: 2024-03-15 18:20:39 +0800
- 上次检查时间: 2024-03-14 23:45:22 +0800
- 状态: 有更新

### cloudnas/clouddrive2
- 当前更新时间: 2024-03-15 17:15:30 +0800
- 上次检查时间: 2024-03-15 17:15:30 +0800
- 状态: 无更新
```

#### 邮件通知

邮件主题：Docker镜像更新通知
邮件内容格式与企业微信通知相同

## 完整的 Secrets 配置列表

| Secret 名称      | 必填 | 说明                                       |
| ---------------- | ---- | ------------------------------------------ |
| `PAT`            | 是   | GitHub Personal Access Token，用于提交更新 |
| `WEBHOOK_URL`    | 否   | 企业微信机器人 Webhook 地址                |
| `EMAIL_FROM`     | 否   | 发送通知的 Gmail 邮箱地址                  |
| `EMAIL_PASSWORD` | 否   | Gmail 应用专用密码                         |
| `EMAIL_TO`       | 否   | 接收通知的邮箱地址                         |

## 常见问题

### Q: 如何禁用某种通知方式？
A: 只需不配置对应的 Secrets 即可。例如，如果不配置 `WEBHOOK_URL`，就不会发送企业微信通知。

### Q: 为什么没有收到通知？

A: 检查以下几点：
1. 确认已正确配置相应的 Secrets
2. 对于企业微信，确认 Webhook 地址是否有效
3. 对于邮件通知：
   - 确认 Gmail 应用专用密码配置正确
   - 检查接收邮箱的垃圾邮件文件夹
   - 确认 Gmail 账户的安全设置允许应用访问

### Q: 可以同时使用多种通知方式吗？

A: 可以。只要配置了相应的 Secrets，系统会同时发送所有已配置的通知。
