# tcm2-report-windows

Windows 专用的 TCM2 闯关报告 skill，适用于：
- Hermes Agent
- OpenClaw
- QClaw

这个仓库的目标是：
- 用 Windows 原生命令/PowerShell 启动 Chrome 9222
- 在 TCM2 已登录的前提下，通过 CDP 稳定提取单班/五班闯关报告
- 给 agent 提供可安装的 skill + 可直接运行的脚本 + 给 QClaw 的安装/运行 prompt

## 目录结构

- `SKILL.md`：主 skill 文件
- `references/`：规则、Windows 操作说明、QClaw 安装说明
- `scripts/`：PowerShell + Python 可执行脚本
- `templates/`：给 QClaw / OpenClaw / Hermes 的提示词模板

## 推荐安装方式

### 方式 1：让支持 skill URL 安装的 agent 直接安装
使用 raw URL：

```text
https://raw.githubusercontent.com/<owner>/<repo>/<branch>/SKILL.md
```

### 方式 2：整个仓库作为 skill 仓库
如果 agent 支持 GitHub repo/tap/source 安装，直接添加整个仓库。

## Windows 前提

- Windows 10/11
- Python 3
- Chrome 已安装
- TCM2 已登录
- `websocket-client` 已安装

```powershell
py -m pip install websocket-client
```

## 最常用命令

### 启动 Chrome 9222
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start_chrome_9222.ps1
```

### 检查冲突
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check_tcm2_conflict.ps1
```

### 跑单班
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_tcm2_class.ps1 -ClassName QV848
```

### 跑五班并输出到 reports/
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_all_tcm2.ps1
```

## 给 QClaw 的推荐用法

1. 先让 QClaw 安装这个 skill
2. 再给它 `templates/QCLAW_RUN_PROMPT.md` 的内容
3. 若需要真实逐班聊天发送，让 QClaw 每班调用一次单班脚本，并逐班 send_message

## 注意

- 当前最稳的是：**脚本负责提取，agent 负责逐班发送**
- 不要在已有 tab 里靠 hash 切班
- 不要只看 URL 判断 detail 页成功
- 不要把 5 个班攒成一条消息
