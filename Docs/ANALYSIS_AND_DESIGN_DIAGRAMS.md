# ANALYSIS & DESIGN DIAGRAMS
# NextGenCV - ATS Resume Builder

---

## 3.1 DATA FLOW DIAGRAM (DFD)

### Level 0 - Context Diagram

```
                    ┌─────────────────────────────────────┐
                    │                                     │
                    │      NextGenCV System               │
    User ──────────>│   (ATS Resume Builder)              │────────> PDF Resume
                    │                                     │
                    │                                     │
                    └─────────────────────────────────────┘
                              ↑           ↓
                              │           │
                         Job Description  ATS Score
```

### Level 1 - Main Processes

```
┌──────────┐
│  User    │
└────┬─────┘
     │
     │ Registration/Login
     ↓
┌─────────────────────────────────────────────────────────────────┐
│  1.0 Authentication                                             │
│  - Register User                                                │
│  - Login/Logout                                                 │
└────┬────────────────────────────────────────────────────────────┘
     │ User Credentials
     ↓
┌─────────────────────────────────────────────────────────────────┐
│  2.0 Resume Management                                          │
│  - Create Resume                                                │
│  - Edit Resume Sections                                         │
│  - Delete Resume                                                │
│  - Duplicate Resume                                             │
└────┬────────────────────────────────────────────────────────────┘
     │ Resume Data
     ↓
┌─────────────────────────────────────────────────────────────────┐
│  D1: Database (SQLite)                                          │
│  - User, Resume, PersonalInfo, Experience, Education,           │
│    Skills, Projects, ResumeVersion                              │
└────┬────────────────────────────────────────────────────────────┘
     │ Resume Content
     ↓
┌─────────────────────────────────────────────────────────────────┐
│  3.0 ATS Analysis                                               │
│  - Extract Keywords from Job Description                        │
│  - Analyze Resume Content                                       │
│  - Calculate ATS Score                                          │
│  - Generate Suggestions                                         │
└────┬────────────────────────────────────────────────────────────┘
     │ Analysis Results
     ↓
┌─────────────────────────────────────────────────────────────────┐
│  4.0 Resume Optimization                                        │
│  - Enhance Action Verbs                                         │
│  - Add Missing Keywords                                         │
│  - Improve Quantification                                       │
│  - Create Optimized Version                                     │
└────┬────────────────────────────────────────────────────────────┘
     │ Optimized Resume
     ↓
┌─────────────────────────────────────────────────────────────────┐
│  5.0 Export & Generation                                        │
│  - Generate PDF (WeasyPrint)                                    │
│  - Generate DOCX                                                │
│  - Generate Plain Text                                          │
│  - Batch Export (ZIP)                                           │
└────┬────────────────────────────────────────────────────────────┘
     │
     ↓
┌──────────┐
│  Output  │
│  Files   │
└──────────┘
```

### Level 2 - ATS Analysis Process (Detailed)

```
┌──────────────┐
│ Job          │
│ Description  │
└──────┬───────┘
       │
       ↓
┌─────────────────────────────────────────────────────────────────┐
│  3.1 Text Preprocessing                                         │
│  - Convert to lowercase                                         │
│  - Remove stop words                                            │
│  - Tokenize text                                                │
└────┬────────────────────────────────────────────────────────────┘
     │ Cleaned Text
     ↓
┌─────────────────────────────────────────────────────────────────┐
│  3.2 Keyword Extraction (spaCy NLP)                             │
│  - Extract nouns, verbs, adjectives                             │
│  - Identify technical terms                                     │
│  - Extract skills and qualifications                            │
└────┬────────────────────────────────────────────────────────────┘
     │ Keywords List
     ↓
┌──────────────┐
│ Resume       │
│ Content      │
└──────┬───────┘
       │
       ↓
┌─────────────────────────────────────────────────────────────────┐
│  3.3 Resume Text Aggregation                                    │
│  - Combine all sections                                         │
│  - Extract experience descriptions                              │
│  - Extract skills and projects                                  │
└────┬────────────────────────────────────────────────────────────┘
     │ Resume Text
     ↓
┌─────────────────────────────────────────────────────────────────┐
│  3.4 Keyword Matching                                           │
│  - Compare JD keywords with resume                              │
│  - Calculate match percentage                                   │
│  - Identify missing keywords                                    │
└────┬────────────────────────────────────────────────────────────┘
     │ Match Results
     ↓
┌─────────────────────────────────────────────────────────────────┐
│  3.5 Multi-Factor Scoring                                       │
│  - Keyword Match Score (30%)                                    │
│  - Skill Relevance Score (25%)                                  │
│  - Experience Impact Score (20%)                                │
│  - Quantification Score (10%)                                   │
│  - Action Verb Score (10%)                                      │
│  - Section Completeness (5%)                                    │
└────┬────────────────────────────────────────────────────────────┘
     │ Final ATS Score
     ↓
┌─────────────────────────────────────────────────────────────────┐
│  3.6 Generate Suggestions                                       │
│  - Missing keywords to add                                      │
│  - Weak action verbs to replace                                 │
│  - Sections needing quantification                              │
│  - Formatting improvements                                      │
└────┬────────────────────────────────────────────────────────────┘
     │
     ↓
┌──────────────┐
│ Analysis     │
│ Report       │
└──────────────┘
```

---

## 3.2 TABLE SPECIFICATIONS (DATABASE)

### User Table
```
┌─────────────────────────────────────────────────────────────────┐
│ User (Django Auth Model)                                        │
├─────────────────────────────────────────────────────────────────┤
│ PK  id              INTEGER         Auto-increment              │
│     username        VARCHAR(150)    Unique, Not Null            │
│     email           VARCHAR(254)    Unique, Not Null            │
│     password        VARCHAR(128)    Hashed, Not Null            │
│     first_name      VARCHAR(150)    Optional                    │
│     last_name       VARCHAR(150)    Optional                    │
│     is_active       BOOLEAN         Default: True               │
│     date_joined     DATETIME        Auto-generated              │
│     last_login      DATETIME        Auto-updated                │
└─────────────────────────────────────────────────────────────────┘
```

### Resume Table
```
┌─────────────────────────────────────────────────────────────────┐
│ Resume                                                          │
├─────────────────────────────────────────────────────────────────┤
│ PK  id                      INTEGER         Auto-increment      │
│ FK  user_id                 INTEGER         → User.id           │
│     title                   VARCHAR(200)    Not Null            │
│     template                VARCHAR(50)     Default: 'professional' │
│     current_version_number  INTEGER         Default: 1          │
│     created_at              DATETIME        Auto-generated      │
│     updated_at              DATETIME        Auto-updated        │
│     last_analyzed_at        DATETIME        Nullable            │
│     last_optimized_at       DATETIME        Nullable            │
├─────────────────────────────────────────────────────────────────┤
│ Indexes:                                                        │
│   - (user_id, updated_at DESC)                                  │
│ Ordering: -updated_at                                           │
└─────────────────────────────────────────────────────────────────┘
```

### PersonalInfo Table
```
┌─────────────────────────────────────────────────────────────────┐
│ PersonalInfo                                                    │
├─────────────────────────────────────────────────────────────────┤
│ PK  id          INTEGER         Auto-increment                  │
│ FK  resume_id   INTEGER         → Resume.id (One-to-One)        │
│     full_name   VARCHAR(200)    Not Null                        │
│     phone       VARCHAR(20)     Optional                        │
│     email       VARCHAR(254)    Email validation                │
│     linkedin    VARCHAR(200)    URL validation, Optional        │
│     github      VARCHAR(200)    URL validation, Optional        │
│     location    VARCHAR(200)    Optional                        │
└─────────────────────────────────────────────────────────────────┘
```

