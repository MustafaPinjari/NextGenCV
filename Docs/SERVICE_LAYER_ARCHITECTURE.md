# Service Layer Architecture

## Overview

NextGenCV v2.0 implements a comprehensive service layer architecture that separates business logic from presentation and data access layers. This document describes the design principles, patterns, and implementation details of the service layer.

## Architecture Principles

### 1. Separation of Concerns

The service layer sits between views (presentation) and models (data):

```
Views (Presentation)
    ↓
Service Layer (Business Logic)
    ↓
Models (Data Access)
    ↓
Database
```

### 2. Single Responsibility

Each service class has a single, well-defined responsibility:
- `PDFParserService`: PDF text extraction only
- `SectionParserService`: Resume section identification only
- `ScoringEngineService`: ATS score calculation only

### 3. Dependency Injection

Services receive dependencies through constructor injection:

```python
class ResumeOptimizerService:
    def __init__(self, 
                 keyword_extractor=None,
                 action_verb_analyzer=None,
                 scoring_engine=None):
        self.keyword_extractor = keyword_extractor or KeywordExtractorService()
        self.action_verb_analyzer = action_verb_analyzer or ActionVerbAnalyzerService()
        self.scoring_engine = scoring_engine or ScoringEngineService()
```

### 4. Testability

All services are designed to be easily testable:
- Pure functions where possible
- Minimal external dependencies
- Clear input/output contracts
- No direct database access in business logic

## Service Organization

### Directory Structure

```
apps/
├── analyzer/
│   └── services/
│       ├── __init__.py
│       ├── keyword_extractor.py
│       ├── scoring_engine.py
│       ├── action_verb_analyzer.py
│       └── quantification_detector.py
│
├── resumes/
│   └── services/
│       ├── __init__.py
│       ├── pdf_parser.py
│       ├── section_parser.py
│       ├── resume_optimizer.py
│       ├── version_service.py
│       ├── bullet_point_rewriter.py
│       ├── keyword_injector.py
│       ├── quantification_suggester.py
│       └── formatting_standardizer.py
│
├── analytics/
│   └── services/
│       ├── __init__.py
│       ├── analytics_service.py
│       ├── trend_analysis.py
│       └── health_score.py
│
└── templates_mgmt/
    └── services/
        ├── __init__.py
        ├── template_service.py
        └── customization_service.py
```

## Core Services

### 1. PDF Processing Services

#### PDFParserService

**Purpose**: Extract text from PDF files

**Location**: `apps/resumes/services/pdf_parser.py`

**Key Methods**:
```python
class PDFParserService:
    @staticmethod
    def extract_text_from_pdf(pdf_file: File) -> str:
        """Extract all text from PDF file"""
        
    @staticmethod
    def clean_extracted_text(text: str) -> str:
        """Clean and normalize extracted text"""
        
    @staticmethod
    def calculate_parsing_confidence(text: str) -> float:
        """Calculate confidence score for extraction quality"""
```

**Dependencies**:
- `pdfplumber`: PDF text extraction
- `bleach`: Text sanitization

**Usage Example**:
```python
from apps.resumes.services.pdf_parser import PDFParserService

parser = PDFParserService()
text = parser.extract_text_from_pdf(uploaded_file)
clean_text = parser.clean_extracted_text(text)
confidence = parser.calculate_parsing_confidence(clean_text)
```

#### SectionParserService

**Purpose**: Identify and parse resume sections from unstructured text

**Location**: `apps/resumes/services/section_parser.py`

**Key Methods**:
```python
class SectionParserService:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
    
    def identify_sections(self, text: str) -> Dict[str, str]:
        """Identify section boundaries in text"""
        
    def parse_personal_info(self, text: str) -> Dict:
        """Extract personal information using NER"""
        
    def parse_experiences(self, text: str) -> List[Dict]:
        """Parse work experience entries"""
        
    def parse_education(self, text: str) -> List[Dict]:
        """Parse education entries"""
        
    def parse_skills(self, text: str) -> List[str]:
        """Extract and categorize skills"""
```

**Dependencies**:
- `spacy`: Natural language processing
- `re`: Regular expressions for pattern matching

