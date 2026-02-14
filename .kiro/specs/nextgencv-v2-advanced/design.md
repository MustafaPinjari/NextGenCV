# Design Document - NextGenCV v2.0 Advanced Features

## Overview

NextGenCV v2.0 expands the existing ATS Resume Builder with advanced capabilities including PDF upload/parsing, AI-powered optimization, version control, and comprehensive analytics. The system maintains a Django monolithic architecture with SQLite database while introducing a robust service layer for business logic separation and future scalability.

### Key Design Principles

1. **Modular Architecture**: Clear separation of concerns across 10 distinct modules
2. **Service Layer Abstraction**: Business logic isolated from views for testability and reusability
3. **Non-Destructive Operations**: All modifications create new versions, preserving history
4. **Security First**: Comprehensive validation and sanitization at every layer
5. **Performance Optimized**: Efficient queries, caching, and async-ready design
6. **Future-Proof**: Architecture supports migration to PostgreSQL and microservices

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Presentation Layer                       │
│  (Django Templates + Bootstrap + JavaScript)                    │
├─────────────────────────────────────────────────────────────────┤
│                         Application Layer                        │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Auth Module  │  │ Resume Module│  │Version Module│         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Upload Module│  │ Fix Engine   │  │Analytics Mod │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │Template Mod  │  │ ATS Analyzer │  │ Admin Module │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
├─────────────────────────────────────────────────────────────────┤
│                         Service Layer                            │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │PDF Parser Svc│  │Keyword Extr  │  │Scoring Engine│         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │Resume Optim  │  │Version Mgmt  │  │Analytics Svc │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
├─────────────────────────────────────────────────────────────────┤
│                         Data Layer                               │
│  (Django ORM + SQLite)                                          │
│                                                                  │
│  Models: Resume, ResumeVersion, UploadedResume,                 │
│          OptimizationHistory, ResumeAnalysis, Template          │
└─────────────────────────────────────────────────────────────────┘
```

### Request Flow Architecture

```
User Request
    ↓
URL Router
    ↓
View Layer (Authorization Check)
    ↓
Service Layer (Business Logic)
    ↓
Data Layer (ORM)
    ↓
Database (SQLite)
    ↓
Service Layer (Data Processing)
    ↓
View Layer (Context Preparation)
    ↓
Template Rendering
    ↓
HTTP Response
```

## Module Architecture


### Module 1: Resume Versioning System

**Purpose**: Track and manage multiple versions of resumes with full history and comparison capabilities.

**Components**:
- `ResumeVersionService`: Handles version creation, retrieval, and restoration
- `VersionComparisonService`: Generates diff views between versions
- Views: `version_list`, `version_detail`, `version_compare`, `version_restore`
- Templates: `version_list.html`, `version_compare.html`

**Data Flow**:
```
Resume Modification → Auto-create Version → Store Metadata → Update Version Number
Version Selection → Load Historical Data → Display Read-Only View
Compare Request → Load Two Versions → Generate Diff → Highlight Changes
Restore Request → Copy Historical Data → Create New Version → Redirect to Edit
```

**Models**:
```python
class ResumeVersion:
    id: AutoField (PK)
    resume: ForeignKey(Resume)
    version_number: IntegerField
    created_at: DateTimeField
    modification_type: CharField  # 'manual', 'optimized', 'restored'
    ats_score: FloatField
    snapshot_data: JSONField  # Complete resume state
    user_notes: TextField
```

**Key Algorithms**:
- **Version Diff Algorithm**: Compare JSON snapshots field-by-field, categorize changes as additions/deletions/modifications
- **Version Numbering**: Auto-increment based on max version for resume
- **Snapshot Creation**: Serialize complete resume state including all sections


### Module 2: PDF Upload and Parsing System

**Purpose**: Extract and structure resume data from uploaded PDF files.

**Components**:
- `PDFParserService`: Extracts text from PDF using PyPDF2 or pdfplumber
- `SectionParserService`: Identifies and extracts resume sections using NLP
- `ResumeStructuringService`: Creates structured Resume objects from parsed data
- Views: `pdf_upload`, `pdf_parse_review`, `pdf_import_confirm`
- Templates: `pdf_upload.html`, `parse_review.html`

**Data Flow**:
```
PDF Upload → Validate File → Extract Text → Clean/Normalize Text
    ↓
Identify Sections → Parse Each Section → Extract Entities
    ↓
Create Structured Data → Display for Review → User Confirms/Edits
    ↓
Save to Database → Create Resume Object → Redirect to Resume Detail
```

**Models**:
```python
class UploadedResume:
    id: AutoField (PK)
    user: ForeignKey(User)
    original_filename: CharField
    file_path: FileField
    uploaded_at: DateTimeField
    file_size: IntegerField
    extracted_text: TextField
    parsing_confidence: FloatField
    parsed_data: JSONField
    status: CharField  # 'uploaded', 'parsing', 'parsed', 'imported', 'failed'
    error_message: TextField