### Experience Table
```
┌─────────────────────────────────────────────────────────────────┐
│ Experience                                                      │
├─────────────────────────────────────────────────────────────────┤
│ PK  id          INTEGER         Auto-increment                  │
│ FK  resume_id   INTEGER         → Resume.id                     │
│     company     VARCHAR(200)    Not Null                        │
│     role        VARCHAR(200)    Not Null                        │
│     start_date  DATE            Not Null                        │
│     end_date    DATE            Nullable (current job)          │
│     description TEXT            Optional                        │
│     order       INTEGER         Default: 0                      │
├─────────────────────────────────────────────────────────────────┤
│ Indexes:                                                        │
│   - (resume_id, order)                                          │
│   - (resume_id, start_date DESC)                                │
│ Ordering: order, -start_date                                    │
│ Constraint: start_date < end_date                               │
└─────────────────────────────────────────────────────────────────┘
```

### Education Table
```
┌─────────────────────────────────────────────────────────────────┐
│ Education                                                       │
├─────────────────────────────────────────────────────────────────┤
│ PK  id          INTEGER         Auto-increment                  │
│ FK  resume_id   INTEGER         → Resume.id                     │
│     institution VARCHAR(200)    Not Null                        │
│     degree      VARCHAR(200)    Not Null                        │
│     field       VARCHAR(200)    Optional                        │
│     start_year  INTEGER         Not Null                        │
│     end_year    INTEGER         Nullable (ongoing)              │
│     order       INTEGER         Default: 0                      │
├─────────────────────────────────────────────────────────────────┤
│ Indexes:                                                        │
│   - (resume_id, order)                                          │
│   - (resume_id, end_year DESC)                                  │
│ Ordering: order, -end_year                                      │
│ Constraint: start_year < end_year                               │
└─────────────────────────────────────────────────────────────────┘
```

### Skill Table
```
┌─────────────────────────────────────────────────────────────────┐
│ Skill                                                           │
├─────────────────────────────────────────────────────────────────┤
│ PK  id          INTEGER         Auto-increment                  │
│ FK  resume_id   INTEGER         → Resume.id                     │
│     name        VARCHAR(100)    Not Null                        │
│     category    VARCHAR(50)     Not Null                        │
├─────────────────────────────────────────────────────────────────┤
│ Indexes:                                                        │
│   - (resume_id, category)                                       │
│ Unique Constraint: (resume_id, name)                            │
└─────────────────────────────────────────────────────────────────┘
```

### Project Table
```
┌─────────────────────────────────────────────────────────────────┐
│ Project                                                         │
├─────────────────────────────────────────────────────────────────┤
│ PK  id           INTEGER         Auto-increment                 │
│ FK  resume_id    INTEGER         → Resume.id                    │
│     name         VARCHAR(200)    Not Null                       │
│     description  TEXT            Optional                       │
│     technologies VARCHAR(500)    Optional                       │
│     url          VARCHAR(200)    URL validation, Optional       │
│     order        INTEGER         Default: 0                     │
├─────────────────────────────────────────────────────────────────┤
│ Indexes:                                                        │
│   - (resume_id, order)                                          │
│ Ordering: order                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### ResumeVersion Table
```
┌─────────────────────────────────────────────────────────────────┐
│ ResumeVersion                                                   │
├─────────────────────────────────────────────────────────────────┤
│ PK  id                INTEGER         Auto-increment            │
│ FK  resume_id         INTEGER         → Resume.id               │
│     version_number    INTEGER         Not Null                  │
│     created_at        DATETIME        Auto-generated            │
│     modification_type VARCHAR(20)     Choices: manual/optimized/restored │
│     ats_score         FLOAT           Nullable                  │
│     snapshot_data     JSON            Complete resume state     │
│     user_notes        TEXT            Optional                  │
├─────────────────────────────────────────────────────────────────┤
│ Indexes:                                                        │
│   - (resume_id, created_at DESC)                                │
│ Unique Constraint: (resume_id, version_number)                  │
│ Ordering: -version_number                                       │
└─────────────────────────────────────────────────────────────────┘
```

### UploadedResume Table
```
┌─────────────────────────────────────────────────────────────────┐
│ UploadedResume                                                  │
├─────────────────────────────────────────────────────────────────┤
│ PK  id                  INTEGER         Auto-increment          │
│ FK  user_id             INTEGER         → User.id               │
│     original_filename   VARCHAR(255)    Not Null                │
│     file_path           VARCHAR(100)    File upload path        │
│     uploaded_at         DATETIME        Auto-generated          │
│     file_size           INTEGER         In bytes                │
│     extracted_text      TEXT            Parsed content          │
│     parsing_confidence  FLOAT           0.0 - 1.0               │
│     parsed_data         JSON            Structured data         │
│     status              VARCHAR(20)     Choices: uploaded/parsing/parsed/imported/failed │
│     error_message       TEXT            Optional                │
├─────────────────────────────────────────────────────────────────┤
│ Indexes:                                                        │
│   - (user_id, uploaded_at DESC)                                 │
│ Ordering: -uploaded_at                                          │
└─────────────────────────────────────────────────────────────────┘
```

### ResumeAnalysis Table
```
┌─────────────────────────────────────────────────────────────────┐
│ ResumeAnalysis                                                  │
├─────────────────────────────────────────────────────────────────┤
│ PK  id                        INTEGER     Auto-increment        │
│ FK  resume_id                 INTEGER     → Resume.id           │
│     job_description           TEXT        Not Null              │
│     analysis_timestamp        DATETIME    Auto-generated        │
│     keyword_match_score       FLOAT       0.0 - 100.0           │
│     skill_relevance_score     FLOAT       0.0 - 100.0           │
│     section_completeness_score FLOAT      0.0 - 100.0           │
│     experience_impact_score   FLOAT       0.0 - 100.0           │
│     quantification_score      FLOAT       0.0 - 100.0           │
│     action_verb_score         FLOAT       0.0 - 100.0           │
│     final_score               FLOAT       Weighted average      │
│     matched_keywords          JSON        Array of strings      │
│     missing_keywords          JSON        Array of strings      │
│     weak_action_verbs         JSON        Array of strings      │
│     missing_quantifications   JSON        Array of strings      │
│     suggestions               JSON        Array of objects      │
├─────────────────────────────────────────────────────────────────┤
│ Indexes:                                                        │
│   - (resume_id, analysis_timestamp DESC)                        │
│ Ordering: -analysis_timestamp                                   │
└─────────────────────────────────────────────────────────────────┘
```

### OptimizationHistory Table
```
┌─────────────────────────────────────────────────────────────────┐
│ OptimizationHistory                                             │
├─────────────────────────────────────────────────────────────────┤
│ PK  id                      INTEGER     Auto-increment          │
│ FK  resume_id               INTEGER     → Resume.id             │
│ FK  original_version_id     INTEGER     → ResumeVersion.id      │
│ FK  optimized_version_id    INTEGER     → ResumeVersion.id      │
│     job_description         TEXT        Not Null                │
│     optimization_timestamp  DATETIME    Auto-generated          │
│     original_score          FLOAT       Before optimization     │
│     optimized_score         FLOAT       After optimization      │
│     improvement_delta       FLOAT       Calculated difference   │
│     changes_summary         JSON        {type: count}           │
│     detailed_changes        JSON        Array of change objects │
│     accepted_changes        JSON        Array of change IDs     │
│     rejected_changes        JSON        Array of change IDs     │
│     user_notes              TEXT        Optional                │
├─────────────────────────────────────────────────────────────────┤
│ Indexes:                                                        │
│   - (resume_id, optimization_timestamp DESC)                    │
│ Ordering: -optimization_timestamp                               │
└─────────────────────────────────────────────────────────────────┘
```

### ResumeTemplate Table
```
┌─────────────────────────────────────────────────────────────────┐
│ ResumeTemplate                                                  │
├─────────────────────────────────────────────────────────────────┤
│ PK  id              INTEGER         Auto-increment              │
│     name            VARCHAR(100)    Unique, Not Null            │
│     display_name    VARCHAR(200)    Not Null                    │
│     description     TEXT            Optional                    │
│     category        VARCHAR(50)     Not Null                    │
│     preview_image   VARCHAR(100)    Image path                  │
│     template_file   VARCHAR(100)    HTML template path          │
│     is_active       BOOLEAN         Default: True               │
│     is_premium      BOOLEAN         Default: False              │
│     created_at      DATETIME        Auto-generated              │
│     updated_at      DATETIME        Auto-updated                │
└─────────────────────────────────────────────────────────────────┘
```

### TemplateCustomization Table
```
┌─────────────────────────────────────────────────────────────────┐
│ TemplateCustomization                                           │
├─────────────────────────────────────────────────────────────────┤
│ PK  id              INTEGER         Auto-increment              │
│ FK  resume_id       INTEGER         → Resume.id (One-to-One)    │
│ FK  template_id     INTEGER         → ResumeTemplate.id         │
│     primary_color   VARCHAR(7)      Hex color code              │
│     secondary_color VARCHAR(7)      Hex color code              │
│     font_family     VARCHAR(100)    Font name                   │
│     font_size       INTEGER         In pixels                   │
│     custom_css      TEXT            Optional CSS                │
│     created_at      DATETIME        Auto-generated              │
│     updated_at      DATETIME        Auto-updated                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3.3 ENTITY RELATIONSHIP DIAGRAM (ERD)

