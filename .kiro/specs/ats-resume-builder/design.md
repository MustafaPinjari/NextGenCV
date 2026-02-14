# Design Document

## Overview

The ATS Optimized Resume Builder is a server-rendered Django web application that follows a layered monolithic architecture. The system uses Django's built-in authentication, ORM with SQLite database, Bootstrap for UI styling, and WeasyPrint for PDF generation. The application emphasizes simplicity, maintainability, and ATS compatibility.

The core workflow involves users creating structured resumes through a wizard interface, managing multiple resume versions, analyzing resumes against job descriptions using keyword matching algorithms, and exporting ATS-compatible PDFs.

## Architecture

### Layered Architecture

The application follows a three-tier layered architecture:

1. **Presentation Layer**: Django templates with Bootstrap CSS framework for responsive UI
2. **Application Layer**: Django views and service classes containing business logic
3. **Data Layer**: Django ORM models with SQLite database

### Request Lifecycle

```
User Request → URL Router → View Function → Service Layer → Database (ORM)
                                                              ↓
User Response ← Template Rendering ← View Function ← Service Layer
```

### Django Project Structure

```
ats_resume_builder/          # Project root
├── manage.py
├── config/                  # Project configuration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── authentication/      # User auth app
│   ├── resumes/            # Resume management app
│   └── analyzer/           # ATS analysis app
├── templates/              # HTML templates
│   ├── base.html
│   ├── authentication/
│   ├── resumes/
│   └── analyzer/
├── static/                 # Static files
│   ├── css/
│   ├── js/
│   └── images/
└── requirements.txt
```

## Components and Interfaces

### 1. Authentication Component

**Purpose**: Handle user registration, login, logout, and session management.

**Django App**: `authentication`

**Models**:
- Uses Django's built-in `User` model (django.contrib.auth.models.User)

