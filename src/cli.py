from __future__ import annotations
import json
import sys
from .moderator import Moderator

def main():
    if len(sys.argv) < 2:
        print('Usage: python -m src.cli "some text to moderate"')
        sys.exit(2)
    # join all args into one text so user can avoid shell quoting issues
    text = " ".join(sys.argv[1:])
    mod = Moderator()
    res = mod.analyze(text)
    print(json.dumps(res, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
