from agent_core import AgentCore
from evolver import Evolver
from monitor import Monitor
from planner import Planner
from approval_server import start_in_thread
import time
import urllib.request
import json


def post_approval(payload, port=8000):
    url = f'http://127.0.0.1:{port}/approve'
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read().decode('utf-8'))


def main():
    # start approval server in background
    start_in_thread(8000)

    goals = [
        {'key': 'accuracy', 'target': 0.9, 'threshold': 0.85, 'required_capability': 'cap_accuracy'},
        {'key': 'efficiency', 'target': 0.8, 'threshold': 0.7, 'required_capability': 'cap_efficiency'},
    ]
    agent = AgentCore('mvp-agent', goals)
    evolver = Evolver(agent)
    monitor = Monitor()
    planner = Planner(agent)

    iterations = 3
    for i in range(1, iterations + 1):
        print(f"--- Iteration {i} ---")
        metrics = agent.evaluate()
        print("Metrics:", metrics)
        monitor.record(i, metrics, notes='post-eval')

        proposals = agent.needs_improvement()
        print("Proposals:", proposals)

        tasks = planner.plan_next()
        print('Planned tasks:', tasks)

        if proposals:
            # create pending proposals, require approval
            pending = evolver.propose_and_apply(proposals, require_approval=True)
            print('Pending proposal created:', pending)

            # simulate owner approving via HTTP (for demo we auto-approve)
            approval_payload = {'approve': True, 'approved_by': 'owner@example.com'}
            try:
                resp = post_approval(approval_payload, port=8000)
                print('Approval server response:', resp)
            except Exception as e:
                print('Approval request failed:', e)

            # attempt to apply pending proposals if approved
            applied = evolver.apply_pending_if_approved()
            print('Apply pending result:', applied)
        else:
            print('No evolution needed')

        time.sleep(0.5)

    print('\nDashboard:', monitor.dashboard())


if __name__ == '__main__':
    main()
