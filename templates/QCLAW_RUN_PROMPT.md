# QClaw 运行 Prompt 模板

把下面整段发给已经安装好 skill 的 QClaw。

---

你现在要执行 TCM2 闯关报告任务。必须先加载并严格遵守 `tcm2-report-windows` skill。

任务目标：
- 处理 5 个班：QV848、JJ014、VD241、RB881、RL526
- 使用 Windows PowerShell + Chrome CDP 9222
- 若环境支持聊天发送，则逐班发送；若不支持，则至少逐班输出独立 markdown 结果

硬要求：
1. 开始前先运行并发占用检查，优先使用 `scripts/check_tcm2_conflict.ps1`
2. 若发现已有 Hermes/OpenClaw/QClaw/Python/Node 相关任务占用 9222 或正在跑 TCM2/run-monitor/battle-record，则停止并报告 PID/PPID/命令行/冲突依据
3. 启动或检查 Chrome 9222，优先使用 `scripts/start_chrome_9222.ps1`
4. 登录态必须通过 `document.cookie` 验证，要求存在 `user_id=` 与 `token=`
5. 不要在已有 tab 里通过 `location.hash` 或 `Page.navigate(...#/class/detail...)` 强切班；优先 `/json/new` 新开 detail 页
6. 不要只看 URL；detail 页必须同时验证班级名、`战队花名册`、`.el-tabs__item`、`闯关记录` tab、`button.level`
7. detail 页失败时，必须 reload；仍失败则关闭 target 并重开，单班最多 3 轮
8. 点“闯关记录”时只能点 `.el-tabs__item` 页签，不要点侧边栏同名菜单
9. 读取关卡表格时优先读 Vue 父组件数据，并做稳定性校验：至少两次一致；异常关卡至少重试 3 次
10. 活跃学生判断必须基于 `结束闯关时间`，默认窗口按 12:00 / 17:00 双锚点
11. 报告格式必须严格遵守 skill 的 `references/report-rules.md`
12. 若数据明显不可信，不要硬发；重试后仍不稳则标记“需人工复核”

推荐执行方式：
- 单班优先调用 `scripts/run_tcm2_class.ps1`
- 五班本地文件批量可调用 `scripts/run_all_tcm2.ps1`
- 若要逐班聊天发送，就让你自己循环调用单班脚本，并逐班 send_message

最后请给我：
- 每班报告
- 若某班失败，明确写出失败步骤、重试次数、卡住现象
- 全部完成后给一条总结
