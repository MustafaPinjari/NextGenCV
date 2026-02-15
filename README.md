# NextGenCV v2.0 - Advanced ATS Resume Builder

A comprehensive Django-based web application for creating, managing, and optimizing resumes for Applicant Tracking Systems (ATS). Version 2.0 introduces advanced features including PDF upload/parsing, AI-powered optimization, version control, and comprehensive analytics.

## Features

### Core Features (v1.0)
- User authentication and registration
- Create and manage multiple resumes
- ATS analysis against job descriptions
- PDF export with ATS-compatible formatting
- Professional resume templates
- Keyword matching and optimization suggestions

### Advanced Features (v2.0)
- **PDF Upload & Parsing**: Upload existing resume PDFs and automatically extract structured data
- **AI-Powered Resume Optimization**: "Fix My Resume" feature that automatically improves content
- **Version Control**: Track all resume changes with full version history and comparison
- **Comprehensive Analytics**: Dashboard with resume health metrics, score trends, and insights
- **Advanced ATS Scoring**: Multi-factor scoring algorithm (keyword match, skills, quantification, action verbs)
- **Template Management**: Multiple professional templates with customization options
- **Enhanced Export**: Export to PDF, DOCX, and plain text formats
- **Batch Operations**: Perform operations on multiple resumes simultaneously
- **Security Enhancements**: Robust file validation, data isolation, and XSS protection

## Technology Stack

- **Backend**: Django 4.2.7
- **Database**: SQLite (PostgreSQL-ready architecture)
- **Frontend**: Bootstrap 5.3.2, Chart.js (for analytics)
- **PDF Generation**: WeasyPrint 60.1
- **PDF Parsing**: pdfplumber
- **NLP Processing**: spaCy (en_core_web_sm model)
- **Document Export**: python-docx
- **Testing**: Hypothesis 6.92.1 (Property-based testing)
- **Security**: bleach (HTML sanitization)

## Project Structure

```
nextgencv-v2/
├── apps/
│   ├── authentication/       # User authentication
│   ├── resumes/             # Resume management
│   │   ├── services/        # Business logic layer
│   │   │   ├── pdf_parser.py
│   │   │   ├── section_parser.py
│   │   │   ├── resume_optimizer.py
│   │   │   ├── version_service.py
│   │   │   └── ...
│   │   └── utils/           # Utility functions
│   ├── analyzer/            # ATS analysis
│   │   └── services/        # Scoring and analysis services
│   │       ├── keyword_extractor.py
│   │       ├── scoring_engine.py
│   │       ├── action_verb_analyzer.py
│   │       └── quantification_detector.py
│   ├── analytics/           # Analytics and dashboard
│   │   └── services/        # Analytics services
│   └── templates_mgmt/      # Template management
│       └── services/        # Template services
├── config/                  # Django settings
├── templates/               # HTML templates
├── static/                  # CSS, JS, images
├── media/                   # User uploads
├── Docs/                    # Documentation
├── manage.py
└── requirements.txt
```

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment tool (venv or virtualenv)

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd nextgencv-v2
```

2. **Create a virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Download spaCy language model**:
```bash
python -m spacy download en_core_web_sm
```

5. **Run migrations**:
```bash
python manage.py migrate
```

6. **Populate resume templates** (optional):
```bash
python manage.py populate_templates
```

7. **Create a superuser** (optional):
```bash
python manage.py createsuperuser
```

8. **Run the development server**:
```bash
python manage.py runserver
```

9. **Access the application** at `http://localhost:8000`

## Development

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.resumes
python manage.py test apps.analyzer
python manage.py test apps.analytics

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Collecting Static Files
```bash
python manage.py collectstatic
```

### Performance Monitoring
```bash
# Collect static files with optimization
python manage.py collectstatic_optimized
```

## Usage Guide

### 1. PDF Upload & Parsing
1. Navigate to "Upload Resume" from the dashboard
2. Select a PDF file (max 10MB)
3. System automatically extracts and structures the content
4. Review parsed data and make corrections if needed
5. Confirm to create a new resume from the parsed data

