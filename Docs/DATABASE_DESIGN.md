# Database Design

DBMS: SQLite

---

# Entity Relationship Design

User (1) ---- (M) Resume  
Resume (1) ---- (1) PersonalInfo  
Resume (1) ---- (M) Experience  
Resume (1) ---- (M) Education  
Resume (1) ---- (M) Skill  
Resume (1) ---- (M) Project  

---

# Tables

## User
- id
- username
- email
- password

## Resume
- id
- user_id (FK)
- title
- template
- created_at
- updated_at

## PersonalInfo
- id
- resume_id (FK)
- full_name
- phone
- email
- linkedin
- github
- location

## Experience
- id
- resume_id (FK)
- company
- role
- start_date
- end_date
- description

## Education
- id
- resume_id (FK)
- institution
- degree
- field
- start_year
- end_year

## Skill
- id
- resume_id (FK)
- name
- category