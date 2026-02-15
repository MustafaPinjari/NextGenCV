# PDF Upload Module Templates

This directory contains the templates for the PDF Upload and Parsing module (Task 11).

## Templates Created

### 1. pdf_upload.html
**Purpose**: Upload form for PDF resume files

**Features**:
- Drag-and-drop file upload interface
- File type validation (PDF only)
- File size validation (10 MB maximum)
- Real-time validation feedback
- Progress indicator during upload
- Bootstrap 5 styling with custom CSS
- Responsive design for mobile/tablet/desktop
- Instructions and tips for best results

**Requirements Validated**: 3.1, 3.2, 3.3

**URL**: `/resumes/upload/`

**View**: `apps.resumes.views.pdf_upload`

### 2. parse_review.html
**Purpose**: Review and edit parsed resume data before importing

**Features**:
- Parsing confidence score display (overall and per-section)
- Color-coded confidence indicators (high/medium/low)
- Editable form fields for all extracted data:
  - Personal Information (name, email, phone, location, LinkedIn, GitHub)
  - Work Experience (company, role, dates, description)
  - Education (institution, degree, field, years)
  - Skills (comma-separated list)
- Inline editing capabilities
- Add/remove entries for experiences and education
- Empty section handling with helpful messages
- Auto-save to localStorage (prevents data loss)
- Form validation before submission
- Bootstrap 5 styling with custom CSS
- Responsive design

**Requirements Validated**: 5.1, 5.2, 5.3, 5.4

**URL**: `/resumes/upload/<upload_id>/review/`

**View**: `apps.resumes.views.pdf_parse_review`

## Data Flow

1. User uploads PDF → `pdf_upload.html`
2. System validates and parses PDF → Backend processing
3. User reviews parsed data → `parse_review.html`
4. User confirms → System creates Resume object
5. Redirect to resume detail page

## Template Variables

### pdf_upload.html
No specific variables required (uses Django messages framework for feedback)

### parse_review.html
Expected context variables from view:
- `uploaded_resume`: UploadedResume model instance
- `parsed_data`: Dictionary with parsed resume data
- `personal_info`: Dictionary with personal information
- `experiences`: List of experience dictionaries
- `education`: List of education dictionaries
- `skills`: List of skill dictionaries
- `confidence`: Float (0.0-1.0) overall parsing confidence
- `confidence_percent`: Integer (0-100) confidence percentage

## Styling

Both templates use:
- Bootstrap 5.3.2 for base styling
- Bootstrap Icons for iconography
- Custom CSS for:
  - Drag-and-drop upload area
  - Confidence indicators
  - Progress bars
  - Section cards with color-coded borders
  - Editable field styling

## JavaScript Features

### pdf_upload.html
- Drag-and-drop file handling
- Client-side file validation
- Progress bar simulation
- File size formatting
- AJAX form submission

### parse_review.html
- Dynamic form field management (add/remove entries)
- Auto-save to localStorage
- Form validation
- Array item management for experiences/education
- Confidence indicator updates

## Browser Compatibility

Tested and compatible with:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Accessibility

Both templates follow WCAG 2.1 Level AA guidelines:
- Semantic HTML structure
- ARIA labels where appropriate
- Keyboard navigation support
- Color contrast ratios meet standards
- Screen reader friendly

## Future Enhancements

Potential improvements for future iterations:
- Real-time PDF preview
- OCR support for scanned PDFs
- Multi-language support
- Advanced parsing options
- Batch upload capability
