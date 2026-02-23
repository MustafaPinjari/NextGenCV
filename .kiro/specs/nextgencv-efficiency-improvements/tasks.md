# Implementation Plan: NextGenCV Efficiency Improvements

## Overview

This task list provides a step-by-step implementation plan for the missing features and efficiency improvements in NextGenCV. Tasks are organized by phase and priority, with each task building on previous work.

## Phase 1: Foundation (Weeks 1-2)

### 1. Complete Resume Health Calculation
- [ ] 1.1 Implement section completeness check
  - Create function to check for presence of personal_info, experiences, education, skills
  - Calculate percentage based on required sections present
  - _Requirements: 7.1, 23.1_

- [ ] 1.2 Implement contact information completeness validation
  - Check for full_name, email, phone in personal_info
  - Calculate completeness score (0-100)
  - _Requirements: 7.2_

- [ ] 1.3 Implement quantified achievement counter
  - Parse experience descriptions for numbers, percentages, dollar amounts
  - Count achievements with vs without quantification
  - Calculate quantification score
  - _Requirements: 7.3_

- [ ] 1.4 Implement action verb strength assessment
  - Create database of strong action verbs (100+ verbs)
  - Create list of weak verbs/phrases ("responsible for", "helped with")
  - Scan experience descriptions for verb usage
  - Calculate action verb strength score
  - _Requirements: 7.4_

- [ ] 1.5 Implement ATS-unfriendly formatting detection
  - Check for tables, text boxes, headers/footers
  - Check for images in text content
  - Check for unusual fonts or formatting
  - Flag any ATS-unfriendly patterns
  - _Requirements: 7.5_

- [ ] 1.6 Create composite health score calculation
  - Combine all component scores with weights
  - Return overall health score (0-100)
  - Update dashboard view to use real calculation
  - _Requirements: 7.6, 7.7_

### 2. Implement Comprehensive ATS Scoring
- [ ] 2.1 Implement keyword match scoring (30% weight)
  - Extract keywords from job description
  - Extract keywords from resume
  - Calculate match percentage
  - Apply 30% weight to final score
  - _Requirements: 6.1_

- [ ] 2.2 Implement skill relevance scoring (20% weight)
  - Extract required skills from job description
  - Compare with resume skills
  - Calculate relevance score
  - Apply 20% weight to final score
  - _Requirements: 6.2_

- [ ] 2.3 Implement section completeness scoring (15% weight)
  - Use section completeness check from health calculation
  - Apply 15% weight to final score
  - _Requirements: 6.3_

- [ ] 2.4 Implement experience impact scoring (15% weight)
  - Analyze experience descriptions for impact keywords
  - Check for leadership, results, achievements
  - Calculate impact score
  - Apply 15% weight to final score
  - _Requirements: 6.4_

- [ ] 2.5 Implement quantification scoring (10% weight)
  - Use quantified achievement counter from health calculation
  - Apply 10% weight to final score
  - _Requirements: 6.5_

- [ ] 2.6 Implement action verb scoring (10% weight)
  - Use action verb strength assessment from health calculation
  - Apply 10% weight to final score
  - _Requirements: 6.6_

- [ ] 2.7 Create weighted composite score calculation
  - Combine all component scores with weights
  - Ensure total equals 100%
  - Store component scores and final score
  - _Requirements: 6.7, 6.8_

- [ ] 2.8 Create score breakdown UI
  - Display individual component scores with progress bars
  - Highlight components below 60%
  - Show specific recommendations for low-scoring components
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

### 3. Create Version History UI
- [ ] 3.1 Create version history list view
  - Display all versions in reverse chronological order
  - Show version number, date, modification type, ATS score
  - Add pagination for resumes with many versions
  - _Requirements: 1.3_

- [ ] 3.2 Implement version detail view
  - Show complete version metadata
  - Display snapshot data in readable format
  - Show user notes if present
  - _Requirements: 1.2_

- [ ] 3.3 Add restore version functionality
  - Add "Restore" button to version history
  - Prompt for confirmation before restoration
  - Create new version based on selected snapshot
  - Mark new version as "restored"
  - Redirect to resume detail after restoration
  - _Requirements: 1.5, 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 3.4 Add delete version functionality
  - Add "Delete" button to version history (optional)
  - Prompt for confirmation before deletion
  - Prevent deletion of current version
  - _Requirements: N/A (optional feature)_

