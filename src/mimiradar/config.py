import os

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "")
TG_API_ID = os.getenv("TG_API_ID", "")
TG_API_HASH = os.getenv("TG_API_HASH", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

POSTS_PER_DAY = int(os.getenv("POSTS_PER_DAY", "4"))

