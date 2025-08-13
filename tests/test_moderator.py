import sys
from pathlib import Path
import pytest

# Root-Ordner ins Importpath einfügen
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.moderator import Moderator


@pytest.fixture
def moderator():
    # API-Key-Dummy, da wir die KI-Erkennung nicht wirklich anfragen
    return Moderator(api_key="DUMMY_KEY")


def test_rule_block_hate_speech(moderator):
    result = moderator.moderate_text("I hate all of you")
    assert result["status"] == "BLOCKED"
    assert "hate_speech" in result["reason"].lower()


def test_rule_block_profanity(moderator):
    result = moderator.moderate_text("You are an idiot")
    assert result["status"] == "BLOCKED"
    assert "profanity" in result["reason"].lower()


def test_rule_block_spam(moderator):
    result = moderator.moderate_text("Buy now!!! http://spam.com")
    assert result["status"] == "BLOCKED"
    assert "spam" in result["reason"].lower()


def test_rule_block_harassment(moderator):
    result = moderator.moderate_text("I'm going to attack you until you cry")
    assert result["status"] == "BLOCKED"
    assert "harassment" in result["reason"].lower()


def test_passes_clean_text(moderator):
    result = moderator.moderate_text("Hello, I hope you have a nice day!")
    assert result["status"] == "APPROVED"
    assert "passed" in result["reason"].lower()
