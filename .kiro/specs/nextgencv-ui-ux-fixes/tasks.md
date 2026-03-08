# Implementation Plan: NextGenCV UI/UX Fixes

## Overview

This implementation plan addresses critical UI/UX issues based on current code analysis. The form input styling and wizard Step 5 completion are already implemented. Remaining work focuses on analytics dashboard data population, template gallery enhancements, and landing page visual improvements.

## Tasks

- [x] 1. Fix Form Input Styling and Visibility
  - Form input CSS variables already defined in design-system.css
  - All form inputs use consistent styling with proper contrast
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 2. Implement Resume Wizard Step 5 Completion
  - Step 5 view logic fully implemented in `resume_create` view
  - AI summary generation endpoint working
  - Template includes character counter and live preview
  - Finish button properly saves and redirects
  - _Requirements: 4.2, 4.3, 4.4, 5.1, 5.2, 5.3, 5.5_

- [x] 3. Populate Analytics Dashboard Charts with Real Data
  - [x] 3.1 Verify chart data structure in analytics view
    - Analytics dashboard already passes `chart_data_json` to template
    - Verify score_trend data includes labels, scores, and moving_average
    - Verify health_by_resume data structure matches Chart.js expectations
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

  - [ ]* 3.2 Write property test for chart data ordering
    - **Property 11: Chart Data Chronological Ordering**
    - **Validates: Requirements 6.1, 6.3**

  - [ ]* 3.3 Write unit tests for analytics data functions
    - Test empty state handling
    - Test data retrieval with multiple analyses
    - Test chart data serialization
    - _Requirements: 6.2_

- [x] 4. Enhance Template Gallery with Preview Modal
  - [x] 4.1 Add thumbnail field to ResumeTemplate model
    - Thumbnail field already exists in model
    - _Requirements: 7.1_

  - [x] 4.2 Update template gallery cards with preview functionality
    - Add eye icon button in upper right corner of thumbnail
    - Ensure "Use Template" button is at bottom of card
    - Add onclick handlers for preview modal
    - _Requirements: 7.1, 7.2, 7.4_

  - [x] 4.3 Implement template preview modal
    - Create modal HTML structure in template gallery
    - Add modal CSS for overlay, content, and animations
    - Implement JavaScript for opening/closing modal
    - Add AJAX loading of preview content
    - Handle Escape key and backdrop click to close
    - Prevent body scroll when modal is open
    - _Requirements: 7.3, 8.1, 8.2, 8.3, 8.4, 8.5_

  - [x] 4.4 Template preview endpoint already exists
    - View and URL route already implemented
    - _Requirements: 7.3_

  - [ ]* 4.5 Write property test for template card elements
    - **Property 12: Template Card Required Elements**
    - **Validates: Requirements 7.1, 7.2, 7.4**

  - [ ]* 4.6 Write unit tests for template preview modal
    - Test modal opens on click
    - Test modal closes on backdrop click
    - Test modal closes on Escape key
    - Test body scroll prevention
    - _Requirements: 8.2, 8.3, 8.4, 8.5_

- [x] 5. Enhance Landing Page Visuals
  - [x] 5.1 Add hero section background image
    - Source or create hero background image (1920x1080px)
    - Add image to static/images/
    - Update hero section CSS with background-image
    - Ensure responsive scaling on mobile
    - _Requirements: 1.1, 1.5_

  - [x] 5.2 Add feature section icons
    - Landing page already uses Bootstrap Icons for features
    - Verify icons are displaying correctly
    - Consider adding custom SVG icons if needed
    - _Requirements: 1.2_

  - [x] 5.3 Add product screenshots to "How It Works" section
    - Create or capture 2-3 product screenshots
    - Optimize images for web (WebP format recommended)
    - Add images to "How It Works" feature cards
    - Ensure responsive image scaling
    - _Requirements: 1.3_

  - [x] 5.4 Enhance landing page interactions
    - Verify hover effects on cards and buttons
    - Add scroll reveal animations if desired
    - Test spacing and visual hierarchy
    - _Requirements: 1.4, 10.5_

  - [ ]* 5.5 Write property test for design system consistency
    - **Property 13: Landing Page Design System Consistency**
    - **Validates: Requirements 1.4**

  - [ ]* 5.6 Write property test for responsive images
    - **Property 14: Responsive Image Scaling**
    - **Validates: Requirements 1.5**

  - [ ]* 5.7 Write unit tests for landing page elements
    - Test hero section structure
    - Test feature icons are present
    - Test CTA buttons link correctly
    - _Requirements: 1.1, 1.2, 10.1, 10.2_

- [x] 6. Final Integration Testing
  - [x] 6.1 Test complete resume creation flow
    - Create resume from Step 1 through Step 5
    - Verify summary saves correctly
    - Verify redirect to resume detail works
    - Verify success message displays
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 6.2 Test analytics dashboard with real data
    - Create test resumes with analyses
    - Verify charts populate with real data
    - Test empty state displays when no data
    - _Requirements: 6.1, 6.2, 6.3_

  - [x] 6.3 Test template gallery workflow
    - Browse templates
    - Click eye icon to preview template in modal
    - Close modal with backdrop click and Escape key
    - Click "Use Template" button to create resume
    - _Requirements: 7.3, 7.5, 8.2, 8.3, 8.4_

  - [x] 6.4 Cross-browser and responsive testing
    - Test in Chrome, Firefox, Safari
    - Test responsive layouts on mobile (320px, 768px, 1024px)
    - Verify all interactions work across browsers

- [x] 7. Fix Template Preview Loading Reliability
  - [x] 7.1 Add comprehensive error handling to template_preview view
    - Add try-except blocks around template retrieval and rendering
    - Return JSON error responses for AJAX requests
    - Log all errors with full stack traces
    - Handle TemplateDoesNotExist exceptions specifically
    - _Requirements: 11.2, 11.3_

  - [x] 7.2 Enhance template service with validation
    - Validate template_file path before rendering
    - Convert sample data dictionaries to mock objects with attributes
    - Add specific error messages for different failure modes
    - Add logging for successful renders
    - _Requirements: 11.4_

  - [x] 7.3 Improve frontend error display
    - Parse JSON error responses from backend
    - Display user-friendly error messages in modal
    - Add troubleshooting steps in error state
    - Show specific error details when available
    - _Requirements: 11.2_

  - [x] 7.4 Create template validation management command
    - Create check_templates command
    - Check all templates for valid template_file paths
    - Check for missing thumbnails
    - Output diagnostic report
    - _Requirements: 11.3_

  - [ ]* 7.5 Write property test for error handling
    - **Property 19: Template Preview Error Handling**
    - **Validates: Requirements 11.2, 11.3**

  - [ ]* 7.6 Write property test for successful preview
    - **Property 20: Template Preview Success Response**
    - **Validates: Requirements 11.1, 11.5**

  - [ ]* 7.7 Write unit tests for template preview
    - Test preview with valid template
    - Test preview with invalid template ID
    - Test preview with missing template file
    - Test error response format
    - _Requirements: 11.1, 11.2, 11.3_

- [ ] 8. Checkpoint - Final verification
  - Ensure all functionality works end-to-end, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Form input styling and wizard Step 5 are already complete
- Analytics dashboard already has chart structure - just needs data verification
- Template gallery needs modal implementation for preview functionality
- Landing page needs visual assets (images, screenshots)
