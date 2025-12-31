#!/usr/bin/env bash
set -euo pipefail

# publish_release.sh
# Usage:
#   ./scripts/publish_release.sh gh    # use gh CLI
#   ./scripts/publish_release.sh curl  # use curl + GITHUB_TOKEN

MODE=${1:-gh}
REPO="yukuotec/my-seeder"
TAG="v0.1.0"
NOTES_FILE="RELEASE_NOTES.md"

if [ "$MODE" = "gh" ]; then
  if ! command -v gh >/dev/null 2>&1; then
    echo "gh CLI not found; install from https://github.com/cli/cli" >&2
    exit 1
  fi
  gh release create "$TAG" --repo "$REPO" --title "$TAG" --notes-file "$NOTES_FILE"
  exit 0
fi

if [ "$MODE" = "curl" ]; then
  if [ -z "${GITHUB_TOKEN:-}" ]; then
    echo "Please set GITHUB_TOKEN environment variable with repo access" >&2
    exit 1
  fi
  BODY=$(python3 - <<PY
import json,sys
with open('RELEASE_NOTES.md','r',encoding='utf-8') as f:
    data=f.read()
print(json.dumps({
  'tag_name':'v0.1.0',
  'name':'v0.1.0',
  'body':data,
  'draft':False,
  'prerelease':False
}))
PY
)

curl -X POST -H "Authorization: token $GITHUB_TOKEN" -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/$REPO/releases" -d "$BODY"
  
exit 0
