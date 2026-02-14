# Implementation Plan: ATS Resume Builder

## Overview

This implementation plan builds a complete ATS Optimized Resume Builder using Django, SQLite, Bootstrap, and WeasyPrint. The implementation follows a layered architecture with clear separation between presentation, application, and data layers. Tasks are organized to build foundational components first, then layer on features incrementally, with testing integrated throughout.

## Tasks

- [x] 1. Project Setup and Configuration
  - Create Django project structure with apps: authentication, resumes, analyzer
  - Configure settings.py with database, static files, templates, security settings
  - Set up requirements.txt with Django, WeasyPrint, Hypothesis, Bootstrap
  - Create base template with Bootstrap CSS and navigation structure
  - Configure URL routing for all apps
  - _Requirements: All (foundational)_

- [x] 2. Database Models and Migrations
  - [x] 2.1 Create Resume models (Resume, PersonalInfo, Experience, Education, Skill, Project)
    - Define all model fields with appropriate types and constraints
    - Add foreign key relationships with CASCADE delete
    - Add unique constraints (resume + skill name)
    - Add ordering meta options for chronological display
    - Add database indexes for performance
    - _Requirements: 2.1, 3.1, 4.1, 5.1, 6.1, 7.1, 14.5_

  - [ ]* 2.2 Write property test for model constraints
    - **Property 44: Resume Cascade Deletion**
    - **Validates: Requirements 12.3, 14.5**

  - [x] 2.3 Create and run initial migrations
    - Generate migration files for all models
    - Apply migrations to create database schema
    - _Requirements: All (foundational)_

- [x] 3. Authentication System
  - [x] 3.1 Implement user registration view and form
    - Create UserRegistrationForm with username, email, password fields
    - Create RegisterView to handle GET (display form) and POST (process registration)
    - Add password hashing using Django's default authentication
    - Add validation for unique username and email
    - _Requirements: 1.1, 1.2, 13.2_

  - [ ] 3.2 Write property tests for registration
    - **Property 1: User Registration Creates Account**
    - **Validates: Requirements 1.1, 13.2**
    - **Property 2: Duplicate Registration Rejection**
    - **Validates: Requirements 1.2**

  - [x] 3.3 Configure Django built-in login and logout views
    - Set up URL patterns for login, logout
    - Create login template with form
    - Configure LOGIN_URL and LOGIN_REDIRECT_URL in settings
    - _Requirements: 1.3, 1.4, 1.5, 18.1_

  - [ ]* 3.4 Write property tests for authentication
    - **Property 3: Valid Login Authentication**
    - **Validates: Requirements 1.3**
    - **Property 4: Invalid Login Rejection**
    - **Validates: Requirements 1.4**
    - **Property 5: Logout Session Termination**
    - **Validates: Requirements 1.5**
    - **Property 53: Login Redirect**
    - **Validates: Requirements 18.1**

  - [x] 3.5 Implement authentication middleware and decorators
    - Apply @login_required decorator to protected views
    - Configure middleware for CSRF protection
    - _Requirements: 1.6, 13.1, 13.5_

  - [ ]* 3.6 Write property tests for access control
    - **Property 6: Protected Resource Access Control**
    - **Validates: Requirements 1.6, 13.5**
    - **Property 46: CSRF Token Validation**
    - **Validates: Requirements 13.1**

