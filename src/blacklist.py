from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Set

CATEGORIES = ["profanity", "hate_speech", "spam", "harassment"]

class Blacklists:
    def __init__(self, base_dir: str):
        self.base = Path(base_dir)
        self.data: Dict[str, Set[str]] = {c: set() for c in CATEGORIES}

    def load(self) -> None:
        for cat in CATEGORIES:
            p = self.base / f"{cat}.txt"
            if p.exists():
                terms: List[str] = [line.strip().lower() for line in p.read_text(encoding="utf-8").splitlines() if line.strip() and not line.strip().startswith("#")]
                self.data[cat] = set(terms)

    def get(self, category: str) -> Set[str]:
        return self.data.get(category, set())