**Usage Example**:
```python
from apps.resumes.services.section_parser import SectionParserService

parser = SectionParserService()
sections = parser.identify_sections(extracted_text)
personal_info = parser.parse_personal_info(sections['header'])
experiences = parser.parse_experiences(sections['experience'])
```

### 2. ATS Analysis Services

#### KeywordExtractorService

**Purpose**: Extract and analyze keywords using NLP

**Location**: `apps/analyzer/services/keyword_extractor.py`

**Key Methods**:
```python
class KeywordExtractorService:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
    
    @staticmethod
    def extract_keywords(text: str, min_length: int = 3) -> Set[str]:
        """Extract keywords from text"""
        
    @staticmethod
    def calculate_keyword_frequency(text: str) -> Dict[str, int]:
        """Calculate frequency of each keyword"""
        
    @staticmethod
    def weight_keywords_by_importance(keywords: Set[str], 
                                     context: str) -> Dict[str, float]:
        """Assign importance weights to keywords"""
```

**Algorithm**:
1. Tokenize text using spaCy
2. Extract nouns, proper nouns, and noun phrases
3. Remove stop words
4. Calculate frequency
5. Weight by position and context

**Usage Example**:
```python
from apps.analyzer.services.keyword_extractor import KeywordExtractorService

extractor = KeywordExtractorService()
resume_keywords = extractor.extract_keywords(resume_text)
jd_keywords = extractor.extract_keywords(job_description)
match_rate = len(resume_keywords & jd_keywords) / len(jd_keywords)
```

#### ScoringEngineService

**Purpose**: Calculate comprehensive ATS scores

**Location**: `apps/analyzer/services/scoring_engine.py`

**Key Methods**:
```python
class ScoringEngineService:
    def __init__(self):
        self.keyword_extractor = KeywordExtractorService()
        self.action_verb_analyzer = ActionVerbAnalyzerService()
        self.quantification_detector = QuantificationDetectorService()
    
    def calculate_ats_score(self, resume: Resume, 
                           job_description: str) -> Dict:
        """Calculate comprehensive ATS score"""
        
    def calculate_keyword_match_score(self, resume_text: str, 
                                     jd_text: str) -> float:
        """Calculate keyword match percentage"""
        
    def calculate_skill_relevance_score(self, skills: List[str], 
                                       jd_keywords: Set[str]) -> float:
        """Calculate skill relevance"""
        
    def calculate_section_completeness_score(self, resume: Resume) -> float:
        """Calculate section completeness"""
        
    def calculate_experience_impact_score(self, experiences: List) -> float:
        """Calculate experience impact"""
        
    def calculate_quantification_score(self, experiences: List) -> float:
        """Calculate quantification score"""
        
    def calculate_action_verb_score(self, experiences: List) -> float:
        """Calculate action verb strength"""
```

**Scoring Formula**:
```
Final Score = (
    keyword_match * 0.30 +
    skill_relevance * 0.20 +
    section_completeness * 0.15 +
    experience_impact * 0.15 +
    quantification * 0.10 +
    action_verb * 0.10
)
```

**Usage Example**:
```python
from apps.analyzer.services.scoring_engine import ScoringEngineService

engine = ScoringEngineService()
scores = engine.calculate_ats_score(resume, job_description)

print(f"Final Score: {scores['final_score']}")
print(f"Keyword Match: {scores['keyword_match_score']}")
print(f"Skill Relevance: {scores['skill_relevance_score']}")
```

### 3. Resume Optimization Services

#### ResumeOptimizerService

**Purpose**: Orchestrate resume optimization process

**Location**: `apps/resumes/services/resume_optimizer.py`

**Key Methods**:
```python
class ResumeOptimizerService:
    def __init__(self):
        self.bullet_rewriter = BulletPointRewriterService()
        self.keyword_injector = KeywordInjectorService()
        self.quant_suggester = QuantificationSuggesterService()
        self.formatter = FormattingStandardizerService()
        self.scoring_engine = ScoringEngineService()
    
    def optimize_resume(self, resume: Resume, 
                       job_description: str) -> Dict:
        """Optimize resume based on job description"""
        
    def generate_optimization_report(self, original: Resume, 
                                    optimized: Dict) -> Dict:
        """Generate detailed optimization report"""
```

