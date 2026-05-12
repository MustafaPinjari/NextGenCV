v# NextGenCV — Main Code Reference

This document presents the key source files of the NextGenCV project, organised by layer. Each section includes the file path, a brief description of its purpose, and the complete source code.

---

## Table of Contents

1. [Data Models — `apps/resumes/models.py`](#1-data-models)
2. [ATS Scoring Engine — `apps/analyzer/services/scoring_engine.py`](#2-ats-scoring-engine)
3. [LLM Service — `apps/resumes/services/llm_service.py`](#3-llm-service)
4. [Resume Optimiser — `apps/resumes/services/resume_optimizer.py`](#4-resume-optimiser)
5. [Version Service — `apps/resumes/services/version_service.py`](#5-version-service)
6. [Beat the ATS — `apps/analyzer/services/beat_the_ats.py`](#6-beat-the-ats)
7. [REST API Views — `apps/api/views.py`](#7-rest-api-views)
8. [Job Tracker Views — `apps/tracker/views.py`](#8-job-tracker-views)
9. [Authentication Views — `apps/authentication/views.py`](#9-authentication-views)
10. [Analytics Service — `apps/analytics/services/analytics_service.py`](#10-analytics-service)

---

## 1. Data Models

**File:** `apps/resumes/models.py`

**Purpose:** Defines the entire relational schema for the resume domain. Contains `Resume` (the root entity), `PersonalInfo` (1:1), `Experience`, `Education`, `Skill`, `Project`, `Certification` (all 1:M), plus `ResumeVersion` (JSON snapshots for version control), `ResumeAnalysis` (ATS score results), `OptimizationHistory` (AI optimisation records), and `UploadedResume` (PDF upload tracking). All models use Django ORM with explicit indexes, validators, and `clean()` methods for business-rule validation.

```python
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator, EmailValidator


class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=200)
    template = models.CharField(max_length=50, default='professional')
    summary = models.TextField(blank=True, default='')
    is_draft = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    current_version_number = models.IntegerField(default=1)
    last_analyzed_at = models.DateTimeField(null=True, blank=True)
    last_optimized_at = models.DateTimeField(null=True, blank=True)
    latest_ats_score = models.FloatField(null=True, blank=True)
    completeness_score = models.IntegerField(default=0)
    share_token = models.CharField(max_length=64, blank=True, db_index=True)
    color_scheme = models.CharField(max_length=50, default='professional_blue')
    font_family = models.CharField(max_length=50, default='Arial')

    class Meta:
        indexes = [models.Index(fields=['user', '-updated_at'])]
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class PersonalInfo(models.Model):
    resume = models.OneToOneField(Resume, on_delete=models.CASCADE, related_name='personal_info')
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(validators=[EmailValidator()])
    linkedin = models.URLField(blank=True, null=True, validators=[URLValidator()])
    github = models.URLField(blank=True, null=True, validators=[URLValidator()])
    location = models.CharField(max_length=200, blank=True)


class Experience(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='experiences')
    company = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True, default='')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, default='')
    achievements = models.TextField(blank=True, default='')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', '-start_date']
        indexes = [
            models.Index(fields=['resume', 'order']),
            models.Index(fields=['resume', '-start_date']),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.end_date and self.start_date > self.end_date:
            raise ValidationError('Start date must be before end date.')


class Education(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    field = models.CharField(max_length=200, blank=True, null=True, default='')
    start_year = models.IntegerField()
    end_year = models.IntegerField(null=True, blank=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    honors = models.CharField(max_length=500, blank=True, default='')
    relevant_coursework = models.TextField(blank=True, default='')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', '-end_year']

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.end_year and self.start_year > self.end_year:
            raise ValidationError('Start year must be before end year.')
        if self.gpa and (self.gpa < 0 or self.gpa > 4.0):
            raise ValidationError('GPA must be between 0.0 and 4.0')


class Skill(models.Model):
    PROFICIENCY_LEVELS = [
        ('beginner', 'Beginner'), ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'), ('expert', 'Expert'),
    ]
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    proficiency_level = models.CharField(max_length=20, choices=PROFICIENCY_LEVELS, default='intermediate')
    years_of_experience = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = [['resume', 'name']]
        indexes = [models.Index(fields=['resume', 'category'])]


class Project(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    technologies = models.CharField(max_length=500, blank=True, default='')
    impact = models.TextField(blank=True, default='')
    url = models.URLField(blank=True, validators=[URLValidator()])
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']


class ResumeVersion(models.Model):
    MODIFICATION_TYPES = [
        ('manual', 'Manual Edit'),
        ('optimized', 'AI Optimized'),
        ('restored', 'Restored from History'),
    ]
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    modification_type = models.CharField(max_length=20, choices=MODIFICATION_TYPES, default='manual')
    ats_score = models.FloatField(null=True, blank=True)
    snapshot_data = models.JSONField()
    user_notes = models.TextField(blank=True)

    class Meta:
        unique_together = [['resume', 'version_number']]
        ordering = ['-version_number']


class ResumeAnalysis(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='analyses')
    job_description = models.TextField()
    analysis_timestamp = models.DateTimeField(auto_now_add=True)
    keyword_match_score = models.FloatField()
    skill_relevance_score = models.FloatField()
    section_completeness_score = models.FloatField()
    experience_impact_score = models.FloatField()
    quantification_score = models.FloatField()
    action_verb_score = models.FloatField()
    final_score = models.FloatField()
    matched_keywords = models.JSONField(default=list)
    missing_keywords = models.JSONField(default=list)
    weak_action_verbs = models.JSONField(default=list)
    missing_quantifications = models.JSONField(default=list)
    suggestions = models.JSONField(default=list)

    class Meta:
        indexes = [models.Index(fields=['resume', '-analysis_timestamp'])]
        ordering = ['-analysis_timestamp']


class OptimizationHistory(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='optimizations')
    original_version = models.ForeignKey(
        ResumeVersion, on_delete=models.SET_NULL, null=True,
        related_name='optimizations_as_original'
    )
    optimized_version = models.ForeignKey(
        ResumeVersion, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='optimizations_as_optimized'
    )
    job_description = models.TextField()
    optimization_timestamp = models.DateTimeField(auto_now_add=True)
    original_score = models.FloatField()
    optimized_score = models.FloatField(null=True, blank=True)
    improvement_delta = models.FloatField(null=True, blank=True)
    changes_summary = models.JSONField(default=dict)
    detailed_changes = models.JSONField(default=list)
    accepted_changes = models.JSONField(default=list)
    rejected_changes = models.JSONField(default=list)
    user_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-optimization_timestamp']
```

---

## 2. ATS Scoring Engine

**File:** `apps/analyzer/services/scoring_engine.py`

**Purpose:** The core analytical engine. Calculates a weighted composite ATS score across six factors: keyword match (30%), skill relevance (20%), section completeness (15%), experience impact (15%), quantification (10%), and action verb quality (10%). Each factor is computed by a dedicated static method. Uses `KeywordExtractorService`, `ActionVerbAnalyzerService`, and `QuantificationDetectorService` internally.

```python
from typing import Dict, Set
from .keyword_extractor import KeywordExtractorService
from .action_verb_analyzer import ActionVerbAnalyzerService
from .quantification_detector import QuantificationDetectorService


class ScoringEngineService:
    """
    Comprehensive ATS scoring engine — evaluates resumes across six
    weighted dimensions and returns a composite score (0-100).
    """

    WEIGHTS = {
        'keyword_match':        0.30,
        'skill_relevance':      0.20,
        'section_completeness': 0.15,
        'experience_impact':    0.15,
        'quantification':       0.10,
        'action_verb':          0.10,
    }

    @staticmethod
    def calculate_ats_score(resume, job_description: str) -> Dict:
        """Run the full six-factor pipeline and return all scores + details."""
        from django.db.models import prefetch_related_objects
        prefetch_related_objects(
            [resume], 'experiences', 'education', 'skills', 'projects', 'personal_info'
        )

        resume_text = ScoringEngineService._get_resume_text(resume)

        keyword_score     = ScoringEngineService.calculate_keyword_match_score(resume_text, job_description)
        skill_score       = ScoringEngineService.calculate_skill_relevance_score(resume, job_description)
        completeness_score= ScoringEngineService.calculate_section_completeness_score(resume)
        impact_score      = ScoringEngineService.calculate_experience_impact_score(resume)
        quant_score       = ScoringEngineService.calculate_quantification_score(resume)
        verb_score        = ScoringEngineService.calculate_action_verb_score(resume)

        final_score = (
            keyword_score      * ScoringEngineService.WEIGHTS['keyword_match']        +
            skill_score        * ScoringEngineService.WEIGHTS['skill_relevance']      +
            completeness_score * ScoringEngineService.WEIGHTS['section_completeness'] +
            impact_score       * ScoringEngineService.WEIGHTS['experience_impact']    +
            quant_score        * ScoringEngineService.WEIGHTS['quantification']       +
            verb_score         * ScoringEngineService.WEIGHTS['action_verb']
        )

        resume_keywords = KeywordExtractorService.extract_keywords(resume_text)
        jd_keywords     = KeywordExtractorService.extract_keywords(job_description)
        matched_keywords  = list(resume_keywords & jd_keywords)
        missing_keywords  = list(jd_keywords - resume_keywords)

        experience_text = ScoringEngineService._get_experience_text(resume)
        verb_analysis   = ActionVerbAnalyzerService.analyze_action_verbs(experience_text)
        missing_quants  = ScoringEngineService._identify_missing_quantifications(resume)

        return {
            'final_score':                round(final_score, 2),
            'keyword_match_score':        round(keyword_score, 2),
            'skill_relevance_score':      round(skill_score, 2),
            'section_completeness_score': round(completeness_score, 2),
            'experience_impact_score':    round(impact_score, 2),
            'quantification_score':       round(quant_score, 2),
            'action_verb_score':          round(verb_score, 2),
            'matched_keywords':           matched_keywords[:20],
            'missing_keywords':           missing_keywords[:20],
            'weak_action_verbs':          verb_analysis['weak_verbs'],
            'missing_quantifications':    missing_quants,
        }

    @staticmethod
    def calculate_keyword_match_score(resume_text: str, job_description: str) -> float:
        if not resume_text or not job_description:
            return 0.0
        resume_kw = KeywordExtractorService.extract_keywords(resume_text)
        jd_kw     = KeywordExtractorService.extract_keywords(job_description)
        if not jd_kw:
            return 50.0
        return min(len(resume_kw & jd_kw) / len(jd_kw) * 100, 100.0)

    @staticmethod
    def calculate_skill_relevance_score(resume, job_description: str) -> float:
        if not job_description:
            return 50.0
        skills = resume.skills.all()
        if not skills:
            return 20.0
        skill_text   = ' '.join(s.name.lower() for s in skills)
        jd_kw        = KeywordExtractorService.extract_keywords(job_description)
        skill_kw     = KeywordExtractorService.extract_keywords(skill_text)
        if not jd_kw:
            return 50.0
        match_ratio  = len(skill_kw & jd_kw) / len(jd_kw)
        base_score   = match_ratio * 80
        skill_bonus  = min(len(skills) * 2, 20)
        return min(base_score + skill_bonus, 100.0)

    @staticmethod
    def calculate_section_completeness_score(resume) -> float:
        score = 0.0
        try:
            pi = resume.personal_info
            if pi.full_name: score += 8
            if pi.email:     score += 8
            if pi.phone:     score += 5
            if pi.location:  score += 4
        except Exception:
            pass
        if resume.experiences.exists():
            score += 15 + min(resume.experiences.count(), 3) * 5
        if resume.education.exists():
            score += 10 + min(resume.education.count(), 2) * 5
        if resume.skills.exists():
            score += 10 + min(resume.skills.count(), 5)
        if resume.projects.exists():
            score += 5 + min(resume.projects.count(), 2) * 2.5
        return min(score, 100.0)

    @staticmethod
    def calculate_experience_impact_score(resume) -> float:
        if not resume.experiences.exists():
            return 0.0
        total = 0.0
        for exp in resume.experiences.all():
            s = 0.0
            if exp.description and exp.description.strip():
                s += 40
                length = len(exp.description)
                if length > 500:   s += 20
                elif length > 200: s += 15
                elif length > 100: s += 10
                elif length > 50:  s += 5
                bullets = exp.description.count('*') + exp.description.count('-') + exp.description.count('*')
                if bullets >= 3:   s += 20
                elif bullets >= 2: s += 15
                elif bullets >= 1: s += 10
                if QuantificationDetectorService.has_quantification(exp.description):
                    s += min(len(QuantificationDetectorService.detect_quantifications(exp.description)) * 5, 20)
            total += s
        return min(total / resume.experiences.count(), 100.0)

    @staticmethod
    def calculate_quantification_score(resume) -> float:
        text = ScoringEngineService._get_experience_text(resume)
        if not text:
            return 0.0
        return QuantificationDetectorService.calculate_quantification_score(text)

    @staticmethod
    def calculate_action_verb_score(resume) -> float:
        text = ScoringEngineService._get_experience_text(resume)
        if not text:
            return 0.0
        return ActionVerbAnalyzerService.calculate_action_verb_score(text)

    @staticmethod
    def _get_resume_text(resume) -> str:
        parts = []
        try:
            pi = resume.personal_info
            if pi: parts.extend([pi.full_name, pi.location])
        except Exception:
            pass
        for exp in resume.experiences.all():
            parts.extend([exp.company, exp.role, exp.description])
        for edu in resume.education.all():
            parts.extend([edu.institution, edu.degree, edu.field])
        for skill in resume.skills.all():
            parts.append(skill.name)
        for proj in resume.projects.all():
            parts.extend([proj.name, proj.description, proj.technologies])
        return ' '.join(str(p) for p in parts if p)

    @staticmethod
    def _get_experience_text(resume) -> str:
        return ' '.join(e.description for e in resume.experiences.all() if e.description)

    @staticmethod
    def _identify_missing_quantifications(resume) -> list:
        missing = []
        for exp in resume.experiences.all():
            if not exp.description:
                continue
            for i, line in enumerate(exp.description.split('\n')):
                line = line.strip()
                if line and len(line) > 20 and not QuantificationDetectorService.has_quantification(line):
                    missing.append({
                        'company': exp.company, 'role': exp.role,
                        'line_number': i + 1, 'text': line[:100],
                    })
        return missing[:10]
```

---

## 3. LLM Service

**File:** `apps/resumes/services/llm_service.py`

**Purpose:** Central gateway for all OpenAI GPT-4o-mini calls. Every method has a graceful rule-based fallback so the application works fully without an API key. Implements a singleton client pattern to avoid re-initialising the OpenAI SDK on every request. Covers bullet rewriting, cover letter generation, professional summary, interview questions, rejection analysis, skill gap analysis, and ATS score explanation.

```python
import logging, json
from typing import Optional
from django.conf import settings

logger = logging.getLogger(__name__)
_openai_client = None


def _get_client():
    """Singleton OpenAI client — created once per process."""
    global _openai_client
    if _openai_client is not None:
        return _openai_client
    if not settings.AI_ENABLED:
        return None
    try:
        from openai import OpenAI
        _openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        return _openai_client
    except Exception as e:
        logger.warning(f"Could not initialise OpenAI client: {e}")
        return None


def _chat(system: str, user: str, max_tokens: int = None, json_mode: bool = False) -> Optional[str]:
    """Send a chat completion. Returns response text or None on failure."""
    client = _get_client()
    if client is None:
        return None
    kwargs = {
        'model': settings.OPENAI_MODEL,
        'messages': [
            {'role': 'system', 'content': system},
            {'role': 'user',   'content': user},
        ],
        'max_tokens':  max_tokens or settings.OPENAI_MAX_TOKENS,
        'temperature': settings.OPENAI_TEMPERATURE,
    }
    if json_mode:
        kwargs['response_format'] = {'type': 'json_object'}
    try:
        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}")
        return None


class LLMService:
    """All AI features route through here. Every method falls back gracefully."""

    @staticmethod
    def rewrite_bullet(bullet: str, job_description: str = '', role: str = '') -> dict:
        """Rewrite a resume bullet point. Falls back to rule-based rewriter."""
        if not bullet or not bullet.strip():
            return {'original': bullet, 'rewritten': bullet,
                    'changed': False, 'reason': 'Empty bullet', 'ai_powered': False}

        system = (
            "You are an expert resume writer. Rewrite the given resume bullet point to be "
            "more impactful: start with a strong action verb, quantify achievements where "
            "possible, be concise (under 25 words), and use keywords from the job description "
            "if provided. Return ONLY the rewritten bullet — no explanation, no quotes."
        )
        context_hint = f"\nJob description context: {job_description[:500]}" if job_description else ""
        rewritten = _chat(system, f"Bullet to rewrite: {bullet}{context_hint}", max_tokens=100)

        if rewritten and rewritten != bullet:
            return {'original': bullet, 'rewritten': rewritten,
                    'changed': True, 'reason': 'AI-powered rewrite', 'ai_powered': True}

        from apps.resumes.services.bullet_point_rewriter import BulletPointRewriterService
        result = BulletPointRewriterService.rewrite_bullet_point(bullet, job_description)
        result['ai_powered'] = False
        return result

    @staticmethod
    def generate_cover_letter(resume, company: str, role: str, job_description: str) -> dict:
        """Generate a personalised cover letter. Falls back to template."""
        info   = getattr(resume, 'personal_info', None)
        name   = info.full_name if info else resume.user.get_full_name() or resume.user.username
        skills = list(resume.skills.values_list('name', flat=True)[:8])
        exps   = list(resume.experiences.order_by('-start_date').values(
            'role', 'company', 'description', 'achievements')[:3])

        system = (
            "You are an expert career coach writing a compelling, personalised cover letter. "
            "3-4 paragraphs, professional, specific to the role and company, "
            "highlight achievements with metrics, mirror JD keywords naturally."
        )
        user = (
            f"Write a cover letter for {name} applying to {role} at {company}.\n\n"
            f"Job Description:\n{job_description[:1000]}\n\n"
            f"Skills: {', '.join(skills)}\n\n"
            f"Experience:\n" +
            '\n'.join(f"- {e['role']} at {e['company']}: "
                      f"{(e['achievements'] or e['description'] or '')[:200]}" for e in exps)
        )
        content = _chat(system, user, max_tokens=600)
        if content:
            return {'content': content, 'ai_powered': True}

        from apps.tracker.cover_letter_service import CoverLetterService
        return {'content': CoverLetterService().generate(resume, company, role, job_description),
                'ai_powered': False}

    @staticmethod
    def generate_interview_questions(resume, role: str, job_description: str,
                                     company: str = '') -> dict:
        """Generate 12 tailored interview questions with talking points."""
        skills = list(resume.skills.values_list('name', flat=True)[:8])
        exps   = list(resume.experiences.order_by('-start_date').values(
            'role', 'company', 'achievements', 'description')[:3])

        system = (
            "Generate 12 tailored interview questions (behavioral, technical, situational, "
            "motivational). For each provide talking_points and resume_evidence. "
            'Return JSON: {"questions": [{"question": str, "category": str, '
            '"talking_points": [str], "resume_evidence": str}]}'
        )
        exp_text = '\n'.join(
            f"- {e['role']} at {e['company']}: "
            f"{(e['achievements'] or e['description'] or '')[:200]}" for e in exps)
        user = (
            f"Role: {role} at {company or 'the company'}\n\n"
            f"Job Description:\n{job_description[:800]}\n\n"
            f"Skills: {', '.join(skills)}\n\nExperience:\n{exp_text}"
        )
        raw = _chat(system, user, max_tokens=1200, json_mode=True)
        if raw:
            try:
                data = json.loads(raw)
                if data.get('questions'):
                    return {'questions': data['questions'], 'ai_powered': True}
            except (json.JSONDecodeError, KeyError):
                pass

        from apps.tracker.interview_prep_service import InterviewPrepService
        return {'questions': InterviewPrepService().generate(resume, role, job_description, company),
                'ai_powered': False}

    @staticmethod
    def analyse_rejection(resume, job_description: str, company: str, role: str) -> dict:
        """AI-powered rejection analysis with rule-based fallback."""
        from apps.analyzer.services.scoring_engine import ScoringEngineService
        score_data = ScoringEngineService.calculate_ats_score(resume, job_description)

        system = (
            "Analyse why a resume may have been rejected. Be direct and actionable. "
            'Return JSON: {"analysis": str, "top_issues": [str], "quick_fixes": [str]}'
        )
        user = (
            f"Role: {role} at {company}\n"
            f"ATS Score: {score_data['final_score']:.0f}/100\n"
            f"Keyword Match: {score_data['keyword_match_score']:.0f}/100\n"
            f"Missing Keywords: {', '.join(score_data['missing_keywords'][:15])}\n"
            f"Job Description:\n{job_description[:800]}"
        )
        raw = _chat(system, user, max_tokens=600, json_mode=True)
        if raw:
            try:
                data = json.loads(raw)
                return {**data, 'score_data': score_data, 'ai_powered': True}
            except (json.JSONDecodeError, KeyError):
                pass

        # Rule-based fallback
        issues, fixes = [], []
        if score_data['keyword_match_score'] < 50:
            issues.append(f"Low keyword match ({score_data['keyword_match_score']:.0f}%)")
            fixes.append(f"Add: {', '.join(score_data['missing_keywords'][:8])}")
        if score_data['quantification_score'] < 40:
            issues.append("Few quantified achievements")
            fixes.append("Add metrics to at least 3 bullet points")
        if score_data['action_verb_score'] < 50:
            issues.append("Weak action verbs")
            fixes.append("Replace with: led, built, delivered, drove, achieved")
        return {
            'analysis': f"Score: {score_data['final_score']:.0f}/100",
            'top_issues': issues, 'quick_fixes': fixes,
            'score_data': score_data, 'ai_powered': False,
        }

    @staticmethod
    def explain_ats_score(score_data: dict, resume_title: str = '') -> str:
        """Plain-English explanation of an ATS score."""
        system = (
            "Explain this ATS score in plain English. Under 100 words. "
            "Be specific about what is working and what needs improvement."
        )
        user = (
            f"Resume: {resume_title}\n"
            f"Overall: {score_data.get('final_score', 0):.0f}/100\n"
            f"Keyword Match: {score_data.get('keyword_match_score', 0):.0f}/100\n"
            f"Skills: {score_data.get('skill_relevance_score', 0):.0f}/100\n"
            f"Completeness: {score_data.get('section_completeness_score', 0):.0f}/100\n"
            f"Experience Impact: {score_data.get('experience_impact_score', 0):.0f}/100\n"
            f"Quantification: {score_data.get('quantification_score', 0):.0f}/100\n"
            f"Action Verbs: {score_data.get('action_verb_score', 0):.0f}/100"
        )
        result = _chat(system, user, max_tokens=150)
        if result:
            return result
        score = score_data.get('final_score', 0)
        if score >= 80:
            return f"Strong resume scoring {score:.0f}/100. Well-optimised for ATS systems."
        elif score >= 60:
            return f"Good resume scoring {score:.0f}/100. Adding missing keywords will push it higher."
        return f"Resume scores {score:.0f}/100. Focus on keyword matching and quantified achievements."
```

---

## 4. Resume Optimiser

**File:** `apps/resumes/services/resume_optimizer.py`

**Purpose:** Orchestrates the full AI optimisation pipeline. Calls four sub-services in sequence — bullet point rewriting, keyword injection, quantification suggestion, and formatting standardisation — then estimates the projected score improvement and returns a structured result with every proposed change tracked individually so the user can accept or reject each one.

```python
from typing import Dict, List
from .bullet_point_rewriter import BulletPointRewriterService
from .keyword_injector import KeywordInjectorService
from .quantification_suggester import QuantificationSuggesterService
from .formatting_standardizer import FormattingStandardizerService
from apps.analyzer.services.keyword_extractor import KeywordExtractorService
from apps.analyzer.services.scoring_engine import ScoringEngineService


class ResumeOptimizerService:
    """Orchestrates all optimisation sub-services into a single pipeline."""

    @staticmethod
    def optimize_resume(resume, job_description: str, options: Dict = None) -> Dict:
        """
        Run the full optimisation pipeline.

        Returns:
            original_score, optimized_score, improvement_delta,
            detailed_changes, changes_summary, optimized_data
        """
        if options is None:
            options = {}

        rewrite_bullets        = options.get('rewrite_bullets', True)
        inject_keywords        = options.get('inject_keywords', True)
        suggest_quantifications= options.get('suggest_quantifications', True)
        standardize_formatting = options.get('standardize_formatting', True)
        max_keywords           = options.get('max_keywords', 10)

        original_analysis = ScoringEngineService.calculate_ats_score(resume, job_description)
        original_score    = original_analysis['final_score']

        detailed_changes = []
        changes_summary  = {
            'bullet_rewrites': 0, 'keyword_injections': 0,
            'quantification_suggestions': 0, 'formatting_fixes': 0, 'total_changes': 0,
        }

        if rewrite_bullets:
            bullet_changes = ResumeOptimizerService._optimize_bullet_points(resume, job_description)
            detailed_changes.extend(bullet_changes)
            changes_summary['bullet_rewrites'] = len(bullet_changes)

        if inject_keywords:
            resume_text      = ResumeOptimizerService._get_resume_text(resume)
            resume_kw        = KeywordExtractorService.extract_keywords(resume_text)
            jd_kw            = KeywordExtractorService.extract_keywords(job_description)
            missing_keywords = jd_kw - resume_kw
            keyword_changes  = KeywordInjectorService.inject_keywords(
                resume, missing_keywords, job_description, max_keywords)
            detailed_changes.extend(keyword_changes)
            changes_summary['keyword_injections'] = len(keyword_changes)

        if suggest_quantifications:
            quant_changes = ResumeOptimizerService._suggest_quantifications(resume)
            detailed_changes.extend(quant_changes)
            changes_summary['quantification_suggestions'] = len(quant_changes)

        if standardize_formatting:
            format_changes = ResumeOptimizerService._standardize_formatting(resume)
            detailed_changes.extend(format_changes)
            changes_summary['formatting_fixes'] = len(format_changes)

        changes_summary['total_changes'] = sum([
            changes_summary['bullet_rewrites'],
            changes_summary['keyword_injections'],
            changes_summary['quantification_suggestions'],
            changes_summary['formatting_fixes'],
        ])

        optimized_data  = ResumeOptimizerService._generate_optimized_data(resume, detailed_changes)
        optimized_score = ResumeOptimizerService._estimate_optimized_score(
            original_score, changes_summary, original_analysis)

        return {
            'original_score':   round(original_score, 2),
            'optimized_score':  round(optimized_score, 2),
            'improvement_delta':round(optimized_score - original_score, 2),
            'detailed_changes': detailed_changes,
            'changes_summary':  changes_summary,
            'optimized_data':   optimized_data,
            'original_analysis':original_analysis,
        }

    @staticmethod
    def _optimize_bullet_points(resume, job_description: str) -> List[Dict]:
        changes = []
        for exp in resume.experiences.all():
            if not exp.description:
                continue
            bullets = [l.strip() for l in exp.description.split('\n') if l.strip()]
            for i, bullet in enumerate(bullets):
                result = BulletPointRewriterService.rewrite_bullet_point(bullet, job_description)
                if result['changed']:
                    changes.append({
                        'type': 'bullet_rewrite', 'section': 'experience',
                        'company': exp.company, 'role': exp.role,
                        'bullet_index': i, 'old_text': result['original'],
                        'new_text': result['rewritten'], 'reason': result['reason'],
                    })
        return changes

    @staticmethod
    def _suggest_quantifications(resume) -> List[Dict]:
        changes = []
        for exp in resume.experiences.all():
            if not exp.description:
                continue
            analysis = QuantificationSuggesterService.analyze_experience_quantification(
                exp.description)
            for suggestion in analysis['suggestions']:
                changes.append({
                    'type': 'quantification_suggestion', 'section': 'experience',
                    'company': exp.company, 'role': exp.role,
                    'old_text': suggestion['original'],
                    'suggested_text': suggestion['example'],
                    'achievement_type': suggestion['achievement_type'],
                    'metric_options': suggestion['suggestions'],
                })
        return changes

    @staticmethod
    def _standardize_formatting(resume) -> List[Dict]:
        changes = []
        for exp in resume.experiences.all():
            if exp.description:
                result = FormattingStandardizerService.standardize_all(exp.description)
                if result['all_changes']:
                    changes.append({
                        'type': 'formatting_standardization', 'section': 'experience',
                        'company': exp.company, 'role': exp.role, 'field': 'description',
                        'old_text': result['original'], 'new_text': result['standardized'],
                        'specific_changes': result['all_changes'],
                    })
        return changes

    @staticmethod
    def _estimate_optimized_score(original_score: float, changes_summary: Dict,
                                   original_analysis: Dict) -> float:
        score = original_score
        if changes_summary['bullet_rewrites'] > 0:
            score += min(changes_summary['bullet_rewrites'] * 3, 15) * 0.10
        if changes_summary['keyword_injections'] > 0:
            score += min(changes_summary['keyword_injections'] * 3, 30) * 0.30
        if changes_summary['quantification_suggestions'] > 0:
            score += min(changes_summary['quantification_suggestions'] * 2, 20) * 0.10
        if changes_summary['formatting_fixes'] > 0:
            score += 2
        return min(score, 100.0)

    @staticmethod
    def _get_resume_text(resume) -> str:
        parts = []
        try:
            pi = resume.personal_info
            if pi: parts.extend([pi.full_name, pi.location])
        except Exception:
            pass
        for exp in resume.experiences.all():
            parts.extend([exp.company, exp.role, exp.description])
        for edu in resume.education.all():
            parts.extend([edu.institution, edu.degree, edu.field])
        for skill in resume.skills.all():
            parts.append(skill.name)
        for proj in resume.projects.all():
            parts.extend([proj.name, proj.description, proj.technologies])
        return ' '.join(str(p) for p in parts if p)
```

---

## 5. Version Service

**File:** `apps/resumes/services/version_service.py`

**Purpose:** Manages the full version control lifecycle for resumes. Creates atomic JSON snapshots of the entire resume state (all related objects), compares any two versions field-by-field to produce a structured diff, and restores a resume to any historical version non-destructively by creating a new version record.

```python
from typing import Dict, List, Optional
from django.db import transaction
from django.db.models import Max
from apps.resumes.models import Resume, ResumeVersion


class VersionService:

    @staticmethod
    def create_version(resume: Resume, modification_type: str = 'manual',
                       user_notes: str = '', ats_score: Optional[float] = None) -> ResumeVersion:
        """Create a new version snapshot atomically."""
        with transaction.atomic():
            max_ver = ResumeVersion.objects.filter(resume=resume).aggregate(
                max_ver=Max('version_number'))['max_ver']
            next_version = (max_ver or 0) + 1

            version = ResumeVersion.objects.create(
                resume=resume,
                version_number=next_version,
                modification_type=modification_type,
                ats_score=ats_score,
                snapshot_data=VersionService._create_snapshot(resume),
                user_notes=user_notes,
            )
            resume.current_version_number = next_version
            resume.save(update_fields=['current_version_number'])
            return version

    @staticmethod
    def _create_snapshot(resume: Resume) -> Dict:
        """Serialise the entire resume and all related objects to a JSON-safe dict."""
        snapshot = {
            'resume_id': resume.id,
            'title':     resume.title,
            'template':  resume.template,
            'created_at':resume.created_at.isoformat(),
            'updated_at':resume.updated_at.isoformat(),
        }
        if hasattr(resume, 'personal_info'):
            pi = resume.personal_info
            snapshot['personal_info'] = {
                'full_name': pi.full_name, 'phone': pi.phone,
                'email': pi.email, 'linkedin': pi.linkedin,
                'github': pi.github, 'location': pi.location,
            }
        snapshot['experiences'] = [
            {'company': e.company, 'role': e.role,
             'start_date': e.start_date.isoformat(),
             'end_date': e.end_date.isoformat() if e.end_date else None,
             'description': e.description, 'order': e.order}
            for e in resume.experiences.all()
        ]
        snapshot['education'] = [
            {'institution': ed.institution, 'degree': ed.degree,
             'field': ed.field, 'start_year': ed.start_year,
             'end_year': ed.end_year, 'order': ed.order}
            for ed in resume.education.all()
        ]
        snapshot['skills'] = [
            {'name': s.name, 'category': s.category}
            for s in resume.skills.all()
        ]
        snapshot['projects'] = [
            {'name': p.name, 'description': p.description,
             'technologies': p.technologies, 'url': p.url, 'order': p.order}
            for p in resume.projects.all()
        ]
        return snapshot

    @staticmethod
    def get_version_history(resume: Resume) -> List[ResumeVersion]:
        return list(ResumeVersion.objects.filter(resume=resume).order_by('-version_number'))

    @staticmethod
    def compare_versions(version1: ResumeVersion, version2: ResumeVersion) -> Dict:
        """Return a structured diff between two version snapshots."""
        s1, s2 = version1.snapshot_data, version2.snapshot_data
        diff = {
            'version1_number': version1.version_number,
            'version2_number': version2.version_number,
            'version1_date':   version1.created_at.isoformat(),
            'version2_date':   version2.created_at.isoformat(),
            'changes': [],
        }
        for field in ['title', 'template']:
            if s1.get(field) != s2.get(field):
                diff['changes'].append({
                    'section': 'resume', 'field': field, 'type': 'modified',
                    'old_value': s1.get(field), 'new_value': s2.get(field),
                })
        diff['changes'].extend(VersionService._compare_dict(
            s1.get('personal_info', {}), s2.get('personal_info', {}), 'personal_info'))
        for section, key in [('experiences','role'),('education','degree'),
                              ('skills','name'),('projects','name')]:
            diff['changes'].extend(VersionService._compare_list(
                s1.get(section, []), s2.get(section, []), section, key))
        return diff

    @staticmethod
    def _compare_dict(dict1: Dict, dict2: Dict, section: str) -> List[Dict]:
        changes = []
        for key in set(dict1) | set(dict2):
            v1, v2 = dict1.get(key), dict2.get(key)
            if v1 != v2:
                change_type = 'added' if key not in dict1 else 'deleted' if key not in dict2 else 'modified'
                changes.append({'section': section, 'field': key, 'type': change_type,
                                 'old_value': v1, 'new_value': v2})
        return changes

    @staticmethod
    def _compare_list(list1: List[Dict], list2: List[Dict],
                      section: str, key_field: str) -> List[Dict]:
        changes = []
        d1 = {item.get(key_field): item for item in list1}
        d2 = {item.get(key_field): item for item in list2}
        for key in set(d1) | set(d2):
            item1, item2 = d1.get(key), d2.get(key)
            if item1 is None:
                changes.append({'section': section, 'item': key, 'type': 'added',
                                 'old_value': None, 'new_value': item2})
            elif item2 is None:
                changes.append({'section': section, 'item': key, 'type': 'deleted',
                                 'old_value': item1, 'new_value': None})
            elif item1 != item2:
                field_changes = [
                    {'field': f, 'old': item1.get(f), 'new': item2.get(f)}
                    for f in set(item1) | set(item2) if item1.get(f) != item2.get(f)
                ]
                if field_changes:
                    changes.append({'section': section, 'item': key,
                                    'type': 'modified', 'field_changes': field_changes})
        return changes

    @staticmethod
    def restore_version(version: ResumeVersion) -> Resume:
        """Non-destructively restore a resume to a historical version."""
        with transaction.atomic():
            resume   = version.resume
            snapshot = version.snapshot_data
            resume.title    = snapshot.get('title', resume.title)
            resume.template = snapshot.get('template', resume.template)
            resume.save()
            if 'personal_info' in snapshot and hasattr(resume, 'personal_info'):
                pi_data = snapshot['personal_info']
                pi = resume.personal_info
                for field in ['full_name', 'phone', 'email', 'linkedin', 'github', 'location']:
                    setattr(pi, field, pi_data.get(field, getattr(pi, field)))
                pi.save()
            VersionService.create_version(
                resume=resume, modification_type='restored',
                user_notes=f'Restored from version {version.version_number}',
                ats_score=version.ats_score,
            )
            return resume
```

---

## 6. Beat the ATS

**File:** `apps/analyzer/services/beat_the_ats.py`

**Purpose:** Gamified keyword battle plan. Given a resume and job description, calculates the current score, identifies the next score threshold (Poor/Fair/Good/Strong/Excellent), and returns the exact minimum set of keywords the user needs to add — ranked by impact — to cross that threshold. Also provides a live score simulation endpoint used by the frontend checkbox UI.

```python
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

THRESHOLDS = [
    (40,  'Poor',      'Most ATS systems will auto-reject below 40.'),
    (60,  'Fair',      'Recruiters may see your resume but it needs work.'),
    (75,  'Good',      'You will pass most ATS filters.'),
    (85,  'Strong',    'You are competitive for this role.'),
    (95,  'Excellent', 'Top-tier ATS score — you stand out.'),
    (101, 'Perfect',   'Maximum score achieved.'),
]


def get_next_threshold(current_score: float):
    for score, label, message in THRESHOLDS:
        if current_score < score:
            return score, label, message
    return 101, 'Perfect', 'Maximum score achieved.'


class BeatTheATSService:

    @staticmethod
    def get_battle_plan(resume, job_description: str) -> Dict:
        """
        Return the minimum keywords needed to cross the next score threshold.
        """
        from apps.analyzer.services.scoring_engine import ScoringEngineService
        from apps.analyzer.services.keyword_extractor import KeywordExtractorService

        score_data    = ScoringEngineService.calculate_ats_score(resume, job_description)
        current_score = score_data['final_score']

        next_threshold, next_label, next_message = get_next_threshold(current_score)

        if current_score >= 95:
            return {
                'current_score': current_score, 'next_threshold': 100,
                'next_label': 'Perfect', 'next_message': 'Maximum score achieved.',
                'points_needed': 0, 'keywords_to_add': [], 'already_winning': True,
            }

        points_needed    = next_threshold - current_score
        missing_keywords = score_data.get('missing_keywords', [])

        jd_keywords      = KeywordExtractorService.extract_keywords(job_description)
        total_jd_kw      = max(len(jd_keywords), 1)
        # Each keyword added improves keyword_match_score proportionally.
        # keyword_match weight = 0.30, so each keyword is worth:
        # (1 / total_jd_keywords) * 100 * 0.30 points
        points_per_kw    = (1 / total_jd_kw) * 100 * 0.30

        existing_skills  = set(s.lower() for s in resume.skills.values_list('name', flat=True))
        exp_text         = ScoringEngineService._get_experience_text(resume).lower()

        keywords_to_add  = []
        cumulative       = 0.0

        for kw in missing_keywords:
            if cumulative >= points_needed * 1.2:
                break
            if len(kw.split()) == 1 and kw.lower() not in existing_skills:
                section = 'Skills'
                reason  = f'Add "{kw}" to your Skills section for immediate keyword match.'
            else:
                section = 'Experience'
                reason  = f'Weave "{kw}" into a bullet point in your most recent role.'
            keywords_to_add.append({
                'keyword': kw, 'impact_points': round(points_per_kw, 1),
                'section': section, 'reason': reason,
            })
            cumulative += points_per_kw

        needed_count = 0
        running      = 0.0
        for kw_data in keywords_to_add:
            running      += kw_data['impact_points']
            needed_count += 1
            if running >= points_needed:
                break

        return {
            'current_score':        round(current_score, 1),
            'next_threshold':       next_threshold,
            'next_label':           next_label,
            'next_message':         next_message,
            'points_needed':        round(points_needed, 1),
            'keywords_needed_count':needed_count,
            'keywords_to_add':      keywords_to_add[:10],
            'already_winning':      False,
            'score_data':           score_data,
        }

    @staticmethod
    def simulate_score_after_keywords(resume, job_description: str,
                                       added_keywords: List[str]) -> float:
        """
        Simulate the ATS score if the user added the given keywords.
        Used for live score preview as users tick checkboxes.
        """
        from apps.analyzer.services.keyword_extractor import KeywordExtractorService
        from apps.analyzer.services.scoring_engine import ScoringEngineService

        resume_text    = ScoringEngineService._get_resume_text(resume)
        augmented_text = resume_text + ' ' + ' '.join(added_keywords)

        resume_kw      = KeywordExtractorService.extract_keywords(augmented_text)
        jd_kw          = KeywordExtractorService.extract_keywords(job_description)
        if not jd_kw:
            return 0.0

        keyword_score  = min(len(resume_kw & jd_kw) / len(jd_kw) * 100, 100)
        score_data     = ScoringEngineService.calculate_ats_score(resume, job_description)
        weights        = ScoringEngineService.WEIGHTS

        simulated = (
            keyword_score                          * weights['keyword_match']        +
            score_data['skill_relevance_score']    * weights['skill_relevance']      +
            score_data['section_completeness_score']* weights['section_completeness']+
            score_data['experience_impact_score']  * weights['experience_impact']    +
            score_data['quantification_score']     * weights['quantification']       +
            score_data['action_verb_score']        * weights['action_verb']
        )
        return round(min(simulated, 100), 1)
```

---

## 7. REST API Views

**File:** `apps/api/views.py`

**Purpose:** DRF ViewSets and function-based API views exposing all major features over HTTP with JWT authentication. `ResumeViewSet` provides full CRUD plus custom actions for ATS analysis, AI optimisation, ATS simulation, and rejection analysis. `JobApplicationViewSet` provides CRUD plus cover letter and interview prep generation. A custom `AIFeatureThrottle` limits AI endpoints to 20 calls/hour per user.

```python
import logging
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle

from apps.resumes.models import Resume, ResumeAnalysis
from apps.tracker.models import JobApplication, CoverLetter, InterviewPrepSession
from .serializers import (
    ResumeListSerializer, ResumeDetailSerializer, ResumeCreateSerializer,
    ResumeAnalysisSerializer, ResumeVersionSerializer,
    JobApplicationSerializer, CoverLetterSerializer, InterviewPrepSerializer,
    UserSerializer,
)

logger = logging.getLogger(__name__)


class AIFeatureThrottle(UserRateThrottle):
    """20 AI calls per hour per user — prevents API key drain."""
    scope = 'ai_features'


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def me(request):
    """Get or update the current user profile."""
    if request.method == 'GET':
        return Response(UserSerializer(request.user).data)
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResumeViewSet(viewsets.ModelViewSet):
    """CRUD for resumes — all operations scoped to the authenticated user."""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user).prefetch_related(
            'personal_info', 'experiences', 'education', 'skills', 'projects', 'certifications'
        )

    def get_serializer_class(self):
        if self.action == 'list':   return ResumeListSerializer
        if self.action == 'create': return ResumeCreateSerializer
        return ResumeDetailSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='analyse',
            throttle_classes=[AIFeatureThrottle])
    def analyse(self, request, pk=None):
        """Trigger ATS analysis. Returns 202 + task_id if Celery is available."""
        resume = self.get_object()
        job_description = request.data.get('job_description', '').strip()
        if not job_description:
            return Response({'error': 'job_description is required'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            from apps.resumes.tasks import analyse_ats_task
            task = analyse_ats_task.delay(resume.id, job_description, request.user.id)
            return Response({'task_id': task.id, 'status': 'queued',
                             'message': 'Poll /api/v1/tasks/{task_id}/ for results.'},
                            status=status.HTTP_202_ACCEPTED)
        except Exception:
            # Synchronous fallback when Celery is unavailable
            from apps.analyzer.services.scoring_engine import ScoringEngineService
            from apps.resumes.services.llm_service import LLMService
            from django.utils import timezone

            score_data  = ScoringEngineService.calculate_ats_score(resume, job_description)
            explanation = LLMService.explain_ats_score(score_data, resume.title)

            analysis = ResumeAnalysis.objects.create(
                resume=resume, job_description=job_description,
                keyword_match_score=score_data['keyword_match_score'],
                skill_relevance_score=score_data['skill_relevance_score'],
                section_completeness_score=score_data['section_completeness_score'],
                experience_impact_score=score_data['experience_impact_score'],
                quantification_score=score_data['quantification_score'],
                action_verb_score=score_data['action_verb_score'],
                final_score=score_data['final_score'],
                matched_keywords=score_data['matched_keywords'],
                missing_keywords=score_data['missing_keywords'],
                weak_action_verbs=score_data['weak_action_verbs'],
                missing_quantifications=score_data['missing_quantifications'],
                suggestions=[explanation],
            )
            resume.latest_ats_score = score_data['final_score']
            resume.last_analyzed_at = timezone.now()
            resume.save(update_fields=['latest_ats_score', 'last_analyzed_at'])
            return Response(ResumeAnalysisSerializer(analysis).data,
                            status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='ats-simulate')
    def ats_simulate(self, request, pk=None):
        """Simulate Taleo, Workday, Greenhouse, Lever, iCIMS scoring."""
        resume = self.get_object()
        from apps.analyzer.services.ats_simulator import ATSSystemSimulator
        return Response(ATSSystemSimulator.simulate_all(
            resume, request.data.get('job_description', '')))

    @action(detail=True, methods=['post'], url_path='rejection-analysis',
            throttle_classes=[AIFeatureThrottle])
    def rejection_analysis(self, request, pk=None):
        """AI-powered analysis of why a resume may have been rejected."""
        resume = self.get_object()
        from apps.resumes.services.llm_service import LLMService
        return Response(LLMService.analyse_rejection(
            resume,
            request.data.get('job_description', ''),
            request.data.get('company', ''),
            request.data.get('role', ''),
        ))

    @action(detail=True, methods=['get'], url_path='versions')
    def versions(self, request, pk=None):
        resume = self.get_object()
        return Response(ResumeVersionSerializer(resume.versions.all(), many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_status(request, task_id: str):
    """Poll the status of a background Celery task."""
    try:
        from celery.result import AsyncResult
        result = AsyncResult(task_id)
        data = {'task_id': task_id, 'status': result.status, 'ready': result.ready()}
        if result.ready():
            data['result'] = (result.result if not isinstance(result.result, Exception)
                              else str(result.result))
        return Response(data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class JobApplicationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class   = JobApplicationSerializer

    def get_queryset(self):
        return JobApplication.objects.filter(user=self.request.user).select_related('resume')

    def perform_create(self, serializer):
        app = serializer.save(user=self.request.user)
        if app.resume:
            latest = app.resume.analyses.order_by('-analysis_timestamp').first()
            if latest:
                app.ats_score_at_apply = latest.final_score
                app.save(update_fields=['ats_score_at_apply'])

    @action(detail=True, methods=['post'], url_path='cover-letter',
            throttle_classes=[AIFeatureThrottle])
    def cover_letter(self, request, pk=None):
        app = self.get_object()
        if not app.resume:
            return Response({'error': 'Link a resume to this application first'},
                            status=status.HTTP_400_BAD_REQUEST)
        existing = getattr(app, 'cover_letter', None)
        if existing and not request.data.get('regenerate'):
            return Response(CoverLetterSerializer(existing).data)
        from apps.resumes.services.llm_service import LLMService
        result = LLMService.generate_cover_letter(
            app.resume, app.company, app.role, app.job_description)
        cl, _ = CoverLetter.objects.update_or_create(
            application=app,
            defaults={'user': request.user, 'resume': app.resume,
                      'company': app.company, 'role': app.role, 'content': result['content']},
        )
        data = CoverLetterSerializer(cl).data
        data['ai_powered'] = result['ai_powered']
        return Response(data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def outcome_analytics(request):
    from apps.tracker.outcome_analytics import OutcomeAnalyticsService
    return Response(OutcomeAnalyticsService().get_user_stats(request.user))
```

---

## 8. Job Tracker Views

**File:** `apps/tracker/views.py`

**Purpose:** Handles the full job application lifecycle — creating, editing, and deleting applications; generating AI cover letters and interview prep questions; running skill gap analysis; displaying salary intelligence; generating follow-up email templates; and analysing rejection patterns by correlating ATS scores with application outcomes.

```python
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from .models import JobApplication, CoverLetter, InterviewPrepSession, SkillGapAnalysis
from .forms import JobApplicationForm, ScrapeJobForm
from .job_scraper import scrape_job_description
from .outcome_analytics import OutcomeAnalyticsService
from .skill_gap_service import SkillGapService
from .salary_service import SalaryIntelligenceService
from apps.resumes.models import Resume


@login_required
def application_list(request):
    applications = JobApplication.objects.filter(user=request.user).select_related('resume')
    stats = OutcomeAnalyticsService().get_user_stats(request.user)
    return render(request, 'tracker/application_list.html',
                  {'applications': applications, 'stats': stats})


@login_required
def application_create(request):
    initial = {'resume': request.GET.get('resume_id'), 'job_url': request.GET.get('job_url', '')}
    form = JobApplicationForm(request.user, request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        app = form.save(commit=False)
        app.user = request.user
        # Snapshot the ATS score at time of application
        if app.resume:
            latest = app.resume.analyses.order_by('-analysis_timestamp').first()
            if latest:
                app.ats_score_at_apply = latest.final_score
        app.save()
        messages.success(request, f'Application to {app.company} saved.')
        return redirect('application_detail', pk=app.pk)
    return render(request, 'tracker/application_form.html', {'form': form, 'action': 'Add'})


@login_required
def generate_cover_letter(request, pk):
    app = get_object_or_404(JobApplication, pk=pk, user=request.user)
    if not app.resume:
        messages.error(request, 'Please link a resume to this application first.')
        return redirect('application_update', pk=pk)

    existing = getattr(app, 'cover_letter', None)
    if request.method == 'POST':
        from .forms import CoverLetterForm
        form = CoverLetterForm(request.POST, instance=existing)
        if form.is_valid():
            cl = form.save(commit=False)
            cl.user = request.user
            cl.application = app
            cl.resume = app.resume
            cl.company = app.company
            cl.role = app.role
            cl.save()
            messages.success(request, 'Cover letter saved.')
            return redirect('application_detail', pk=pk)
    else:
        if existing and not request.GET.get('regenerate'):
            from .forms import CoverLetterForm
            form = CoverLetterForm(instance=existing)
        else:
            from apps.resumes.services.llm_service import LLMService
            result = LLMService.generate_cover_letter(
                resume=app.resume, company=app.company,
                role=app.role, job_description=app.job_description)
            from .forms import CoverLetterForm
            form = CoverLetterForm(initial={'content': result['content']})
            if result['ai_powered']:
                messages.success(request, 'Cover letter generated with AI.')
            else:
                messages.info(request, 'Cover letter generated from template.')
    return render(request, 'tracker/cover_letter_form.html', {'form': form, 'application': app})


@login_required
def interview_prep(request, pk):
    app = get_object_or_404(JobApplication, pk=pk, user=request.user)
    existing = InterviewPrepSession.objects.filter(application=app).first()
    if request.method == 'POST' or not existing:
        if not app.resume:
            messages.error(request, 'Link a resume to this application first.')
            return redirect('application_update', pk=pk)
        from apps.resumes.services.llm_service import LLMService
        result = LLMService.generate_interview_questions(
            resume=app.resume, role=app.role,
            job_description=app.job_description, company=app.company)
        existing, _ = InterviewPrepSession.objects.update_or_create(
            application=app,
            defaults={
                'user': request.user, 'resume': app.resume,
                'role': app.role, 'company': app.company,
                'job_description': app.job_description,
                'questions': result['questions'],
            })
    return render(request, 'tracker/interview_prep.html', {
        'application': app, 'session': existing,
        'questions': existing.questions if existing else [],
    })


@login_required
def skill_gap(request):
    resumes = request.user.resumes.all()
    if request.method == 'POST':
        resume_id   = request.POST.get('resume_id')
        target_role = request.POST.get('target_role', '').strip()
        jd_texts    = [t.strip() for t in request.POST.get('job_descriptions', '').split('---') if t.strip()]
        if not resume_id or not target_role:
            messages.error(request, 'Please select a resume and enter a target role.')
            return render(request, 'tracker/skill_gap_form.html', {'resumes': resumes})
        resume = get_object_or_404(Resume, pk=resume_id, user=request.user)
        result = SkillGapService().analyse(resume, target_role, jd_texts or [''])
        analysis = SkillGapAnalysis.objects.create(
            user=request.user, resume=resume, target_role=target_role,
            job_descriptions=jd_texts, missing_skills=result['missing_skills'],
            present_skills=result['present_skills'], recommendations=result['recommendations'])
        return render(request, 'tracker/skill_gap_result.html',
                      {'analysis': analysis, 'result': result, 'resume': resume})
    return render(request, 'tracker/skill_gap_form.html', {'resumes': resumes})


@login_required
def rejection_analysis(request):
    rejected      = JobApplication.objects.filter(user=request.user, status='rejected')
    total_rejected= rejected.count()
    if total_rejected == 0:
        return render(request, 'tracker/rejection_analysis.html',
                      {'total_rejected': 0, 'patterns': [], 'suggestions': []})

    score_buckets = {'0-40': 0, '41-60': 0, '61-75': 0, '76+': 0}
    for app in rejected:
        s = app.ats_score_at_apply or 0
        if s <= 40:   score_buckets['0-40']  += 1
        elif s <= 60: score_buckets['41-60'] += 1
        elif s <= 75: score_buckets['61-75'] += 1
        else:         score_buckets['76+']   += 1

    from django.db.models import Count
    common_roles = (rejected.values('role').annotate(count=Count('id')).order_by('-count')[:5])

    suggestions = []
    worst_bucket = max(score_buckets, key=score_buckets.get)
    if worst_bucket in ('0-40', '41-60'):
        suggestions.append({
            'icon': 'bi-graph-up',
            'text': "Most rejections happened with ATS scores below 60. Use 'Fix My Resume' to optimise before applying.",
            'priority': 'high',
        })
    if score_buckets['76+'] > 0:
        suggestions.append({
            'icon': 'bi-person-check',
            'text': "You are getting rejected even with high ATS scores — the issue may be at the interview stage.",
            'priority': 'medium',
        })
    return render(request, 'tracker/rejection_analysis.html', {
        'total_rejected': total_rejected, 'score_buckets': score_buckets,
        'common_roles': common_roles, 'suggestions': suggestions,
    })
```

---

## 9. Authentication Views

**File:** `apps/authentication/views.py`

**Purpose:** Handles user registration (with async email verification via Celery), email token verification, profile editing, password change, account settings (delete all resumes, delete account, export all data as ZIP), and the main dashboard view which aggregates resume health scores, ATS score trends, job tracker stats, and activity log into a single context for Chart.js rendering.

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm
from .models import EmailVerificationToken
import logging

logger = logging.getLogger(__name__)


def _rate_limit_check(request, group: str, rate: str = '10/m') -> bool:
    try:
        from ratelimit.utils import is_ratelimited
        return is_ratelimited(request, group=group, key='ip', rate=rate,
                               method='POST', increment=True)
    except ImportError:
        return False


def register(request):
    """Create account and send email verification link asynchronously."""
    if request.method == 'POST':
        if _rate_limit_check(request, group='register', rate='5/m'):
            messages.error(request, 'Too many registration attempts. Please wait a minute.')
            return render(request, 'authentication/register.html',
                          {'form': UserRegistrationForm()})
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user     = form.save()
            username = form.cleaned_data.get('username')
            token_obj = EmailVerificationToken.create_for_user(user)
            try:
                from apps.resumes.tasks import send_verification_email_task
                base_url = request.build_absolute_uri('/').rstrip('/')
                send_verification_email_task.delay(user.id, token_obj.token, base_url)
            except Exception as e:
                logger.warning(f'Could not queue verification email: {e}')
            messages.success(request,
                f'Account created for {username}! Check your email to verify your address.')
            return redirect('login')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    return render(request, 'authentication/register.html', {'form': form})


def verify_email(request, token: str):
    """Verify email address via one-time token link."""
    token_obj = get_object_or_404(EmailVerificationToken, token=token)
    if token_obj.is_verified:
        messages.info(request, 'Your email is already verified.')
        return redirect('login')
    if token_obj.is_expired:
        messages.error(request, 'This link has expired. Request a new one below.')
        return redirect('resend_verification')
    from django.utils import timezone
    token_obj.verified_at = timezone.now()
    token_obj.save(update_fields=['verified_at'])
    token_obj.user.is_active = True
    token_obj.user.save(update_fields=['is_active'])
    messages.success(request, 'Email verified! You can now log in.')
    return redirect('login')


@login_required
def profile(request):
    """Edit profile fields and change password."""
    user = request.user
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_profile':
            email = request.POST.get('email', '').strip()
            if email and email != user.email:
                from django.contrib.auth.models import User as AuthUser
                if AuthUser.objects.filter(email=email).exclude(pk=user.pk).exists():
                    messages.error(request, 'That email is already in use.')
                    return redirect('profile')
            user.first_name = request.POST.get('first_name', '').strip()
            user.last_name  = request.POST.get('last_name', '').strip()
            user.email      = email
            user.save(update_fields=['first_name', 'last_name', 'email'])
            messages.success(request, 'Profile updated successfully.')
        elif action == 'change_password':
            from django.contrib.auth import update_session_auth_hash
            current = request.POST.get('current_password')
            new_pw  = request.POST.get('new_password')
            confirm = request.POST.get('confirm_password')
            if not user.check_password(current):
                messages.error(request, 'Current password is incorrect.')
            elif new_pw != confirm:
                messages.error(request, 'New passwords do not match.')
            elif len(new_pw) < 8:
                messages.error(request, 'Password must be at least 8 characters.')
            else:
                user.set_password(new_pw)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully.')
        return redirect('profile')
    from apps.resumes.models import Resume
    return render(request, 'authentication/profile.html',
                  {'user': user, 'resume_count': Resume.objects.filter(user=user).count()})


@login_required
def settings(request):
    """Danger-zone actions: delete resumes, delete account, export data."""
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'delete_all_resumes':
            from apps.resumes.models import Resume
            count, _ = Resume.objects.filter(user=request.user).delete()
            messages.success(request, f'Deleted {count} resume(s).')
        elif action == 'delete_account':
            from django.contrib.auth import logout
            user = request.user
            logout(request)
            user.delete()
            messages.success(request, 'Your account has been permanently deleted.')
            return redirect('login')
        elif action == 'export_data':
            import json, io, zipfile
            from apps.resumes.models import Resume
            from django.http import HttpResponse
            resumes = Resume.objects.filter(user=request.user).prefetch_related(
                'personal_info', 'experiences', 'education', 'skills', 'projects')
            export = {
                'user': {
                    'username': request.user.username,
                    'email': request.user.email,
                    'date_joined': request.user.date_joined.isoformat(),
                },
                'resumes': [{
                    'title': r.title, 'template': r.template,
                    'experiences': [{'company': e.company, 'role': e.role,
                                     'description': e.description}
                                    for e in r.experiences.all()],
                    'skills': [{'name': s.name, 'category': s.category}
                               for s in r.skills.all()],
                } for r in resumes],
            }
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr('nextgencv_export.json', json.dumps(export, indent=2))
            buf.seek(0)
            response = HttpResponse(buf.getvalue(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="nextgencv_data_export.zip"'
            return response
        return redirect('settings')
    return render(request, 'authentication/settings.html', {'user': request.user})


@login_required
def dashboard(request):
    """Main dashboard — aggregates resume health, ATS trends, tracker stats, activity log."""
    import json
    from django.db.models import Avg
    from django.utils import timezone
    from apps.resumes.services import ResumeService
    from apps.analytics.services.analytics_service import AnalyticsService
    from apps.resumes.models import ResumeAnalysis
    from apps.tracker.models import JobApplication
    from apps.authentication.models import ActivityLog

    resumes = ResumeService.get_user_resumes(request.user)

    resume_health   = None
    average_score   = None
    score_breakdown = None

    if resumes.exists():
        resume_health = AnalyticsService.calculate_resume_health(resumes.first())
        analyses_qs   = ResumeAnalysis.objects.filter(resume__user=request.user)
        if analyses_qs.exists():
            agg = analyses_qs.aggregate(Avg('final_score'))
            average_score = round(agg['final_score__avg'], 1) if agg['final_score__avg'] else None
            latest = analyses_qs.order_by('-analysis_timestamp').first()
            if latest:
                score_breakdown = {
                    'keyword_match':       round(latest.keyword_match_score, 1),
                    'skill_relevance':     round(latest.skill_relevance_score, 1),
                    'section_completeness':round(latest.section_completeness_score, 1),
                    'experience_impact':   round(latest.experience_impact_score, 1),
                    'quantification':      round(latest.quantification_score, 1),
                    'action_verbs':        round(latest.action_verb_score, 1),
                }

    apps_qs = JobApplication.objects.filter(user=request.user)
    tracker_stats = {
        'total':     apps_qs.count(),
        'applied':   apps_qs.filter(status__in=['applied','interview','offer','rejected']).count(),
        'interviews':apps_qs.filter(status__in=['interview','offer']).count(),
        'offers':    apps_qs.filter(status='offer').count(),
    }
    tracker_stats['callback_rate'] = (
        round(tracker_stats['interviews'] / tracker_stats['applied'] * 100, 1)
        if tracker_stats['applied'] else 0)

    chart_data_json = None
    show_charts     = False
    if resumes.exists():
        analyses = ResumeAnalysis.objects.filter(
            resume__user=request.user).order_by('analysis_timestamp')[:12]
        if analyses.count() >= 1:
            show_charts = True
            chart_data_json = json.dumps({
                'score_trend': {
                    'labels': [a.analysis_timestamp.strftime('%b %d') for a in analyses],
                    'scores': [float(a.final_score) for a in analyses],
                },
                'breakdown': score_breakdown or {},
            })

    return render(request, 'authentication/dashboard_new.html', {
        'user': request.user, 'resumes': resumes,
        'resume_health': resume_health, 'average_score': average_score,
        'score_breakdown': score_breakdown, 'tracker_stats': tracker_stats,
        'show_charts': show_charts, 'chart_data_json': chart_data_json,
        'current_date': timezone.now(), 'is_new_user': not resumes.exists(),
        'recent_activities': [
            {'type': act.action, 'description': act.description, 'timestamp': act.created_at}
            for act in ActivityLog.objects.filter(user=request.user)[:8]
        ],
    })
```

---

## 10. Analytics Service

**File:** `apps/analytics/services/analytics_service.py`

**Purpose:** Calculates resume health scores (five-component weighted formula), score trends with moving averages, top missing keywords aggregated across all analyses, and a full improvement report with personalised recommendations. Uses Django's `LocMemCache` (or Redis in production) to avoid recomputing expensive aggregations on every page load.

```python
from typing import Dict, List, Tuple
from django.contrib.auth.models import User
from django.db.models import Avg
from apps.resumes.models import Resume, ResumeAnalysis, OptimizationHistory
from apps.analyzer.services.action_verb_analyzer import ActionVerbAnalyzerService
from apps.analyzer.services.quantification_detector import QuantificationDetectorService
from .cache_utils import (
    get_cached_resume_health, cache_resume_health,
    get_cached_score_trends,  cache_score_trends,
)


class AnalyticsService:

    @staticmethod
    def calculate_resume_health(resume: Resume) -> float:
        """
        Five-component health score (0-100):
          40 pts — section completeness
          15 pts — contact info completeness
          20 pts — quantified achievements
          15 pts — strong action verb usage
          10 pts — ATS-friendly template
        """
        cached = get_cached_resume_health(resume.id)
        if cached is not None:
            return cached

        health = 0.0

        # 1. Section completeness (40 pts)
        sections = {
            'personal_info': hasattr(resume, 'personal_info'),
            'experiences':   resume.experiences.exists(),
            'education':     resume.education.exists(),
            'skills':        resume.skills.exists(),
        }
        health += (sum(1 for v in sections.values() if v) / len(sections)) * 40

        # 2. Contact info completeness (15 pts)
        if hasattr(resume, 'personal_info'):
            pi = resume.personal_info
            contact_fields = [bool(pi.email), bool(pi.phone), bool(pi.location)]
            health += (sum(contact_fields) / len(contact_fields)) * 15

        # 3. Quantified achievements (20 pts)
        total_bullets      = 0
        quantified_bullets = 0
        for exp in resume.experiences.all():
            if exp.description:
                bullets = [l.strip() for l in exp.description.split('\n') if l.strip()]
                total_bullets += len(bullets)
                for bullet in bullets:
                    if QuantificationDetectorService.has_quantification(bullet):
                        quantified_bullets += 1
        if total_bullets > 0:
            health += (quantified_bullets / total_bullets) * 20

        # 4. Strong action verb usage (15 pts)
        strong_verb_count = 0
        for exp in resume.experiences.all():
            if exp.description:
                for bullet in [l.strip() for l in exp.description.split('\n') if l.strip()]:
                    words = bullet.split()
                    if words:
                        first = words[0].lower().rstrip('.,;:')
                        if first in ActionVerbAnalyzerService.STRONG_ACTION_VERBS:
                            strong_verb_count += 1
        if total_bullets > 0:
            health += (strong_verb_count / total_bullets) * 15

        # 5. ATS-friendly template (10 pts)
        if resume.template in ['professional', 'modern', 'classic']:
            health += 10

        health = round(health, 2)
        cache_resume_health(resume.id, health)
        return health

    @staticmethod
    def get_score_trends(user: User, window_size: int = 5) -> Dict:
        """
        Score trend over time with moving average.
        Cached for 10 minutes per user.
        """
        cached = get_cached_score_trends(user.id)
        if cached is not None:
            return cached

        analyses = ResumeAnalysis.objects.filter(
            resume__user=user
        ).order_by('analysis_timestamp').values_list('final_score', 'analysis_timestamp')

        if not analyses:
            return {'scores': [], 'timestamps': [], 'moving_average': [],
                    'improvement_rate': 0.0, 'trend': 'no_data'}

        scores     = [s for s, _ in analyses]
        timestamps = [ts.isoformat() for _, ts in analyses]
        moving_avg = AnalyticsService._calculate_moving_average(scores, window_size)

        improvement_rate = (scores[-1] - scores[0]) / len(scores) if len(scores) >= 2 else 0.0
        trend = ('improving' if improvement_rate > 0.5
                 else 'declining' if improvement_rate < -0.5 else 'stable')

        result = {
            'scores': scores, 'timestamps': timestamps,
            'moving_average': moving_avg,
            'improvement_rate': round(improvement_rate, 2),
            'trend': trend,
        }
        cache_score_trends(user.id, result)
        return result

    @staticmethod
    def _calculate_moving_average(scores: List[float], window_size: int) -> List[float]:
        moving_avg = []
        for i in range(len(scores)):
            window = scores[max(0, i - window_size + 1): i + 1]
            moving_avg.append(round(sum(window) / len(window), 2))
        return moving_avg

    @staticmethod
    def get_top_missing_keywords(user: User, limit: int = 10) -> List[Tuple[str, int]]:
        """Aggregate missing keywords across all analyses, ranked by frequency."""
        keyword_counts: Dict[str, int] = {}
        for analysis in ResumeAnalysis.objects.filter(resume__user=user):
            for kw in analysis.missing_keywords:
                keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
        return sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:limit]

    @staticmethod
    def generate_improvement_report(user: User) -> Dict:
        """Comprehensive improvement report with personalised recommendations."""
        resumes = Resume.objects.filter(user=user).prefetch_related(
            'analyses', 'optimizations', 'versions')

        if not resumes.exists():
            return {
                'total_resumes': 0, 'average_health': 0.0,
                'total_optimizations': 0, 'average_improvement': 0.0,
                'top_missing_keywords': [],
                'recommendations': ['Create your first resume to get started!'],
            }

        health_scores = [AnalyticsService.calculate_resume_health(r) for r in resumes]
        average_health = sum(health_scores) / len(health_scores)

        all_opts = OptimizationHistory.objects.filter(resume__user=user)
        improvements = [o.improvement_delta for o in all_opts if o.improvement_delta is not None]
        average_improvement = sum(improvements) / len(improvements) if improvements else 0.0

        top_missing = AnalyticsService.get_top_missing_keywords(user, limit=10)
        recommendations = AnalyticsService._generate_recommendations(
            average_health, all_opts.count(), top_missing, resumes)

        return {
            'total_resumes':       resumes.count(),
            'average_health':      round(average_health, 2),
            'total_optimizations': all_opts.count(),
            'average_improvement': round(average_improvement, 2),
            'top_missing_keywords':top_missing,
            'recommendations':     recommendations,
            'health_scores':       health_scores,
        }

    @staticmethod
    def _generate_recommendations(average_health, total_optimizations,
                                   top_missing_keywords, resumes) -> List[str]:
        recs = []
        if average_health < 50:
            recs.append("Resume health is below 50%. Complete all sections and add quantified achievements.")
        elif average_health < 70:
            recs.append("Resume health is moderate. Add more quantified achievements and stronger action verbs.")
        else:
            recs.append("Resume health is good! Keep maintaining high-quality content.")
        if total_optimizations == 0:
            recs.append("Try 'Fix My Resume' to automatically optimise for ATS systems.")
        if top_missing_keywords:
            top3 = [kw for kw, _ in top_missing_keywords[:3]]
            recs.append(f"Frequently missing keywords: {', '.join(top3)}")
        for resume in resumes:
            if not resume.experiences.exists():
                recs.append(f"Add work experience to '{resume.title}' to improve completeness.")
                break
            if not resume.skills.exists():
                recs.append(f"Add skills to '{resume.title}' to improve keyword matching.")
                break
        return recs
```

---

*End of NextGenCV Main Code Reference*
