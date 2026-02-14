# Resume Optimization Services

This directory contains the service layer for resume optimization functionality in NextGenCV v2.0.

## Overview

The optimization services provide AI-powered resume improvement capabilities including:
- Bullet point rewriting with strong action verbs
- Natural keyword injection based on job descriptions
- Quantification suggestions for achievements
- ATS-friendly formatting standardization
- Comprehensive orchestration of all optimization features

## Services

### 1. BulletPointRewriterService

**Purpose**: Rewrites resume bullet points by replacing weak verbs with strong action verbs.

**Key Methods**:
- `rewrite_bullet_point(bullet, context)` - Rewrites a single bullet point
- `select_strong_verb(bullet, context)` - Selects appropriate action verb based on context
- `starts_with_action_verb(bullet)` - Checks if bullet starts with action verb
- `rewrite_multiple_bullets(bullets, context)` - Batch rewrite operation

**Example Usage**:
```python
from apps.resumes.services import BulletPointRewriterService

bullet = "Worked on developing web applications"
result = BulletPointRewriterService.rewrite_bullet_point(bullet)

print(result['rewritten'])  # "Developed web applications"
print(result['changed'])    # True
print(result['reason'])     # "Replaced weak verb 'worked on' with 'developed'"
```

**Features**:
- Context-aware verb selection (team, system, process, etc.)
- Handles multi-word weak phrases ("responsible for", "worked on")
- Maintains original meaning while improving impact
- Provides detailed change explanations

### 2. KeywordInjectorService

**Purpose**: Naturally injects missing keywords from job descriptions into resume content.

**Key Methods**:
- `inject_keywords(resume, missing_keywords, job_description, max_keywords)` - Main injection method
- `find_best_injection_point(resume, keyword)` - Finds optimal location for keyword
- `inject_keyword_naturally(text, keyword, injection_type)` - Creates natural injection text
- `calculate_keyword_priority(keywords, job_description)` - Prioritizes keywords by frequency

**Example Usage**:
```python
from apps.resumes.services import KeywordInjectorService

missing_keywords = {'python', 'django', 'react'}
job_description = "We need Python and Django experience..."

changes = KeywordInjectorService.inject_keywords(
    resume, 
    missing_keywords, 
    job_description, 
    max_keywords=5
)

for change in changes:
    print(f"Injected '{change['keyword']}' into {change['location']}")
```

**Features**:
- Prioritizes keywords by frequency in job description
- Context-aware injection (skill, technology, methodology, tool)
- Natural language templates for different keyword types
- Smart injection point selection (skills > experience > projects)

### 3. QuantificationSuggesterService

**Purpose**: Suggests quantifications for achievements lacking measurable metrics.

**Key Methods**:
- `suggest_quantification(bullet)` - Suggests metrics for a bullet point
- `classify_achievement(bullet)` - Classifies achievement type
- `suggest_for_multiple_bullets(bullets)` - Batch suggestion operation
- `analyze_experience_quantification(description)` - Analyzes quantification coverage

**Example Usage**:
```python
from apps.resumes.services import QuantificationSuggesterService

bullet = "Improved system performance"
result = QuantificationSuggesterService.suggest_quantification(bullet)

print(result['achievement_type'])  # "performance"
print(result['suggestions'])       # ['X% faster', 'X% improvement', ...]
print(result['example'])           # "Improved system performance by X% faster"
```

**Achievement Types**:
- Performance (speed, efficiency, throughput)
- Scale (users, transactions, data volume)
- Team (size, mentorship, management)
- Financial (revenue, savings, ROI)
- Time (duration, deadlines, delivery)
- Quality (uptime, accuracy, reliability)
- Customer (satisfaction, retention, support)
- Project (deliverables, milestones, features)
- Automation (time saved, processes automated)
- Code (lines, coverage, refactoring)

### 4. FormattingStandardizerService

**Purpose**: Standardizes resume formatting to ATS-friendly formats.

**Key Methods**:
- `standardize_section_headings(text)` - Standardizes section headers
- `standardize_date_formats(text)` - Converts dates to "Month YYYY" format
- `remove_problematic_formatting(text)` - Removes ATS-unfriendly patterns
- `standardize_all(text)` - Applies all standardizations
- `validate_ats_friendly(text)` - Validates ATS compatibility

**Example Usage**:
```python
from apps.resumes.services import FormattingStandardizerService

text = "Work History:\n01/2020 - 12/2022"
result = FormattingStandardizerService.standardize_all(text)

print(result['standardized'])  # "Work Experience:\nJanuary 2020 - December 2022"
print(len(result['all_changes']))  # Number of changes made
```

**Standardizations**:
- Section headings (Work History → Work Experience)
- Date formats (01/2020 → January 2020)
- Special characters (• → -, — → -)
- Whitespace (multiple spaces, tabs)
- Smart quotes to regular quotes

### 5. ResumeOptimizerService (Orchestrator)

