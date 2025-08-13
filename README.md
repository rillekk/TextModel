CLI:
python -m src.cli "Some text to moderate"

REST API:
uvicorn src.api:app --reload --port 8000
POST /moderate {"text":"..."}