```
┌─────────────────────┐
│      User           │
│ (Django Auth)       │
├─────────────────────┤
│ PK id               │
│    username         │
│    email            │
│    password         │
│    first_name       │
│    last_name        │
│    is_active        │
│    date_joined      │
└──────────┬──────────┘
           │
           │ 1
           │
           │ M
           ↓
┌─────────────────────┐                    ┌─────────────────────┐
│      Resume         │ 1 ──────────── 1   │   PersonalInfo      │
├─────────────────────┤                    ├─────────────────────┤
│ PK id               │                    │ PK id               │
│ FK user_id          │                    │ FK resume_id        │
│    title            │                    │    full_name        │
│    template         │                    │    phone            │
│    current_version  │                    │    email            │
│    created_at       │                    │    linkedin         │
│    updated_at       │                    │    github           │
│    last_analyzed_at │                    │    location         │
│    last_optimized_at│                    └─────────────────────┘
└──────────┬──────────┘
           │
           ├─────────────────────────────────────────────────────┐
           │                                                     │
           │ 1                                                   │ 1
           │                                                     │
           │ M                                                   │ M
           ↓                                                     ↓
┌─────────────────────┐                    ┌─────────────────────┐
│    Experience       │                    │     Education       │
├─────────────────────┤                    ├─────────────────────┤
│ PK id               │                    │ PK id               │
│ FK resume_id        │                    │ FK resume_id        │
│    company          │                    │    institution      │
│    role             │                    │    degree           │
│    start_date       │                    │    field            │
│    end_date         │                    │    start_year       │
│    description      │                    │    end_year         │
│    order            │                    │    order            │
└─────────────────────┘                    └─────────────────────┘
           │
           │ 1
           │
           │ M
           ↓
┌─────────────────────┐                    ┌─────────────────────┐
│       Skill         │                    │      Project        │
├─────────────────────┤                    ├─────────────────────┤
│ PK id               │                    │ PK id               │
│ FK resume_id        │                    │ FK resume_id        │
│    name             │                    │    name             │
│    category         │                    │    description      │
└─────────────────────┘                    │    technologies     │
           ↑                                │    url              │
           │                                │    order            │
           │ 1                              └─────────────────────┘
           │                                           ↑
           │ M                                         │
           │                                           │ 1
┌──────────┴──────────┐                               │
│      Resume         │                               │ M
└──────────┬──────────┘                               │
           │                                           │
           │ 1                              ┌──────────┴──────────┐
           │                                │      Resume         │
           │ M                              └──────────┬──────────┘
           ↓                                           │
┌─────────────────────┐                               │ 1
│   ResumeVersion     │                               │
├─────────────────────┤                               │ M
│ PK id               │                               ↓
│ FK resume_id        │                    ┌─────────────────────┐
│    version_number   │                    │  ResumeAnalysis     │
│    created_at       │                    ├─────────────────────┤
│    modification_type│                    │ PK id               │
│    ats_score        │                    │ FK resume_id        │
│    snapshot_data    │                    │    job_description  │
│    user_notes       │                    │    analysis_timestamp│
└──────────┬──────────┘                    │    keyword_match_score│
           │                                │    skill_relevance_score│
           │                                │    section_completeness│
           │                                │    experience_impact│
           │                                │    quantification_score│
           │                                │    action_verb_score│
           │                                │    final_score      │
           │                                │    matched_keywords │
           │                                │    missing_keywords │
           │                                │    weak_action_verbs│
           │                                │    missing_quantifications│
           │                                │    suggestions      │
           │                                └─────────────────────┘
           │
           │ 1                              ┌─────────────────────┐
           │                                │      Resume         │
           │ M                              └──────────┬──────────┘
           ↓                                           │
┌─────────────────────┐                               │ 1
│ OptimizationHistory │                               │
├─────────────────────┤                               │ M
│ PK id               │                               ↓
│ FK resume_id        │                    ┌─────────────────────┐
│ FK original_version │                    │  UploadedResume     │
│ FK optimized_version│                    ├─────────────────────┤
│    job_description  │                    │ PK id               │
│    optimization_timestamp│               │ FK user_id          │
│    original_score   │                    │    original_filename│
│    optimized_score  │                    │    file_path        │
│    improvement_delta│                    │    uploaded_at      │
│    changes_summary  │                    │    file_size        │
│    detailed_changes │                    │    extracted_text   │
│    accepted_changes │                    │    parsing_confidence│
│    rejected_changes │                    │    parsed_data      │
│    user_notes       │                    │    status           │
└─────────────────────┘                    │    error_message    │
                                           └─────────────────────┘

┌─────────────────────┐
│  ResumeTemplate     │
├─────────────────────┤
│ PK id               │
│    name             │
│    display_name     │
│    description      │
│    category         │
│    preview_image    │
│    template_file    │
│    is_active        │
│    is_premium       │
│    created_at       │
│    updated_at       │
└──────────┬──────────┘
           │
           │ 1
           │
           │ M
           ↓
┌─────────────────────┐
│ TemplateCustomization│
├─────────────────────┤
│ PK id               │
│ FK resume_id        │
│ FK template_id      │
│    primary_color    │
│    secondary_color  │
│    font_family      │
│    font_size        │
│    custom_css       │
│    created_at       │
│    updated_at       │
└─────────────────────┘
```

### Cardinality Summary:
- User (1) ──→ (M) Resume
- User (1) ──→ (M) UploadedResume
- Resume (1) ──→ (1) PersonalInfo
- Resume (1) ──→ (M) Experience
- Resume (1) ──→ (M) Education
- Resume (1) ──→ (M) Skill
- Resume (1) ──→ (M) Project
- Resume (1) ──→ (M) ResumeVersion
- Resume (1) ──→ (M) ResumeAnalysis
- Resume (1) ──→ (M) OptimizationHistory
- Resume (1) ──→ (1) TemplateCustomization
- ResumeTemplate (1) ──→ (M) TemplateCustomization
- ResumeVersion (1) ──→ (M) OptimizationHistory (as original)
- ResumeVersion (1) ──→ (M) OptimizationHistory (as optimized)

