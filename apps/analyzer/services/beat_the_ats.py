"""
Beat the ATS — tells users exactly which keywords to add to cross the next
score threshold (e.g. push from 62 → 80).

This is the highest-impact hackathon differentiator: specific, actionable,
gamified. Users can see their score tick up in real time as they add keywords.
"""
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

# Score thresholds with labels
THRESHOLDS = [
    (40,  'Poor',      'Most ATS systems will auto-reject below 40.'),
    (60,  'Fair',      'Recruiters may see your resume but it needs work.'),
    (75,  'Good',      'You will pass most ATS filters.'),
    (85,  'Strong',    'You are competitive for this role.'),
    (95,  'Excellent', 'Top-tier ATS score \u2014 you stand out.'),
    (101, 'Perfect',   'Maximum score achieved.'),
]


def get_next_threshold(current_score: float):
    """Return (target_score, label, message) for the next threshold above current_score."""
    for score, label, message in THRESHOLDS:
        if current_score < score:
            return score, label, message
    return 101, 'Perfect', 'Maximum score achieved.'


class BeatTheATSService:
    """
    Given a resume and job description, returns the minimum set of keywords
    the user needs to add to cross the next score threshold.
    """

    @staticmethod
    def get_battle_plan(resume, job_description: str) -> Dict:
        """
        Returns a battle plan: current score, next threshold, and the exact
        keywords (ranked by impact) needed to get there.

        Returns:
            {
                current_score: float,
                next_threshold: int,
                next_label: str,
                next_message: str,
                points_needed: float,
                keywords_to_add: [
                    {keyword, impact_points, section, reason}
                ],
                already_winning: bool,
            }
        """
        from apps.analyzer.services.scoring_engine import ScoringEngineService
        from apps.analyzer.services.keyword_extractor import KeywordExtractorService

        score_data = ScoringEngineService.calculate_ats_score(resume, job_description)
        current_score = score_data['final_score']

        next_threshold, next_label, next_message = get_next_threshold(current_score)

        if current_score >= 95:
            return {
                'current_score': current_score,
                'next_threshold': 100,
                'next_label': 'Perfect',
                'next_message': 'Maximum score achieved.',
                'points_needed': 0,
                'keywords_to_add': [],
                'already_winning': True,
            }

        points_needed = next_threshold - current_score
        missing_keywords = score_data.get('missing_keywords', [])

        # Estimate impact of each missing keyword
        # Each keyword added improves keyword_match_score proportionally.
        # keyword_match weight = 0.30, so each keyword is worth:
        # (1 / total_jd_keywords) * 100 * 0.30 points
        resume_text = ScoringEngineService._get_resume_text(resume)
        jd_keywords = KeywordExtractorService.extract_keywords(job_description)
        total_jd_kw = max(len(jd_keywords), 1)
        points_per_keyword = (1 / total_jd_kw) * 100 * 0.30

        # Rank missing keywords by how likely they are to appear in skills vs experience
        existing_skills = set(s.lower() for s in resume.skills.values_list('name', flat=True))
        existing_exp_text = ScoringEngineService._get_experience_text(resume).lower()

        keywords_to_add = []
        cumulative = 0.0

        for kw in missing_keywords:
            if cumulative >= points_needed * 1.2:
                break  # We have enough suggestions to comfortably cross the threshold

            # Determine best section to add this keyword
            if len(kw.split()) == 1 and kw.lower() not in existing_skills:
                section = 'Skills'
                reason = f'Add "{kw}" to your Skills section for immediate keyword match.'
            else:
                section = 'Experience'
                reason = f'Weave "{kw}" into a bullet point in your most recent role.'

            keywords_to_add.append({
                'keyword': kw,
                'impact_points': round(points_per_keyword, 1),
                'section': section,
                'reason': reason,
            })
            cumulative += points_per_keyword

        # How many keywords are actually needed
        needed_count = 0
        running = 0.0
        for kw_data in keywords_to_add:
            running += kw_data['impact_points']
            needed_count += 1
            if running >= points_needed:
                break

        return {
            'current_score': round(current_score, 1),
            'next_threshold': next_threshold,
            'next_label': next_label,
            'next_message': next_message,
            'points_needed': round(points_needed, 1),
            'keywords_needed_count': needed_count,
            'keywords_to_add': keywords_to_add[:10],  # cap at 10
            'already_winning': False,
            'score_data': score_data,
        }

    @staticmethod
    def simulate_score_after_keywords(resume, job_description: str, added_keywords: List[str]) -> float:
        """
        Simulate what the ATS score would be if the user added the given keywords.
        Used for the live score preview as users tick checkboxes.
        """
        from apps.analyzer.services.keyword_extractor import KeywordExtractorService
        from apps.analyzer.services.scoring_engine import ScoringEngineService

        resume_text = ScoringEngineService._get_resume_text(resume)
        augmented_text = resume_text + ' ' + ' '.join(added_keywords)

        resume_kw = KeywordExtractorService.extract_keywords(augmented_text)
        jd_kw = KeywordExtractorService.extract_keywords(job_description)

        if not jd_kw:
            return 0.0

        matched = resume_kw & jd_kw
        keyword_score = min(len(matched) / len(jd_kw) * 100, 100)

        # Get current component scores and substitute the new keyword score
        score_data = ScoringEngineService.calculate_ats_score(resume, job_description)
        weights = ScoringEngineService.WEIGHTS

        simulated = (
            keyword_score * weights['keyword_match'] +
            score_data['skill_relevance_score'] * weights['skill_relevance'] +
            score_data['section_completeness_score'] * weights['section_completeness'] +
            score_data['experience_impact_score'] * weights['experience_impact'] +
            score_data['quantification_score'] * weights['quantification'] +
            score_data['action_verb_score'] * weights['action_verb']
        )
        return round(min(simulated, 100), 1)
