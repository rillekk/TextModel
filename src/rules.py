from __future__ import annotations
import re
from typing import Dict, List, Set, Tuple

HARDBLOCK_PATTERNS = {
    # Dinge, die du *sofort* blocken willst (Phrasen matchen, case‑insensitive)
    "harassment": [r"\bkill\s+yourself\b", r"i\s+will\s+find\s+you"],
    "hate_speech": [r"\bsubhuman\b", r"go\s+back\s+to\s+your\s+country"],
}

class RuleResult:
    def __init__(self):
        self.flagged: Dict[str, Dict[str, List[str]]] = {}
        self.blocked: bool = False
        self.block_reasons: List[str] = []

    def to_dict(self) -> dict:
        return {"blocked": self.blocked, "block_reasons": self.block_reasons, "flagged": self.flagged}


def _scan_keywords(text: str, terms: Set[str]) -> List[str]:
    hits = []
    low = text.lower()
    for t in terms:
        if t and t in low:
            hits.append(t)
    return hits


def _scan_regex(text: str, patterns: List[str]) -> List[str]:
    hits = []
    for pat in patterns:
        if re.search(pat, text, re.IGNORECASE):
            hits.append(pat)
    return hits


def apply_rules(text: str, blacklists: Dict[str, Set[str]]) -> RuleResult:
    res = RuleResult()

    # Keyword‑Treffer sammeln
    for cat, terms in blacklists.items():
        kw_hits = _scan_keywords(text, terms)
        if kw_hits:
            res.flagged.setdefault(cat, {})["keywords"] = kw_hits

    # Regex‑Hardblocks prüfen
    for cat, pats in HARDBLOCK_PATTERNS.items():
        re_hits = _scan_regex(text, pats)
        if re_hits:
            res.flagged.setdefault(cat, {})["regex"] = re_hits
            res.blocked = True
            res.block_reasons.append(f"Rule hard‑block: {cat} via regex {re_hits}")

    # Einfache Heuristiken (Spam: Links/Triggerphrases => blocken)
    if "spam" in blacklists:
        spam_hits = _scan_keywords(text, blacklists["spam"])
        if any(h.startswith("http") for h in spam_hits) or (len(spam_hits) >= 2):
            res.blocked = True
            res.flagged.setdefault("spam", {}).setdefault("keywords", []).extend(spam_hits)
            res.block_reasons.append("Rule hard‑block: spam heuristic")

    return res