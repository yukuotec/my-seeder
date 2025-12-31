from typing import List, Dict, Any


class Planner:
    def __init__(self, agent_core):
        self.agent = agent_core

    def plan_next(self) -> List[Dict[str, Any]]:
        # 简单计划：基于需要改进的项目返回任务清单
        needs = self.agent.needs_improvement()
        tasks = []
        for n in needs:
            tasks.append({'task': f"implement {n['required_capability']}", 'for': n['key']})
        return tasks