```

**Key Algorithms**:

**Text Extraction**:
```python
def extract_text_from_pdf(pdf_file):
    # Use pdfplumber for better text extraction
    with pdfplumber.open(pdf_file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return clean_text(text)
```

**Section Identification**:
```python
def identify_sections(text):
    sections = {}
    # Pattern matching for common section headers
    patterns = {
        'experience': r'(work experience|professional experience|employment)',
        'education': r'(education|academic background)',
        'skills': r'(skills|technical skills|core competencies)',
        'projects': r'(projects|portfolio)'
    }
    # Use regex + NLP to identify section boundaries
    # Return dict with section names and content
    return sections
```

**Entity Extraction**:
```python
def extract_experience_entries(text):
    # Use spaCy NER to identify:
    # - Company names (ORG entities)
    # - Dates (DATE entities)
    # - Job titles (pattern matching)
    # - Bullet points (line-based parsing)
    return experiences
```


### Module 3: Advanced ATS Scoring Engine

**Purpose**: Provide comprehensive, multi-factor ATS compatibility scoring.

**Components**:
- `ScoringEngineService`: Calculates weighted composite scores
- `KeywordExtractorService`: Extracts and weights keywords using NLP
- `ActionVerbAnalyzerService`: Evaluates strength of action verbs
- `QuantificationDetectorService`: Identifies measurable achievements
- Views: `score_detail`, `score_history`
- Templates: `score_breakdown.html`, `score_trends.html`

**Data Flow**:
```
Resume + Job Description → Extract Keywords → Calculate Match %
    ↓
Analyze Skills → Weight by Relevance → Calculate Skill Score
    ↓
Check Sections → Calculate Completeness → Section Score
    ↓
Analyze Experience → Evaluate Impact → Experience Score
    ↓
Detect Quantification → Count Metrics → Quantification Score
    ↓
Analyze Action Verbs → Evaluate Strength → Action Verb Score
    ↓
Apply Weights → Calculate Composite → Store Score
```

**Models**:
```python
class ResumeAnalysis:
    id: AutoField (PK)
    resume: ForeignKey(Resume)
    job_description: TextField
    analysis_timestamp: DateTimeField
    
    # Component Scores
    keyword_match_score: FloatField
    skill_relevance_score: FloatField
    section_completeness_score: FloatField
    experience_impact_score: FloatField
    quantification_score: FloatField
    action_verb_score: FloatField
    
    # Composite Score
    final_score: FloatField
    
    # Detailed Analysis
    matched_keywords: JSONField
    missing_keywords: JSONField
    weak_action_verbs: JSONField
    missing_quantifications: JSONField
    suggestions: JSONField
```

**Scoring Algorithm**:

```python
def calculate_ats_score(resume, job_description):
    # Component 1: Keyword Match (30%)
    resume_keywords = extract_keywords(resume.get_full_text())
    jd_keywords = extract_keywords(job_description)
    keyword_score = len(resume_keywords & jd_keywords) / len(jd_keywords) * 100
    
    # Component 2: Skill Relevance (20%)
    skill_score = calculate_skill_relevance(resume.skills, jd_keywords)
    
    # Component 3: Section Completeness (15%)
    completeness_score = calculate_section_completeness(resume)
    
    # Component 4: Experience Impact (15%)
    impact_score = calculate_experience_impact(resume.experiences)
    
    # Component 5: Quantification (10%)
    quant_score = calculate_quantification_score(resume.experiences)
    
    # Component 6: Action Verb Strength (10%)
    verb_score = calculate_action_verb_score(resume.experiences)
    
    # Weighted Composite
    final_score = (
        keyword_score * 0.30 +
        skill_score * 0.20 +
        completeness_score * 0.15 +
        impact_score * 0.15 +
        quant_score * 0.10 +
        verb_score * 0.10
    )
    
    return {
        'final_score': final_score,
        'keyword_match_score': keyword_score,
        'skill_relevance_score': skill_score,
        'section_completeness_score': completeness_score,
        'experience_impact_score': impact_score,
        'quantification_score': quant_score,
        'action_verb_score': verb_score
    }
```

**Keyword Extraction with NLP**:
```python
def extract_keywords(text):
    # Use spaCy for NLP processing
    doc = nlp(text)
    
    # Extract nouns, proper nouns, and technical terms
    keywords = set()
    for token in doc:
        if token.pos_ in ['NOUN', 'PROPN'] and len(token.text) > 2:
            keywords.add(token.lemma_.lower())
    
    # Extract noun phrases
    for chunk in doc.noun_chunks:
        if len(chunk.text.split()) <= 3:  # Max 3-word phrases
            keywords.add(chunk.text.lower())
    
    # Remove stop words
    keywords = keywords - STOP_WORDS
    
    return keywords
```


### Module 4: Auto Resume Fix Engine

**Purpose**: Automatically optimize resumes using AI-powered analysis and rewriting.

**Components**:
- `ResumeOptimizerService`: Orchestrates optimization process
- `BulletPointRewriterService`: Improves achievement statements
- `KeywordInjectorService`: Naturally inserts missing keywords
- `QuantificationSuggesterService`: Suggests metrics for achievements
- `FormattingStandardizerService`: Fixes ATS-unfriendly formatting
- Views: `fix_resume`, `fix_preview`, `fix_accept`
- Templates: `fix_comparison.html`, `fix_suggestions.html`

**Data Flow**:
```
User Clicks "Fix Resume" → Load Resume + Job Description
    ↓
Analyze Current State → Identify Weaknesses
    ↓
Rewrite Bullet Points → Insert Keywords → Add Quantification
    ↓
Standardize Formatting → Generate Suggestions
    ↓
Create Optimized Version → Calculate New Score
    ↓
Display Side-by-Side Comparison → User Reviews Changes
    ↓
User Accepts → Create New Resume Version → Store Optimization History
```

**Models**:
```python
class OptimizationHistory:
    id: AutoField (PK)
    resume: ForeignKey(Resume)
    original_version: ForeignKey(ResumeVersion)
    optimized_version: ForeignKey(ResumeVersion)
    job_description: TextField
    optimization_timestamp: DateTimeField
    
    # Scores
    original_score: FloatField
    optimized_score: FloatField
    improvement_delta: FloatField
    
    # Changes Made
    changes_summary: JSONField  # {type: count}
    detailed_changes: JSONField  # [{section, field, old, new, reason}]
    
    # User Actions
    accepted_changes: JSONField
    rejected_changes: JSONField
    user_notes: TextField
```

**Optimization Algorithms**:

**1. Bullet Point Rewriting**:
```python
STRONG_ACTION_VERBS = [
    'achieved', 'accelerated', 'accomplished', 'delivered', 'developed',
    'engineered', 'established', 'executed', 'generated', 'implemented',
    'improved', 'increased', 'launched', 'led', 'optimized', 'reduced',
    'spearheaded', 'streamlined', 'transformed'
]

WEAK_VERBS = ['did', 'made', 'worked', 'helped', 'responsible for']

def rewrite_bullet_point(bullet, context):
    # Identify weak verb
    for weak in WEAK_VERBS:
        if bullet.lower().startswith(weak):
            # Replace with strong verb based on context
            strong_verb = select_strong_verb(bullet, context)
            bullet = bullet.replace(weak, strong_verb, 1)
    
    # Ensure starts with action verb
    if not starts_with_action_verb(bullet):
        bullet = add_action_verb(bullet)
    
    # Add quantification if missing
    if not has_quantification(bullet):
        bullet = suggest_quantification(bullet)
    
    return bullet

def select_strong_verb(bullet, context):
    # Use keyword matching to select appropriate verb
    if 'team' in bullet.lower():
        return random.choice(['led', 'managed', 'coordinated'])
    elif 'system' in bullet.lower() or 'application' in bullet.lower():
        return random.choice(['developed', 'engineered', 'built'])
    elif 'process' in bullet.lower():
        return random.choice(['optimized', 'streamlined', 'improved'])
    else:
        return random.choice(STRONG_ACTION_VERBS)
```

**2. Keyword Injection**:
```python
def inject_keywords(resume, missing_keywords, job_description):
    changes = []
    
    # Prioritize keywords by frequency in JD
    keyword_freq = calculate_keyword_frequency(job_description)
    sorted_keywords = sorted(missing_keywords, 
                            key=lambda k: keyword_freq.get(k, 0), 
                            reverse=True)
    
    # Inject top N keywords
    for keyword in sorted_keywords[:10]:
        # Find best location for keyword
        location = find_best_injection_point(resume, keyword)
        
        if location:
            # Inject naturally
            new_text = inject_keyword_naturally(location['text'], keyword)
            changes.append({
                'type': 'keyword_injection',
                'keyword': keyword,
                'location': location['section'],
                'old_text': location['text'],
                'new_text': new_text
            })
    
    return changes

def inject_keyword_naturally(text, keyword):
    # Use templates to inject keyword naturally
    templates = [
        f"Utilized {keyword} to enhance...",
        f"Leveraged {keyword} for...",
        f"Implemented {keyword}-based solutions...",
        f"Expertise in {keyword}..."
    ]
    
    # Select template based on context
    template = select_template(text, keyword)
    return template
```

**3. Quantification Suggestion**:
```python
def suggest_quantification(bullet):
    # Identify achievement type
    achievement_type = classify_achievement(bullet)
    
    # Suggest appropriate metrics
    suggestions = {
        'performance': ['X% faster', 'X% improvement', 'reduced by X%'],
        'scale': ['X users', 'X transactions', 'X requests/day'],
        'team': ['team of X', 'X developers', 'X stakeholders'],
        'financial': ['$X revenue', '$X savings', 'X% ROI'],
        'time': ['X months', 'X weeks', 'delivered X days early']
    }
    
    return suggestions.get(achievement_type, ['[add metric]'])
```

**4. Formatting Standardization**:
```python
def standardize_formatting(resume):
    changes = []
    
    # Standardize section headings
    section_mapping = {
        'work history': 'Work Experience',
        'employment': 'Work Experience',
        'jobs': 'Work Experience',
        'schooling': 'Education',
        'degrees': 'Education',
        'technical skills': 'Skills',
        'competencies': 'Skills'
    }
    
    # Standardize date formats
    # MM/YYYY → Month YYYY
    # YYYY-MM → Month YYYY
    
    # Remove problematic formatting
    # - Tables
    # - Text boxes
    # - Headers/footers
    # - Multiple columns
    
    return changes
```


### Module 5: Analytics and Dashboard System

**Purpose**: Provide comprehensive analytics and insights on resume performance.

**Components**:
- `AnalyticsService`: Aggregates and computes analytics metrics
- `TrendAnalysisService`: Calculates trends over time
- `HealthScoreService`: Computes overall resume health
- Views: `analytics_dashboard`, `score_trends`, `improvement_report`
- Templates: `dashboard.html`, `analytics.html`, `trends.html`

**Data Flow**:
```
Dashboard Request → Load User Resumes → Calculate Metrics
    ↓
Aggregate Scores → Calculate Trends → Identify Patterns
    ↓
Compute Health Metrics → Generate Recommendations
    ↓
Prepare Chart Data → Render Dashboard
```

**Dashboard Metrics**:

1. **Resume Health Meter** (0-100):
```python
def calculate_resume_health(resume):
    health_score = 0
    
    # Section completeness (40 points)
    sections = ['personal_info', 'experiences', 'education', 'skills']
    completed = sum(1 for s in sections if has_content(resume, s))
    health_score += (completed / len(sections)) * 40
    
    # Contact info completeness (15 points)
    contact_fields = ['email', 'phone', 'location']
    completed_contact = sum(1 for f in contact_fields 
                           if getattr(resume.personal_info, f, None))
    health_score += (completed_contact / len(contact_fields)) * 15
    
    # Quantified achievements (20 points)
    total_bullets = count_bullet_points(resume.experiences)
    quantified = count_quantified_bullets(resume.experiences)
    if total_bullets > 0:
        health_score += (quantified / total_bullets) * 20
    
    # Action verb usage (15 points)
    strong_verbs = count_strong_action_verbs(resume.experiences)
    if total_bullets > 0:
        health_score += (strong_verbs / total_bullets) * 15
    
    # ATS-friendly formatting (10 points)
    if is_ats_friendly_format(resume):
        health_score += 10
    
    return health_score
```

2. **Score Trend Analysis**:
```python
def calculate_score_trends(user):
    analyses = ResumeAnalysis.objects.filter(
        resume__user=user
    ).order_by('analysis_timestamp')
    
    # Calculate moving average
    window_size = 5
    scores = [a.final_score for a in analyses]
    moving_avg = calculate_moving_average(scores, window_size)
    
    # Calculate improvement rate
    if len(scores) >= 2:
        improvement_rate = (scores[-1] - scores[0]) / len(scores)
    else:
        improvement_rate = 0
    
    return {
        'scores': scores,
        'moving_average': moving_avg,
        'improvement_rate': improvement_rate,
        'trend': 'improving' if improvement_rate > 0 else 'declining'
    }
```

3. **Top Missing Keywords**:
```python
def get_top_missing_keywords(user, limit=10):
    analyses = ResumeAnalysis.objects.filter(resume__user=user)
    
    # Aggregate missing keywords across all analyses
    keyword_counts = {}
    for analysis in analyses:
        for keyword in analysis.missing_keywords:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
    
    # Sort by frequency
    top_keywords = sorted(keyword_counts.items(), 
                         key=lambda x: x[1], 
                         reverse=True)[:limit]
    
    return top_keywords
```

**Dashboard UI Components**:

```html
<!-- Resume Health Meter -->
<div class="health-meter">
    <h3>Resume Health</h3>
    <div class="progress" style="height: 30px;">
        <div class="progress-bar" 
             style="width: {{ health_score }}%"
             class="{% if health_score >= 80 %}bg-success
                    {% elif health_score >= 60 %}bg-warning
                    {% else %}bg-danger{% endif %}">
            {{ health_score }}%
        </div>
    </div>
</div>

<!-- Score Trend Chart -->
<div class="score-trend">
    <h3>ATS Score Trend</h3>
    <canvas id="scoreTrendChart"></canvas>
</div>

<!-- Missing Keywords -->
<div class="missing-keywords">
    <h3>Top Missing Keywords</h3>
    <ul>
        {% for keyword, count in top_missing_keywords %}
        <li>
            <span class="keyword">{{ keyword }}</span>
            <span class="badge">{{ count }} analyses</span>
        </li>
        {% endfor %}
    </ul>
</div>
```


### Module 6: Template Management System

**Purpose**: Manage multiple resume templates with customization options.

**Components**:
- `TemplateService`: CRUD operations for templates
- `TemplateCustomizationService`: Handles user customizations
- `TemplatePreviewService`: Generates previews with sample data
- Views: `template_list`, `template_preview`, `template_customize`
- Templates: `template_gallery.html`, `template_preview.html`

**Models**:
```python
class ResumeTemplate:
    id: AutoField (PK)
    name: CharField
    description: TextField
    template_file: CharField  # Path to HTML template
    thumbnail: ImageField
    is_active: BooleanField
    is_default: BooleanField
    created_at: DateTimeField
    updated_at: DateTimeField
    usage_count: IntegerField
    
    # Customization Options
    supports_color_customization: BooleanField
    supports_font_customization: BooleanField
    available_colors: JSONField
    available_fonts: JSONField

class TemplateCustomization:
    id: AutoField (PK)
    resume: ForeignKey(Resume)
    template: ForeignKey(ResumeTemplate)
    color_scheme: CharField
    font_family: CharField
    custom_css: TextField
    created_at: DateTimeField
```

**Template Structure**:
```
templates/
├── resumes/
│   ├── professional.html
│   ├── modern.html
│   ├── classic.html
│   ├── creative.html
│   └── minimal.html
└── template_base.html
```

**Customization System**:
```python
def apply_customization(template, customization):
    # Load base template
    base_html = load_template(template.template_file)
    
    # Apply color scheme
    if customization.color_scheme:
        base_html = apply_color_scheme(base_html, customization.color_scheme)
    
    # Apply font family
    if customization.font_family:
        base_html = apply_font_family(base_html, customization.font_family)
    
    # Apply custom CSS
    if customization.custom_css:
        base_html = inject_custom_css(base_html, customization.custom_css)
    
    return base_html
```


## Database Schema

### New Tables

```sql
-- Resume Versioning
CREATE TABLE resume_version (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id INTEGER NOT NULL,
    version_number INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL,
    modification_type VARCHAR(20) NOT NULL,
    ats_score FLOAT,
    snapshot_data TEXT NOT NULL,  -- JSON
    user_notes TEXT,
    FOREIGN KEY (resume_id) REFERENCES resume(id) ON DELETE CASCADE,
    UNIQUE (resume_id, version_number)
);

CREATE INDEX idx_resume_version_resume ON resume_version(resume_id, created_at DESC);

-- Uploaded Resumes
CREATE TABLE uploaded_resume (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    uploaded_at TIMESTAMP NOT NULL,
    file_size INTEGER NOT NULL,
    extracted_text TEXT,
    parsing_confidence FLOAT,
    parsed_data TEXT,  -- JSON
    status VARCHAR(20) NOT NULL,
    error_message TEXT,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
);

CREATE INDEX idx_uploaded_resume_user ON uploaded_resume(user_id, uploaded_at DESC);

-- Resume Analysis
CREATE TABLE resume_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id INTEGER NOT NULL,
    job_description TEXT NOT NULL,
    analysis_timestamp TIMESTAMP NOT NULL,
    
    -- Component Scores
    keyword_match_score FLOAT NOT NULL,
    skill_relevance_score FLOAT NOT NULL,
    section_completeness_score FLOAT NOT NULL,
    experience_impact_score FLOAT NOT NULL,
    quantification_score FLOAT NOT NULL,
    action_verb_score FLOAT NOT NULL,
    
    -- Composite Score
    final_score FLOAT NOT NULL,
    
    -- Detailed Analysis (JSON)
    matched_keywords TEXT,
    missing_keywords TEXT,
    weak_action_verbs TEXT,
    missing_quantifications TEXT,
    suggestions TEXT,
    
    FOREIGN KEY (resume_id) REFERENCES resume(id) ON DELETE CASCADE
);

