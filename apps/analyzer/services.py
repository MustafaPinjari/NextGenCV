"""
ATS Analyzer Service

This module provides services for analyzing resumes against job descriptions
using keyword extraction and matching algorithms.
"""

import string
from typing import Set
from apps.resumes.models import Resume


class ATSAnalyzerService:
    """
    Service class for ATS (Applicant Tracking System) resume analysis.
    
    Provides methods for:
    - Aggregating resume text from all sections
    - Cleaning and preprocessing text
    - Extracting keywords
    - Calculating match scores
    - Generating improvement suggestions
    """
    
    # Common English stop words to filter out during keyword extraction
    STOP_WORDS = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
        'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have',
        'had', 'what', 'when', 'where', 'who', 'which', 'why', 'how', 'all',
        'each', 'she', 'do', 'does', 'did', 'doing', 'would', 'could', 'should',
        'may', 'might', 'must', 'can', 'or', 'if', 'than', 'then', 'so',
        'no', 'not', 'only', 'own', 'same', 'such', 'too', 'very', 'just',
        'about', 'into', 'through', 'during', 'before', 'after', 'above',
        'below', 'up', 'down', 'out', 'off', 'over', 'under', 'again',
        'further', 'once', 'here', 'there', 'all', 'both', 'few', 'more',
        'most', 'other', 'some', 'any', 'been', 'being', 'am', 'were'
    }
    
    @staticmethod
    def aggregate_resume_text(resume) -> str:
        """
        Aggregate all text content from a resume into a single string.
        
        Concatenates content from:
        - Personal information (name, location)
        - All work experiences (company, role, description)
        - All education entries (institution, degree, field)
        - All skills (name)
        - All projects (name, description, technologies)
        
        Args:
            resume: Resume model instance with related sections
            
        Returns:
            str: Concatenated text from all resume sections with spacing
            
        Validates: Requirements 17.1, 17.2, 17.3, 17.4, 17.5, 17.6
        """
        text_parts = []
        
        # Personal information
        try:
            personal_info = resume.personal_info
            text_parts.append(personal_info.full_name)
            text_parts.append(personal_info.location)
            if personal_info.email:
                text_parts.append(personal_info.email)
        except Exception:
            # Personal info might not exist
            pass
        
        # Work experiences
        for experience in resume.experiences.all():
            text_parts.append(experience.company)
            text_parts.append(experience.role)
            text_parts.append(experience.description)
        
        # Education
        for education in resume.education.all():
            text_parts.append(education.institution)
            text_parts.append(education.degree)
            text_parts.append(education.field)
        
        # Skills
        for skill in resume.skills.all():
            text_parts.append(skill.name)
        
        # Projects
        for project in resume.projects.all():
            text_parts.append(project.name)
            text_parts.append(project.description)
            text_parts.append(project.technologies)
        
        # Join all parts with spaces
        return ' '.join(text_parts)
    
    @staticmethod
    def clean_text(text: str) -> list:
        """
        Clean and preprocess text for keyword extraction.
        
        Processing steps:
        1. Convert to lowercase
        2. Remove punctuation
        3. Tokenize by whitespace
        
        Args:
            text: Raw text string to clean
            
        Returns:
            list: List of cleaned tokens
            
        Validates: Requirements 10.1, 10.3
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation
        translator = str.maketrans('', '', string.punctuation)
        text = text.translate(translator)
        
        # Tokenize by whitespace
        tokens = text.split()
        
        return tokens
    
    @staticmethod
    def extract_keywords(text: str) -> Set[str]:
        """
        Extract meaningful keywords from text.
        
        Processing steps:
        1. Clean text (lowercase, remove punctuation, tokenize)
        2. Remove stop words
        3. Filter words with length < 3
        4. Return unique keywords as a set
        
        Args:
            text: Raw text string to extract keywords from
            
        Returns:
            Set[str]: Set of unique keywords
            
        Validates: Requirements 9.2, 10.1, 10.2, 10.3
        """
        # Clean the text
        tokens = ATSAnalyzerService.clean_text(text)
        
        # Remove stop words and filter by length
        keywords = {
            token for token in tokens
            if token not in ATSAnalyzerService.STOP_WORDS and len(token) >= 3
        }
        
        return keywords
    
    @staticmethod
    def calculate_match_score(resume_keywords: Set[str], jd_keywords: Set[str]) -> dict:
        """
        Calculate match score between resume and job description keywords.
        
        Calculates:
        - matched_keywords: Keywords present in both resume and job description
        - missing_keywords: Keywords in job description but not in resume
        - score: Percentage match (matched / total_jd_keywords * 100)
        
        Args:
            resume_keywords: Set of keywords extracted from resume
            jd_keywords: Set of keywords extracted from job description
            
        Returns:
            dict: {
                'score': float (0-100),
                'matched_keywords': list of matched keywords,
                'missing_keywords': list of missing keywords
            }
            
        Validates: Requirements 9.3, 9.4, 9.5, 10.4, 10.5
        """
        # Calculate matched keywords (intersection)
        matched_keywords = resume_keywords & jd_keywords
        
        # Calculate missing keywords (difference)
        missing_keywords = jd_keywords - resume_keywords
        
        # Calculate score
        if len(jd_keywords) == 0:
            score = 0.0
        else:
            score = (len(matched_keywords) / len(jd_keywords)) * 100
        
        return {
            'score': score,
            'matched_keywords': sorted(list(matched_keywords)),
            'missing_keywords': sorted(list(missing_keywords))
        }
    
    @staticmethod
    def generate_suggestions(missing_keywords: list) -> list:
        """
        Generate actionable suggestions based on missing keywords.
        
        Creates suggestions for adding missing keywords to relevant resume sections.
        Provides specific guidance on where to incorporate keywords.
        
        Args:
            missing_keywords: List of keywords present in job description but not in resume
            
        Returns:
            list: List of suggestion strings
            
        Validates: Requirements 9.6
        """
        suggestions = []
        
        if not missing_keywords:
            suggestions.append("Great! Your resume contains all the key terms from the job description.")
            return suggestions
        
        # General suggestion
        suggestions.append(
            f"Your resume is missing {len(missing_keywords)} keywords from the job description. "
            "Consider incorporating these terms naturally into your resume:"
        )
        
        # Categorize keywords and provide specific suggestions
        # For simplicity, we'll provide general guidance
        keyword_list = ', '.join(missing_keywords[:10])  # Show first 10
        if len(missing_keywords) > 10:
            keyword_list += f", and {len(missing_keywords) - 10} more"
        
        suggestions.append(f"Missing keywords: {keyword_list}")
        
        # Provide actionable advice
        suggestions.append(
            "Tips for improvement:"
        )
        suggestions.append(
            "- Add relevant missing keywords to your work experience descriptions"
        )
        suggestions.append(
            "- Include missing technical skills in your Skills section"
        )
        suggestions.append(
            "- Incorporate missing terms into your project descriptions"
        )
        suggestions.append(
            "- Ensure your resume uses the same terminology as the job description"
        )
        
        return suggestions
    
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
            
        Validates: Requirements 9.2, 9.3, 9.4, 9.5, 9.6
        """
        # Load the resume with all related sections
        resume = Resume.objects.prefetch_related(
            'personal_info',
            'experiences',
            'education',
            'skills',
            'projects'
        ).get(id=resume_id)
        
        # Aggregate resume text
        resume_text = ATSAnalyzerService.aggregate_resume_text(resume)
        
        # Extract keywords from resume
        resume_keywords = ATSAnalyzerService.extract_keywords(resume_text)
        
        # Extract keywords from job description
        jd_keywords = ATSAnalyzerService.extract_keywords(job_description)
        
        # Calculate match score
        match_result = ATSAnalyzerService.calculate_match_score(resume_keywords, jd_keywords)
        
        # Generate suggestions
        suggestions = ATSAnalyzerService.generate_suggestions(match_result['missing_keywords'])
        
        # Return complete analysis result
        return {
            'score': match_result['score'],
            'matched_keywords': match_result['matched_keywords'],
            'missing_keywords': match_result['missing_keywords'],
            'suggestions': suggestions
        }