**Optimization Pipeline**:
```
1. Analyze Current State
   ↓
2. Extract Missing Keywords
   ↓
3. Rewrite Weak Bullet Points
   ↓
4. Inject Keywords Naturally
   ↓
5. Suggest Quantification
   ↓
6. Standardize Formatting
   ↓
7. Calculate New Score
   ↓
8. Generate Change Report
```

**Usage Example**:
```python
from apps.resumes.services.resume_optimizer import ResumeOptimizerService

optimizer = ResumeOptimizerService()
result = optimizer.optimize_resume(resume, job_description)

print(f"Original Score: {result['original_score']}")
print(f"Optimized Score: {result['optimized_score']}")
print(f"Improvement: +{result['improvement_delta']}")
print(f"Changes Made: {len(result['changes'])}")
```

#### BulletPointRewriterService

**Purpose**: Improve achievement statements

**Location**: `apps/resumes/services/bullet_point_rewriter.py`

**Key Methods**:
```python
class BulletPointRewriterService:
    STRONG_ACTION_VERBS = [
        'achieved', 'accelerated', 'accomplished', 'delivered',
        'developed', 'engineered', 'established', 'executed',
        'generated', 'implemented', 'improved', 'increased',
        'launched', 'led', 'optimized', 'reduced', 'spearheaded',
        'streamlined', 'transformed'
    ]
    
    WEAK_VERBS = ['did', 'made', 'worked', 'helped', 'responsible for']
    
    def rewrite_bullet_point(self, bullet: str, context: str) -> str:
        """Rewrite bullet point with strong action verb"""
        
    def select_strong_verb(self, bullet: str, context: str) -> str:
        """Select appropriate strong verb based on context"""
        
    def starts_with_action_verb(self, bullet: str) -> bool:
        """Check if bullet starts with action verb"""
```

**Algorithm**:
1. Identify weak verbs
2. Analyze context (team, system, process, etc.)
3. Select appropriate strong verb
4. Rewrite maintaining meaning
5. Ensure quantification is preserved

### 4. Version Management Services

#### VersionService

**Purpose**: Manage resume versions

**Location**: `apps/resumes/services/version_service.py`

**Key Methods**:
```python
class VersionService:
    @staticmethod
    def create_version(resume: Resume, 
                      modification_type: str = 'manual',
                      user_notes: str = '') -> ResumeVersion:
        """Create new version snapshot"""
        
    @staticmethod
    def get_version_history(resume: Resume) -> QuerySet:
        """Get all versions for resume"""
        
    @staticmethod
    def compare_versions(version1: ResumeVersion, 
                        version2: ResumeVersion) -> Dict:
        """Generate diff between two versions"""
        
    @staticmethod
    def restore_version(version: ResumeVersion) -> Resume:
        """Restore resume to previous version"""
```

**Version Snapshot Structure**:
```python
{
    'personal_info': {
        'full_name': str,
        'email': str,
        'phone': str,
        'location': str
    },
    'summary': str,
    'experiences': [
        {
            'job_title': str,
            'company': str,
            'location': str,
            'start_date': str,
            'end_date': str,
            'responsibilities': str
        }
    ],
    'education': [...],
    'skills': [...],
    'projects': [...]
}
```

**Usage Example**:
```python
from apps.resumes.services.version_service import VersionService

# Create version
version = VersionService.create_version(
    resume=resume,
    modification_type='optimized',
    user_notes='Optimized for Software Engineer role'
)

# Compare versions
diff = VersionService.compare_versions(version1, version2)

# Restore version
VersionService.restore_version(old_version)
```

### 5. Analytics Services

#### AnalyticsService

**Purpose**: Compute analytics and insights

**Location**: `apps/analytics/services/analytics_service.py`

**Key Methods**:
```python
class AnalyticsService:
    @staticmethod
    def calculate_resume_health(resume: Resume) -> float:
        """Calculate overall resume health score"""
        
    @staticmethod
    def get_score_trends(user: User) -> Dict:
        """Get ATS score trends over time"""
        
    @staticmethod
    def get_top_missing_keywords(user: User, limit: int = 10) -> List:
        """Get most frequently missing keywords"""
        
    @staticmethod
    def generate_improvement_report(user: User) -> Dict:
        """Generate comprehensive improvement report"""
```