CREATE INDEX idx_resume_analysis_resume ON resume_analysis(resume_id, analysis_timestamp DESC);

-- Optimization History
CREATE TABLE optimization_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id INTEGER NOT NULL,
    original_version_id INTEGER NOT NULL,
    optimized_version_id INTEGER,
    job_description TEXT NOT NULL,
    optimization_timestamp TIMESTAMP NOT NULL,
    
    -- Scores
    original_score FLOAT NOT NULL,
    optimized_score FLOAT,
    improvement_delta FLOAT,
    
    -- Changes (JSON)
    changes_summary TEXT,
    detailed_changes TEXT,
    accepted_changes TEXT,
    rejected_changes TEXT,
    user_notes TEXT,
    
    FOREIGN KEY (resume_id) REFERENCES resume(id) ON DELETE CASCADE,
    FOREIGN KEY (original_version_id) REFERENCES resume_version(id),
    FOREIGN KEY (optimized_version_id) REFERENCES resume_version(id)
);

CREATE INDEX idx_optimization_history_resume ON optimization_history(resume_id, optimization_timestamp DESC);

-- Resume Templates
CREATE TABLE resume_template (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    template_file VARCHAR(200) NOT NULL,
    thumbnail VARCHAR(200),
    is_active BOOLEAN NOT NULL DEFAULT 1,
    is_default BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    usage_count INTEGER NOT NULL DEFAULT 0,
    
    -- Customization Options (JSON)
    supports_color_customization BOOLEAN NOT NULL DEFAULT 1,
    supports_font_customization BOOLEAN NOT NULL DEFAULT 1,
    available_colors TEXT,
    available_fonts TEXT
);

