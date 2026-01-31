import json
import time
import urllib.request
from pathlib import Path

from mimiradar.sources import SOURCES, BLOCKLIST


def check_url(url: str):
    if url in BLOCKLIST:
        return False
    try:
        req = urllib.request.Request(
            url,
            method="HEAD",
            headers={"User-Agent": "MimiRadar/0.1", "Range": "bytes=0-1024"},
        )
        with urllib.request.urlopen(req, timeout=4) as resp:
            code = resp.getcode()
            return 200 <= code < 400
    except Exception:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "MimiRadar/0.1", "Range": "bytes=0-512"},
            )
            with urllib.request.urlopen(req, timeout=4) as resp:
                code = resp.getcode()
                return 200 <= code < 400
        except Exception:
            return False


def main(target_ok: int = 200, max_total_checks: int = 300, max_seconds: int = 170):
    store = Path("data/ok_sources.json")
    if store.exists():
        data = json.loads(store.read_text(encoding="utf-8"))
        ok = data.get("sources", {})
    else:
        ok = {}

    checked = set()
    for group, urls in ok.items():
        for u in urls:
            checked.add(u)

    total_checks = 0
    start = time.monotonic()

    for group, urls in SOURCES.items():
        ok.setdefault(group, [])
        for url in urls:
            if len(sum(ok.values(), [])) >= target_ok:
                break
            if total_checks >= max_total_checks:
                break
            if time.monotonic() - start > max_seconds:
                break
            if url in checked:
                continue
            total_checks += 1
            checked.add(url)
            if check_url(url):
                ok[group].append(url)
            if total_checks % 10 == 0:
                print(f"checked {total_checks}, ok {len(sum(ok.values(), []))}")
        if len(sum(ok.values(), [])) >= target_ok or total_checks >= max_total_checks or (time.monotonic() - start > max_seconds):
            break

    total_ok = len(sum(ok.values(), []))
    with store.open("w", encoding="utf-8") as f:
        json.dump({"total_ok": total_ok, "checked": len(checked), "sources": ok}, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