### 4. Checkpoint - Ensure all tests pass
- Ensure all tests pass, ask the user if questions arise.

## Phase 2: Auto-Fix Engine (Weeks 3-5)

### 5. Create Optimization Service Layer
- [ ] 5.1 Create OptimizationService class
  - Set up service structure in `apps/resumes/services/optimization_service.py`
  - Define main optimization method signature
  - Set up error handling and logging
  - _Requirements: 1.1_

- [ ] 5.2 Implement keyword extraction from job description
  - Use NLP library (spacy or nltk) to extract keywords
  - Remove stop words
  - Identify important terms (nouns, verbs, skills)
  - Categorize keywords by type
  - _Requirements: 1.2, 1.3_

- [ ] 5.3 Implement keyword insertion algorithm
  - Identify sections where keywords can be added
  - Generate natural sentences containing keywords
  - Ensure keywords fit contextually
  - Avoid keyword stuffing
  - _Requirements: 1.3_

- [ ] 5.4 Implement action verb replacement logic
  - Detect weak verbs in experience descriptions
  - Match weak verbs to strong alternatives
  - Replace while maintaining sentence structure
  - Ensure grammatical correctness
  - _Requirements: 1.2_

- [ ] 5.5 Implement quantification suggestion logic
  - Detect unquantified achievements
  - Suggest types of metrics to add
  - Generate example quantified statements
  - _Requirements: 1.4_

- [ ] 5.6 Implement section heading standardization
  - Define standard ATS-friendly headings
  - Map non-standard headings to standard ones
  - Update resume sections with standard headings
  - _Requirements: 1.5_

- [ ] 5.7 Create optimization result data structure
  - Define structure for storing changes
  - Include original text, new text, reason, section
  - Calculate improvement score delta
  - _Requirements: 1.7_

### 6. Create Optimization Preview UI
- [ ] 6.1 Create optimization preview template
  - Design side-by-side comparison layout
  - Add sections for original and optimized content
  - Include score improvement display
  - _Requirements: 2.1_

- [ ] 6.2 Implement change highlighting
  - Highlight additions in green
  - Highlight removals in red
  - Show unchanged content in default color
  - _Requirements: 2.2_

- [ ] 6.3 Add explanation tooltips
  - Show reason for each change on hover
  - Include category of change (keyword, verb, quantification)
  - _Requirements: 2.3_

- [ ] 6.4 Implement accept/reject individual changes
  - Add checkbox or button for each change
  - Track which changes are accepted/rejected
  - Update preview based on selections
  - _Requirements: 2.4_

- [ ] 6.5 Add accept all / reject all buttons
  - Implement "Accept All Changes" button
  - Implement "Reject All Changes" button
  - Show confirmation before bulk actions
  - _Requirements: 2.4_

- [ ] 6.6 Show score improvement delta
  - Display original score vs optimized score
  - Show improvement as +X points
  - Use visual indicator (color, icon)
  - _Requirements: 2.3, 2.5_

- [ ] 6.7 Implement save optimized resume
  - Create new resume version with accepted changes
  - Mark version as "optimized"
  - Store optimization metadata
  - Redirect to resume detail after save
  - _Requirements: 2.6, 2.7_

### 7. Create Optimization History Tracking
- [ ] 7.1 Create OptimizationHistory record on optimization
  - Store original version reference
  - Store optimized version reference (after save)
  - Store job description used
  - Store timestamp
  - _Requirements: 3.1, 10.1_

- [ ] 7.2 Store optimization scores
  - Store original score
  - Store optimized score
  - Calculate and store improvement delta
  - _Requirements: 3.2, 10.2_

- [ ] 7.3 Store change summary
  - Count changes by type (keyword, verb, quantification)
  - Store as JSON dictionary
  - _Requirements: 3.5_

- [ ] 7.4 Store detailed changes
  - Store array of change objects
  - Include section, field, old value, new value, reason
  - _Requirements: 3.5_

- [ ] 7.5 Track accepted/rejected changes
  - Store which changes user accepted
  - Store which changes user rejected
  - _Requirements: 3.5_

