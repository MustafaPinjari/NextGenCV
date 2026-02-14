# Implementation Plan: NextGenCV v2.0 Advanced Features

## Overview

This implementation plan builds upon the existing ATS Resume Builder to add advanced features including PDF upload/parsing, AI-powered optimization, version control, and comprehensive analytics. The implementation follows a modular approach, building each major feature incrementally while maintaining the existing system's functionality.

## Implementation Strategy

1. **Non-Breaking Changes**: All new features are additive and don't modify existing functionality
2. **Service Layer First**: Build service layer before views to enable testing
3. **Incremental Rollout**: Each module can be deployed independently
4. **Database Migrations**: Careful migration strategy to add new tables without disrupting existing data

## Tasks

- [x] 1. Project Setup and Dependencies
  - Add new dependencies to requirements.txt: pdfplumber, spaCy, python-docx
  - Download spaCy language model: `python -m spacy download en_core_web_sm`
  - Create new Django apps: `analytics`, `templates_mgmt`
  - Update project structure with service layer directories
  - _Requirements: All (foundational)_

- [x] 2. Database Schema Updates
  - [x] 2.1 Create ResumeVersion model and migration
    - Define model with all fields (version_number, snapshot_data, etc.)
    - Add indexes on (resume_id, created_at)
    - Add unique constraint on (resume_id, version_number)
    - _Requirements: 1.1, 1.6_

  - [x] 2.2 Create UploadedResume model and migration
    - Define model with file handling fields
    - Add FileField for PDF storage
    - Add JSONField for parsed_data
    - Add indexes on (user_id, uploaded_at)
    - _Requirements: 3.1, 3.6_

  - [x] 2.3 Create ResumeAnalysis model and migration
    - Define model with all score component fields
    - Add JSONField for detailed analysis data
    - Add indexes on (resume_id, analysis_timestamp)
    - _Requirements: 6.1, 6.7, 6.8_

  - [x] 2.4 Create OptimizationHistory model and migration
    - Define model with version references
    - Add JSONField for changes tracking
    - Add foreign keys to ResumeVersion
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

  - [x] 2.5 Create ResumeTemplate and TemplateCustomization models
    - Define template model with metadata
    - Define customization model with user preferences
    - Add unique constraint on (resume_id) for customization
    - _Requirements: 13.1, 13.2, 13.6, 14.1, 14.5_

  - [x] 2.6 Add fields to existing Resume model
    - Add current_version_number field
    - Add last_analyzed_at timestamp
    - Add last_optimized_at timestamp
    - Create migration with default values
    - _Requirements: 1.1, 6.8, 8.8_

- [x] 3. Service Layer - PDF Processing
  - [x] 3.1 Create PDFParserService
    - Implement extract_text_from_pdf() using pdfplumber
    - Implement clean_extracted_text() with sanitization
    - Implement calculate_parsing_confidence()
    - Handle multi-column layouts
    - _Requirements: 3.4, 3.5, 5.5_

  - [x] 3.2 Create SectionParserService
    - Implement identify_sections() with regex patterns
    - Implement parse_personal_info() with entity extraction
    - Implement parse_experiences() with date/company extraction
    - Implement parse_education() with institution extraction
    - Implement parse_skills() with categorization
    - Use spaCy for NER (Named Entity Recognition)
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.7_

  - [x] 3.3 Create file validation utilities
    - Implement validate_pdf_file() with type/size checks
    - Implement has_embedded_scripts() scanner
    - Implement secure_filename_generator()
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_

