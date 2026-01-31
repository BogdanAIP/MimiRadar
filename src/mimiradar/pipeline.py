from datetime import datetime
from .sources import SOURCES


def run():
    # TODO: implement fetch -> dedupe -> classify -> render -> publish
    now = datetime.utcnow().isoformat()
    return {"status": "ok", "time": now, "sources": SOURCES}
