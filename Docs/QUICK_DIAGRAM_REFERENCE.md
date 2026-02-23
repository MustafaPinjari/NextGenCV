# Quick Diagram Reference Guide

## Generated Diagrams

Your project now has the following diagram files:

### 1. Complete ERD (All Apps)
**File:** `Docs/ERD_Diagram.png`
- Shows all Django models including built-in auth models
- Includes all relationships and fields
- Best for: Complete system overview

### 2. Custom Apps ERD
**File:** `Docs/ERD_Custom_Apps.png`
- Shows only your custom app models
- Cleaner view without Django built-in models
- Best for: Understanding your business logic

### 3. Text-Based Diagrams
**File:** `Docs/ANALYSIS_AND_DESIGN_DIAGRAMS.md`
- DFD (Data Flow Diagrams)
- Table Specifications
- ERD (ASCII art)
- Activity Diagrams
- Sequence Diagrams
- Class Diagrams
- Best for: Documentation, version control, easy editing

---

## Regenerating Diagrams

### Update ERD After Model Changes

```bash
# Activate virtual environment
source venv/bin/activate

# Generate complete ERD
python manage.py graph_models -a -g -o Docs/ERD_Diagram.png

# Generate custom apps only
python manage.py graph_models resumes analyzer analytics templates_mgmt authentication -g -o Docs/ERD_Custom_Apps.png
```

### Additional Options

```bash
# Exclude certain models
python manage.py graph_models -a -X LogEntry,Permission,Group -o Docs/ERD_Clean.png

# Include only specific apps
python manage.py graph_models resumes -o Docs/ERD_Resumes_Only.png

# Output as DOT file (for further customization)
python manage.py graph_models -a -o Docs/ERD.dot

# Group by app
python manage.py graph_models -a -g -o Docs/ERD_Grouped.png

# Show inheritance
python manage.py graph_models -a -I -o Docs/ERD_Inheritance.png
```

---

## Viewing Diagrams

### In VS Code
1. Install "Image Preview" extension
2. Click on .png files to view
3. Or right-click → "Open Preview"

### In Browser
1. Open file manager
2. Double-click the .png file
3. Opens in default image viewer

### In Terminal
```bash
# Using eog (Eye of GNOME)
eog Docs/ERD_Diagram.png

# Using xdg-open (opens default viewer)
xdg-open Docs/ERD_Diagram.png
```

---

## Diagram Legend

### ERD Symbols

**Boxes:**
- Model/Table name at top
- Fields listed below
- Primary keys usually marked

**Arrows:**
- → ForeignKey (Many-to-One)
- ⟷ OneToOneField
- ⇉ ManyToManyField

**Colors (if enabled):**
- Different colors for different apps
- Helps identify app boundaries

---

## Common Commands

### Show All URLs
```bash
python manage.py show_urls
```

### Show Database Schema
```bash
python manage.py dbshell
.schema
.tables
```

### Inspect Database
```bash
python manage.py inspectdb
```

### Show Migrations
```bash
python manage.py showmigrations
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'django_extensions'"
```bash
pip install django-extensions
```
Add to INSTALLED_APPS in settings.py

### "ModuleNotFoundError: No module named 'pygraphviz'"
```bash
# Install system dependencies first
sudo apt-get install graphviz graphviz-dev

# Then install Python package
pip install pygraphviz
```

### "Command not found: graph_models"
Make sure django-extensions is in INSTALLED_APPS

### Diagram is too large/complex
```bash
# Exclude Django built-in models
python manage.py graph_models -a -X LogEntry,Permission,Group,ContentType,Session -o Docs/ERD_Simple.png

# Or generate per-app diagrams
python manage.py graph_models resumes -o Docs/ERD_Resumes.png
python manage.py graph_models analyzer -o Docs/ERD_Analyzer.png
```

---

## Integration with Documentation

### For Project Reports
1. Use `ERD_Custom_Apps.png` - cleaner view
2. Include in Word/PDF documents
3. Reference in architecture section

### For Team Documentation
1. Keep `ERD_Diagram.png` updated
2. Commit to version control
3. Reference in README.md

### For Presentations
1. Use high-resolution PNG exports
2. Consider grouping by app
3. Highlight specific relationships

---

## Best Practices

1. **Regenerate after model changes**
   - After adding/removing models
   - After changing relationships
   - Before major releases

2. **Keep multiple versions**
   - Full diagram (all apps)
   - Custom apps only
   - Per-app diagrams

3. **Version control**
   - Commit diagram images
   - Include generation date in filename
   - Document in commit messages

4. **Documentation**
   - Reference diagrams in docs
   - Explain custom relationships
   - Keep legend updated

---

## Quick Reference Table

| Task | Command |
|------|---------|
| Full ERD | `python manage.py graph_models -a -g -o erd.png` |
| Custom apps | `python manage.py graph_models app1 app2 -o erd.png` |
| Exclude models | `python manage.py graph_models -a -X Model1,Model2 -o erd.png` |
| Group by app | `python manage.py graph_models -a -g -o erd.png` |
| Show inheritance | `python manage.py graph_models -a -I -o erd.png` |
| DOT format | `python manage.py graph_models -a -o erd.dot` |
| Show URLs | `python manage.py show_urls` |
| DB schema | `python manage.py dbshell` then `.schema` |

---

## Additional Resources

### Django Extensions Documentation
https://django-extensions.readthedocs.io/

### Graphviz Documentation
https://graphviz.org/documentation/

### Model Visualization
https://django-extensions.readthedocs.io/en/latest/graph_models.html

---

## Next Steps

1. ✅ View generated ERD diagrams
2. ✅ Compare with text-based diagrams in ANALYSIS_AND_DESIGN_DIAGRAMS.md
3. ✅ Use diagrams in your project documentation
4. ✅ Update diagrams when models change
5. ✅ Share with team members

---

**Last Updated:** Generated automatically with django-extensions
**Location:** `Docs/` directory
**Maintained by:** Project team