---

## 3.4 ACTIVITY DIAGRAM

### User Registration & Resume Creation Flow

```
                    ┌─────────┐
                    │  Start  │
                    └────┬────┘
                         │
                         ↓
                  ┌──────────────┐
                  │ Visit Website│
                  └──────┬───────┘
                         │
                         ↓
                  ┌──────────────┐
              ┌───│ Registered?  │───┐
              │   └──────────────┘   │
              │ No                   │ Yes
              ↓                      ↓
       ┌─────────────┐        ┌─────────────┐
       │  Register   │        │    Login    │
       │  Account    │        └──────┬──────┘
       └──────┬──────┘               │
              │                      │
              └──────────┬───────────┘
                         │
                         ↓
                  ┌──────────────┐
                  │  Dashboard   │
                  └──────┬───────┘
                         │
                         ↓
                  ┌──────────────┐
                  │ Create Resume│
                  └──────┬───────┘
                         │
                         ↓
              ┌──────────────────────┐
              │ Choose Creation Mode │
              └──────┬───────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ↓            ↓            ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Build from   │ │ Upload PDF   │ │ Use Template │
│   Scratch    │ │   Resume     │ │              │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       │                ↓                │
       │         ┌──────────────┐        │
       │         │  Parse PDF   │        │
       │         └──────┬───────┘        │
       │                │                │
       │                ↓                │
       │         ┌──────────────┐        │
       │         │ Review Parsed│        │
       │         │     Data     │        │
       │         └──────┬───────┘        │
       │                │                │
       └────────────────┼────────────────┘
                        │
                        ↓
              ┌──────────────────┐
              │ Enter Personal   │
              │   Information    │
              └──────┬───────────┘
                     │
                     ↓
              ┌──────────────────┐
              │ Add Work         │
              │   Experience     │
              └──────┬───────────┘
                     │
                     ↓
              ┌──────────────────┐
              │ Add Education    │
              └──────┬───────────┘
                     │
                     ↓
              ┌──────────────────┐
              │ Add Skills       │
              └──────┬───────────┘
                     │
                     ↓
              ┌──────────────────┐
              │ Add Projects     │
              │  (Optional)      │
              └──────┬───────────┘
                     │
                     ↓
              ┌──────────────────┐
              │ Select Template  │
              └──────┬───────────┘
                     │
                     ↓
              ┌──────────────────┐
              │ Preview Resume   │
              └──────┬───────────┘
                     │
                     ↓
              ┌──────────────────┐
          ┌───│  Satisfied?      │───┐
          │   └──────────────────┘   │
          │ No                       │ Yes
          │                          │
          ↓                          ↓
   ┌─────────────┐           ┌─────────────┐
   │ Edit Resume │           │ Save Resume │
   └──────┬──────┘           └──────┬──────┘
          │                          │
          └──────────┬───────────────┘
                     │
                     ↓
                ┌─────────┐
                │   End   │
                └─────────┘
```

### ATS Analysis & Optimization Flow

```
                    ┌─────────┐
                    │  Start  │
                    └────┬────┘
                         │
                         ↓
              ┌──────────────────┐
              │ Select Resume    │
              └──────┬───────────┘
                     │
                     ↓
              ┌──────────────────┐
              │ Click "Analyze"  │
              └──────┬───────────┘
                     │
                     ↓
              ┌──────────────────┐
              │ Paste Job        │
              │  Description     │
              └──────┬───────────┘
                     │
                     ↓
              ┌──────────────────┐
              │ Submit for       │
              │   Analysis       │
              └──────┬───────────┘
                     │
                     ↓
        ┌────────────────────────────┐
        │ System: Extract Keywords   │
        │ from Job Description       │
        └────────────┬───────────────┘
                     │
                     ↓
        ┌────────────────────────────┐
        │ System: Aggregate Resume   │
        │ Content (All Sections)     │
        └────────────┬───────────────┘
                     │
                     ↓
        ┌────────────────────────────┐
        │ System: Perform Keyword    │
        │ Matching Analysis          │
        └────────────┬───────────────┘
                     │
                     ↓
        ┌────────────────────────────┐
        │ System: Calculate Scores   │
        │ - Keyword Match (30%)      │
        │ - Skill Relevance (25%)    │
        │ - Experience Impact (20%)  │
        │ - Quantification (10%)     │
        │ - Action Verbs (10%)       │
        │ - Completeness (5%)        │
        └────────────┬───────────────┘
                     │
                     ↓
        ┌────────────────────────────┐
        │ System: Generate           │
        │ Suggestions & Report       │
        └────────────┬───────────────┘
                     │
                     ↓
              ┌──────────────────┐
              │ Display Analysis │
              │    Results       │
              └──────┬───────────┘
                     │
                     ↓
              ┌──────────────────┐
          ┌───│ Score < 70%?     │───┐
          │   └──────────────────┘   │
          │ Yes                      │ No
          │                          │
          ↓                          ↓
   ┌─────────────┐           ┌─────────────┐
   │ Optimize    │           │ Export      │
   │  Resume     │           │  Resume     │
   └──────┬──────┘           └──────┬──────┘
          │                          │
          ↓                          │
   ┌─────────────┐                  │
   │ Review      │                  │
   │ Suggestions │                  │
   └──────┬──────┘                  │
          │                          │
          ↓                          │
   ┌─────────────┐                  │
   │ Accept/     │                  │
   │ Reject      │                  │
   │ Changes     │                  │
   └──────┬──────┘                  │
          │                          │
          ↓                          │
   ┌─────────────┐                  │
   │ Create New  │                  │
   │  Version    │                  │
   └──────┬──────┘                  │
          │                          │
          └──────────┬───────────────┘
                     │
                     ↓
                ┌─────────┐
                │   End   │
                └─────────┘
```

### Resume Export Flow

```
                    ┌─────────┐
                    │  Start  │
                    └────┬────┘
                         │
                         ↓
              ┌──────────────────┐
              │ Select Resume    │
              └──────┬───────────┘
                     │
                     ↓
              ┌──────────────────┐
              │ Click "Export"   │
              └──────┬───────────┘
                     │
                     ↓
              ┌──────────────────┐
              │ Choose Format    │
              └──────┬───────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ↓            ↓            ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│     PDF      │ │    DOCX      │ │  Plain Text  │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       ↓                ↓                ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Render HTML  │ │ Generate     │ │ Extract Text │
│  Template    │ │  Document    │ │   Content    │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       ↓                ↓                ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ WeasyPrint   │ │ python-docx  │ │ Format as    │
│ Convert to   │ │  Library     │ │  Plain Text  │
│     PDF      │ │              │ │              │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └────────────────┼────────────────┘
                        │
                        ↓
              ┌──────────────────┐
              │ Download File    │
              └──────┬───────────┘
                     │
                     ↓
                ┌─────────┐
                │   End   │
                └─────────┘
```

---

## 3.5 SEQUENCE DIAGRAM

### Resume Creation Sequence

