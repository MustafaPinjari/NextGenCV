Performance Fixes
Move NLP/AI to Celery (infrastructure already exists)

Redis-backed sessions

Eliminate double keyword extraction

Dashboard resume slice at DB level

🎨 UI/UX Redesign
Loading states on all AI operations (skeleton + spinner)

ATS score emotional context + benchmark framing

Wizard auto-save to localStorage

Mobile wizard bottom-sheet preview

Live score update as user types

Rewrite — ScoringEngineService.calculate_ats_score
The current version runs NLP 4+ times and has no caching. Here is the production version:

Synchronous NLP/AI in request thread — blocks all workers

No rate limiting on auth endpoints — brute-force trivial

Media files publicly accessible without auth

Insecure fallback SECRET_KEY

SSRF in job scraper

🟡 Important Improvements
Double keyword extraction — 4x unnecessary NLP calls per analysis

**kwargs unpacking into ORM — silent data corruption risk

Wizard session race condition — multi-tab corruption

OpenAI client thread-safety — intermittent failures under load

PDF import ignores user's cleared data — silent data loss

ActivityLog deletion broken on PostgreSQL

🟢 Nice-to-have
Wizard localStorage backup

Mobile wizard preview as bottom sheet

ATS score emotional framing

Loading skeletons on AI operations

Resume benchmarking against field averages

Live ATS score as you type — WebSocket or debounced AJAX that updates the score ring in real-time as the user edits their resume. No other tool does this.

"Apply in 1 click" flow — User pastes a LinkedIn job URL → system extracts JD → auto-runs analysis → shows a 3-step fix list → user accepts → downloads optimized resume. End-to-end in under 2 minutes.

Callback rate leaderboard — "Resumes with 80+ ATS score in Software Engineering get 4.2x more callbacks (based on 1,247 tracked applications)." Even with mock data for the demo, this is compelling.

AI interview coach — After applying, the system generates 10 likely interview questions based on the JD + resume gap. Judges love end-to-end thinking.

Demo storytelling strategy
Don't demo features. Demo a story:

"Meet Sarah. She's applied to 47 jobs and heard nothing back. She uploads her resume. NextGenCV shows her score: 31/100. It shows her exactly which 14 keywords are missing. She accepts the AI fixes. Score jumps to 78. She applies again. Three days later, she gets a call."


# NextGenCV

An ATS resume builder built with Django. Create, optimise, and track resumes against job descriptions — with AI-powered rewriting, real ATS system simulation, job application tracking, and outcome analytics.

---

## Features

### Resume Builder
- Multi-step wizard with live preview
- Import from PDF upload or LinkedIn profile URL
- Version control — full snapshots with diff comparison and restore
- Export to PDF, DOCX, and plain text
- Template customisation (colour schemes, fonts)
- Resume sharing via public link

### AI-Powered Optimisation
- **Fix My Resume** — rewrites bullet points with stronger action verbs and keywords
- **Cover letter generation** — personalised to the role and company
- **Professional summary** — generated from your experience and skills
- **Interview prep** — tailored questions with STAR talking points and resume evidence
- **Rejection analysis** — explains why a resume may have been rejected for a specific role
- All AI features fall back to rule-based heuristics if no API key is set

### ATS Analysis
- 6-factor scoring: keyword match, skill relevance, section completeness, experience impact, quantification, action verbs
- **ATS system simulation** — shows how Taleo, Workday, Greenhouse, Lever, and iCIMS would each parse and score your resume
- Missing keyword detection with injection suggestions

### Job Application Tracker
- Track applications through: Saved → Applied → Interview → Offer → Rejected
- Snapshot ATS score at time of application
- Cover letter and interview prep per application
- Follow-up email templates
- Skill gap analysis against target roles
- Salary intelligence (US market data)

### Outcome Analytics
- Callback rate by ATS score bucket — does a higher score actually get more interviews?
- Best-performing resume identification
- Rejection pattern analysis
- **Resume A/B testing** — compare two versions, track which gets more responses

