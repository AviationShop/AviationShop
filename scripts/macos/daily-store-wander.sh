#!/bin/bash
# Runs the Aviation Shop wander on this Mac via Cursor CLI.
set -euo pipefail

REPO_DIR="${AVIATIONSHOP_REPO:-}"
if [[ -z "$REPO_DIR" ]]; then
  REPO_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi
cd "$REPO_DIR"

export PATH="$HOME/.local/bin:$HOME/.cursor/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"

if ! command -v agent >/dev/null 2>&1; then
  echo "Cursor CLI (agent) not found. Install: curl https://cursor.com/install -fsS | bash" >&2
  echo "Then run: agent login" >&2
  exit 1
fi

DATE="$(date +%Y-%m-%d)"
REPORT="$HOME/Desktop/aviationshop-wander-${DATE}.md"
mkdir -p "$HOME/Desktop"

PROMPT="$(cat <<EOF
Wander the LIVE Aviation Shop storefront today on THIS computer's browser (not a headless datacenter browser).

Follow ${REPO_DIR}/.cursor/automations/daily-store-wander.md exactly.
Use ${REPO_DIR}/.cursor/automations/wander-seeds.json only as starting points.
Read ${HOME}/.aviationshop-wander-log.md if it exists so you do not repeat products from the last 14 days.

Store: https://www.aviationshop.com
Every browser/curl request MUST include User-Agent substring Cursor-Store-Wander (Cloudflare skip rule).
Do not checkout, do not log in, do not open a pull request.
Write the daily report in Turkish for Onur.
Also write the same report to ${REPORT}
Append today's visited URLs to ${HOME}/.aviationshop-wander-log.md
EOF
)"

LOG_DIR="${HOME}/Library/Logs/aviationshop"
mkdir -p "$LOG_DIR"

agent -p "$PROMPT" --force --output-format text | tee "${LOG_DIR}/wander-${DATE}.log"