```
User          Browser        Django View      Service Layer     Database
 │               │                │                 │              │
 │ Click Create  │                │                 │              │
 │──────────────>│                │                 │              │
 │               │ GET /resumes/create             │              │
 │               │───────────────>│                 │              │
 │               │                │                 │              │
 │               │   Render Form  │                 │              │
 │               │<───────────────│                 │              │
 │               │                │                 │              │
 │  Fill Form    │                │                 │              │
 │<──────────────│                │                 │              │
 │               │                │                 │              │
 │ Submit Form   │                │                 │              │
 │──────────────>│                │                 │              │
 │               │ POST /resumes/create            │              │
 │               │───────────────>│                 │              │
 │               │                │ create_resume() │              │
 │               │                │────────────────>│              │
 │               │                │                 │ INSERT Resume│
 │               │                │                 │─────────────>│
 │               │                │                 │              │
 │               │                │                 │ Resume ID    │
 │               │                │                 │<─────────────│
 │               │                │                 │              │
 │               │                │                 │ INSERT PersonalInfo│
 │               │                │                 │─────────────>│
 │               │                │                 │              │
 │               │                │                 │ INSERT Experience│
 │               │                │                 │─────────────>│
 │               │                │                 │              │
 │               │                │                 │ INSERT Education│
 │               │                │                 │─────────────>│
 │               │                │                 │              │
 │               │                │                 │ INSERT Skills│
 │               │                │                 │─────────────>│
 │               │                │                 │              │
 │               │                │   Resume Object │              │
 │               │                │<────────────────│              │
 │               │                │                 │              │
 │               │  Redirect to   │                 │              │
 │               │  Resume Detail │                 │              │
 │               │<───────────────│                 │              │
 │               │                │                 │              │
 │ View Resume   │                │                 │              │
 │<──────────────│                │                 │              │
 │               │                │                 │              │
```

### ATS Analysis Sequence

```
User          Browser        Django View      ATS Service       NLP Engine    Database
 │               │                │                 │                │           │
 │ Click Analyze │                │                 │                │           │
 │──────────────>│                │                 │                │           │
 │               │ GET /analyze/resume_id          │                │           │
 │               │───────────────>│                 │                │           │
 │               │                │                 │                │           │
 │               │   Render Form  │                 │                │           │
 │               │<───────────────│                 │                │           │
 │               │                │                 │                │           │
 │ Paste Job Desc│                │                 │                │           │
 │<──────────────│                │                 │                │           │
 │               │                │                 │                │           │
 │ Submit        │                │                 │                │           │
 │──────────────>│                │                 │                │           │
 │               │ POST /analyze/resume_id         │                │           │
 │               │───────────────>│                 │                │           │
 │               │                │ analyze_resume()│                │           │
 │               │                │────────────────>│                │           │
 │               │                │                 │                │           │
 │               │                │                 │ GET Resume Data│           │
 │               │                │                 │───────────────────────────>│
 │               │                │                 │                │           │
 │               │                │                 │ Resume Content │           │
 │               │                │                 │<───────────────────────────│
 │               │                │                 │                │           │
 │               │                │                 │ extract_keywords(JD)       │
 │               │                │                 │───────────────>│           │
 │               │                │                 │                │           │
 │               │                │                 │  JD Keywords   │           │
 │               │                │                 │<───────────────│           │
 │               │                │                 │                │           │
 │               │                │                 │ extract_keywords(Resume)   │
 │               │                │                 │───────────────>│           │
 │               │                │                 │                │           │
 │               │                │                 │ Resume Keywords│           │
 │               │                │                 │<───────────────│           │
 │               │                │                 │                │           │
 │               │                │                 │ calculate_scores()         │
 │               │                │                 │────────────────────────────│
 │               │                │                 │                │           │
 │               │                │                 │ generate_suggestions()     │
 │               │                │                 │────────────────────────────│
 │               │                │                 │                │           │
 │               │                │                 │ SAVE Analysis  │           │
 │               │                │                 │───────────────────────────>│
 │               │                │                 │                │           │
 │               │                │  Analysis Result│                │           │
 │               │                │<────────────────│                │           │
 │               │                │                 │                │           │
 │               │  Render Results│                 │                │           │
 │               │<───────────────│                 │                │           │
 │               │                │                 │                │           │
 │ View Analysis │                │                 │                │           │
 │<──────────────│                │                 │                │           │
 │               │                │                 │                │           │
```

### Resume Optimization Sequence

```
User          Browser        Django View    Optimization Service  AI Engine    Database
 │               │                │                 │                │           │
 │ Click Optimize│                │                 │                │           │
 │──────────────>│                │                 │                │           │
 │               │ GET /fix/resume_id              │                │           │
 │               │───────────────>│                 │                │           │
 │               │                │                 │                │           │
 │               │   Render Form  │                 │                │           │
 │               │<───────────────│                 │                │           │
 │               │                │                 │                │           │
 │ Submit JD     │                │                 │                │           │
 │──────────────>│                │                 │                │           │
 │               │ POST /fix/preview/resume_id     │                │           │
 │               │───────────────>│                 │                │           │
 │               │                │ optimize_resume()               │           │
 │               │                │────────────────>│                │           │
 │               │                │                 │                │           │
 │               │                │                 │ GET Resume     │           │
 │               │                │                 │───────────────────────────>│
 │               │                │                 │                │           │
 │               │                │                 │ Resume Data    │           │
 │               │                │                 │<───────────────────────────│
 │               │                │                 │                │           │
 │               │                │                 │ analyze_gaps() │           │
 │               │                │                 │───────────────>│           │
 │               │                │                 │                │           │
 │               │                │                 │ Gap Analysis   │           │
 │               │                │                 │<───────────────│           │
 │               │                │                 │                │           │
 │               │                │                 │ enhance_action_verbs()     │
 │               │                │                 │───────────────>│           │
 │               │                │                 │                │           │
 │               │                │                 │ Enhanced Text  │           │
 │               │                │                 │<───────────────│           │
 │               │                │                 │                │           │
 │               │                │                 │ inject_keywords()          │
 │               │                │                 │───────────────>│           │
 │               │                │                 │                │           │
 │               │                │                 │ Optimized Text │           │
 │               │                │                 │<───────────────│           │
 │               │                │                 │                │           │
 │               │                │                 │ add_quantification()       │
 │               │                │                 │───────────────>│           │
 │               │                │                 │                │           │
 │               │                │                 │ Final Text     │           │
 │               │                │                 │<───────────────│           │
 │               │                │                 │                │           │
 │               │                │  Optimized Data │                │           │
 │               │                │<────────────────│                │           │
 │               │                │                 │                │           │
 │               │  Side-by-Side  │                 │                │           │
 │               │   Comparison   │                 │                │           │
 │               │<───────────────│                 │                │           │
 │               │                │                 │                │           │
 │ Review Changes│                │                 │                │           │
 │<──────────────│                │                 │                │           │
 │               │                │                 │                │           │
 │ Accept Changes│                │                 │                │           │
 │──────────────>│                │                 │                │           │
 │               │ POST /fix/accept/resume_id      │                │           │
 │               │───────────────>│                 │                │           │
 │               │                │                 │                │           │
 │               │                │ CREATE New Version              │           │
 │               │                │────────────────────────────────────────────>│
 │               │                │                 │                │           │
 │               │                │ SAVE OptimizationHistory        │           │
 │               │                │────────────────────────────────────────────>│
 │               │                │                 │                │           │
 │               │  Redirect to   │                 │                │           │
 │               │  Resume Detail │                 │                │           │
 │               │<───────────────│                 │                │           │
 │               │                │                 │                │           │
 │ View Updated  │                │                 │                │           │
 │    Resume     │                │                 │                │           │
 │<──────────────│                │                 │                │           │
 │               │                │                 │                │           │
```

### PDF Export Sequence