- [x] 4. Service Layer - NLP and Scoring
  - [x] 4.1 Create KeywordExtractorService
    - Implement extract_keywords() using spaCy
    - Implement calculate_keyword_frequency()
    - Implement weight_keywords_by_importance()
    - Remove stop words and short tokens
    - Extract noun phrases
    - _Requirements: 6.1, 8.2_

  - [x] 4.2 Create ActionVerbAnalyzerService
    - Define STRONG_ACTION_VERBS list
    - Define WEAK_VERBS list
    - Implement analyze_action_verbs()
    - Implement calculate_action_verb_score()
    - _Requirements: 6.6, 8.2_

  - [x] 4.3 Create QuantificationDetectorService
    - Implement detect_quantifications() with regex
    - Implement has_quantification() checker
    - Implement calculate_quantification_score()
    - Detect numbers, percentages, dollar amounts
    - _Requirements: 6.5, 8.4_

  - [x] 4.4 Create ScoringEngineService
    - Implement calculate_ats_score() main function
    - Implement calculate_keyword_match_score()
    - Implement calculate_skill_relevance_score()
    - Implement calculate_section_completeness_score()
    - Implement calculate_experience_impact_score()
    - Apply weighted formula (30%, 20%, 15%, 15%, 10%, 10%)
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_

- [x] 5. Service Layer - Resume Optimization
  - [x] 5.1 Create BulletPointRewriterService
    - Implement rewrite_bullet_point() with verb replacement
    - Implement select_strong_verb() based on context
    - Implement starts_with_action_verb() checker
    - Use action verb lists from ActionVerbAnalyzerService
    - _Requirements: 8.2_

  - [x] 5.2 Create KeywordInjectorService
    - Implement inject_keywords() with natural placement
    - Implement find_best_injection_point()
    - Implement inject_keyword_naturally() with templates
    - Prioritize keywords by frequency in job description
    - _Requirements: 8.3_

  - [x] 5.3 Create QuantificationSuggesterService
    - Implement suggest_quantification() with templates
    - Implement classify_achievement() by type
    - Provide metric suggestions by achievement type
    - _Requirements: 8.4_

  - [x] 5.4 Create FormattingStandardizerService
    - Implement standardize_section_headings()
    - Implement standardize_date_formats()
    - Implement remove_problematic_formatting()
    - _Requirements: 8.5_

  - [x] 5.5 Create ResumeOptimizerService (orchestrator)
    - Implement optimize_resume() main function
    - Coordinate all optimization sub-services
    - Generate detailed_changes list
    - Calculate improvement delta
    - _Requirements: 8.1, 8.7, 8.8, 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 6. Service Layer - Versioning and Analytics
  - [x] 6.1 Create VersionService
    - Implement create_version() with snapshot serialization
    - Implement get_version_history() with ordering
    - Implement compare_versions() with diff generation
    - Implement restore_version() creating new version
    - Auto-increment version numbers
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5_

  - [x] 6.2 Create AnalyticsService
    - Implement calculate_resume_health() with weighted components
    - Implement get_score_trends() with moving average
    - Implement get_top_missing_keywords() with aggregation
    - Implement generate_improvement_report()
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 12.1, 12.2, 12.3, 12.4, 12.5, 12.6_

  - [x] 6.3 Create TrendAnalysisService
    - Implement calculate_moving_average()
    - Implement calculate_improvement_rate()
    - Implement identify_trend_direction()
    - _Requirements: 11.3, 11.6_

- [x] 7. Views and URLs - PDF Upload Module
  - [x] 7.1 Create pdf_upload view (GET/POST)
    - Display upload form
    - Validate uploaded file
    - Save to UploadedResume model
    - Extract text using PDFParserService
    - Parse sections using SectionParserService
    - Redirect to review page
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 4.8_

  - [x] 7.2 Create pdf_parse_review view
    - Load UploadedResume
    - Display parsed data in editable form
    - Show parsing confidence score
    - Allow inline editing of extracted data
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [x] 7.3 Create pdf_import_confirm view
    - Create Resume from parsed data
    - Create initial ResumeVersion
    - Run initial ATS analysis
    - Redirect to resume detail
    - _Requirements: 4.8, 5.4_

  - [x] 7.4 Add URL patterns for PDF upload
    - /resumes/upload/
    - /resumes/upload/<id>/review/
    - /resumes/upload/<id>/confirm/
    - _Requirements: All PDF upload requirements_

