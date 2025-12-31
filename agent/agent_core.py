import json
import os
from typing import Dict, Any, List

STATE_FILE = os.path.join(os.path.dirname(__file__), 'state.json')


class AgentCore:
    def __init__(self, name: str, goals: List[Dict[str, Any]]):
        self.name = name
        self.goals = goals
        self.version = '0.1.0'
        self.capabilities: Dict[str, Any] = {}
        self.metrics: Dict[str, float] = {}
        self.load_state()

    def load_state(self):
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.version = data.get('version', self.version)
            self.capabilities = data.get('capabilities', self.capabilities)
            self.metrics = data.get('metrics', self.metrics)

    def save_state(self):
        data = {
            'name': self.name,
            'version': self.version,
            'goals': self.goals,
            'capabilities': self.capabilities,
            'metrics': self.metrics,
        }
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def evaluate(self) -> Dict[str, float]:
        # 简单评估：根据已知能力调整指标（MVP 模拟）
        results = {}
        for g in self.goals:
            key = g['key']
            target = g['target']
            base = self.metrics.get(key, 0.0)
            # 如果有相关能力，略微提升
            if g.get('required_capability') in self.capabilities:
                base += 0.3
            else:
                base += 0.05
            # clamp
            base = min(base, 1.0)
            results[key] = base
            self.metrics[key] = base
        self.save_state()
        return results

    def needs_improvement(self) -> List[Dict[str, Any]]:
        proposals = []
        for g in self.goals:
            key = g['key']
            threshold = g.get('threshold', g['target'])
            val = self.metrics.get(key, 0.0)
            if val < threshold:
                proposals.append({
                    'key': key,
                    'current': val,
                    'target': g['target'],
                    'required_capability': g.get('required_capability')
                })
        return proposals