```
User          Browser        Django View      Export Service    WeasyPrint    File System
 │               │                │                 │                │           │
 │ Click Export  │                │                 │                │           │
 │──────────────>│                │                 │                │           │
 │               │ GET /export/pdf/resume_id       │                │           │
 │               │───────────────>│                 │                │           │
 │               │                │ export_to_pdf() │                │           │
 │               │                │────────────────>│                │           │
 │               │                │                 │                │           │
 │               │                │                 │ GET Resume Data│           │
 │               │                │                 │───────────────────────────>│
 │               │                │                 │                │           │
 │               │                │                 │ Resume Object  │           │
 │               │                │                 │<───────────────────────────│
 │               │                │                 │                │           │
 │               │                │                 │ render_template()          │
 │               │                │                 │────────────────────────────│
 │               │                │                 │                │           │
 │               │                │                 │ HTML Content   │           │
 │               │                │                 │────────────────────────────│
 │               │                │                 │                │           │
 │               │                │                 │ HTML_to_PDF()  │           │
 │               │                │                 │───────────────>│           │
 │               │                │                 │                │           │
 │               │                │                 │ PDF Binary     │           │
 │               │                │                 │<───────────────│           │
 │               │                │                 │                │           │
 │               │                │  PDF Response   │                │           │
 │               │                │<────────────────│                │           │
 │               │                │                 │                │           │
 │               │  Download PDF  │                 │                │           │
 │               │<───────────────│                 │                │           │
 │               │                │                 │                │           │
 │ Save to Disk  │                │                 │                │           │
 │──────────────────────────────────────────────────────────────────────────────>│
 │               │                │                 │                │           │
```

---

## 3.6 CLASS DIAGRAM

```
┌─────────────────────────────────────────────────────────────────┐
│                          User                                   │
│                    (Django Auth Model)                          │
├─────────────────────────────────────────────────────────────────┤
│ - id: Integer                                                   │
│ - username: String                                              │
│ - email: String                                                 │
│ - password: String                                              │
│ - first_name: String                                            │
│ - last_name: String                                             │
│ - is_active: Boolean                                            │
│ - date_joined: DateTime                                         │
├─────────────────────────────────────────────────────────────────┤
│ + register(): Boolean                                           │
│ + login(): Boolean                                              │
│ + logout(): void                                                │
│ + update_profile(): Boolean                                     │
│ + get_resumes(): List<Resume>                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ 1..*
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                         Resume                                  │
├─────────────────────────────────────────────────────────────────┤
│ - id: Integer                                                   │
│ - user_id: Integer (FK)                                         │
│ - title: String                                                 │
│ - template: String                                              │
│ - current_version_number: Integer                               │
│ - created_at: DateTime                                          │
│ - updated_at: DateTime                                          │
│ - last_analyzed_at: DateTime                                    │
│ - last_optimized_at: DateTime                                   │
├─────────────────────────────────────────────────────────────────┤
│ + create(): Resume                                              │
│ + update(): Boolean                                             │
│ + delete(): Boolean                                             │
│ + duplicate(): Resume                                           │
│ + get_all_sections(): Dict                                      │
│ + export_to_pdf(): File                                         │
│ + export_to_docx(): File                                        │
│ + export_to_text(): String                                      │
│ + create_version(): ResumeVersion                               │
│ + get_latest_analysis(): ResumeAnalysis                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┬───────────────┐
         │               │               │               │
         │ 1..1          │ 1..*          │ 1..*          │ 1..*
         ↓               ↓               ↓               ↓
┌──────────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  PersonalInfo    │ │  Experience  │ │  Education   │ │    Skill     │
├──────────────────┤ ├──────────────┤ ├──────────────┤ ├──────────────┤
│ - id: Integer    │ │ - id: Integer│ │ - id: Integer│ │ - id: Integer│
│ - resume_id: FK  │ │ - resume_id:FK│ │ - resume_id:FK│ │ - resume_id:FK│
│ - full_name: Str │ │ - company:Str│ │ - institution│ │ - name: Str  │
│ - phone: String  │ │ - role: Str  │ │ - degree: Str│ │ - category:Str│
│ - email: String  │ │ - start_date │ │ - field: Str │ └──────────────┘
│ - linkedin: URL  │ │ - end_date   │ │ - start_year │
│ - github: URL    │ │ - description│ │ - end_year   │
│ - location: Str  │ │ - order: Int │ │ - order: Int │
├──────────────────┤ ├──────────────┤ ├──────────────┤
│ + update(): Bool │ │ + add(): Bool│ │ + add(): Bool│
│ + validate():Bool│ │ + update():  │ │ + update():  │
└──────────────────┘ │   Bool       │ │   Bool       │
                     │ + delete():  │ │ + delete():  │
                     │   Bool       │ │   Bool       │
                     │ + reorder(): │ │ + reorder(): │
                     │   Bool       │ │   Bool       │
                     └──────────────┘ └──────────────┘

         ┌───────────────┼───────────────┬───────────────┐
         │               │               │               │
         │ 1..*          │ 1..*          │ 1..*          │ 1..*
         ↓               ↓               ↓               ↓
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│    Project       │ │  ResumeVersion   │ │ ResumeAnalysis   │ │OptimizationHistory│
├──────────────────┤ ├──────────────────┤ ├──────────────────┤ ├──────────────────┤
│ - id: Integer    │ │ - id: Integer    │ │ - id: Integer    │ │ - id: Integer    │
│ - resume_id: FK  │ │ - resume_id: FK  │ │ - resume_id: FK  │ │ - resume_id: FK  │
│ - name: String   │ │ - version_number │ │ - job_description│ │ - original_ver_id│
│ - description    │ │ - created_at     │ │ - analysis_time  │ │ - optimized_ver_id│
│ - technologies   │ │ - modification   │ │ - keyword_match  │ │ - job_description│
│ - url: URL       │ │   _type          │ │   _score         │ │ - optimization   │
│ - order: Integer │ │ - ats_score      │ │ - skill_relevance│ │   _timestamp     │
├──────────────────┤ │ - snapshot_data  │ │   _score         │ │ - original_score │
│ + add(): Bool    │ │ - user_notes     │ │ - section_       │ │ - optimized_score│
│ + update(): Bool │ ├──────────────────┤ │   completeness   │ │ - improvement    │
│ + delete(): Bool │ │ + create(): Ver  │ │ - experience     │ │   _delta         │
│ + reorder(): Bool│ │ + restore(): Bool│ │   _impact_score  │ │ - changes_summary│
└──────────────────┘ │ + compare(): Dict│ │ - quantification │ │ - detailed_changes│
                     │ + get_snapshot():│ │   _score         │ │ - accepted_changes│
                     │   Dict           │ │ - action_verb    │ │ - rejected_changes│
                     └──────────────────┘ │   _score         │ │ - user_notes     │
                                          │ - final_score    │ ├──────────────────┤
                                          │ - matched_keywords│ │ + create(): Opt  │
                                          │ - missing_keywords│ │ + get_changes(): │
                                          │ - weak_action_verbs│ │   List           │
                                          │ - missing_quant  │ │ + calculate_delta│
                                          │ - suggestions    │ │   (): Float      │
                                          ├──────────────────┤ └──────────────────┘
                                          │ + analyze(): Res │
                                          │ + get_score():   │
                                          │   Float          │
                                          │ + get_suggestions│
                                          │   (): List       │
                                          └──────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      ATSAnalyzerService                         │
├─────────────────────────────────────────────────────────────────┤
│ - nlp_engine: spaCy                                             │
│ - stop_words: Set<String>                                       │
│ - strong_action_verbs: List<String>                             │
├─────────────────────────────────────────────────────────────────┤
│ + analyze_resume(resume: Resume, jd: String): ResumeAnalysis   │
│ + extract_keywords(text: String): List<String>                 │
│ + calculate_keyword_match(resume: Resume, jd_keywords: List):  │
│   Float                                                         │
│ + calculate_skill_relevance(resume: Resume, jd: String): Float │
│ + calculate_experience_impact(resume: Resume): Float           │
│ + calculate_quantification_score(resume: Resume): Float        │
│ + calculate_action_verb_score(resume: Resume): Float           │
│ + calculate_section_completeness(resume: Resume): Float        │
│ + generate_suggestions(analysis: ResumeAnalysis): List<String> │
│ + identify_missing_keywords(resume: Resume, jd: String):       │
│   List<String>                                                  │
│ + identify_weak_action_verbs(resume: Resume): List<String>     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   ResumeOptimizationService                     │
├─────────────────────────────────────────────────────────────────┤
│ - analyzer: ATSAnalyzerService                                  │
│ - action_verb_replacements: Dict<String, List<String>>          │
│ - quantification_templates: List<String>                        │
├─────────────────────────────────────────────────────────────────┤
│ + optimize_resume(resume: Resume, jd: String):                 │
│   OptimizationHistory                                           │
│ + enhance_action_verbs(text: String): String                   │
│ + inject_keywords(text: String, keywords: List<String>): String│
│ + add_quantification(text: String): String                     │
│ + generate_optimized_version(resume: Resume, changes: Dict):   │
│   Resume                                                        │
│ + calculate_improvement(original: Resume, optimized: Resume):  │
│   Float                                                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      ExportService                              │
├─────────────────────────────────────────────────────────────────┤
│ - template_engine: Django Templates                             │
│ - pdf_generator: WeasyPrint                                     │
│ - docx_generator: python-docx                                   │
├─────────────────────────────────────────────────────────────────┤
│ + export_to_pdf(resume: Resume): File                           │
│ + export_to_docx(resume: Resume): File                          │
│ + export_to_text(resume: Resume): String                        │
│ + batch_export(resumes: List<Resume>, format: String): ZipFile │
│ + render_template(resume: Resume, template: String): HTML      │
│ + apply_customization(html: HTML, customization: Dict): HTML   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      PDFParserService                           │
├─────────────────────────────────────────────────────────────────┤
│ - pdf_reader: pdfplumber                                        │
│ - nlp_engine: spaCy                                             │
├─────────────────────────────────────────────────────────────────┤
│ + parse_pdf(file: File): UploadedResume                         │
│ + extract_text(pdf: File): String                               │
│ + extract_personal_info(text: String): Dict                     │
│ + extract_experience(text: String): List<Dict>                  │
│ + extract_education(text: String): List<Dict>                   │
│ + extract_skills(text: String): List<String>                    │
│ + calculate_parsing_confidence(parsed_data: Dict): Float        │
│ + create_resume_from_parsed(parsed_data: Dict, user: User):    │
│   Resume                                                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    TemplateService                              │
├─────────────────────────────────────────────────────────────────┤
│ - template_repository: List<ResumeTemplate>                     │
├─────────────────────────────────────────────────────────────────┤
│ + get_all_templates(): List<ResumeTemplate>                     │
│ + get_template_by_id(id: Integer): ResumeTemplate              │
│ + apply_template(resume: Resume, template: ResumeTemplate):    │
│   Boolean                                                       │
│ + customize_template(resume: Resume, customization: Dict):     │
│   TemplateCustomization                                         │
│ + preview_template(template: ResumeTemplate, sample_data: Dict):│
│   HTML                                                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    AnalyticsService                             │
├─────────────────────────────────────────────────────────────────┤
│ - cache: Django Cache                                           │
├─────────────────────────────────────────────────────────────────┤
│ + get_user_analytics(user: User): Dict                          │
│ + get_resume_health_score(resume: Resume): Float               │
│ + get_score_trends(resume: Resume): List<Dict>                 │
│ + get_top_missing_keywords(resume: Resume): List<String>        │
│ + get_optimization_history(resume: Resume): List<Dict>          │
│ + generate_improvement_report(user: User): Dict                 │
│ + calculate_average_score(user: User): Float                    │
└─────────────────────────────────────────────────────────────────┘
```

