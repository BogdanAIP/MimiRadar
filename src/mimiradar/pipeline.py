import re
import time
from datetime import datetime
from urllib.parse import urlparse

import feedparser
import requests
from bs4 import BeautifulSoup

from .config import DRY_RUN, TG_BOT_TOKEN, CHANNELS
from .telegram import post_to_channel
from .sources import SOURCES


KEYWORDS = {
    "MoltbookSkills": ["skill", "skills", "гайд", "tool", "plugin", "sdk"],
    "MoltbookAgents": ["agent", "agents", "leader", "karma", "bot"],
    "MoltbookNews": ["update", "release", "moltbook", "announcement"],
    "MoltbookRu": ["рус", "ru", "рос"],
    "MoltbookX": ["twitter", "x.com", "reddit", "discord"],
    "MoltbookSwarm": ["swarm", "orchestr", "multi-agent", "collab"],
    "OpenSource": ["open source", "github", "release", "new project"],
    "BadNews": ["earthquake", "war", "attack", "crisis", "disaster", "terror"],
}


def _fetch(url: str) -> str:
    r = requests.get(url, timeout=20, headers={"User-Agent": "MimiRadar/0.1"})
    r.raise_for_status()
    return r.text


def _parse_rss(url: str):
    feed = feedparser.parse(url)
    items = []
    for e in feed.entries[:30]:
        items.append({
            "title": e.get("title", ""),
            "link": e.get("link", ""),
            "summary": re.sub("<.*?>", "", e.get("summary", ""))[:500],
            "source": url,
        })
    return items


def _parse_html(url: str):
    html = _fetch(url)
    soup = BeautifulSoup(html, "html.parser")
    items = []
    for a in soup.select("a")[:50]:
        title = (a.get_text() or "").strip()
        link = a.get("href") or ""
        if not title or not link:
            continue
        if link.startswith("/"):
            link = f"{urlparse(url).scheme}://{urlparse(url).netloc}{link}"
        items.append({"title": title[:140], "link": link, "summary": "", "source": url})
    return items[:20]


def _classify(item):
    text = f"{item['title']} {item['summary']} {item['link']}".lower()
    for channel, keys in KEYWORDS.items():
        if any(k in text for k in keys):
            return channel
    return "OpenSource"


def _render(item):
    title = item["title"].strip()
    link = item["link"].strip()
    summary = item["summary"].strip()
    parts = [title]
    if summary:
        parts.append(summary[:400])
    if link:
        parts.append(link)
    return "

".join(parts)


def run(limit_per_source: int = 5):
    seen = set()
    queue = []
    for group, urls in SOURCES.items():
        for url in urls:
            if url.endswith(".xml") or url.endswith(".rss") or "rss" in url or "feed" in url or "atom" in url:
                items = _parse_rss(url)
            else:
                items = _parse_html(url)
            for it in items[:limit_per_source]:
                key = it.get("link") or it.get("title")
                if key in seen:
                    continue
                seen.add(key)
                queue.append(it)
            time.sleep(1)

    results = []
    for item in queue[:20]:
        channel_key = _classify(item)
        channel = CHANNELS.get(channel_key)
        text = _render(item)
        if DRY_RUN:
            results.append({"channel": channel, "text": text, "dry": True})
        else:
            res = post_to_channel(TG_BOT_TOKEN, channel, text, silent=True)
            results.append(res)
        time.sleep(1)

    return {"status": "ok", "time": datetime.utcnow().isoformat(), "posted": len(results), "results": results}