-- Template Customizations
CREATE TABLE template_customization (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id INTEGER NOT NULL,
    template_id INTEGER NOT NULL,
    color_scheme VARCHAR(50),
    font_family VARCHAR(100),
    custom_css TEXT,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (resume_id) REFERENCES resume(id) ON DELETE CASCADE,
    FOREIGN KEY (template_id) REFERENCES resume_template(id),
    UNIQUE (resume_id)
);
```

### Modified Tables

```sql
-- Add fields to existing Resume table
ALTER TABLE resume ADD COLUMN current_version_number INTEGER DEFAULT 1;
ALTER TABLE resume ADD COLUMN last_analyzed_at TIMESTAMP;
ALTER TABLE resume ADD COLUMN last_optimized_at TIMESTAMP;
```

### Entity Relationship Diagram

```
User (1) ──────< (M) Resume
                      │
                      ├──── (1:M) ResumeVersion
                      ├──── (1:M) ResumeAnalysis
                      ├──── (1:M) OptimizationHistory
                      ├──── (1:1) TemplateCustomization
                      │
                      ├──── (1:1) PersonalInfo
                      ├──── (1:M) Experience
                      ├──── (1:M) Education
                      ├──── (1:M) Skill
                      └──── (1:M) Project

User (1) ──────< (M) UploadedResume