- [ ] 7.6 Create optimization history list view
  - Display all optimization sessions
  - Show date, job description snippet, score improvement
  - Add pagination for many sessions
  - _Requirements: 3.3, 10.3_

- [ ] 7.7 Create optimization detail view
  - Show complete optimization metadata
  - Display all changes with accept/reject status
  - Show job description used
  - Link to original and optimized versions
  - _Requirements: 3.4, 3.5, 10.4, 10.5_

### 8. Checkpoint - Ensure all tests pass
- Ensure all tests pass, ask the user if questions arise.

## Phase 3: Version Comparison (Week 6)

### 9. Create Version Comparison Interface
- [ ] 9.1 Create version selection UI
  - Add "Compare Versions" button to version history
  - Allow selection of two versions via checkboxes or dropdown
  - Validate that exactly two versions are selected
  - _Requirements: 2.1_

- [ ] 9.2 Create side-by-side comparison view
  - Display both versions in parallel columns
  - Align sections for easy comparison
  - Use responsive layout for mobile
  - _Requirements: 2.1, 2.2_

- [ ] 9.3 Implement content difference highlighting
  - Use diff algorithm to identify changes
  - Highlight added content in green
  - Highlight removed content in red
  - Show unchanged content normally
  - _Requirements: 2.2, 2.4_

- [ ] 9.4 Show score changes between versions
  - Display ATS score for each version
  - Show score delta with +/- indicator
  - Use color coding (green for improvement, red for decline)
  - _Requirements: 2.3_

- [ ] 9.5 Implement section-by-section diff view
  - Allow toggling between full view and section view
  - Show differences for each section separately
  - Highlight which sections changed
  - _Requirements: 2.5_

### 10. Checkpoint - Ensure all tests pass
- Ensure all tests pass, ask the user if questions arise.

## Phase 4: Keyword & Achievement Assistance (Weeks 7-8)

### 11. Create Keyword Suggestion Engine
- [ ] 11.1 Implement industry/role extraction
  - Extract job title from resume
  - Identify industry from experience and skills
  - Use NLP to categorize role and industry
  - _Requirements: 17.1_

- [ ] 11.2 Create keyword database by industry
  - Build database of keywords by industry/role
  - Include technical skills, soft skills, certifications
  - Source from job posting data or industry standards
  - _Requirements: 17.2_

- [ ] 11.3 Implement relevance scoring algorithm
  - Score keywords based on job description match
  - Consider frequency in job postings
  - Factor in user's industry and role
  - _Requirements: 17.4_

- [ ] 11.4 Create keyword categorization logic
  - Categorize keywords (technical, soft skills, certifications)
  - Group related keywords
  - _Requirements: 17.3_

- [ ] 11.5 Implement contextual placement suggestions
  - Suggest which section to add keyword
  - Provide example sentences
  - Ensure natural language flow
  - _Requirements: 18.1, 18.2, 18.4_

- [ ] 11.6 Create keyword suggestion UI
  - Display 10+ keyword suggestions
  - Show relevance score for each
  - Allow filtering by category
  - Add "Add to Resume" button for each keyword
  - _Requirements: 17.2, 17.5, 17.6_

### 12. Create Achievement Quantification Assistant
- [ ] 12.1 Implement unquantified achievement detection
  - Parse experience descriptions
  - Identify statements without numbers/metrics
  - Use NLP to detect achievement patterns
  - Achieve 80%+ detection accuracy
  - _Requirements: 19.1, 19.5_

- [ ] 12.2 Create quantification templates database
  - Build templates for common scenarios
  - Include cost reduction, time savings, team leadership, project completion
  - Store template patterns and prompts
  - _Requirements: 20.2_

- [ ] 12.3 Implement template matching algorithm
  - Match achievements to appropriate templates
  - Consider context and achievement type
  - _Requirements: 20.2_

- [ ] 12.4 Create guided quantification UI
  - Display unquantified achievements
  - Show suggested templates
  - Prompt for specific values (numbers, percentages, timeframes)
  - Generate quantified statement
  - Allow editing before saving
  - _Requirements: 19.2, 19.3, 19.4, 20.3, 20.4, 20.5_

### 13. Create Action Verb Analyzer
- [ ] 13.1 Create strong action verb database
  - Build database of 100+ strong action verbs
  - Categorize by function (leadership, technical, creative, etc.)
  - _Requirements: 21.5_

