"""
Management command to seed the database with realistic mock data.

Usage:
    python manage.py seed_mock_data
    python manage.py seed_mock_data --users 3
    python manage.py seed_mock_data --flush   # clear existing data first
"""

import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from apps.resumes.models import (
    Resume, PersonalInfo, Experience, Education,
    Skill, Project, Certification, ResumeVersion,
    ResumeAnalysis, OptimizationHistory,
)
from apps.authentication.models import ActivityLog, SavedJobDescription
from apps.tracker.models import JobApplication, CoverLetter, InterviewPrepSession, SkillGapAnalysis


# ---------------------------------------------------------------------------
# Static mock data pools
# ---------------------------------------------------------------------------

USERS = [
    {"username": "alex_johnson", "email": "alex.johnson@example.com", "first_name": "Alex", "last_name": "Johnson", "password": "mockpass123"},
    {"username": "sarah_chen",   "email": "sarah.chen@example.com",   "first_name": "Sarah", "last_name": "Chen",    "password": "mockpass123"},
    {"username": "marcus_lee",   "email": "marcus.lee@example.com",   "first_name": "Marcus", "last_name": "Lee",   "password": "mockpass123"},
]

RESUME_TEMPLATES = ["professional", "modern", "classic", "creative", "minimal"]
COLOR_SCHEMES    = ["professional_blue", "dark_slate", "forest_green", "crimson_red", "midnight_purple"]
FONT_FAMILIES    = ["Arial", "Calibri", "Georgia", "Helvetica", "Times New Roman"]

SUMMARIES = [
    "Results-driven software engineer with 5+ years of experience building scalable web applications. "
    "Passionate about clean code, performance optimization, and delivering exceptional user experiences.",

    "Data-focused product manager with a track record of launching 0-to-1 products that drive measurable growth. "
    "Skilled at bridging technical and business teams to ship features users love.",

    "Full-stack developer specializing in Python/Django and React. "
    "Experienced in cloud infrastructure, CI/CD pipelines, and agile methodologies. "
    "Committed to writing maintainable, well-tested code.",
]

COMPANIES = [
    "Google", "Amazon", "Microsoft", "Meta", "Apple",
    "Stripe", "Shopify", "Airbnb", "Uber", "Netflix",
    "Salesforce", "Atlassian", "Twilio", "Datadog", "Snowflake",
    "Accenture", "Deloitte", "IBM", "Oracle", "SAP",
]

ROLES = [
    "Software Engineer", "Senior Software Engineer", "Staff Engineer",
    "Product Manager", "Senior Product Manager",
    "Data Scientist", "Machine Learning Engineer",
    "DevOps Engineer", "Site Reliability Engineer",
    "Frontend Developer", "Backend Developer", "Full Stack Developer",
    "Engineering Manager", "Technical Lead",
]

LOCATIONS = [
    "San Francisco, CA", "New York, NY", "Seattle, WA",
    "Austin, TX", "Boston, MA", "Chicago, IL",
    "Remote", "London, UK", "Toronto, Canada",
]

ACHIEVEMENTS_POOL = [
    "Reduced API response time by 40% through query optimization and caching strategies",
    "Led migration of monolithic application to microservices, improving deployment frequency by 3x",
    "Mentored 4 junior engineers, 2 of whom were promoted within 12 months",
    "Increased test coverage from 45% to 92%, reducing production bugs by 60%",
    "Designed and shipped a real-time notification system serving 2M+ daily active users",
    "Reduced infrastructure costs by $120K/year by right-sizing cloud resources",
    "Built an internal analytics dashboard adopted by 15 teams across the organization",
    "Improved CI/CD pipeline speed by 55% by parallelizing test suites",
    "Delivered a payment integration that processed $5M in transactions in its first quarter",
    "Collaborated with design and product to ship a redesigned onboarding flow, boosting activation by 28%",
    "Automated manual reporting workflows, saving the team 8 hours per week",
    "Architected a multi-tenant SaaS platform supporting 500+ enterprise customers",
]

