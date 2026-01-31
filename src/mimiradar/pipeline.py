import json
import logging
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from html.parser import HTMLParser
from urllib.parse import urljoin
import urllib.request

from .config import DRY_RUN, TG_BOT_TOKEN, CHANNELS
from .telegram import post_to_channel
from .sources import SOURCES


LOG_PATH = "logs/run.log"
DATA_PATH = "data/last_run.json"

logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

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
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MimiRadar/0.1"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        logging.warning("fetch failed %s: %s", url, e)
        return ""


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self._current_href = None

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        for k, v in attrs:
            if k == "href":
                self._current_href = v

    def handle_endtag(self, tag):
        if tag == "a":
            self._current_href = None

    def handle_data(self, data):
        if self._current_href and data.strip():
            self.links.append((data.strip(), self._current_href))


def _parse_rss(url: str):
    xml_text = _fetch(url)
    items = []
    if not xml_text:
        return items
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        logging.warning("rss parse failed %s: %s", url, e)
        return items

    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        summary = (item.findtext("description") or "").strip()
        summary = re.sub("<.*?>", "", summary)[:500]
        if title or link:
            items.append({"title": title, "link": link, "summary": summary, "source": url})

    if not items:
        for entry in root.findall(".//{http://www.w3.org/2005/Atom}entry"):
            title = (entry.findtext("{http://www.w3.org/2005/Atom}title") or "").strip()
            link_el = entry.find("{http://www.w3.org/2005/Atom}link")
            link = (link_el.get("href") if link_el is not None else "").strip()
            summary = (entry.findtext("{http://www.w3.org/2005/Atom}summary") or "").strip()
            summary = re.sub("<.*?>", "", summary)[:500]
            if title or link:
                items.append({"title": title, "link": link, "summary": summary, "source": url})

    return items


def _parse_html(url: str):
    html = _fetch(url)
    if not html:
        return []
    parser = LinkParser()
    parser.feed(html)
    items = []
    for title, link in parser.links[:50]:
        if link.startswith("/"):
            link = urljoin(url, link)
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
    return "\n\n".join(parts)


def run(limit_per_source: int = 5, max_posts: int = 20):
    seen = set()
    queue = []
    for group, urls in SOURCES.items():
        for url in urls:
            try:
                if url.endswith(".xml") or url.endswith(".rss") or "rss" in url or "feed" in url or "atom" in url:
                    items = _parse_rss(url)
                else:
                    items = _parse_html(url)
            except Exception as e:
                logging.warning("parse failed %s: %s", url, e)
                items = []
            for it in items[:limit_per_source]:
                key = it.get("link") or it.get("title")
                if key in seen:
                    continue
                seen.add(key)
                queue.append(it)
            time.sleep(0.5)

    results = []
    for item in queue[:max_posts]:
        channel_key = _classify(item)
        channel = CHANNELS.get(channel_key)
        text = _render(item)
        if not channel:
            continue
        if DRY_RUN:
            results.append({"channel": channel, "text": text, "dry": True})
        else:
            try:
                res = post_to_channel(TG_BOT_TOKEN, channel, text, silent=True)
                results.append(res)
            except Exception as e:
                logging.warning("post failed %s: %s", channel, e)
        time.sleep(0.5)

    output = {"status": "ok", "time": datetime.utcnow().isoformat(), "posted": len(results), "results": results}
    Path(DATA_PATH).write_text(json.dumps(output, ensure_ascii=False, indent=2))
    logging.info("run finished posted=%s", len(results))
    return output
