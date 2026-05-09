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

