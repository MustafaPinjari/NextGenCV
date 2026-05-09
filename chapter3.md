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