**Views**:
- `RegisterView`: Handles user registration
- `LoginView`: Handles user login (Django's built-in)
- `LogoutView`: Handles user logout (Django's built-in)
- `DashboardView`: Main landing page after login

**Forms**:
- `UserRegistrationForm`: Validates username, email, password
- Uses Django's built-in `AuthenticationForm` for login

**URLs**:
- `/register/` → RegisterView
- `/login/` → LoginView
- `/logout/` → LogoutView
- `/dashboard/` → DashboardView

**Security**:
- CSRF protection on all forms
- Password hashing using Django's default PBKDF2 algorithm
- Login required decorator on protected views

### 2. Resume Management Component

**Purpose**: CRUD operations for resumes and all resume sections.

**Django App**: `resumes`

**Models**:

```python
class Resume:
    id: AutoField (PK)
    user: ForeignKey(User)
    title: CharField(max_length=200)
    template: CharField(max_length=50, default='professional')
    created_at: DateTimeField(auto_now_add=True)
    updated_at: DateTimeField(auto_now=True)

class PersonalInfo:
    id: AutoField (PK)
    resume: OneToOneField(Resume)
    full_name: CharField(max_length=200)
    phone: CharField(max_length=20)
    email: EmailField()
    linkedin: URLField(blank=True)
    github: URLField(blank=True)
    location: CharField(max_length=200)

class Experience:
    id: AutoField (PK)
    resume: ForeignKey(Resume)
    company: CharField(max_length=200)
    role: CharField(max_length=200)
    start_date: DateField()
    end_date: DateField(null=True, blank=True)
    description: TextField()
    order: IntegerField(default=0)

class Education:
    id: AutoField (PK)
    resume: ForeignKey(Resume)
    institution: CharField(max_length=200)
    degree: CharField(max_length=200)
    field: CharField(max_length=200)
    start_year: IntegerField()
    end_year: IntegerField(null=True, blank=True)
    order: IntegerField(default=0)

class Skill:
    id: AutoField (PK)
    resume: ForeignKey(Resume)
    name: CharField(max_length=100)
    category: CharField(max_length=50)

class Project:
    id: AutoField (PK)
    resume: ForeignKey(Resume)
    name: CharField(max_length=200)
    description: TextField()
    technologies: CharField(max_length=500)
    url: URLField(blank=True)
    order: IntegerField(default=0)
```

**Views**:
- `ResumeListView`: Display all user's resumes (dashboard)
- `ResumeCreateView`: Wizard for creating new resume
- `ResumeUpdateView`: Edit existing resume
- `ResumeDetailView`: Preview resume
- `ResumeDeleteView`: Delete resume
- `ResumeDuplicateView`: Duplicate existing resume

**Forms**:
- `ResumeForm`: Resume title and template selection
- `PersonalInfoForm`: Personal information fields
- `ExperienceForm`: Work experience entry
- `EducationForm`: Education entry
- `SkillForm`: Skill entry
- `ProjectForm`: Project entry

**Services**:
- `ResumeService`: Business logic for resume operations
  - `create_resume(user, data)`: Create new resume with all sections
  - `update_resume(resume_id, data)`: Update resume sections
  - `duplicate_resume(resume_id)`: Create copy of resume
  - `delete_resume(resume_id)`: Delete resume and cascade sections
  - `get_user_resumes(user)`: Retrieve all resumes for user

**URLs**:
- `/resumes/` → ResumeListView
- `/resumes/create/` → ResumeCreateView
- `/resumes/<id>/` → ResumeDetailView
- `/resumes/<id>/edit/` → ResumeUpdateView
- `/resumes/<id>/delete/` → ResumeDeleteView
- `/resumes/<id>/duplicate/` → ResumeDuplicateView

### 3. ATS Analyzer Component

**Purpose**: Analyze resume against job descriptions and provide optimization suggestions.

**Django App**: `analyzer`

**Services**:

```python
class ATSAnalyzerService:
    def analyze_resume(resume_id, job_description):
        """
        Main analysis function
        Returns: {
            'score': float,
            'matched_keywords': list,
            'missing_keywords': list,
            'suggestions': list
        }
        """
        
    def aggregate_resume_text(resume):
        """Combine all resume sections into single text"""
        
    def extract_keywords(text):
        """Extract keywords from text"""
        
    def clean_text(text):
        """Lowercase, remove stop words, tokenize"""
        
    def calculate_match_score(resume_keywords, jd_keywords):
        """Calculate percentage match"""
        
    def generate_suggestions(missing_keywords):
        """Create actionable suggestions"""
```

**Algorithm Details**:

1. **Text Aggregation**:
   - Concatenate: personal_info + experiences + education + skills + projects
   - Join with spaces

2. **Text Cleaning**:
   - Convert to lowercase
   - Remove punctuation
   - Tokenize by whitespace
   - Remove stop words (using NLTK or custom list)

3. **Keyword Extraction**:
   - Extract unique words from cleaned text
   - Filter words with length < 3 characters
   - Return set of keywords

4. **Match Calculation**:
   ```
   matched_keywords = resume_keywords ∩ jd_keywords
   total_jd_keywords = |jd_keywords|
   score = (|matched_keywords| / total_jd_keywords) × 100
   missing_keywords = jd_keywords - resume_keywords
   ```

5. **Suggestion Generation**:
   - For each missing keyword, suggest adding to relevant section
   - Prioritize high-frequency keywords from job description

**Views**:
- `AnalyzeResumeView`: Display analysis form and results

**Forms**:
- `JobDescriptionForm`: Text area for job description input

**URLs**:
- `/resumes/<id>/analyze/` → AnalyzeResumeView

### 4. PDF Export Component

**Purpose**: Generate ATS-compatible PDF resumes.

**Library**: WeasyPrint

**Services**:

```python
class PDFExportService:
    def generate_pdf(resume_id):
        """
        Generate PDF from resume
        Returns: PDF file as HttpResponse
        """
        
    def render_resume_html(resume):
        """Render resume template to HTML string"""
```

**Process**:
1. Load resume with all related sections
2. Render Django template to HTML string
3. Pass HTML to WeasyPrint
4. Generate PDF bytes
5. Return as downloadable HttpResponse with content-type application/pdf

**Template Requirements**:
- Use web-safe fonts
- Avoid complex CSS (flexbox/grid okay, but keep simple)
- Use absolute units (pt, px) for print
- Ensure text is selectable (no text-as-images)

**Views**:
- `ExportPDFView`: Generate and download PDF

**URLs**:
- `/resumes/<id>/export/` → ExportPDFView

### 5. Template Rendering Component

**Purpose**: Render resumes with different visual templates.

**Templates**:
- `resumes/templates/professional.html`: Default professional template
- Future templates can be added as separate HTML files

**Template Context**:
```python
{
    'resume': Resume object,
    'personal_info': PersonalInfo object,
    'experiences': QuerySet[Experience],
    'education': QuerySet[Education],
    'skills': QuerySet[Skill] (grouped by category),
    'projects': QuerySet[Project]
}
```

**Template Features**:
- Conditional rendering (hide empty sections)
- Responsive layout using Bootstrap grid
- Print-friendly CSS for PDF generation
- Live preview using HTMX or vanilla JavaScript

## Data Models

### Entity Relationships

```
User (1) ──────< (M) Resume
                      │
                      ├──── (1:1) PersonalInfo
                      ├──── (1:M) Experience
                      ├──── (1:M) Education
                      ├──── (1:M) Skill
                      └──── (1:M) Project
```

### Model Constraints

1. **Resume**:
   - `user` is required (ForeignKey with CASCADE delete)
   - `title` max length 200 characters
   - `template` defaults to 'professional'
   - Indexed on `user` and `updated_at`

2. **PersonalInfo**:
   - One-to-one with Resume (CASCADE delete)
   - `full_name` and `email` are required
   - `email` must be valid email format
   - `linkedin` and `github` must be valid URLs if provided

3. **Experience**:
   - `resume` ForeignKey with CASCADE delete
   - `start_date` must be before `end_date` if `end_date` is provided
   - Ordered by `order` field, then by `start_date` descending

4. **Education**:
   - `resume` ForeignKey with CASCADE delete
   - `start_year` must be before `end_year` if `end_year` is provided
   - Ordered by `order` field, then by `end_year` descending

5. **Skill**:
   - `resume` ForeignKey with CASCADE delete
   - Unique constraint on (`resume`, `name`) to prevent duplicates

6. **Project**:
   - `resume` ForeignKey with CASCADE delete
   - `url` must be valid URL if provided
   - Ordered by `order` field

### Database Indexes

```python
# Resume model
class Meta:
    indexes = [
        models.Index(fields=['user', '-updated_at']),
    ]

# Experience model
class Meta:
    ordering = ['order', '-start_date']

# Education model
class Meta:
    ordering = ['order', '-end_year']

# Skill model
class Meta:
    unique_together = [['resume', 'name']]

# Project model
class Meta:
    ordering = ['order']
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: User Registration Creates Account
*For any* valid registration data (unique username, unique email, valid password), submitting the registration form should create a new user account in the database with hashed password.
**Validates: Requirements 1.1, 13.2**

### Property 2: Duplicate Registration Rejection
*For any* existing user, attempting to register with the same username or email should be rejected with an appropriate error message.
**Validates: Requirements 1.2**

### Property 3: Valid Login Authentication
*For any* registered user with correct credentials, submitting the login form should authenticate the user and establish a session.
**Validates: Requirements 1.3**

### Property 4: Invalid Login Rejection
*For any* login attempt with incorrect credentials (wrong password or non-existent username), the system should reject authentication and display an error.
**Validates: Requirements 1.4**

### Property 5: Logout Session Termination
*For any* authenticated user session, performing logout should terminate the session and prevent access to protected resources.
**Validates: Requirements 1.5**

### Property 6: Protected Resource Access Control
*For any* protected URL, attempting to access it without authentication should redirect to the login page.
**Validates: Requirements 1.6, 13.5**

### Property 7: Resume Creation and Association
*For any* authenticated user and valid resume data, creating a resume should save it to the database and associate it with the user's account.
**Validates: Requirements 2.2**

### Property 8: Resume Unique Identifier Assignment
*For any* resume creation, the system should assign a unique ID and a valid creation timestamp.
**Validates: Requirements 2.3**

### Property 9: Dashboard Resume Display
*For any* user, the dashboard should display exactly the set of resumes associated with that user's account and no others.
**Validates: Requirements 2.4, 13.3**

### Property 10: Personal Information Storage
*For any* valid personal information data, adding it to a resume should store all fields (full_name, phone, email, linkedin, github, location) correctly.
**Validates: Requirements 3.1**

### Property 11: Personal Information Update Persistence
*For any* existing personal information, updating any field should persist the changes to the database.
**Validates: Requirements 3.2**

### Property 12: Email Validation
*For any* invalid email format string, attempting to save it as personal information email should be rejected with a validation error.
**Validates: Requirements 3.3**

### Property 13: URL Validation
*For any* invalid URL format string, attempting to save it as LinkedIn or GitHub URL should be rejected with a validation error.
**Validates: Requirements 3.4**

### Property 14: Personal Information Required Fields
*For any* personal information submission missing full_name or email, the system should reject it with a validation error.
**Validates: Requirements 3.5**

### Property 15: Experience Entry Storage
*For any* valid experience data, adding it to a resume should store all fields (company, role, start_date, end_date, description) correctly.
**Validates: Requirements 4.1**

### Property 16: Current Experience Null End Date
*For any* experience entry marked as current (no end_date), the system should accept and store it with end_date as null.
**Validates: Requirements 4.2**

### Property 17: Experience Chronological Ordering
*For any* set of experience entries on a resume, they should be displayed in reverse chronological order by start_date.
**Validates: Requirements 4.3**

### Property 18: Experience Deletion
*For any* experience entry, deleting it should remove it from the database and it should no longer appear in the resume.
**Validates: Requirements 4.4**

### Property 19: Experience Date Validation
*For any* experience entry where start_date is after end_date, the system should reject it with a validation error.
**Validates: Requirements 4.5**

### Property 20: Education Entry Storage
*For any* valid education data, adding it to a resume should store all fields (institution, degree, field, start_year, end_year) correctly.
**Validates: Requirements 5.1**

### Property 21: Education Chronological Ordering
*For any* set of education entries on a resume, they should be displayed in reverse chronological order by end_year.
**Validates: Requirements 5.2**

### Property 22: Education Deletion
*For any* education entry, deleting it should remove it from the database and it should no longer appear in the resume.
**Validates: Requirements 5.3**

### Property 23: Education Year Validation
*For any* education entry where start_year is after end_year, the system should reject it with a validation error.
**Validates: Requirements 5.4**

### Property 24: Education Required Fields
*For any* education submission missing institution or degree, the system should reject it with a validation error.
**Validates: Requirements 5.5**

### Property 25: Skill Storage
*For any* valid skill data, adding it to a resume should store both name and category correctly.
**Validates: Requirements 6.1**

### Property 26: Skill Category Grouping
*For any* set of skills on a resume, when rendered, they should be grouped by category.
**Validates: Requirements 6.2**

### Property 27: Skill Deletion
*For any* skill entry, deleting it should remove it from the database and it should no longer appear in the resume.
**Validates: Requirements 6.3**

### Property 28: Duplicate Skill Prevention
*For any* resume, attempting to add a skill with a name that already exists on that resume should be rejected.
**Validates: Requirements 6.5**

### Property 29: Project Entry Storage
*For any* valid project data, adding it to a resume should store all fields (name, description, technologies, url) correctly.
**Validates: Requirements 7.1**

### Property 30: Project Order Preservation
*For any* sequence of project additions, the projects should be displayed in the order they were added.
**Validates: Requirements 7.2**

### Property 31: Project Deletion
*For any* project entry, deleting it should remove it from the database and it should no longer appear in the resume.
**Validates: Requirements 7.3**

### Property 32: Project URL Validation
*For any* invalid URL format string, attempting to save it as a project URL should be rejected with a validation error.
**Validates: Requirements 7.4**

### Property 33: Project Required Fields
*For any* project submission missing name or description, the system should reject it with a validation error.
**Validates: Requirements 7.5**

### Property 34: Template Application
*For any* resume with a selected template, rendering the resume should use that specific template.
**Validates: Requirements 8.2, 16.1**

### Property 35: Empty Section Hiding
*For any* resume with empty sections (no entries), those sections should not appear in the rendered output.
**Validates: Requirements 8.4**

### Property 36: Keyword Extraction
*For any* text input, the keyword extraction function should return a set of lowercase, non-stop-word tokens.
**Validates: Requirements 9.2, 10.1, 10.2, 10.3**

### Property 37: Keyword Comparison
*For any* resume and job description, the analysis should correctly identify matched keywords (intersection) and missing keywords (difference).
**Validates: Requirements 9.3, 9.5**

### Property 38: Match Score Calculation
*For any* resume and job description analysis, the match score should equal (matched_keywords_count / total_jd_keywords_count) × 100 and be between 0 and 100.
**Validates: Requirements 9.4, 10.4, 10.5**

### Property 39: Suggestion Generation
*For any* analysis with missing keywords, the system should generate suggestions for improvement.
**Validates: Requirements 9.6**

### Property 40: PDF Generation
*For any* resume, exporting to PDF should produce a valid PDF file that can be downloaded.
**Validates: Requirements 11.1, 11.3**

### Property 41: PDF Text Selectability
*For any* generated PDF, the text content should be selectable (not rendered as images).
**Validates: Requirements 11.5**

### Property 42: Resume Edit Data Loading
*For any* resume, loading it for editing should retrieve all associated sections (personal info, experiences, education, skills, projects).
**Validates: Requirements 12.1**

### Property 43: Resume Duplication
*For any* resume, duplicating it should create a new resume with a different ID but identical content in all sections.
**Validates: Requirements 12.2**

### Property 44: Resume Cascade Deletion
*For any* resume, deleting it should also remove all associated sections (personal info, experiences, education, skills, projects) from the database.
**Validates: Requirements 12.3, 14.5**

### Property 45: Dashboard Resume Display Fields
*For any* resume displayed on the dashboard, the rendered card should contain the resume title, template name, and last updated timestamp.
**Validates: Requirements 12.5, 18.3**

### Property 46: CSRF Token Validation
*For any* form submission without a valid CSRF token, the system should reject the request.
**Validates: Requirements 13.1**

### Property 47: Resume Authorization
*For any* user attempting to access a resume, the system should verify the resume belongs to that user before allowing access.
**Validates: Requirements 13.3, 13.4**

### Property 48: Form Validation
*For any* form submission with invalid data, the system should perform server-side validation and return field-specific error messages.
**Validates: Requirements 14.1, 14.2**

### Property 49: Length Limit Validation
*For any* form field with a maximum length, submitting input exceeding that length should be rejected with an error.
**Validates: Requirements 14.3**

### Property 50: XSS Input Sanitization
*For any* user input containing potential XSS payloads (script tags, event handlers), the system should sanitize the input before storage or display.
**Validates: Requirements 14.4**

### Property 51: Template Selection and Storage
*For any* resume creation or update with a template selection, the system should store the template identifier with the resume.
**Validates: Requirements 16.2, 16.5**

### Property 52: Resume Text Aggregation Completeness
*For any* resume, the aggregated text should include content from personal information, all experiences, all education entries, all skills, and all projects.
**Validates: Requirements 17.1, 17.2, 17.3, 17.4, 17.5, 17.6**

### Property 53: Login Redirect
*For any* successful login, the system should redirect the user to the dashboard.
**Validates: Requirements 18.1**

### Property 54: Dashboard Resume Ordering
*For any* user's dashboard, resumes should be displayed in reverse chronological order by last updated timestamp.
**Validates: Requirements 18.2**

## Error Handling

### Validation Errors

**Client-Side Validation**:
- HTML5 form validation for basic checks (required fields, email format, URL format)
- JavaScript validation for immediate feedback
- Does not replace server-side validation

**Server-Side Validation**:
- Django form validation using Form classes
- Model validation using Model.clean() methods
- Custom validators for business logic (date ranges, duplicate skills)

**Error Response Format**:
```python
{
    'field_name': ['Error message 1', 'Error message 2'],
    'another_field': ['Error message']
}
```

**Error Display**:
- Display errors next to relevant form fields
- Use Bootstrap alert classes for styling
- Preserve user input on validation failure

### Database Errors

**Integrity Errors**:
- Catch IntegrityError for unique constraint violations
- Convert to user-friendly messages
- Example: "A skill with this name already exists on this resume"

**Foreign Key Violations**:
- Should not occur due to CASCADE delete
- If occurs, log error and display generic message

**Connection Errors**:
- Catch database connection errors
- Display maintenance message to user
- Log error for admin investigation

### Authentication Errors

**Invalid Credentials**:
- Display generic message: "Invalid username or password"
- Do not reveal which field is incorrect (security)
- Rate limit login attempts (Django built-in)

**Session Expiration**:
- Redirect to login page
- Display message: "Your session has expired. Please log in again."
- Preserve intended destination for post-login redirect

**Permission Denied**:
- Return 403 Forbidden status
- Display message: "You do not have permission to access this resource"
- Log unauthorized access attempts

### PDF Generation Errors

**Template Rendering Errors**:
- Catch template syntax errors
- Log error with stack trace
- Display message: "Unable to generate PDF. Please try again."

**WeasyPrint Errors**:
- Catch PDF generation exceptions
- Log error details
- Display message: "PDF generation failed. Please contact support."

**Missing Data Errors**:
- Validate resume has minimum required data before PDF generation
- Display message: "Please add personal information before exporting"

### ATS Analysis Errors

**Empty Input**:
- Validate job description is not empty
- Display message: "Please enter a job description"

**Processing Errors**:
- Catch exceptions in keyword extraction or analysis
- Log error details
- Display message: "Analysis failed. Please try again."

**Invalid Resume State**:
- Validate resume has content before analysis
- Display message: "Please add content to your resume before analysis"

## Testing Strategy

### Testing Approach

The testing strategy employs both unit tests and property-based tests to ensure comprehensive coverage:

- **Unit Tests**: Validate specific examples, edge cases, and integration points
- **Property-Based Tests**: Verify universal properties hold across all inputs using randomized testing

### Property-Based Testing Configuration

**Library**: Hypothesis (Python property-based testing library)

**Configuration**:
- Minimum 100 iterations per property test
- Each test tagged with format: **Feature: ats-resume-builder, Property {number}: {property_text}**
- Tests reference design document properties

**Example Test Structure**:
```python
from hypothesis import given, strategies as st
from hypothesis import settings

@settings(max_examples=100)
@given(
    username=st.text(min_size=3, max_size=150),
    email=st.emails(),
    password=st.text(min_size=8, max_size=128)
)
def test_user_registration_creates_account(username, email, password):
    """
    Feature: ats-resume-builder, Property 1: User Registration Creates Account
    For any valid registration data, submitting the registration form should 
    create a new user account in the database with hashed password.
    """
    # Test implementation
```

### Test Organization

**Directory Structure**:
```
apps/
├── authentication/
│   ├── tests/
│   │   ├── test_models.py
│   │   ├── test_views.py
│   │   ├── test_forms.py
│   │   └── test_properties.py  # Property-based tests
├── resumes/
│   ├── tests/
│   │   ├── test_models.py
│   │   ├── test_views.py
│   │   ├── test_services.py
│   │   └── test_properties.py
└── analyzer/
    ├── tests/
    │   ├── test_services.py
    │   └── test_properties.py
```

### Unit Test Coverage

**Model Tests**:
- Test model creation with valid data
- Test model validation rules
- Test model methods and properties
- Test cascade deletion behavior

**View Tests**:
- Test GET requests return correct templates
- Test POST requests with valid data
- Test POST requests with invalid data
- Test authentication requirements
- Test authorization checks

**Form Tests**:
- Test form validation with valid data
- Test form validation with invalid data
- Test custom validators
- Test form field requirements

**Service Tests**:
- Test business logic functions
- Test data transformation
- Test error handling
- Test integration between components

### Property-Based Test Coverage

**Authentication Properties** (Properties 1-6):
- User registration, login, logout flows
- Access control and session management

**Resume Management Properties** (Properties 7-9, 42-45):
- Resume CRUD operations
- Data association and retrieval

**Section Management Properties** (Properties 10-33):
- Personal info, experience, education, skill, project CRUD
- Validation rules and constraints

**Rendering Properties** (Properties 34-35, 51):
- Template application and rendering
- Conditional display logic

**ATS Analysis Properties** (Properties 36-39, 52):
- Keyword extraction and matching
- Score calculation
- Text aggregation

**PDF Export Properties** (Properties 40-41):
- PDF generation and format

**Security Properties** (Properties 46-47, 50):
- CSRF protection
- Authorization checks
- Input sanitization

**Validation Properties** (Properties 48-49):
- Form validation
- Length limits

**Dashboard Properties** (Properties 53-54):
- Navigation and display ordering

### Integration Testing

**End-to-End Flows**:
- Complete resume creation workflow
- Resume editing and updating
- ATS analysis workflow
- PDF export workflow

**Database Integration**:
- Test transactions and rollbacks
- Test cascade operations
- Test query performance with realistic data volumes

### Test Data Generation

**Hypothesis Strategies**:
```python
# Custom strategies for domain objects
@st.composite
def resume_data(draw):
    return {
        'title': draw(st.text(min_size=1, max_size=200)),
        'template': draw(st.sampled_from(['professional', 'modern', 'classic']))
    }

@st.composite
def experience_data(draw):
    start_date = draw(st.dates(min_value=date(1970, 1, 1)))
    end_date = draw(st.one_of(
        st.none(),
        st.dates(min_value=start_date)
    ))
    return {
        'company': draw(st.text(min_size=1, max_size=200)),
        'role': draw(st.text(min_size=1, max_size=200)),
        'start_date': start_date,
        'end_date': end_date,
        'description': draw(st.text(min_size=1, max_size=2000))
    }
```

### Test Execution

**Running Tests**:
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.authentication

# Run property-based tests only
python manage.py test --tag=property

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

**Continuous Integration**:
- Run full test suite on every commit
- Require all tests to pass before merge
- Track code coverage metrics
- Run property tests with increased iterations in CI (500+)

### Performance Testing

**Load Testing**:
- Test concurrent user access
- Test database query performance
- Test PDF generation under load
- Test ATS analysis performance

**Benchmarks**:
- Page load time < 2 seconds
- ATS analysis < 1 second
- PDF generation < 3 seconds

**Tools**:
- Django Debug Toolbar for query analysis
- Locust or Apache JMeter for load testing
- cProfile for Python profiling