- [x] 4. Resume Management - Core CRUD
  - [x] 4.1 Create ResumeService class for business logic
    - Implement create_resume(user, data) method
    - Implement get_user_resumes(user) method
    - Implement update_resume(resume_id, data) method
    - Implement delete_resume(resume_id) method
    - Implement duplicate_resume(resume_id) method
    - _Requirements: 2.2, 2.3, 12.1, 12.2, 12.3_

  - [ ]* 4.2 Write property tests for resume operations
    - **Property 7: Resume Creation and Association**
    - **Validates: Requirements 2.2**
    - **Property 8: Resume Unique Identifier Assignment**
    - **Validates: Requirements 2.3**
    - **Property 43: Resume Duplication**
    - **Validates: Requirements 12.2**

  - [x] 4.3 Create ResumeListView (Dashboard)
    - Display all user's resumes ordered by updated_at descending
    - Show resume title, template, last updated timestamp
    - Add links to edit, analyze, export, duplicate, delete
    - Handle empty state with welcome message
    - _Requirements: 2.4, 12.5, 18.2, 18.3, 18.5_

  - [ ]* 4.4 Write property tests for dashboard
    - **Property 9: Dashboard Resume Display**
    - **Validates: Requirements 2.4, 13.3**
    - **Property 45: Dashboard Resume Display Fields**
    - **Validates: Requirements 12.5, 18.3**
    - **Property 54: Dashboard Resume Ordering**
    - **Validates: Requirements 18.2**

  - [x] 4.5 Create ResumeCreateView with wizard interface
    - Implement multi-step form for resume creation
    - Step 1: Resume title and template selection
    - Step 2: Personal information
    - Step 3: Experience entries (allow multiple)
    - Step 4: Education entries (allow multiple)
    - Step 5: Skills (allow multiple)
    - Step 6: Projects (allow multiple)
    - Step 7: Review and save
    - _Requirements: 2.2, 2.3_

  - [x] 4.6 Create ResumeUpdateView for editing
    - Load existing resume with all sections
    - Allow editing all sections with forms
    - Save changes on submit
    - _Requirements: 12.1_

  - [ ]* 4.7 Write property test for resume editing
    - **Property 42: Resume Edit Data Loading**
    - **Validates: Requirements 12.1**

  - [x] 4.8 Create ResumeDeleteView with confirmation
    - Display confirmation prompt before deletion
    - Delete resume and cascade to all sections
    - Redirect to dashboard after deletion
    - _Requirements: 12.3, 12.4_

  - [x] 4.9 Implement authorization checks for all resume views
    - Verify resume belongs to authenticated user before any operation
    - Return 403 Forbidden if unauthorized
    - _Requirements: 13.3, 13.4_

  - [ ]* 4.10 Write property tests for authorization
    - **Property 47: Resume Authorization**
    - **Validates: Requirements 13.3, 13.4**

- [x] 5. Resume Sections - Personal Information
  - [x] 5.1 Create PersonalInfoForm with validation
    - Add fields: full_name, phone, email, linkedin, github, location
    - Validate email format
    - Validate URL formats for linkedin and github
    - Make full_name and email required
    - _Requirements: 3.1, 3.3, 3.4, 3.5_

  - [ ]* 5.2 Write property tests for personal info
    - **Property 10: Personal Information Storage**
    - **Validates: Requirements 3.1**
    - **Property 11: Personal Information Update Persistence**
    - **Validates: Requirements 3.2**
    - **Property 12: Email Validation**
    - **Validates: Requirements 3.3**
    - **Property 13: URL Validation**
    - **Validates: Requirements 3.4**
    - **Property 14: Personal Information Required Fields**
    - **Validates: Requirements 3.5**

  - [x] 5.3 Integrate personal info form into resume create/update views
    - Add personal info step to creation wizard
    - Add personal info section to update view
    - _Requirements: 3.1, 3.2_

- [x] 6. Resume Sections - Experience
  - [x] 6.1 Create ExperienceForm with validation
    - Add fields: company, role, start_date, end_date, description
    - Allow end_date to be null (current position)
    - Validate start_date is before end_date when both present
    - _Requirements: 4.1, 4.2, 4.5_

  - [ ]* 6.2 Write property tests for experience
    - **Property 15: Experience Entry Storage**
    - **Validates: Requirements 4.1**
    - **Property 16: Current Experience Null End Date**
    - **Validates: Requirements 4.2**
    - **Property 17: Experience Chronological Ordering**
    - **Validates: Requirements 4.3**
    - **Property 18: Experience Deletion**
    - **Validates: Requirements 4.4**
    - **Property 19: Experience Date Validation**
    - **Validates: Requirements 4.5**

  - [x] 6.3 Create views for adding/editing/deleting experience entries
    - Allow multiple experience entries per resume
    - Display experiences in reverse chronological order
    - _Requirements: 4.1, 4.3, 4.4_

