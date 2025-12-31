#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
import json
import urllib.request
from agent.approval_server import start_in_thread
from agent.agent_core import AgentCore
from agent.evolver import Evolver


def run_demo(port=8002):
    # start server
    start_in_thread(port)
    time.sleep(0.2)

    # create a baseline state and pending
    goals = [
        {'key': 'accuracy', 'target': 0.9, 'threshold': 0.85, 'required_capability': 'cap_accuracy'},
    ]
    agent = AgentCore('demo-agent', goals)
    evolver = Evolver(agent)

    # force low metrics and create pending
    agent.metrics = {'accuracy': 0.0}
    agent.save_state()
    proposals = agent.needs_improvement()
    pending = evolver.propose_and_apply(proposals, require_approval=True)
    pid = pending.get('pending_id')
    print('Created pending:', pending)

    # list pending via server
    with urllib.request.urlopen(f'http://127.0.0.1:{port}/pending') as resp:
        print('Pending list response:', resp.read().decode())

    # send approve request
    url = f'http://127.0.0.1:{port}/approve'
    body = json.dumps({'pending_id': pid, 'approve': True, 'by': 'demo'}).encode('utf-8')
    req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        print('Approve response:', resp.read().decode())

    # wait and show final state
    time.sleep(0.2)
    print('Final agent state version:', agent.version)


if __name__ == '__main__':
    run_demo()