ResumeTemplate (1) ──────< (M) TemplateCustomization
ResumeTemplate (1) ──────< (M) Resume

ResumeVersion (1) ──────< (M) OptimizationHistory (as original)
ResumeVersion (1) ──────< (M) OptimizationHistory (as optimized)
```


## Service Layer Architecture

### Directory Structure

```
apps/
├── analyzer/
│   ├── services/
│   │   ├── __init__.py
│   │   ├── keyword_extractor.py
│   │   ├── scoring_engine.py
│   │   ├── action_verb_analyzer.py
│   │   └── quantification_detector.py
│   └── utils/
│       ├── nlp_utils.py
│       └── text_processing.py
│
├── resumes/
│   ├── services/
│   │   ├── __init__.py
│   │   ├── resume_service.py
│   │   ├── version_service.py
│   │   ├── pdf_parser.py
│   │   ├── section_parser.py
│   │   └── resume_optimizer.py
│   └── utils/
│       ├── file_validators.py
│       └── text_cleaners.py
│
├── analytics/
│   ├── services/
│   │   ├── __init__.py
│   │   ├── analytics_service.py
│   │   ├── trend_analysis.py
│   │   └── health_score.py
│
└── templates_mgmt/
    ├── services/
    │   ├── __init__.py
    │   ├── template_service.py
    │   └── customization_service.py
```

### Service Layer Interfaces

**KeywordExtractorService**:
```python
class KeywordExtractorService:
    @staticmethod
    def extract_keywords(text: str, min_length: int = 3) -> Set[str]:
        """Extract keywords using NLP"""
        pass
    
    @staticmethod
    def calculate_keyword_frequency(text: str) -> Dict[str, int]:
        """Calculate frequency of each keyword"""
        pass
    
    @staticmethod
    def weight_keywords_by_importance(keywords: Set[str], context: str) -> Dict[str, float]:
        """Assign importance weights to keywords"""
        pass
```

**ScoringEngineService**:
```python
class ScoringEngineService:
    @staticmethod
    def calculate_ats_score(resume: Resume, job_description: str) -> Dict:
        """Calculate comprehensive ATS score"""
        pass
    
    @staticmethod
    def calculate_keyword_match_score(resume_keywords: Set, jd_keywords: Set) -> float:
        """Calculate keyword match percentage"""
        pass
    
    @staticmethod
    def calculate_skill_relevance_score(skills: QuerySet, jd_keywords: Set) -> float:
        """Calculate skill relevance"""
        pass
    
    @staticmethod
    def calculate_section_completeness_score(resume: Resume) -> float:
        """Calculate section completeness"""
        pass
```

**ResumeOptimizerService**:
```python
class ResumeOptimizerService:
    @staticmethod
    def optimize_resume(resume: Resume, job_description: str) -> Dict:
        """Run full optimization pipeline"""
        pass
    
    @staticmethod
    def rewrite_bullet_points(experiences: QuerySet, context: str) -> List[Dict]:
        """Improve bullet points with strong action verbs"""
        pass
    
    @staticmethod
    def inject_keywords(resume: Resume, missing_keywords: Set) -> List[Dict]:
        """Naturally inject missing keywords"""
        pass
    
    @staticmethod
    def suggest_quantifications(experiences: QuerySet) -> List[Dict]:
        """Suggest metrics for achievements"""
        pass
```

**PDFParserService**:
```python
class PDFParserService:
    @staticmethod
    def extract_text_from_pdf(pdf_file: File) -> str:
        """Extract text from PDF"""
        pass
    
    @staticmethod
    def clean_extracted_text(text: str) -> str:
        """Clean and normalize extracted text"""
        pass
    
    @staticmethod
    def calculate_parsing_confidence(text: str, parsed_data: Dict) -> float:
        """Calculate confidence in parsing accuracy"""
        pass
```

**SectionParserService**:
```python
class SectionParserService:
    @staticmethod
    def identify_sections(text: str) -> Dict[str, str]:
        """Identify resume sections"""
        pass
    
    @staticmethod
    def parse_personal_info(text: str) -> Dict:
        """Extract personal information"""
        pass
    
    @staticmethod
    def parse_experiences(text: str) -> List[Dict]:
        """Extract work experience entries"""
        pass
    
    @staticmethod
    def parse_education(text: str) -> List[Dict]:
        """Extract education entries"""
        pass
    
    @staticmethod
    def parse_skills(text: str) -> List[Dict]:
        """Extract skills"""
        pass
```

**VersionService**:
```python
class VersionService:
    @staticmethod
    def create_version(resume: Resume, modification_type: str) -> ResumeVersion:
        """Create new resume version"""
        pass
    
    @staticmethod
    def get_version_history(resume: Resume) -> QuerySet:
        """Get all versions for resume"""
        pass
    
    @staticmethod
    def compare_versions(version1: ResumeVersion, version2: ResumeVersion) -> Dict:
        """Generate diff between versions"""
        pass
    
    @staticmethod
    def restore_version(version: ResumeVersion) -> Resume:
        """Restore resume to specific version"""
        pass
