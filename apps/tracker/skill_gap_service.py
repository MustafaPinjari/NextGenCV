import re
from collections import Counter
from apps.resumes.models import Resume


class SkillGapService:
    """
    Analyses multiple job descriptions for a target role and identifies
    skills the user is missing vs what the market consistently demands.
    """

    # Curated skill lists by domain for fallback when JDs are sparse
    DOMAIN_SKILLS = {
        'software': ['Python', 'JavaScript', 'SQL', 'Git', 'Docker', 'AWS', 'REST APIs',
                     'Agile', 'CI/CD', 'Testing', 'Linux', 'React', 'Node.js'],
        'data': ['Python', 'SQL', 'Machine Learning', 'Pandas', 'NumPy', 'Tableau',
                 'Power BI', 'Statistics', 'TensorFlow', 'Spark', 'ETL', 'Data Visualization'],
        'product': ['Product Roadmap', 'User Research', 'A/B Testing', 'Agile', 'Scrum',
                    'Stakeholder Management', 'SQL', 'Analytics', 'Wireframing', 'OKRs'],
        'marketing': ['SEO', 'Google Analytics', 'Content Strategy', 'Social Media',
                      'Email Marketing', 'CRM', 'Copywriting', 'Paid Ads', 'HubSpot'],
        'design': ['Figma', 'Adobe XD', 'User Research', 'Prototyping', 'Wireframing',
                   'Design Systems', 'Accessibility', 'HTML/CSS', 'Sketch'],
    }

    def analyse(self, resume: Resume, target_role: str, job_descriptions: list) -> dict:
        """
        Args:
            resume: Resume object
            target_role: e.g. "Senior Python Developer"
            job_descriptions: list of JD strings (1-10)
        Returns:
            dict with missing_skills, present_skills, recommendations
        """
        resume_skills = {s.lower() for s in resume.skills.values_list('name', flat=True)}
        resume_text = self._resume_full_text(resume).lower()

        # Extract all skills mentioned across JDs
        jd_skill_counts = Counter()
        for jd in job_descriptions:
            for skill in self._extract_skills(jd):
                jd_skill_counts[skill.lower()] += 1

        # Fallback: use domain skills if JDs are sparse
        if len(jd_skill_counts) < 5:
            domain = self._detect_domain(target_role)
            for skill in self.DOMAIN_SKILLS.get(domain, self.DOMAIN_SKILLS['software']):
                jd_skill_counts[skill.lower()] = jd_skill_counts.get(skill.lower(), 0) + 1

        total_jds = max(len(job_descriptions), 1)

        missing, present = [], []
        for skill_lower, count in jd_skill_counts.most_common(30):
            frequency = round(count / total_jds * 100)
            in_resume = skill_lower in resume_skills or skill_lower in resume_text
            display_name = self._display_name(skill_lower, jd_skill_counts)
            entry = {
                'skill': display_name,
                'frequency': frequency,
                'importance': 'high' if frequency >= 60 else 'medium' if frequency >= 30 else 'low',
            }
            if in_resume:
                present.append(entry)
            else:
                missing.append(entry)

        recommendations = self._recommendations(missing[:10], target_role)

        return {
            'missing_skills': missing[:15],
            'present_skills': present[:15],
            'recommendations': recommendations,
            'coverage_score': round(len(present) / max(len(present) + len(missing), 1) * 100),
        }

    def _resume_full_text(self, resume: Resume) -> str:
        parts = [resume.summary or '']
        for exp in resume.experiences.all():
            parts.extend([exp.role, exp.description or '', exp.achievements or ''])
        for proj in resume.projects.all():
            parts.extend([proj.description or '', proj.technologies or ''])
        return ' '.join(parts)

    def _extract_skills(self, text: str) -> list:
        pattern = re.compile(
            r'\b(Python|Java(?:Script)?|TypeScript|React|Vue|Angular|Node\.js|'
            r'Django|Flask|FastAPI|Spring|\.NET|C\+\+|C#|Go|Rust|Kotlin|Swift|'
            r'AWS|Azure|GCP|Docker|Kubernetes|Terraform|Ansible|Jenkins|'
            r'SQL|PostgreSQL|MySQL|MongoDB|Redis|Elasticsearch|Kafka|Spark|'
            r'Git|CI/CD|REST|GraphQL|gRPC|Microservices|'
            r'Machine Learning|Deep Learning|TensorFlow|PyTorch|scikit-learn|'
            r'Pandas|NumPy|Tableau|Power BI|Excel|'
            r'Agile|Scrum|Kanban|JIRA|Confluence|'
            r'Linux|Bash|Shell|'
            r'Figma|Sketch|Adobe XD|'
            r'SEO|Google Analytics|HubSpot|Salesforce)\b',
            re.IGNORECASE
        )
        return [m.group(0) for m in pattern.finditer(text)]

    def _detect_domain(self, role: str) -> str:
        role_lower = role.lower()
        if any(w in role_lower for w in ['data', 'analyst', 'scientist', 'ml', 'ai']):
            return 'data'
        if any(w in role_lower for w in ['product', 'pm', 'manager']):
            return 'product'
        if any(w in role_lower for w in ['design', 'ux', 'ui']):
            return 'design'
        if any(w in role_lower for w in ['market', 'growth', 'seo', 'content']):
            return 'marketing'
        return 'software'

    def _display_name(self, skill_lower: str, counts: Counter) -> str:
        # Return the original casing from the counter key that matches
        for k in counts:
            if k.lower() == skill_lower:
                return k
        return skill_lower.title()

    def _recommendations(self, missing_skills: list, role: str) -> list:
        recs = []
        high = [s['skill'] for s in missing_skills if s['importance'] == 'high']
        medium = [s['skill'] for s in missing_skills if s['importance'] == 'medium']

        if high:
            recs.append({
                'priority': 'high',
                'action': f"Add {', '.join(high[:3])} to your resume — these appear in 60%+ of {role} job postings.",
            })
        if medium:
            recs.append({
                'priority': 'medium',
                'action': f"Consider learning {', '.join(medium[:3])} to broaden your appeal for {role} roles.",
            })
        if missing_skills:
            recs.append({
                'priority': 'low',
                'action': "If you have experience with any missing skills, add them even if they're not your primary focus.",
            })
        return recs
