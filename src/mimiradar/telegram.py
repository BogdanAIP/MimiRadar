import requests


def post_to_channel(bot_token: str, channel: str, text: str, silent: bool = True):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": channel,
        "text": text,
        "disable_web_page_preview": False,
        "disable_notification": silent,
    }
    r = requests.post(url, json=payload, timeout=20)
    return r.json()
