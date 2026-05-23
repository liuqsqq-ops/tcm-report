# Windows 操作说明

## 1. 安装依赖
```powershell
py -m pip install websocket-client
```

## 2. 启动 Chrome 9222
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start_chrome_9222.ps1
```

该脚本会：
- 关闭现有 chrome.exe
- 寻找 Chrome 安装路径
- 用 9222 启动 Chrome
- 使用独立 user-data-dir

## 3. 检查并发冲突
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check_tcm2_conflict.ps1
```

输出重点看：
- 9222 监听者
- 命令行里是否含 tcm2 / battle-record / run-monitor / hermes / openclaw / qclaw

如发现冲突，不要继续跑提取。

## 4. 跑单班
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_tcm2_class.ps1 -ClassName QV848
```

可选参数：
- `-ClassId`
- `-Total`
- `-OutFile`
- `-SkipConflictCheck`
- `-SkipChromeStart`

## 5. 跑五班
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_all_tcm2.ps1
```

默认输出到：
- `./reports/QV848.md`
- `./reports/JJ014.md`
- `./reports/VD241.md`
- `./reports/RB881.md`
- `./reports/RL526.md`

## 6. 登录态要求
脚本不会帮你登录 TCM2。
必须先在 Chrome 里把 TCM2 登录好。

## 7. 最稳的人工配合方式
如果某个班 detail 页反复加载异常：
1. 保持 Chrome 在前台
2. 你手动打开 TCM2
3. 手动点进目标班级
4. 再让 agent/脚本继续读取
