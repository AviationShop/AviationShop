#!/bin/bash
# Install a macOS LaunchAgent that runs the store wander every day at 10:00 local time.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
LABEL="com.aviationshop.daily-wander"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
SCRIPT="${REPO_DIR}/scripts/macos/daily-store-wander.sh"
LOG_DIR="$HOME/Library/Logs/aviationshop"

chmod +x "$SCRIPT" "${REPO_DIR}/scripts/macos/uninstall-10am.sh"
mkdir -p "$HOME/Library/LaunchAgents" "$LOG_DIR"

export PATH="$HOME/.local/bin:$HOME/.cursor/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"
if ! command -v agent >/dev/null 2>&1; then
  echo "Cursor CLI yok. Önce şunu çalıştır:"
  echo "  curl https://cursor.com/install -fsS | bash"
  echo "  agent login"
  exit 1
fi

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>${SCRIPT}</string>
  </array>
  <key>WorkingDirectory</key>
  <string>${REPO_DIR}</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>AVIATIONSHOP_REPO</key>
    <string>${REPO_DIR}</string>
    <key>PATH</key>
    <string>${HOME}/.local/bin:${HOME}/.cursor/bin:/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin</string>
  </dict>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>10</integer>
    <key>Minute</key>
    <integer>0</integer>
  </dict>
  <key>RunAtLoad</key>
  <false/>
  <key>StandardOutPath</key>
  <string>${LOG_DIR}/launchd.out.log</string>
  <key>StandardErrorPath</key>
  <string>${LOG_DIR}/launchd.err.log</string>
</dict>
</plist>
EOF

launchctl bootout "gui/$(id -u)/${LABEL}" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
launchctl enable "gui/$(id -u)/${LABEL}" >/dev/null 2>&1 || true

echo "Kuruldu: her gün 10:00 (bu Mac’in saat dilimi)"
echo "Plist: $PLIST"
echo "Rapor: ~/Desktop/aviationshop-wander-YYYY-MM-DD.md"
echo "Kaldırmak için: ${REPO_DIR}/scripts/macos/uninstall-10am.sh"
echo
echo "Şimdi bir kez dene:"
echo "  ${SCRIPT}"
