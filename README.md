# Moderation Prototype

Setup:
1. python -m venv .venv
2. .\.venv\Scripts\Activate.ps1
3. pip install -r requirements.txt
4. copy .env.example -> .env und ggf ANTHROPIC_API_KEY setzen

CLI:
python -m src.cli "Some text to moderate"

REST API:
uvicorn src.api:app --reload --port 8000
POST /moderate {"text":"..."}