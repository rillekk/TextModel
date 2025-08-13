from __future__ import annotations
import json
from typing import Dict, Any, Optional
import re

# try to import anthropic; if not available, we gracefully degrade.
try:
    import anthropic
except Exception:
    anthropic = None

from .config import MODEL_ID, ANTHROPIC_API_KEY

PROMPT = """
You are a strict content moderator. Classify the MESSAGE against these categories:
- Hate Speech: insults or dehumanization targeting protected characteristics.
- Profanity: offensive/vulgar words (context matters; standalone swearing counts).
- Spam: unsolicited promo, scams, repetitive links, mass marketing.
- Harassment/Cyberbullying: targeted threats, intimidation, persistent abuse.

Return ONLY compact JSON with this exact schema (no prose):
{
  "hate_speech": {"flagged": <true|false>, "confidence": <0..1>, "evidence": ["..."]},
  "profanity":   {"flagged": <true|false>, "confidence": <0..1>, "evidence": ["..."]},
  "spam":        {"flagged": <true|false>, "confidence": <0..1>, "evidence": ["..."]},
  "harassment":  {"flagged": <true|false>, "confidence": <0..1>, "evidence": ["..."]},
  "violation":   <true|false>,
  "reason":      "Short reason summarizing which categories and why"
}
If borderline, set flagged=false and violation=false.
"""

class ClaudeModerator:
    def __init__(self, api_key: Optional[str]):
        self.api_key = (api_key or "").strip()
        self.client = None
        if anthropic and self.api_key:
            try:
                # try a couple of common client names
                if hasattr(anthropic, "Anthropic"):
                    self.client = anthropic.Anthropic(api_key=self.api_key)
                elif hasattr(anthropic, "Client"):
                    self.client = anthropic.Client(api_key=self.api_key)
                else:
                    self.client = None
            except Exception:
                self.client = None

    def available(self) -> bool:
        return self.client is not None

    def _extract_text_from_response(self, resp: Any) -> str:
        # This helper tries multiple response shapes to get textual output.
        try:
            if isinstance(resp, dict):
                # common keys
                for k in ("text", "completion", "content", "output"):
                    v = resp.get(k)
                    if isinstance(v, str) and v.strip():
                        return v
                    if isinstance(v, list) and v:
                        # try to get first item text
                        itm = v[0]
                        if isinstance(itm, dict):
                            for kk in ("text", "content"):
                                if itm.get(kk):
                                    return itm.get(kk)
                        else:
                            return str(itm)
            else:
                # object with attributes
                for attr in ("content", "text", "completion", "output"):
                    v = getattr(resp, attr, None)
                    if isinstance(v, str) and v.strip():
                        return v
                    if isinstance(v, list) and v:
                        itm = v[0]
                        if isinstance(itm, dict):
                            for kk in ("text", "content"):
                                if itm.get(kk):
                                    return itm.get(kk)
                        else:
                            return str(itm)
        except Exception:
            pass
        return ""

    def moderate(self, text: str) -> Dict[str, Any]:
        if not self.client:
            return {"skipped": True, "note": "anthropic SDK not available or no API key provided"}

        # Prefer messages.create if available (newer SDK), fallback to completions
        try:
            if hasattr(self.client, "messages") and hasattr(self.client.messages, "create"):
                # messages API
                resp = self.client.messages.create(
                    model=MODEL_ID,
                    messages=[
                        {"role": "system", "content": PROMPT},
                        {"role": "user", "content": text}
                    ],
                    max_tokens=400,
                    temperature=0,
                )
                raw_text = self._extract_text_from_response(resp)
            elif hasattr(self.client, "completions") and hasattr(self.client.completions, "create"):
                prompt = PROMPT + "\n\nMESSAGE:\n" + text
                resp = self.client.completions.create(model=MODEL_ID, prompt=prompt, max_tokens=400, temperature=0)
                raw_text = self._extract_text_from_response(resp)
            else:
                return {"error": "unsupported_anthropic_client"}
        except Exception as e:
            return {"error": "exception_during_api_call", "message": str(e)}

        # Try to parse JSON from the model output
        if not raw_text:
            return {"error": "empty_response", "raw": ""}

        # Try direct JSON, else try to find JSON substring
        try:
            return json.loads(raw_text)
        except Exception:
            m = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if m:
                try:
                    return json.loads(m.group(0))
                except Exception:
                    return {"raw": raw_text}
            return {"raw": raw_text}
