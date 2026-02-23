# DIAGRAM USAGE GUIDE
# How to Use the Analysis & Design Diagrams

---

## Quick Reference

All diagrams are located in: `Docs/ANALYSIS_AND_DESIGN_DIAGRAMS.md`

This document contains:
1. Data Flow Diagram (DFD) - Levels 0, 1, and 2
2. Table Specifications (Database Schema)
3. Entity Relationship Diagram (ERD)
4. Activity Diagrams (3 workflows)
5. Sequence Diagrams (4 interactions)
6. Class Diagram (Complete system)

---

## When to Use Each Diagram

### 1. DFD (Data Flow Diagram)
**Use when:**
- Explaining how data moves through the system
- Identifying data transformation points
- Understanding system boundaries
- Planning new features that involve data processing

**Example scenarios:**
- "How does job description data become an ATS score?"
- "What happens to resume data during optimization?"
- "Where is data validated and transformed?"

### 2. Table Specifications
**Use when:**
- Designing database migrations
- Understanding data constraints
- Planning queries and indexes
- Documenting database schema

**Example scenarios:**
- "What fields does the Resume table have?"
- "What are the foreign key relationships?"
- "What indexes exist for performance?"

### 3. ERD (Entity Relationship Diagram)
**Use when:**
- Understanding data relationships
- Planning database queries
- Designing new features that need data
- Explaining the data model to others

**Example scenarios:**
- "How are resumes connected to users?"
- "What's the relationship between Resume and Experience?"
- "Can I delete a resume without affecting versions?"

### 4. Activity Diagrams
**Use when:**
- Understanding user workflows
- Planning UI/UX flows
- Identifying decision points
- Testing user journeys

**Example scenarios:**
- "What steps does a user take to create a resume?"
- "What happens if PDF parsing fails?"
- "How does the optimization workflow work?"

### 5. Sequence Diagrams
**Use when:**
- Understanding system interactions
- Debugging request/response cycles
- Planning API integrations
- Documenting timing and order of operations

**Example scenarios:**
- "What happens when a user clicks 'Analyze'?"
- "How do the view, service, and database interact?"
- "What's the order of operations during PDF export?"

### 6. Class Diagram
**Use when:**
- Understanding code structure
- Planning new classes or services
- Refactoring code
- Documenting object relationships

**Example scenarios:**
- "What methods does the Resume class have?"
- "How do service classes interact with models?"
- "What's the structure of the ATS analyzer?"

---

## Mapping to Your Codebase

### Quick Mapping Table

| Diagram Element | Code Location |
|----------------|---------------|
| User (Model) | `django.contrib.auth.models.User` |
| Resume (Model) | `apps/resumes/models.py::Resume` |
| Authentication Process | `apps/authentication/views.py` |
| Resume Management | `apps/resumes/views.py` |
| ATS Analysis | `apps/analyzer/views.py` + `apps/analyzer/services.py` |
| Templates | `apps/templates_mgmt/` |
| Analytics | `apps/analytics/views.py` |
| Database | `db.sqlite3` |

### Finding Code from Diagrams

**From DFD Process:**
1. Identify the process number (e.g., "3.0 ATS Analysis")
2. Look in the corresponding app (e.g., `apps/analyzer/`)
3. Check `views.py` for user-facing functions
4. Check `services.py` for business logic

**From ERD Entity:**
1. Identify the entity name (e.g., "Experience")
2. Look in `apps/resumes/models.py`
3. Find the class definition
4. Check relationships via ForeignKey fields

**From Activity Step:**
1. Identify the activity (e.g., "Create Resume")
2. Look in `config/urls.py` for routing
3. Follow to app-specific `urls.py`
4. Find the view function

**From Sequence Message:**
1. Identify the message (e.g., "analyze_resume()")
2. Search in service files
3. Trace the call chain
4. Check database operations

**From Class:**
1. Identify the class name
2. For models: check `apps/*/models.py`
3. For services: check `apps/*/services.py`
4. For views: check `apps/*/views.py`

---

## Common Use Cases

### Use Case 1: Adding a New Feature

**Scenario:** Add a "Resume Score History" feature

**Steps:**
1. Check ERD → Identify related entities (Resume, ResumeAnalysis)
2. Check Table Specs → Understand existing fields
3. Design new table if needed
4. Check DFD → Identify where data flows
5. Check Activity Diagram → Plan user workflow
6. Check Sequence Diagram → Plan interactions
7. Check Class Diagram → Plan new methods

### Use Case 2: Debugging an Issue

**Scenario:** ATS analysis returns incorrect score

**Steps:**
1. Check Sequence Diagram → Trace the analysis flow
2. Check DFD Level 2 → Identify transformation steps
3. Check Class Diagram → Find relevant service methods
4. Add logging at each step
5. Verify data at each transformation point