### 2. Resume Optimization ("Fix My Resume")
1. Open any resume
2. Click "Fix My Resume"
3. Paste the job description you're targeting
4. System analyzes and optimizes your resume:
   - Replaces weak action verbs with strong ones
   - Inserts missing keywords naturally
   - Suggests quantification for achievements
   - Standardizes formatting
5. Review side-by-side comparison
6. Accept or reject changes

### 3. Version Management
1. View version history from resume detail page
2. Compare any two versions to see differences
3. Restore previous versions (creates new version)
4. Track ATS score changes across versions

### 4. Analytics Dashboard
1. Access from main navigation
2. View resume health meter (0-100 score)
3. Track ATS score trends over time
4. Identify top missing keywords
5. Review optimization history and improvements

### 5. Template Customization
1. Browse template gallery
2. Preview templates with sample data
3. Select a template for your resume
4. Customize colors and fonts
5. Add custom CSS if needed

### 6. Export Options
- **PDF**: ATS-compatible format
- **DOCX**: Editable Word document
- **Plain Text**: For ATS parsing
- Export any version of your resume

## API Endpoints

### Authentication
- `POST /auth/register/` - User registration
- `POST /auth/login/` - User login
- `POST /auth/logout/` - User logout

### Resume Management
- `GET /resumes/` - List all user resumes
- `POST /resumes/create/` - Create new resume
- `GET /resumes/<id>/` - View resume details
- `POST /resumes/<id>/update/` - Update resume
- `POST /resumes/<id>/delete/` - Delete resume

### PDF Upload & Parsing
- `POST /resumes/upload/` - Upload PDF file
- `GET /resumes/upload/<id>/review/` - Review parsed data
- `POST /resumes/upload/<id>/confirm/` - Confirm and import

### Resume Optimization
- `POST /resumes/<id>/fix/` - Start optimization
- `GET /resumes/<id>/fix/preview/` - Preview optimized version
- `POST /resumes/<id>/fix/accept/` - Accept changes
- `POST /resumes/<id>/fix/reject/` - Reject changes

### Version Management
- `GET /resumes/<id>/versions/` - List all versions
- `GET /resumes/<id>/versions/<version_id>/` - View specific version
- `GET /resumes/<id>/versions/compare/` - Compare two versions
- `POST /resumes/<id>/versions/<version_id>/restore/` - Restore version

### Analytics
- `GET /analytics/dashboard/` - Main analytics dashboard
- `GET /analytics/trends/` - Detailed trend analysis
- `GET /analytics/improvement-report/` - Comprehensive report

### Template Management
- `GET /templates/gallery/` - Browse templates
- `GET /templates/<id>/preview/` - Preview template
- `POST /templates/<id>/customize/` - Customize template

### Export
- `GET /resumes/<id>/export/pdf/` - Export as PDF
- `GET /resumes/<id>/export/docx/` - Export as DOCX
- `GET /resumes/<id>/export/text/` - Export as plain text
- `GET /resumes/<id>/versions/<version_id>/export/<format>/` - Export specific version

## Architecture

### Service Layer Pattern
The application uses a service layer architecture to separate business logic from views:

```python
# Example: Using services in views
from apps.resumes.services.resume_optimizer import ResumeOptimizerService

def fix_preview(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    job_description = request.session.get('job_description')
    
    # Business logic in service layer
    optimizer = ResumeOptimizerService()
    optimized_data = optimizer.optimize_resume(resume, job_description)
    
    return render(request, 'resumes/fix_comparison.html', {
        'original': resume,
        'optimized': optimized_data
    })
```

### Key Services

**PDF Processing**:
- `PDFParserService`: Extracts text from PDF files
- `SectionParserService`: Identifies and parses resume sections using NLP

**ATS Analysis**:
- `KeywordExtractorService`: Extracts keywords using spaCy
- `ScoringEngineService`: Calculates multi-factor ATS scores
- `ActionVerbAnalyzerService`: Evaluates action verb strength
- `QuantificationDetectorService`: Identifies quantified achievements

**Resume Optimization**:
- `ResumeOptimizerService`: Orchestrates optimization process
- `BulletPointRewriterService`: Improves achievement statements
- `KeywordInjectorService`: Naturally inserts missing keywords
- `QuantificationSuggesterService`: Suggests metrics
- `FormattingStandardizerService`: Fixes ATS-unfriendly formatting

