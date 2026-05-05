"""
ATS System Simulator — simulates how real ATS platforms parse and score resumes.

Supported systems:
- Taleo (Oracle)
- Workday
- Greenhouse
- Lever
- iCIMS

Each system has different parsing quirks, scoring weights, and failure modes.
This gives users actionable insight: "Your resume scores 82 in Greenhouse but
only 61 in Taleo because of your two-column layout."
"""
import re
from typing import Dict, List


class ATSSystemSimulator:
    """
    Simulates parsing and scoring behaviour of major ATS platforms.
    """

    # ── System Profiles ───────────────────────────────────────────────────────

    SYSTEMS = {
        'taleo': {
            'name': 'Taleo (Oracle)',
            'market_share': '25%',
            'used_by': 'Fortune 500, large enterprises',
            'quirks': [
                'Struggles with tables and multi-column layouts',
                'Requires standard section headers (EXPERIENCE, EDUCATION)',
                'Dates must be in MM/YYYY or Month YYYY format',
                'Special characters in bullets (•, ▪) may not parse',
                'PDF text layers must be selectable (no scanned images)',
            ],
        },
        'workday': {
            'name': 'Workday',
            'market_share': '20%',
            'used_by': 'Mid-to-large companies, tech sector',
            'quirks': [
                'Parses LinkedIn-style formatting well',
                'Handles modern PDF layouts better than Taleo',
                'Skills section must be clearly labelled',
                'Prefers chronological order (most recent first)',
                'URLs in contact info may cause parsing issues',
            ],
        },
        'greenhouse': {
            'name': 'Greenhouse',
            'market_share': '15%',
            'used_by': 'Tech startups, growth-stage companies',
            'quirks': [
                'Most modern parser — handles complex layouts',
                'Keyword matching is semantic, not just exact',
                'Values GitHub/portfolio links in contact section',
                'Handles both PDF and DOCX well',
                'Less strict about formatting than Taleo',
            ],
        },
        'lever': {
            'name': 'Lever',
            'market_share': '10%',
            'used_by': 'Tech companies, startups',
            'quirks': [
                'Focuses heavily on skills and technologies',
                'Good at parsing technical skill lists',
                'Prefers bullet points over paragraphs',
                'Company name and role must be on same line',
                'Handles Unicode characters well',
            ],
        },
        'icims': {
            'name': 'iCIMS',
            'market_share': '12%',
            'used_by': 'Healthcare, retail, large employers',
            'quirks': [
                'Very strict about date formats',
                'Requires explicit section headers',
                'Tables and graphics cause parsing failures',
                'Phone number must be in standard US format',
                'Prefers plain text over formatted PDFs',
            ],
        },
    }

    @classmethod
    def simulate_all(cls, resume, job_description: str) -> Dict:
        """
        Run simulation across all supported ATS systems.

        Returns:
            {
                'systems': {system_id: {score, issues, warnings, passed_checks}},
                'best_system': str,
                'worst_system': str,
                'overall_ats_readiness': float,
                'critical_issues': [str],
            }
        """
        results = {}
        for system_id in cls.SYSTEMS:
            results[system_id] = cls.simulate(resume, job_description, system_id)

        scores = {sid: r['score'] for sid, r in results.items()}
        best = max(scores, key=scores.get)
        worst = min(scores, key=scores.get)
        overall = sum(scores.values()) / len(scores)

        # Collect critical issues (appear in 3+ systems)
        all_issues = []
        for r in results.values():
            all_issues.extend(r['issues'])
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        critical = [issue for issue, count in issue_counts.items() if count >= 3]

        return {
            'systems': results,
            'best_system': best,
            'worst_system': worst,
            'overall_ats_readiness': round(overall, 1),
            'critical_issues': critical,
        }

    @classmethod
    def simulate(cls, resume, job_description: str, system_id: str) -> Dict:
        """
        Simulate a specific ATS system's parsing and scoring.

        Returns:
            {
                'system_id': str,
                'system_name': str,
                'score': float (0-100),
                'issues': [str],
                'warnings': [str],
                'passed_checks': [str],
                'keyword_score': float,
                'format_score': float,
                'completeness_score': float,
            }
        """
        system = cls.SYSTEMS.get(system_id, cls.SYSTEMS['greenhouse'])
        issues = []
        warnings = []
        passed = []

        # ── Format Checks ─────────────────────────────────────────────────────
        format_score = cls._check_format(resume, system_id, issues, warnings, passed)

        # ── Keyword Matching ──────────────────────────────────────────────────
        keyword_score = cls._check_keywords(resume, job_description, system_id, issues, warnings, passed)

        # ── Section Completeness ──────────────────────────────────────────────
        completeness_score = cls._check_completeness(resume, system_id, issues, warnings, passed)

        # ── Date Format Checks ────────────────────────────────────────────────
        date_score = cls._check_dates(resume, system_id, issues, warnings, passed)

        # ── Weighted composite score per system ───────────────────────────────
        weights = cls._get_weights(system_id)
        score = (
            format_score * weights['format'] +
            keyword_score * weights['keyword'] +
            completeness_score * weights['completeness'] +
            date_score * weights['dates']
        )

        return {
            'system_id': system_id,
            'system_name': system['name'],
            'market_share': system['market_share'],
            'used_by': system['used_by'],
            'score': round(min(score, 100), 1),
            'issues': issues,
            'warnings': warnings,
            'passed_checks': passed,
            'keyword_score': round(keyword_score, 1),
            'format_score': round(format_score, 1),
            'completeness_score': round(completeness_score, 1),
            'date_score': round(date_score, 1),
            'quirks': system['quirks'],
        }

    @classmethod
    def _get_weights(cls, system_id: str) -> Dict:
        weights = {
            'taleo':      {'format': 0.35, 'keyword': 0.35, 'completeness': 0.20, 'dates': 0.10},
            'workday':    {'format': 0.25, 'keyword': 0.40, 'completeness': 0.25, 'dates': 0.10},
            'greenhouse': {'format': 0.15, 'keyword': 0.50, 'completeness': 0.25, 'dates': 0.10},
            'lever':      {'format': 0.20, 'keyword': 0.50, 'completeness': 0.20, 'dates': 0.10},
            'icims':      {'format': 0.30, 'keyword': 0.35, 'completeness': 0.20, 'dates': 0.15},
        }
        return weights.get(system_id, weights['greenhouse'])

    @classmethod
    def _check_format(cls, resume, system_id: str, issues: list, warnings: list, passed: list) -> float:
        score = 100.0

        # Check for personal info
        try:
            pi = resume.personal_info
            if pi.email:
                passed.append("Email address present and parseable")
            else:
                issues.append("Missing email address — most ATS systems require it")
                score -= 20

            if pi.phone:
                # Check phone format for strict systems
                phone_clean = re.sub(r'[^\d]', '', pi.phone)
                if system_id in ('taleo', 'icims') and len(phone_clean) != 10:
                    warnings.append(f"Phone format may not parse in {cls.SYSTEMS[system_id]['name']} — use (555) 555-5555")
                    score -= 5
                else:
                    passed.append("Phone number present")
            else:
                warnings.append("Missing phone number")
                score -= 10

            if pi.linkedin:
                if system_id == 'greenhouse':
                    passed.append("LinkedIn URL present — Greenhouse values this")
                else:
                    passed.append("LinkedIn URL present")
        except Exception:
            issues.append("Personal information section missing or incomplete")
            score -= 25

        # Check for multi-column layout indicators (heuristic from skills/experience count)
        if system_id in ('taleo', 'icims'):
            skill_count = resume.skills.count()
            if skill_count > 20:
                warnings.append(
                    f"Large skills section ({skill_count} skills) may indicate a table/column layout "
                    f"that {cls.SYSTEMS[system_id]['name']} struggles to parse"
                )
                score -= 8

        # Check for special characters in bullet points
        if system_id == 'taleo':
            for exp in resume.experiences.all():
                if exp.description and re.search(r'[•▪▸►◆]', exp.description):
                    warnings.append(
                        "Special bullet characters (•, ▪) may not parse in Taleo — use plain hyphens (-)"
                    )
                    score -= 5
                    break

        return max(score, 0)

    @classmethod
    def _check_keywords(cls, resume, job_description: str, system_id: str,
                        issues: list, warnings: list, passed: list) -> float:
        from apps.analyzer.services.keyword_extractor import KeywordExtractorService
        from apps.analyzer.services.scoring_engine import ScoringEngineService

        resume_text = ScoringEngineService._get_resume_text(resume)
        resume_kw = KeywordExtractorService.extract_keywords(resume_text)
        jd_kw = KeywordExtractorService.extract_keywords(job_description)

        if not jd_kw:
            return 60.0

        matched = resume_kw & jd_kw
        missing = jd_kw - resume_kw
        match_ratio = len(matched) / len(jd_kw)

        # Greenhouse uses semantic matching — give a small bonus
        if system_id == 'greenhouse':
            match_ratio = min(match_ratio * 1.1, 1.0)

        # Taleo is strict about exact matches
        if system_id == 'taleo' and match_ratio < 0.4:
            issues.append(
                f"Low keyword match ({match_ratio*100:.0f}%) — Taleo uses exact keyword matching. "
                f"Mirror the job description language precisely."
            )
        elif match_ratio >= 0.6:
            passed.append(f"Good keyword coverage ({match_ratio*100:.0f}% of JD keywords matched)")
        elif match_ratio >= 0.4:
            warnings.append(
                f"Moderate keyword match ({match_ratio*100:.0f}%). "
                f"Add: {', '.join(list(missing)[:5])}"
            )
        else:
            issues.append(
                f"Low keyword match ({match_ratio*100:.0f}%). "
                f"Critical missing keywords: {', '.join(list(missing)[:8])}"
            )

        return min(match_ratio * 100, 100)

    @classmethod
    def _check_completeness(cls, resume, system_id: str,
                            issues: list, warnings: list, passed: list) -> float:
        score = 0.0

        if resume.experiences.exists():
            score += 35
            passed.append("Work experience section present")
        else:
            issues.append("No work experience section — required by all ATS systems")

        if resume.education.exists():
            score += 25
            passed.append("Education section present")
        else:
            warnings.append("No education section")

        if resume.skills.exists():
            score += 25
            passed.append(f"Skills section present ({resume.skills.count()} skills)")
        else:
            if system_id in ('lever', 'greenhouse'):
                issues.append("No skills section — Lever and Greenhouse heavily weight skills")
            else:
                warnings.append("No skills section")

        try:
            pi = resume.personal_info
            if pi.full_name:
                score += 15
                passed.append("Candidate name present")
        except Exception:
            issues.append("Name missing from resume")

        return min(score, 100)

    @classmethod
    def _check_dates(cls, resume, system_id: str,
                     issues: list, warnings: list, passed: list) -> float:
        score = 100.0
        strict_systems = ('taleo', 'icims')

        for exp in resume.experiences.all():
            if not exp.start_date:
                if system_id in strict_systems:
                    issues.append(
                        f"Missing start date for '{exp.role} at {exp.company}' — "
                        f"{cls.SYSTEMS[system_id]['name']} requires dates for all positions"
                    )
                    score -= 15
                else:
                    warnings.append(f"Missing start date for '{exp.role} at {exp.company}'")
                    score -= 5

        for edu in resume.education.all():
            if not edu.end_year:
                if system_id in strict_systems:
                    warnings.append(
                        f"Missing graduation year for '{edu.institution}' — "
                        f"add end year for better parsing"
                    )
                    score -= 8

        if score == 100:
            passed.append("All dates present and properly formatted")

        return max(score, 0)