- [ ] 8. Views and URLs - Resume Optimization Module
  - [ ] 8.1 Create fix_resume view (GET/POST)
    - Display job description form
    - Store job description in session
    - Redirect to optimization processing
    - _Requirements: 8.1_

  - [ ] 8.2 Create fix_preview view
    - Load resume and job description
    - Run ResumeOptimizerService
    - Calculate new score
    - Store results in session
    - Display side-by-side comparison
    - Show improvement delta
    - _Requirements: 9.1, 9.2, 9.3, 9.4_

  - [ ] 8.3 Create fix_accept view
    - Create new ResumeVersion with optimized data
    - Create OptimizationHistory record
    - Clear session
    - Redirect to resume detail
    - _Requirements: 9.6, 10.1, 10.2, 10.3_

  - [ ] 8.4 Create fix_reject view
    - Clear session
    - Redirect to resume detail
    - _Requirements: 9.5_

  - [ ] 8.5 Add URL patterns for optimization
    - /resumes/<id>/fix/
    - /resumes/<id>/fix/preview/
    - /resumes/<id>/fix/accept/
    - /resumes/<id>/fix/reject/
    - _Requirements: All optimization requirements_

- [ ] 9. Views and URLs - Version Management Module
  - [ ] 9.1 Create version_list view
    - Load all versions for resume
    - Display version history with metadata
    - Show version numbers, dates, scores
    - _Requirements: 1.3, 1.6_

  - [ ] 9.2 Create version_detail view
    - Load specific version
    - Display read-only view of historical state
    - Show version metadata
    - _Requirements: 1.4_

  - [ ] 9.3 Create version_compare view
    - Load two versions
    - Generate diff using VersionService
    - Display side-by-side comparison
    - Highlight additions/deletions/modifications
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [ ] 9.4 Create version_restore view
    - Create new version from historical version
    - Redirect to resume edit
    - _Requirements: 1.5_

  - [ ] 9.5 Add URL patterns for versioning
    - /resumes/<id>/versions/
    - /resumes/<id>/versions/<version_id>/
    - /resumes/<id>/versions/compare/
    - /resumes/<id>/versions/<version_id>/restore/
    - _Requirements: All versioning requirements_

- [ ] 10. Views and URLs - Analytics Dashboard Module
  - [ ] 10.1 Create analytics_dashboard view
    - Calculate resume health using AnalyticsService
    - Get score trends
    - Get top missing keywords
    - Prepare chart data (JSON for Chart.js)
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7_

  - [ ] 10.2 Create analytics_trends view
    - Load all analyses for user
    - Calculate detailed trends
    - Generate trend charts
    - _Requirements: 11.3, 11.6_

  - [ ] 10.3 Create improvement_report view
    - Generate comprehensive report
    - Show optimization history
    - Display recommendations
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7_

  - [ ] 10.4 Add URL patterns for analytics
    - /analytics/dashboard/
    - /analytics/trends/
    - /analytics/improvement-report/
    - _Requirements: All analytics requirements_

