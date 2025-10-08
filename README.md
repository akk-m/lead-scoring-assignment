# Lead Scoring Service

A backend service to score leads using rule-based logic and Gemini AI.

## Setup Steps
1. Clone: `git clone <your-repo-url>`
2. Virtual env: `venv\Scripts\activate` (Windows)
3. Install: `pip install -r requirements.txt`
4. Set API key: `set GEMINI_API_KEY=your-key` (Windows CMD)
5. Run: `uvicorn app.main:app --reload`

## API Usage Examples
- POST /offer: `curl -X POST http://localhost:8000/offer -H "Content-Type: application/json" -d '{"name": "AI Outreach", "value_props": ["24/7"], "ideal_use_cases": ["SaaS"]}'`
- POST /leads/upload: `curl -X POST http://localhost:8000/leads/upload -F "file=@leads.csv"`

## Rule Logic
- Role: +20 (decision maker), +10 (influencer), 0 (else)
- Industry: +20 (exact), +10 (adjacent), 0 (else)
- Completeness: +10 (all fields)