**Version Management**:
- `VersionService`: Handles version creation, comparison, and restoration

**Analytics**:
- `AnalyticsService`: Computes resume health and trends
- `TrendAnalysisService`: Analyzes score improvements over time

### Database Schema

The application uses the following main models:

- **Resume**: Core resume data
- **ResumeVersion**: Version history with snapshots
- **UploadedResume**: Uploaded PDF files and parsed data
- **ResumeAnalysis**: ATS analysis results
- **OptimizationHistory**: Optimization session records
- **ResumeTemplate**: Template definitions
- **TemplateCustomization**: User template customizations

See `Docs/DATABASE_DESIGN.md` for detailed schema documentation.

## Security Features

- **File Upload Validation**: Type, size, and MIME type verification
- **Embedded Script Detection**: Scans PDFs for malicious content
- **Text Sanitization**: All extracted text is sanitized to prevent XSS
- **Data Isolation**: Users can only access their own data
- **CSRF Protection**: All forms protected against CSRF attacks
- **Secure File Storage**: Files stored with random names outside web root
- **Authorization Checks**: All views verify user ownership

## Performance Optimizations

- **Database Indexing**: Optimized indexes on frequently queried fields
- **Query Optimization**: Uses `select_related` and `prefetch_related`
- **Caching**: Analytics data cached for 5 minutes
- **Async-Ready**: Service layer designed for future async operations
- **Efficient PDF Processing**: Streaming for large files

## Testing

The application includes comprehensive test coverage:

- **Unit Tests**: Test individual services and utilities
- **Integration Tests**: Test complete workflows
- **Property-Based Tests**: Test correctness properties using Hypothesis
- **Security Tests**: Validate file upload security and data isolation
- **Performance Tests**: Measure response times and scalability

Run specific test suites:
```bash
# Service layer tests
python manage.py test apps.resumes.services
python manage.py test apps.analyzer.services

# Integration tests
python manage.py test apps.resumes.test_integration_flows

# Property-based tests
python manage.py test apps.resumes.test_property_based

# Security tests
python manage.py test apps.resumes.test_security
```

## Troubleshooting

### Common Issues

**spaCy model not found**:
```bash
python -m spacy download en_core_web_sm
```

**PDF parsing fails**:
- Ensure PDF is not password-protected
- Check file size is under 10MB
- Verify PDF contains extractable text (not scanned images)

**WeasyPrint installation issues**:
- On Ubuntu/Debian: `sudo apt-get install python3-dev python3-pip python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info`
- On macOS: `brew install cairo pango gdk-pixbuf libffi`

**Database migration conflicts**:
```bash
python manage.py migrate --fake-initial
```

### Performance Issues

If experiencing slow performance:
1. Check database indexes are created: `python manage.py sqlmigrate resumes 0002`
2. Clear cache: Delete `.hypothesis` directory
3. Optimize static files: `python manage.py collectstatic_optimized`

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `python manage.py test`
5. Commit changes: `git commit -am 'Add feature'`
6. Push to branch: `git push origin feature-name`
7. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for all public methods
- Keep service layer methods focused and testable

## Documentation

Additional documentation available in the `Docs/` directory:

- **ARCHITECTURE.md**: Detailed system architecture
- **DATABASE_DESIGN.md**: Complete database schema
- **SYSTEM_DESIGN.md**: System design decisions
- **USER_FLOW.md**: User interaction flows
- **DEVELOPMENT_ROADMAP.md**: Future enhancements

## Deployment

See `DEPLOYMENT.md` for production deployment instructions including:
- Environment configuration
- Database setup (PostgreSQL migration)
- Static file serving
- Security checklist
- Performance tuning

## Version History

### v2.0.0 (Current)
- PDF upload and parsing with NLP
- AI-powered resume optimization
- Version control system
- Comprehensive analytics dashboard
- Advanced ATS scoring (6 factors)
- Template management and customization
- Enhanced export options (PDF, DOCX, text)
- Security enhancements
- Performance optimizations

### v1.0.0
- Basic resume creation and management
- Simple ATS analysis
- PDF export
- User authentication
- Template system

## License

This project is for educational purposes.