```

**AnalyticsService**:
```python
class AnalyticsService:
    @staticmethod
    def calculate_resume_health(resume: Resume) -> float:
        """Calculate overall resume health score"""
        pass
    
    @staticmethod
    def get_score_trends(user: User) -> Dict:
        """Calculate score trends over time"""
        pass
    
    @staticmethod
    def get_top_missing_keywords(user: User, limit: int = 10) -> List[Tuple]:
        """Get most frequently missing keywords"""
        pass
    
    @staticmethod
    def generate_improvement_report(user: User) -> Dict:
        """Generate comprehensive improvement report"""
        pass
```


## API/View Flow Specifications

### PDF Upload Flow

```
GET /resumes/upload/
    → Display upload form
    → Template: pdf_upload.html

POST /resumes/upload/
    → Validate file (type, size)
    → Save to UploadedResume
    → Extract text (PDFParserService)
    → Parse sections (SectionParserService)
    → Redirect to /resumes/upload/<id>/review/

GET /resumes/upload/<id>/review/
    → Load UploadedResume
    → Display parsed data for review
    → Allow inline editing
    → Template: parse_review.html

POST /resumes/upload/<id>/confirm/
    → Create Resume from parsed data
    → Create initial ResumeVersion
    → Run initial ATS analysis
    → Redirect to /resumes/<resume_id>/
```

### Resume Optimization Flow

```
GET /resumes/<id>/fix/
    → Load resume
    → Display job description form
    → Template: fix_resume.html

POST /resumes/<id>/fix/
    → Load resume + job description
    → Run optimization (ResumeOptimizerService)
    → Calculate new score
    → Store in session
    → Redirect to /resumes/<id>/fix/preview/

GET /resumes/<id>/fix/preview/
    → Load optimization results from session
    → Display side-by-side comparison
    → Show improvement delta
    → Template: fix_comparison.html

POST /resumes/<id>/fix/accept/
    → Create new ResumeVersion with optimized data
    → Create OptimizationHistory record
    → Clear session
    → Redirect to /resumes/<id>/

POST /resumes/<id>/fix/reject/
    → Clear session
    → Redirect to /resumes/<id>/
```

### Version Management Flow

```
GET /resumes/<id>/versions/
    → Load all versions for resume
    → Display version history
    → Template: version_list.html

GET /resumes/<id>/versions/<version_id>/
    → Load specific version
    → Display read-only view
    → Template: version_detail.html

GET /resumes/<id>/versions/compare/?v1=<id1>&v2=<id2>
    → Load two versions
    → Generate diff (VersionService)
    → Display side-by-side comparison
    → Template: version_compare.html

POST /resumes/<id>/versions/<version_id>/restore/
    → Create new version from historical version
    → Redirect to /resumes/<id>/edit/
```

### Analytics Dashboard Flow

```
GET /analytics/dashboard/
    → Calculate resume health (AnalyticsService)
    → Get score trends
    → Get top missing keywords
    → Prepare chart data
    → Template: analytics_dashboard.html

GET /analytics/trends/
    → Load all analyses for user
    → Calculate detailed trends
    → Generate charts
    → Template: analytics_trends.html

GET /analytics/improvement-report/
    → Generate comprehensive report
    → Show optimization history
    → Display recommendations
    → Template: improvement_report.html
```

### Template Management Flow

```
GET /templates/
    → Load all active templates
    → Display gallery
    → Template: template_gallery.html

GET /templates/<id>/preview/
    → Load template
    → Generate preview with sample data
    → Template: template_preview.html

POST /resumes/<id>/template/customize/
    → Save customization preferences
    → Apply to resume
    → Redirect to /resumes/<id>/
```


## Security Design

### File Upload Security

**Validation Pipeline**:
```python
def validate_uploaded_file(file):
    # 1. Check file extension
    if not file.name.endswith('.pdf'):
        raise ValidationError("Only PDF files are allowed")
    
    # 2. Check MIME type
    if file.content_type != 'application/pdf':
        raise ValidationError("Invalid file type")
    
    # 3. Check file size (10MB limit)
    if file.size > 10 * 1024 * 1024:
        raise ValidationError("File size exceeds 10MB limit")
    
    # 4. Scan for embedded scripts
    if has_embedded_scripts(file):
        raise ValidationError("File contains potentially malicious content")
    
    return True
```

**Secure File Storage**:
```python
def save_uploaded_file(file, user):
    # Generate secure random filename
    ext = file.name.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    
    # Store outside web root
    upload_path = os.path.join(settings.MEDIA_ROOT, 'uploads', str(user.id))
    os.makedirs(upload_path, exist_ok=True)
    
    file_path = os.path.join(upload_path, filename)
    
    # Save file
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    
    return file_path
```

**Text Sanitization**:
```python
def sanitize_extracted_text(text):
    # Remove potential XSS vectors
    text = bleach.clean(text, tags=[], strip=True)
    
    # Remove control characters
    text = ''.join(char for char in text if char.isprintable() or char.isspace())
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    return text
```

### Data Isolation

**Authorization Middleware**:
```python
def check_resume_ownership(user, resume_id):
    resume = get_object_or_404(Resume, id=resume_id)
    if resume.user != user:
        raise PermissionDenied("You do not have permission to access this resume")
    return resume
```

**Query Filtering**:
```python
# Always filter by user
resumes = Resume.objects.filter(user=request.user)
versions = ResumeVersion.objects.filter(resume__user=request.user)
analyses = ResumeAnalysis.objects.filter(resume__user=request.user)
```

### Input Validation

**Form Validation**:
```python
class JobDescriptionForm(forms.Form):
    job_description = forms.CharField(
        widget=forms.Textarea,
        max_length=10000,
        validators=[MinLengthValidator(50)]
    )
    
    def clean_job_description(self):
        jd = self.cleaned_data['job_description']
        # Sanitize input
        jd = bleach.clean(jd, tags=[], strip=True)
        return jd
```

## Performance Optimization

### Database Optimization

**Indexes**:
```python
class Meta:
    indexes = [
        models.Index(fields=['user', '-created_at']),
        models.Index(fields=['resume', '-analysis_timestamp']),
        models.Index(fields=['resume', '-version_number']),
    ]
```

**Query Optimization**:
```python
# Use select_related for foreign keys
resume = Resume.objects.select_related('personal_info').get(id=resume_id)