**Purpose**: Coordinates all optimization services to provide comprehensive resume improvement.

**Key Methods**:
- `optimize_resume(resume, job_description, options)` - Main optimization pipeline

**Example Usage**:
```python
from apps.resumes.services import ResumeOptimizerService

result = ResumeOptimizerService.optimize_resume(
    resume,
    job_description,
    options={
        'rewrite_bullets': True,
        'inject_keywords': True,
        'suggest_quantifications': True,
        'standardize_formatting': True,
        'max_keywords': 10
    }
)

print(f"Original Score: {result['original_score']}")
print(f"Optimized Score: {result['optimized_score']}")
print(f"Improvement: +{result['improvement_delta']} points")
print(f"Total Changes: {result['changes_summary']['total_changes']}")
```

**Result Structure**:
```python
{
    'original_score': 65.5,
    'optimized_score': 78.2,
    'improvement_delta': 12.7,
    'changes_summary': {
        'bullet_rewrites': 8,
        'keyword_injections': 5,
        'quantification_suggestions': 6,
        'formatting_fixes': 3,
        'total_changes': 22
    },
    'detailed_changes': [
        {
            'type': 'bullet_rewrite',
            'section': 'experience',
            'company': 'Tech Corp',
            'old_text': '...',
            'new_text': '...',
            'reason': '...'
        },
        # ... more changes
    ],
    'optimized_data': {
        'personal_info': {...},
        'experiences': [...],
        'education': [...],
        'skills': [...],
        'projects': [...]
    }
}
```

## Architecture

### Service Layer Pattern

All services follow a consistent pattern:
- Static methods for stateless operations
- Clear input/output contracts
- Comprehensive error handling
- Detailed change tracking
- Context-aware processing

### Integration with Existing Services

The optimization services integrate with existing analyzer services:
- `KeywordExtractorService` - For keyword extraction and analysis
- `ActionVerbAnalyzerService` - For action verb lists and analysis
- `QuantificationDetectorService` - For detecting existing quantifications
- `ScoringEngineService` - For ATS score calculation

### Data Flow

```
User Request
    ↓
ResumeOptimizerService (Orchestrator)
    ↓
┌─────────────────┬──────────────────┬─────────────────┬──────────────────┐
│ BulletPoint     │ Keyword          │ Quantification  │ Formatting       │
│ Rewriter        │ Injector         │ Suggester       │ Standardizer     │
└─────────────────┴──────────────────┴─────────────────┴──────────────────┘
    ↓                   ↓                   ↓                   ↓
Detailed Changes List
    ↓
Optimized Resume Data
    ↓
Score Estimation
    ↓
Complete Result
```

## Testing

### Unit Tests

Run individual service tests:
```bash
python test_optimization_services.py
```

### Integration Tests

Run full optimization test:
```bash
python test_resume_optimizer_full.py
```

### Test Coverage

All services have been tested with:
- Valid inputs
- Edge cases (empty strings, None values)
- Multiple items (batch operations)
- Integration scenarios

## Performance Considerations

### Optimization Speed

- Bullet rewriting: O(n) where n = number of bullets
- Keyword injection: O(k*s) where k = keywords, s = sections
- Quantification: O(n) where n = number of bullets
- Formatting: O(m) where m = text length

### Memory Usage

- Services are stateless (no instance state)
- Changes tracked in lists (minimal memory overhead)
- No caching (stateless design)

### Scalability

- All operations are synchronous
- Can be easily converted to async for future scaling
- No database queries in service layer (passed as parameters)

## Future Enhancements

### Planned Features

1. **Machine Learning Integration**
   - Train models on successful resume optimizations
   - Personalized verb selection based on industry
   - Context-aware keyword placement

2. **Advanced NLP**
   - Semantic similarity for better keyword matching
   - Sentiment analysis for tone optimization
   - Entity recognition for better parsing

3. **A/B Testing**
   - Track optimization effectiveness
   - Compare different optimization strategies
   - User feedback integration

4. **Batch Processing**
   - Optimize multiple resumes simultaneously
   - Portfolio-wide optimization
   - Bulk keyword injection

## Requirements Validation

This implementation satisfies the following requirements from the design document:

- **Requirement 8.1**: Automated resume optimization ✓
- **Requirement 8.2**: Bullet point rewriting with strong action verbs ✓
- **Requirement 8.3**: Natural keyword injection ✓
- **Requirement 8.4**: Quantification suggestions ✓
- **Requirement 8.5**: Formatting standardization ✓
- **Requirement 8.7**: Detailed change tracking ✓
- **Requirement 8.8**: Score improvement calculation ✓
- **Requirement 9.1-9.5**: Optimization transparency and review ✓

## Contributing

When adding new optimization features:

1. Follow the existing service pattern
2. Add comprehensive docstrings
3. Include example usage in docstrings
4. Add unit tests
5. Update this README
6. Ensure integration with ResumeOptimizerService

## License

Part of NextGenCV v2.0 - ATS Resume Builder
