"""
LLM Service — OpenAI integration with graceful fallback to rule-based heuristics.

All AI features route through this service. If OPENAI_API_KEY is not set or
the API call fails, the service falls back to the existing rule-based logic
so the app always works.

Usage:
    from apps.resumes.services.llm_service import LLMService
    result = LLMService.rewrite_bullet(bullet, context)
"""
import logging
import json
from typing import Optional

from django.conf import settings

logger = logging.getLogger(__name__)

# Singleton client — created once, reused across all requests
_openai_client = None


def _get_client():
    """Return a singleton OpenAI client. Thread-safe for read after first write."""
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
    """
    Send a chat completion request. Returns the response text or None on failure.
    """
    client = _get_client()
    if client is None:
        return None

    kwargs = {
        'model': settings.OPENAI_MODEL,
        'messages': [
            {'role': 'system', 'content': system},
            {'role': 'user', 'content': user},
        ],
        'max_tokens': max_tokens or settings.OPENAI_MAX_TOKENS,
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
    """
    Central LLM service. Every method has a fallback so the app works without an API key.
    """

    # ── Bullet Point Rewriting ────────────────────────────────────────────────

    @staticmethod
    def rewrite_bullet(bullet: str, job_description: str = '', role: str = '') -> dict:
        """
        Rewrite a resume bullet point using LLM or rule-based fallback.

        Returns:
            {original, rewritten, changed, reason, ai_powered}
        """
        if not bullet or not bullet.strip():
            return {'original': bullet, 'rewritten': bullet, 'changed': False,
                    'reason': 'Empty bullet', 'ai_powered': False}

        system = (
            "You are an expert resume writer. Rewrite the given resume bullet point to be "
            "more impactful: start with a strong action verb, quantify achievements where "
            "possible, be concise (under 25 words), and use keywords from the job description "
            "if provided. Return ONLY the rewritten bullet — no explanation, no quotes."
        )
        context_hint = f"\nJob description context: {job_description[:500]}" if job_description else ""
        user = f"Bullet to rewrite: {bullet}{context_hint}"

        rewritten = _chat(system, user, max_tokens=100)

        if rewritten and rewritten != bullet:
            return {
                'original': bullet,
                'rewritten': rewritten,
                'changed': True,
                'reason': 'AI-powered rewrite for stronger impact',
                'ai_powered': True,
            }

        # Fallback to rule-based
        from apps.resumes.services.bullet_point_rewriter import BulletPointRewriterService
        result = BulletPointRewriterService.rewrite_bullet_point(bullet, job_description)
        result['ai_powered'] = False
        return result

    @staticmethod
    def rewrite_bullets_batch(bullets: list, job_description: str = '', role: str = '') -> list:
        """Rewrite multiple bullets. Uses a single API call for efficiency."""
        if not bullets:
            return []

        if not settings.AI_ENABLED:
            from apps.resumes.services.bullet_point_rewriter import BulletPointRewriterService
            results = BulletPointRewriterService.rewrite_multiple_bullets(bullets, job_description)
            for r in results:
                r['ai_powered'] = False
            return results

        system = (
            "You are an expert resume writer. Rewrite each resume bullet point to be more "
            "impactful: strong action verbs, quantified achievements, concise (under 25 words). "
            "Use keywords from the job description where natural. "
            "Return a JSON object with key 'bullets' containing an array of rewritten strings "
            "in the same order as input."
        )
        numbered = '\n'.join(f"{i+1}. {b}" for i, b in enumerate(bullets))
        jd_hint = f"\nJob description: {job_description[:600]}" if job_description else ""
        user = f"Bullets to rewrite:{jd_hint}\n{numbered}"

        raw = _chat(system, user, max_tokens=800, json_mode=True)
        if raw:
            try:
                data = json.loads(raw)
                rewritten_list = data.get('bullets', [])
                if len(rewritten_list) == len(bullets):
                    return [
                        {
                            'original': orig,
                            'rewritten': new,
                            'changed': orig.strip() != new.strip(),
                            'reason': 'AI-powered rewrite',
                            'ai_powered': True,
                        }
                        for orig, new in zip(bullets, rewritten_list)
                    ]
            except (json.JSONDecodeError, KeyError):
                pass

        # Fallback
        from apps.resumes.services.bullet_point_rewriter import BulletPointRewriterService
        results = BulletPointRewriterService.rewrite_multiple_bullets(bullets, job_description)
        for r in results:
            r['ai_powered'] = False
        return results

    # ── Cover Letter Generation ───────────────────────────────────────────────

    @staticmethod
    def generate_cover_letter(resume, company: str, role: str, job_description: str) -> dict:
        """
        Generate a personalised cover letter using LLM or template fallback.

        Returns:
            {content, ai_powered}
        """
        info = getattr(resume, 'personal_info', None)
        name = info.full_name if info else resume.user.get_full_name() or resume.user.username
        skills = list(resume.skills.values_list('name', flat=True)[:8])
        experiences = list(resume.experiences.order_by('-start_date').values(
            'role', 'company', 'description', 'achievements'
        )[:3])

        system = (
            "You are an expert career coach writing a compelling, personalised cover letter. "
            "The letter should be professional, specific to the role and company, highlight "
            "relevant achievements with metrics, and be 3-4 paragraphs. "
            "Do NOT use generic filler phrases. Mirror keywords from the job description naturally."
        )
        user = (
            f"Write a cover letter for {name} applying to {role} at {company}.\n\n"
            f"Job Description:\n{job_description[:1000]}\n\n"
            f"Candidate Skills: {', '.join(skills)}\n\n"
            f"Recent Experience:\n" +
            '\n'.join(
                f"- {e['role']} at {e['company']}: {(e['achievements'] or e['description'] or '')[:200]}"
                for e in experiences
            )
        )

        content = _chat(system, user, max_tokens=600)
        if content:
            return {'content': content, 'ai_powered': True}

        # Fallback to template-based
        from apps.tracker.cover_letter_service import CoverLetterService
        content = CoverLetterService().generate(resume, company, role, job_description)
        return {'content': content, 'ai_powered': False}

    # ── Professional Summary ──────────────────────────────────────────────────

    @staticmethod
    def generate_summary(wizard_data: dict) -> dict:
        """
        Generate a professional summary from wizard data.

        Returns:
            {summary, ai_powered}
        """
        experiences = wizard_data.get('experiences', [])
        skills = [s['name'] for s in wizard_data.get('skills', [])]
        education = wizard_data.get('education', [])

        system = (
            "You are an expert resume writer. Write a compelling 2-3 sentence professional "
            "summary for a resume. Be specific, use strong language, avoid clichés. "
            "Return ONLY the summary text."
        )
        exp_text = '\n'.join(
            f"- {e.get('role', '')} at {e.get('company', '')}: {e.get('description', '')[:150]}"
            for e in experiences[:3]
        )
        edu_text = ', '.join(
            f"{e.get('degree', '')} in {e.get('field', '')} from {e.get('institution', '')}"
            for e in education[:2]
        )
        user = (
            f"Experience:\n{exp_text}\n\n"
            f"Skills: {', '.join(skills[:10])}\n\n"
            f"Education: {edu_text}"
        )

        summary = _chat(system, user, max_tokens=150)
        if summary:
            return {'summary': summary, 'ai_powered': True}

        # Fallback
        from apps.resumes.views import generate_ai_summary
        return {'summary': generate_ai_summary(wizard_data), 'ai_powered': False}

    # ── Interview Questions ───────────────────────────────────────────────────

    @staticmethod
    def generate_interview_questions(resume, role: str, job_description: str, company: str = '') -> dict:
        """
        Generate tailored interview questions with talking points.

        Returns:
            {questions: [...], ai_powered}
        """
        skills = list(resume.skills.values_list('name', flat=True)[:8])
        experiences = list(resume.experiences.order_by('-start_date').values(
            'role', 'company', 'achievements', 'description'
        )[:3])

        system = (
            "You are an expert interview coach. Generate 12 tailored interview questions "
            "for the candidate based on their resume and the job description. "
            "Include a mix of: behavioral (STAR), technical, situational, and motivational questions. "
            "For each question provide talking points and relevant resume evidence. "
            "Return JSON: {\"questions\": [{\"question\": str, \"category\": str, "
            "\"talking_points\": [str], \"resume_evidence\": str}]}"
        )
        exp_text = '\n'.join(
            f"- {e['role']} at {e['company']}: {(e['achievements'] or e['description'] or '')[:200]}"
            for e in experiences
        )
        user = (
            f"Role: {role} at {company or 'the company'}\n\n"
            f"Job Description:\n{job_description[:800]}\n\n"
            f"Candidate Skills: {', '.join(skills)}\n\n"
            f"Experience:\n{exp_text}"
        )

        raw = _chat(system, user, max_tokens=1200, json_mode=True)
        if raw:
            try:
                data = json.loads(raw)
                questions = data.get('questions', [])
                if questions:
                    return {'questions': questions, 'ai_powered': True}
            except (json.JSONDecodeError, KeyError):
                pass

        # Fallback
        from apps.tracker.interview_prep_service import InterviewPrepService
        questions = InterviewPrepService().generate(resume, role, job_description, company)
        return {'questions': questions, 'ai_powered': False}

    # ── Rejection Analysis ────────────────────────────────────────────────────

    @staticmethod
    def analyse_rejection(resume, job_description: str, company: str, role: str) -> dict:
        """
        Analyse why a resume may have been rejected for a specific role.

        Returns:
            {analysis, suggestions, ai_powered}
        """
        from apps.analyzer.services.scoring_engine import ScoringEngineService
        score_data = ScoringEngineService.calculate_ats_score(resume, job_description)

        system = (
            "You are an expert ATS and hiring consultant. Analyse why a resume may have been "
            "rejected for a specific role. Be direct, specific, and actionable. "
            "Return JSON: {\"analysis\": str, \"top_issues\": [str], \"quick_fixes\": [str]}"
        )
        user = (
            f"Role: {role} at {company}\n\n"
            f"ATS Score: {score_data['final_score']:.0f}/100\n"
            f"Keyword Match: {score_data['keyword_match_score']:.0f}/100\n"
            f"Missing Keywords: {', '.join(score_data['missing_keywords'][:15])}\n"
            f"Weak Action Verbs: {', '.join(score_data['weak_action_verbs'][:10])}\n\n"
            f"Job Description:\n{job_description[:800]}"
        )

        raw = _chat(system, user, max_tokens=600, json_mode=True)
        if raw:
            try:
                data = json.loads(raw)
                return {
                    'analysis': data.get('analysis', ''),
                    'top_issues': data.get('top_issues', []),
                    'quick_fixes': data.get('quick_fixes', []),
                    'score_data': score_data,
                    'ai_powered': True,
                }
            except (json.JSONDecodeError, KeyError):
                pass

        # Fallback: rule-based analysis
        issues = []
        fixes = []
        if score_data['keyword_match_score'] < 50:
            issues.append(f"Low keyword match ({score_data['keyword_match_score']:.0f}%) — resume doesn't mirror JD language")
            fixes.append(f"Add these missing keywords: {', '.join(score_data['missing_keywords'][:8])}")
        if score_data['quantification_score'] < 40:
            issues.append("Few quantified achievements — ATS and recruiters prefer numbers")
            fixes.append("Add metrics to at least 3 bullet points (%, $, time saved, team size)")
        if score_data['action_verb_score'] < 50:
            issues.append("Weak action verbs reduce impact score")
            fixes.append("Replace weak verbs with: led, built, delivered, drove, achieved")

        return {
            'analysis': f"Your resume scored {score_data['final_score']:.0f}/100 for this role.",
            'top_issues': issues,
            'quick_fixes': fixes,
            'score_data': score_data,
            'ai_powered': False,
        }

    # ── Skill Gap Analysis ────────────────────────────────────────────────────

    @staticmethod
    def analyse_skill_gap(resume, target_role: str, job_descriptions: list) -> dict:
        """
        AI-powered skill gap analysis with learning recommendations.

        Returns:
            {missing_skills, present_skills, recommendations, ai_powered}
        """
        skills = list(resume.skills.values_list('name', flat=True))
        jd_combined = '\n\n'.join(job_descriptions[:3])[:1500]

        system = (
            "You are a career development expert. Analyse the skill gap between a candidate's "
            "current skills and what's needed for their target role. "
            "Return JSON: {\"missing_skills\": [{\"skill\": str, \"importance\": \"high|medium|low\", "
            "\"learn_in\": str}], \"present_skills\": [str], "
            "\"recommendations\": [{\"action\": str, \"resource\": str, \"timeline\": str}]}"
        )
        user = (
            f"Target Role: {target_role}\n\n"
            f"Current Skills: {', '.join(skills)}\n\n"
            f"Job Descriptions:\n{jd_combined}"
        )

        raw = _chat(system, user, max_tokens=800, json_mode=True)
        if raw:
            try:
                data = json.loads(raw)
                return {
                    'missing_skills': data.get('missing_skills', []),
                    'present_skills': data.get('present_skills', skills),
                    'recommendations': data.get('recommendations', []),
                    'ai_powered': True,
                }
            except (json.JSONDecodeError, KeyError):
                pass

        # Fallback
        from apps.tracker.skill_gap_service import SkillGapService
        result = SkillGapService().analyse(resume, target_role, job_descriptions)
        result['ai_powered'] = False
        return result

    # ── ATS Explanation ───────────────────────────────────────────────────────

    @staticmethod
    def explain_ats_score(score_data: dict, resume_title: str = '') -> str:
        """
        Generate a human-readable explanation of an ATS score.
        """
        system = (
            "You are an ATS expert. Explain this resume's ATS score in plain English. "
            "Be specific about what's working and what needs improvement. "
            "Keep it under 100 words. Be direct and actionable."
        )
        user = (
            f"Resume: {resume_title}\n"
            f"Overall Score: {score_data.get('final_score', 0):.0f}/100\n"
            f"Keyword Match: {score_data.get('keyword_match_score', 0):.0f}/100\n"
            f"Skills Relevance: {score_data.get('skill_relevance_score', 0):.0f}/100\n"
            f"Section Completeness: {score_data.get('section_completeness_score', 0):.0f}/100\n"
            f"Experience Impact: {score_data.get('experience_impact_score', 0):.0f}/100\n"
            f"Quantification: {score_data.get('quantification_score', 0):.0f}/100\n"
            f"Action Verbs: {score_data.get('action_verb_score', 0):.0f}/100"
        )

        explanation = _chat(system, user, max_tokens=150)
        if explanation:
            return explanation

        # Fallback
        score = score_data.get('final_score', 0)
        if score >= 80:
            return f"Strong resume scoring {score:.0f}/100. Well-optimised for ATS systems."
        elif score >= 60:
            return f"Good resume scoring {score:.0f}/100. Adding missing keywords and quantifying achievements will push it higher."
        else:
            return f"Resume scores {score:.0f}/100. Focus on keyword matching and adding measurable achievements."