# Use prefetch_related for reverse foreign keys
resume = Resume.objects.prefetch_related(
    'experiences',
    'education',
    'skills',
    'projects',
    'versions'
).get(id=resume_id)
```

**Caching Strategy**:
```python
from django.core.cache import cache

def get_resume_health(resume_id):
    cache_key = f'resume_health_{resume_id}'
    health_score = cache.get(cache_key)
    
    if health_score is None:
        health_score = AnalyticsService.calculate_resume_health(resume_id)
        cache.set(cache_key, health_score, timeout=300)  # 5 minutes
    
    return health_score
```

### Async Processing Considerations

While the current system is synchronous, the architecture supports future async processing:

```python
# Future async implementation
async def optimize_resume_async(resume_id, job_description):
    # Long-running optimization
    result = await ResumeOptimizerService.optimize_resume(resume_id, job_description)
    return result

# Can be called with:
# result = await optimize_resume_async(resume_id, jd)
```

### File Processing Optimization

**Chunked File Reading**:
```python
def extract_text_from_large_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
            # Process in chunks to avoid memory issues
            if len(text) > 1000000:  # 1MB of text
                yield text
                text = ""
    if text:
        yield text
```

## Error Handling

### Error Categories

1. **Validation Errors**: User input errors
2. **Processing Errors**: PDF parsing, NLP failures
3. **System Errors**: Database, file system issues

### Error Handling Strategy

```python
def upload_and_parse_resume(request):
    try:
        # Validate file
        file = request.FILES['resume']
        validate_uploaded_file(file)
        
        # Save file
        uploaded_resume = UploadedResume.objects.create(
            user=request.user,
            original_filename=file.name,
            file_size=file.size
        )
        
        # Extract text
        try:
            text = PDFParserService.extract_text_from_pdf(file)
            uploaded_resume.extracted_text = text
            uploaded_resume.status = 'extracted'
            uploaded_resume.save()
        except Exception as e:
            uploaded_resume.status = 'failed'
            uploaded_resume.error_message = str(e)
            uploaded_resume.save()
            raise
        
        # Parse sections
        try:
            parsed_data = SectionParserService.parse_resume(text)
            uploaded_resume.parsed_data = parsed_data
            uploaded_resume.status = 'parsed'
            uploaded_resume.save()
        except Exception as e:
            uploaded_resume.status = 'failed'
            uploaded_resume.error_message = str(e)
            uploaded_resume.save()
            raise
        
        return uploaded_resume
        
    except ValidationError as e:
        messages.error(request, str(e))
        return None
    except Exception as e:
        logger.error(f"Resume upload failed: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred while processing your resume. Please try again.")
        return None
```

### User-Friendly Error Messages

```python
ERROR_MESSAGES = {
    'invalid_file_type': "Please upload a PDF file. Other file types are not supported.",
    'file_too_large': "Your file is too large. Please upload a file smaller than 10MB.",
    'parsing_failed': "We couldn't parse your resume. Please ensure it's a text-based PDF (not scanned).",
    'low_confidence': "We had trouble understanding your resume format. Please review the extracted data carefully.",
    'optimization_failed': "Resume optimization failed. Please try again or contact support.",
}
```


## Testing Strategy

### Unit Testing

**Service Layer Tests**:
```python
class KeywordExtractorServiceTest(TestCase):
    def test_extract_keywords_basic(self):
        text = "Python developer with Django experience"
        keywords = KeywordExtractorService.extract_keywords(text)
        self.assertIn('python', keywords)
        self.assertIn('django', keywords)
    
    def test_extract_keywords_removes_stop_words(self):
        text = "The developer worked with the team"
        keywords = KeywordExtractorService.extract_keywords(text)
        self.assertNotIn('the', keywords)
        self.assertNotIn('with', keywords)

class ScoringEngineServiceTest(TestCase):
    def test_calculate_keyword_match_score(self):
        resume_keywords = {'python', 'django', 'postgresql'}
        jd_keywords = {'python', 'django', 'react', 'postgresql'}
        score = ScoringEngineService.calculate_keyword_match_score(
            resume_keywords, jd_keywords
        )
        self.assertEqual(score, 75.0)  # 3/4 = 75%
```

### Integration Testing

**PDF Upload Flow Test**:
```python
class PDFUploadIntegrationTest(TestCase):
    def test_complete_upload_flow(self):
        # Create test PDF
        pdf_file = create_test_pdf()
        
        # Upload
        response = self.client.post('/resumes/upload/', {
            'resume': pdf_file
        })
        self.assertEqual(response.status_code, 302)
        
        # Check UploadedResume created
        uploaded = UploadedResume.objects.latest('id')
        self.assertEqual(uploaded.status, 'parsed')
        self.assertIsNotNone(uploaded.extracted_text)
        
        # Confirm import
        response = self.client.post(f'/resumes/upload/{uploaded.id}/confirm/')
        self.assertEqual(response.status_code, 302)
        
        # Check Resume created
        resume = Resume.objects.latest('id')
        self.assertIsNotNone(resume.personal_info)
```

### Property-Based Testing

**Optimization Properties**:
```python
from hypothesis import given, strategies as st

@given(st.text(min_size=10, max_size=1000))
def test_optimization_preserves_meaning(original_text):
    # Property: Optimization should not change core meaning
    optimized = ResumeOptimizerService.rewrite_bullet_point(original_text)
    
    # Extract key entities from both
    original_entities = extract_entities(original_text)
    optimized_entities = extract_entities(optimized)
    
    # Core entities should be preserved
    assert len(original_entities & optimized_entities) >= len(original_entities) * 0.8
```

## Future Scaling Roadmap

### Phase 1: Current Implementation (SQLite + Django)
- All features implemented synchronously
- SQLite database
- File storage on local filesystem
- Single server deployment

### Phase 2: PostgreSQL Migration
```python
# Database settings for PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nextgencv',
        'USER': 'nextgencv_user',
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

**Migration Steps**:
1. Update database settings
2. Run migrations: `python manage.py migrate`
3. Migrate data: `python manage.py dumpdata > data.json` → `python manage.py loaddata data.json`
4. Update indexes for PostgreSQL-specific optimizations

### Phase 3: Async Processing
```python
# Add Celery for background tasks
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Async tasks
@shared_task
def optimize_resume_task(resume_id, job_description):
    result = ResumeOptimizerService.optimize_resume(resume_id, job_description)
    return result

# Call async
task = optimize_resume_task.delay(resume_id, jd)
```