- [ ] 13.2 Implement weak verb detection
  - Create list of weak verbs and phrases
  - Scan experience descriptions for weak verbs
  - Identify passive voice constructions
  - _Requirements: 21.1, 21.2_

- [ ] 13.3 Implement verb replacement suggestions
  - Suggest 3-5 strong alternatives for each weak verb
  - Maintain original meaning and context
  - Ensure grammatical correctness
  - _Requirements: 21.3, 21.4_

- [ ] 13.4 Implement verb diversity analysis
  - Count verb usage frequency
  - Detect repeated verbs (used 3+ times)
  - Suggest synonyms for repeated verbs
  - _Requirements: 22.1, 22.2, 22.3, 22.4_

- [ ] 13.5 Add verb strength scoring
  - Calculate verb diversity score
  - Include in resume health metrics
  - _Requirements: 22.5_

- [ ] 13.6 Create action verb analysis UI
  - Highlight weak verbs in experience descriptions
  - Show replacement suggestions on click
  - Display verb usage frequency
  - Add "Replace" button for one-click replacement
  - _Requirements: 21.2, 21.3, 21.4_

### 14. Checkpoint - Ensure all tests pass
- Ensure all tests pass, ask the user if questions arise.

## Phase 5: Batch Operations (Week 9)

### 15. Create Multi-Select Interface
- [ ] 15.1 Add checkboxes to resume list
  - Add checkbox to each resume card
  - Style checkboxes to match design system
  - _Requirements: 10.1, 10.2_

- [ ] 15.2 Implement select all/deselect all
  - Add "Select All" button above resume list
  - Add "Deselect All" button
  - Update all checkboxes on click
  - _Requirements: 10.4, 10.5_

- [ ] 15.3 Create batch actions toolbar
  - Show toolbar when resumes are selected
  - Include Export, Analyze, Delete buttons
  - Display selected count
  - _Requirements: 10.3, 10.6_

- [ ] 15.4 Add JavaScript for multi-select
  - Handle checkbox state changes
  - Track selected resume IDs
  - Show/hide toolbar based on selection
  - Update selected count dynamically
  - _Requirements: 10.2, 10.3_

### 16. Implement Batch Export
- [ ] 16.1 Create batch export endpoint
  - Accept list of resume IDs
  - Accept export format (PDF, DOCX, TXT)
  - Validate user owns all selected resumes
  - _Requirements: 11.1_

- [ ] 16.2 Implement batch PDF generation
  - Generate PDF for each selected resume
  - Use existing PDF export service
  - Handle errors gracefully
  - _Requirements: 11.2_

- [ ] 16.3 Create ZIP archive
  - Create ZIP file containing all exported resumes
  - Use resume titles for filenames
  - Handle duplicate filenames
  - _Requirements: 11.3_

- [ ] 16.4 Add progress indicator
  - Show progress bar during batch export
  - Display "Exporting X of Y resumes..."
  - _Requirements: 11.5_

- [ ] 16.5 Implement error handling
  - Track which exports succeed/fail
  - Report failed exports to user
  - Include successful exports in ZIP even if some fail
  - _Requirements: 11.6_

- [ ] 16.6 Provide download link
  - Return ZIP file as download
  - Include format in filename (e.g., "resumes_pdf.zip")
  - _Requirements: 11.4_

### 17. Implement Batch Analysis
- [ ] 17.1 Create batch analysis endpoint
  - Accept list of resume IDs
  - Accept job description
  - Validate user owns all selected resumes
  - _Requirements: 12.1_

- [ ] 17.2 Analyze all selected resumes
  - Run ATS analysis for each resume
  - Use same job description for all
  - Complete within 5 seconds per resume
  - _Requirements: 12.2, 12.6_

- [ ] 17.3 Create comparison table UI
  - Display all resumes in table
  - Show score for each resume
  - Include key metrics (keyword match, section completeness, etc.)
  - _Requirements: 12.3_

- [ ] 17.4 Highlight best-scoring resume
  - Identify resume with highest score
  - Use visual indicator (color, icon, badge)
  - _Requirements: 12.4_