- [ ] 11. Templates - PDF Upload Module
  - [ ] 11.1 Create pdf_upload.html template
    - File upload form with drag-and-drop
    - File type and size validation messages
    - Progress indicator
    - Bootstrap styling
    - _Requirements: 3.1, 3.2, 3.3_

  - [ ] 11.2 Create parse_review.html template
    - Display parsed sections in editable forms
    - Show parsing confidence score
    - Highlight low-confidence sections
    - Allow inline editing
    - Confirm/cancel buttons
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ] 12. Templates - Optimization Module
  - [ ] 12.1 Create fix_resume.html template
    - Job description textarea
    - Instructions and tips
    - Submit button
    - _Requirements: 8.1_

  - [ ] 12.2 Create fix_comparison.html template
    - Side-by-side comparison layout
    - Original vs optimized columns
    - Highlight changes with color coding
    - Show improvement delta prominently
    - List of changes by category
    - Accept/reject buttons
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ] 13. Templates - Version Management Module
  - [ ] 13.1 Create version_list.html template
    - Timeline view of versions
    - Version cards with metadata
    - Compare and restore buttons
    - _Requirements: 1.3, 1.6_

  - [ ] 13.2 Create version_detail.html template
    - Read-only resume view
    - Version metadata display
    - Restore button
    - _Requirements: 1.4_

  - [ ] 13.3 Create version_compare.html template
    - Side-by-side comparison
    - Diff highlighting (green/red)
    - Section-by-section navigation
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ] 14. Templates - Analytics Dashboard Module
  - [ ] 14.1 Create analytics_dashboard.html template
    - Resume health meter (progress bar)
    - Score trend chart (Chart.js)
    - Top missing keywords list
    - Section completeness indicators
    - Quick stats cards
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

  - [ ] 14.2 Create analytics_trends.html template
    - Detailed trend charts
    - Moving average visualization
    - Improvement rate display
    - _Requirements: 11.3, 11.6_

  - [ ] 14.3 Create improvement_report.html template
    - Comprehensive report layout
    - Optimization history table
    - Recommendations list
    - Export to PDF button
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7_

- [ ] 15. Template Management System
  - [ ] 15.1 Create additional resume templates
    - Create modern.html template (already exists, enhance)
    - Create classic.html template (already exists, enhance)
    - Create creative.html template (new)
    - Create minimal.html template (new)
    - _Requirements: 13.5_

  - [ ] 15.2 Create TemplateService
    - Implement get_all_templates()
    - Implement get_template_by_id()
    - Implement generate_preview_with_sample_data()
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6_

  - [ ] 15.3 Create CustomizationService
    - Implement apply_customization()
    - Implement apply_color_scheme()
    - Implement apply_font_family()
    - Implement inject_custom_css()
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_

  - [ ] 15.4 Create template_gallery view
    - Display all active templates
    - Show thumbnails
    - Preview button for each
    - _Requirements: 13.1, 13.2, 13.3, 13.4_

  - [ ] 15.5 Create template_preview view
    - Generate preview with sample data
    - Display in modal or full page
    - Select button
    - _Requirements: 13.6_

  - [ ] 15.6 Create template_customize view
    - Color scheme selector
    - Font family selector
    - Custom CSS textarea
    - Live preview
    - Save customization
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_

- [ ] 16. Enhanced Export Features
  - [ ] 16.1 Add DOCX export support
    - Install python-docx library
    - Create DOCXExportService
    - Implement generate_docx() method
    - Maintain formatting in DOCX
    - _Requirements: 21.2, 21.5_

  - [ ] 16.2 Add plain text export
    - Create TextExportService
    - Implement generate_text() method
    - Format for ATS parsing
    - _Requirements: 21.3_

  - [ ] 16.3 Add version-specific export
    - Modify export views to accept version parameter
    - Allow exporting any historical version
    - _Requirements: 21.6_

  - [ ] 16.4 Create batch export functionality
    - Create batch_export view
    - Allow selecting multiple resumes
    - Generate ZIP file with all exports
    - _Requirements: 22.1, 22.4_

- [ ] 17. Security Enhancements
  - [ ] 17.1 Implement file upload security
    - Add file type validation
    - Add MIME type verification
    - Add file size limits
    - Add embedded script scanner
    - _Requirements: 15.1, 15.2, 15.3, 15.4_

  - [ ] 17.2 Implement secure file storage
    - Generate secure random filenames
    - Store files outside web root
    - Implement access control checks
    - _Requirements: 15.5, 15.6_

  - [ ] 17.3 Implement text sanitization
    - Add bleach library for HTML sanitization
    - Sanitize all extracted text
    - Remove control characters
    - _Requirements: 15.7_

  - [ ] 17.4 Implement data isolation
    - Add authorization checks to all views
    - Filter queries by user
    - Prevent cross-user data access
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5_

  - [ ] 17.5 Implement cascade deletion
    - Ensure proper CASCADE on foreign keys
    - Test deletion of user deletes all data
    - _Requirements: 16.6_

