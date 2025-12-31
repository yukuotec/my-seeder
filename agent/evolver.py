import os
import json
from datetime import datetime

CHANGELOG = os.path.join(os.path.dirname(__file__), 'changelog.md')
VERSION_FILE = os.path.join(os.path.dirname(__file__), 'VERSION')
PENDING_FILE = os.path.join(os.path.dirname(__file__), 'pending_proposals.json')
BACKUP_DIR = os.path.join(os.path.dirname(__file__), 'backups')
APPROVAL_FILE = os.path.join(os.path.dirname(__file__), 'approval.json')


def read_version():
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return '0.1.0'


def write_version(v: str):
    with open(VERSION_FILE, 'w', encoding='utf-8') as f:
        f.write(v)


class Evolver:
    def __init__(self, agent_core):
        self.agent = agent_core
        self.version = read_version()
        os.makedirs(BACKUP_DIR, exist_ok=True)

    def increment_version(self):
        parts = [int(x) for x in self.version.split('.')]
        parts[2] += 1
        self.version = f"{parts[0]}.{parts[1]}.{parts[2]}"
        write_version(self.version)
        return self.version

    def _backup_state(self):
        ts = datetime.utcnow().strftime('%Y%m%dT%H%M%S')
        src = os.path.join(os.path.dirname(__file__), 'state.json')
        if os.path.exists(src):
            dst = os.path.join(BACKUP_DIR, f'state_backup_{ts}.json')
            with open(src, 'r', encoding='utf-8') as fsrc, open(dst, 'w', encoding='utf-8') as fdst:
                fdst.write(fsrc.read())
            return dst
        return None

    def propose_and_apply(self, proposals, require_approval: bool = False):
        if not proposals:
            return None

        # Prepare applied capabilities list
        caps = [p.get('required_capability') or f"cap_{p['key']}" for p in proposals]

        if require_approval:
            # write pending proposals for external approval
            pending = {'proposals': proposals, 'caps': caps, 'proposed_at': datetime.utcnow().isoformat()}
            with open(PENDING_FILE, 'w', encoding='utf-8') as f:
                json.dump(pending, f, ensure_ascii=False, indent=2)
            return {'pending': True, 'pending_file': PENDING_FILE}

        # non-approval immediate apply
        backup = self._backup_state()
        applied = []
        for cap in caps:
            self.agent.capabilities[cap] = {'added_at': datetime.utcnow().isoformat(), 'backup': backup}
            applied.append(cap)

        new_ver = self.increment_version()
        self.agent.version = new_ver
        self.agent.save_state()
        self._append_changelog(applied)
        return {'version': new_ver, 'applied': applied}

    def apply_pending_if_approved(self):
        if not os.path.exists(PENDING_FILE):
            return None
        try:
            with open(PENDING_FILE, 'r', encoding='utf-8') as f:
                pending = json.load(f)
        except Exception:
            return None

        # check approval file
        if not os.path.exists(APPROVAL_FILE):
            return {'approved': False, 'reason': 'no approval file'}
        try:
            with open(APPROVAL_FILE, 'r', encoding='utf-8') as f:
                approval = json.load(f)
        except Exception:
            return {'approved': False, 'reason': 'invalid approval file'}

        # approval should match pending timestamp or simply be a boolean approve
        if not approval.get('approve', False):
            return {'approved': False, 'reason': 'explicitly not approved'}

        # apply
        backup = self._backup_state()
        caps = pending.get('caps', [])
        for cap in caps:
            self.agent.capabilities[cap] = {'added_at': datetime.utcnow().isoformat(), 'backup': backup}

        new_ver = self.increment_version()
        self.agent.version = new_ver
        self.agent.save_state()
        self._append_changelog(caps)

        # cleanup pending and approval files
        try:
            os.remove(PENDING_FILE)
        except Exception:
            pass
        try:
            os.remove(APPROVAL_FILE)
        except Exception:
            pass

        return {'version': new_ver, 'applied': caps}

    def rollback_to_backup(self, backup_path: str):
        # restore a backup state file
        if not os.path.exists(backup_path):
            return {'ok': False, 'reason': 'backup not found'}
        dst = os.path.join(os.path.dirname(__file__), 'state.json')
        with open(backup_path, 'r', encoding='utf-8') as fsrc, open(dst, 'w', encoding='utf-8') as fdst:
            fdst.write(fsrc.read())
        # reload agent state
        self.agent.load_state()
        return {'ok': True, 'restored': backup_path}

    def _append_changelog(self, caps):
        entry = f"## {self.version} - {datetime.utcnow().isoformat()}\n"
        entry += '\n'.join([f"- Added capability: {c}" for c in caps]) + '\n\n'
        with open(CHANGELOG, 'a', encoding='utf-8') as f:
            f.write(entry)
