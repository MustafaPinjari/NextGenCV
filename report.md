# NextGenCV — Complete Project Report

---

## 1.1 Need for System

### The Problem

The modern job market is broken for applicants. Over **75% of resumes are rejected before a human ever reads them** — filtered out automatically by Applicant Tracking Systems (ATS). These are software platforms used by virtually every mid-to-large employer (Taleo, Workday, Greenhouse, Lever, iCIMS) to screen, parse, and rank incoming applications before a recruiter sees them.

The core problem has several dimensions:

**1. ATS Incompatibility**
Most job seekers write resumes for human readers — using creative formatting, tables, columns, graphics, and non-standard section headers. ATS systems cannot reliably parse these. A well-qualified candidate gets scored zero not because of their experience, but because their resume used a two-column layout or a bullet character that Taleo cannot read.

**2. Keyword Mismatch**
ATS systems rank resumes by keyword relevance against the job description. A candidate may have all the required skills but use different terminology — writing "built REST services" when the job description says "REST API development." The system scores them low. Without knowing which exact keywords are missing, candidates cannot fix this.

**3. No Feedback Loop**
Traditional resume tools (Word, Google Docs) give zero feedback on ATS compatibility. Candidates apply, hear nothing, and have no idea why. There is no mechanism to understand what score their resume received, which keywords were missing, or how to improve before the next application.

**4. Generic Resumes**
Most candidates send the same resume to every job. ATS systems reward tailored resumes that mirror the specific language of each job description. Manually tailoring a resume for every application is time-consuming and most candidates do not do it.

**5. Fragmented Tooling**
The job search process involves many disconnected tasks — writing a resume, analyzing it against a job description, tracking applications, writing cover letters, preparing for interviews, researching salaries. Candidates juggle multiple tools (or none at all) with no unified workflow.

**6. No Visibility into the Process**
Candidates have no data on their own performance. They cannot see trends in their ATS scores over time, identify which skills they are consistently missing across job descriptions, or understand patterns in their rejections.

### Why a Dedicated System is Needed

Existing tools fail to address these problems adequately:

| Tool | Limitation |
|---|---|
| Microsoft Word / Google Docs | No ATS analysis, no keyword feedback, no scoring |
| LinkedIn Resume Builder | Basic formatting only, no ATS simulation |
| Generic resume websites (Canva, Zety) | Focus on visual design — often produce ATS-unfriendly output |
| Manual keyword matching | Time-consuming, error-prone, no scoring |
| Separate job trackers (spreadsheets) | Disconnected from resume data, no ATS score correlation |

A dedicated system is needed that:
- **Understands how ATS systems work** and scores resumes accordingly
- **Provides actionable, specific feedback** — not generic tips but exact missing keywords and scores
- **Simulates multiple ATS platforms** so candidates know their compatibility across different systems
- **Integrates the full job search workflow** — resume building, analysis, optimization, application tracking, cover letters, interview prep — in one place
- **Tracks progress over time** so candidates can see whether their improvements are working
- **Uses AI to automate the tedious parts** — rewriting bullet points, injecting keywords, generating cover letters — while keeping the candidate in control

### Who Needs This System

**Primary Users — Active Job Seekers**
Professionals actively applying for jobs who need to maximize their chances of passing ATS screening. Particularly relevant for software engineers and tech professionals, recent graduates entering a competitive market, career changers who need to reframe their experience in new terminology, and professionals applying to large enterprises where ATS usage is near-universal.

**Secondary Users — Passive Job Seekers**
Employed professionals who want to keep their resume current and competitive, monitor their market value via salary intelligence, and be ready to move quickly when the right opportunity appears.

### Summary

NextGenCV exists because the gap between a qualified candidate and a successful application is largely technical — not a matter of experience or skill, but of knowing how automated systems work and optimizing accordingly. The system brings transparency, automation, and data to a process that has historically been opaque and manual, giving every job seeker the same advantages that were previously only available to those with expensive career coaches or insider knowledge.

---

## 1.2 Scope and Feasibility of Work

### Scope

NextGenCV is a full-stack web application that covers the complete job-search lifecycle for a registered user. The scope is defined across three boundaries:

**In Scope**

| Area | What is Covered |
|---|---|
| Resume Management | Create, edit, duplicate, delete, version, export (PDF/DOCX), public share |
| ATS Analysis | 6-component weighted scoring, keyword gap analysis, improvement suggestions |
| ATS Simulation | Simulate Taleo, Workday, Greenhouse, Lever, iCIMS parsing behaviour |
| AI Optimization | Bullet point rewriting, keyword injection, quantification suggestions, formatting standardization |
| Beat the ATS | Threshold-based keyword battle plan, score simulation |
| Analytics | Health scores, score trends, section completeness, improvement reports |
| Job Tracker | Application pipeline, status tracking, outcome analytics, rejection analysis |
| Cover Letters | AI-generated and template-based cover letters per application |
| Interview Prep | AI-generated interview questions with talking points and resume evidence |
| Skill Gap Analysis | Multi-JD skill gap identification with market frequency scoring |
| Salary Intelligence | Role and location-based salary ranges with negotiation tips |
| Follow-up Emails | Pre-written templates for post-apply, post-interview, offer negotiation |
| PDF Upload & Import | Parse existing PDF resumes and import into the system |
| REST API | Full DRF API with JWT authentication for all major features |
| User Accounts | Registration, email verification, profile, password management, data export |

**Out of Scope**

- Direct job board integration (Indeed, LinkedIn job postings)
- Real-time recruiter communication
- Video interview tools
- Payment processing / subscription billing (pricing UI exists but no payment gateway)
- Mobile native applications (iOS/Android)
- Multi-language resume support

### Feasibility

**Technical Feasibility**
The system is built entirely on mature, well-documented open-source technologies. Django 4.2 is a production-proven framework with a large ecosystem. All third-party libraries (spaCy, pdfplumber, WeasyPrint, OpenAI SDK) are actively maintained. The architecture is a standard layered monolith — a well-understood pattern with no experimental components. The system runs on SQLite in development and can migrate to PostgreSQL for production with minimal changes.

**Operational Feasibility**
The application is server-rendered with progressive enhancement via JavaScript. It requires no special client-side installation. Any modern browser on any device can use it. The Django Admin interface provides operational management without custom tooling.

**Economic Feasibility**
- Development uses entirely free and open-source software — zero licensing costs
- Hosting can be done on a single VPS (e.g., DigitalOcean, AWS EC2) at low cost
- The only variable cost is the OpenAI API — all AI features have rule-based fallbacks, so the system is fully functional at zero AI cost
- SQLite eliminates the need for a separate database server in early stages
- Celery uses an in-memory broker in development — Redis is only needed for production scale

**Schedule Feasibility**
The system is already implemented and functional. The codebase contains 7 Django apps, 20+ service classes, a full REST API, and comprehensive documentation. The modular service-layer architecture means new features can be added independently without disrupting existing functionality.

---

## 1.3 Operating Environment — Hardware and Software

### Hardware Requirements

**Server (Minimum — Development / Small Production)**

| Component | Minimum | Recommended |
|---|---|---|
| CPU | 1 vCPU / 1 GHz | 2 vCPU / 2 GHz+ |
| RAM | 1 GB | 2–4 GB |
| Storage | 10 GB SSD | 20 GB SSD |
| Network | 100 Mbps | 1 Gbps |

**Server (Production — Medium Scale)**

| Component | Specification |
|---|---|
| CPU | 4 vCPU |
| RAM | 8 GB |
| Storage | 50 GB SSD + separate media storage |
| Network | 1 Gbps |
| Cache Server | Redis instance (separate or same host) |

**Client (End User)**

| Component | Minimum |
|---|---|
| Device | Desktop, laptop, tablet, or smartphone |
| RAM | 2 GB |
| Display | 320px minimum width (responsive design) |
| Network | Broadband internet connection |

No special hardware is required on the client side. The application is entirely browser-based.

### Software Requirements

**Server-Side Software**

| Software | Version | Purpose |
|---|---|---|
| Python | 3.10+ | Runtime language |
| Django | 4.2.7 | Web framework |
| SQLite | 3.x (bundled) | Database (development) |
| PostgreSQL | 14+ (optional) | Database (production) |
| Redis | 5.0+ (optional) | Celery broker + cache (production) |
| Celery | 5.3.6 | Async task queue |
| Gunicorn / uWSGI | Latest | WSGI server (production) |
| Nginx | Latest | Reverse proxy (production) |
| spaCy en_core_web_sm | 3.x | NLP model |

**Python Package Dependencies**

| Package | Version | Purpose |
|---|---|---|
| Django | 4.2.7 | Core framework |
| djangorestframework | 3.15.2 | REST API |
| djangorestframework-simplejwt | 5.3.1 | JWT tokens |
| django-cors-headers | 4.3.1 | CORS handling |
| django-celery-results | 2.5.1 | Task result storage |
| django-extensions | 4.1 | Dev utilities |
| celery | 5.3.6 | Task queue |
| redis | 5.0.1 | Redis client |
| openai | 1.35.0 | AI/LLM integration |
| spacy | 3.8.14 | NLP processing |
| pdfplumber | 0.10.3 | PDF text extraction |
| WeasyPrint | 59.0 | PDF generation |
| python-docx | 1.1.0 | DOCX generation |
| Pillow | 10.4.0 | Image processing |
| bleach | 6.1.0 | HTML sanitization |
| libsass | 0.22.0 | SCSS compilation |
| requests | 2.31.0 | HTTP client |
| hypothesis | 6.92.1 | Property-based testing |

**Client-Side Software**

| Software | Version | Purpose |
|---|---|---|
| Any modern browser | Chrome 90+, Firefox 88+, Safari 14+, Edge 90+ | Application access |
| JavaScript (ES6+) | Built-in | Interactivity, AJAX, wizard |
| Bootstrap Icons | 1.11.1 | Icon library (CDN) |
| Chart.js | Latest (CDN) | Analytics charts |
| Google Fonts (Inter) | CDN | Typography |

**Development Tools**

| Tool | Purpose |
|---|---|
| VS Code | Primary IDE |
| Git | Version control |
| Python venv | Virtual environment |
| Django manage.py | Database migrations, dev server |
| compile_scss.py | SCSS to CSS compilation |

**Environment Variables Required**

| Variable | Required | Default |
|---|---|---|
| `SECRET_KEY` | Yes (production) | Insecure fallback (dev only) |
| `DEBUG` | No | `True` |
| `ALLOWED_HOSTS` | Yes (production) | `localhost,127.0.0.1` |
| `OPENAI_API_KEY` | No | Empty (AI features disabled) |
| `REDIS_URL` | No | `memory://` (in-process) |
| `MEDIA_ROOT` | No | `./media` |
| `DJANGO_ENV` | No | Development mode |

---

## 1.4 Architecture of System

### Architectural Pattern

NextGenCV follows a **Layered Monolithic Architecture** with a dedicated **Service Layer** separating business logic from presentation and data access. This is a well-established pattern for Django applications that balances simplicity with maintainability.

```
┌─────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                  │
│         Django Templates + Custom CSS/JS             │
│              REST API (DRF + JWT)                    │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                 APPLICATION LAYER                    │
│           Django Views + URL Router                  │
│              Service Layer (Business Logic)          │
│   ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│   │ Resume   │ │ Analyzer │ │    Tracker       │   │
│   │ Services │ │ Services │ │    Services      │   │
│   └──────────┘ └──────────┘ └──────────────────┘   │
│   ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│   │Analytics │ │   LLM    │ │  PDF/DOCX Export │   │
│   │ Services │ │ Service  │ │    Services      │   │
│   └──────────┘ └──────────┘ └──────────────────┘   │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                    DATA LAYER                        │
│              Django ORM (Models)                     │
│                  SQLite / PostgreSQL                 │
└─────────────────────────────────────────────────────┘
```

### Request Lifecycle

```
Browser Request
      │
      ▼
  Middleware Stack
  (Security, CORS, GZip, Performance Monitor)
      │
      ▼
  URL Router (config/urls.py)
      │
      ▼
  View Function / ViewSet
      │
      ▼
  Service Layer (Business Logic)
      │
      ├──► Django ORM ──► SQLite / PostgreSQL
      │
      ├──► OpenAI API (async via Celery)
      │
      └──► spaCy NLP Engine
      │
      ▼
  Template Rendering / JSON Serialization
      │
      ▼
  HTTP Response to Browser
```

### Application Module Architecture

The system is divided into 7 Django apps, each with its own models, views, URLs, and service layer:

```
config/                    ← Project settings, root URLs, middleware
apps/
 ├── authentication/       ← User auth, dashboard, profile, activity log
 ├── resumes/              ← Core resume CRUD, wizard, export, versioning
 │    └── services/        ← 10+ service classes
 ├── analyzer/             ← ATS scoring, keyword analysis, simulation
 │    └── services/        ← 6 service classes
 ├── analytics/            ← Charts, trends, improvement reports
 │    └── services/        ← 3 service classes
 ├── tracker/              ← Job applications, cover letters, interview prep
 ├── templates_mgmt/       ← Resume template gallery
 └── api/                  ← REST API (DRF ViewSets)
```

### Async Architecture (Celery)

Long-running tasks (AI analysis, optimization) are offloaded to Celery:

```
Web Request
    │
    ▼
Django View ──► Celery Task Queue ──► Worker Process
    │                                       │
    │◄── Task ID (202 Accepted)             │
    │                                       ▼
    │                               OpenAI API / NLP
    │                                       │
    ▼                                       ▼
Client polls                        Django DB (results)
/api/v1/tasks/{id}/
```

In development, `CELERY_TASK_ALWAYS_EAGER = True` runs tasks synchronously (no worker needed). In production with Redis, tasks run in a separate worker process.

### Database Schema Overview

```
User (Django built-in)
 ├── Resume (many)
 │    ├── PersonalInfo (one-to-one)
 │    ├── Experience (many)
 │    ├── Education (many)
 │    ├── Skill (many)
 │    ├── Project (many)
 │    ├── Certification (many)
 │    ├── ResumeVersion (many)       ← full JSON snapshots
 │    ├── ResumeAnalysis (many)      ← ATS score results
 │    └── OptimizationHistory (many) ← AI optimization records
 ├── JobApplication (many)
 │    ├── CoverLetter (one-to-one)
 │    └── InterviewPrepSession (many)
 ├── SkillGapAnalysis (many)
 ├── ActivityLog (many)
 └── SavedJobDescription (many)
```

### Security Architecture

```
Every Request
    │
    ├── CSRF Token Validation (all POST forms)
    ├── Session Authentication (web UI)
    ├── JWT Authentication (REST API)
    │
    ▼
Every Protected View
    ├── @login_required decorator
    └── Ownership check: resume.user == request.user
```

Additional security layers:
- `SecurityHeadersMiddleware` — XSS filter, content-type nosniff, clickjacking protection
- `bleach` — HTML sanitization on all user-generated content
- File upload validation — PDF-only, 10MB limit, embedded script detection
- Rate limiting — 100 req/hour general, 20 req/hour AI endpoints
- Password validation — length, common password, numeric-only checks

### Caching Architecture

```
Request for Analytics / Health Score
    │
    ▼
Cache Check (Django LocMemCache / Redis)
    │
    ├── HIT ──► Return cached value (fast path)
    │
    └── MISS ──► Calculate ──► Store in cache ──► Return
                               (5 min TTL for analytics)
                               (10 min TTL for score trends)
```

---

## 1.6 Detail Description of Technology Used

### 1. Django 4.2 (Core Framework)

Django is a high-level Python web framework that follows the Model-View-Template (MVT) pattern. It provides the foundational structure for the entire application.

**How it is used in NextGenCV:**
- **ORM** — All database interactions go through Django's ORM. Models define the schema; queries use Python objects instead of raw SQL. This makes the codebase database-agnostic (SQLite in dev, PostgreSQL in production).
- **URL Routing** — `config/urls.py` maps URL patterns to view functions. Each app has its own `urls.py` included via `include()`.
- **Views** — Function-based views handle all web page requests. Each view enforces authentication, calls service layer methods, and renders templates.
- **Templates** — Django's template engine renders server-side HTML. Templates use inheritance (`{% extends %}`) with a base layout for public pages and a separate layout for authenticated pages.
- **Middleware** — Custom middleware handles GZip compression, cache headers, security headers, and performance monitoring.
- **Admin** — Django Admin provides a management interface for models without custom code.
- **Sessions** — Used to persist multi-step wizard data across requests. `SESSION_SAVE_EVERY_REQUEST = True` prevents data loss on refresh.
- **Messages Framework** — Flash messages for success/error feedback after form submissions.
- **Authentication** — Built-in `User` model, `@login_required` decorator, password hashing (PBKDF2), and password validators.

---

### 2. Django REST Framework (DRF) + SimpleJWT

DRF is a toolkit for building REST APIs on top of Django. SimpleJWT provides JSON Web Token authentication.

**How it is used in NextGenCV:**
- `ResumeViewSet` and `JobApplicationViewSet` provide full CRUD via `ModelViewSet`
- Custom `@action` decorators add non-CRUD endpoints (analyse, optimise, ats-simulate, cover-letter, interview-prep)
- Different serializers for different operations — `ResumeListSerializer`, `ResumeDetailSerializer`, `ResumeCreateSerializer`
- JWT access tokens (1-hour lifetime) and refresh tokens (7-day lifetime) for stateless API authentication
- `AIFeatureThrottle` — custom throttle class limiting AI endpoints to 20 calls/hour per user
- `PageNumberPagination` — 20 items per page on list endpoints

---

### 3. spaCy (Natural Language Processing)

spaCy is an industrial-strength NLP library for Python. The `en_core_web_sm` model is used for English text processing.

**How it is used in NextGenCV:**
- **Keyword Extraction** — `KeywordExtractorService` uses spaCy to tokenize text, extract nouns and noun phrases, and remove stop words. This powers the core ATS keyword matching algorithm.
- **Section Parsing** — `SectionParserService` uses spaCy's Named Entity Recognition (NER) to identify personal information (names, locations, organizations) from raw PDF text.
- **Lazy Loading** — The NLP model is loaded once and cached as a class variable to avoid reloading on every request.

```
Resume Text / Job Description
        │
        ▼
   spaCy Pipeline
   (tokenize → POS tag → NER → dependency parse)
        │
        ▼
   Keyword Set (nouns, proper nouns, noun phrases)
        │
        ▼
   Set intersection → Matched / Missing keywords
```

---

### 4. OpenAI API (GPT-4o-mini)

The OpenAI Python SDK connects to OpenAI's chat completion API for all AI-powered features.

**How it is used in NextGenCV:**
All AI features are implemented in `LLMService` with a consistent pattern — attempt the OpenAI API call, fall back to rule-based generation if the API key is absent or the call fails.

| Feature | Prompt Strategy |
|---|---|
| Professional Summary | Structured prompt with experience, skills, education data |
| Bullet Point Rewriting | Few-shot prompt with weak → strong bullet examples |
| Cover Letter | Role/company/JD context with resume data injected |
| Interview Questions | Role + JD + resume skills → categorized questions with talking points |
| ATS Score Explanation | Score breakdown → plain-English explanation |
| Rejection Analysis | Resume + JD + company/role → likely rejection reasons |

**Configuration:** Model `gpt-4o-mini`, max tokens 1500, temperature 0.7. `AI_ENABLED` flag auto-detects from `OPENAI_API_KEY`.

---

### 5. Celery + Redis (Async Task Processing)

Celery is a distributed task queue. Redis acts as the message broker in production.

**How it is used in NextGenCV:**
- ATS analysis and AI optimization are submitted as Celery tasks via `.delay()` — the API returns `202 Accepted` with a task ID immediately
- The client polls `/api/v1/tasks/{task_id}/` for results
- Email verification emails are sent asynchronously
- In development: `CELERY_TASK_ALWAYS_EAGER = True` — tasks run synchronously inline, no Redis or worker needed
- In production: Redis broker, separate worker process (`celery -A config worker`)
- Task results stored in Django DB via `django-celery-results`
- Task time limit: 5 minutes hard, 4 minutes soft

---

### 6. pdfplumber (PDF Parsing)

pdfplumber is a Python library for extracting text and structured data from PDF files.

**How it is used in NextGenCV:**
- `PDFParserService` opens uploaded PDF files with pdfplumber
- Extracts text page by page and concatenates into a single string
- Calculates a parsing confidence score based on text density and structure
- The extracted text is passed to `SectionParserService` for structured parsing into resume sections
- Handles multi-page resumes and various PDF encodings

---

### 7. WeasyPrint (PDF Generation)

