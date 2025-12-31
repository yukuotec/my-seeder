# 自我进化 Agent 设计说明（MVP）

目标概览
- 目标驱动：Agent 持续评估目标完成度并迭代自身能力。
- 可版本化：每次进化生成新版本并记录变更日志。
- 可审计：关键操作有日志和回滚点（简单实现：写入状态与 changelog）。

高层模块
- `agent/agent_core.py`：Agent 核心，管理目标、能力、评估函数与状态持久化。
- `agent/evolver.py`：进化器，基于评估结果生成改进建议并应用（版本、模块化改进）。
- `agent/planner.py`：任务规划器（简单策略驱动），生成下步工作项。
- `agent/monitor.py`：监控与报告，记录成本/效能等 KPI 并导出为 JSON。
- `agent/main.py`：运行示例，演示若干次自我评估与进化循环。

数据与持久化
- `agent/state.json`：Agent 当前状态（version、capabilities、metrics）。
- `agent/changelog.md`：每次进化记录变更摘要。

演化策略（MVP）
- 评估差距：若 metric < 目标阈值，生成改进提案（添加能力、优化参数）。
- 应用改进：写入新 `state.json`，更新 `VERSION`，追加 `changelog.md`。
- 主人审批：在 CLI 中模拟审批流程（默认自动批准，用于演示）。

扩展方向（非 MVP）
- 引入 CI/CD、自动 PR、真实运行时迁移、成本计量与收益模型、权限化审批。