### Class Relationships Summary:

1. User → Resume (1:M)
2. Resume → PersonalInfo (1:1)
3. Resume → Experience (1:M)
4. Resume → Education (1:M)
5. Resume → Skill (1:M)
6. Resume → Project (1:M)
7. Resume → ResumeVersion (1:M)
8. Resume → ResumeAnalysis (1:M)
9. Resume → OptimizationHistory (1:M)
10. ResumeVersion → OptimizationHistory (1:M as original)
11. ResumeVersion → OptimizationHistory (1:M as optimized)

### Service Layer Classes:

- ATSAnalyzerService: Handles all ATS analysis logic
- ResumeOptimizationService: Handles resume optimization
- ExportService: Handles all export operations
- PDFParserService: Handles PDF parsing and import
- TemplateService: Handles template management
- AnalyticsService: Handles analytics and reporting

---

## HOW TO MAP THESE DIAGRAMS

### 1. DFD (Data Flow Diagram) Mapping

The DFD shows how data flows through your system. To map it to your codebase:

**Level 0 (Context):**
- Maps to the entire Django project
- User interactions → HTTP requests
- System outputs → HTTP responses

**Level 1 (Main Processes):**
- Process 1.0 (Authentication) → `apps/authentication/views.py`
- Process 2.0 (Resume Management) → `apps/resumes/views.py`
- Process 3.0 (ATS Analysis) → `apps/analyzer/views.py` + `apps/analyzer/services.py`
- Process 4.0 (Optimization) → `apps/resumes/views.py` (fix_* functions)
- Process 5.0 (Export) → `apps/resumes/views.py` (export_* functions)
- D1 (Database) → `apps/*/models.py` + `db.sqlite3`

**Level 2 (Detailed ATS Analysis):**
- Process 3.1-3.6 → `apps/analyzer/services.py` methods
- NLP operations → spaCy library integration

### 2. Table Specifications Mapping

Each table specification maps directly to Django models:

```
Table Specification          →    Django Model File
─────────────────────────────────────────────────────────────
User                        →    django.contrib.auth.models.User
Resume                      →    apps/resumes/models.py::Resume
PersonalInfo                →    apps/resumes/models.py::PersonalInfo
Experience                  →    apps/resumes/models.py::Experience
Education                   →    apps/resumes/models.py::Education
Skill                       →    apps/resumes/models.py::Skill
Project                     →    apps/resumes/models.py::Project
ResumeVersion               →    apps/resumes/models.py::ResumeVersion
UploadedResume              →    apps/resumes/models.py::UploadedResume
ResumeAnalysis              →    apps/resumes/models.py::ResumeAnalysis
OptimizationHistory         →    apps/resumes/models.py::OptimizationHistory
ResumeTemplate              →    apps/templates_mgmt/models.py::ResumeTemplate
TemplateCustomization       →    apps/templates_mgmt/models.py::TemplateCustomization
```

**To verify mapping:**
```bash
# View actual database schema
python manage.py sqlmigrate resumes 0001
python manage.py dbshell
.schema
```

### 3. ERD (Entity Relationship Diagram) Mapping

The ERD shows relationships between entities. Map to Django ORM:

**One-to-One Relationships:**
```python
# Resume → PersonalInfo (1:1)
class PersonalInfo(models.Model):
    resume = models.OneToOneField(Resume, on_delete=models.CASCADE, 
                                  related_name='personal_info')
```

**One-to-Many Relationships:**
```python
# User → Resume (1:M)
class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
                            related_name='resumes')

# Resume → Experience (1:M)
class Experience(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, 
                              related_name='experiences')
```

