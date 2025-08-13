from __future__ import annotations
import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
MODEL_ID = os.getenv("ANTHROPIC_MODEL", "claude-3-7-sonnet-20250219")
BLACKLIST_DIR = os.getenv("BLACKLIST_DIR", "./data/blacklist")

def has_api_key() -> bool:
    return bool(ANTHROPIC_API_KEY)
