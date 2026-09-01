#!/usr/bin/env python3
"""Read botdefense-worker archive (GET /last). Requires WORKER_SECRET env."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

WORKER_URL = os.environ.get(
    "BOTDEFENSE_WORKER_URL",
    "https://botdefense-worker.oevitan.workers.dev",
).rstrip("/")
UA = "Mozilla/5.0 (compatible; AviationShopBotDefenseReport/1.0)"


def main() -> int:
    secret = os.environ.get("WORKER_SECRET", "").strip()
    if not secret:
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": "WORKER_SECRET ortam değişkeni yok. Cursor environment secret olarak ekle.",
                }
            ),
            file=sys.stderr,
        )
        return 2

    req = urllib.request.Request(
        f"{WORKER_URL}/last",
        headers={
            "Authorization": f"Bearer {secret}",
            "User-Agent": UA,
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:400]
        print(
            json.dumps({"ok": False, "error": f"HTTP {exc.code}", "body": body}),
            file=sys.stderr,
        )
        return 1
    except Exception as exc:  # noqa: BLE001 — surface any network failure as JSON
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1

    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
