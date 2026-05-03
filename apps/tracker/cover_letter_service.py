from apps.resumes.models import Resume


class CoverLetterService:
    """
    Generates a tailored cover letter from resume data and a job description.
    Uses template-based generation (no external API required).
    """

    STRONG_VERBS = ['led', 'built', 'delivered', 'drove', 'achieved', 'designed',
                    'developed', 'launched', 'managed', 'improved', 'reduced', 'increased']

    def generate(self, resume: Resume, company: str, role: str, job_description: str) -> str:
        info = getattr(resume, 'personal_info', None)
        name = info.full_name if info else resume.user.get_full_name() or resume.user.username

        # Extract top skills
        skills = list(resume.skills.values_list('name', flat=True)[:6])
        skills_str = ', '.join(skills) if skills else 'relevant technical and professional skills'

        # Extract top experience bullet
        top_exp = resume.experiences.order_by('-start_date').first()
        exp_sentence = ''
        if top_exp:
            exp_sentence = (
                f"Most recently, I served as {top_exp.role} at {top_exp.company}, "
                f"where I {self._first_achievement(top_exp)}."
            )

        # Extract a quantified achievement if available
        achievement = self._best_achievement(resume)

        # Pull 2-3 keywords from JD to mirror back
        jd_keywords = self._extract_jd_keywords(job_description, skills)
        kw_phrase = ' and '.join(jd_keywords[:2]) if jd_keywords else role

        summary = resume.summary.strip() if resume.summary else ''

        letter = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {role} position at {company}. With my background in {kw_phrase}, I am confident I can make an immediate and meaningful contribution to your team.

{exp_sentence}

{f'Throughout my career, {achievement}' if achievement else f'I bring hands-on experience in {skills_str}, and a track record of delivering results in fast-paced environments.'}

{f'{summary}' if summary else f'I am particularly drawn to {company} because of the opportunity to work on {role.lower()} challenges at scale. I thrive in collaborative environments and am passionate about delivering high-quality outcomes.'}

I would welcome the opportunity to discuss how my experience aligns with your needs. Thank you for your time and consideration.

Sincerely,
{name}"""

        return letter.strip()

    def _first_achievement(self, exp) -> str:
        if exp.achievements:
            first = exp.achievements.strip().split('\n')[0].lstrip('•-– ').strip()
            if first:
                return first.lower().rstrip('.')
        if exp.description:
            return exp.description.split('.')[0].lower().rstrip('.')
        return 'contributed to key initiatives'

    def _best_achievement(self, resume: Resume) -> str:
        import re
        for exp in resume.experiences.order_by('-start_date'):
            for line in exp.achievements.split('\n'):
                line = line.strip().lstrip('•-– ')
                if re.search(r'\d+%|\$\d+|\d+x|\d+ (users|customers|revenue|cost)', line, re.I):
                    return line[0].lower() + line[1:] if line else ''
        return ''

    def _extract_jd_keywords(self, job_description: str, resume_skills: list) -> list:
        import re
        words = re.findall(r'\b[A-Za-z][a-z]{3,}\b', job_description)
        freq = {}
        stop = {'with', 'that', 'this', 'will', 'have', 'from', 'your', 'their',
                'team', 'work', 'role', 'able', 'must', 'also', 'into', 'more',
                'about', 'what', 'when', 'where', 'which', 'would', 'should'}
        for w in words:
            wl = w.lower()
            if wl not in stop:
                freq[wl] = freq.get(wl, 0) + 1
        # Prefer words that also appear in resume skills
        skill_lower = {s.lower() for s in resume_skills}
        ranked = sorted(freq.items(), key=lambda x: (x[0] in skill_lower, x[1]), reverse=True)
        return [w for w, _ in ranked[:3]]