- [x] 7. Resume Sections - Education
  - [x] 7.1 Create EducationForm with validation
    - Add fields: institution, degree, field, start_year, end_year
    - Make institution and degree required
    - Validate start_year is before end_year when both present
    - _Requirements: 5.1, 5.4, 5.5_

  - [ ]* 7.2 Write property tests for education
    - **Property 20: Education Entry Storage**
    - **Validates: Requirements 5.1**
    - **Property 21: Education Chronological Ordering**
    - **Validates: Requirements 5.2**
    - **Property 22: Education Deletion**
    - **Validates: Requirements 5.3**
    - **Property 23: Education Year Validation**
    - **Validates: Requirements 5.4**
    - **Property 24: Education Required Fields**
    - **Validates: Requirements 5.5**

  - [x] 7.3 Create views for adding/editing/deleting education entries
    - Allow multiple education entries per resume
    - Display education in reverse chronological order
    - _Requirements: 5.1, 5.2, 5.3_

- [x] 8. Resume Sections - Skills
  - [x] 8.1 Create SkillForm with validation
    - Add fields: name, category
    - Validate skill name is unique per resume
    - Support categories: Technical, Soft Skills, Languages, Tools
    - _Requirements: 6.1, 6.4, 6.5_

  - [ ]* 8.2 Write property tests for skills
    - **Property 25: Skill Storage**
    - **Validates: Requirements 6.1**
    - **Property 26: Skill Category Grouping**
    - **Validates: Requirements 6.2**
    - **Property 27: Skill Deletion**
    - **Validates: Requirements 6.3**
    - **Property 28: Duplicate Skill Prevention**
    - **Validates: Requirements 6.5**

  - [x] 8.3 Create views for adding/editing/deleting skills
    - Allow multiple skills per resume
    - Group skills by category in display
    - _Requirements: 6.1, 6.2, 6.3_

- [-] 9. Resume Sections - Projects
  - [x] 9.1 Create ProjectForm with validation
    - Add fields: name, description, technologies, url
    - Make name and description required
    - Validate URL format if provided
    - _Requirements: 7.1, 7.4, 7.5_

  - [ ]* 9.2 Write property tests for projects
    - **Property 29: Project Entry Storage**
    - **Validates: Requirements 7.1**
    - **Property 30: Project Order Preservation**
    - **Validates: Requirements 7.2**
    - **Property 31: Project Deletion**
    - **Validates: Requirements 7.3**
    - **Property 32: Project URL Validation**
    - **Validates: Requirements 7.4**
    - **Property 33: Project Required Fields**
    - **Validates: Requirements 7.5**

  - [x] 9.3 Create views for adding/editing/deleting projects
    - Allow multiple projects per resume
    - Preserve order of project additions
    - _Requirements: 7.1, 7.2, 7.3_

- [x] 10. Checkpoint - Core Resume Management Complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Resume Template Rendering
  - [x] 11.1 Create professional template (professional.html)
    - Design clean, ATS-friendly layout
    - Use Bootstrap for responsive grid
    - Include sections: personal info, experience, education, skills, projects
    - Hide empty sections conditionally
    - _Requirements: 8.2, 8.4, 16.3_

  - [ ]* 11.2 Write property tests for template rendering
    - **Property 34: Template Application**
    - **Validates: Requirements 8.2, 16.1**
    - **Property 35: Empty Section Hiding**
    - **Validates: Requirements 8.4**
    - **Property 51: Template Selection and Storage**
    - **Validates: Requirements 16.2, 16.5**

  - [x] 11.3 Create ResumeDetailView for preview
    - Render resume using selected template
    - Display formatted preview
    - Add action buttons (edit, analyze, export, duplicate, delete)
    - _Requirements: 8.2, 16.1, 16.2_

