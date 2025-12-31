#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent.agent_core import AgentCore
from agent.evolver import Evolver
import json
import os


def run():
    goals = [
        {'key': 'accuracy', 'target': 0.9, 'threshold': 0.85, 'required_capability': 'cap_accuracy'},
    ]
    agent = AgentCore('demo-file-agent', goals)
    evolver = Evolver(agent)

    # reset low metrics
    agent.metrics = {'accuracy': 0.0}
    agent.save_state()

    proposals = agent.needs_improvement()
    pending = evolver.propose_and_apply(proposals, require_approval=True)
    pid = pending.get('pending_id')
    print('Pending created:', pending)

    # simulate an approver writing the approval file (approval_{pid}.json in pending dir)
    approval_payload = {'approve': True, 'approved_by': 'file-approver'}
    approval_path = os.path.join(os.path.dirname(__file__), '..', 'agent', 'pending', f'approval_{pid}.json')
    os.makedirs(os.path.dirname(approval_path), exist_ok=True)
    with open(approval_path, 'w', encoding='utf-8') as f:
        json.dump(approval_payload, f, ensure_ascii=False, indent=2)
    # then apply any approved pending
    res = evolver.apply_pending_if_approved()
    print('Apply result:', res)
    print('Agent version after apply:', agent.version)


if __name__ == '__main__':
    run()
