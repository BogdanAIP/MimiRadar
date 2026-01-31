import os

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "")
TG_API_ID = os.getenv("TG_API_ID", "")
TG_API_HASH = os.getenv("TG_API_HASH", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

POSTS_PER_DAY = int(os.getenv("POSTS_PER_DAY", "4"))
DRY_RUN = os.getenv("DRY_RUN", "1") == "1"

CHANNELS = {
    "MoltbookSkills": "@MolbookSkills",
    "MoltbookAgents": "@MoltbookAgents",
    "MoltbookNews": "@MoltbookNews",
    "MoltbookRu": "@MoltbookRu",
    "MoltbookX": "@MoltbookX",
    "MoltbookSwarm": "@MoltbookSwarm",
    "OpenSource": "@open_source_mimi",
    "BadNews": "@Plohie_Novosti_24",
}
