# ATS scoring engine service
from typing import Dict, Set
from .keyword_extractor import KeywordExtractorService
from .action_verb_analyzer import ActionVerbAnalyzerService
from .quantification_detector import QuantificationDetectorService


class ScoringEngineService:
    """
    Comprehensive ATS scoring engine that calculates weighted composite scores.
    Evaluates resumes across multiple dimensions for ATS compatibility.
    """
    
    # Scoring weights (must sum to 1.0)
    WEIGHTS = {
        'keyword_match': 0.30,      # 30%
        'skill_relevance': 0.20,    # 20%
        'section_completeness': 0.15,  # 15%
        'experience_impact': 0.15,  # 15%
        'quantification': 0.10,     # 10%
        'action_verb': 0.10         # 10%
    }
    
    @staticmethod
    def calculate_ats_score(resume, job_description: str) -> Dict:
        """
        Calculate comprehensive ATS score for a resume.
        
        Args:
            resume: Resume model instance
            job_description: Job description text
            
        Returns:
            Dictionary containing all component scores and final weighted score
        """
        # Extract resume text
        resume_text = ScoringEngineService._get_resume_text(resume)
        
        # Calculate component scores
        keyword_score = ScoringEngineService.calculate_keyword_match_score(
            resume_text, job_description
        )
        
        skill_score = ScoringEngineService.calculate_skill_relevance_score(
            resume, job_description
        )
        
        completeness_score = ScoringEngineService.calculate_section_completeness_score(
            resume
        )
        
        impact_score = ScoringEngineService.calculate_experience_impact_score(
            resume
        )
        
        quant_score = ScoringEngineService.calculate_quantification_score(
            resume
        )
        
        verb_score = ScoringEngineService.calculate_action_verb_score(
            resume
        )
        
        # Calculate weighted final score
        final_score = (
            keyword_score * ScoringEngineService.WEIGHTS['keyword_match'] +
            skill_score * ScoringEngineService.WEIGHTS['skill_relevance'] +
            completeness_score * ScoringEngineService.WEIGHTS['section_completeness'] +
            impact_score * ScoringEngineService.WEIGHTS['experience_impact'] +
            quant_score * ScoringEngineService.WEIGHTS['quantification'] +
            verb_score * ScoringEngineService.WEIGHTS['action_verb']
        )
        
        # Extract keywords for detailed analysis
        resume_keywords = KeywordExtractorService.extract_keywords(resume_text)
        jd_keywords = KeywordExtractorService.extract_keywords(job_description)
        
        matched_keywords = list(resume_keywords & jd_keywords)
        missing_keywords = list(jd_keywords - resume_keywords)
        
        # Analyze action verbs
        experience_text = ScoringEngineService._get_experience_text(resume)
        verb_analysis = ActionVerbAnalyzerService.analyze_action_verbs(experience_text)
        
        # Detect missing quantifications
        missing_quants = ScoringEngineService._identify_missing_quantifications(resume)
        
        return {
            'final_score': round(final_score, 2),
            'keyword_match_score': round(keyword_score, 2),
            'skill_relevance_score': round(skill_score, 2),
            'section_completeness_score': round(completeness_score, 2),
            'experience_impact_score': round(impact_score, 2),
            'quantification_score': round(quant_score, 2),
            'action_verb_score': round(verb_score, 2),
            'matched_keywords': matched_keywords[:20],  # Top 20
            'missing_keywords': missing_keywords[:20],  # Top 20
            'weak_action_verbs': verb_analysis['weak_verbs'],
            'missing_quantifications': missing_quants
        }
    
    @staticmethod
    def calculate_keyword_match_score(resume_text: str, job_description: str) -> float:
        """
        Calculate keyword match percentage between resume and job description.
        
        Args:
            resume_text: Full resume text
            job_description: Job description text
            
        Returns:
            Score from 0-100 based on keyword overlap
        """
        if not resume_text or not job_description:
            return 0.0
        
        resume_keywords = KeywordExtractorService.extract_keywords(resume_text)
        jd_keywords = KeywordExtractorService.extract_keywords(job_description)
        
        if not jd_keywords:
            return 50.0  # Neutral score if no JD keywords
        
        # Calculate overlap
        matched = resume_keywords & jd_keywords
        match_ratio = len(matched) / len(jd_keywords)
        
        # Convert to 0-100 scale
        score = match_ratio * 100
        
        # Cap at 100
        return min(score, 100.0)
    
    @staticmethod
    def calculate_skill_relevance_score(resume, job_description: str) -> float:
        """
        Calculate skill relevance based on job description keywords.
        
        Args:
            resume: Resume model instance
            job_description: Job description text
            
        Returns:
            Score from 0-100 based on skill relevance
        """
        if not job_description:
            return 50.0  # Neutral score
        
        # Get resume skills
        skills = resume.skills.all()
        if not skills:
            return 20.0  # Low score for no skills
        
        skill_text = ' '.join([skill.name.lower() for skill in skills])
        
        # Extract JD keywords
        jd_keywords = KeywordExtractorService.extract_keywords(job_description)
        skill_keywords = KeywordExtractorService.extract_keywords(skill_text)
        
        if not jd_keywords:
            return 50.0
        
        # Calculate overlap
        matched = skill_keywords & jd_keywords
        match_ratio = len(matched) / len(jd_keywords)
        
        # Convert to 0-100 scale with bonus for having skills
        base_score = match_ratio * 80  # Max 80 from matching
        skill_bonus = min(len(skills) * 2, 20)  # Up to 20 bonus for having skills
        
        score = base_score + skill_bonus
        
        return min(score, 100.0)
    
    @staticmethod
    def calculate_section_completeness_score(resume) -> float:
        """
        Calculate section completeness score.
        
        Args:
            resume: Resume model instance
            
        Returns:
            Score from 0-100 based on presence and completeness of sections
        """
        score = 0.0
        
        # Personal Info (25 points)
        try:
            personal_info = resume.personal_info
            if personal_info:
                # Check required fields
                if personal_info.full_name:
                    score += 8
                if personal_info.email:
                    score += 8
                if personal_info.phone:
                    score += 5
                if personal_info.location:
                    score += 4
        except:
            pass
        
        # Experience (30 points)
        if resume.experiences.exists():
            score += 15  # Has experience section
            # Bonus for multiple experiences
            exp_count = min(resume.experiences.count(), 3)
            score += exp_count * 5
        
        # Education (20 points)
        if resume.education.exists():
            score += 10  # Has education section
            # Bonus for multiple entries
            edu_count = min(resume.education.count(), 2)
            score += edu_count * 5
        
        # Skills (15 points)
        if resume.skills.exists():
            score += 10  # Has skills section
            # Bonus for multiple skills
            skill_count = min(resume.skills.count(), 5)
            score += skill_count * 1
        
        # Projects (10 points - optional but valuable)
        if resume.projects.exists():
            score += 5
            project_count = min(resume.projects.count(), 2)
            score += project_count * 2.5
        
        return min(score, 100.0)
    
    @staticmethod
    def calculate_experience_impact_score(resume) -> float:
        """
        Calculate experience impact score based on content quality.
        
        Args:
            resume: Resume model instance
            
        Returns:
            Score from 0-100 based on experience quality
        """
        if not resume.experiences.exists():
            return 0.0
        
        experiences = resume.experiences.all()
        total_score = 0.0
        
        for exp in experiences:
            exp_score = 0.0
            
            # Has description (40 points)
            if exp.description and exp.description.strip():
                exp_score += 40
                
                # Length of description (20 points)
                desc_length = len(exp.description)
                if desc_length > 500:
                    exp_score += 20
                elif desc_length > 200:
                    exp_score += 15
                elif desc_length > 100:
                    exp_score += 10
                elif desc_length > 50:
                    exp_score += 5
                
                # Has bullet points (20 points)
                bullet_count = exp.description.count('•') + exp.description.count('-') + exp.description.count('*')
                if bullet_count >= 3:
                    exp_score += 20
                elif bullet_count >= 2:
                    exp_score += 15
                elif bullet_count >= 1:
                    exp_score += 10
                
                # Has quantifications (20 points)
                if QuantificationDetectorService.has_quantification(exp.description):
                    quant_count = len(QuantificationDetectorService.detect_quantifications(exp.description))
                    exp_score += min(quant_count * 5, 20)
            
            total_score += exp_score
        
        # Average across all experiences
        avg_score = total_score / resume.experiences.count()
        
        return min(avg_score, 100.0)
    
    @staticmethod
    def calculate_quantification_score(resume) -> float:
        """
        Calculate quantification score across all experiences.
        
        Args:
            resume: Resume model instance
            
        Returns:
            Score from 0-100 based on quantified achievements
        """
        experience_text = ScoringEngineService._get_experience_text(resume)
        
        if not experience_text:
            return 0.0
        
        return QuantificationDetectorService.calculate_quantification_score(experience_text)
    
    @staticmethod
    def calculate_action_verb_score(resume) -> float:
        """
        Calculate action verb strength score.
        
        Args:
            resume: Resume model instance
            
        Returns:
            Score from 0-100 based on action verb strength
        """
        experience_text = ScoringEngineService._get_experience_text(resume)
        
        if not experience_text:
            return 0.0
        
        return ActionVerbAnalyzerService.calculate_action_verb_score(experience_text)
    
    @staticmethod
    def _get_resume_text(resume) -> str:
        """Get all text content from resume."""
        text_parts = []
        
        # Personal info
        try:
            pi = resume.personal_info
            if pi:
                text_parts.extend([pi.full_name, pi.location])
        except:
            pass
        
        # Experiences
        for exp in resume.experiences.all():
            text_parts.extend([exp.company, exp.role, exp.description])
        
        # Education
        for edu in resume.education.all():
            text_parts.extend([edu.institution, edu.degree, edu.field])
        
        # Skills
        for skill in resume.skills.all():
            text_parts.append(skill.name)
        
        # Projects
        for proj in resume.projects.all():
            text_parts.extend([proj.name, proj.description, proj.technologies])
        
        return ' '.join([str(part) for part in text_parts if part])
    
    @staticmethod
    def _get_experience_text(resume) -> str:
        """Get text from experience descriptions only."""
        experiences = resume.experiences.all()
        return ' '.join([exp.description for exp in experiences if exp.description])
    
    @staticmethod
    def _identify_missing_quantifications(resume) -> list:
        """Identify bullet points that lack quantification."""
        missing = []
        
        for exp in resume.experiences.all():
            if not exp.description:
                continue
            
            # Split into bullet points
            lines = exp.description.split('\n')
            for i, line in enumerate(lines):
                line = line.strip()
                if line and len(line) > 20:  # Meaningful line
                    if not QuantificationDetectorService.has_quantification(line):
                        missing.append({
                            'company': exp.company,
                            'role': exp.role,
                            'line_number': i + 1,
                            'text': line[:100]  # First 100 chars
                        })
        
        return missing[:10]  # Return top 10


