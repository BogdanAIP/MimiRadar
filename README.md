# MimiRadar

Content radar + Telegram publishing.

## Setup

Create `.env` (not committed):

```
TG_BOT_TOKEN=
TG_API_ID=
TG_API_HASH=
OPENAI_API_KEY=
POSTS_PER_DAY=4
DRY_RUN=1
```

## Run

```
python -m pip install -e .
python scripts/validate_sources.py
python scripts/run.py
```