### Phase 4: Microservices Architecture
```
API Gateway
    ↓
┌─────────────┬─────────────┬─────────────┬─────────────┐
│   Auth      │   Resume    │   Parser    │  Analytics  │
│  Service    │   Service   │   Service   │   Service   │
└─────────────┴─────────────┴─────────────┴─────────────┘
       ↓              ↓             ↓             ↓
   PostgreSQL    PostgreSQL    MongoDB      TimescaleDB
```

**Service Boundaries**:
- **Auth Service**: User management, authentication
- **Resume Service**: Resume CRUD, versioning
- **Parser Service**: PDF parsing, NLP processing
- **Analytics Service**: Scoring, trends, recommendations

### Phase 5: Cloud Deployment
```
Load Balancer
    ↓
┌─────────────┬─────────────┬─────────────┐
│   Web       │   Web       │   Web       │
│  Server 1   │  Server 2   │  Server 3   │
└─────────────┴─────────────┴─────────────┘
       ↓              ↓             ↓
   RDS PostgreSQL    S3 Storage    ElastiCache Redis
```

**Cloud Services**:
- **Compute**: AWS EC2 or ECS
- **Database**: AWS RDS (PostgreSQL)
- **File Storage**: AWS S3
- **Cache**: AWS ElastiCache (Redis)
- **Queue**: AWS SQS
- **CDN**: AWS CloudFront

## Deployment Architecture

### Current Deployment (Single Server)

```
Nginx (Reverse Proxy)
    ↓
Gunicorn (WSGI Server)
    ↓
Django Application
    ↓
SQLite Database
```

**Configuration**:
```nginx
# nginx.conf
server {
    listen 80;
    server_name nextgencv.com;
    
    location /static/ {
        alias /var/www/nextgencv/staticfiles/;
    }
    
    location /media/ {
        alias /var/www/nextgencv/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# gunicorn.conf.py
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
timeout = 120
```

### Monitoring and Logging

**Logging Configuration**:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/nextgencv/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/nextgencv/error.log',
            'maxBytes': 10485760,
            'backupCount': 5,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
        },
        'apps': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
        },
    },
}
```

**Performance Monitoring**:
```python
# Add django-debug-toolbar for development
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

# Add django-silk for production profiling
INSTALLED_APPS += ['silk']
MIDDLEWARE += ['silk.middleware.SilkyMiddleware']
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Version Creation Atomicity
*For any* resume modification, creating a new version should be atomic—either the version is fully created with all metadata, or no version is created at all.
**Validates: Requirements 1.1**

### Property 2: Version Number Uniqueness
*For any* resume, version numbers should be unique and sequential within that resume's version history.
**Validates: Requirements 1.1, 1.6**

### Property 3: PDF Upload Validation
*For any* uploaded file, if it passes validation, it must be a valid PDF file under 10MB with no embedded scripts.
**Validates: Requirements 3.1, 3.2, 3.3, 15.1, 15.2, 15.3, 15.4**

### Property 4: Text Sanitization
*For any* extracted text from PDF, the sanitized output should contain no XSS vectors or control characters.
**Validates: Requirements 3.5, 15.7**

### Property 5: Section Parsing Completeness
*For any* successfully parsed resume, at least one section (personal info, experience, education, or skills) must be identified.
**Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**

### Property 6: Score Composition
*For any* ATS score calculation, the final score should equal the weighted sum of component scores and be between 0 and 100.
**Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7**

### Property 7: Optimization Non-Destructive
*For any* resume optimization, the original resume should remain unchanged and a new version should be created.
**Validates: Requirements 9.6, 9.7**

### Property 8: Keyword Injection Naturalness
*For any* keyword injection, the resulting text should maintain grammatical correctness and readability.
**Validates: Requirements 8.3**

### Property 9: Version Comparison Symmetry
*For any* two versions A and B, comparing A to B should show the inverse changes of comparing B to A.
**Validates: Requirements 2.1, 2.2, 2.3**

### Property 10: Data Isolation
*For any* user, they should only be able to access resumes, versions, and analyses that belong to them.
**Validates: Requirements 16.1, 16.2, 16.3, 16.4, 16.5**

### Property 11: Health Score Bounds
*For any* resume, the health score should be between 0 and 100 inclusive.
**Validates: Requirements 12.1, 12.2, 12.3, 12.4, 12.5, 12.6**

### Property 12: Template Customization Persistence
*For any* template customization, applying it to a resume should persist the customization and be reflected in all future renders.
**Validates: Requirements 14.1, 14.2, 14.3, 14.4, 14.5**

### Property 13: Optimization Improvement
*For any* accepted optimization, the optimized version's ATS score should be greater than or equal to the original score.
**Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7**

### Property 14: File Storage Security
*For any* uploaded file, it should be stored with a secure random filename outside the web root directory.
**Validates: Requirements 15.5, 15.6**

### Property 15: Response Time Compliance
*For any* PDF upload under 5MB, processing should complete within 5 seconds.
**Validates: Requirements 17.1**

## Error Handling Strategy

### Graceful Degradation

```python
def get_resume_with_fallback(resume_id):
    try:
        # Try to load with all related data
        resume = Resume.objects.prefetch_related(
            'experiences', 'education', 'skills', 'projects'
        ).get(id=resume_id)
        return resume
    except Resume.DoesNotExist:
        raise Http404("Resume not found")
    except Exception as e:
        # Log error but try basic load
        logger.error(f"Error loading resume {resume_id}: {e}")
        try:
            resume = Resume.objects.get(id=resume_id)
            return resume
        except:
            raise Http404("Resume not found")
```

### User Feedback

```python
def handle_optimization_error(request, resume_id, error):
    if isinstance(error, ValidationError):
        messages.error(request, f"Validation error: {error}")
    elif isinstance(error, TimeoutError):
        messages.error(request, "Optimization took too long. Please try again.")
    else:
        logger.error(f"Optimization failed for resume {resume_id}: {error}", exc_info=True)
        messages.error(request, "An unexpected error occurred. Our team has been notified.")
    
    return redirect('resume_detail', pk=resume_id)
```

This completes the comprehensive design document for NextGenCV v2.0 Advanced Features!