class ATSAnalyzerService(ScoringEngineService):
    """
    Alias for ScoringEngineService to maintain backward compatibility.
    This is the main service class that should be imported.
    """
    
    @staticmethod
    def analyze_resume(resume_id: int, job_description: str) -> dict:
        """
        Main analysis function to compare resume against job description.
        
        Performs complete ATS analysis workflow:
        1. Aggregate all resume text
        2. Extract keywords from resume
        3. Extract keywords from job description
        4. Calculate match score
        5. Generate improvement suggestions
        
        Args:
            resume_id: ID of the resume to analyze
            job_description: Job description text to compare against
            
        Returns:
            dict: {
                'score': float (0-100),
                'matched_keywords': list of matched keywords,
                'missing_keywords': list of missing keywords,
                'suggestions': list of suggestion strings
            }
            
        Raises:
            Resume.DoesNotExist: If resume_id is invalid
        """
        from apps.resumes.models import Resume
        
        # Load the resume with all related sections
        resume = Resume.objects.prefetch_related(
            'personal_info',
            'experiences',
            'education',
            'skills',
            'projects'
        ).get(id=resume_id)
        
        # Aggregate resume text
        resume_text = ScoringEngineService._get_resume_text(resume)
        
        # Extract keywords from resume
        resume_keywords = KeywordExtractorService.extract_keywords(resume_text)
        
        # Extract keywords from job description
        jd_keywords = KeywordExtractorService.extract_keywords(job_description)
        
        # Calculate match score
        matched_keywords = list(resume_keywords & jd_keywords)
        missing_keywords = list(jd_keywords - resume_keywords)
        
        if len(jd_keywords) == 0:
            score = 0.0
        else:
            score = (len(matched_keywords) / len(jd_keywords)) * 100
        
        # Generate suggestions
        suggestions = []
        
        if not missing_keywords:
            suggestions.append("Great! Your resume contains all the key terms from the job description.")
        else:
            suggestions.append(
                f"Your resume is missing {len(missing_keywords)} keywords from the job description. "
                "Consider incorporating these terms naturally into your resume:"
            )
            
            keyword_list = ', '.join(missing_keywords[:10])
            if len(missing_keywords) > 10:
                keyword_list += f", and {len(missing_keywords) - 10} more"
            
            suggestions.append(f"Missing keywords: {keyword_list}")
            suggestions.append("Tips for improvement:")
            suggestions.append("- Add relevant missing keywords to your work experience descriptions")
            suggestions.append("- Include missing technical skills in your Skills section")
            suggestions.append("- Incorporate missing terms into your project descriptions")
            suggestions.append("- Ensure your resume uses the same terminology as the job description")
        
        # Return complete analysis result
        return {
            'score': score,
            'matched_keywords': sorted(matched_keywords),
            'missing_keywords': sorted(missing_keywords),
            'suggestions': suggestions
        }
