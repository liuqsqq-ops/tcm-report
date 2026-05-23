---
name: tcm2-report-windows
version: 1.0.0
description: Windows 专用 TCM2 闯关报告 skill。适用于 Hermes / OpenClaw / QClaw。遇到 TCM2、闯关报告、战绩、QV848/JJ014/VD241/RB881/RL526、Chrome CDP 9222、逐班发送等任务时必须加载。内含 Windows PowerShell 启动/检查脚本、CDP 提取脚本、报告规则、重试策略、GitHub 分发说明。
---

# TCM2 Report for Windows

这是 **Windows 专用交付版**。目标不是“解释原理”，而是让另一个 agent 直接拿去执行。

如果你是 agent，用户提到以下内容时，必须优先加载本 skill：
- TCM2
- 闯关报告 / 战绩报告
- QV848 / JJ014 / VD241 / RB881 / RL526
- 大侠 / 少侠 / 书童
- Chrome CDP / 9222
- 逐班发送
- 活跃学生

---

## 1. 这份 skill 自带什么

请按需读取这些附带文件：

- `references/windows-operations.md`
  - Windows 下如何启动 Chrome 9222、检查端口、检查冲突、运行脚本
- `references/report-rules.md`
  - 报告格式、首关/后续关规则、活跃学生规则
- `references/qclaw-install.md`
  - 给 QClaw / OpenClaw / Hermes 的安装说明与 GitHub raw URL 模板
- `scripts/tcm2_portable_extract.py`
  - 单班稳定提取脚本，Windows 可运行
- `scripts/start_chrome_9222.ps1`
  - PowerShell 启动脚本
- `scripts/check_tcm2_conflict.ps1`
  - PowerShell 并发占用检查脚本
- `scripts/run_tcm2_class.ps1`
  - PowerShell 单班运行器
- `scripts/run_all_tcm2.ps1`
  - PowerShell 五班批量运行器（输出文件，不负责聊天发送）
- `templates/QCLAW_INSTALL_PROMPT.md`
  - 让 QClaw 从 GitHub URL 安装并执行的提示词模板
- `templates/QCLAW_RUN_PROMPT.md`
  - 让 QClaw 加载 skill 后执行闯关任务的提示词模板

---

## 2. 核心原则

### 2.1 不要只看 URL
detail URL 对了，不等于页面好了。必须同时验证：
- 正文包含班级名
- 正文包含 `战队花名册`
- `.el-tabs__item` 数量 > 0
- 能点 `闯关记录`
- 有 `button.level`

### 2.2 不要在已有 tab 里用 hash 强切班
这些方式不可靠：
- `location.hash = ...`
- `Page.navigate(...#/class/detail...)`
- SPA 内程序化改 hash

优先：
- `/json/new` 新开完整 detail URL
- 或用户手动点击班级

### 2.3 逐班发送，不要攒总包
如果环境支持聊天发送：
- 每完成一个班立刻回一条消息
- 五个班结束后再发总结

如果只是跑脚本文件输出：
- 每班单独输出一个 markdown 文件
- 不要把所有班糊成一份大块文本

### 2.4 活跃学生按“结束闯关时间”判断
不是开始时间，不是别的字段。
默认窗口：12:00 / 17:00 双锚点。

### 2.5 detail 页失败时，重试整个页面，不只是重试表格
如果出现：
- body 空白
- `.el-tabs__item` 为 0
- 没有 `战队花名册`
- 没有 level button

处理方式：
1. reload
2. 仍失败则关闭 target
3. 再 `/json/new` 开新页
4. 单班 detail 页最多 3 轮

---

## 3. 固定班级参数

| 班级 | classId | 阶段 | 人数 |
|------|---------|------|------|
| QV848 | 60018 | 大侠7段 + 书童2段 | 26 |
| JJ014 | 60024 | 少侠6段 + 书童1段 | 21 |
| VD241 | 60056 | 少侠6段 + 书童1段 | 26 |
| RB881 | 120003 | 少侠6段 + 书童1段 | 20 |
| RL526 | 180020 | 少侠4段 | 25 |