- [ ] 18. Performance Optimization
  - [ ] 18.1 Add database indexes
    - Add indexes to all new models
    - Add composite indexes for common queries
    - Test query performance
    - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.5_

  - [ ] 18.2 Implement query optimization
    - Use select_related for foreign keys
    - Use prefetch_related for reverse relations
    - Optimize N+1 query problems
    - _Requirements: 18.2_

  - [ ] 18.3 Implement caching
    - Add cache for resume health scores
    - Add cache for analytics data
    - Set appropriate cache timeouts
    - _Requirements: 18.3_

  - [ ] 18.4 Add performance monitoring
    - Install django-silk
    - Configure profiling
    - Monitor slow queries
    - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5_

- [ ] 19. User Experience Enhancements
  - [ ] 19.1 Add guided tutorials
    - Create tutorial overlays for new features
    - Add contextual help tooltips
    - Create help documentation
    - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.5_

  - [ ] 19.2 Implement responsive design
    - Test all new pages on mobile
    - Adjust layouts for tablet
    - Ensure touch-friendly interactions
    - _Requirements: 20.1, 20.2, 20.3, 20.4, 20.5_

  - [ ] 19.3 Add progress indicators
    - Add loading spinners for long operations
    - Add progress bars for file uploads
    - Add progress indicators for optimization
    - _Requirements: 22.4_

- [ ] 20. Testing and Quality Assurance
  - [ ] 20.1 Write unit tests for services
    - Test KeywordExtractorService
    - Test ScoringEngineService
    - Test ResumeOptimizerService
    - Test PDFParserService
    - Test VersionService
    - Test AnalyticsService
    - Aim for 80%+ code coverage
    - _Requirements: All_

  - [ ] 20.2 Write integration tests
    - Test PDF upload flow end-to-end
    - Test optimization flow end-to-end
    - Test version management flow
    - Test analytics dashboard
    - _Requirements: All_

  - [ ] 20.3 Write property-based tests
    - Test optimization preserves meaning
    - Test version comparison symmetry
    - Test score bounds
    - Test data isolation
    - _Requirements: All_

  - [ ] 20.4 Perform security testing
    - Test file upload validation
    - Test XSS protection
    - Test authorization checks
    - Test data isolation
    - _Requirements: All security requirements_

  - [ ] 20.5 Perform performance testing
    - Test with large PDF files
    - Test with many versions
    - Test concurrent users
    - Measure response times
    - _Requirements: All performance requirements_

- [ ] 21. Documentation and Deployment
  - [ ] 21.1 Update documentation
    - Update README with new features
    - Document new API endpoints
    - Create user guide for new features
    - Document service layer architecture
    - _Requirements: All_

  - [ ] 21.2 Create deployment guide
    - Document deployment steps
    - Document environment variables
    - Document dependency installation
    - Create deployment checklist
    - _Requirements: All_

  - [ ] 21.3 Perform final testing
    - Run full test suite
    - Perform manual testing
    - Test on staging environment
    - Get user feedback
    - _Requirements: All_

- [ ] 22. Final Checkpoint - NextGenCV v2.0 Complete
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- This is a major expansion building on the existing system
- Each module can be developed and deployed incrementally
- Service layer should be built before views for better testability
- All new features are additive and don't break existing functionality
- Security and performance are integrated throughout
- The architecture supports future migration to PostgreSQL and microservices
- Property-based tests ensure correctness of complex algorithms
- Comprehensive error handling and user feedback at every step
