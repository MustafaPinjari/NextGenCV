# ATS Optimized Resume Builder

A Django-based web application for creating, managing, and optimizing resumes for Applicant Tracking Systems (ATS).

## Features

- User authentication and registration
- Create and manage multiple resumes
- ATS analysis against job descriptions
- PDF export with ATS-compatible formatting
- Professional resume templates
- Keyword matching and optimization suggestions

## Technology Stack

- **Backend**: Django 4.2.7
- **Database**: SQLite
- **Frontend**: Bootstrap 5.3.2
- **PDF Generation**: WeasyPrint 60.1
- **Testing**: Hypothesis 6.92.1 (Property-based testing)

## Project Structure

```
ats_resume_builder/
├── apps/
│   ├── authentication/    # User authentication
│   ├── resumes/          # Resume management
│   └── analyzer/         # ATS analysis
├── config/               # Django settings
├── templates/            # HTML templates
├── static/              # CSS, JS, images
├── manage.py
└── requirements.txt
```

## Setup Instructions

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

6. Access the application at `http://localhost:8000`

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Collecting Static Files
```bash
python manage.py collectstatic
```

## License

This project is for educational purposes.