- [ ] 17.5 Show key differences
  - Display what makes top resume better
  - Show missing keywords in lower-scoring resumes
  - _Requirements: 12.5_

### 18. Checkpoint - Ensure all tests pass
- Ensure all tests pass, ask the user if questions arise.

## Phase 6: Template Customization (Week 10)

### 19. Implement Color Scheme Customization
- [ ] 19.1 Add color picker UI
  - Add "Customize Template" button to resume editor
  - Implement color picker component
  - Show current color
  - _Requirements: 13.1, 13.2_

- [ ] 19.2 Implement real-time preview
  - Update resume preview as color changes
  - Apply color to headings, accents, borders
  - _Requirements: 13.3_

- [ ] 19.3 Create preset color schemes
  - Define 4+ preset schemes (Professional Blue, Creative Purple, Modern Green, Classic Black)
  - Allow quick selection of presets
  - _Requirements: 13.6_

- [ ] 19.4 Store color preferences
  - Add color_scheme field to Resume model
  - Save selected color with resume
  - Load color when editing resume
  - _Requirements: 13.4_

- [ ] 19.5 Apply colors in PDF export
  - Update PDF generation to use custom colors
  - Ensure colors are ATS-compatible
  - _Requirements: 13.5_

### 20. Implement Font Selection
- [ ] 20.1 Create ATS-safe font list
  - Define 5+ ATS-safe fonts (Arial, Calibri, Georgia, Times New Roman, Helvetica)
  - Exclude decorative/script fonts
  - _Requirements: 14.2, 14.6_

- [ ] 20.2 Add font selection dropdown
  - Display font options in dropdown
  - Show font preview in dropdown
  - _Requirements: 14.1_

- [ ] 20.3 Implement real-time preview
  - Update resume preview as font changes
  - Apply font to all text
  - _Requirements: 14.3_

- [ ] 20.4 Store font preferences
  - Add font_family field to Resume model
  - Save selected font with resume
  - Load font when editing resume
  - _Requirements: 14.4_

- [ ] 20.5 Embed fonts in PDF export
  - Update PDF generation to use custom font
  - Embed font in PDF for consistency
  - _Requirements: 14.5_

### 21. Checkpoint - Ensure all tests pass
- Ensure all tests pass, ask the user if questions arise.

## Phase 7: Enhanced Export (Week 11)

### 22. Implement DOCX Export
- [ ] 22.1 Install python-docx library
  - Add python-docx to requirements.txt
  - Install dependency
  - _Requirements: 15.2_

- [ ] 22.2 Create DOCX export service
  - Create DOCXExportService class
  - Implement document generation logic
  - _Requirements: 15.2_

- [ ] 22.3 Implement DOCX template rendering
  - Create DOCX template structure
  - Populate with resume data
  - Apply formatting (fonts, colors, spacing)
  - _Requirements: 15.2_

- [ ] 22.4 Preserve formatting in DOCX
  - Maintain section structure
  - Apply bold, italic, bullet points
  - Ensure professional appearance
  - _Requirements: 15.2_

- [ ] 22.5 Apply custom colors/fonts
  - Use resume's color_scheme and font_family
  - Apply to DOCX document
  - _Requirements: 15.2_

- [ ] 22.6 Create DOCX export endpoint
  - Add route for DOCX export
  - Return DOCX file as download
  - Include .docx extension in filename
  - _Requirements: 15.2_

### 23. Implement TXT Export
- [ ] 23.1 Create TXT export service
  - Create TextExportService class
  - Implement plain text generation logic
  - _Requirements: 15.3_

- [ ] 23.2 Implement plain text rendering
  - Convert resume to plain text format
  - Use basic formatting (spacing, bullets, line breaks)
  - Ensure readability
  - _Requirements: 15.3_

- [ ] 23.3 Create TXT export endpoint
  - Add route for TXT export
  - Return TXT file as download
  - Include .txt extension in filename
  - _Requirements: 15.3_

### 24. Implement Version-Specific Export
- [ ] 24.1 Add export button to version history
  - Add "Export" dropdown to each version
  - Show format options (PDF, DOCX, TXT)
  - _Requirements: 16.1_

- [ ] 24.2 Implement version snapshot rendering
  - Load version snapshot data
  - Render using snapshot instead of current data
  - Apply template from snapshot
  - _Requirements: 16.2, 16.4_

