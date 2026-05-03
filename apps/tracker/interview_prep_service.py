import re
from apps.resumes.models import Resume


class InterviewPrepService:
    """
    Generates interview questions tailored to the resume + job description.
    No external API needed — uses resume data and JD keyword analysis.
    """

    BEHAVIORAL_TEMPLATES = [
        ("Tell me about a time you {verb} {context}.", "behavioral"),
        ("Describe a situation where you had to {verb} {context}.", "behavioral"),
        ("Give me an example of when you {verb} under pressure.", "behavioral"),
        ("What's your biggest achievement related to {context}?", "behavioral"),
    ]

    TECHNICAL_TEMPLATES = [
        ("How have you used {skill} in a production environment?", "technical"),
        ("Walk me through your experience with {skill}.", "technical"),
        ("What challenges have you faced working with {skill} and how did you solve them?", "technical"),
        ("How would you compare {skill} to alternatives you've used?", "technical"),
    ]

    ROLE_TEMPLATES = [
        ("Why are you interested in this {role} position?", "motivation"),
        ("Where do you see yourself in 5 years as a {role}?", "motivation"),
        ("What does success look like to you in a {role} role?", "motivation"),
        ("What's the most complex {role} challenge you've tackled?", "situational"),
    ]

    UNIVERSAL = [
        ("Tell me about yourself.", "introduction"),
        ("What are your greatest strengths?", "self-assessment"),
        ("What is your biggest weakness and how are you working on it?", "self-assessment"),
        ("Why are you leaving your current role?", "motivation"),
        ("Do you have any questions for us?", "closing"),
    ]

    def generate(self, resume: Resume, role: str, job_description: str, company: str = '') -> list:
        questions = []

        # 1. Universal questions always included
        for q, cat in self.UNIVERSAL:
            questions.append(self._build(q, cat, resume, role))

        # 2. Role-specific questions
        for template, cat in self.ROLE_TEMPLATES[:2]:
            q = template.format(role=role)
            questions.append(self._build(q, cat, resume, role))

        # 3. Technical questions from resume skills + JD keywords
        skills = list(resume.skills.values_list('name', flat=True)[:8])
        jd_skills = self._extract_tech_skills(job_description)
        combined_skills = list(dict.fromkeys(jd_skills + skills))[:6]

        for skill in combined_skills[:4]:
            template, cat = self.TECHNICAL_TEMPLATES[len(questions) % len(self.TECHNICAL_TEMPLATES)]
            q = template.format(skill=skill)
            questions.append(self._build(q, cat, resume, role, skill=skill))

        # 4. Behavioral questions from experience achievements
        experiences = resume.experiences.order_by('-start_date')[:3]
        verbs_contexts = self._extract_verbs_contexts(experiences)
        for verb, context in verbs_contexts[:3]:
            template, cat = self.BEHAVIORAL_TEMPLATES[len(questions) % len(self.BEHAVIORAL_TEMPLATES)]
            q = template.format(verb=verb, context=context)
            questions.append(self._build(q, cat, resume, role, verb=verb, context=context))

        # 5. JD-specific questions
        jd_themes = self._extract_jd_themes(job_description)
        for theme in jd_themes[:2]:
            q = f"The role mentions {theme} — can you walk us through your experience with that?"
            questions.append(self._build(q, 'situational', resume, role))

        return questions[:15]  # Cap at 15 questions

    def _build(self, question: str, category: str, resume: Resume, role: str,
               skill: str = '', verb: str = '', context: str = '') -> dict:
        talking_points = self._talking_points(category, resume, role, skill, verb, context)
        evidence = self._find_resume_evidence(resume, skill or context)
        return {
            'question': question,
            'category': category,
            'talking_points': talking_points,
            'resume_evidence': evidence,
        }

    def _talking_points(self, category, resume, role, skill='', verb='', context='') -> list:
        points = []
        if category == 'introduction':
            exp = resume.experiences.order_by('-start_date').first()
            edu = resume.education.order_by('-end_year').first()
            if exp:
                points.append(f"Start with your most recent role: {exp.role} at {exp.company}")
            if edu:
                points.append(f"Mention your {edu.degree} from {edu.institution}")
            points.append(f"Connect your background to why you want this {role} role")
            points.append("Keep it under 2 minutes — end with why you're here today")

        elif category == 'technical':
            points.append(f"Describe a specific project where you used {skill}")
            points.append("Mention scale: team size, data volume, users impacted")
            points.append("Include a challenge you overcame and what you learned")
            points.append("Compare to alternatives if relevant (shows depth)")

        elif category == 'behavioral':
            points.append("Use the STAR method: Situation, Task, Action, Result")
            points.append("Quantify the result if possible (%, $, time saved)")
            points.append(f"Pick an example that directly relates to {role} responsibilities")
            points.append("Keep the focus on YOUR actions, not the team's")

        elif category == 'motivation':
            points.append(f"Research the company before the interview")
            points.append(f"Connect your career goals to this {role} position specifically")
            points.append("Be honest but frame everything positively")

        elif category == 'self-assessment':
            points.append("For strengths: pick ones relevant to the role with evidence")
            points.append("For weaknesses: choose real ones you're actively improving")
            points.append("Show self-awareness — avoid clichés like 'I work too hard'")

        else:
            points.append("Be specific and concise")
            points.append("Use examples from your resume where possible")

        return points

    def _find_resume_evidence(self, resume: Resume, keyword: str) -> str:
        if not keyword:
            return ''
        kw_lower = keyword.lower()
        for exp in resume.experiences.all():
            text = f"{exp.description} {exp.achievements}".lower()
            if kw_lower in text:
                # Return first relevant sentence
                for line in (exp.achievements or exp.description or '').split('\n'):
                    if kw_lower in line.lower() and line.strip():
                        return f"{exp.role} at {exp.company}: {line.strip().lstrip('•-– ')}"
        for proj in resume.projects.all():
            if kw_lower in f"{proj.description} {proj.technologies}".lower():
                return f"Project '{proj.name}': {proj.description[:120]}"
        return ''

    def _extract_tech_skills(self, jd: str) -> list:
        tech_pattern = re.compile(
            r'\b(Python|Java|JavaScript|TypeScript|React|Node\.js|Django|Flask|'
            r'AWS|Azure|GCP|Docker|Kubernetes|SQL|PostgreSQL|MongoDB|Redis|'
            r'Git|CI/CD|REST|GraphQL|Machine Learning|TensorFlow|PyTorch|'
            r'Agile|Scrum|Linux|Terraform|Spark|Kafka|Elasticsearch)\b',
            re.IGNORECASE
        )
        found = tech_pattern.findall(jd)
        return list(dict.fromkeys(found))  # deduplicate preserving order

    def _extract_verbs_contexts(self, experiences) -> list:
        strong_verbs = ['led', 'built', 'designed', 'delivered', 'managed', 'improved',
                        'reduced', 'increased', 'launched', 'developed', 'architected',
                        'optimized', 'scaled', 'mentored', 'drove']
        results = []
        for exp in experiences:
            text = exp.achievements or exp.description or ''
            for line in text.split('\n'):
                line = line.strip().lstrip('•-– ')
                if not line:
                    continue
                first_word = line.split()[0].lower().rstrip('d') if line.split() else ''
                for verb in strong_verbs:
                    if verb.startswith(first_word) and len(first_word) > 2:
                        context = f"at {exp.company}"
                        results.append((verb, context))
                        break
            if len(results) >= 3:
                break
        return results or [('delivered results', 'in a fast-paced environment')]

    def _extract_jd_themes(self, jd: str) -> list:
        themes = []
        patterns = [
            r'experience (?:with|in) ([^,.]+)',
            r'knowledge of ([^,.]+)',
            r'ability to ([^,.]+)',
            r'strong ([^,.]+) skills',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, jd, re.IGNORECASE)
            for m in matches:
                m = m.strip()
                if 5 < len(m) < 60:
                    themes.append(m)
            if len(themes) >= 4:
                break
        return themes[:4]