WeasyPrint converts HTML/CSS to PDF by rendering the page as a browser would, then outputting a PDF binary.

**How it is used in NextGenCV:**
- `PDFExportService` renders the resume's selected HTML template (e.g., `professional.html`) with all resume data
- Passes the rendered HTML string to WeasyPrint's `HTML().write_pdf()` method
- Returns the PDF bytes as a Django `HttpResponse` with `Content-Disposition: attachment`
- Falls back to returning the HTML file on Windows (WeasyPrint requires GTK libraries not available on Windows by default)
- Supports exporting specific resume versions via the `version_id` parameter

---

### 8. python-docx (DOCX Export)

python-docx creates and modifies Microsoft Word `.docx` files programmatically using the Open XML format.

**How it is used in NextGenCV:**
- `DOCXExportService` builds a Word document from scratch
- Adds styled headings, paragraphs, and tables matching the resume structure
- Applies ATS-safe fonts (Arial, Calibri) and standard formatting
- Returns the DOCX bytes as a downloadable HTTP response
- Supports version-specific export

---

### 9. Custom Design System (CSS/SCSS)

The frontend uses a custom-built design system rather than a third-party CSS framework.

**How it is used in NextGenCV:**
- `static/css/design-system.css` — 4000+ line component library defining all UI components (buttons, cards, forms, navigation, sidebar, alerts, badges)
- `static/scss/` — SCSS source files compiled via `libsass` using `compile_scss.py`
- CSS custom properties (variables) for theming — dark mode by default with `--bg`, `--surface`, `--primary`, `--text` design tokens
- Separate layout stylesheets: `authenticated.css` (sidebar layout), `public.css` (marketing pages)
- No external CSS framework dependency — fully self-contained

---

### 10. Chart.js (Data Visualization)

Chart.js is a JavaScript charting library loaded via CDN for rendering interactive analytics charts.

**How it is used in NextGenCV:**
- Analytics dashboard: line chart for ATS score trends over time with moving average overlay
- Radar/bar chart for score component breakdown (keyword match, skill relevance, etc.)
- Section completeness bar chart across all resumes
- Outcome analytics: application status distribution
- Chart data is prepared server-side as JSON (`chart_data_json` context variable) and passed to Chart.js initialization in the template — no client-side API calls needed

---

### 11. Hypothesis (Property-Based Testing)

Hypothesis is a Python library for property-based testing — it generates thousands of random inputs automatically to find edge cases that example-based tests miss.

**How it is used in NextGenCV:**
- Used in the analytics and analyzer test suites
- Tests scoring functions with randomly generated resume data to verify invariants (e.g., score always between 0 and 100, keyword match never exceeds 100%)
- `.hypothesis/examples/` stores previously found failing examples for regression testing — these are replayed on every test run

---

### Technology Interaction Summary

```
User Browser
    │
    │  HTTP / HTTPS
    ▼
Django (Views + Templates)
    │
    ├──► spaCy ──────────────── Keyword extraction, NER
    │
    ├──► OpenAI API ─────────── AI text generation (async via Celery)
    │
    ├──► pdfplumber ─────────── Parse uploaded PDF resumes
    │
    ├──► WeasyPrint ─────────── Generate PDF exports
    │
    ├──► python-docx ────────── Generate DOCX exports
    │
    ├──► Django ORM ─────────── SQLite / PostgreSQL
    │
    ├──► Celery + Redis ──────── Async task queue
    │
    └──► Django Cache ────────── LocMemCache / Redis
```

---

---

# Chapter 2: Proposed System

---

## 2.1 Proposed System

### Overview

The proposed system, **NextGenCV**, is a full-stack, AI-powered web application that replaces the fragmented, manual, and feedback-free process of resume writing and job searching with a unified, data-driven platform. It is built on Django 4.2 and delivered entirely through a web browser — no installation required on the client side.

The system is designed around a single core insight: getting hired is not just about qualifications, it is about presenting those qualifications in a format that both automated systems and human recruiters can evaluate positively. NextGenCV addresses both dimensions simultaneously.

### What the Proposed System Does

The system operates across five interconnected modules:

**Module 1 — Resume Builder**
A guided, multi-step wizard walks users through creating a structured resume section by section: Personal Information → Work Experience → Education → Skills → Professional Summary. A live preview panel updates in real time as the user types. The system stores each resume in a normalized relational database, enabling structured analysis and export. Users can maintain multiple resumes simultaneously, duplicate them for different roles, and track every change through an automatic version history.

**Module 2 — ATS Analysis and Optimization Engine**
The core intelligence of the system. When a user pastes a job description, the engine:
1. Extracts keywords from both the resume and the job description using NLP (spaCy)
2. Calculates a composite ATS score across six weighted dimensions
3. Identifies exactly which keywords are present and which are missing
4. Simulates how five major ATS platforms (Taleo, Workday, Greenhouse, Lever, iCIMS) would parse and score the resume
5. Generates a "battle plan" showing the minimum keywords needed to cross the next score threshold

The AI optimization feature ("Fix My Resume") then rewrites weak bullet points, injects missing keywords naturally, suggests quantifications, and standardizes formatting — presenting the changes in a side-by-side comparison where the user accepts or rejects each modification individually.

**Module 3 — Analytics and Progress Tracking**
A dashboard that aggregates data across all of a user's resumes and analyses to show: resume health scores, ATS score trends over time with moving averages, section completeness percentages, top missing keywords across all job descriptions analyzed, and improvement deltas from optimization sessions. An improvement report categorizes recommendations by priority (high/medium/low) and tracks progress.

