#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent.agent_core import AgentCore
from agent.evolver import Evolver
import json

def main():
    goals = [
        {'key': 'accuracy', 'target': 0.9, 'threshold': 0.85, 'required_capability': 'cap_accuracy'},
        {'key': 'efficiency', 'target': 0.8, 'threshold': 0.7, 'required_capability': 'cap_efficiency'},
    ]

    # reset base state to known low metrics so proposals will be generated
    state_path = os.path.join(os.path.dirname(__file__), '..', 'agent', 'state.json')
    with open(state_path, 'w', encoding='utf-8') as f:
        json.dump({'name':'mvp-agent','version':'0.1.0','goals':goals,'capabilities':{},'metrics':{'accuracy':0.0,'efficiency':0.0}}, f, ensure_ascii=False, indent=2)

    agent = AgentCore('demo-agent', goals)
    agent.evaluate()
    proposals = agent.needs_improvement()
    print('Proposals:', proposals)
    evolver = Evolver(agent)
    res = evolver.propose_and_apply(proposals, require_approval=True)
    print('Pending created:', res)

if __name__ == '__main__':
    main()