### Use Case 3: Explaining to Stakeholders

**Scenario:** Present system architecture to non-technical audience

**Steps:**
1. Start with DFD Level 0 → Show system boundary
2. Show Activity Diagram → Demonstrate user workflows
3. Show DFD Level 1 → Explain main processes
4. Use ERD → Explain data relationships (simplified)

### Use Case 4: Onboarding New Developer

**Scenario:** Help new team member understand codebase

**Steps:**
1. Show DFD Level 0 → System overview
2. Show ERD → Data model
3. Show Activity Diagrams → User workflows
4. Show Class Diagram → Code structure
5. Show Sequence Diagrams → Interaction patterns
6. Provide mapping guide → Connect diagrams to code

### Use Case 5: Planning Database Migration

**Scenario:** Add new field to Resume model

**Steps:**
1. Check Table Specifications → Understand current schema
2. Check ERD → Identify affected relationships
3. Check Class Diagram → Identify affected methods
4. Check Sequence Diagrams → Identify affected flows
5. Plan migration script
6. Update diagrams

---

## Diagram Maintenance

### When to Update Diagrams

**Always update when:**
- Adding new models
- Changing relationships
- Adding new features
- Modifying workflows
- Refactoring architecture

**Update checklist:**
- [ ] DFD: New data flows or processes
- [ ] Table Specs: New fields or tables
- [ ] ERD: New entities or relationships
- [ ] Activity: New user workflows
- [ ] Sequence: New interactions
- [ ] Class: New classes or methods

### How to Update

1. **Identify changes in code**
   ```bash
   git diff main...feature-branch
   ```

2. **Update relevant diagrams**
   - Edit `Docs/ANALYSIS_AND_DESIGN_DIAGRAMS.md`
   - Follow existing ASCII art style
   - Maintain consistency

3. **Verify accuracy**
   - Compare with actual code
   - Test workflows
   - Review with team

4. **Commit with code changes**
   ```bash
   git add Docs/ANALYSIS_AND_DESIGN_DIAGRAMS.md
   git commit -m "Update diagrams for [feature]"
   ```

---

## Tips for Reading Diagrams

### DFD Tips:
- Follow arrows to trace data flow
- Circles/rectangles = processes
- Parallel lines = data stores
- External entities = squares

### ERD Tips:
- Lines show relationships
- 1:M means one-to-many
- M:M means many-to-many
- PK = Primary Key, FK = Foreign Key

### Activity Tips:
- Diamonds = decision points
- Rectangles = activities
- Arrows = flow direction
- Parallel paths = concurrent activities

### Sequence Tips:
- Read top to bottom
- Vertical lines = lifelines
- Horizontal arrows = messages
- Dashed arrows = returns

### Class Tips:
- Top section = attributes
- Bottom section = methods
- Lines = relationships
- + = public, - = private

---

## Tools and Resources

### Viewing Diagrams:
- Any text editor (VS Code, Sublime, etc.)
- Markdown preview
- GitHub/GitLab web interface

### Generating from Code:
```bash
# ERD from models
pip install django-extensions pygraphviz
python manage.py graph_models -a -o erd.png

# Class diagram from code
pip install pylint
pyreverse -o png -p NextGenCV apps/

# URL routing
pip install django-extensions
python manage.py show_urls
```

### Converting to Images:
- Use online ASCII to image converters
- Use draw.io to recreate
- Use PlantUML for UML diagrams
- Use Mermaid for flowcharts

---

## FAQ

**Q: Do I need to update diagrams for every small change?**
A: No, update for significant changes like new models, major features, or workflow changes.

**Q: Can I generate these diagrams automatically?**
A: Partially. ERD and class diagrams can be auto-generated, but DFD, activity, and sequence diagrams require manual creation.

**Q: Which diagram is most important?**
A: ERD and DFD are most critical for understanding the system. Others provide additional context.

**Q: How do I keep diagrams in sync with code?**
A: Include diagram updates in your definition of done for features. Review during code reviews.

**Q: Can I use different diagram formats?**
A: Yes! These are ASCII art for easy version control, but you can recreate in any tool.

---

## Next Steps

1. **Read through all diagrams** in `ANALYSIS_AND_DESIGN_DIAGRAMS.md`
2. **Map one feature** from diagram to code
3. **Trace one workflow** through all diagram types
4. **Update one diagram** with a recent change
5. **Share with team** and gather feedback

---

## Support

For questions about:
- **Diagrams**: Check this guide and the main diagram document
- **Code mapping**: See the "Practical Mapping Guide" section
- **Updates**: Follow the "Diagram Maintenance" section
- **Tools**: See the "Tools and Resources" section

Happy diagramming! 📊