**Module 4 — Job Application Tracker**
A full application pipeline manager that tracks every job application through statuses: Saved → Applied → Interview → Offer → Rejected/Withdrawn. The system snapshots the ATS score at the time of application, enabling outcome analytics — correlating ATS scores with interview callback rates. Additional tools include: AI-generated cover letters, AI-generated interview preparation questions (with talking points drawn from the user's own resume), follow-up email templates, rejection pattern analysis, and salary intelligence by role and location.

**Module 5 — REST API**
A complete DRF-based REST API with JWT authentication exposes all major features programmatically. This enables future integration with third-party tools, mobile applications, or browser extensions.

### How the Proposed System Differs from the Existing Approach

| Aspect | Without NextGenCV | With NextGenCV |
|---|---|---|
| Resume creation | Manual in Word/Google Docs | Guided wizard with live preview |
| ATS feedback | None | Real-time score with 6-component breakdown |
| Keyword optimization | Manual guesswork | Exact missing keywords identified by NLP |
| ATS platform compatibility | Unknown | Simulated across 5 major platforms |
| AI improvement | None | Automated bullet rewriting, keyword injection |
| Version control | Manual file copies | Automatic snapshots with restore |
| Application tracking | Spreadsheet | Integrated pipeline with ATS score correlation |
| Cover letters | Written from scratch | AI-generated, tailored to role and company |
| Interview prep | Ad hoc | AI questions drawn from resume and JD |
| Progress visibility | None | Score trends, health scores, improvement reports |
| Salary data | External research | Built-in by role and location |

### System Boundaries

The system begins when a user registers an account and ends when they export a finalized resume or submit a job application. It does not submit applications on behalf of users, communicate with recruiters, or integrate with live job boards. All data is stored per-user and is never shared between accounts.

---

## 2.2 Objective of System

The objectives of NextGenCV are organized into primary objectives (core purpose) and secondary objectives (supporting goals).

### Primary Objectives

**OBJ-01: Maximize ATS Pass Rate**
Enable users to create resumes that score above 75 on the system's ATS scoring engine when matched against a relevant job description. Provide specific, actionable feedback — not generic advice — so users know exactly what to change and why.

**OBJ-02: Eliminate Keyword Guesswork**
Automatically identify every keyword present in a job description that is absent from the user's resume. Present these as a prioritized list with context on where and how to add them naturally, removing the need for manual comparison.

**OBJ-03: Simulate Real ATS Behaviour**
Give users visibility into how their resume performs across the five most widely used ATS platforms — Taleo, Workday, Greenhouse, Lever, and iCIMS — each with its own parsing quirks, scoring weights, and failure modes. A resume that scores 85 in Greenhouse but 52 in Taleo needs different fixes than one that scores consistently across all systems.

**OBJ-04: Automate Resume Improvement**
Reduce the time and skill required to improve a resume from hours of manual editing to minutes of reviewing AI-generated suggestions. The optimization engine should produce measurable score improvements (target: +10 to +20 points) on a well-formed resume with a relevant job description.

**OBJ-05: Unify the Job Search Workflow**
Consolidate resume building, ATS analysis, application tracking, cover letter generation, interview preparation, and salary research into a single platform so users do not need to switch between multiple disconnected tools.

### Secondary Objectives

**OBJ-06: Track Progress Over Time**
Provide users with longitudinal data on their resume quality — score trends, health scores, improvement rates — so they can see whether their efforts are working and identify patterns in what makes their resumes more effective.

**OBJ-07: Preserve Resume History**
Automatically version every change to a resume so users can compare states, understand what improved their score, and restore any previous version without losing work.

**OBJ-08: Support Multiple Resumes**
Allow users to maintain separate, tailored resumes for different roles, industries, or career stages — each independently analyzed, versioned, and exportable.

**OBJ-09: Produce ATS-Safe Exports**
Generate PDF and DOCX exports that are formatted for ATS compatibility — standard fonts, no tables or columns, selectable text, standard section headings — so the visual output does not undermine the optimization work done in the system.

**OBJ-10: Provide Outcome Intelligence**
Correlate application outcomes (interview, offer, rejection) with ATS scores at the time of application, giving users data-driven insight into the relationship between their resume quality and their job search results.

**OBJ-11: Ensure Data Security and Privacy**
Enforce strict per-user data isolation — every resume, analysis, and application is accessible only to its owner. Protect all data in transit and at rest using industry-standard security practices.

**OBJ-12: Remain Functional Without AI**
All AI-powered features must have rule-based fallbacks so the system is fully usable without an OpenAI API key. The core value proposition — ATS scoring, keyword analysis, version history, application tracking — must not depend on any paid external service.

### Measurable Success Criteria

| Objective | Success Metric |
|---|---|
| ATS Pass Rate | Users achieve score ≥ 75 after one optimization session |
| Keyword Identification | 100% of JD keywords identified and classified as matched/missing |
| ATS Simulation | All 5 platforms simulated with system-specific issue detection |
| Optimization Speed | Full optimization cycle completes in under 60 seconds |
| Export Quality | PDF exports pass pdfplumber text extraction with ≥ 90% confidence |
| Page Performance | All pages load in under 2 seconds on standard broadband |
| Security | Zero cross-user data access; all routes protected by authentication |

---

## 2.3 User Requirements

User requirements are organized by user type and then by functional area. They describe what users need to be able to do — not how the system implements it.

### User Types

| User Type | Description |
|---|---|
| **Guest** | Unauthenticated visitor browsing the landing page |
| **Registered User** | Authenticated user with a personal account |
| **Admin** | Staff user with access to Django Admin for system management |

---

### Guest User Requirements

| ID | Requirement |
|---|---|
| GUR-01 | The guest shall be able to view the landing page describing the system's features, pricing, and testimonials without logging in. |
| GUR-02 | The guest shall be able to register a new account by providing a username, email address, and password. |
| GUR-03 | The guest shall be able to log in to an existing account using their username and password. |
| GUR-04 | The guest shall be able to request a password reset via their registered email address. |
| GUR-05 | The guest shall receive an email verification link upon registration and must verify their email before full access is granted. |

---

### Registered User Requirements

#### Account Management

| ID | Requirement |
|---|---|
| RUR-01 | The user shall be able to view and edit their profile information (first name, last name, email address). |
| RUR-02 | The user shall be able to change their password by providing their current password and a new password. |
| RUR-03 | The user shall be able to export all their data (resumes, applications) as a downloadable ZIP file containing JSON. |
| RUR-04 | The user shall be able to delete all their resumes in a single action. |
| RUR-05 | The user shall be able to permanently delete their account and all associated data. |

#### Resume Creation and Management

| ID | Requirement |
|---|---|
| RUR-06 | The user shall be able to create a new resume using a guided multi-step wizard covering: Personal Information, Work Experience, Education, Skills, and Professional Summary. |
| RUR-07 | The user shall be able to see a live preview of their resume updating in real time as they fill in the wizard steps. |
| RUR-08 | The user shall be able to add, edit, and remove multiple entries for Work Experience, Education, Skills, Projects, and Certifications. |
| RUR-09 | The user shall be able to request an AI-generated professional summary based on their entered experience and skills. |
| RUR-10 | The user shall be able to view a list of all their resumes with title, last updated date, and ATS score. |
| RUR-11 | The user shall be able to edit any section of an existing resume at any time. |
| RUR-12 | The user shall be able to duplicate an existing resume to use as a starting point for a new version. |
| RUR-13 | The user shall be able to delete a resume with a confirmation prompt. |
| RUR-14 | The user shall be able to select a template (Professional, Modern, Creative, Minimal) for their resume. |
| RUR-15 | The user shall be able to customize the color scheme and font family of their selected template. |
| RUR-16 | The user shall be able to generate a public shareable link for their resume. |

#### PDF Upload and Import

| ID | Requirement |
|---|---|
| RUR-17 | The user shall be able to upload an existing resume in PDF format (maximum 10MB). |
| RUR-18 | The system shall automatically extract text from the uploaded PDF and parse it into structured resume sections. |
| RUR-19 | The user shall be able to review the parsed data, correct any errors, and confirm the import to create a new resume. |
| RUR-20 | The user shall be shown a parsing confidence score indicating the reliability of the automatic extraction. |

#### ATS Analysis

| ID | Requirement |
|---|---|
| RUR-21 | The user shall be able to analyze any of their resumes against a job description by pasting the job description text. |
| RUR-22 | The system shall return a composite ATS score (0–100) broken down into six components: Keyword Match, Skill Relevance, Section Completeness, Experience Impact, Quantification, and Action Verb Strength. |
| RUR-23 | The system shall display a list of keywords from the job description that are present in the resume (matched) and those that are absent (missing). |
| RUR-24 | The system shall provide specific, actionable improvement suggestions based on the analysis results. |
| RUR-25 | The user shall be able to save frequently used job descriptions for reuse in future analyses. |
| RUR-26 | The user shall be able to simulate how their resume would be parsed and scored by Taleo, Workday, Greenhouse, Lever, and iCIMS individually. |
| RUR-27 | Each ATS simulation result shall include: a score, a list of issues, a list of warnings, a list of passed checks, and system-specific quirks. |
| RUR-28 | The user shall be able to access a "Beat the ATS" feature that shows the minimum keywords needed to cross the next score threshold, with a simulated score after adding those keywords. |

#### AI Resume Optimization

| ID | Requirement |
|---|---|
| RUR-29 | The user shall be able to trigger an AI optimization of their resume against a specific job description. |
| RUR-30 | The system shall present the optimization results as a side-by-side comparison showing the original and optimized versions with all changes highlighted. |
| RUR-31 | The user shall be able to accept all changes, reject all changes, or review and accept/reject individual changes. |
| RUR-32 | The system shall display the original ATS score, the optimized ATS score, and the improvement delta before the user accepts changes. |
| RUR-33 | Accepted optimization changes shall be saved as a new resume version, preserving the original. |

#### Version History

| ID | Requirement |
|---|---|
| RUR-34 | The system shall automatically create a version snapshot every time a resume is saved or optimized. |
| RUR-35 | The user shall be able to view the full version history of any resume, showing version number, date, modification type, and ATS score. |
| RUR-36 | The user shall be able to view a read-only snapshot of any historical version. |
| RUR-37 | The user shall be able to restore any previous version, which creates a new version based on the historical state without deleting newer versions. |
| RUR-38 | The user shall be able to export any specific version as PDF or DOCX. |

#### Export

| ID | Requirement |
|---|---|
| RUR-39 | The user shall be able to export any resume as a PDF file with the selected template and customizations applied. |
| RUR-40 | The user shall be able to export any resume as a DOCX (Microsoft Word) file. |
| RUR-41 | Exported files shall be named after the resume title and downloaded directly to the user's device. |

#### Analytics

| ID | Requirement |
|---|---|
| RUR-42 | The user shall be able to view an analytics dashboard showing: overall resume health score, total resume count, total version count, ATS score trend over time, section completeness percentages, and top missing keywords. |
| RUR-43 | The user shall be able to view a detailed score trend chart showing all analyses over time with a moving average line. |
| RUR-44 | The user shall be able to view an improvement report showing overall status, prioritized recommendations, optimization history, and per-resume health scores. |

#### Job Application Tracker

| ID | Requirement |
|---|---|
| RUR-45 | The user shall be able to create a job application record with: company name, role, job URL, job description, linked resume, status, applied date, and notes. |
| RUR-46 | The user shall be able to move applications through a status pipeline: Saved → Applied → Interview → Offer → Rejected / Withdrawn. |
| RUR-47 | The system shall automatically record the ATS score of the linked resume at the time the application is created. |
| RUR-48 | The user shall be able to view outcome analytics showing: total applications, callback rate, interview rate, offer rate, and ATS score distribution by outcome. |
| RUR-49 | The user shall be able to view a rejection analysis identifying patterns in rejected applications by ATS score bucket and application stage. |

#### Cover Letters

| ID | Requirement |
|---|---|
| RUR-50 | The user shall be able to generate a cover letter for any job application, tailored to the company, role, and job description. |
| RUR-51 | The generated cover letter shall draw on the user's resume data (experience, skills, achievements) to personalize the content. |
| RUR-52 | The user shall be able to edit the generated cover letter before saving it. |
| RUR-53 | The user shall be able to regenerate the cover letter at any time. |

#### Interview Preparation

| ID | Requirement |
|---|---|
| RUR-54 | The user shall be able to generate a set of interview preparation questions for any job application. |
| RUR-55 | Each generated question shall include: the question text, category (behavioral/technical/situational), suggested talking points, and relevant evidence from the user's resume. |
| RUR-56 | The user shall be able to regenerate interview questions on demand. |

#### Skill Gap Analysis

| ID | Requirement |
|---|---|
| RUR-57 | The user shall be able to perform a skill gap analysis by selecting a resume, entering a target role, and optionally pasting one or more job descriptions. |
| RUR-58 | The system shall return: a list of skills present in the resume, a list of skills missing relative to the target role, frequency scores for each skill (how often it appears in the provided JDs), and prioritized recommendations. |
| RUR-59 | The system shall provide a coverage score showing what percentage of required skills the user already has. |

#### Salary Intelligence

| ID | Requirement |
|---|---|
| RUR-60 | The user shall be able to look up salary ranges for any role by entering a job title and optional location. |
| RUR-61 | The system shall return low, mid, and high salary estimates with the detected seniority level and location multiplier applied. |
| RUR-62 | The system shall provide salary negotiation tips relevant to the detected seniority level. |

#### Follow-up Emails

| ID | Requirement |
|---|---|
| RUR-63 | The user shall be able to generate a follow-up email template for any application at three stages: After Applying, After Interview, and Offer Negotiation. |
| RUR-64 | The generated email shall be pre-filled with the application's company name, role, applied date, and the user's name from their resume. |

---

### Admin User Requirements

| ID | Requirement |
|---|---|
| AUR-01 | The admin shall be able to view, create, edit, and delete all user accounts via the Django Admin interface. |
| AUR-02 | The admin shall be able to manage resume templates — add new templates, deactivate existing ones, and set a default template. |
| AUR-03 | The admin shall be able to view all resumes, analyses, and optimization records across all users for support and moderation purposes. |
| AUR-04 | The admin shall be able to view application logs and performance monitoring data. |

---

### Non-Functional User Requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-01 | Performance | All standard pages shall load within 2 seconds on a broadband connection. |
| NFR-02 | Performance | ATS analysis shall complete within 3 seconds for a standard resume and job description. |
| NFR-03 | Performance | PDF export shall complete within 5 seconds. |
| NFR-04 | Security | All routes requiring authentication shall redirect unauthenticated users to the login page. |
| NFR-05 | Security | Users shall only be able to access their own resumes, analyses, and applications — cross-user access shall be blocked with a 403 response. |
| NFR-06 | Security | All forms shall be protected against CSRF attacks using Django's built-in CSRF token mechanism. |
| NFR-07 | Security | Passwords shall be stored as hashed values using PBKDF2 — never in plain text. |
| NFR-08 | Usability | The system shall be fully usable on desktop, tablet, and mobile devices via responsive design. |
| NFR-09 | Usability | The system shall support keyboard navigation and include ARIA labels for screen reader accessibility. |
| NFR-10 | Reliability | No user data shall be lost due to a page refresh during the resume creation wizard (session persistence). |
| NFR-11 | Reliability | All AI features shall have rule-based fallbacks — the system shall remain fully functional without an OpenAI API key. |
| NFR-12 | Availability | The system shall handle errors gracefully — all 404, 403, and 500 errors shall display custom error pages with navigation options. |
| NFR-13 | Maintainability | Business logic shall be encapsulated in service classes, not in views, to enable independent testing and modification. |
| NFR-14 | Data Integrity | All database operations involving multiple related records shall be wrapped in transactions to prevent partial writes. |

---

---

# Chapter 3: Analysis and Design


# Chapter 3: Analysis & Design

## 3.1 Data Flow Diagrams (DFD)

### Level 0 — Context Diagram

```
                        ┌─────────────────────────────────────────┐
                        │                                         │
   ┌──────────┐         │           N e x t G e n C V            │         ┌─────────────────┐
   │          │ ──────► │                                         │ ──────► │   OpenAI API    │
   │   User   │         │         (AI-Powered ATS Resume          │ ◄────── │  (GPT-4o-mini)  │
   │          │ ◄────── │              Builder)                   │         └─────────────────┘
   └──────────┘         │                                         │
                        │                                         │         ┌─────────────────┐
  [Registration]        │                                         │ ──────► │   Celery /      │
  [Login]               │                                         │ ◄────── │   Redis Queue   │
  [Resume Data]         │                                         │         └─────────────────┘
  [Job Description]     │                                         │
  [Analysis Request]    │                                         │         ┌─────────────────┐
  [Export Request]      │                                         │ ──────► │  WeasyPrint     │
                        │                                         │ ◄────── │  (PDF Engine)   │
  [Analysis Results]    │                                         │         └─────────────────┘
  [Optimized Resume]    │                                         │
  [PDF / DOCX File]     │                                         │         ┌─────────────────┐
  [Dashboard Data]      │                                         │ ──────► │  spaCy NLP      │
                        │                                         │ ◄────── │  (en_core_web)  │
                        │                                         │         └─────────────────┘
                        │                                         │
   ┌──────────┐         │                                         │         ┌─────────────────┐
   │  Admin   │ ──────► │                                         │ ──────► │  SQLite DB      │
   │          │ ◄────── │                                         │ ◄────── │  (Persistent    │
   └──────────┘         │                                         │         │   Storage)      │
                        └─────────────────────────────────────────┘         └─────────────────┘
```

---

### Level 1 — Main Processes

```
                                    ┌──────────────────────────────────────────────────────────────────┐
                                    │                        NextGenCV System                           │
                                    │                                                                    │
   ┌──────────┐                     │  ┌─────────────────┐        ┌──────────────────────────────┐     │
   │          │──[credentials]─────►│  │  1.0            │        │  D1: auth_user               │     │
   │          │◄─[session/token]────│  │  Authentication │◄──────►│  D2: authentication_         │     │
   │          │                     │  │  & User Mgmt    │        │       activitylog             │     │
   │          │                     │  └────────┬────────┘        └──────────────────────────────┘     │
   │          │                     │           │ [user_id]                                             │
   │          │                     │           ▼                                                        │
   │          │──[resume data]─────►│  ┌─────────────────┐        ┌──────────────────────────────┐     │
   │          │◄─[resume list/      │  │  2.0            │        │  D3: resumes_resume           │     │
   │          │   detail]───────────│  │  Resume         │◄──────►│  D4: resumes_personalinfo    │     │
   │          │                     │  │  Management     │        │  D5: resumes_experience      │     │
   │          │                     │  └────────┬────────┘        │  D6: resumes_education       │     │
   │          │                     │           │ [resume_id]      │  D7: resumes_skill           │     │
   │  User    │                     │           ▼                  │  D8: resumes_project         │     │
   │          │──[job description]─►│  ┌─────────────────┐        │  D9: resumes_certification   │     │
   │          │◄─[score/keywords/   │  │  3.0            │        └──────────────────────────────┘     │
   │          │   suggestions]──────│  │  ATS Analysis   │◄──────►  D10: resumes_resumeanalysis        │
   │          │                     │  └────────┬────────┘                                             │
   │          │                     │           │ [analysis_id]                                         │
   │          │                     │           ▼                                                        │
   │          │──[fix request]─────►│  ┌─────────────────┐        ┌──────────────────────────────┐     │
   │          │◄─[optimized text]───│  │  4.0            │◄──────►│  D11: resumes_               │     │
   │          │                     │  │  AI             │        │       optimizationhistory    │     │
   │          │                     │  │  Optimization   │        └──────────────────────────────┘     │
   │          │                     │  └────────┬────────┘                                             │
   │          │                     │           │                   ┌──────────────────────────────┐    │
   │          │──[export request]──►│  ┌─────────────────┐        │  D12: resumes_resumeversion  │    │
   │          │◄─[PDF/DOCX file]────│  │  5.0            │◄──────►│  D13: resumes_uploadedresume │    │
   │          │                     │  │  Export &       │        └──────────────────────────────┘    │
   │          │                     │  │  Version Ctrl   │                                             │
   │          │                     │  └────────┬────────┘                                             │
   │          │                     │           │                                                        │
   │          │──[app data]────────►│  ┌─────────────────┐        ┌──────────────────────────────┐     │
   │          │◄─[tracker views]────│  │  6.0            │◄──────►│  D14: tracker_jobapplication │     │
   │          │                     │  │  Job Tracker    │        │  D15: tracker_coverletter    │     │
   │          │                     │  │  & AI Tools     │        │  D16: tracker_interviewprep  │     │
   │          │                     │  └────────┬────────┘        │  D17: tracker_skillgap       │     │
   │          │                     │           │                  └──────────────────────────────┘     │
   │          │──[view request]────►│  ┌─────────────────┐        ┌──────────────────────────────┐     │
   │          │◄─[charts/metrics]───│  │  7.0            │◄──────►│  D18: (aggregated from       │     │
   └──────────┘                     │  │  Analytics      │        │   resumes + tracker tables)  │     │
                                    │  └─────────────────┘        └──────────────────────────────┘     │
                                    └──────────────────────────────────────────────────────────────────┘
```

---

### Level 2 — ATS Analysis Process (Process 3.0) in Detail

```
                        ┌──────────────────────────────────────────────────────────────────────┐
                        │                    3.0  ATS Analysis Process                          │
                        │                                                                        │
   [resume_id]          │                                                                        │
   [job_description] ──►│  ┌──────────────────┐                                                 │
                        │  │  3.1             │  [raw text]                                     │
                        │  │  Text            ├──────────────────────────────────────────────►  │
                        │  │  Preprocessing   │  • Lowercase normalisation                      │
                        │  │                  │  • Punctuation / stopword removal               │
                        │  │  (resume text    │  • Tokenisation                                 │
                        │  │   + JD text)     │                                                 │
                        │  └──────────────────┘                                                 │
                        │          │ [clean tokens]                                              │
                        │          ▼                                                              │
                        │  ┌──────────────────┐                                                 │
                        │  │  3.2             │  [keyword list]                                 │
                        │  │  Keyword         ├──────────────────────────────────────────────►  │
                        │  │  Extraction      │  • spaCy NLP pipeline                           │
                        │  │  (spaCy NLP)     │  • Named Entity Recognition                     │
                        │  │                  │  • Noun-chunk extraction                        │
                        │  │                  │  • TF-IDF weighting                             │
                        │  └──────────────────┘                                                 │
                        │          │ [jd_keywords, resume_keywords]                              │
                        │          ▼                                                              │
                        │  ┌──────────────────┐                                                 │
                        │  │  3.3             │                                                  │
                        │  │  Resume          │  • Fetch PersonalInfo, Experience,               │
                        │  │  Aggregation     │    Education, Skills, Projects,                  │
                        │  │                  │    Certifications from DB                        │
                        │  │  (DB read)       │  • Flatten into structured text                 │
                        │  └──────────────────┘                                                 │
                        │          │ [structured_resume_data]                                    │
                        │          ▼                                                              │
                        │  ┌──────────────────┐                                                 │
                        │  │  3.4             │  [match_results]                                │
                        │  │  Keyword         ├──────────────────────────────────────────────►  │
                        │  │  Matching        │  • Exact match                                  │
                        │  │                  │  • Semantic similarity (spaCy vectors)           │
                        │  │                  │  • Missing keyword list                         │
                        │  └──────────────────┘                                                 │
                        │          │ [match_data]                                                │
                        │          ▼                                                              │
                        │  ┌──────────────────────────────────────────────────────────────┐     │
                        │  │  3.5   Six-Factor Scoring Engine                              │     │
                        │  │                                                                │     │
                        │  │  ┌────────────────────┐   ┌────────────────────┐             │     │
                        │  │  │ Factor 1           │   │ Factor 2           │             │     │
                        │  │  │ Keyword Match      │   │ Action Verb        │             │     │
                        │  │  │ Score (0–100)      │   │ Score (0–100)      │             │     │
                        │  │  └────────────────────┘   └────────────────────┘             │     │
                        │  │  ┌────────────────────┐   ┌────────────────────┐             │     │
                        │  │  │ Factor 3           │   │ Factor 4           │             │     │
                        │  │  │ Quantification     │   │ Format / Structure │             │     │
                        │  │  │ Score (0–100)      │   │ Score (0–100)      │             │     │
                        │  │  └────────────────────┘   └────────────────────┘             │     │
                        │  │  ┌────────────────────┐   ┌────────────────────┐             │     │
                        │  │  │ Factor 5           │   │ Factor 6           │             │     │
                        │  │  │ Skills Coverage    │   │ ATS Compatibility  │             │     │
                        │  │  │ Score (0–100)      │   │ Score (0–100)      │             │     │
                        │  │  └────────────────────┘   └────────────────────┘             │     │
                        │  │                                                                │     │
                        │  │         Weighted Average ──► Overall Score (0–100)            │     │
                        │  └──────────────────────────────────────────────────────────────┘     │
                        │          │ [scores]                                                    │
                        │          ▼                                                              │
                        │  ┌──────────────────┐                                                 │
                        │  │  3.6             │  [suggestions, missing_keywords,               │
                        │  │  Suggestion      │   improvement_tips]                             │
                        │  │  Generation      │  • Per-factor improvement tips                  │
                        │  │                  │  • Missing keyword recommendations              │
                        │  │                  │  • Action verb replacements                     │
                        │  └──────────────────┘                                                 │
                        │          │                                                              │
                        │          ▼                                                              │
                        │  [Save to resumes_resumeanalysis] ──► [Return to User]                │
                        └──────────────────────────────────────────────────────────────────────┘
```

✅ Section 3.1 complete. Type 'next' for the next section.

---

## 3.2 Table Specification (Database)

This section provides a full specification for every database table used in NextGenCV. Django's built-in `auth_user` table is included for completeness. All tables use SQLite as the underlying engine.

---

### Table 1 — `auth_user` (Django Built-in)

| Column Name    | Data Type     | Constraints                  | Description                                      |
|----------------|---------------|------------------------------|--------------------------------------------------|
| id             | INTEGER       | PK, AUTO INCREMENT           | Unique user identifier                           |
| username       | VARCHAR(150)  | NOT NULL, UNIQUE             | Login username                                   |
| email          | VARCHAR(254)  | NOT NULL                     | User email address                               |
| password       | VARCHAR(128)  | NOT NULL                     | Hashed password (PBKDF2 by default)              |
| first_name     | VARCHAR(150)  | NOT NULL, DEFAULT ''         | User's first name                                |
| last_name      | VARCHAR(150)  | NOT NULL, DEFAULT ''         | User's last name                                 |
| is_active      | BOOLEAN       | NOT NULL, DEFAULT TRUE       | Whether the account is active                    |
| is_staff       | BOOLEAN       | NOT NULL, DEFAULT FALSE      | Whether user can access Django admin             |
| is_superuser   | BOOLEAN       | NOT NULL, DEFAULT FALSE      | Whether user has all permissions                 |
| date_joined    | DATETIME      | NOT NULL                     | Timestamp when account was created               |
| last_login     | DATETIME      | NULL                         | Timestamp of most recent login                   |

---

### Table 2 — `resumes_resume`

| Column Name             | Data Type     | Constraints                        | Description                                          |
|-------------------------|---------------|------------------------------------|------------------------------------------------------|
| id                      | INTEGER       | PK, AUTO INCREMENT                 | Unique resume identifier                             |
| user_id                 | INTEGER       | FK → auth_user.id, NOT NULL        | Owner of the resume                                  |
| title                   | VARCHAR(200)  | NOT NULL                           | Resume title (e.g. "Software Engineer Resume")       |
| template                | VARCHAR(50)   | NOT NULL, DEFAULT 'professional'   | Selected template slug                               |
| summary                 | TEXT          | NOT NULL, DEFAULT ''               | Professional summary paragraph                       |
| is_draft                | BOOLEAN       | NOT NULL, DEFAULT TRUE             | Draft flag; FALSE = published/complete               |
| created_at              | DATETIME      | NOT NULL, AUTO                     | Creation timestamp                                   |
| updated_at              | DATETIME      | NOT NULL, AUTO UPDATE              | Last modification timestamp                          |
| current_version_number  | INTEGER       | NOT NULL, DEFAULT 1                | Tracks the latest version number                     |
| last_analyzed_at        | DATETIME      | NULL                               | Timestamp of most recent ATS analysis                |
| last_optimized_at       | DATETIME      | NULL                               | Timestamp of most recent AI optimisation             |
| latest_ats_score        | REAL          | NULL                               | Cached ATS score from last analysis                  |
| completeness_score      | INTEGER       | NOT NULL, DEFAULT 0                | Resume completeness percentage (0–100)               |
| share_token             | VARCHAR(64)   | NOT NULL, DEFAULT '', INDEX        | Token for public sharing link                        |
| color_scheme            | VARCHAR(50)   | NOT NULL, DEFAULT 'professional_blue' | Active colour scheme name                         |
| font_family             | VARCHAR(50)   | NOT NULL, DEFAULT 'Arial'          | Active font family name                              |

**Indexes:** `(user_id, -updated_at)`

---

### Table 3 — `resumes_personalinfo`

| Column Name | Data Type    | Constraints                          | Description                              |
|-------------|--------------|--------------------------------------|------------------------------------------|
| id          | INTEGER      | PK, AUTO INCREMENT                   | Unique record identifier                 |
| resume_id   | INTEGER      | FK → resumes_resume.id, UNIQUE, NOT NULL | One-to-one link to parent resume     |
| full_name   | VARCHAR(200) | NOT NULL                             | Candidate's full name                    |
| phone       | VARCHAR(20)  | NOT NULL, DEFAULT ''                 | Contact phone number                     |
| email       | VARCHAR(254) | NOT NULL, EmailValidator             | Contact email address                    |
| linkedin    | VARCHAR(200) | NULL, URLValidator                   | LinkedIn profile URL                     |
| github      | VARCHAR(200) | NULL, URLValidator                   | GitHub profile URL                       |
| location    | VARCHAR(200) | NOT NULL, DEFAULT ''                 | City, State / Country                    |

---

### Table 4 — `resumes_experience`

| Column Name  | Data Type    | Constraints                        | Description                                              |
|--------------|--------------|------------------------------------|----------------------------------------------------------|
| id           | INTEGER      | PK, AUTO INCREMENT                 | Unique record identifier                                 |
| resume_id    | INTEGER      | FK → resumes_resume.id, NOT NULL   | Parent resume                                            |
| company      | VARCHAR(200) | NOT NULL                           | Employer / company name                                  |
| role         | VARCHAR(200) | NOT NULL                           | Job title / role                                         |
| location     | VARCHAR(200) | NOT NULL, DEFAULT ''               | Work location (city, country)                            |
| start_date   | DATE         | NOT NULL                           | Employment start date                                    |
| end_date     | DATE         | NULL                               | Employment end date; NULL = current position             |
| description  | TEXT         | NOT NULL, DEFAULT ''               | Brief role overview                                      |
| achievements | TEXT         | NOT NULL, DEFAULT ''               | Bullet-point achievements (one per line)                 |
| order        | INTEGER      | NOT NULL, DEFAULT 0                | Display order within resume                              |

**Indexes:** `(resume_id, order)`, `(resume_id, -start_date)`

---

### Table 5 — `resumes_education`

| Column Name         | Data Type      | Constraints                        | Description                                    |
|---------------------|----------------|------------------------------------|------------------------------------------------|
| id                  | INTEGER        | PK, AUTO INCREMENT                 | Unique record identifier                       |
| resume_id           | INTEGER        | FK → resumes_resume.id, NOT NULL   | Parent resume                                  |
| institution         | VARCHAR(200)   | NOT NULL                           | University / college name                      |
| degree              | VARCHAR(200)   | NOT NULL                           | Degree type (e.g. BSc, MSc)                    |
| field               | VARCHAR(200)   | NULL, DEFAULT ''                   | Field of study / major                         |
| start_year          | INTEGER        | NOT NULL                           | Year studies began                             |
| end_year            | INTEGER        | NULL                               | Year studies ended; NULL = in progress         |
| gpa                 | DECIMAL(3,2)   | NULL                               | GPA out of 4.0                                 |
| honors              | VARCHAR(500)   | NOT NULL, DEFAULT ''               | Honours, awards, distinctions                  |
| relevant_coursework | TEXT           | NOT NULL, DEFAULT ''               | Comma-separated relevant courses               |
| order               | INTEGER        | NOT NULL, DEFAULT 0                | Display order within resume                    |

**Indexes:** `(resume_id, order)`, `(resume_id, -end_year)`

---

### Table 6 — `resumes_skill`

| Column Name         | Data Type   | Constraints                                    | Description                                      |
|---------------------|-------------|------------------------------------------------|--------------------------------------------------|
| id                  | INTEGER     | PK, AUTO INCREMENT                             | Unique record identifier                         |
| resume_id           | INTEGER     | FK → resumes_resume.id, NOT NULL               | Parent resume                                    |
| name                | VARCHAR(100)| NOT NULL                                       | Skill name (e.g. "Python")                       |
| category            | VARCHAR(50) | NOT NULL                                       | Skill category (Languages, Frameworks, Tools…)   |
| proficiency_level   | VARCHAR(20) | NOT NULL, DEFAULT 'intermediate', CHOICES      | beginner / intermediate / advanced / expert      |
| years_of_experience | INTEGER     | NULL                                           | Years of experience with this skill              |

**Unique constraint:** `(resume_id, name)`  
**Index:** `(resume_id, category)`

---

### Table 7 — `resumes_project`

| Column Name  | Data Type    | Constraints                        | Description                                        |
|--------------|--------------|------------------------------------|----------------------------------------------------|
| id           | INTEGER      | PK, AUTO INCREMENT                 | Unique record identifier                           |
| resume_id    | INTEGER      | FK → resumes_resume.id, NOT NULL   | Parent resume                                      |
| name         | VARCHAR(200) | NOT NULL                           | Project name                                       |
| description  | TEXT         | NOT NULL, DEFAULT ''               | Brief project description                          |
| technologies | VARCHAR(500) | NOT NULL, DEFAULT ''               | Comma-separated technologies used                  |
| impact       | TEXT         | NOT NULL, DEFAULT ''               | Quantifiable results / impact                      |
| url          | VARCHAR(200) | NOT NULL, DEFAULT '', URLValidator | GitHub, live demo, or portfolio link               |
| start_date   | DATE         | NULL                               | Project start date                                 |
| end_date     | DATE         | NULL                               | Project end date                                   |
| order        | INTEGER      | NOT NULL, DEFAULT 0                | Display order within resume                        |

**Index:** `(resume_id, order)`

---

### Table 8 — `resumes_resumeversion`

| Column Name       | Data Type   | Constraints                        | Description                                          |
|-------------------|-------------|------------------------------------|------------------------------------------------------|
| id                | INTEGER     | PK, AUTO INCREMENT                 | Unique record identifier                             |
| resume_id         | INTEGER     | FK → resumes_resume.id, NOT NULL   | Parent resume                                        |
| version_number    | INTEGER     | NOT NULL                           | Sequential version number                            |
| created_at        | DATETIME    | NOT NULL, AUTO                     | Snapshot creation timestamp                          |
| modification_type | VARCHAR(20) | NOT NULL, DEFAULT 'manual', CHOICES| manual / optimized / restored                        |
| ats_score         | REAL        | NULL                               | ATS score at time of snapshot                        |
| snapshot_data     | JSON        | NOT NULL                           | Complete resume state serialised as JSON             |
| user_notes        | TEXT        | NOT NULL, DEFAULT ''               | Optional user note for this version                  |

**Unique constraint:** `(resume_id, version_number)`  
**Indexes:** `(resume_id, -created_at)`, `(resume_id, created_at)`

---

### Table 9 — `resumes_uploadedresume`

| Column Name         | Data Type    | Constraints                        | Description                                        |
|---------------------|--------------|------------------------------------|----------------------------------------------------|
| id                  | INTEGER      | PK, AUTO INCREMENT                 | Unique record identifier                           |
| user_id             | INTEGER      | FK → auth_user.id, NOT NULL        | Uploading user                                     |
| original_filename   | VARCHAR(255) | NOT NULL                           | Original file name as uploaded                     |
| file_path           | VARCHAR(100) | NOT NULL                           | Server path: `uploads/YYYY/MM/DD/<file>`           |
| uploaded_at         | DATETIME     | NOT NULL, AUTO                     | Upload timestamp                                   |
| file_size           | INTEGER      | NOT NULL                           | File size in bytes                                 |
| extracted_text      | TEXT         | NOT NULL, DEFAULT ''               | Raw text extracted from PDF                        |
| parsing_confidence  | REAL         | NULL                               | Parser confidence score (0.0–1.0)                  |
| parsed_data         | JSON         | NULL                               | Structured data extracted from PDF                 |
| status              | VARCHAR(20)  | NOT NULL, DEFAULT 'uploaded', CHOICES | uploaded / parsing / parsed / imported / failed |
| error_message       | TEXT         | NOT NULL, DEFAULT ''               | Error detail if parsing failed                     |

**Index:** `(user_id, -uploaded_at)`

---

### Table 10 — `resumes_resumeanalysis`

| Column Name                | Data Type | Constraints                        | Description                                        |
|----------------------------|-----------|------------------------------------|---------------------------------------------------|
| id                         | INTEGER   | PK, AUTO INCREMENT                 | Unique record identifier                           |
| resume_id                  | INTEGER   | FK → resumes_resume.id, NOT NULL   | Analysed resume                                    |
| job_description            | TEXT      | NOT NULL                           | Job description text used for analysis             |
| analysis_timestamp         | DATETIME  | NOT NULL, AUTO                     | When the analysis was run                          |
| keyword_match_score        | REAL      | NOT NULL                           | Factor 1: keyword match score (0–100)              |
| skill_relevance_score      | REAL      | NOT NULL                           | Factor 2: skill relevance score (0–100)            |
| section_completeness_score | REAL      | NOT NULL                           | Factor 3: section completeness score (0–100)       |
| experience_impact_score    | REAL      | NOT NULL                           | Factor 4: experience impact / action verb score    |
| quantification_score       | REAL      | NOT NULL                           | Factor 5: quantification score (0–100)             |
| action_verb_score          | REAL      | NOT NULL                           | Factor 6: action verb quality score (0–100)        |
| final_score                | REAL      | NOT NULL                           | Weighted composite ATS score (0–100)               |
| matched_keywords           | JSON      | NOT NULL, DEFAULT []               | List of keywords found in both resume and JD       |
| missing_keywords           | JSON      | NOT NULL, DEFAULT []               | List of JD keywords absent from resume             |
| weak_action_verbs          | JSON      | NOT NULL, DEFAULT []               | Weak verbs detected with suggested replacements    |
| missing_quantifications    | JSON      | NOT NULL, DEFAULT []               | Bullet points lacking measurable metrics           |
| suggestions                | JSON      | NOT NULL, DEFAULT []               | Ordered list of improvement suggestions            |

**Index:** `(resume_id, -analysis_timestamp)`

---

### Table 11 — `resumes_optimizationhistory`

| Column Name            | Data Type | Constraints                                      | Description                                          |
|------------------------|-----------|--------------------------------------------------|------------------------------------------------------|
| id                     | INTEGER   | PK, AUTO INCREMENT                               | Unique record identifier                             |
| resume_id              | INTEGER   | FK → resumes_resume.id, NOT NULL                 | Resume being optimised                               |
| original_version_id    | INTEGER   | FK → resumes_resumeversion.id, SET NULL, NULL    | Version snapshot before optimisation                 |
| optimized_version_id   | INTEGER   | FK → resumes_resumeversion.id, SET NULL, NULL    | Version snapshot after optimisation                  |
| job_description        | TEXT      | NOT NULL                                         | Job description used for optimisation                |
| optimization_timestamp | DATETIME  | NOT NULL, AUTO                                   | When optimisation was run                            |
| original_score         | REAL      | NOT NULL                                         | ATS score before optimisation                        |
| optimized_score        | REAL      | NULL                                             | ATS score after optimisation                         |
| improvement_delta      | REAL      | NULL                                             | Score difference (optimized − original)              |
| changes_summary        | JSON      | NOT NULL, DEFAULT {}                             | Count of changes by type `{type: count}`             |
| detailed_changes       | JSON      | NOT NULL, DEFAULT []                             | Full change log `[{section, field, old, new, reason}]` |
| accepted_changes       | JSON      | NOT NULL, DEFAULT []                             | Changes accepted by the user                         |
| rejected_changes       | JSON      | NOT NULL, DEFAULT []                             | Changes rejected by the user                         |
| user_notes             | TEXT      | NOT NULL, DEFAULT ''                             | Optional user notes on this optimisation             |

**Index:** `(resume_id, -optimization_timestamp)`

---

### Table 12 — `resumes_certification`

| Column Name    | Data Type    | Constraints                        | Description                                    |
|----------------|--------------|------------------------------------|------------------------------------------------|
| id             | INTEGER      | PK, AUTO INCREMENT                 | Unique record identifier                       |
| resume_id      | INTEGER      | FK → resumes_resume.id, NOT NULL   | Parent resume                                  |
| name           | VARCHAR(200) | NOT NULL                           | Certification name                             |
| issuer         | VARCHAR(200) | NOT NULL, DEFAULT ''               | Issuing organisation                           |
| issue_date     | DATE         | NULL                               | Date certification was issued                  |
| expiry_date    | DATE         | NULL                               | Expiry date; NULL = does not expire            |
| credential_id  | VARCHAR(200) | NOT NULL, DEFAULT ''               | Unique credential / badge ID                   |
| credential_url | VARCHAR(200) | NOT NULL, DEFAULT ''               | Verification URL                               |
| order          | INTEGER      | NOT NULL, DEFAULT 0                | Display order within resume                    |

**Ordering:** `(order, -issue_date)`

---

### Table 13 — `templates_mgmt_resumetemplate`

| Column Name                   | Data Type    | Constraints                  | Description                                          |
|-------------------------------|--------------|------------------------------|------------------------------------------------------|
| id                            | INTEGER      | PK, AUTO INCREMENT           | Unique template identifier                           |
| name                          | VARCHAR(100) | NOT NULL, UNIQUE             | Template slug / display name                         |
| description                   | TEXT         | NOT NULL, DEFAULT ''         | Human-readable template description                  |
| template_file                 | VARCHAR(200) | NOT NULL                     | Relative path to the HTML template file              |
| thumbnail                     | VARCHAR(100) | NULL                         | Path to thumbnail image (upload_to: template_thumbnails/) |
| is_active                     | BOOLEAN      | NOT NULL, DEFAULT TRUE       | Whether template is available to users               |
| is_default                    | BOOLEAN      | NOT NULL, DEFAULT FALSE      | Whether this is the system default template          |
| created_at                    | DATETIME     | NOT NULL, AUTO               | Creation timestamp                                   |
| updated_at                    | DATETIME     | NOT NULL, AUTO UPDATE        | Last update timestamp                                |
| usage_count                   | INTEGER      | NOT NULL, DEFAULT 0          | Number of resumes using this template                |
| supports_color_customization  | BOOLEAN      | NOT NULL, DEFAULT TRUE       | Whether colour scheme can be changed                 |
| supports_font_customization   | BOOLEAN      | NOT NULL, DEFAULT TRUE       | Whether font family can be changed                   |
| available_colors              | JSON         | NOT NULL, DEFAULT []         | List of supported colour scheme names                |
| available_fonts               | JSON         | NOT NULL, DEFAULT []         | List of supported font family names                  |

---

### Table 14 — `templates_mgmt_templatecustomization`

| Column Name  | Data Type    | Constraints                                    | Description                                      |
|--------------|--------------|------------------------------------------------|--------------------------------------------------|
| id           | INTEGER      | PK, AUTO INCREMENT                             | Unique record identifier                         |
| resume_id    | INTEGER      | FK → resumes_resume.id, UNIQUE, NOT NULL       | One-to-one link to resume                        |
| template_id  | INTEGER      | FK → templates_mgmt_resumetemplate.id, PROTECT | Selected template (protected from deletion)      |
| color_scheme | VARCHAR(50)  | NOT NULL, DEFAULT ''                           | Active colour scheme name                        |
| font_family  | VARCHAR(100) | NOT NULL, DEFAULT ''                           | Active font family name                          |
| custom_css   | TEXT         | NOT NULL, DEFAULT ''                           | User-supplied CSS overrides                      |
| created_at   | DATETIME     | NOT NULL, AUTO                                 | Customisation creation timestamp                 |

---

### Table 15 — `tracker_jobapplication`

| Column Name        | Data Type    | Constraints                                      | Description                                          |
|--------------------|--------------|--------------------------------------------------|------------------------------------------------------|
| id                 | INTEGER      | PK, AUTO INCREMENT                               | Unique application identifier                        |
| user_id            | INTEGER      | FK → auth_user.id, NOT NULL                      | Owning user                                          |
| company            | VARCHAR(200) | NOT NULL                                         | Company applied to                                   |
| role               | VARCHAR(200) | NOT NULL                                         | Job title applied for                                |
| job_url            | VARCHAR(200) | NOT NULL, DEFAULT ''                             | Link to the job posting                              |
| job_description    | TEXT         | NOT NULL, DEFAULT ''                             | Full job description text                            |
| resume_id          | INTEGER      | FK → resumes_resume.id, SET NULL, NULL           | Resume used for this application                     |
| resume_version_id  | INTEGER      | FK → resumes_resumeversion.id, SET NULL, NULL    | Specific version of resume used                      |
| status             | VARCHAR(20)  | NOT NULL, DEFAULT 'saved', CHOICES               | saved / applied / interview / offer / rejected / withdrawn |
| ats_score_at_apply | REAL         | NULL                                             | ATS score of resume at time of application           |
| applied_date       | DATE         | NULL                                             | Date application was submitted                       |
| notes              | TEXT         | NOT NULL, DEFAULT ''                             | User notes on this application                       |
| created_at         | DATETIME     | NOT NULL, AUTO                                   | Record creation timestamp                            |
| updated_at         | DATETIME     | NOT NULL, AUTO UPDATE                            | Last update timestamp                                |

**Indexes:** `(user_id, -updated_at)`, `(user_id, status)`

---

### Table 16 — `tracker_coverletter`

| Column Name    | Data Type    | Constraints                                          | Description                                      |
|----------------|--------------|------------------------------------------------------|--------------------------------------------------|
| id             | INTEGER      | PK, AUTO INCREMENT                                   | Unique record identifier                         |
| user_id        | INTEGER      | FK → auth_user.id, NOT NULL                          | Owning user                                      |
| application_id | INTEGER      | FK → tracker_jobapplication.id, CASCADE, UNIQUE, NULL| Linked job application (optional, one-to-one)    |
| resume_id      | INTEGER      | FK → resumes_resume.id, SET NULL, NULL               | Resume the letter was generated from             |
| company        | VARCHAR(200) | NOT NULL                                             | Target company name                              |
| role           | VARCHAR(200) | NOT NULL                                             | Target role / job title                          |
| content        | TEXT         | NOT NULL                                             | Full cover letter text                           |
| created_at     | DATETIME     | NOT NULL, AUTO                                       | Creation timestamp                               |
| updated_at     | DATETIME     | NOT NULL, AUTO UPDATE                                | Last update timestamp                            |

---

### Table 17 — `tracker_interviewprepsession`

| Column Name     | Data Type    | Constraints                                      | Description                                              |
|-----------------|--------------|--------------------------------------------------|----------------------------------------------------------|
| id              | INTEGER      | PK, AUTO INCREMENT                               | Unique session identifier                                |
| user_id         | INTEGER      | FK → auth_user.id, NOT NULL                      | Owning user                                              |
| application_id  | INTEGER      | FK → tracker_jobapplication.id, CASCADE, NULL    | Linked job application (optional)                        |
| resume_id       | INTEGER      | FK → resumes_resume.id, SET NULL, NULL           | Resume used as context for question generation           |
| role            | VARCHAR(200) | NOT NULL                                         | Target role for interview preparation                    |
| company         | VARCHAR(200) | NOT NULL, DEFAULT ''                             | Target company name                                      |
| job_description | TEXT         | NOT NULL, DEFAULT ''                             | Job description used to generate questions               |
| questions       | JSON         | NOT NULL, DEFAULT []                             | `[{question, category, talking_points, resume_evidence}]`|
| created_at      | DATETIME     | NOT NULL, AUTO                                   | Session creation timestamp                               |

---

### Table 18 — `tracker_skillgapanalysis`

| Column Name      | Data Type    | Constraints                                  | Description                                          |
|------------------|--------------|----------------------------------------------|------------------------------------------------------|
| id               | INTEGER      | PK, AUTO INCREMENT                           | Unique record identifier                             |
| user_id          | INTEGER      | FK → auth_user.id, NOT NULL                  | Owning user                                          |
| resume_id        | INTEGER      | FK → resumes_resume.id, SET NULL, NULL       | Resume analysed for skill gaps                       |
| target_role      | VARCHAR(200) | NOT NULL                                     | Target job role for gap analysis                     |
| job_descriptions | JSON         | NOT NULL, DEFAULT []                         | List of JD texts used in analysis                    |
| missing_skills   | JSON         | NOT NULL, DEFAULT []                         | `[{skill, frequency, importance}]`                   |
| present_skills   | JSON         | NOT NULL, DEFAULT []                         | Skills already present in resume                     |
| recommendations  | JSON         | NOT NULL, DEFAULT []                         | Learning / upskilling recommendations                |
| created_at       | DATETIME     | NOT NULL, AUTO                               | Analysis creation timestamp                          |

---

### Table 19 — `authentication_activitylog`

| Column Name   | Data Type    | Constraints                        | Description                                              |
|---------------|--------------|------------------------------------|----------------------------------------------------------|
| id            | INTEGER      | PK, AUTO INCREMENT                 | Unique log entry identifier                              |
| user_id       | INTEGER      | FK → auth_user.id, NOT NULL        | User who performed the action                            |
| action        | VARCHAR(50)  | NOT NULL, CHOICES                  | Action type (resume_created, resume_analyzed, etc.)      |
| description   | VARCHAR(300) | NOT NULL                           | Human-readable description of the action                 |
| resume_id     | INTEGER      | NULL                               | ID of related resume (denormalised for speed)            |
| resume_title  | VARCHAR(200) | NOT NULL, DEFAULT ''               | Title of related resume (denormalised for speed)         |
| metadata      | JSON         | NOT NULL, DEFAULT {}               | Additional context data for the action                   |
| created_at    | DATETIME     | NOT NULL, AUTO                     | Timestamp of the action                                  |

**Index:** `(user_id, -created_at)`  
**Note:** Capped at 200 entries per user; oldest entries are auto-deleted.

---

### Table 20 — `authentication_savedjobdescription`

| Column Name  | Data Type    | Constraints                        | Description                                          |
|--------------|--------------|------------------------------------|------------------------------------------------------|
| id           | INTEGER      | PK, AUTO INCREMENT                 | Unique record identifier                             |
| user_id      | INTEGER      | FK → auth_user.id, NOT NULL        | Owning user                                          |
| title        | VARCHAR(200) | NOT NULL                           | Short label (e.g. "Senior Python Dev @ Google")      |
| company      | VARCHAR(200) | NOT NULL, DEFAULT ''               | Company name                                         |
| job_url      | VARCHAR(200) | NOT NULL, DEFAULT ''               | Link to original job posting                         |
| content      | TEXT         | NOT NULL                           | Full job description text                            |
| created_at   | DATETIME     | NOT NULL, AUTO                     | Creation timestamp                                   |
| last_used_at | DATETIME     | NULL                               | Timestamp when last used for analysis                |

**Index:** `(user_id, -created_at)`

---

✅ Section 3.2 complete. Type 'next' for the next section.

---

## 3.3 Entity Relationship Diagram (ERD)

The full ERD is split into three sub-diagrams for clarity. Cardinality notation used:
- `||` = exactly one
- `|<` or `>|` = one (mandatory side)
- `o<` or `>o` = zero or one (optional)
- `||--o{` = one-to-many (zero or more)
- `||--||` = one-to-one

---

### Sub-Diagram 1 — Core Resume ERD

```
┌─────────────────────────────┐
│         auth_user           │
├─────────────────────────────┤
│ PK  id          INTEGER     │
│     username    VARCHAR(150)│
│     email       VARCHAR(254)│
│     password    VARCHAR(128)│
│     first_name  VARCHAR(150)│
│     last_name   VARCHAR(150)│
│     is_active   BOOLEAN     │
│     is_staff    BOOLEAN     │
│     date_joined DATETIME    │
└──────────────┬──────────────┘
               │ 1
               │
               │ M  (one user → many resumes)
               ▼
┌─────────────────────────────┐
│       resumes_resume        │
├─────────────────────────────┤
│ PK  id                      │
│ FK  user_id                 │
│     title       VARCHAR(200)│
│     template    VARCHAR(50) │
│     summary     TEXT        │
│     is_draft    BOOLEAN     │
│     created_at  DATETIME    │
│     updated_at  DATETIME    │
│     current_version_number  │
│     latest_ats_score  REAL  │
│     completeness_score INT  │
│     share_token VARCHAR(64) │
│     color_scheme VARCHAR(50)│
│     font_family  VARCHAR(50)│
└──┬──────┬──────┬──────┬─────┘
   │      │      │      │
   │1     │1     │1     │1
   │      │      │      │
   │1     │M     │M     │M
   ▼      ▼      ▼      ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ resumes_     │  │ resumes_     │  │ resumes_     │  │ resumes_     │
│ personalinfo │  │ experience   │  │ education    │  │ skill        │
├──────────────┤  ├──────────────┤  ├──────────────┤  ├──────────────┤
│PK id         │  │PK id         │  │PK id         │  │PK id         │
│FK resume_id  │  │FK resume_id  │  │FK resume_id  │  │FK resume_id  │
│   full_name  │  │   company    │  │   institution│  │   name       │
│   phone      │  │   role       │  │   degree     │  │   category   │
│   email      │  │   location   │  │   field      │  │   proficiency│
│   linkedin   │  │   start_date │  │   start_year │  │   years_exp  │
│   github     │  │   end_date   │  │   end_year   │  └──────────────┘
│   location   │  │   description│  │   gpa        │
└──────────────┘  │   achievements│  │   honors     │
  (1:1 with       │   order      │  │   coursework │
   resume)        └──────────────┘  │   order      │
                  (1:M with resume) └──────────────┘
                                    (1:M with resume)

   resume 1
   │
   ├──────────────────────────────────────────────────────┐
   │ M                                                    │ M
   ▼                                                      ▼
┌──────────────────────┐              ┌──────────────────────┐
│   resumes_project    │              │ resumes_certification│
├──────────────────────┤              ├──────────────────────┤
│ PK id                │              │ PK id                │
│ FK resume_id         │              │ FK resume_id         │
│    name              │              │    name              │
│    description       │              │    issuer            │
│    technologies      │              │    issue_date        │
│    impact            │              │    expiry_date       │
│    url               │              │    credential_id     │
│    start_date        │              │    credential_url    │
│    end_date          │              │    order             │
│    order             │              └──────────────────────┘
└──────────────────────┘              (1:M with resume)
(1:M with resume)
```

---

### Sub-Diagram 2 — Analysis & Versioning ERD

```
┌─────────────────────────────┐
│       resumes_resume        │
│  PK id  |  FK user_id  ...  │
└──┬──────┬──────┬──────┬─────┘
   │      │      │      │
   │1     │1     │1     │1
   │      │      │      │
   │M     │M     │M     │M
   ▼      ▼      ▼      ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  resumes_    │  │  resumes_    │  │  resumes_    │  │  templates_  │
│ resumeversion│  │resumeanalysis│  │optimization  │  │ mgmt_template│
│              │  │              │  │  history     │  │ customization│
├──────────────┤  ├──────────────┤  ├──────────────┤  ├──────────────┤
│PK id         │  │PK id         │  │PK id         │  │PK id         │
│FK resume_id  │  │FK resume_id  │  │FK resume_id  │  │FK resume_id  │
│   version_no │  │   job_desc   │  │FK orig_ver_id│  │FK template_id│
│   created_at │  │   timestamp  │  │FK opt_ver_id │  │   color_sch  │
│   mod_type   │  │   kw_score   │  │   job_desc   │  │   font_fam   │
│   ats_score  │  │   skill_score│  │   orig_score │  │   custom_css │
│   snapshot   │  │   section_sc │  │   opt_score  │  │   created_at │
│   user_notes │  │   exp_score  │  │   delta      │  └──────────────┘
└──────┬───────┘  │   quant_score│  │   changes    │  (1:1 with resume)
       │          │   verb_score │  │   accepted   │
       │          │   final_score│  │   rejected   │
       │          │   matched_kw │  └──────┬───────┘
       │          │   missing_kw │         │
       │          │   suggestions│         │ FK orig_version_id
       │          └──────────────┘         │ FK opt_version_id
       │          (1:M with resume)        │ (M:1 back to resumeversion)
       │                                   │
       └───────────────────────────────────┘
         resumeversion ←── optimizationhistory
         (one version can be referenced as
          original OR optimized in many
          optimization records)

┌─────────────────────────────┐
│      auth_user              │
│  PK id  ...                 │
└──────────────┬──────────────┘
               │ 1
               │ M
               ▼
┌─────────────────────────────┐
│    resumes_uploadedresume   │
├─────────────────────────────┤
│ PK id                       │
│ FK user_id                  │
│    original_filename        │
│    file_path                │
│    uploaded_at              │
│    file_size                │
│    extracted_text           │
│    parsing_confidence       │
│    parsed_data   JSON       │
│    status                   │
│    error_message            │
└─────────────────────────────┘
(1:M  user → uploaded resumes;
 independent of resumes_resume
 until imported)

┌─────────────────────────────┐
│  templates_mgmt_            │
│  resumetemplate             │
├─────────────────────────────┤
│ PK id                       │
│    name         UNIQUE      │
│    description              │
│    template_file            │
│    thumbnail                │
│    is_active                │
│    is_default               │
│    usage_count              │
│    supports_color           │
│    supports_font            │
│    available_colors  JSON   │
│    available_fonts   JSON   │
└──────────────┬──────────────┘
               │ 1
               │ M  (one template → many customizations)
               ▼
┌─────────────────────────────┐
│  templates_mgmt_            │
│  templatecustomization      │
├─────────────────────────────┤
│ PK id                       │
│ FK resume_id   (1:1)        │
│ FK template_id              │
│    color_scheme             │
│    font_family              │
│    custom_css               │
│    created_at               │
└─────────────────────────────┘
```

---

### Sub-Diagram 3 — Tracker ERD

```
┌─────────────────────────────┐        ┌─────────────────────────────┐
│         auth_user           │        │       resumes_resume        │
│  PK id  ...                 │        │  PK id  ...                 │
└──────────────┬──────────────┘        └──────────────┬──────────────┘
               │ 1                                    │ 1
               │                                      │
               │ M                                    │ M
               ▼                                      ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      tracker_jobapplication                          │
├──────────────────────────────────────────────────────────────────────┤
│ PK  id                                                               │
│ FK  user_id            → auth_user.id          (NOT NULL)            │
│ FK  resume_id          → resumes_resume.id      (NULL, SET NULL)     │
│ FK  resume_version_id  → resumes_resumeversion.id (NULL, SET NULL)  │
│     company            VARCHAR(200)                                  │
│     role               VARCHAR(200)                                  │
│     job_url            VARCHAR(200)                                  │
│     job_description    TEXT                                          │
│     status             VARCHAR(20)  CHOICES                          │
│     ats_score_at_apply REAL                                          │
│     applied_date       DATE                                          │
│     notes              TEXT                                          │
│     created_at         DATETIME                                      │
│     updated_at         DATETIME                                      │
└──────┬──────────────────────────────────────────────────────────────┘
       │ 1
       │
       ├─────────────────────────────────────────────────────────────┐
       │ 1 (optional)                                                │ M (optional)
       ▼                                                             ▼
┌──────────────────────────┐              ┌──────────────────────────┐
│   tracker_coverletter    │              │ tracker_interviewprep    │
│                          │              │       session            │
├──────────────────────────┤              ├──────────────────────────┤
│ PK id                    │              │ PK id                    │
│ FK user_id               │              │ FK user_id               │
│ FK application_id (1:1)  │              │ FK application_id        │
│ FK resume_id             │              │ FK resume_id             │
│    company               │              │    role                  │
│    role                  │              │    company               │
│    content  TEXT         │              │    job_description       │
│    created_at            │              │    questions  JSON       │
│    updated_at            │              │    created_at            │
└──────────────────────────┘              └──────────────────────────┘
(1:1 optional with                        (1:M optional with
 jobapplication)                           jobapplication)

┌─────────────────────────────┐        ┌─────────────────────────────┐
│         auth_user           │        │       resumes_resume        │
│  PK id  ...                 │        │  PK id  ...                 │
└──────────────┬──────────────┘        └──────────────┬──────────────┘
               │ 1                                    │ 1
               │ M                                    │ M
               ▼                                      ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    tracker_skillgapanalysis                          │
├──────────────────────────────────────────────────────────────────────┤
│ PK  id                                                               │
│ FK  user_id          → auth_user.id         (NOT NULL)               │
│ FK  resume_id        → resumes_resume.id    (NULL, SET NULL)         │
│     target_role      VARCHAR(200)                                    │
│     job_descriptions JSON                                            │
│     missing_skills   JSON                                            │
│     present_skills   JSON                                            │
│     recommendations  JSON                                            │
│     created_at       DATETIME                                        │
└──────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────┐
│         auth_user           │
│  PK id  ...                 │
└──────────────┬──────────────┘
               │ 1
               ├──────────────────────────────────────────────────────┐
               │ M                                                    │ M
               ▼                                                      ▼
┌──────────────────────────────┐        ┌──────────────────────────────┐
│  authentication_activitylog  │        │ authentication_saved         │
│                              │        │    jobdescription            │
├──────────────────────────────┤        ├──────────────────────────────┤
│ PK id                        │        │ PK id                        │
│ FK user_id                   │        │ FK user_id                   │
│    action      VARCHAR(50)   │        │    title    VARCHAR(200)     │
│    description VARCHAR(300)  │        │    company  VARCHAR(200)     │
│    resume_id   INT (denorm.) │        │    job_url  VARCHAR(200)     │
│    resume_title VARCHAR(200) │        │    content  TEXT             │
│    metadata    JSON          │        │    created_at               │
│    created_at                │        │    last_used_at             │
└──────────────────────────────┘        └──────────────────────────────┘
(1:M  user → activity logs)             (1:M  user → saved JDs)
```

---

### Cardinality Summary Table

| Relationship                                          | Type  | Notes                                      |
|-------------------------------------------------------|-------|--------------------------------------------|
| auth_user → resumes_resume                            | 1 : M | One user owns many resumes                 |
| resumes_resume → resumes_personalinfo                 | 1 : 1 | Each resume has exactly one personal info  |
| resumes_resume → resumes_experience                   | 1 : M | One resume has many experience entries     |
| resumes_resume → resumes_education                    | 1 : M | One resume has many education entries      |
| resumes_resume → resumes_skill                        | 1 : M | One resume has many skills                 |
| resumes_resume → resumes_project                      | 1 : M | One resume has many projects               |
| resumes_resume → resumes_certification                | 1 : M | One resume has many certifications         |
| resumes_resume → resumes_resumeversion                | 1 : M | One resume has many version snapshots      |
| resumes_resume → resumes_resumeanalysis               | 1 : M | One resume has many analysis records       |
| resumes_resume → resumes_optimizationhistory          | 1 : M | One resume has many optimisation records   |
| resumes_resumeversion → resumes_optimizationhistory   | 1 : M | One version referenced as original/optimized |
| auth_user → resumes_uploadedresume                    | 1 : M | One user uploads many PDF files            |
| resumes_resume → templates_mgmt_templatecustomization | 1 : 1 | Each resume has one customisation record   |
| templates_mgmt_resumetemplate → templatecustomization | 1 : M | One template used by many customisations   |
| auth_user → tracker_jobapplication                    | 1 : M | One user tracks many applications          |
| resumes_resume → tracker_jobapplication               | 1 : M | One resume linked to many applications     |
| tracker_jobapplication → tracker_coverletter          | 1 : 1 | One application has at most one cover letter |
| tracker_jobapplication → tracker_interviewprepsession | 1 : M | One application can have many prep sessions |
| auth_user → tracker_skillgapanalysis                  | 1 : M | One user runs many skill gap analyses      |
| auth_user → authentication_activitylog                | 1 : M | One user has many activity log entries     |
| auth_user → authentication_savedjobdescription        | 1 : M | One user saves many job descriptions       |

---

✅ Section 3.3 complete. Type 'next' for the next section.

---

## 3.4 Object Diagram

The object diagram below shows a concrete runtime snapshot of the NextGenCV system. It captures real in-memory object instances with example attribute values, illustrating how the model layer looks at a specific point in time for user **sarah_dev**.

```
╔══════════════════════════════════════════════════════════════════════════════════╗
║                         OBJECT DIAGRAM — Runtime Snapshot                       ║
║                    User: sarah_dev  |  Date: 2026-05-09 14:32:00                ║
╚══════════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────┐
│  user1 : auth_user                          │
├─────────────────────────────────────────────┤
│  id           = 42                          │
│  username     = "sarah_dev"                 │
│  email        = "sarah@example.com"         │
│  first_name   = "Sarah"                     │
│  last_name    = "Mitchell"                  │
│  is_active    = True                        │
│  is_staff     = False                       │
│  date_joined  = 2025-11-03 09:15:00         │
└──────────────────┬──────────────────────────┘
                   │ user_id (FK)
          ┌────────┴────────┐
          │                 │
          ▼                 ▼
┌─────────────────────┐   ┌─────────────────────────────┐
│  resume1 : Resume   │   │  resume2 : Resume            │
├─────────────────────┤   ├─────────────────────────────┤
│  id            = 101│   │  id              = 102       │
│  user_id       = 42 │   │  user_id         = 42        │
│  title         =    │   │  title           =           │
│  "Software Eng  "   │   │  "Data Scientist Resume"     │
│  "Resume 2026"  "   │   │  template        = "modern"  │
│  template      =    │   │  summary         =           │
│  "professional" │   │   │  "ML engineer with 3 yrs..." │
│  summary       =    │   │  is_draft        = True      │
│  "Full-stack dev"   │   │  latest_ats_score = None     │
│  "with 5 yrs exp"   │   │  completeness_score = 35     │
│  is_draft      =    │   │  current_version_number = 1  │
│  False          │   │   │  created_at = 2026-04-20     │
│  latest_ats_score=  │   │  updated_at = 2026-04-20     │
│  78.5           │   │   └─────────────────────────────┘
│  completeness_  │   │   (resume2 is a work-in-progress
│  score     = 91 │   │    draft, not yet analysed)
│  current_version│   │
│  _number   = 3  │   │
│  color_scheme = │   │
│  "professional_ │   │
│   blue"         │   │
│  font_family =  │   │
│  "Arial"        │   │
│  created_at =   │   │
│  2026-01-15      │   │
│  updated_at =   │   │
│  2026-05-09      │   │
└────────┬────────┘
         │ resume_id (FK)
         │
    ┌────┴──────────────────────────────────────────────────────────┐
    │                                                               │
    ▼                                                               │
┌──────────────────────────────────────┐                           │
│  personalInfo1 : PersonalInfo        │                           │
├──────────────────────────────────────┤                           │
│  id          = 88                    │                           │
│  resume_id   = 101                   │                           │
│  full_name   = "Sarah Mitchell"      │                           │
│  phone       = "+1-555-0192"         │                           │
│  email       = "sarah@example.com"   │                           │
│  linkedin    = "linkedin.com/in/     │                           │
│                 sarah-mitchell-dev"  │                           │
│  github      = "github.com/sarah-m" │                           │
│  location    = "Austin, TX, USA"     │                           │
└──────────────────────────────────────┘                           │
(1:1 with resume1)                                                 │
                                                                   │
    ┌──────────────────────────────────────────────────────────────┘
    │ resume_id (FK)
    │
    ├──────────────────────────────────────────────────────────────┐
    ▼                                                              ▼
┌──────────────────────────────────────┐  ┌──────────────────────────────────────┐
│  experience1 : Experience            │  │  experience2 : Experience            │
├──────────────────────────────────────┤  ├──────────────────────────────────────┤
│  id          = 201                   │  │  id          = 202                   │
│  resume_id   = 101                   │  │  resume_id   = 101                   │
│  company     = "TechCorp Inc."       │  │  company     = "StartupXYZ"          │
│  role        = "Senior Software Eng" │  │  role        = "Junior Developer"    │
│  location    = "Austin, TX"          │  │  location    = "Remote"              │
│  start_date  = 2022-03-01            │  │  start_date  = 2020-06-01            │
│  end_date    = None  (current)       │  │  end_date    = 2022-02-28            │
│  description = "Led backend dev for  │  │  description = "Built REST APIs and  │
│   microservices platform"            │  │   React dashboards"                  │
│  achievements= "Reduced API latency  │  │  achievements= "Delivered 3 features │
│   by 40%\nLed team of 6 engineers\n  │  │   on time\nImproved test coverage    │
│   Migrated 2M records to PostgreSQL" │  │   from 45% to 80%"                  │
│  order       = 0                     │  │  order       = 1                     │
└──────────────────────────────────────┘  └──────────────────────────────────────┘

    │ resume_id (FK)
    ▼
┌──────────────────────────────────────┐
│  education1 : Education              │
├──────────────────────────────────────┤
│  id          = 301                   │
│  resume_id   = 101                   │
│  institution = "University of Texas" │
│  degree      = "BSc"                 │
│  field       = "Computer Science"    │
│  start_year  = 2016                  │
│  end_year    = 2020                  │
│  gpa         = 3.82                  │
│  honors      = "Magna Cum Laude"     │
│  relevant_   =                       │
│  coursework  = "Algorithms, OS,      │
│                 Distributed Systems" │
│  order       = 0                     │
└──────────────────────────────────────┘

    │ resume_id (FK)
    ├──────────────────────────────────────────────────────────────┐
    ▼                                                              │
┌──────────────────────────┐  ┌──────────────────────────┐  ┌──────────────────────────┐
│  skill1 : Skill          │  │  skill2 : Skill          │  │  skill3 : Skill          │
├──────────────────────────┤  ├──────────────────────────┤  ├──────────────────────────┤
│  id          = 401       │  │  id          = 402       │  │  id          = 403       │
│  resume_id   = 101       │  │  resume_id   = 101       │  │  resume_id   = 101       │
│  name        = "Python"  │  │  name        = "Django"  │  │  name        = "Docker"  │
│  category    = "Languages"│  │  category    ="Frameworks"│  │  category    = "Tools"  │
│  proficiency = "expert"  │  │  proficiency = "advanced"│  │  proficiency ="advanced" │
│  years_exp   = 5         │  │  years_exp   = 4         │  │  years_exp   = 3         │
└──────────────────────────┘  └──────────────────────────┘  └──────────────────────────┘

    │ resume_id (FK)
    ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│  analysis1 : ResumeAnalysis                                                      │
├──────────────────────────────────────────────────────────────────────────────────┤
│  id                         = 501                                                │
│  resume_id                  = 101                                                │
│  job_description            = "We are looking for a Senior Software Engineer     │
│                                with Python, Django, REST APIs, Docker, AWS..."   │
│  analysis_timestamp         = 2026-05-09 14:30:00                               │
│  keyword_match_score        = 82.0                                               │
│  skill_relevance_score      = 88.0                                               │
│  section_completeness_score = 95.0                                               │
│  experience_impact_score    = 71.0                                               │
│  quantification_score       = 68.0                                               │
│  action_verb_score          = 66.5                                               │
│  final_score                = 78.5                                               │
│  matched_keywords           = ["Python", "Django", "REST API", "Docker",         │
│                                "microservices", "PostgreSQL"]                    │
│  missing_keywords           = ["AWS", "Kubernetes", "CI/CD", "Terraform"]       │
│  weak_action_verbs          = [{"verb": "worked on", "suggestion": "engineered"},│
│                                {"verb": "helped with","suggestion": "delivered"}]│
│  missing_quantifications    = ["StartupXYZ: achievement 3 lacks a metric"]      │
│  suggestions                = ["Add AWS experience or certification",            │
│                                "Replace weak verbs in experience section",       │
│                                "Quantify StartupXYZ achievements"]              │
└──────────────────────────────────────────────────────────────────────────────────┘
(linked to resume1 via resume_id = 101)

    │ resume_id (FK) + user_id (FK)
    ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│  application1 : JobApplication                                                   │
├──────────────────────────────────────────────────────────────────────────────────┤
│  id                  = 601                                                       │
│  user_id             = 42                                                        │
│  company             = "CloudBase Ltd."                                          │
│  role                = "Senior Software Engineer"                                │
│  job_url             = "https://jobs.cloudbase.io/senior-swe-2026"              │
│  resume_id           = 101                                                       │
│  resume_version_id   = 15   (version 3 snapshot of resume1)                     │
│  status              = "interview"                                               │
│  ats_score_at_apply  = 78.5                                                      │
│  applied_date        = 2026-05-07                                                │
│  notes               = "Recruiter reached out via LinkedIn. Phone screen         │
│                          scheduled for May 14."                                  │
│  created_at          = 2026-05-07 10:00:00                                       │
│  updated_at          = 2026-05-09 09:45:00                                       │
└──────────────────────────────────────────────────────────────────────────────────┘
(linked to resume1 via resume_id = 101, and to user1 via user_id = 42)
```

---

✅ Section 3.4 complete. Type 'next' for the next section.

---

## 3.5 Class Diagram

The class diagram below shows all major service classes in NextGenCV, their attributes, methods, and relationships (composition, dependency, and inheritance). Classes are grouped by layer.

```
╔══════════════════════════════════════════════════════════════════════════════════════════╗
║                          NextGenCV — Service Layer Class Diagram                         ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝

 ┌─────────────────────────────────────────────────────────────────────────────────────┐
 │                           ANALYSIS LAYER                                            │
 └─────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│         <<service>>                      │
│         KeywordExtractorService          │
├──────────────────────────────────────────┤
│ - _nlp : spacy.Language  (singleton)     │
│ - STOP_WORDS : Set[str]                  │
├──────────────────────────────────────────┤
│ + extract_keywords(text, min_length)     │
│   : Set[str]                             │
│ + calculate_keyword_frequency(text)      │
│   : Dict[str, int]                       │
│ + weight_keywords_by_importance(         │
│     keywords, context)                   │
│   : Dict[str, float]                     │
│ - _get_nlp() : spacy.Language            │
└──────────────────────────────────────────┘
                    ▲
                    │ uses
                    │
┌──────────────────────────────────────────┐
│         <<service>>                      │
│         ActionVerbAnalyzerService        │
├──────────────────────────────────────────┤
│ + STRONG_ACTION_VERBS : Set[str]         │
│ + WEAK_VERBS : Set[str]                  │
├──────────────────────────────────────────┤
│ + analyze_action_verbs(text) : Dict      │
│   → {strong_verbs, weak_verbs,           │
│      total_verbs, strong_count,          │
│      weak_count}                         │
│ + calculate_action_verb_score(text)      │
│   : float                                │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│         <<service>>                      │
│         QuantificationDetectorService    │
├──────────────────────────────────────────┤
│ + PATTERNS : Dict[str, str]              │
│   (percentage, dollar, number,           │
│    range, multiplier, time)              │
├──────────────────────────────────────────┤
│ + detect_quantifications(text) : List    │
│ + has_quantification(text) : bool        │
│ + calculate_quantification_score(text)   │
│   : float                                │
│ + get_quantification_summary(text) : Dict│
└──────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────┐
│         <<service>>                                                                   │
│         ScoringEngineService                                                          │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ + WEIGHTS : Dict[str, float]                                                          │
│   {keyword_match: 0.30, skill_relevance: 0.20, section_completeness: 0.15,           │
│    experience_impact: 0.15, quantification: 0.10, action_verb: 0.10}                 │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ + calculate_ats_score(resume, job_description) : Dict                                 │
│ + calculate_keyword_match_score(resume_text, job_description) : float                │
│ + calculate_skill_relevance_score(resume, job_description) : float                   │
│ + calculate_section_completeness_score(resume) : float                               │
│ + calculate_experience_impact_score(resume) : float                                  │
│ + calculate_quantification_score(resume) : float                                     │
│ + calculate_action_verb_score(resume) : float                                        │
│ - _get_resume_text(resume) : str                                                      │
│ - _get_experience_text(resume) : str                                                  │
│ - _identify_missing_quantifications(resume) : List                                   │
└──────────────────────────────────────────────────────────────────────────────────────┘
         ▲
         │ inherits
         │
┌──────────────────────────────────────────┐
│         <<service>>                      │
│         ATSAnalyzerService               │
│         (extends ScoringEngineService)   │
├──────────────────────────────────────────┤
│ + analyze_resume(resume_id,              │
│     job_description) : Dict              │
│   → {score, matched_keywords,            │
│      missing_keywords, suggestions}      │
└──────────────────────────────────────────┘

  ScoringEngineService ──────────────────────────────────────────────────────────────────
       │ uses                    │ uses                          │ uses
       ▼                         ▼                               ▼
  KeywordExtractorService   ActionVerbAnalyzerService   QuantificationDetectorService


┌──────────────────────────────────────────────────────────────────────────────────────┐
│         <<service>>                                                                   │
│         ATSSystemSimulator                                                            │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ + SYSTEMS : Dict  {taleo, workday, greenhouse, lever, icims}                         │
│   each entry: {name, market_share, used_by, quirks[]}                                │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ + simulate_all(resume, job_description) : Dict                                        │
│   → {systems, best_system, worst_system,                                             │
│      overall_ats_readiness, critical_issues}                                         │
│ + simulate(resume, job_description, system_id) : Dict                                │
│   → {system_id, system_name, score, issues,                                          │
│      warnings, passed_checks, keyword_score,                                         │
│      format_score, completeness_score, date_score}                                   │
│ - _get_weights(system_id) : Dict                                                      │
│ - _check_format(resume, system_id, ...) : float                                      │
│ - _check_keywords(resume, job_description, system_id, ...) : float                   │
│ - _check_completeness(resume, system_id, ...) : float                                │
│ - _check_dates(resume, system_id, ...) : float                                       │
└──────────────────────────────────────────────────────────────────────────────────────┘
         │ uses
         ▼
  ScoringEngineService, KeywordExtractorService

┌──────────────────────────────────────────────────────────────────────────────────────┐
│         <<service>>                                                                   │
│         BeatTheATSService                                                             │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ (module-level) THRESHOLDS : List[Tuple]                                               │
│   [(40,'Poor'), (60,'Fair'), (75,'Good'), (85,'Strong'), (95,'Excellent')]            │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ + get_battle_plan(resume, job_description) : Dict                                     │
│   → {current_score, next_threshold, next_label,                                      │
│      points_needed, keywords_to_add[],                                               │
│      keywords_needed_count, already_winning}                                         │
│ + simulate_score_after_keywords(resume,                                               │
│     job_description, added_keywords) : float                                         │
└──────────────────────────────────────────────────────────────────────────────────────┘
         │ uses
         ▼
  ScoringEngineService, KeywordExtractorService


 ┌─────────────────────────────────────────────────────────────────────────────────────┐
 │                           OPTIMISATION LAYER                                        │
 └─────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────┐
│         <<service>>                                                                   │
│         LLMService                                                                    │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ (module) MODEL : str = "gpt-4o-mini"                                                  │
│ (module) MAX_TOKENS_DEFAULT : int = 800                                               │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ + rewrite_bullet(bullet, job_description, role) : Dict                                │
│   → {original, rewritten, improvement_reason}                                        │
│ + rewrite_bullets_batch(bullets, job_description, role) : List                       │
│ + generate_cover_letter(resume, company, role, job_description) : Dict               │
│   → {content, word_count, tone}                                                      │
│ + generate_summary(wizard_data) : Dict                                                │
│   → {summary, word_count}                                                            │
│ + generate_interview_questions(resume, role, job_description, company) : Dict        │
│   → {questions[{question, category, talking_points, resume_evidence}]}               │
│ + analyse_rejection(resume, job_description, company, role) : Dict                   │
│   → {likely_reasons[], improvement_areas[], action_items[]}                          │
│ + analyse_skill_gap(resume, target_role, job_descriptions) : Dict                    │
│   → {missing_skills[], present_skills[], recommendations[]}                          │
│ + explain_ats_score(score_data, resume_title) : str                                  │
│ - _get_client() : openai.OpenAI                                                       │
│ - _chat(system, user, max_tokens, json_mode) : Optional[str]                         │
└──────────────────────────────────────────────────────────────────────────────────────┘
         ▲
         │ uses (dependency)
         │
┌──────────────────────────────────────────────────────────────────────────────────────┐
│         <<service>>                                                                   │
│         ResumeOptimizerService                                                        │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ (composes: LLMService, ScoringEngineService,                                          │
│  KeywordExtractorService, QuantificationDetectorService)                              │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ + optimize_resume(resume, job_description, options) : Dict                            │
│   → {original_score, optimized_score, improvement_delta,                             │
│      changes_summary, detailed_changes, optimized_data}                              │
│ - _optimize_bullet_points(resume, job_description) : List[Dict]                      │
│   → [{section, field, old_value, new_value, reason, type}]                           │
│ - _suggest_quantifications(resume) : List[Dict]                                      │
│ - _standardize_formatting(resume) : List[Dict]                                       │
│ - _generate_optimized_data(resume, detailed_changes) : Dict                          │
│ - _estimate_optimized_score(original_score, changes_summary) : float                 │
│ - _get_resume_text(resume) : str                                                      │
└──────────────────────────────────────────────────────────────────────────────────────┘


 ┌─────────────────────────────────────────────────────────────────────────────────────┐
 │                           RESUME MANAGEMENT LAYER                                   │
 └─────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────┐
│         <<service>>                                                                   │
│         ResumeService                                                                 │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ + create_resume(user, data) : Resume                                                  │
│   (creates Resume + PersonalInfo + Experience[]                                       │
│    + Education[] + Skill[] + Project[])                                               │
│ + get_user_resumes(user) : QuerySet[Resume]                                           │
│ + update_resume(resume_id, data) : Resume                                             │
│ + delete_resume(resume_id) : None                                                     │
│ + duplicate_resume(resume_id) : Resume                                                │
└──────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────┐
│         <<service>>                                                                   │
│         VersionService                                                                │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ + create_version(resume, modification_type,                                           │
│     ats_score, user_notes) : ResumeVersion                                           │
│ + get_version_history(resume) : List[ResumeVersion]                                  │
│ + compare_versions(version1, version2) : Dict                                         │
│   → {added[], removed[], modified[]}                                                 │
│ + restore_version(version) : Resume                                                   │
│ - _create_snapshot(resume) : Dict                                                     │
│ - _compare_dict(dict1, dict2, section) : List[Dict]                                  │
│ - _compare_list(list1, list2, section, key) : List[Dict]                             │
└──────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────┐
│         <<service>>                                                                   │
│         PDFExportService                                                              │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ + generate_pdf(resume_id, version_id) : Tuple[bytes, Resume]                         │
│ + render_resume_html(resume) : str                                                    │
│   (uses WeasyPrint; falls back to HTML on Windows)                                   │
└──────────────────────────────────────────────────────────────────────────────────────┘


 ┌─────────────────────────────────────────────────────────────────────────────────────┐
 │                           ANALYTICS LAYER                                           │
 └─────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────┐
│         <<service>>                                                                   │
│         AnalyticsService                                                              │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ + calculate_resume_health(resume) : float                                             │
│   (components: section completeness 40pts,                                           │
│    contact info 15pts, quantified achievements 20pts,                                │
│    action verbs 15pts, ATS-friendly format 10pts)                                    │
│ + get_score_trends(user, window_size) : Dict                                          │
│   → {scores[], timestamps[], moving_average[],                                       │
│      improvement_rate, trend}                                                        │
│ + get_top_missing_keywords(user, limit) : List[Tuple[str,int]]                       │
│ + generate_improvement_report(user) : Dict                                            │
│   → {total_resumes, average_health, total_optimizations,                             │
│      average_improvement, top_missing_keywords, recommendations[]}                   │
│ - _calculate_moving_average(scores, window_size) : List[float]                       │
│ - _generate_recommendations(...) : List[str]                                         │
└──────────────────────────────────────────────────────────────────────────────────────┘
         │ uses
         ▼
  ActionVerbAnalyzerService, QuantificationDetectorService


 ┌─────────────────────────────────────────────────────────────────────────────────────┐
 │                    RELATIONSHIPS SUMMARY                                            │
 └─────────────────────────────────────────────────────────────────────────────────────┘

  Legend:
  ──────►   uses / dependency (one class calls another)
  ══════►   composes (owns an instance of)
  ──────▷   inherits / extends

  ResumeOptimizerService  ══════►  LLMService
  ResumeOptimizerService  ──────►  ScoringEngineService
  ResumeOptimizerService  ──────►  KeywordExtractorService
  ResumeOptimizerService  ──────►  QuantificationDetectorService

  ScoringEngineService    ──────►  KeywordExtractorService
  ScoringEngineService    ──────►  ActionVerbAnalyzerService
  ScoringEngineService    ──────►  QuantificationDetectorService

  ATSAnalyzerService      ──────▷  ScoringEngineService  (inherits)

  ATSSystemSimulator      ──────►  ScoringEngineService
  ATSSystemSimulator      ──────►  KeywordExtractorService

  BeatTheATSService       ──────►  ScoringEngineService
  BeatTheATSService       ──────►  KeywordExtractorService

  AnalyticsService        ──────►  ActionVerbAnalyzerService
  AnalyticsService        ──────►  QuantificationDetectorService

  VersionService          ──────►  ResumeVersion  (model)
  PDFExportService        ──────►  WeasyPrint  (external lib)
  LLMService              ──────►  OpenAI API  (external service)
```

---

✅ Section 3.5 complete. Type 'next' for the next section.

---

## 3.6 Use Case Diagram

Three actors interact with NextGenCV: **Guest** (unauthenticated visitor), **Registered User** (authenticated), and **Admin** (Django superuser). Use cases are grouped by module. Include (`<<include>>`) and extend (`<<extend>>`) relationships are shown where relevant.

```
╔══════════════════════════════════════════════════════════════════════════════════════════════╗
║                          NextGenCV — Use Case Diagram                                        ║
╚══════════════════════════════════════════════════════════════════════════════════════════════╝

  ACTORS
  ──────
  [Guest]            Unauthenticated visitor
  [Registered User]  Logged-in account holder
  [Admin]            Django superuser / staff


┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  MODULE: Authentication                                                                      │
│                                                                                              │
│  [Guest] ──────────────────────────────► ( Register Account )                               │
│                                                  │                                           │
│                                          <<include>>                                         │
│                                                  ▼                                           │
│                                          ( Send Verification Email )                         │
│                                                                                              │
│  [Guest] ──────────────────────────────► ( Login )                                          │
│                                                  │                                           │
│                                          <<extend>>                                          │
│                                                  ▼                                           │
│                                          ( Two-Factor / Email Verify )                       │
│                                                                                              │
│  [Registered User] ────────────────────► ( Verify Email Address )                           │
│  [Registered User] ────────────────────► ( Resend Verification Email )                      │
│  [Registered User] ────────────────────► ( Logout )                                         │
│  [Registered User] ────────────────────► ( Reset Password )                                 │
│                                                  │                                           │
│                                          <<include>>                                         │
│                                                  ▼                                           │
│                                          ( Receive Reset Email )                             │
│                                                                                              │
│  [Registered User] ────────────────────► ( View Dashboard )                                 │
│  [Registered User] ────────────────────► ( Edit Profile )                                   │
│  [Registered User] ────────────────────► ( Change Settings )                                │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  MODULE: Resume Management                                                                   │
│                                                                                              │
│  [Registered User] ────────────────────► ( View Resume List )                               │
│  [Registered User] ────────────────────► ( Create Resume via Wizard )                       │
│                                                  │                                           │
│                                          <<include>>                                         │
│                                                  ▼                                           │
│                                          ( Step 1: Personal Info )                           │
│                                          ( Step 2: Experience )                              │
│                                          ( Step 3: Education )                               │
│                                          ( Step 4: Skills )                                  │
│                                          ( Step 5: Summary )                                 │
│                                                                                              │
│  [Registered User] ────────────────────► ( View Resume Detail )                             │
│  [Registered User] ────────────────────► ( Edit Resume )                                    │
│                                                  │                                           │
│                                          <<include>>                                         │
│                                                  ▼                                           │
│                                          ( Add / Edit / Delete Experience )                  │
│                                          ( Add / Edit / Delete Education )                   │
│                                          ( Add / Edit / Delete Skill )                       │
│                                          ( Add / Edit / Delete Project )                     │
│                                                                                              │
│  [Registered User] ────────────────────► ( Delete Resume )                                  │
│  [Registered User] ────────────────────► ( Duplicate Resume )                               │
│  [Registered User] ────────────────────► ( Export Resume as PDF )                           │
│                                                  │                                           │
│                                          <<extend>>                                          │
│                                                  ▼                                           │
│                                          ( Export Specific Version as PDF )                  │
│                                                                                              │
│  [Registered User] ────────────────────► ( Export Resume as DOCX )                          │
│  [Registered User] ────────────────────► ( Export Resume as Plain Text )                    │
│  [Registered User] ────────────────────► ( Upload PDF Resume )                              │
│                                                  │                                           │
│                                          <<include>>                                         │
│                                                  ▼                                           │
│                                          ( Review Parsed Data )                              │
│                                          ( Confirm Import to Resume )                        │
│                                                                                              │
│  [Registered User] ────────────────────► ( Share Resume via Public Link )                   │
│  [Guest]           ────────────────────► ( View Public Resume )                             │
│  [Registered User] ────────────────────► ( Customise Template )                             │
│                                                  │                                           │
│                                          <<include>>                                         │
│                                                  ▼                                           │
│                                          ( Select Colour Scheme )                            │
│                                          ( Select Font Family )                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  MODULE: ATS Analysis                                                                        │
│                                                                                              │
│  [Registered User] ────────────────────► ( Analyse Resume vs Job Description )              │
│                                                  │                                           │
│                                          <<include>>                                         │
│                                                  ▼                                           │
│                                          ( Extract Keywords via spaCy )                      │
│                                          ( Calculate 6-Factor Score )                        │
│                                          ( Generate Keyword Suggestions )                    │
│                                          ( Save Analysis to DB )                             │
│                                                                                              │
│  [Registered User] ────────────────────► ( Simulate ATS Systems )                           │
│                                                  │                                           │
│                                          <<include>>                                         │
│                                                  ▼                                           │
│                                          ( Simulate Taleo )                                  │
│                                          ( Simulate Workday )                                │
│                                          ( Simulate Greenhouse )                             │
│                                          ( Simulate Lever )                                  │
│                                          ( Simulate iCIMS )                                  │
│                                                                                              │
│  [Registered User] ────────────────────► ( Beat the ATS )                                   │
│                                                  │                                           │
│                                          <<include>>                                         │
│                                                  ▼                                           │
│                                          ( Get Battle Plan )                                 │
│                                          ( Simulate Score After Adding Keywords )            │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  MODULE: AI Optimisation (Fix My Resume)                                                     │
│                                                                                              │
│  [Registered User] ────────────────────► ( Start AI Optimisation )                          │
│                                                  │                                           │
│                                          <<include>>                                         │
│                                                  ▼                                           │
│                                          ( Rewrite Bullet Points via GPT-4o-mini )          │
│                                          ( Suggest Quantifications )                         │
│                                          ( Standardise Formatting )                          │
│                                          ( Calculate Improvement Delta )                     │
│                                                                                              │
│  [Registered User] ────────────────────► ( Preview Optimised Changes )                      │
│  [Registered User] ────────────────────► ( Accept All Changes )                             │
│  [Registered User] ────────────────────► ( Reject All Changes )                             │
│  [Registered User] ────────────────────► ( Accept / Reject Individual Changes )             │
│                                                  │                                           │
│                                          <<extend>>                                          │
│                                                  ▼                                           │
│                                          ( Save Optimisation History Record )                │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  MODULE: Version Control                                                                     │
│                                                                                              │
│  [Registered User] ────────────────────► ( View Version History )                           │
│  [Registered User] ────────────────────► ( View Version Detail / Snapshot )                 │
│  [Registered User] ────────────────────► ( Compare Two Versions )                           │
│  [Registered User] ────────────────────► ( Restore Previous Version )                       │
│                                                  │                                           │
│                                          <<include>>                                         │
│                                                  ▼                                           │
│                                          ( Create New Version Snapshot )                     │
│                                          ( Update Resume Current Version Number )            │
│                                                                                              │
│  [Registered User] ────────────────────► ( View Optimisation History )                      │
│  [Registered User] ────────────────────► ( View Optimisation Detail )                       │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  MODULE: Analytics                                                                           │
│                                                                                              │
│  [Registered User] ────────────────────► ( View Analytics Dashboard )                       │
│                                                  │                                           │
│                                          <<include>>                                         │
│                                                  ▼                                           │
│                                          ( Calculate Resume Health Scores )                  │
│                                          ( Display Score Trend Chart )                       │
│                                          ( Show Top Missing Keywords )                       │
│                                                                                              │
│  [Registered User] ────────────────────► ( View Score Trends )                              │
│                                                  │                                           │
│                                          <<include>>                                         │
│                                                  ▼                                           │
│                                          ( Calculate Moving Average )                        │
│                                                                                              │
│  [Registered User] ────────────────────► ( View Improvement Report )                        │
│                                                  │                                           │
│                                          <<include>>                                         │
│                                                  ▼                                           │
│                                          ( Generate Personalised Recommendations )           │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  MODULE: Job Tracker                                                                         │
│                                                                                              │
│  [Registered User] ────────────────────► ( View Applications List )                         │
│  [Registered User] ────────────────────► ( Add Job Application )                            │
│                                                  │                                           │
│                                          <<extend>>                                          │
│                                                  ▼                                           │
│                                          ( Scrape Job from URL )                             │
│                                                                                              │
│  [Registered User] ────────────────────► ( View Application Detail )                        │
│  [Registered User] ────────────────────► ( Edit Application )                               │
│  [Registered User] ────────────────────► ( Delete Application )                             │
│  [Registered User] ────────────────────► ( Update Application Status )                      │
│                                                  │                                           │
│                                          (status: saved → applied → interview                │
│                                           → offer / rejected / withdrawn)                   │
│                                                                                              │
│  [Registered User] ────────────────────► ( View Outcome Dashboard )                         │
│  [Registered User] ────────────────────► ( View Rejection Analysis )                        │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  MODULE: AI Tools (GPT-4o-mini powered)                                                      │
│                                                                                              │
│  [Registered User] ────────────────────► ( Generate Cover Letter )                          │
│                                                  │                                           │
│                                          <<include>>                                         │
│                                                  ▼                                           │
│                                          ( Call LLMService.generate_cover_letter() )        │
│                                          ( Link to Job Application )                         │
│                                                                                              │
│  [Registered User] ────────────────────► ( Generate Interview Prep Questions )              │
│                                                  │                                           │
│                                          <<include>>                                         │
│                                                  ▼                                           │
│                                          ( Call LLMService.generate_interview_questions() ) │
│                                          ( Save InterviewPrepSession )                       │
│                                                                                              │
│  [Registered User] ────────────────────► ( Run Skill Gap Analysis )                         │
│                                                  │                                           │
│                                          <<include>>                                         │
│                                                  ▼                                           │
│                                          ( Call LLMService.analyse_skill_gap() )            │
│                                          ( Save SkillGapAnalysis )                           │
│                                                                                              │
│  [Registered User] ────────────────────► ( Generate Follow-up Email )                       │
│  [Registered User] ────────────────────► ( Analyse Rejection )                              │
│  [Registered User] ────────────────────► ( View Salary Intelligence )                       │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  MODULE: Template Gallery                                                                    │
│                                                                                              │
│  [Registered User] ────────────────────► ( Browse Template Gallery )                        │
│  [Registered User] ────────────────────► ( Preview Template )                               │
│  [Registered User] ────────────────────► ( Select Template for Resume )                     │
│  [Registered User] ────────────────────► ( Customise Template )                             │
│                                                  │                                           │
│                                          <<include>>                                         │
│                                                  ▼                                           │
│                                          ( Preview Customisation Live )                      │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  MODULE: REST API (api/v1/)                                                                  │
│                                                                                              │
│  [Registered User] ────────────────────► ( Obtain JWT Token )                               │
│  [Registered User] ────────────────────► ( Refresh JWT Token )                              │
│  [Registered User] ────────────────────► ( Get Current User Profile )                       │
│  [Registered User] ────────────────────► ( CRUD Resumes via API )                           │
│  [Registered User] ────────────────────► ( CRUD Job Applications via API )                  │
│  [Registered User] ────────────────────► ( Poll Async Task Status )                         │
│  [Registered User] ────────────────────► ( Get Outcome Analytics )                          │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  MODULE: Admin Panel (/admin/)                                                               │
│                                                                                              │
│  [Admin] ──────────────────────────────► ( Manage Users )                                   │
│  [Admin] ──────────────────────────────► ( Manage Resumes )                                 │
│  [Admin] ──────────────────────────────► ( Manage Resume Templates )                        │
│  [Admin] ──────────────────────────────► ( View Activity Logs )                             │
│  [Admin] ──────────────────────────────► ( Manage Job Applications )                        │
│  [Admin] ──────────────────────────────► ( View Analysis Records )                          │
│  [Admin] ──────────────────────────────► ( Manage Optimisation History )                    │
└─────────────────────────────────────────────────────────────────────────────────────────────┘


  ACTOR SUMMARY
  ─────────────
  ┌──────────────────┬──────────────────────────────────────────────────────────────────┐
  │ Actor            │ Accessible Modules                                               │
  ├──────────────────┼──────────────────────────────────────────────────────────────────┤
  │ Guest            │ Register, Login, Password Reset, View Public Resume              │
  ├──────────────────┼──────────────────────────────────────────────────────────────────┤
  │ Registered User  │ All modules: Auth, Resume Mgmt, ATS Analysis, AI Optimisation,  │
  │                  │ Version Control, Analytics, Job Tracker, AI Tools,               │
  │                  │ Template Gallery, REST API                                       │
  ├──────────────────┼──────────────────────────────────────────────────────────────────┤
  │ Admin            │ All Registered User capabilities + Django Admin panel            │
  └──────────────────┴──────────────────────────────────────────────────────────────────┘
```

---

✅ Section 3.6 complete. Type 'next' for the next section.

---

## 3.7 Website Map Diagram

The site map below shows every URL route in NextGenCV, organised hierarchically by module. Routes are grouped under their URL prefix as defined in `config/urls.py`. Authentication-required routes are marked `[auth]`. Admin-only routes are marked `[admin]`.

```
╔══════════════════════════════════════════════════════════════════════════════════════════╗
║                          NextGenCV — Full Website Map                                    ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝

/  (Landing Page)
│
├── robots.txt                          Static robots file
├── help/                               Documentation / Help Centre
│
├── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──
│
├── auth/                               ◄── Authentication Module
│   ├── register/                       Register new account
│   ├── verify-email/<token>/           Verify email address (one-time link)
│   ├── resend-verification/            Resend verification email  [auth]
│   ├── login/                          Login page
│   ├── logout/                         Logout (POST)
│   ├── dashboard/                      User dashboard             [auth]
│   ├── profile/                        View / edit profile        [auth]
│   ├── settings/                       Account settings           [auth]
│   ├── password-reset/                 Request password reset
│   ├── password-reset/done/            Password reset email sent
│   ├── password-reset/<uidb64>/<token>/  Set new password
│   └── password-reset/complete/        Password reset complete
│
├── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──
│
├── resumes/                            ◄── Resume Management Module
│   ├── (list)                          Resume list / dashboard    [auth]
│   ├── create/                         Multi-step creation wizard [auth]
│   │   ├── Step 1 — Personal Info
│   │   ├── Step 2 — Experience
│   │   ├── Step 3 — Education
│   │   ├── Step 4 — Skills
│   │   └── Step 5 — Summary & Finish
│   ├── generate-summary/               AI summary generation (AJAX) [auth]
│   ├── linkedin-import/                Import from LinkedIn        [auth]
│   ├── batch-export/                   Batch export multiple PDFs  [auth]
│   ├── batch-analysis/                 Batch ATS analysis          [auth]
│   ├── upload/                         Upload existing PDF resume  [auth]
│   ├── upload/<id>/review/             Review parsed PDF data      [auth]
│   ├── upload/<id>/confirm/            Confirm import to resume    [auth]
│   ├── upload/<id>/file/               Serve uploaded file (secure)[auth]
│   ├── upload/<id>/download/           Download uploaded file      [auth]
│   ├── upload-async/                   Async PDF upload (Celery)   [auth]
│   ├── task/<task_id>/progress/        SSE task progress stream    [auth]
│   ├── public/<token>/                 Public resume view (no auth)
│   │
│   └── <id>/                           ◄── Per-Resume Routes
│       ├── (detail)                    Resume detail / preview     [auth]
│       ├── edit/                       Edit resume                 [auth]
│       ├── delete/                     Delete resume (confirm)     [auth]
│       ├── duplicate/                  Duplicate resume            [auth]
│       ├── share/                      Generate / manage share link[auth]
│       │
│       ├── export/                     Export as PDF               [auth]
│       ├── export/docx/                Export as DOCX              [auth]
│       ├── export/text/                Export as plain text        [auth]
│       │
│       ├── ats-simulate/               ATS system simulation       [auth]
│       ├── rejection-analysis/         AI rejection analysis       [auth]
│       ├── keywords/                   Keyword suggestions         [auth]
│       ├── keywords/add/               Add suggested keyword       [auth]
│       ├── customize/                  Template customisation      [auth]
│       │
│       ├── fix/                        ◄── AI Optimisation (Fix My Resume)
│       │   ├── (start)                 Start optimisation          [auth]
│       │   ├── preview/                Preview proposed changes    [auth]
│       │   ├── accept/                 Accept all / selected changes[auth]
│       │   └── reject/                 Reject all / selected changes[auth]
│       ├── fix-async/                  Async optimisation (Celery) [auth]
│       │
│       ├── versions/                   ◄── Version Control
│       │   ├── (list)                  Version history list        [auth]
│       │   ├── compare/                Compare two versions        [auth]
│       │   └── <version_id>/           Version detail / snapshot   [auth]
│       │       └── restore/            Restore this version        [auth]
│       │
│       ├── optimizations/              ◄── Optimisation History
│       │   ├── (list)                  Optimisation history list   [auth]
│       │   └── <optimization_id>/      Optimisation detail         [auth]
│       │
│       ├── experience/                 ◄── Experience CRUD
│       │   ├── add/                    Add experience entry        [auth]
│       │   └── <exp_id>/
│       │       ├── edit/               Edit experience entry       [auth]
│       │       └── delete/             Delete experience entry     [auth]
│       │
│       ├── education/                  ◄── Education CRUD
│       │   ├── add/                    Add education entry         [auth]
│       │   └── <edu_id>/
│       │       ├── edit/               Edit education entry        [auth]
│       │       └── delete/             Delete education entry      [auth]
│       │
│       ├── skill/                      ◄── Skill CRUD
│       │   ├── add/                    Add skill                   [auth]
│       │   └── <skill_id>/
│       │       ├── edit/               Edit skill                  [auth]
│       │       └── delete/             Delete skill                [auth]
│       │
│       └── project/                    ◄── Project CRUD
│           ├── add/                    Add project                 [auth]
│           └── <project_id>/
│               ├── edit/               Edit project                [auth]
│               └── delete/             Delete project              [auth]
│
├── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──
│
├── analyzer/                           ◄── ATS Analyser Module
│   ├── <resume_id>/analyze/            Run ATS analysis            [auth]
│   └── <resume_id>/beat-the-ats/       Beat the ATS battle plan    [auth]
│
├── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──
│
├── analytics/                          ◄── Analytics Module
│   ├── dashboard/                      Analytics dashboard         [auth]
│   ├── trends/                         Score trends chart          [auth]
│   └── improvement-report/             Improvement report          [auth]
│
├── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──
│
├── templates/                          ◄── Template Gallery Module
│   ├── gallery/                        Browse all templates        [auth]
│   ├── preview/<template_id>/          Preview a template          [auth]
│   ├── select/<template_id>/<resume_id>/  Apply template to resume [auth]
│   ├── customize/<resume_id>/          Customise template          [auth]
│   └── customize/<resume_id>/preview/  Live customisation preview  [auth]
│
├── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──
│
├── tracker/                            ◄── Job Tracker Module
│   ├── (list)                          Applications list           [auth]
│   ├── create/                         Add new application         [auth]
│   ├── scrape/                         Scrape job from URL         [auth]
│   ├── outcomes/                       Outcome analytics dashboard [auth]
│   ├── skill-gap/                      Skill gap analysis          [auth]
│   ├── salary/                         Salary intelligence         [auth]
│   ├── rejections/                     Rejection analysis          [auth]
│   │
│   └── <id>/                           ◄── Per-Application Routes
│       ├── (detail)                    Application detail          [auth]
│       ├── edit/                       Edit application            [auth]
│       ├── delete/                     Delete application          [auth]
│       ├── cover-letter/               Generate cover letter (AI)  [auth]
│       ├── interview-prep/             Generate interview questions (AI) [auth]
│       └── followup/                   Generate follow-up email (AI) [auth]
│
├── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──
│
├── api/v1/                             ◄── REST API (DRF + JWT)
│   ├── auth/
│   │   ├── token/                      POST — obtain JWT token pair
│   │   ├── token/refresh/              POST — refresh access token
│   │   └── token/verify/               POST — verify token validity
│   │
│   ├── me/                             GET  — current user profile [auth]
│   ├── tasks/<task_id>/                GET  — async task status    [auth]
│   ├── outcomes/                       GET  — outcome analytics    [auth]
│   │
│   ├── resumes/                        ◄── Resume ViewSet (CRUD)
│   │   ├── (list)                      GET  — list resumes         [auth]
│   │   ├── (create)                    POST — create resume        [auth]
│   │   └── <id>/
│   │       ├── (retrieve)              GET  — resume detail        [auth]
│   │       ├── (update)                PUT/PATCH — update resume   [auth]
│   │       └── (destroy)               DELETE — delete resume      [auth]
│   │
│   └── applications/                   ◄── JobApplication ViewSet (CRUD)
│       ├── (list)                      GET  — list applications    [auth]
│       ├── (create)                    POST — create application   [auth]
│       └── <id>/
│           ├── (retrieve)              GET  — application detail   [auth]
│           ├── (update)                PUT/PATCH — update          [auth]
│           └── (destroy)               DELETE — delete             [auth]
│
├── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──
│
├── admin/                              ◄── Django Admin Panel     [admin]
│   ├── auth/user/                      Manage users
│   ├── resumes/resume/                 Manage resumes
│   ├── resumes/resumeanalysis/         View analysis records
│   ├── resumes/optimizationhistory/    View optimisation history
│   ├── resumes/resumeversion/          View version snapshots
│   ├── resumes/uploadedresume/         View uploaded PDFs
│   ├── templates_mgmt/resumetemplate/  Manage resume templates
│   ├── tracker/jobapplication/         Manage job applications
│   ├── tracker/coverletter/            View cover letters
│   ├── authentication/activitylog/     View activity logs
│   └── authentication/savedjobdescription/  View saved JDs
│
└── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──


  LEGEND
  ──────
  [auth]   Route requires authenticated session (login_required)
  [admin]  Route requires is_staff = True or is_superuser = True
  (list)   URL is the prefix itself with no additional segment
  <id>     Integer primary key path parameter
  <token>  String token path parameter
  SSE      Server-Sent Events (real-time streaming)
  AJAX     Endpoint called via XMLHttpRequest / fetch
  CRUD     Create, Read, Update, Delete operations
```

---

# Chapter 5: Conclusion

---

## 5.1 Conclusion

NextGenCV was conceived to solve a problem that is both technically specific and practically significant: the majority of qualified job applicants are eliminated before a human recruiter ever reads their resume, not because of a lack of skill or experience, but because of how automated screening systems process documents. This project set out to build a system that makes the mechanics of that screening process transparent, measurable, and improvable for every job seeker.

The system that has been designed and implemented achieves that goal across five interconnected dimensions.

### Resume Management

The multi-step creation wizard guides users through building a fully structured resume — personal information, work experience, education, skills, projects, and certifications — with a live preview that updates in real time. The normalized relational database schema (20 tables across 7 Django apps) stores every section independently, enabling structured analysis, targeted editing, and granular version control. Users can maintain multiple resumes simultaneously, duplicate them for different target roles, export them as PDF or DOCX, and share them via a public link. Every change is automatically snapshotted, giving users a complete version history they can compare and restore at any point.

### ATS Analysis and Scoring

The core analytical engine implements a six-factor weighted scoring model that evaluates a resume against a specific job description across keyword match (30%), skill relevance (20%), section completeness (15%), experience impact (15%), quantification (10%), and action verb quality (10%). The spaCy NLP pipeline extracts keywords from both the resume and the job description using part-of-speech tagging and noun-chunk extraction, enabling both exact and semantic matching. The ATS System Simulator extends this by modelling the specific parsing behaviours and scoring weights of five major platforms — Taleo, Workday, Greenhouse, Lever, and iCIMS — giving users platform-specific scores and actionable warnings. The Beat the ATS feature calculates the minimum set of keywords needed to cross the next score threshold, turning an abstract score into a concrete, gamified action plan.

### AI-Powered Optimisation

The Fix My Resume pipeline integrates GPT-4o-mini with four rule-based services — bullet point rewriting, keyword injection, quantification suggestion, and formatting standardisation — to produce a comprehensive set of proposed changes. Critically, the system presents every change in a side-by-side comparison and requires the user to accept or reject each modification individually. This design keeps the user in control while automating the most time-consuming parts of resume improvement. The optimisation history records every session with before/after scores and a full change log, creating an auditable trail of improvements.

### Analytics and Progress Tracking

The analytics module aggregates data across all of a user's resumes and analysis sessions to surface trends that would otherwise be invisible. Resume health scores, ATS score trajectories with moving averages, section completeness breakdowns, and top missing keywords across all job descriptions analysed are presented in a dashboard built with Chart.js. The improvement report generates personalised recommendations ranked by impact. Caching (5–10 minute TTL) ensures that expensive aggregation queries do not degrade performance as a user's data grows.

### Job Tracker and AI Tools

The job application tracker closes the feedback loop between resume quality and application outcomes. By recording the ATS score at the time of application and tracking the application through its full lifecycle (Saved → Applied → Interview → Offer → Rejected/Withdrawn), the system enables outcome analytics — users can see whether higher ATS scores correlate with more interview callbacks. The AI tools module (cover letter generation, interview preparation questions, skill gap analysis, rejection analysis, follow-up email generation, salary intelligence) consolidates the entire job search workflow into a single platform, eliminating the need to switch between multiple disconnected tools.

### Technical Achievement

From a software engineering perspective, the project demonstrates a clean layered architecture: a presentation layer (Django templates + DRF REST API), an application layer (20+ service classes with clear single responsibilities), and a data layer (Django ORM over SQLite/PostgreSQL). The service layer pattern ensures that business logic is fully decoupled from views and models, making every service independently testable and reusable. The asynchronous task architecture (Celery + Redis) handles long-running AI operations without blocking web requests. The system includes a complete REST API with JWT authentication, property-based testing with Hypothesis, a custom SCSS design system, and comprehensive security controls including CSRF protection, ownership validation on every resource, HTML sanitisation, file upload validation, and rate limiting on AI endpoints.

### Summary

NextGenCV successfully delivers on its stated objectives. It brings transparency to a process that has historically been opaque, automation to tasks that have historically been manual, and data to decisions that have historically been made by guesswork. A job seeker using NextGenCV knows their exact ATS score against any job description, knows precisely which keywords are missing and where to add them, can simulate how their resume performs across the five most widely used ATS platforms, can have their bullet points rewritten and keywords injected by AI in seconds, and can track every application with its associated resume version and score. The system is fully functional, architecturally sound, and built on a foundation that is ready to scale.

---

## 5.2 Limitations

Despite the breadth of functionality delivered, NextGenCV has a number of limitations that are important to acknowledge honestly. These fall into four categories: technical constraints, scope boundaries, AI dependency risks, and usability considerations.

---

### 1. Database and Scalability Constraints

**SQLite in Development**
The system uses SQLite as its default database. SQLite is a file-based, single-writer database that is well-suited for development and low-traffic deployments but is not appropriate for concurrent multi-user production environments. Under simultaneous write operations — for example, multiple users submitting AI optimisation requests at the same time — SQLite will serialize writes and can produce locking errors. Migration to PostgreSQL is supported by the architecture but requires explicit configuration and is not the out-of-the-box default.

**No Horizontal Scaling**
The current architecture is a single-process monolith. While Celery allows async task offloading, the Django application itself runs as a single instance. There is no built-in support for load balancing across multiple application servers, shared session storage, or distributed caching. Scaling beyond a single server requires additional infrastructure work (shared Redis session store, external media storage such as S3, a load balancer).

**In-Memory Caching**
The caching layer uses Django's `LocMemCache` by default — a per-process, in-memory cache that is lost on every server restart and is not shared between processes. In a multi-worker deployment, each worker maintains its own cache, leading to redundant computation and inconsistent cache hits. Production deployments require Redis-backed caching to realise the full performance benefit.

---

### 2. ATS Simulation Accuracy

**Simulated, Not Real**
The ATS System Simulator models the behaviour of Taleo, Workday, Greenhouse, Lever, and iCIMS based on publicly documented parsing quirks and general knowledge of how these systems work. It does not connect to any of these platforms directly. The scores and warnings it produces are approximations — useful for guidance but not guaranteed to match what a real ATS would produce for a given resume. ATS vendors update their algorithms regularly and do not publish their exact scoring logic.

**Keyword Matching is Lexical, Not Fully Semantic**
The keyword extraction pipeline uses spaCy's `en_core_web_sm` model — a small, general-purpose English model. While it performs noun-chunk extraction and lemmatisation, it does not use word embeddings or transformer-based semantic similarity. This means that "built REST services" and "REST API development" may not be recognised as semantically equivalent, even though a human recruiter would consider them the same skill. The system can miss matches that a more sophisticated NLP model would catch.

**English Only**
The spaCy pipeline is configured for English (`en_core_web_sm`). Resumes or job descriptions in other languages will produce poor keyword extraction results. There is no language detection or multi-language support.

---

### 3. AI Feature Limitations

**OpenAI API Dependency**
All AI-powered features — bullet point rewriting, cover letter generation, interview preparation, skill gap analysis, rejection analysis, and salary intelligence — depend on the OpenAI API. If the API key is absent, the API is unavailable, or the account has exhausted its quota, these features fall back to rule-based alternatives that are significantly less capable. The quality of AI output is also non-deterministic: the same prompt can produce different results on different calls, and GPT-4o-mini occasionally produces outputs that are generic, factually imprecise, or stylistically inconsistent with the user's voice.

**No Fine-Tuning or Domain Adaptation**
The LLM is used via zero-shot and few-shot prompting with no fine-tuning on resume-specific data. A model fine-tuned on a large corpus of high-quality resumes and successful job applications would likely produce more consistently strong rewrites. The current approach is limited by the general-purpose nature of GPT-4o-mini.

**Token and Cost Constraints**
The system caps AI responses at 1,500 tokens and limits AI endpoints to 20 requests per hour per user. For users with long resumes or complex job descriptions, this can result in truncated outputs. The per-token cost of the OpenAI API also means that heavy usage by many users would incur significant operating costs that are not currently managed by a billing or subscription system.

**No Feedback Loop for AI Quality**
There is no mechanism for users to rate the quality of AI-generated content (e.g., thumbs up/down on a rewritten bullet point). Without this feedback, there is no data to identify systematic weaknesses in the prompts or to improve output quality over time.

---

### 4. PDF Parsing Limitations

**Parsing Confidence Varies Significantly**
The `PDFParserService` uses pdfplumber to extract text from uploaded PDF resumes. Parsing quality depends heavily on how the PDF was created. PDFs generated from Word or Google Docs with selectable text parse well. Scanned PDFs (image-based), PDFs with complex multi-column layouts, PDFs with embedded tables, and PDFs created by design tools (Canva, Adobe InDesign) often produce garbled or incomplete text extraction. The system reports a parsing confidence score but cannot guarantee accurate section detection for poorly structured PDFs.

**No OCR Support**
The system does not include Optical Character Recognition (OCR). Scanned PDF resumes — common for older documents or documents received as image scans — cannot be parsed at all. The extracted text will be empty or near-empty, and the import will fail silently or produce an unusable result.

**Section Detection is Heuristic**
`SectionParserService` uses pattern matching and NER to identify resume sections (Experience, Education, Skills, etc.) from raw extracted text. This works reliably for standard resume formats but fails for unconventional layouts, non-standard section headers, or resumes that do not follow a chronological structure. Incorrectly detected sections require manual correction after import.

---

### 5. Platform and Deployment Constraints

**WeasyPrint on Windows**
WeasyPrint requires GTK and Pango system libraries for PDF rendering. These are not available on Windows by default. On Windows development environments, PDF export falls back to returning an HTML file that the user must print to PDF manually via the browser. This is a known limitation documented in the codebase but represents a degraded experience for Windows users and developers.

**No Production Deployment Configuration**
The repository ships with a development configuration (`DEBUG=True`, SQLite, console email backend, in-memory Celery). There is no included production deployment configuration — no Dockerfile, no `docker-compose.yml`, no Nginx configuration, no Gunicorn setup, and no CI/CD pipeline. Deploying to production requires significant manual configuration work.

**Media File Storage**
Uploaded PDF files are stored on the local filesystem under `MEDIA_ROOT`. In a multi-server or containerised deployment, this means uploaded files are not accessible across instances. Production deployments require an external object storage solution (e.g., AWS S3, Cloudflare R2) which is not currently integrated.

---

### 6. Functional Scope Limitations

**No Real Job Board Integration**
The system has a job scraping endpoint (`/tracker/scrape/`) but does not integrate with live job boards (Indeed, LinkedIn, Glassdoor). Users must manually copy and paste job descriptions. There is no automated job discovery, saved search, or job recommendation feature.

**No Payment or Subscription System**
The pricing UI exists in the frontend but there is no payment gateway integration (Stripe, PayPal). All features are available to all registered users with no access control based on subscription tier. This means the system cannot be monetised in its current state without additional development.

**No Mobile Application**
The web interface is responsive and usable on mobile browsers, but there is no native iOS or Android application. Features that benefit from mobile-native capabilities — such as camera-based document scanning, push notifications for application status changes, or offline access — are not available.

**No Real-Time Collaboration**
Resumes cannot be shared for collaborative editing. There is no multi-user editing, commenting, or review workflow. A user cannot invite a career coach or mentor to review and annotate their resume within the platform.

**Activity Log Capped at 200 Entries**
The `ActivityLog` model automatically deletes entries beyond the 200 most recent per user. For power users with high activity, this means older activity history is permanently lost and cannot be recovered.

---

### Summary of Limitations

| Category | Limitation | Severity |
|---|---|---|
| Database | SQLite not suitable for concurrent production use | Medium |
| Scalability | Single-process monolith, no horizontal scaling | Medium |
| ATS Simulation | Approximated, not connected to real ATS platforms | Medium |
| NLP | Small spaCy model, no semantic similarity | Medium |
| Language | English only | Medium |
| AI | OpenAI API dependency, non-deterministic output | Medium |
| AI | No fine-tuning, generic prompts | Low |
| PDF Parsing | Fails on scanned / complex layout PDFs | High |
| PDF Parsing | No OCR support | High |
| PDF Export | WeasyPrint unavailable on Windows | Medium |
| Deployment | No production config, no Docker, no CI/CD | High |
| Media Storage | Local filesystem only, not cloud-ready | Medium |
| Scope | No job board integration | Low |
| Scope | No payment system | Low |
| Scope | No mobile application | Low |
| Scope | No collaborative editing | Low |

---

## 5.3 Future Enhancements

The limitations identified in Section 5.2 define a clear roadmap for future development. The enhancements below are organised by priority and grouped into short-term improvements (addressable with moderate effort), medium-term features (requiring significant new development), and long-term strategic directions (requiring architectural changes or external integrations).

---

### Short-Term Enhancements

#### 1. Production-Ready Deployment Configuration

The most immediately impactful improvement is providing a complete production deployment stack. This would include:

- A `Dockerfile` and `docker-compose.yml` that bundles the Django application, Celery worker, Redis broker, and Nginx reverse proxy into a single orchestrated environment
- A `settings/production.py` configuration file with PostgreSQL, Redis caching, S3 media storage, SMTP email, and `ManifestStaticFilesStorage`
- A GitHub Actions CI/CD pipeline that runs tests, lints code, builds the Docker image, and deploys to a cloud provider on every push to `main`
- Environment-specific secret management using a tool such as AWS Secrets Manager or HashiCorp Vault

This enhancement directly addresses the highest-severity limitation identified in Section 5.2 and is a prerequisite for any real-world deployment.

#### 2. PostgreSQL Migration and Connection Pooling

Replacing SQLite with PostgreSQL as the default database would unlock concurrent write support, full-text search (`django.contrib.postgres`), JSONB indexing for the `snapshot_data` and `suggestions` fields, and proper connection pooling via PgBouncer. The Django ORM abstracts most of the migration — the primary work is updating `DATABASES` settings, running `migrate`, and adding PostgreSQL-specific indexes where beneficial.

#### 3. OCR Support for Scanned PDFs

Integrating Tesseract OCR (via the `pytesseract` Python wrapper) into the `PDFParserService` would allow the system to extract text from image-based PDFs. The workflow would be: attempt pdfplumber extraction → if confidence is below a threshold → convert PDF pages to images using `pdf2image` → run Tesseract OCR → return extracted text. This would significantly expand the range of PDF resumes the system can import successfully.

#### 4. Semantic Keyword Matching

Replacing the current lexical keyword matching with a semantic similarity model would reduce false negatives where equivalent skills are expressed with different terminology. The most practical approach is to replace `en_core_web_sm` with `en_core_web_md` or `en_core_web_lg` (which include word vectors) and use spaCy's built-in `.similarity()` method for token comparison. A more powerful alternative is to use a sentence-transformer model (e.g., `all-MiniLM-L6-v2` from the `sentence-transformers` library) to embed both resume text and job description text and compute cosine similarity. This would allow "built REST services" and "REST API development" to be recognised as semantically equivalent.

#### 5. User Feedback on AI Output

Adding a simple thumbs-up / thumbs-down rating on every AI-generated output (rewritten bullet points, cover letters, interview questions) would create a feedback dataset. This data could be used to identify systematic weaknesses in prompts, fine-tune future models, and filter out low-quality outputs before they are shown to users. The implementation requires only a new `AIFeedback` model and a lightweight AJAX endpoint.

---

### Medium-Term Enhancements

#### 6. Live Job Board Integration

Integrating with job board APIs would eliminate the need for users to manually copy and paste job descriptions. Planned integrations:

- **LinkedIn Jobs API** — search and import job postings directly into the tracker
- **Indeed Publisher API** — job search by role, location, and salary range
- **Adzuna API** — salary data and job market trends by region

Each integration would allow users to click "Analyse against this job" directly from a job listing, automatically populating the job description field and triggering an ATS analysis. A browser extension (Chrome/Firefox) could provide the same capability on any job board without a formal API integration.

#### 7. Subscription and Billing System

Implementing a tiered subscription model using Stripe would allow the platform to be monetised. A proposed tier structure:

| Tier | Features | Price |
|---|---|---|
| Free | 2 resumes, 5 analyses/month, basic export | £0/month |
| Pro | Unlimited resumes, unlimited analyses, AI features, all exports | £9/month |
| Team | Pro + shared workspace, collaborative editing, admin dashboard | £25/month |

The implementation requires Stripe Checkout integration, a `Subscription` model linked to `auth_user`, and middleware that checks the user's tier before allowing access to premium features. Django's permission system can enforce feature gating cleanly.

#### 8. Collaborative Resume Review

A review workflow would allow users to share a resume with a specific person (career coach, mentor, recruiter) for annotated feedback within the platform. The feature would include:

- A `ReviewInvitation` model with a time-limited token
- An inline annotation interface where reviewers can highlight text and leave comments
- Email notifications when comments are added or resolved
- A `ReviewSession` history showing all feedback received on each version

This transforms NextGenCV from a solo tool into a collaborative career development platform.

#### 9. Multi-Language Support

Extending the NLP pipeline to support languages beyond English would open the platform to a significantly larger user base. The implementation would involve:

- Language detection on resume and job description text using `langdetect` or spaCy's `langdetect` component
- Loading the appropriate spaCy language model (`fr_core_news_sm`, `de_core_news_sm`, etc.) based on detected language
- Translating the action verb and keyword databases to each supported language
- Internationalising the Django templates using `django.utils.translation` and `.po` message files

An initial release could target French, German, and Spanish — the three largest non-English job markets in Europe.

#### 10. Resume A/B Testing Enhancement

The system already has an `ab_testing.py` module. Expanding this into a full A/B testing framework would allow users to test two versions of their resume against the same job description and track which version generates more interview callbacks. The enhancement would include:

- Automatic random assignment of resume version when applying to a job
- Statistical significance testing on outcome data (chi-squared test on interview callback rates)
- A dashboard showing which resume elements correlate with better outcomes across the user's application history

---

### Long-Term Strategic Enhancements

#### 11. Fine-Tuned Resume Optimisation Model

The current AI optimisation relies on general-purpose GPT-4o-mini with prompt engineering. A long-term improvement is to fine-tune a smaller, faster model specifically on resume optimisation tasks. The training data would be constructed from:

- Pairs of weak and strong bullet points (sourced from public resume datasets and user feedback)
- Before/after optimisation examples rated highly by users
- Job description / resume pairs with known positive outcomes (interview callbacks)

A fine-tuned model would produce more consistent, domain-specific rewrites at lower cost and latency than the general-purpose API. It could be hosted locally (eliminating the OpenAI API dependency) using a framework such as Ollama or vLLM.

#### 12. Real-Time ATS Score as You Type

A real-time scoring mode would recalculate the ATS score incrementally as the user edits their resume, without requiring a manual "Analyse" action. This would be implemented using:

- A debounced JavaScript event listener on all resume text fields
- A lightweight scoring endpoint that accepts partial resume data and returns an updated score
- A persistent score indicator in the sidebar that updates live

The technical challenge is making the scoring fast enough for real-time use. The solution is to cache the job description keyword set and only recompute the affected scoring factors (keyword match, action verb score) on each keystroke, rather than running the full six-factor pipeline.

#### 13. Mobile Native Application

A React Native or Flutter mobile application would provide a native experience for job seekers who manage their search primarily on mobile. Key mobile-specific features would include:

- Camera-based resume scanning (photograph a printed resume → OCR → import)
- Push notifications for application status reminders ("You applied 2 weeks ago — time to follow up?")
- Offline resume viewing and editing with background sync
- One-tap job application tracking from the mobile browser via a share extension

The existing REST API (DRF + JWT) already provides the backend foundation for a mobile client with no additional server-side work required.

#### 14. Recruiter-Facing Portal

A complementary recruiter portal would allow hiring managers to post job descriptions and receive a ranked list of candidate resumes from NextGenCV users who have opted in to be discoverable. This would create a two-sided marketplace:

- Candidates opt in to a talent pool and set their target roles, locations, and availability
- Recruiters post job descriptions and receive a ranked list of matching candidates with ATS scores
- Candidates are notified when a recruiter views their profile

This transforms NextGenCV from a candidate tool into a full recruitment platform, significantly expanding its commercial potential.

#### 15. Predictive Application Success Scoring

By aggregating anonymised outcome data across all users (ATS score at application → interview callback → offer), the system could train a predictive model that estimates the probability of a successful application before the user submits it. The model would take as input the ATS score, the user's historical callback rate, the company size, the role seniority, and the time since the job was posted, and output a probability estimate. This would give users a data-driven signal on whether to apply now, improve the resume first, or skip the role entirely.

---

### Enhancement Roadmap Summary

| Priority | Enhancement | Effort | Impact |
|---|---|---|---|
| Short-term | Production deployment config (Docker, CI/CD) | Medium | High |
| Short-term | PostgreSQL + connection pooling | Low | High |
| Short-term | OCR for scanned PDFs | Medium | High |
| Short-term | Semantic keyword matching | Medium | High |
| Short-term | AI output feedback ratings | Low | Medium |
| Medium-term | Live job board integration | High | High |
| Medium-term | Subscription and billing (Stripe) | High | High |
| Medium-term | Collaborative resume review | High | Medium |
| Medium-term | Multi-language NLP support | High | Medium |
| Medium-term | A/B testing framework expansion | Medium | Medium |
| Long-term | Fine-tuned resume optimisation model | Very High | High |
| Long-term | Real-time ATS score as you type | Medium | High |
| Long-term | Mobile native application | Very High | High |
| Long-term | Recruiter-facing portal | Very High | Very High |
| Long-term | Predictive application success scoring | Very High | High |

---

---

## Bibliography

The following references cover the academic literature, official technical documentation, and industry sources consulted during the design and development of NextGenCV. References are formatted in APA 7th edition style.

---

### Academic and Industry Research

Applicant Tracking Systems (ATS) and Resume Screening

Bogen, M., & Rieke, A. (2018). *Help wanted: An examination of hiring algorithms, equity, and bias*. Upturn. https://upturn.org/work/help-wanted/

Chalfin, A., Danieli, O., Hillis, A., Jain, M., Jung, J., Shroff, R., & Stevenson, B. (2016). Productivity and selection of human capital with machine learning. *American Economic Review, 106*(5), 124–127. https://doi.org/10.1257/aer.p20161029

Dattner, B., Chamorro-Premuzic, T., Buchband, R., & Schettler, L. (2019, May 6). The legal and ethical implications of using AI in hiring. *Harvard Business Review*. https://hbr.org/2019/04/the-legal-and-ethical-implications-of-using-ai-in-hiring

Jobscan. (2023). *2023 job seeker nation report: How job seekers are navigating the modern job market*. Jobscan Research. https://www.jobscan.co/blog/job-seeker-nation/

LinkedIn Economic Graph. (2023). *Future of skills 2023: The skills companies need most*. LinkedIn Talent Solutions. https://economicgraph.linkedin.com/research/future-of-skills

Raghavan, M., Barocas, S., Kleinberg, J., & Levy, K. (2020). Mitigating bias in algorithmic hiring: Evaluating claims and practices. *Proceedings of the 2020 Conference on Fairness, Accountability, and Transparency*, 469–481. https://doi.org/10.1145/3351095.3372828

Resume Genius. (2024). *ATS resume statistics: How applicant tracking systems affect your job search*. Resume Genius Research. https://resumegenius.com/blog/resume-help/ats-resume-statistics

Van Esch, P., Black, J. S., & Ferolie, J. (2019). Marketing AI recruitment: The next phase in job application and selection. *Computers in Human Behavior, 90*, 215–222. https://doi.org/10.1016/j.chb.2018.09.009

---

### Natural Language Processing

Bird, S., Klein, E., & Loper, E. (2009). *Natural language processing with Python: Analyzing text with the natural language toolkit*. O'Reilly Media. https://www.nltk.org/book/

Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of deep bidirectional transformers for language understanding. *Proceedings of NAACL-HLT 2019*, 4171–4186. https://doi.org/10.18653/v1/N19-1423

Honnibal, M., Montani, I., Van Landeghem, S., & Boyd, A. (2020). *spaCy: Industrial-strength natural language processing in Python* (Version 3.x) [Software]. Explosion AI. https://doi.org/10.5281/zenodo.1212303

Manning, C. D., Raghavan, P., & Schütze, H. (2008). *Introduction to information retrieval*. Cambridge University Press. https://nlp.stanford.edu/IR-book/

Mikolov, T., Chen, K., Corrado, G., & Dean, J. (2013). Efficient estimation of word representations in vector space. *arXiv preprint arXiv:1301.3781*. https://arxiv.org/abs/1301.3781

Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. *Proceedings of EMNLP-IJCNLP 2019*, 3982–3992. https://doi.org/10.18653/v1/D19-1410

Salton, G., & Buckley, C. (1988). Term-weighting approaches in automatic text retrieval. *Information Processing & Management, 24*(5), 513–523. https://doi.org/10.1016/0306-4573(88)90021-0

---

### Large Language Models and AI

Brown, T., Mann, B., Ryder, N., Subbiah, M., Kaplan, J., Dhariwal, P., Neelakantan, A., Shyam, P., Sastry, G., Askell, A., Agarwal, S., Herbert-Voss, A., Krueger, G., Henighan, T., Child, R., Ramesh, A., Ziegler, D., Wu, J., Winter, C., … Amodei, D. (2020). Language models are few-shot learners. *Advances in Neural Information Processing Systems, 33*, 1877–1901. https://arxiv.org/abs/2005.14165

OpenAI. (2023). *GPT-4 technical report*. OpenAI. https://arxiv.org/abs/2303.08774

OpenAI. (2024). *OpenAI API reference: Chat completions* (Version 1.35.0) [API documentation]. https://platform.openai.com/docs/api-reference/chat

Wei, J., Wang, X., Schuurmans, D., Bosma, M., Ichter, B., Xia, F., Chi, E., Le, Q., & Zhou, D. (2022). Chain-of-thought prompting elicits reasoning in large language models. *Advances in Neural Information Processing Systems, 35*, 24824–24837. https://arxiv.org/abs/2201.11903

---

### Web Development and Software Engineering

Django Software Foundation. (2023). *Django documentation* (Version 4.2). https://docs.djangoproject.com/en/4.2/

Django REST Framework. (2024). *Django REST framework documentation* (Version 3.15.2). Tom Christie. https://www.django-rest-framework.org/

Fielding, R. T. (2000). *Architectural styles and the design of network-based software architectures* [Doctoral dissertation, University of California, Irvine]. https://ics.uci.edu/~fielding/pubs/dissertation/top.htm

Fowler, M. (2002). *Patterns of enterprise application architecture*. Addison-Wesley Professional.

Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). *Design patterns: Elements of reusable object-oriented software*. Addison-Wesley Professional.

