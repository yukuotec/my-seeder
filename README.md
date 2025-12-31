# my-seeder — 自我进化 Agent 示例

运行示例：

```bash
python3 agent/main.py
```

该 MVP 仅用于演示：评估 → 生成改进建议 → 应用改进（版本+changelog）→ 记录监控数据。

快速推送到你的 GitHub 仓库：

```bash
git init
git add .
git commit -m "Initial MVP: self-evolving agent"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

CI: 项目包含 GitHub Actions workflow（`.github/workflows/ci.yml`），在每次 push/PR 时运行 `pytest`。

CLI: 新增 `agent/cli.py`，支持以下命令（在仓库根目录运行）：

```bash
# 查看 Agent 当前状态
python3 agent/cli.py status

# 列出备份
python3 agent/cli.py list-backups

# 显示挂起的 proposals
python3 agent/cli.py show-pending

# 创建本地审批（写入 approval.json）
python3 agent/cli.py approve --by owner@example.com

# 应用挂起（如果已经审批）
python3 agent/cli.py apply-pending

# 回滚到某个备份文件（backup 文件名或完整路径）
python3 agent/cli.py rollback state_backup_2025...
```

