import json
import time
import urllib.request

from mimiradar.sources import SOURCES, BLOCKLIST


def check_url(url: str):
    if url in BLOCKLIST:
        return {"url": url, "status": "blocked"}
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "MimiRadar/0.1", "Range": "bytes=0-1024"},
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            code = resp.getcode()
            ctype = resp.headers.get("Content-Type", "")
            return {"url": url, "status": "ok", "code": code, "content_type": ctype}
    except Exception as e:
        return {"url": url, "status": "error", "error": str(e)}


def main():
    results = {"groups": {}, "summary": {"ok": 0, "error": 0, "blocked": 0}}
    start = time.monotonic()
    for group, urls in SOURCES.items():
        group_results = []
        for url in urls:
            res = check_url(url)
            group_results.append(res)
            results["summary"][res["status"]] += 1
            print(group, res["status"], url)
            time.sleep(0.2)
            if time.monotonic() - start > 120:
                print("Timeout reached, stopping validation early")
                results["groups"][group] = group_results
                with open("data/sources_status.json", "w", encoding="utf-8") as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                return
        results["groups"][group] = group_results

    with open("data/sources_status.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
