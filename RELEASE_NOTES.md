# Release v0.1.0

Date: 2025-12-31

## Overview
Initial MVP release of the self-evolving Agent. The project demonstrates a minimal end-to-end loop:
- Goal-driven evaluation
- Proposal generation for capability improvements
- Approval flow (HTTP approval server)
- Applying changes with versioning, changelog and backup/rollback support
- Monitoring and simple KPI recording

## Notable Files / Modules
- `agent/agent_core.py`: Agent core (state, evaluation, proposals)
- `agent/evolver.py`: Evolver that generates/apply proposals, supports pending approvals and rollback backups
- `agent/approval_server.py`: Small HTTP server to receive approval payloads
- `agent/planner.py`: Simple planner to convert proposals into tasks
- `agent/monitor.py`: Records metrics to `agent/monitor.json`
- `agent/main.py`: Demo runner that simulates iterations and approval flow

## Changelog (excerpt)

From `agent/changelog.md`:

```
## 0.1.1 - 2025-12-31T14:31:23.917651
- Added capability: cap_accuracy
- Added capability: cap_efficiency

## 0.1.2 - 2025-12-31T14:31:24.422473
- Added capability: cap_accuracy
- Added capability: cap_efficiency

## 0.1.3 - 2025-12-31T14:31:24.924801
- Added capability: cap_accuracy
- Added capability: cap_efficiency

```

## How to publish this release (two options)

1) Using GitHub CLI (`gh`) — recommended if you have `gh` authenticated:

```bash
gh release create v0.1.0 --title "v0.1.0" --notes-file RELEASE_NOTES.md
```

2) Using `curl` with a GitHub token (export `GITHUB_TOKEN` first):

```bash
curl -X POST -H "Authorization: token $GITHUB_TOKEN" -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/yukuotec/my-seeder/releases \
  -d '{"tag_name":"v0.1.0","name":"v0.1.0","body":"'"$(sed ':a;N;$!ba;s/"/\\"/g' RELEASE_NOTES.md)"'","draft":false,"prerelease":false}'
```

Replace `yukuotec/my-seeder` in the URL if your repository path differs.