**To visualize your actual ERD:**
```bash
# Install django-extensions
pip install django-extensions pygraphviz

# Generate ERD
python manage.py graph_models -a -o erd.png
```

### 4. Activity Diagram Mapping

Activity diagrams map to user workflows and view functions:

**Resume Creation Flow:**
```
Activity Step                    →    Code Location
─────────────────────────────────────────────────────────────
Visit Website                   →    config/urls.py (root URL)
Register/Login                  →    apps/authentication/views.py
Dashboard                       →    apps/authentication/views.py::dashboard
Create Resume                   →    apps/resumes/views.py::resume_create
Choose Creation Mode            →    Template: templates/resumes/create.html
Build from Scratch              →    Form submission flow
Upload PDF                      →    apps/resumes/views.py::pdf_upload
Parse PDF                       →    apps/resumes/services.py::PDFParserService
Enter Sections                  →    Form wizard steps
Select Template                 →    apps/templates_mgmt/views.py
Preview Resume                  →    apps/resumes/views.py::resume_detail
Save Resume                     →    Database INSERT operations
```

**ATS Analysis Flow:**
```
Activity Step                    →    Code Location
─────────────────────────────────────────────────────────────
Select Resume                   →    apps/resumes/views.py::resume_list
Click Analyze                   →    apps/analyzer/views.py::analyze_resume
Paste Job Description           →    Template form
Submit for Analysis             →    POST request handler
Extract Keywords                →    apps/analyzer/services.py::extract_keywords
Perform Analysis                →    apps/analyzer/services.py::analyze_resume
Calculate Scores                →    apps/analyzer/services.py::calculate_*_score
Generate Suggestions            →    apps/analyzer/services.py::generate_suggestions
Display Results                 →    Template: templates/analyzer/results.html
```

### 5. Sequence Diagram Mapping

Sequence diagrams map to the request-response cycle:

**Resume Creation Sequence:**
```
Sequence Step                    →    Code Execution Path
─────────────────────────────────────────────────────────────
GET /resumes/create             →    config/urls.py → apps/resumes/urls.py
                                →    apps/resumes/views.py::resume_create (GET)
Render Form                     →    render(request, 'resumes/create.html')
POST /resumes/create            →    apps/resumes/views.py::resume_create (POST)
create_resume()                 →    Service layer method
INSERT Resume                   →    Resume.objects.create()
INSERT PersonalInfo             →    PersonalInfo.objects.create()
INSERT Experience               →    Experience.objects.create()
Redirect                        →    redirect('resume_detail', pk=resume.id)
```

**To trace actual execution:**
```python
# Add logging to views
import logging
logger = logging.getLogger(__name__)

def resume_create(request):
    logger.info(f"Resume create called by {request.user}")
    # ... rest of code
```

### 6. Class Diagram Mapping

The class diagram maps to your Django models and service classes:

**Model Classes:**
```
Class Diagram Class             →    Django Model
─────────────────────────────────────────────────────────────
User                           →    django.contrib.auth.models.User
Resume                         →    apps/resumes/models.py::Resume
PersonalInfo                   →    apps/resumes/models.py::PersonalInfo
Experience                     →    apps/resumes/models.py::Experience
Education                      →    apps/resumes/models.py::Education
Skill                          →    apps/resumes/models.py::Skill
Project                        →    apps/resumes/models.py::Project
ResumeVersion                  →    apps/resumes/models.py::ResumeVersion
ResumeAnalysis                 →    apps/resumes/models.py::ResumeAnalysis
OptimizationHistory            →    apps/resumes/models.py::OptimizationHistory
```

**Service Classes:**
```
Class Diagram Service           →    Implementation
─────────────────────────────────────────────────────────────
ATSAnalyzerService             →    apps/analyzer/services.py
ResumeOptimizationService      →    apps/resumes/services.py (optimization methods)
ExportService                  →    apps/resumes/views.py (export_* functions)
PDFParserService               →    apps/resumes/services.py (PDF parsing)
TemplateService                →    apps/templates_mgmt/views.py
AnalyticsService               →    apps/analytics/views.py
```

**Methods map to:**
- Model methods → Instance methods in model classes
- Service methods → Functions in service modules or view functions

---

## PRACTICAL MAPPING GUIDE

### Step 1: Identify Your Current Location

```bash
# List all apps
ls apps/

# List models in an app
python manage.py inspectdb

# List all URLs
python manage.py show_urls  # requires django-extensions
```

### Step 2: Map URLs to Views

```python
# config/urls.py shows main routing
# apps/*/urls.py shows app-specific routing

# Example mapping:
URL: /resumes/create/
→ config/urls.py: path('resumes/', include('apps.resumes.urls'))
→ apps/resumes/urls.py: path('create/', views.resume_create, name='resume_create')
→ apps/resumes/views.py: def resume_create(request)
```

### Step 3: Map Views to Models

```python
# In views.py, look for:
Resume.objects.create()      → Creates Resume instance
Resume.objects.get(pk=pk)    → Retrieves Resume instance
resume.experiences.all()     → Gets related Experience instances
```

### Step 4: Map Models to Database

```bash
# See actual database tables
python manage.py dbshell
.tables

# See table schema
.schema resumes_resume
.schema resumes_experience
```

### Step 5: Map Business Logic to Services

```python
# Look for service layer in:
apps/analyzer/services.py    → ATS analysis logic
apps/resumes/services.py     → Resume operations
apps/analytics/views.py      → Analytics calculations
```

### Step 6: Map Templates to Views

```python
# In views.py:
return render(request, 'resumes/detail.html', context)
                      ↓
# Maps to: templates/resumes/detail.html
```

---

## VERIFICATION CHECKLIST

Use this checklist to verify your diagrams match your implementation:

### DFD Verification:
- [ ] Each process box has corresponding view function
- [ ] Each data store has corresponding model
- [ ] Each data flow has corresponding variable/parameter

### ERD Verification:
- [ ] Each entity has corresponding Django model
- [ ] Each relationship has corresponding ForeignKey/OneToOneField
- [ ] Cardinality matches related_name usage

### Activity Diagram Verification:
- [ ] Each activity has corresponding view or function
- [ ] Decision points match if/else in code
- [ ] Flow matches URL routing

### Sequence Diagram Verification:
- [ ] Each message has corresponding function call
- [ ] Order matches actual execution order
- [ ] Return values match actual returns

### Class Diagram Verification:
- [ ] Each class has corresponding model or service
- [ ] Each attribute has corresponding field
- [ ] Each method has corresponding function

---

## TOOLS FOR AUTOMATIC MAPPING

### Generate ERD from Models:
```bash
pip install django-extensions pygraphviz
python manage.py graph_models -a -g -o erd.png
```

### Generate Class Diagram:
```bash
pip install pylint
pyreverse -o png -p NextGenCV apps/
```

### Visualize URL Routing:
```bash
pip install django-extensions
python manage.py show_urls
```

### Database Schema:
```bash
python manage.py sqlmigrate resumes 0001
python manage.py dbshell
.schema
```

---

## CONCLUSION

These diagrams provide a comprehensive view of your NextGenCV system architecture. Use them for:

1. **Documentation**: Share with team members and stakeholders
2. **Development**: Reference when adding new features
3. **Debugging**: Trace data flow and identify issues
4. **Onboarding**: Help new developers understand the system
5. **Academic**: Include in project reports and presentations

Each diagram type serves a specific purpose:
- **DFD**: Shows data movement
- **ERD**: Shows data structure
- **Activity**: Shows user workflows
- **Sequence**: Shows time-ordered interactions
- **Class**: Shows object structure and relationships

Keep these diagrams updated as your system evolves!