Grinberg, M. (2018). *Flask web development: Developing web applications with Python* (2nd ed.). O'Reilly Media.

Holovaty, A., & Kaplan-Moss, J. (2009). *The definitive guide to Django: Web development done right* (2nd ed.). Apress.

Mozilla Developer Network. (2024). *HTTP — MDN web docs*. Mozilla. https://developer.mozilla.org/en-US/docs/Web/HTTP

OWASP Foundation. (2021). *OWASP top ten 2021*. Open Web Application Security Project. https://owasp.org/Top10/

---

### Database and Data Management

Codd, E. F. (1970). A relational model of data for large shared data banks. *Communications of the ACM, 13*(6), 377–387. https://doi.org/10.1145/362384.362685

PostgreSQL Global Development Group. (2024). *PostgreSQL 16 documentation*. https://www.postgresql.org/docs/16/

SQLite Consortium. (2024). *SQLite documentation*. https://www.sqlite.org/docs.html

---

### Asynchronous Processing and Caching

Celery Project. (2024). *Celery: Distributed task queue documentation* (Version 5.3.6). https://docs.celeryq.dev/en/stable/

Redis Ltd. (2024). *Redis documentation* (Version 7.x). https://redis.io/docs/

---

### PDF Processing and Document Generation

pdfplumber. (2024). *pdfplumber: Plumb a PDF for detailed information about each text character, rectangle, and line* (Version 0.10.3) [Software]. Jeremy Singer-Vine. https://github.com/jsvine/pdfplumber