- [x] 12. ATS Analyzer - Text Processing
  - [x] 12.1 Create ATSAnalyzerService class
    - Implement aggregate_resume_text(resume) method
    - Concatenate all resume sections with spacing
    - Include: personal info, experiences, education, skills, projects
    - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6_

  - [ ]* 12.2 Write property test for text aggregation
    - **Property 52: Resume Text Aggregation Completeness**
    - **Validates: Requirements 17.1, 17.2, 17.3, 17.4, 17.5, 17.6**

  - [x] 12.3 Implement clean_text(text) method
    - Convert to lowercase
    - Remove punctuation
    - Tokenize by whitespace
    - _Requirements: 10.1, 10.3_

  - [x] 12.4 Implement extract_keywords(text) method
    - Call clean_text to preprocess
    - Remove stop words (use NLTK stopwords or custom list)
    - Filter words with length < 3
    - Return set of unique keywords
    - _Requirements: 9.2, 10.1, 10.2, 10.3_

  - [ ]* 12.5 Write property test for keyword extraction
    - **Property 36: Keyword Extraction**
    - **Validates: Requirements 9.2, 10.1, 10.2, 10.3**

- [x] 13. ATS Analyzer - Matching and Scoring
  - [x] 13.1 Implement calculate_match_score(resume_keywords, jd_keywords) method
    - Calculate matched_keywords = resume_keywords ∩ jd_keywords
    - Calculate missing_keywords = jd_keywords - resume_keywords
    - Calculate score = (|matched_keywords| / |jd_keywords|) × 100
    - Return dict with score, matched_keywords, missing_keywords
    - _Requirements: 9.3, 9.4, 9.5, 10.4, 10.5_

  - [ ]* 13.2 Write property tests for matching and scoring
    - **Property 37: Keyword Comparison**
    - **Validates: Requirements 9.3, 9.5**
    - **Property 38: Match Score Calculation**
    - **Validates: Requirements 9.4, 10.4, 10.5**

  - [x] 13.3 Implement generate_suggestions(missing_keywords) method
    - Create actionable suggestions based on missing keywords
    - Suggest adding keywords to relevant sections
    - _Requirements: 9.6_

  - [ ]* 13.4 Write property test for suggestions
    - **Property 39: Suggestion Generation**
    - **Validates: Requirements 9.6**

  - [x] 13.5 Implement main analyze_resume(resume_id, job_description) method
    - Aggregate resume text
    - Extract resume keywords
    - Extract job description keywords
    - Calculate match score
    - Generate suggestions
    - Return complete analysis result
    - _Requirements: 9.2, 9.3, 9.4, 9.5, 9.6_

- [x] 14. ATS Analyzer - Views and UI
  - [x] 14.1 Create JobDescriptionForm
    - Add textarea for job description input
    - Validate job description is not empty
    - _Requirements: 9.1_

  - [x] 14.2 Create AnalyzeResumeView
    - Display job description form
    - Call ATSAnalyzerService.analyze_resume on submit
    - Display results: match score, matched keywords, missing keywords, suggestions
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

  - [x] 14.3 Create analysis results template
    - Show match score prominently with visual indicator (progress bar)
    - List matched keywords
    - List missing keywords
    - Display suggestions
    - _Requirements: 9.4, 9.5, 9.6_

- [x] 15. Checkpoint - ATS Analysis Complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 16. PDF Export
  - [x] 16.1 Install and configure WeasyPrint
    - Add WeasyPrint to requirements.txt
    - Configure static file handling for PDF generation
    - _Requirements: 11.1_

  - [x] 16.2 Create PDFExportService class
    - Implement render_resume_html(resume) method
    - Use Django template rendering to generate HTML string
    - Apply print-friendly CSS
    - _Requirements: 11.1_

  - [x] 16.3 Implement generate_pdf(resume_id) method
    - Load resume with all sections
    - Render HTML using template
    - Pass HTML to WeasyPrint
    - Generate PDF bytes
    - Return as HttpResponse with content-type application/pdf
    - _Requirements: 11.1, 11.2, 11.3_

  - [ ]* 16.4 Write property tests for PDF export
    - **Property 40: PDF Generation**
    - **Validates: Requirements 11.1, 11.3**
    - **Property 41: PDF Text Selectability**
    - **Validates: Requirements 11.5**

  - [x] 16.5 Create ExportPDFView
    - Call PDFExportService.generate_pdf
    - Set appropriate headers for download
    - Handle errors gracefully
    - _Requirements: 11.3_

  - [x] 16.6 Create print-friendly CSS for PDF templates
    - Use absolute units (pt, px)
    - Ensure text is selectable
    - Avoid complex layouts that break in PDF
    - _Requirements: 11.2, 11.5_