**Health Score Calculation**:
```python
health_score = (
    section_completeness * 0.40 +
    contact_completeness * 0.15 +
    quantification_rate * 0.20 +
    action_verb_rate * 0.15 +
    formatting_score * 0.10
)
```

**Usage Example**:
```python
from apps.analytics.services.analytics_service import AnalyticsService

# Calculate health
health = AnalyticsService.calculate_resume_health(resume)

# Get trends
trends = AnalyticsService.get_score_trends(user)

# Get missing keywords
keywords = AnalyticsService.get_top_missing_keywords(user, limit=10)
```

## Service Integration Patterns

### 1. Service Composition

Services can be composed to create higher-level functionality:

```python
class ResumeOptimizerService:
    def __init__(self):
        # Compose multiple services
        self.keyword_extractor = KeywordExtractorService()
        self.action_verb_analyzer = ActionVerbAnalyzerService()
        self.bullet_rewriter = BulletPointRewriterService()
        self.keyword_injector = KeywordInjectorService()
        self.scoring_engine = ScoringEngineService()
    
    def optimize_resume(self, resume, job_description):
        # Use composed services
        jd_keywords = self.keyword_extractor.extract_keywords(job_description)
        resume_keywords = self.keyword_extractor.extract_keywords(resume.get_full_text())
        missing_keywords = jd_keywords - resume_keywords
        
        # Rewrite bullets
        optimized_experiences = []
        for exp in resume.experiences.all():
            bullets = exp.responsibilities.split('\n')
            optimized_bullets = [
                self.bullet_rewriter.rewrite_bullet_point(b, job_description)
                for b in bullets
            ]
            optimized_experiences.append({
                **exp.__dict__,
                'responsibilities': '\n'.join(optimized_bullets)
            })
        
        # Inject keywords
        optimized_experiences = self.keyword_injector.inject_keywords(
            optimized_experiences,
            missing_keywords
        )
        
        # Calculate new score
        new_score = self.scoring_engine.calculate_ats_score(
            optimized_resume,
            job_description
        )
        
        return {
            'optimized_data': optimized_experiences,
            'score': new_score,
            'changes': changes
        }
```

### 2. Service Orchestration in Views

Views use services to implement business logic:

```python
from apps.resumes.services.resume_optimizer import ResumeOptimizerService
from apps.resumes.services.version_service import VersionService
from apps.analyzer.services.scoring_engine import ScoringEngineService

def fix_preview(request, resume_id):
    # Get data
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    job_description = request.session.get('job_description')
    
    # Use services for business logic
    optimizer = ResumeOptimizerService()
    result = optimizer.optimize_resume(resume, job_description)
    
    # Store in session
    request.session['optimization_result'] = result
    
    # Render
    return render(request, 'resumes/fix_comparison.html', {
        'original': resume,
        'optimized': result['optimized_data'],
        'changes': result['changes'],
        'score_improvement': result['improvement_delta']
    })

def fix_accept(request, resume_id):
    # Get data
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    result = request.session.get('optimization_result')
    
    # Apply changes (business logic in service)
    # ... update resume with optimized data ...
    
    # Create version (business logic in service)
    version_service = VersionService()
    version_service.create_version(
        resume=resume,
        modification_type='optimized',
        user_notes='Optimized via Fix My Resume'
    )
    
    # Clear session
    del request.session['optimization_result']
    
    return redirect('resumes:resume_detail', resume_id=resume.id)
```

### 3. Service Testing

Services are designed to be easily testable:

```python
# tests/test_keyword_extractor.py
from apps.analyzer.services.keyword_extractor import KeywordExtractorService

class TestKeywordExtractorService(TestCase):
    def setUp(self):
        self.extractor = KeywordExtractorService()
    
    def test_extract_keywords_basic(self):
        text = "Python developer with Django experience"
        keywords = self.extractor.extract_keywords(text)
        
        self.assertIn('python', keywords)
        self.assertIn('django', keywords)
        self.assertIn('developer', keywords)
    
    def test_extract_keywords_removes_stopwords(self):
        text = "The quick brown fox"
        keywords = self.extractor.extract_keywords(text)
        
        self.assertNotIn('the', keywords)
        self.assertIn('fox', keywords)
    
    def test_keyword_frequency(self):
        text = "Python Python Django Python"
        freq = self.extractor.calculate_keyword_frequency(text)
        
        self.assertEqual(freq['python'], 3)
        self.assertEqual(freq['django'], 1)
```

## Error Handling

Services use consistent error handling patterns:

```python
class PDFParserService:
    class PDFParsingError(Exception):
        """Raised when PDF parsing fails"""
        pass
    
    @staticmethod
    def extract_text_from_pdf(pdf_file):
        try:
            with pdfplumber.open(pdf_file) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            raise PDFParserService.PDFParsingError(
                f"Failed to extract text from PDF: {str(e)}"
            )
```

Views handle service errors:

```python
def pdf_upload(request):
    if request.method == 'POST':
        try:
            parser = PDFParserService()
            text = parser.extract_text_from_pdf(request.FILES['file'])
            # ... continue processing ...
        except PDFParserService.PDFParsingError as e:
            messages.error(request, str(e))
            return redirect('resumes:pdf_upload')
```

## Performance Considerations

### 1. Caching

Services can implement caching for expensive operations:

```python
from django.core.cache import cache

class AnalyticsService:
    @staticmethod
    def calculate_resume_health(resume):
        cache_key = f'resume_health_{resume.id}_{resume.updated_at}'
        cached_health = cache.get(cache_key)
        
        if cached_health is not None:
            return cached_health
        
        # Calculate health (expensive operation)
        health = # ... calculation ...
        
        # Cache for 5 minutes
        cache.set(cache_key, health, 300)
        
        return health
```

### 2. Lazy Loading

Services use lazy loading for NLP models:

```python
class KeywordExtractorService:
    _nlp = None
    
    @classmethod
    def get_nlp(cls):
        if cls._nlp is None:
            cls._nlp = spacy.load('en_core_web_sm')
        return cls._nlp
    
    def extract_keywords(self, text):
        nlp = self.get_nlp()
        doc = nlp(text)
        # ... process ...
```

### 3. Batch Processing

Services support batch operations:

```python
class ScoringEngineService:
    def calculate_ats_scores_batch(self, resumes, job_description):
        """Calculate scores for multiple resumes efficiently"""
        # Extract JD keywords once
        jd_keywords = self.keyword_extractor.extract_keywords(job_description)
        
        # Process all resumes
        results = []
        for resume in resumes:
            score = self._calculate_score_with_cached_keywords(
                resume,
                jd_keywords
            )
            results.append(score)
        
        return results
```

## Future Enhancements

### 1. Async Support

Services are designed to support async operations:

```python
class PDFParserService:
    @staticmethod
    async def extract_text_from_pdf_async(pdf_file):
        """Async version of PDF extraction"""
        # Implementation using async libraries
        pass
```

### 2. Microservices Migration

Service layer architecture supports future microservices migration:

```
Current: Monolithic Django App
    ↓
Future: Microservices
    - PDF Processing Service (FastAPI)
    - NLP Analysis Service (FastAPI)
    - Scoring Service (FastAPI)
    - Version Management Service (Django)
```

### 3. API Layer

Services can be exposed via REST API:

```python
# api/views.py
from rest_framework.views import APIView
from apps.analyzer.services.scoring_engine import ScoringEngineService

class ATSScoreAPIView(APIView):
    def post(self, request):
        resume_id = request.data.get('resume_id')
        job_description = request.data.get('job_description')
        
        # Use service
        engine = ScoringEngineService()
        resume = Resume.objects.get(id=resume_id)
        scores = engine.calculate_ats_score(resume, job_description)
        
        return Response(scores)
```

## Conclusion

The service layer architecture in NextGenCV v2.0 provides:
- Clear separation of concerns
- Highly testable code
- Reusable business logic
- Easy maintenance and extension
- Future-proof design for scaling

All business logic is encapsulated in services, making the codebase maintainable, testable, and ready for future enhancements.
