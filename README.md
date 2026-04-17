# AI Interview Engine

An MVP implementation of an adaptive AI interview platform that:

- analyzes a JD and resume
- generates practical interview questions
- runs a live text or browser-voice interview
- evaluates each answer
- produces a final score and recommendation

## 1. Recommended Tech Stack

### Frontend
- React + TypeScript + Vite
- Browser Speech Recognition API for MVP voice capture
- Plain CSS with a custom UI theme

### Backend
- FastAPI for interview APIs
- Pydantic for schema validation
- OpenAI API for analysis, question generation, and evaluation
- SQLAlchemy for persistent interview storage
- SQLite for zero-setup local development
- PostgreSQL-ready configuration for production

### Next-Phase Upgrades
- Redis for caching and async job state
- Azure Speech or Google Speech-to-Text for production-grade voice
- S3 or Azure Blob for audio/video transcript storage
- Celery or FastAPI background jobs for report generation

## 2. System Architecture

```text
React Frontend
  -> JD/Resume Form
  -> Live Interview UI
  -> Voice Capture

FastAPI Backend
  -> Profile Analysis Engine
  -> Question Generation Engine
  -> Answer Evaluation Engine
  -> Final Report Engine

AI Layer
  -> OpenAI responses API

Storage
  -> SQLite locally
  -> PostgreSQL in production
```

## 3. Project Structure

```text
backend/
  app/
    main.py
    db.py
    models.py
    repositories.py
    schemas.py
    config.py
    services/
      ai_client.py
      interview_engine.py
frontend/
  src/
    App.tsx
    api.ts
    types.ts
    styles.css
```

## 4. Core Modules Implemented

### JD + Resume Understanding Engine
- Endpoint: `POST /api/v1/analyze-profile`
- Upload endpoint: `POST /api/v1/documents/extract`
- Extracts:
  - required skills
  - candidate skills
  - gap skills
  - experience match
  - focus areas
- Supports uploaded `.txt`, `.md`, `.pdf`, and `.docx` files for both JD and resume
- Offline fallback now recognizes broader role families including SAP, QA Automation, backend engineering, DevOps/cloud, data engineering, and Salesforce-style CRM terms

### Question Generation Engine
- Generates 5 ordered interview questions
- Mixes:
  - technical
  - behavioral
  - scenario
- Uses easy -> medium -> hard progression

### Live Interview Engine
- Starts an interview session
- Shows one question at a time
- Supports typed answers
- Supports browser speech capture for MVP voice mode

### Answer Evaluation Engine
- Scores each answer on:
  - technical accuracy
  - communication
  - confidence
  - relevance
- Returns feedback and next-step direction

### Final Feedback Engine
- Aggregates per-answer scores
- Produces:
  - final recommendation
  - strengths
  - weaknesses
  - overall summary

## 5. Step-by-Step Build Guide

### Step 1: Start with MVP scope
Build only this first:
- JD + resume text input
- JD + resume file upload
- profile analysis
- question generation
- live text interview
- answer scoring
- final report

Do not start with:
- webcam emotion analysis
- cheating detection
- eye tracking
- production telephony

### Step 2: Run the backend

From `backend/`:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```

Set `.env` values before starting if needed:

```env
DATABASE_URL=sqlite:///./ai_interview_engine.db
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini
```

The app creates its tables automatically on startup.

For PostgreSQL later, replace `DATABASE_URL` with:

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/ai_interview_engine
```

Without an API key, the backend still works using heuristic fallback logic.
That fallback is now tuned for common skills across:
- SAP MM / procurement / inventory
- QA automation
- Java / Python / .NET / web backend
- DevOps / cloud / CI-CD
- Data engineering / analytics
- Salesforce / ServiceNow / Workday style enterprise platforms

### Step 3: Run the frontend

From `frontend/`:

```powershell
npm install
npm run dev
```

Open:

- `http://localhost:5173`

### Step 4: Test the full flow

1. Paste a JD
2. Or upload a JD/resume file with the browse buttons
3. Paste or review the extracted text
4. Click `Analyze JD + Resume`
5. Review skill match and gaps
6. Click `Start Live Interview`
7. Answer each question by text or voice
8. Review final report and recommendation

## 6. API Flow

### Analyze candidate profile

```http
POST /api/v1/analyze-profile
```

Request:

```json
{
  "role_title": "QA Automation Engineer",
  "job_description": "Need Java, Selenium, API testing, SQL and CI/CD...",
  "resume": "5 years of QA automation with Java and Selenium..."
}
```

### Start interview

```http
POST /api/v1/interviews/start
```

### Submit answer

```http
POST /api/v1/interviews/{session_id}/answer
```

### Get final report

```http
GET /api/v1/interviews/{session_id}/report
```

### Extract text from uploaded JD or resume

```http
POST /api/v1/documents/extract
```

## 7. Why This Stack Is Right

### React
- fast UI iteration
- easy voice and chat interface
- ideal for dashboards and interview experiences

### FastAPI
- very fast to build structured AI APIs
- excellent typing and validation
- easy OpenAI integration

### OpenAI
- best fit for:
  - JD parsing
  - adaptive interview question generation
  - answer evaluation
  - final feedback summaries

## 8. Production Roadmap

### Phase 1
- current MVP
- text + browser voice
- SQLite persistence for local development

### Phase 2
- recruiter auth
- candidate invite links
- resume upload and parsing
- transcript history
- PostgreSQL production setup

### Phase 3
- Azure or Google Speech-to-Text
- text-to-speech interviewer voice
- real adaptive branching by answer quality
- PDF report generation

### Phase 4
- proctoring and anti-cheating controls
- video interview support
- analytics dashboards
- bias monitoring and human review controls

## 9. Important Product Advice

- Start with interview quality, not fancy AI effects.
- Good prompts and grounded scoring matter more than face analysis.
- Keep a human review step in any hiring decision.
- Treat fairness and privacy as product requirements, not add-ons.

## 10. Best Next Step

If we continue this together, the next strongest improvement is:

1. add recruiter login
2. add candidate invite/session ownership
3. connect production speech-to-text
4. deploy backend and frontend
5. add migrations with Alembic

## Official OpenAI Reference Used

- [Responses API](https://platform.openai.com/docs/api-reference/responses?lang=python)
