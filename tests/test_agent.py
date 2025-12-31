import json
import importlib
import os

import agent.agent_core as ac
import agent.evolver as ev


def test_agent_evaluate_and_needs_improvement(tmp_path, monkeypatch):
    # isolate state file
    state_file = tmp_path / "state.json"
    monkeypatch.setattr(ac, 'STATE_FILE', str(state_file))

    goals = [{'key': 'm', 'target': 0.9, 'threshold': 0.85, 'required_capability': 'cap_m'}]
    agent = ac.AgentCore('t', goals)

    metrics = agent.evaluate()
    assert 'm' in metrics

    proposals = agent.needs_improvement()
    assert isinstance(proposals, list)


def test_evolver_pending_and_apply(tmp_path, monkeypatch):
    # redirect evolver files to temp
    monkeypatch.setattr(ev, 'PENDING_FILE', str(tmp_path / 'pending.json'))
    monkeypatch.setattr(ev, 'APPROVAL_FILE', str(tmp_path / 'approval.json'))
    monkeypatch.setattr(ev, 'VERSION_FILE', str(tmp_path / 'VERSION'))
    monkeypatch.setattr(ev, 'CHANGELOG', str(tmp_path / 'changelog.md'))
    monkeypatch.setattr(ev, 'BACKUP_DIR', str(tmp_path / 'backups'))

    # prepare agent with isolated state
    monkeypatch.setattr(ac, 'STATE_FILE', str(tmp_path / 'state.json'))
    goals = [{'key': 'k', 'target': 0.9, 'threshold': 0.85, 'required_capability': 'cap_k'}]
    agent = ac.AgentCore('t', goals)

    evolver = ev.Evolver(agent)
    proposals = agent.needs_improvement()
    res = evolver.propose_and_apply(proposals, require_approval=True)
    assert res.get('pending', False)

    # create approval file and apply
    with open(ev.APPROVAL_FILE, 'w', encoding='utf-8') as f:
        json.dump({'approve': True}, f)

    applied = evolver.apply_pending_if_approved()
    assert applied and 'applied' in applied