推荐顺序：QV848 → JJ014 → VD241 → RB881 → RL526

---

## 4. 执行顺序

### 4.1 开始前先做并发占用检查
优先运行：
- `scripts/check_tcm2_conflict.ps1`

如果发现：
- 已有其他 Hermes / OpenClaw / QClaw / Python / Node 任务在碰 TCM2 / 9222 / run-monitor / battle-record

则：
- 不要继续执行提取
- 把 PID / PPID / 命令行 / 冲突依据报给用户

### 4.2 检查 Chrome 9222
优先运行：
- `scripts/start_chrome_9222.ps1`

要求：
- Chrome 前台可见
- CDP 端口固定 9222
- 独立 user-data-dir

### 4.3 通过 document.cookie 检查登录态
必须确认：
- `user_id=` 存在
- `token=` 存在

不要依赖 `Network.getCookies`。

### 4.4 逐班提取
优先用：
- `scripts/run_tcm2_class.ps1`
- 或脚本内层 `tcm2_portable_extract.py`

### 4.5 五班批量
如果只需要输出本地文件，可用：
- `scripts/run_all_tcm2.ps1`

如果需要聊天逐班发送：
- 让 agent 自己循环调用单班脚本
- 每个班完成就发送

---

## 5. 读取与校验规则

### 5.1 闯关记录页签
只能点 `.el-tabs__item` 里的 `闯关记录`，不能点侧边栏同名菜单。

### 5.2 表格数据优先来源
优先读取可见 `.el-table` 对应 Vue 组件父节点的数据：
- `__vue__.$parent.list`
- `__vue__.$parent.query.lessonId`
- `__vue__.$parent.query.classId`

不要优先用脆弱的 DOM 文本解析。

### 5.3 单关稳定性
点击关卡后：
- 至少读两次
- 结果一致才算稳定
- 异常关卡至少重试 3 次，最多 5 次
- 丢弃空表、半刷新过渡态、明显与人数/百分比矛盾的数据

### 5.4 明显假数据不要发
例如：
- 页面低百分比，你却读成全员完成
- `✅0 🔄0 ❌0` 却显示 100%
- 同关多次读取完全不一致

处理：
- 重试
- 多数一致取值
- 仍不稳则标记“需人工复核”

---

## 6. 报告规则

详细规则见 `references/report-rules.md`。这里记核心：
- 标题必须带真实 `第N周`
- 关卡号保留原始阿拉伯数字形式，如 `第35关卡`
- 百分比保留页面原值
- 每阶段首关无条件列全部 🔄+❌ 名字
- 后续关根据上一关 ❌ 数量决定列名还是只报数
- 已完成（✅）不列名字
- 活跃学生表必须完整

---

## 7. GitHub 分发与安装

如果用户让你从 GitHub 安装本 skill：
1. 读取 `references/qclaw-install.md`
2. 优先使用 **raw SKILL.md URL**
3. raw URL 模板：
   - `https://raw.githubusercontent.com/<owner>/<repo>/<branch>/SKILL.md`

如果安装器支持拉整个 skill 目录，则应保证同目录下附带 `scripts/`、`references/`、`templates/` 一并可用。

如果安装器只能安装单个 `SKILL.md`：
- 仍然安装 `SKILL.md`
- 但要提醒用户同时拉取整个仓库，以便脚本/参考文件可用

---

## 8. 给 QClaw / OpenClaw / Hermes 的工作方式

### 如果是安装 skill
读：`templates/QCLAW_INSTALL_PROMPT.md`

### 如果是执行提取任务
读：`templates/QCLAW_RUN_PROMPT.md`

### 如果只是本地脚本执行
直接调用 PowerShell / Python 脚本即可。

---

## 9. 最后提醒

如果你不确定 detail 页是不是好了，默认它**没好**。
如果你不确定表格是不是稳定，默认它**还不稳**。

TCM2 这个活最怕的不是慢，是**发错**。
宁可多做一次校验，也别拿假数据充完成。
