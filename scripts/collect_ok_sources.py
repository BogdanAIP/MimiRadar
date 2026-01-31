import json
import time
import urllib.request
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
        with urllib.request.urlopen(req, timeout=5) as resp:
            code = resp.getcode()
            return 200 <= code < 400
    except Exception:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "MimiRadar/0.1", "Range": "bytes=0-512"},
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                code = resp.getcode()
                return 200 <= code < 400
        except Exception:
            return False


def main(target_ok: int = 200, max_total_checks: int = 120):
    ok = {}
    total_checks = 0
    for group, urls in SOURCES.items():
        ok[group] = []
        for url in urls:
            if len(sum(ok.values(), [])) >= target_ok:
                break
            if total_checks >= max_total_checks:
                break
            total_checks += 1
            if check_url(url):
                ok[group].append(url)
            time.sleep(0.03)
        if len(sum(ok.values(), [])) >= target_ok or total_checks >= max_total_checks:
            break

    total_ok = len(sum(ok.values(), []))
    with open("data/ok_sources.json", "w", encoding="utf-8") as f:
        json.dump({"total_ok": total_ok, "checked": total_checks, "sources": ok}, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