INSTITUTIONS = [
    ("Massachusetts Institute of Technology", "B.S.", "Computer Science"),
    ("Stanford University", "M.S.", "Computer Science"),
    ("University of California, Berkeley", "B.S.", "Electrical Engineering & Computer Science"),
    ("Carnegie Mellon University", "M.S.", "Software Engineering"),
    ("University of Michigan", "B.S.", "Computer Science"),
    ("Georgia Institute of Technology", "M.S.", "Machine Learning"),
    ("University of Texas at Austin", "B.S.", "Computer Science"),
    ("Cornell University", "B.S.", "Information Science"),
]

SKILL_SETS = {
    "Languages":   ["Python", "JavaScript", "TypeScript", "Go", "Java", "Rust", "SQL", "Bash"],
    "Frameworks":  ["Django", "React", "Node.js", "FastAPI", "Spring Boot", "Next.js", "Vue.js"],
    "Tools":       ["Docker", "Kubernetes", "Terraform", "Git", "Jenkins", "GitHub Actions", "Ansible"],
    "Databases":   ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "DynamoDB"],
    "Cloud":       ["AWS", "GCP", "Azure", "Heroku", "Vercel"],
    "Soft Skills": ["Leadership", "Communication", "Problem Solving", "Agile", "Mentoring"],
}

PROJECTS = [
    {
        "name": "OpenResume",
        "description": "Open-source resume builder with ATS optimization and PDF export.",
        "technologies": "React, TypeScript, Node.js, PostgreSQL",
        "impact": "1,200+ GitHub stars; used by 3,000+ job seekers",
        "url": "https://github.com/alexjohnson/openresume",
    },
    {
        "name": "PriceWatch",
        "description": "E-commerce price tracking tool with email alerts and historical charts.",
        "technologies": "Python, Django, Celery, Redis, Chart.js",
        "impact": "Tracked 50K+ products; 800 active users",
        "url": "https://github.com/sarahchen/pricewatch",
    },
    {
        "name": "DevMetrics",
        "description": "Engineering productivity dashboard aggregating data from GitHub, Jira, and PagerDuty.",
        "technologies": "Python, FastAPI, React, PostgreSQL, Docker",
        "impact": "Adopted by 12 engineering teams; reduced incident MTTR by 20%",
        "url": "https://github.com/marcuslee/devmetrics",
    },
    {
        "name": "SmartBudget",
        "description": "Personal finance app with ML-powered spending categorization.",
        "technologies": "Python, scikit-learn, Flask, SQLite, React Native",
        "impact": "4.6-star rating on App Store; 10K+ downloads",
        "url": "https://github.com/alexjohnson/smartbudget",
    },
]

CERTIFICATIONS = [
    ("AWS Certified Solutions Architect – Associate", "Amazon Web Services", "2023-03-15", "2026-03-15"),
    ("Google Professional Cloud Developer", "Google Cloud", "2022-11-01", "2024-11-01"),
    ("Certified Kubernetes Administrator (CKA)", "Cloud Native Computing Foundation", "2023-07-20", None),
    ("Professional Scrum Master I (PSM I)", "Scrum.org", "2021-05-10", None),
    ("HashiCorp Certified: Terraform Associate", "HashiCorp", "2023-01-08", "2025-01-08"),
]

JOB_DESCRIPTIONS = [
    {
        "title": "Senior Software Engineer @ Stripe",
        "company": "Stripe",
        "content": (
            "We are looking for a Senior Software Engineer to join our Payments Infrastructure team. "
            "You will design and build highly reliable, scalable systems that process millions of transactions daily. "
            "Requirements: 5+ years of experience, proficiency in Python or Go, experience with distributed systems, "
            "strong understanding of databases and caching, excellent communication skills."
        ),
    },
    {
        "title": "Staff Engineer @ Shopify",
        "company": "Shopify",
        "content": (
            "Shopify is seeking a Staff Engineer to lead technical strategy for our Merchant Platform. "
            "You will drive architecture decisions, mentor senior engineers, and collaborate with product leadership. "
            "Requirements: 8+ years of experience, deep expertise in Ruby on Rails or Python, "
            "experience leading large-scale migrations, strong written communication."
        ),
    },
    {
        "title": "ML Engineer @ Datadog",
        "company": "Datadog",
        "content": (
            "Join Datadog's AI/ML team to build intelligent alerting and anomaly detection features. "
            "You will develop and deploy ML models at scale using Python, TensorFlow, and Kubernetes. "
            "Requirements: 3+ years of ML engineering experience, strong Python skills, "
            "experience with time-series data, familiarity with MLOps practices."
        ),
    },
]

