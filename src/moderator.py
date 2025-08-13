# src/moderator.py
import re
import requests
import os

class Moderator:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key muss gesetzt sein (Parameter oder Umgebungsvariable ANTHROPIC_API_KEY).")

        # Lokale Blacklist-Patterns
        self.hate_speech_patterns = [r"\bhate\b"]
        self.profanity_patterns = [r"\bidiot\b", r"\bstupid\b"]
        self.spam_patterns = [r"http[s]?://", r"buy now", r"free money"]
        self.harassment_patterns = [r"\battack\b", r"\bkill\b"]

    def moderate_text(self, text: str) -> dict:
        """
        Moderiert Text:
        1. Regelbasierte Blacklist-Checks
        2. Falls frei → Claude API Analyse
        """
        lower_text = text.lower()

        # Regelbasierte Checks
        if any(re.search(pat, lower_text) for pat in self.hate_speech_patterns):
            return {"status": "BLOCKED", "reason": "Contains hate_speech"}
        if any(re.search(pat, lower_text) for pat in self.profanity_patterns):
            return {"status": "BLOCKED", "reason": "Contains profanity"}
        if any(re.search(pat, lower_text) for pat in self.spam_patterns):
            return {"status": "BLOCKED", "reason": "Contains spam"}
        if any(re.search(pat, lower_text) for pat in self.harassment_patterns):
            return {"status": "BLOCKED", "reason": "Contains harassment"}

        # Falls nichts gefunden → Claude API
        return self._check_with_claude(text)

    def _check_with_claude(self, text: str) -> dict:
        """
        Schickt den Text an die Claude API zur Moderation.
        """
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": "claude-3-haiku-20240307",  # günstig & schnell
            "max_tokens": 100,
            "messages": [
                {
                    "role": "user",
                    "content": f"""Check the following text for hate speech, profanity, spam, or harassment.
Return JSON with keys 'status' (BLOCKED or APPROVED) and 'reason'.
Text: {text}"""
                }
            ]
        }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            return {"status": "ERROR", "reason": f"Claude API error: {response.status_code} - {response.text}"}

        try:
            content = response.json()["content"][0]["text"]
            # Claude sollte direkt JSON zurückgeben
            import json
            result = json.loads(content)
            return result
        except Exception as e:
            return {"status": "ERROR", "reason": f"Failed to parse Claude response: {e}"}
