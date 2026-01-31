import json
import urllib.request


def post_to_channel(bot_token: str, channel: str, text: str, silent: bool = True):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": channel,
        "text": text,
        "disable_web_page_preview": False,
        "disable_notification": silent,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))
