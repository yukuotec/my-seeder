#!/usr/bin/env python3
import argparse
import os
import json
from evolver import Evolver, PENDING_FILE, APPROVAL_FILE, BACKUP_DIR
from agent_core import AgentCore


def load_agent():
    # lightweight: create AgentCore with no goals to inspect state
    agent = AgentCore('cli-agent', [])
    return agent


def cmd_status(args):
    agent = load_agent()
    print('Agent name:', agent.name)
    print('Version:', getattr(agent, 'version', 'unknown'))
    print('Capabilities:', json.dumps(agent.capabilities, indent=2, ensure_ascii=False))
    print('Metrics:', json.dumps(agent.metrics, indent=2, ensure_ascii=False))
    if os.path.exists(PENDING_FILE):
        print('\nPending proposals found at', PENDING_FILE)
    else:
        print('\nNo pending proposals')


def cmd_list_backups(args):
    path = BACKUP_DIR
    if not os.path.exists(path):
        print('No backups directory:', path)
        return
    files = sorted(os.listdir(path))
    if not files:
        print('No backup files')
        return
    for f in files:
        print(f)


def cmd_show_pending(args):
    if not os.path.exists(PENDING_FILE):
        print('No pending proposals')
        return
    with open(PENDING_FILE, 'r', encoding='utf-8') as f:
        print(f.read())


def cmd_approve(args):
    payload = {'approve': True, 'approved_by': args.by}
    with open(APPROVAL_FILE, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print('Wrote approval to', APPROVAL_FILE)


def cmd_apply_pending(args):
    agent = load_agent()
    evolver = Evolver(agent)
    res = evolver.apply_pending_if_approved()
    print('Result:', res)


def cmd_rollback(args):
    agent = load_agent()
    evolver = Evolver(agent)
    backup = args.file
    if not os.path.exists(backup):
        # try in backup dir
        candidate = os.path.join(BACKUP_DIR, backup)
        if os.path.exists(candidate):
            backup = candidate
        else:
            print('Backup not found:', args.file)
            return
    res = evolver.rollback_to_backup(backup)
    print('Rollback result:', res)


def main():
    p = argparse.ArgumentParser(description='Agent CLI for status, approval and rollback')
    sub = p.add_subparsers(dest='cmd')

    sub.add_parser('status')
    sub.add_parser('list-backups')
    sub.add_parser('show-pending')

    ap = sub.add_parser('approve')
    ap.add_argument('--by', default='owner')

    sub.add_parser('apply-pending')

    rb = sub.add_parser('rollback')
    rb.add_argument('file', help='backup file name or full path')

    args = p.parse_args()
    if not args.cmd:
        p.print_help()
        return

    if args.cmd == 'status':
        cmd_status(args)
    elif args.cmd == 'list-backups':
        cmd_list_backups(args)
    elif args.cmd == 'show-pending':
        cmd_show_pending(args)
    elif args.cmd == 'approve':
        cmd_approve(args)
    elif args.cmd == 'apply-pending':
        cmd_apply_pending(args)
    elif args.cmd == 'rollback':
        cmd_rollback(args)


if __name__ == '__main__':
    main()
