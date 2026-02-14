# System Design Document

---

# 1. High-Level Design

Client (Browser)
    ↓
Django Server
    ↓
SQLite Database

All rendering is server-side.

---

# 2. Component Design

## A. Authentication Component
- Uses Django Auth
- Middleware-based protection

## B. Resume Management Component
- CRUD operations
- Section-based modular structure

## C. ATS Analyzer Component

Steps:
1. Aggregate resume text
2. Clean text
3. Extract keywords from job description
4. Compute similarity score
5. Generate suggestions

---

# 3. ATS Algorithm (Design)

Input:
- Resume Text
- Job Description Text

Process:
- Convert to lowercase
- Remove stop words
- Tokenize
- Count keyword matches
- Calculate percentage match

Score Formula:
Score = (Matched Keywords / Total JD Keywords) × 100

---

# 4. PDF Generation Design

1. Render resume template to HTML
2. Pass HTML to WeasyPrint
3. Generate PDF
4. Return as downloadable response

---

# 5. Security Design

- All forms use CSRF token
- Login required for resume access
- Data filtered by user_id
- Server-side validation