### REST API
Full DRF API at `/api/v1/` with JWT authentication — see [API docs](#api) below.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 4.2.7 |
| Async tasks | Celery 5.3.6 + Redis (optional) |
| AI / LLM | OpenAI API (`gpt-4o-mini` default) |
| REST API | Django REST Framework + SimpleJWT |
| PDF parsing | pdfplumber + spaCy |
| PDF export | WeasyPrint |
| DOCX export | python-docx |
| Database | SQLite (dev) / PostgreSQL-ready |
| Frontend | Django templates, Bootstrap 5, vanilla JS |

---

## Quick Start

### 1. Clone and set up

```bash
git clone https://github.com/your-username/nextgencv.git
cd nextgencv

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Configure environment

```bash
cp .env.example .env
```

Open `.env` and set at minimum:

```env
SECRET_KEY=your-secret-key-here   # generate one (see below)
OPENAI_API_KEY=sk-...             # optional — app works without it
```

Generate a secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Run migrations and start

```bash
python manage.py migrate
python manage.py runserver
```

Visit `http://localhost:8000`

### 4. (Optional) Seed mock data

```bash
python manage.py seed_mock_data
```

Demo accounts created:
```
alex_johnson / mockpass123
sarah_chen   / mockpass123
marcus_lee   / mockpass123
```

---

## AI Features Setup

Set `OPENAI_API_KEY` in `.env`. The default model is `gpt-4o-mini` (fast and cheap).

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

Without a key, every AI feature falls back to the built-in rule-based engine — the app is fully functional either way.

---

## Async Tasks (Celery)

By default (`REDIS_URL=memory://`), tasks run synchronously inline — no worker needed.

To enable true background processing:

1. Install [Memurai](https://www.memurai.com/get-memurai) (Windows) or Redis
2. Update `.env`:
   ```env
   REDIS_URL=redis://localhost:6379/0
   ```
3. Start the worker (use `--pool=solo` on Windows):
   ```bash
   celery -A config worker --pool=solo --loglevel=info
   ```

---

## Project Structure

```
nextgencv/
├── apps/
│   ├── api/                  # REST API (DRF + JWT)
│   ├── analytics/            # Resume health & score trends
│   ├── analyzer/             # ATS scoring engine
│   │   └── services/
│   │       ├── scoring_engine.py
│   │       ├── ats_simulator.py      # Taleo/Workday/Greenhouse/Lever/iCIMS
│   │       └── keyword_extractor.py
│   ├── authentication/       # Auth, email verification, activity log
│   ├── resumes/              # Core resume management
│   │   ├── services/
│   │   │   ├── llm_service.py        # Central AI/LLM integration
│   │   │   ├── pdf_parser.py
│   │   │   ├── linkedin_importer.py
│   │   │   └── bullet_point_rewriter.py
│   │   ├── tasks.py                  # Celery async tasks
│   │   └── ab_testing.py             # A/B test model
│   ├── templates_mgmt/       # Template gallery
│   └── tracker/              # Job application tracker
│       ├── cover_letter_service.py
│       ├── interview_prep_service.py
│       ├── outcome_analytics.py
│       └── salary_service.py
├── config/
│   ├── settings.py
│   ├── celery.py
│   └── urls.py
├── templates/
├── static/
├── .env.example              # Copy to .env and fill in values
├── requirements.txt
└── manage.py
```

---

## API

Base URL: `/api/v1/`

### Authentication

```
POST /api/v1/auth/token/          # Get JWT token pair
POST /api/v1/auth/token/refresh/  # Refresh access token
```

### Resumes

```
GET    /api/v1/resumes/                        # List resumes
POST   /api/v1/resumes/                        # Create resume
GET    /api/v1/resumes/{id}/                   # Resume detail
PATCH  /api/v1/resumes/{id}/                   # Update resume
DELETE /api/v1/resumes/{id}/                   # Delete resume
POST   /api/v1/resumes/{id}/analyse/           # Trigger ATS analysis
POST   /api/v1/resumes/{id}/optimise/          # Trigger AI optimisation
POST   /api/v1/resumes/{id}/ats-simulate/      # ATS system simulation
POST   /api/v1/resumes/{id}/rejection-analysis/ # Why was I rejected?
GET    /api/v1/resumes/{id}/versions/          # Version history
POST   /api/v1/resumes/linkedin-import/        # Import LinkedIn profile
```

### Applications

```
GET    /api/v1/applications/                        # List applications
POST   /api/v1/applications/                        # Create application
GET    /api/v1/applications/{id}/                   # Application detail
POST   /api/v1/applications/{id}/cover-letter/      # Generate cover letter
POST   /api/v1/applications/{id}/interview-prep/    # Generate interview questions
```

### Other

```
GET    /api/v1/me/                  # Current user profile
GET    /api/v1/outcomes/            # Outcome analytics
GET    /api/v1/tasks/{task_id}/     # Poll async task status
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | — | Django secret key (required) |
| `DEBUG` | `True` | Set to `False` in production |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated allowed hosts |
| `REDIS_URL` | `memory://` | Redis URL or `memory://` for inline tasks |
| `OPENAI_API_KEY` | — | OpenAI key (optional — enables AI features) |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model to use |
| `OPENAI_MAX_TOKENS` | `1500` | Max tokens per request |
| `DJANGO_ENV` | — | Set to `production` for prod settings |

---

## Running Tests

```bash
python manage.py test apps.authentication
python manage.py test apps.resumes
python manage.py test apps.analyzer
python manage.py test apps.tracker
```

---

## Deployment Checklist

- [ ] Set `DEBUG=False`
- [ ] Set a strong `SECRET_KEY`
- [ ] Set `ALLOWED_HOSTS` to your domain
- [ ] Set `DJANGO_ENV=production`
- [ ] Switch `REDIS_URL` to a real Redis instance
- [ ] Configure SMTP email (replace console backend)
- [ ] Run `python manage.py collectstatic`
- [ ] Serve media files via nginx or S3
- [ ] Use gunicorn or uvicorn as the WSGI server

---

## License

MIT
