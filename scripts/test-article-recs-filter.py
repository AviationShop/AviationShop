#!/usr/bin/env python3
"""Mirrors theme/sections/article-news.liquid related-recs allow/deny rule."""

AC_TOKS = (
    "boeing,airbus,embraer,cessna,concorde,mcdonnell,md-11,md11,dreamliner,"
    "a220,a320,a321,a330,a340,a350,a380,737,747,757,767,777,787,727,"
    "fighter,f-16,f16,-designed"
).split(",")


def handle_allowed(handle: str) -> bool:
    h = handle.strip().lower()
    if not h or "latam" in h:
        return False
    if "-enthusiasts" in h or "-airlines" in h or "-airways" in h:
        return True
    return any(tok in h for tok in AC_TOKS)


def related_handles(tags: list[str]) -> list[str]:
    seen: list[str] = []
    for tag in tags:
        if "collection:related:" not in tag:
            continue
        handle = tag.replace("collection:related:", "", 1).strip().lower()
        if handle_allowed(handle) and handle not in seen:
            seen.append(handle)
    if seen:
        return seen
    for tag in tags:
        if "collection:random:" in tag or "collection:related:" in tag:
            continue
        if "collection:" not in tag:
            continue
        handle = tag.split("collection:", 1)[-1].strip().lower()
        if handle_allowed(handle):
            return [handle]
    return []


CASES = [
    (
        "breeze live tags",
        [
            "Airbus A220",
            "collection:random:airbus-a380-products",
            "collection:related:breeze-airways-enthusiasts",
            "collection:related:the-airbus-a220",
        ],
        ["breeze-airways-enthusiasts", "the-airbus-a220"],
    ),
    (
        "alaska live tags",
        [
            "Alaska Airlines",
            "Boeing 737",
            "collection:random:pilots-oclock",
            "collection:related:alaska-airlines-enthusiasts",
            "collection:related:boeing-737-products",
        ],
        ["alaska-airlines-enthusiasts", "boeing-737-products"],
    ),
    (
        "airline only",
        ["collection:related:breeze-airways-enthusiasts"],
        ["breeze-airways-enthusiasts"],
    ),
    (
        "aircraft only",
        ["collection:related:boeing-737-products"],
        ["boeing-737-products"],
    ),
    (
        "LATAM enthusiasts denied",
        ["collection:related:latam-airlines-enthusiasts"],
        [],
    ),
    (
        "LATAM plus aircraft still shows aircraft",
        [
            "collection:related:latam-airlines-enthusiasts",
            "collection:related:boeing-737-products",
        ],
        ["boeing-737-products"],
    ),
    (
        "unrelated collection denied",
        ["collection:related:featured-products"],
        [],
    ),
    (
        "random tag ignored",
        ["collection:random:airbus-a380-products"],
        [],
    ),
]


def main() -> int:
    failed = 0
    for name, tags, expected in CASES:
        got = related_handles(tags)
        ok = got == expected
        print(f"{'OK' if ok else 'FAIL':4} {name}: {got}")
        if not ok:
            print(f"     expected {expected}")
            failed += 1
    assert handle_allowed("breeze-airways-enthusiasts")
    assert handle_allowed("alaska-airlines-enthusiasts")
    assert handle_allowed("the-airbus-a220")
    assert handle_allowed("boeing-737-products")
    assert not handle_allowed("latam-airlines-enthusiasts")
    assert not handle_allowed("latam-airlines")
    return failed


if __name__ == "__main__":
    raise SystemExit(main())