- [ ] 24.3 Include version number in filename
  - Append version number to filename
  - Format: "Resume_Title_v3.pdf"
  - _Requirements: 16.3_

- [ ] 24.4 Support all formats for historical versions
  - Enable PDF, DOCX, TXT export for any version
  - Use same export services
  - _Requirements: 16.5_

### 25. Checkpoint - Ensure all tests pass
- Ensure all tests pass, ask the user if questions arise.

## Phase 8: Section Completeness & Polish (Week 12)

### 26. Implement Section Completeness Checker
- [ ] 26.1 Implement required section validation
  - Check for Personal Info, Experience, Education, Skills
  - Identify missing required sections
  - _Requirements: 23.1_

- [ ] 26.2 Create warning banner UI
  - Display warning at top of resume editor
  - List missing sections
  - Explain importance of each section
  - _Requirements: 23.2, 23.3_

- [ ] 26.3 Add navigation to section editor
  - Make warning clickable
  - Navigate to appropriate section editor
  - _Requirements: 23.4_

- [ ] 26.4 Display section completeness percentage
  - Calculate percentage of required sections present
  - Show in dashboard and resume detail
  - _Requirements: 23.5_

- [ ] 26.5 Implement optional section recommendations
  - Recommend optional sections (Projects, Certifications, Publications, Awards)
  - Base recommendations on industry and role
  - Explain benefit of each section
  - Limit to 3 recommendations
  - _Requirements: 24.1, 24.2, 24.4, 24.5_

- [ ] 26.6 Add section from recommendation
  - Add "Add Section" button to recommendations
  - Create section when clicked
  - Navigate to section editor
  - _Requirements: 24.3_

### 27. Enhance Resume Duplication
- [ ] 27.1 Improve duplicate functionality
  - Ensure all sections are copied
  - Append " (Copy)" to title
  - Reset version history (start at version 1)
  - _Requirements: 25.1, 25.2, 25.3, 25.4_

- [ ] 27.2 Optimize duplication performance
  - Use efficient database queries
  - Complete within 2 seconds
  - _Requirements: 25.5, 25.6_

- [ ] 27.3 Redirect to edit page
  - Redirect to resume editor after duplication
  - Show success message
  - _Requirements: 25.5_

### 28. Implement Performance Optimizations
- [ ] 28.1 Add database indexes
  - Add index on (user_id, updated_at) for Resume
  - Add index on (resume_id, created_at) for ResumeVersion
  - Add index on (resume_id, analysis_timestamp) for ResumeAnalysis
  - _Requirements: 27.5, 28.1, 28.4_

- [ ] 28.2 Optimize dashboard queries
  - Use select_related for foreign keys
  - Use prefetch_related for reverse foreign keys
  - Reduce number of database queries
  - _Requirements: 27.2_

- [ ] 28.3 Implement caching for computed metrics
  - Cache resume health scores for 5 minutes
  - Cache ATS scores for 5 minutes
  - Use Django cache framework
  - _Requirements: 27.3, 28.3_

- [ ] 28.4 Optimize PDF generation
  - Cache template assets
  - Use efficient rendering
  - Ensure completion within 5 seconds
  - _Requirements: 28.2_

- [ ] 28.5 Add lazy loading for resume previews
  - Load resume cards first
  - Lazy load preview images
  - Improve perceived performance
  - _Requirements: 27.4_

- [ ] 28.6 Test performance with large datasets
  - Test dashboard with 100+ resumes
  - Test batch operations with 10+ resumes
  - Ensure response times meet targets
  - _Requirements: 27.1, 27.4_

### 29. Final Checkpoint - Ensure all tests pass
- Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Focus on completing one phase before moving to the next
- Test thoroughly after each phase

## Dependencies

Before starting implementation, ensure these dependencies are installed:

```bash
pip install python-docx==0.8.11
pip install spacy==3.7.2
python -m spacy download en_core_web_sm
pip install nltk==3.8.1
```

## Testing Strategy

- Write unit tests for each service method
- Write integration tests for complete workflows
- Test with real resume data and job descriptions
- Verify performance meets targets (< 2s dashboard, < 10s optimization, < 5s PDF)
- Conduct user acceptance testing after each phase
