# System Architecture

## Architecture Type
Layered Monolithic Architecture

Presentation Layer → Django Templates + Bootstrap  
Application Layer → Django Views + Services  
Data Layer → Django ORM (SQLite)

---

# Logical Layers

1. Presentation Layer
   - HTML templates
   - Bootstrap UI
   - Form handling

2. Application Layer
   - Views
   - Business Logic Services
   - ATS Scoring Engine

3. Data Layer
   - Models
   - ORM Queries
   - SQLite

---

# Request Lifecycle

User Request
    ↓
URL Router
    ↓
View Function
    ↓
Service Layer
    ↓
Database
    ↓
Template Rendering
    ↓
HTTP Response

---

# Scalability Consideration

Although SQLite is used:
- Use service layer abstraction
- Avoid raw SQL
- Keep DB migration friendly

Future upgrade:
SQLite → PostgreSQL (minimal changes)