- [x] 17. Form Validation and Security
  - [x] 17.1 Add comprehensive server-side validation to all forms
    - Validate all required fields
    - Validate field lengths against model max_length
    - Validate data types and formats
    - Return field-specific error messages
    - _Requirements: 14.1, 14.2, 14.3_

  - [ ]* 17.2 Write property tests for validation
    - **Property 48: Form Validation**
    - **Validates: Requirements 14.1, 14.2**
    - **Property 49: Length Limit Validation**
    - **Validates: Requirements 14.3**

  - [x] 17.3 Implement XSS protection
    - Use Django's automatic HTML escaping in templates
    - Sanitize user input in forms
    - Test with XSS payloads to verify protection
    - _Requirements: 14.4_

  - [ ]* 17.4 Write property test for XSS protection
    - **Property 50: XSS Input Sanitization**
    - **Validates: Requirements 14.4**

  - [x] 17.5 Ensure CSRF protection on all forms
    - Add {% csrf_token %} to all form templates
    - Verify CSRF middleware is enabled
    - Test form submissions without CSRF token
    - _Requirements: 13.1_

- [x] 18. Static Files and UI Polish
  - [x] 18.1 Create custom CSS for branding and polish
    - Add custom styles on top of Bootstrap
    - Style resume preview for professional appearance
    - Style analysis results display
    - _Requirements: 8.2, 8.3_

  - [x] 18.2 Add JavaScript for enhanced UX
    - Add client-side form validation for immediate feedback
    - Add confirmation dialogs for delete actions
    - Add dynamic form fields for adding multiple entries (experience, education, etc.)
    - _Requirements: 12.4_

  - [x] 18.3 Create landing page for guests
    - Design attractive landing page with feature highlights
    - Add call-to-action buttons for register/login
    - _Requirements: 1.1, 1.3_

  - [x] 18.4 Optimize static file serving
    - Configure static file collection
    - Set up static file caching headers
    - _Requirements: 15.1_

- [x] 19. Error Handling and User Feedback
  - [x] 19.1 Create custom error templates
    - 404 Not Found template
    - 403 Forbidden template
    - 500 Server Error template
    - _Requirements: 13.4_

  - [x] 19.2 Add user feedback messages
    - Success messages for create/update/delete operations
    - Error messages for validation failures
    - Info messages for guidance
    - Use Django messages framework
    - _Requirements: 14.2_

  - [x] 19.3 Implement error logging
    - Configure Django logging
    - Log authentication failures
    - Log authorization violations
    - Log PDF generation errors
    - Log ATS analysis errors
    - _Requirements: All error handling_

- [x] 20. Final Integration and Testing
  - [ ]* 20.1 Run complete property-based test suite
    - Execute all 54 property tests with 100+ iterations each
    - Verify all properties pass
    - Fix any failures discovered

  - [ ]* 20.2 Run unit test suite
    - Execute all unit tests
    - Verify code coverage meets targets
    - Fix any failures

  - [x] 20.3 Perform manual end-to-end testing
    - Test complete user registration and login flow
    - Test complete resume creation workflow
    - Test resume editing and management
    - Test ATS analysis with various job descriptions
    - Test PDF export with different resume content
    - Test error scenarios and edge cases
    - _Requirements: All_

  - [x] 20.4 Performance optimization
    - Add database indexes for frequently queried fields
    - Optimize ORM queries (use select_related, prefetch_related)
    - Test page load times and optimize as needed
    - _Requirements: 15.1, 15.5_

- [x] 21. Final Checkpoint - Project Complete
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at major milestones
- Property tests validate universal correctness properties across all inputs
- Unit tests validate specific examples, edge cases, and integration points
- The implementation follows a bottom-up approach: models → services → views → templates
- Security and validation are integrated throughout, not added as afterthoughts
