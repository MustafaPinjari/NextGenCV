# NextGenCV v2.0 API Documentation

## Overview

This document provides comprehensive documentation for all API endpoints in NextGenCV v2.0. All endpoints require authentication unless otherwise specified.

## Authentication

### Register User
**Endpoint**: `POST /auth/register/`

**Request Body**:
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "password_confirm": "string"
}
```

**Response**: `302 Redirect` to login page

**Errors**:
- `400`: Validation errors (passwords don't match, username taken, etc.)

---

### Login
**Endpoint**: `POST /auth/login/`

**Request Body**:
```json
{
  "username": "string",
  "password": "string"
}
```

**Response**: `302 Redirect` to dashboard

**Errors**:
- `401`: Invalid credentials

---

### Logout
**Endpoint**: `POST /auth/logout/`

**Response**: `302 Redirect` to landing page

---

## Resume Management

### List Resumes
**Endpoint**: `GET /resumes/`

**Query Parameters**:
- `page` (optional): Page number for pagination

**Response**: `200 OK`
```html
<!-- Rendered template with resume list -->
```

**Context Data**:
```python
{
  'resumes': QuerySet[Resume],
  'page_obj': Page
}
```

---

### Create Resume
**Endpoint**: `GET /resumes/create/` (form) or `POST /resumes/create/` (submit)

**Request Body** (POST):
```json
{
  "title": "string",
  "full_name": "string",
  "email": "string",
  "phone": "string",
  "location": "string",
  "summary": "string"
}
```

**Response**: `302 Redirect` to resume detail page

**Errors**:
- `400`: Validation errors

---

### View Resume
**Endpoint**: `GET /resumes/<int:resume_id>/`

**Response**: `200 OK`

**Context Data**:
```python
{
  'resume': Resume,
  'experiences': QuerySet[Experience],
  'education': QuerySet[Education],
  'skills': QuerySet[Skill],
  'projects': QuerySet[Project],
  'current_version': int,
  'last_analyzed': datetime,
  'ats_score': float
}
```

**Errors**:
- `404`: Resume not found
- `403`: User doesn't own resume

---

### Update Resume
**Endpoint**: `GET /resumes/<int:resume_id>/update/` (form) or `POST /resumes/<int:resume_id>/update/` (submit)

**Request Body** (POST):
```json
{
  "title": "string",
  "full_name": "string",
  "email": "string",
  "phone": "string",
  "location": "string",
  "summary": "string"
}
```

**Response**: `302 Redirect` to resume detail page

**Side Effects**:
- Creates new ResumeVersion automatically

**Errors**:
- `404`: Resume not found
- `403`: User doesn't own resume
- `400`: Validation errors

---

### Delete Resume
**Endpoint**: `GET /resumes/<int:resume_id>/delete/` (confirmation) or `POST /resumes/<int:resume_id>/delete/` (confirm)

**Response**: `302 Redirect` to resume list

**Side Effects**:
- Cascades delete to all versions, analyses, and optimizations

**Errors**:
- `404`: Resume not found
- `403`: User doesn't own resume

---

## PDF Upload & Parsing

### Upload PDF
**Endpoint**: `GET /resumes/upload/` (form) or `POST /resumes/upload/` (submit)

**Request Body** (POST - multipart/form-data):
```
file: <PDF file>
```

**File Requirements**:
- Type: application/pdf
- Max size: 10MB
- Must contain extractable text

**Response**: `302 Redirect` to parse review page

**Side Effects**:
- Creates UploadedResume record
- Extracts text using PDFParserService
- Parses sections using SectionParserService

**Errors**:
- `400`: Invalid file type
- `413`: File too large
- `400`: PDF contains embedded scripts
- `500`: Parsing failed

---

### Review Parsed Data
**Endpoint**: `GET /resumes/upload/<int:upload_id>/review/`

**Response**: `200 OK`

**Context Data**:
```python
{
  'uploaded_resume': UploadedResume,
  'parsed_data': {
    'personal_info': dict,
    'experiences': list[dict],
    'education': list[dict],
    'skills': list[str],
    'projects': list[dict]
  },
  'parsing_confidence': float,
  'low_confidence_sections': list[str]
}
```

**Errors**:
- `404`: Upload not found
- `403`: User doesn't own upload

---

### Confirm Import
**Endpoint**: `POST /resumes/upload/<int:upload_id>/confirm/`

**Request Body**:
```json
{
  "title": "string",
  "personal_info": {
    "full_name": "string",
    "email": "string",
    "phone": "string",
    "location": "string"
  },
  "experiences": [...],
  "education": [...],
  "skills": [...],
  "projects": [...]
}
```

**Response**: `302 Redirect` to resume detail page

**Side Effects**:
- Creates Resume from parsed data
- Creates initial ResumeVersion
- Runs initial ATS analysis
- Updates UploadedResume status to 'imported'

**Errors**:
- `404`: Upload not found
- `403`: User doesn't own upload
- `400`: Validation errors

---

## Resume Optimization

### Start Optimization
**Endpoint**: `GET /resumes/<int:resume_id>/fix/` (form) or `POST /resumes/<int:resume_id>/fix/` (submit)

**Request Body** (POST):
```json
{
  "job_description": "string (required, min 100 chars)"
}
```

**Response**: `302 Redirect` to preview page

**Side Effects**:
- Stores job description in session

**Errors**:
- `404`: Resume not found
- `403`: User doesn't own resume
- `400`: Job description too short

---

### Preview Optimization
**Endpoint**: `GET /resumes/<int:resume_id>/fix/preview/`

**Response**: `200 OK`

**Context Data**:
```python
{
  'resume': Resume,
  'job_description': str,
  'optimized_data': {
    'experiences': list[dict],
    'skills': list[str],
    'summary': str
  },
  'changes': list[{
    'type': str,  # 'action_verb', 'keyword', 'quantification', 'formatting'
    'section': str,
    'field': str,
    'old_value': str,
    'new_value': str,
    'reason': str
  }],
  'original_score': float,
  'optimized_score': float,
  'improvement_delta': float,
  'changes_by_type': dict[str, int]
}
```

**Processing**:
- Runs ResumeOptimizerService
- Calculates new ATS score
- Stores results in session

**Errors**:
- `404`: Resume not found
- `403`: User doesn't own resume
- `400`: No job description in session

---

### Accept Optimization
**Endpoint**: `POST /resumes/<int:resume_id>/fix/accept/`

**Response**: `302 Redirect` to resume detail page

**Side Effects**:
- Creates new ResumeVersion with optimized data
- Creates OptimizationHistory record
- Clears session data

**Errors**:
- `404`: Resume not found
- `403`: User doesn't own resume
- `400`: No optimization data in session

---

### Reject Optimization
**Endpoint**: `POST /resumes/<int:resume_id>/fix/reject/`

**Response**: `302 Redirect` to resume detail page

**Side Effects**:
- Clears session data

**Errors**:
- `404`: Resume not found
- `403`: User doesn't own resume

---

## Version Management

### List Versions
**Endpoint**: `GET /resumes/<int:resume_id>/versions/`

**Response**: `200 OK`

**Context Data**:
```python
{
  'resume': Resume,
  'versions': QuerySet[ResumeVersion].order_by('-created_at'),
  'version_count': int
}
```

**Errors**:
- `404`: Resume not found
- `403`: User doesn't own resume

---

### View Version
**Endpoint**: `GET /resumes/<int:resume_id>/versions/<int:version_id>/`

**Response**: `200 OK`

**Context Data**:
```python
{
  'resume': Resume,
  'version': ResumeVersion,
  'snapshot_data': dict,  # Complete resume state at that version
  'is_current': bool
}
```

**Errors**:
- `404`: Resume or version not found
- `403`: User doesn't own resume

---

### Compare Versions
**Endpoint**: `GET /resumes/<int:resume_id>/versions/compare/?v1=<id>&v2=<id>`

**Query Parameters**:
- `v1`: First version ID
- `v2`: Second version ID

**Response**: `200 OK`

**Context Data**:
```python
{
  'resume': Resume,
  'version1': ResumeVersion,
  'version2': ResumeVersion,
  'diff': {
    'personal_info': list[dict],  # [{field, old, new, change_type}]
    'experiences': list[dict],
    'education': list[dict],
    'skills': list[dict],
    'summary': dict
  },
  'score_change': float
}
```

**Errors**:
- `404`: Resume or versions not found
- `403`: User doesn't own resume
- `400`: Missing version parameters

---

### Restore Version
**Endpoint**: `POST /resumes/<int:resume_id>/versions/<int:version_id>/restore/`

**Response**: `302 Redirect` to resume edit page

**Side Effects**:
- Creates new ResumeVersion based on historical version
- Increments version number
- Sets modification_type to 'restored'

**Errors**:
- `404`: Resume or version not found
- `403`: User doesn't own resume

---

## Analytics

### Analytics Dashboard
**Endpoint**: `GET /analytics/dashboard/`

**Response**: `200 OK`

**Context Data**:
```python
{
  'resume_health': float,  # 0-100
  'total_resumes': int,
  'total_versions': int,
  'total_optimizations': int,
  'avg_improvement': float,
  'score_trend_data': {
    'labels': list[str],  # Dates
    'scores': list[float]
  },
  'top_missing_keywords': list[tuple[str, int]],
  'section_completeness': dict[str, float],
  'recent_analyses': QuerySet[ResumeAnalysis]
}
```

**Errors**:
- None (shows empty state if no data)

---

### Trend Analysis
**Endpoint**: `GET /analytics/trends/`

**Response**: `200 OK`

**Context Data**:
```python
{
  'analyses': QuerySet[ResumeAnalysis],
  'trend_data': {
    'scores': list[float],
    'moving_average': list[float],
    'improvement_rate': float,
    'trend_direction': str  # 'improving', 'declining', 'stable'
  },
  'component_trends': dict[str, list[float]]
}
```

---

### Improvement Report
**Endpoint**: `GET /analytics/improvement-report/`

**Response**: `200 OK`

**Context Data**:
```python
{
  'optimization_history': QuerySet[OptimizationHistory],
  'total_improvements': float,
  'avg_improvement_per_session': float,
  'most_common_changes': dict[str, int],
  'recommendations': list[str],
  'score_progression': list[dict]
}
```

---

## Template Management

### Template Gallery
**Endpoint**: `GET /templates/gallery/`

**Response**: `200 OK`

**Context Data**:
```python
{
  'templates': QuerySet[ResumeTemplate].filter(is_active=True),
  'user_customizations': dict[int, TemplateCustomization]
}
```

---

### Template Preview
**Endpoint**: `GET /templates/<int:template_id>/preview/`

**Response**: `200 OK`

**Context Data**:
```python
{
  'template': ResumeTemplate,
  'sample_resume': dict,  # Sample data for preview
  'preview_html': str
}
```

**Errors**:
- `404`: Template not found
- `400`: Template not active

---

### Customize Template
**Endpoint**: `GET /templates/<int:template_id>/customize/?resume_id=<id>` (form) or `POST /templates/<int:template_id>/customize/` (submit)

**Request Body** (POST):
```json
{
  "resume_id": int,
  "color_scheme": "string",
  "font_family": "string",
  "custom_css": "string (optional)"
}
```

**Response**: `302 Redirect` to resume detail page

**Side Effects**:
- Creates or updates TemplateCustomization

**Errors**:
- `404`: Template or resume not found
- `403`: User doesn't own resume
- `400`: Validation errors

---

## Export

### Export as PDF
**Endpoint**: `GET /resumes/<int:resume_id>/export/pdf/`

**Query Parameters**:
- `version` (optional): Version ID to export

**Response**: `200 OK` with `Content-Type: application/pdf`

**Headers**:
```
Content-Disposition: attachment; filename="resume_<id>.pdf"
```

**Errors**:
- `404`: Resume not found
- `403`: User doesn't own resume

---

### Export as DOCX
**Endpoint**: `GET /resumes/<int:resume_id>/export/docx/`

**Query Parameters**:
- `version` (optional): Version ID to export

**Response**: `200 OK` with `Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document`

**Headers**:
```
Content-Disposition: attachment; filename="resume_<id>.docx"
```

**Errors**:
- `404`: Resume not found
- `403`: User doesn't own resume

---

### Export as Plain Text
**Endpoint**: `GET /resumes/<int:resume_id>/export/text/`

**Query Parameters**:
- `version` (optional): Version ID to export

**Response**: `200 OK` with `Content-Type: text/plain`

**Headers**:
```
Content-Disposition: attachment; filename="resume_<id>.txt"
```

**Errors**:
- `404`: Resume not found
- `403`: User doesn't own resume

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "error": "Validation error message",
  "fields": {
    "field_name": ["Error message"]
  }
}
```

### 401 Unauthorized
```json
{
  "error": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "error": "You don't have permission to access this resource"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "An unexpected error occurred"
}
```

## Rate Limiting

Currently, no rate limiting is implemented. For production deployment, consider implementing rate limiting on:
- PDF upload endpoints (5 uploads per hour)
- Optimization endpoints (10 optimizations per hour)
- Export endpoints (20 exports per hour)

## Pagination

List endpoints support pagination with the following parameters:
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 10, max: 100)

Pagination response includes:
```python
{
  'count': int,  # Total items
  'next': str,   # Next page URL
  'previous': str,  # Previous page URL
  'results': list
}
```

## Webhooks

Currently, no webhooks are implemented. Future versions may include webhooks for:
- Resume optimization completed
- New version created
- ATS score threshold reached

## API Versioning

Current API version: v2.0

Future versions will use URL-based versioning:
- `/api/v2/resumes/`
- `/api/v3/resumes/`

## Authentication Methods

Currently supported:
- Session-based authentication (Django sessions)

Future support planned:
- JWT tokens
- OAuth2
- API keys

## CORS

CORS is not currently enabled. For API access from external domains, configure CORS in `config/settings.py`:

```python
CORS_ALLOWED_ORIGINS = [
    "https://example.com",
]
```
