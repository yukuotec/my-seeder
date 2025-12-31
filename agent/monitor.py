import json
import os
from typing import Dict, Any

MONITOR_FILE = os.path.join(os.path.dirname(__file__), 'monitor.json')


class Monitor:
    def __init__(self):
        self.path = MONITOR_FILE
        self.data = {'iterations': []}
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except Exception:
                self.data = {'iterations': []}

    def record(self, iteration: int, metrics: Dict[str, float], notes: str = ''):
        self.data['iterations'].append({'iteration': iteration, 'metrics': metrics, 'notes': notes})
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def dashboard(self) -> Dict[str, Any]:
        # return a lightweight KPI summary
        last = self.data['iterations'][-1] if self.data['iterations'] else {}
        return {'last_iteration': last}