WeasyPrint. (2024). *WeasyPrint documentation* (Version 59.0). Kozea. https://doc.courtbouillon.org/weasyprint/stable/

python-docx. (2024). *python-docx documentation* (Version 1.1.0) [Software]. https://python-docx.readthedocs.io/

---

### Testing

Hypothesis. (2024). *Hypothesis: Property-based testing for Python documentation* (Version 6.92.1). https://hypothesis.readthedocs.io/

MacIver, D. R., Hatfield-Dodds, Z., & Contributors. (2019). Hypothesis: A new approach to property-based testing. *Journal of Open Source Software, 4*(43), 1891. https://doi.org/10.21105/joss.01891

---

### Security

Bernstein, D. J. (2005). *Cache-timing attacks on AES*. https://cr.yp.to/antiforgery/cachetiming-20050414.pdf

Django Software Foundation. (2023). *Django security documentation*. https://docs.djangoproject.com/en/4.2/topics/security/

Stuttard, D., & Pinto, M. (2011). *The web application hacker's handbook: Finding and exploiting security flaws* (2nd ed.). Wiley.

---

### Data Visualization

Chart.js Contributors. (2024). *Chart.js documentation* (Version 4.x). https://www.chartjs.org/docs/latest/

Tufte, E. R. (2001). *The visual display of quantitative information* (2nd ed.). Graphics Press.

---
