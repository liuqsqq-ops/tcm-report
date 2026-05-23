# GitHub 上传说明

## 推荐仓库名
- `tcm2-report-windows`
- `tcm2-skill-windows`

## 推荐仓库结构
仓库根目录直接就是 skill 根目录：

- `SKILL.md`
- `README.md`
- `references/`
- `scripts/`
- `templates/`

这样安装 raw URL 时最干净。

## raw URL 模板
上传 GitHub 后，把：
- `<owner>` 换成你的 GitHub 用户名/组织
- `<repo>` 换成仓库名
- `<branch>` 通常是 `main`

```text
https://raw.githubusercontent.com/<owner>/<repo>/<branch>/SKILL.md
```

## 推荐给 agent 的最短指令
### 安装
请从这个 URL 安装 skill：
`https://raw.githubusercontent.com/<owner>/<repo>/<branch>/SKILL.md`

### 执行
加载 `tcm2-report-windows` skill，然后按 skill 的 Windows 脚本和规则执行 TCM2 闯关报告。

## 最佳实践
如果 agent 支持：
- 安装 `SKILL.md`
- 同时读取同仓库下 `scripts/`、`references/`、`templates/`

就能把这套 skill 发挥完整。