APPLICATION_DATA = [
    ("Google", "Senior Software Engineer", "applied", 78.5),
    ("Stripe", "Staff Engineer", "interview", 85.0),
    ("Airbnb", "Backend Engineer", "saved", None),
    ("Meta", "Software Engineer E5", "rejected", 62.0),
    ("Shopify", "Senior Backend Developer", "offer", 91.0),
    ("Netflix", "Senior Software Engineer", "applied", 74.0),
    ("Datadog", "ML Engineer", "interview", 80.5),
    ("Twilio", "Platform Engineer", "withdrawn", 55.0),
]

COVER_LETTER_TEMPLATE = (
    "Dear Hiring Manager,\n\n"
    "I am excited to apply for the {role} position at {company}. With my background in software engineering "
    "and a passion for building scalable, reliable systems, I believe I would be a strong addition to your team.\n\n"
    "In my previous roles, I have delivered impactful projects including reducing API latency by 40%, "
    "leading a microservices migration, and mentoring junior engineers. I thrive in collaborative environments "
    "and am energized by technically challenging problems.\n\n"
    "I would love the opportunity to discuss how my experience aligns with {company}'s goals. "
    "Thank you for your consideration.\n\n"
    "Best regards,\n{name}"
)

INTERVIEW_QUESTIONS = [
    {
        "question": "Tell me about a time you had to make a difficult technical trade-off.",
        "category": "Behavioral",
        "talking_points": ["Describe the context", "Explain the options considered", "Justify your decision", "Share the outcome"],
        "resume_evidence": "Led microservices migration with trade-offs between speed and reliability",
    },
    {
        "question": "How do you design a system to handle 10x traffic growth?",
        "category": "System Design",
        "talking_points": ["Horizontal scaling", "Caching layers", "Database sharding", "Load balancing", "Async processing"],
        "resume_evidence": "Designed notification system for 2M+ DAU",
    },
    {
        "question": "Describe your approach to code reviews.",
        "category": "Behavioral",
        "talking_points": ["Focus on learning, not criticism", "Automate style checks", "Prioritize correctness and maintainability"],
        "resume_evidence": "Mentored 4 junior engineers",
    },
]


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def rand_date(start_year: int, end_year: int) -> date:
    start = date(start_year, 1, 1)
    end   = date(end_year, 12, 31)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def rand_past_datetime(days_back: int = 365):
    return timezone.now() - timedelta(days=random.randint(1, days_back))


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------

