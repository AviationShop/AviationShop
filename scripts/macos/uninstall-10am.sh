#!/bin/bash
set -euo pipefail
LABEL="com.aviationshop.daily-wander"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
launchctl bootout "gui/$(id -u)/${LABEL}" >/dev/null 2>&1 || true
rm -f "$PLIST"
echo "Kaldırıldı: ${LABEL}"
