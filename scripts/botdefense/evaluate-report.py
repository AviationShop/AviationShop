#!/usr/bin/env python3
"""Decide whether today's bot-defense run needs a human report (silence principle)."""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timezone
from typing import Any


SAFE_NAME_HINTS = (
    "türk telekom",
    "turk telekom",
    "superonline",
    "starlink",
    "google",
    "facebook",
    "proton",
    "meta",
)


def _records(payload: dict[str, Any]) -> list[dict[str, Any]]:
    last = payload.get("last")
    if isinstance(last, dict) and "date" in last:
        # /last returns only the newest; optional full log may be under other keys
        runs = payload.get("runs") or payload.get("log") or payload.get("value")
        if isinstance(runs, str):
            try:
                runs = json.loads(runs)
            except json.JSONDecodeError:
                runs = None
        if isinstance(runs, list) and runs:
            return [r for r in runs if isinstance(r, dict) and "date" in r]
        return [last]
    if isinstance(payload.get("value"), str):
        try:
            arr = json.loads(payload["value"])
            if isinstance(arr, list):
                return [r for r in arr if isinstance(r, dict) and "date" in r]
        except json.JSONDecodeError:
            pass
    return []


def _bot_volume(rec: dict[str, Any]) -> int:
    stats = rec.get("stats") or {}
    return int(stats.get("block") or 0) + int(stats.get("challenge") or 0)


def _org_names(items: list[dict[str, Any]]) -> list[str]:
    return [str(i.get("org") or "") for i in items]


def evaluate(payload: dict[str, Any], today: str | None = None) -> dict[str, Any]:
    today = today or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    records = sorted(_records(payload), key=lambda r: r.get("date", ""))
    if not records:
        return {
            "notify": True,
            "reasons": ["archive_empty"],
            "message": (
                "Bot savunması koşuyor ama raporunu arşivleyemiyor olabilir "
                "(Shopify yazma izni / Worker arşivi). Ne eklediğini göremiyorum."
            ),
        }

    by_date = {r["date"]: r for r in records}
    current = by_date.get(today)
    if not current:
        last = records[-1]
        return {
            "notify": True,
            "reasons": ["missing_today"],
            "message": (
                f"Bugünün bot savunması koşumu yok. Son koşum: {last.get('date')} "
                f"({last.get('ts')})."
            ),
            "last_date": last.get("date"),
        }

    prev_dates = [d for d in by_date if d < today]
    previous = by_date[prev_dates[-1]] if prev_dates else None
    reasons: list[str] = []
    lines: list[str] = []

    auto_block = current.get("auto_block") or []
    auto_chal = current.get("auto_challenge") or []
    review = current.get("review") or []
    block_patch = current.get("block_patch") or {}
    chal_patch = current.get("challenge_patch") or {}

    if auto_block or auto_chal:
        reasons.append("action")
        for item in auto_block:
            applied = block_patch.get("applied")
            lines.append(
                f"Engel listesine eklendi: {item.get('org')} "
                f"(~{item.get('count')} istek / 3s)"
                + (" — kurala yazıldı." if applied else " — yazma teyidi yok.")
            )
        for item in auto_chal:
            applied = chal_patch.get("applied")
            lines.append(
                f"Doğrulama listesine eklendi: {item.get('org')} "
                f"(~{item.get('count')} istek / 3s)"
                + (" — kurala yazıldı." if applied else " — yazma teyidi yok.")
            )

    if review:
        reasons.append("review")
        for item in review:
            lines.append(
                f"İnceleme: {item.get('org')} (~{item.get('count')} istek). "
                "Ne yapalım — dokunmayalım mı, doğrulamaya mı alalım?"
            )

    if block_patch.get("ok") is False or chal_patch.get("ok") is False:
        reasons.append("patch_failed")
        lines.append(
            "Cloudflare kural güncellemesini reddetti. Bugünkü ekleme tamamlanmamış olabilir."
        )

    if previous:
        cur_v = _bot_volume(current)
        prev_v = _bot_volume(previous)
        if prev_v > 0 and cur_v >= prev_v * 1.5:
            reasons.append("volume_spike")
            lines.append(
                f"Bot hacmi (engel+doğrulama) düne göre belirgin arttı: "
                f"{prev_v:,} → {cur_v:,}."
            )

    if current.get("ip_lookup_ok") is False:
        reasons.append("ip_lookup")
        lines.append(
            "IP sınıflandırma servisi bugün çalışmadı — karar kalitesi düşük."
        )

    for name in _org_names(auto_block) + _org_names(auto_chal):
        low = name.lower()
        if any(h in low for h in SAFE_NAME_HINTS):
            reasons.append("safe_list_hit")
            lines.append(
                f"DİKKAT: güvenli listede olması gereken bir ağ işlem görmüş görünüyor: {name}."
            )

    # Monday weekly summary (UTC date)
    try:
        weekday = date.fromisoformat(today).weekday()  # Mon=0
    except ValueError:
        weekday = -1
    if weekday == 0:
        reasons.append("monday_summary")
        week = [by_date[d] for d in sorted(by_date) if d >= _days_ago(today, 6) and d <= today]
        vols = [_bot_volume(r) for r in week]
        added = []
        for r in week:
            for item in (r.get("auto_challenge") or []) + (r.get("auto_block") or []):
                added.append(f"{r.get('date')}: {item.get('org')}")
        rc = current.get("rule_counts") or {}
        lines.append(
            "Haftalık özet — "
            f"bot hacmi min/max: {min(vols) if vols else 0:,}/{max(vols) if vols else 0:,}; "
            f"eklenen ağlar: {len(added)}; "
            f"kurallar: engel {rc.get('block')}, doğrulama {rc.get('challenge')}."
        )
        if added:
            lines.append("Eklenenler: " + "; ".join(added[-12:]))

    notify = bool(reasons)
    message = "\n".join(lines).strip()
    if notify and not message:
        message = current.get("text") or "Bot savunması kaydı var; detay için arşive bak."

    return {
        "notify": notify,
        "reasons": reasons,
        "date": today,
        "message": message,
        "stats": current.get("stats"),
        "rule_counts": current.get("rule_counts"),
        "auto_block": auto_block,
        "auto_challenge": auto_chal,
        "review": review,
        "text": current.get("text"),
    }


def _days_ago(day: str, n: int) -> str:
    d = date.fromisoformat(day)
    from datetime import timedelta

    return (d - timedelta(days=n)).isoformat()


def main() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        print(json.dumps({"ok": False, "error": "stdin boş — fetch-last.py çıktısını pipe et"}))
        return 2
    payload = json.loads(raw)
    result = evaluate(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not result.get("notify") else 10


if __name__ == "__main__":
    raise SystemExit(main())
