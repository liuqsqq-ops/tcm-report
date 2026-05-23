# QClaw / OpenClaw / Hermes 安装说明

## GitHub raw URL 模板
把 `<owner>`、`<repo>`、`<branch>` 换成真实值：

```text
https://raw.githubusercontent.com/<owner>/<repo>/<branch>/SKILL.md
```

## 对 Hermes Agent
如果支持直接安装 skill URL，可用：
```bash
hermes skills install https://raw.githubusercontent.com/<owner>/<repo>/<branch>/SKILL.md
```

## 对 QClaw / OpenClaw
如果它支持 Hermes/OpenClaw 风格 skill 安装：
- 优先给它 raw `SKILL.md` URL
- 同时确保它能访问整个 GitHub 仓库，以便读取 `scripts/`、`references/`、`templates/`

## 推荐做法
1. 安装 skill
2. 验证 skill 名字为 `tcm2-report-windows`
3. 再投喂执行 prompt

## 如果安装器只能安装单文件
那它可能只能装进 `SKILL.md` 本体。
这种情况下：
- 让 agent 安装 raw `SKILL.md`
- 再让 agent 读取仓库里的相对文件，或直接 clone / 下载整个仓库

## 推荐仓库根目录
建议把 skill 做成仓库根目录就是 skill 根：
- `SKILL.md`
- `scripts/`
- `references/`
- `templates/`

这样 raw URL 最干净，也方便别的 agent 理解。