class Command(BaseCommand):
    help = "Seed the database with realistic mock data for development and testing."

    def add_arguments(self, parser):
        parser.add_argument(
            "--users",
            type=int,
            default=len(USERS),
            help="Number of mock users to create (max %d)" % len(USERS),
        )
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete all existing mock data before seeding.",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            self._flush()

        num_users = min(options["users"], len(USERS))
        self.stdout.write(self.style.MIGRATE_HEADING(f"\n🌱  Seeding mock data for {num_users} user(s)...\n"))

        for user_data in USERS[:num_users]:
            user = self._create_user(user_data)
            resumes = self._create_resumes(user)
            self._create_saved_job_descriptions(user)
            self._create_job_applications(user, resumes)
            self._create_activity_logs(user, resumes)
            self._create_skill_gap_analysis(user, resumes)

        self.stdout.write(self.style.SUCCESS("\n✅  Mock data seeded successfully!\n"))
        self.stdout.write("   Demo credentials  →  username: alex_johnson  |  password: mockpass123\n")

    # ------------------------------------------------------------------
    # Flush
    # ------------------------------------------------------------------

    def _flush(self):
        self.stdout.write(self.style.WARNING("  Flushing existing mock data..."))
        usernames = [u["username"] for u in USERS]
        users = User.objects.filter(username__in=usernames)
        # Cascading deletes handle related objects
        count, _ = users.delete()
        self.stdout.write(self.style.WARNING(f"  Deleted {count} user record(s) and all related data.\n"))

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------

    def _create_user(self, data: dict) -> User:
        user, created = User.objects.get_or_create(
            username=data["username"],
            defaults={
                "email":      data["email"],
                "first_name": data["first_name"],
                "last_name":  data["last_name"],
            },
        )
        if created:
            user.set_password(data["password"])
            user.save()
            self.stdout.write(f"  👤  Created user: {user.username}")
        else:
            self.stdout.write(f"  👤  User already exists, skipping: {user.username}")
        return user

    # ------------------------------------------------------------------
    # Resumes
    # ------------------------------------------------------------------

    def _create_resumes(self, user: User) -> list:
        resumes = []
        resume_titles = [
            f"{user.first_name} {user.last_name} — Software Engineer",
            f"{user.first_name} {user.last_name} — Senior Developer",
            f"{user.first_name} {user.last_name} — Tech Lead",
        ]

        for i, title in enumerate(resume_titles):
            resume = Resume.objects.create(
                user=user,
                title=title,
                template=random.choice(RESUME_TEMPLATES),
                summary=SUMMARIES[i % len(SUMMARIES)],
                is_draft=(i == 2),  # last one is a draft
                color_scheme=random.choice(COLOR_SCHEMES),
                font_family=random.choice(FONT_FAMILIES),
                latest_ats_score=round(random.uniform(55, 95), 1),
                completeness_score=random.randint(70, 100),
                last_analyzed_at=rand_past_datetime(90),
                last_optimized_at=rand_past_datetime(60),
                current_version_number=random.randint(2, 5),
            )

            self._create_personal_info(resume, user)
            self._create_experiences(resume)
            self._create_education(resume)
            self._create_skills(resume)
            self._create_projects(resume)
            self._create_certifications(resume)
            self._create_resume_versions(resume)
            self._create_resume_analyses(resume)

            resumes.append(resume)
            self.stdout.write(f"    📄  Resume: {resume.title}")

        return resumes

    def _create_personal_info(self, resume: Resume, user: User):
        PersonalInfo.objects.create(
            resume=resume,
            full_name=f"{user.first_name} {user.last_name}",
            phone=f"+1 ({random.randint(200,999)}) {random.randint(100,999)}-{random.randint(1000,9999)}",
            email=user.email,
            linkedin=f"https://linkedin.com/in/{user.username}",
            github=f"https://github.com/{user.username}",
            location=random.choice(LOCATIONS),
        )

    def _create_experiences(self, resume: Resume):
        num = random.randint(2, 4)
        end_year = date.today().year
        for i in range(num):
            start_year = end_year - random.randint(1, 3)
            start = date(start_year, random.randint(1, 12), 1)
            end   = date(end_year, random.randint(1, 12), 1) if i > 0 else None  # current role has no end
            achievements = random.sample(ACHIEVEMENTS_POOL, k=random.randint(3, 5))
            Experience.objects.create(
                resume=resume,
                company=random.choice(COMPANIES),
                role=random.choice(ROLES),
                location=random.choice(LOCATIONS),
                start_date=start,
                end_date=end,
                description="Worked on core platform features, collaborated with cross-functional teams, "
                            "and contributed to technical roadmap planning.",
                achievements="\n".join(f"• {a}" for a in achievements),
                order=i,
            )
            end_year = start_year - 1

    def _create_education(self, resume: Resume):
        num = random.randint(1, 2)
        for i, (institution, degree, field) in enumerate(random.sample(INSTITUTIONS, num)):
            end_year   = date.today().year - random.randint(2, 8)
            start_year = end_year - random.randint(3, 4)
            Education.objects.create(
                resume=resume,
                institution=institution,
                degree=degree,
                field=field,
                start_year=start_year,
                end_year=end_year,
                gpa=round(random.uniform(3.2, 4.0), 2),
                honors=random.choice(["Dean's List", "Magna Cum Laude", "Summa Cum Laude", ""]),
                relevant_coursework="Algorithms, Data Structures, Operating Systems, Distributed Systems, Machine Learning",
                order=i,
            )

    def _create_skills(self, resume: Resume):
        proficiency_levels = ["beginner", "intermediate", "advanced", "expert"]
        for category, skill_list in SKILL_SETS.items():
            selected = random.sample(skill_list, k=random.randint(2, min(4, len(skill_list))))
            for skill_name in selected:
                Skill.objects.get_or_create(
                    resume=resume,
                    name=skill_name,
                    defaults={
                        "category": category,
                        "proficiency_level": random.choice(proficiency_levels),
                        "years_of_experience": random.randint(1, 7),
                    },
                )

    def _create_projects(self, resume: Resume):
        selected = random.sample(PROJECTS, k=random.randint(2, len(PROJECTS)))
        for i, proj in enumerate(selected):
            start = rand_date(2020, 2023)
            end   = start + timedelta(days=random.randint(60, 365))
            Project.objects.create(
                resume=resume,
                name=proj["name"],
                description=proj["description"],
                technologies=proj["technologies"],
                impact=proj["impact"],
                url=proj["url"],
                start_date=start,
                end_date=end,
                order=i,
            )

    def _create_certifications(self, resume: Resume):
        selected = random.sample(CERTIFICATIONS, k=random.randint(1, 3))
        for i, (name, issuer, issue_str, expiry_str) in enumerate(selected):
            issue_date  = date.fromisoformat(issue_str)
            expiry_date = date.fromisoformat(expiry_str) if expiry_str else None
            Certification.objects.create(
                resume=resume,
                name=name,
                issuer=issuer,
                issue_date=issue_date,
                expiry_date=expiry_date,
                credential_id=f"CERT-{random.randint(100000, 999999)}",
                order=i,
            )

    def _create_resume_versions(self, resume: Resume):
        mod_types = ["manual", "optimized", "restored"]
        for v in range(1, resume.current_version_number + 1):
            snapshot = {
                "title": resume.title,
                "summary": resume.summary,
                "version": v,
                "experiences": [],
                "education": [],
                "skills": [],
            }
            ResumeVersion.objects.create(
                resume=resume,
                version_number=v,
                modification_type=random.choice(mod_types),
                ats_score=round(random.uniform(50, 95), 1),
                snapshot_data=snapshot,
                user_notes=f"Version {v} snapshot" if v > 1 else "Initial version",
            )

    def _create_resume_analyses(self, resume: Resume):
        jd = random.choice(JOB_DESCRIPTIONS)
        matched   = random.sample(["Python", "Django", "REST API", "PostgreSQL", "Docker", "AWS", "CI/CD"], k=4)
        missing   = random.sample(["Kubernetes", "Terraform", "Go", "GraphQL", "Redis"], k=2)
        weak_verbs = ["worked on", "helped with", "was responsible for"]
        suggestions = [
            "Add quantifiable metrics to your experience bullet points.",
            "Include more industry-specific keywords from the job description.",
            "Strengthen action verbs — replace 'worked on' with 'engineered' or 'architected'.",
        ]
        ResumeAnalysis.objects.create(
            resume=resume,
            job_description=jd["content"],
            keyword_match_score=round(random.uniform(55, 90), 1),
            skill_relevance_score=round(random.uniform(60, 95), 1),
            section_completeness_score=round(random.uniform(70, 100), 1),
            experience_impact_score=round(random.uniform(50, 90), 1),
            quantification_score=round(random.uniform(45, 85), 1),
            action_verb_score=round(random.uniform(55, 90), 1),
            final_score=round(random.uniform(60, 92), 1),
            matched_keywords=matched,
            missing_keywords=missing,
            weak_action_verbs=weak_verbs,
            missing_quantifications=["Add metrics to experience at " + random.choice(COMPANIES)],
            suggestions=suggestions,
        )

    # ------------------------------------------------------------------
    # Saved Job Descriptions
    # ------------------------------------------------------------------

    def _create_saved_job_descriptions(self, user: User):
        for jd in JOB_DESCRIPTIONS:
            SavedJobDescription.objects.create(
                user=user,
                title=jd["title"],
                company=jd["company"],
                content=jd["content"],
                last_used_at=rand_past_datetime(30),
            )

    # ------------------------------------------------------------------
    # Job Applications
    # ------------------------------------------------------------------

    def _create_job_applications(self, user: User, resumes: list):
        for company, role, status, ats_score in APPLICATION_DATA:
            resume = random.choice(resumes)
            applied_date = rand_date(2024, 2025) if status != "saved" else None
            app = JobApplication.objects.create(
                user=user,
                company=company,
                role=role,
                job_url=f"https://careers.{company.lower().replace(' ', '')}.com/jobs/12345",
                job_description=random.choice(JOB_DESCRIPTIONS)["content"],
                resume=resume,
                status=status,
                ats_score_at_apply=ats_score,
                applied_date=applied_date,
                notes=f"Applied via LinkedIn. Referral from a friend at {company}." if status != "saved" else "",
            )

            # Cover letter for applied/interview/offer applications
            if status in ("applied", "interview", "offer"):
                full_name = f"{user.first_name} {user.last_name}"
                CoverLetter.objects.create(
                    user=user,
                    application=app,
                    resume=resume,
                    company=company,
                    role=role,
                    content=COVER_LETTER_TEMPLATE.format(role=role, company=company, name=full_name),
                )

            # Interview prep for interview/offer applications
            if status in ("interview", "offer"):
                InterviewPrepSession.objects.create(
                    user=user,
                    application=app,
                    resume=resume,
                    role=role,
                    company=company,
                    job_description=random.choice(JOB_DESCRIPTIONS)["content"],
                    questions=INTERVIEW_QUESTIONS,
                )

    # ------------------------------------------------------------------
    # Activity Logs
    # ------------------------------------------------------------------

    def _create_activity_logs(self, user: User, resumes: list):
        actions = [
            ("resume_created",   "Created resume '{title}'"),
            ("resume_updated",   "Updated resume '{title}'"),
            ("resume_analyzed",  "Analyzed resume '{title}' against a job description"),
            ("resume_optimized", "Optimized resume '{title}' — score improved by 12 points"),
            ("resume_exported",  "Exported resume '{title}' as PDF"),
            ("application_created", "Added job application for Software Engineer at Google"),
            ("application_updated", "Updated application status to Interview"),
        ]
        for resume in resumes:
            for action, desc_template in random.sample(actions, k=random.randint(3, 5)):
                ActivityLog.objects.create(
                    user=user,
                    action=action,
                    description=desc_template.format(title=resume.title),
                    resume_id=resume.id,
                    resume_title=resume.title,
                    metadata={"source": "mock_data"},
                )

    # ------------------------------------------------------------------
    # Skill Gap Analysis
    # ------------------------------------------------------------------

    def _create_skill_gap_analysis(self, user: User, resumes: list):
        resume = resumes[0]
        SkillGapAnalysis.objects.create(
            user=user,
            resume=resume,
            target_role="Staff Software Engineer",
            job_descriptions=[jd["content"] for jd in JOB_DESCRIPTIONS],
            missing_skills=[
                {"skill": "Kubernetes", "frequency": 3, "importance": "high"},
                {"skill": "Go",         "frequency": 2, "importance": "medium"},
                {"skill": "GraphQL",    "frequency": 2, "importance": "medium"},
                {"skill": "Terraform",  "frequency": 1, "importance": "low"},
            ],
            present_skills=["Python", "Django", "PostgreSQL", "Docker", "AWS", "React"],
            recommendations=[
                "Complete the Certified Kubernetes Administrator (CKA) course.",
                "Build a side project using Go to demonstrate proficiency.",
                "Add a GraphQL API to one of your existing projects.",
            ],
        )
