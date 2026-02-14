# Software Requirement Specification (SRS)
## Project: ATS Optimized Resume Builder
## Technology: Django + SQLite + Bootstrap

---

# 1. Introduction

## 1.1 Purpose
This document defines the functional and non-functional requirements for the ATS Optimized Resume Builder Web Application.

## 1.2 Scope
The system allows users to:
- Create structured resumes
- Optimize resumes for ATS
- Analyze resume vs job description
- Export resume to PDF
- Manage multiple resumes

---

# 2. Overall Description

## 2.1 Product Perspective
Standalone server-rendered web application built using Django.

## 2.2 User Classes

### Guest User
- Register
- Login
- View landing page

### Registered User
- Create resumes
- Edit resumes
- Analyze resumes
- Export PDF

### Admin
- Manage resume templates
- Monitor users

---

# 3. Functional Requirements

## FR-01 Authentication
System shall support registration, login, logout.

## FR-02 Resume Creation
User shall create multiple resumes.

## FR-03 Resume Editing
User shall dynamically manage sections:
- Personal Info
- Summary
- Experience
- Education
- Skills
- Projects
- Certifications

## FR-04 Resume Preview
System shall render formatted preview.

## FR-05 Resume Analyzer
System shall:
- Accept job description
- Extract keywords
- Compare with resume
- Return score
- Suggest missing keywords

## FR-06 Resume Export
System shall generate ATS-safe PDF.

---

# 4. Non-Functional Requirements

## NFR-01 Performance
- Page load < 2 sec
- Resume analysis < 1 sec
- PDF generation < 3 sec

## NFR-02 Security
- CSRF protection
- Password hashing
- Auth-required routes

## NFR-03 Reliability
- ACID compliant database
- No data loss

## NFR-04 Maintainability
- Modular Django apps
- Clean code structure