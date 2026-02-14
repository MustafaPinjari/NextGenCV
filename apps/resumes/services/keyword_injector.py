# Keyword injection service
from typing import Dict, List, Set, Optional
import random
from apps.analyzer.services.keyword_extractor import KeywordExtractorService


class KeywordInjectorService:
    """
    Service for naturally injecting missing keywords into resume content.
    Prioritizes keywords by frequency and finds optimal injection points.
    """
    
    # Templates for natural keyword injection
    INJECTION_TEMPLATES = {
        'skill': [
            "Utilized {keyword} to enhance project outcomes",
            "Leveraged {keyword} for improved efficiency",
            "Applied {keyword} expertise to solve complex problems",
            "Demonstrated proficiency in {keyword}",
            "Expertise in {keyword} and related technologies",
        ],
        'technology': [
            "Implemented {keyword}-based solutions",
            "Developed applications using {keyword}",
            "Worked extensively with {keyword}",
            "Built systems leveraging {keyword}",
            "Integrated {keyword} into existing infrastructure",
        ],
        'methodology': [
            "Followed {keyword} best practices",
            "Applied {keyword} principles throughout development",
            "Utilized {keyword} methodology for project delivery",
            "Implemented {keyword} framework",
            "Adopted {keyword} approach for optimal results",
        ],
        'tool': [
            "Used {keyword} for project management",
            "Leveraged {keyword} to streamline workflows",
            "Utilized {keyword} for enhanced productivity",
            "Implemented {keyword} for better collaboration",
            "Adopted {keyword} for improved efficiency",
        ],
        'general': [
            "Experience with {keyword}",
            "Proficient in {keyword}",
            "Skilled in {keyword}",
            "Knowledge of {keyword}",
            "Familiar with {keyword}",
        ]
    }
    
    @staticmethod
    def inject_keywords(resume, missing_keywords: Set[str], job_description: str, max_keywords: int = 10) -> List[Dict]:
        """
        Inject missing keywords naturally into resume content.
        
        Args:
            resume: Resume model instance
            missing_keywords: Set of keywords to inject
            job_description: Job description text for context
            max_keywords: Maximum number of keywords to inject
            
        Returns:
            List of injection changes made
        """
        if not missing_keywords:
            return []
        
        # Prioritize keywords by frequency in job description
        keyword_freq = KeywordExtractorService.calculate_keyword_frequency(job_description)
        
        # Sort keywords by frequency (descending)
        sorted_keywords = sorted(
            missing_keywords,
            key=lambda k: keyword_freq.get(k, 0),
            reverse=True
        )[:max_keywords]
        
        changes = []
        
        for keyword in sorted_keywords:
            # Find best injection point
            injection_point = KeywordInjectorService.find_best_injection_point(
                resume, keyword
            )
            
            if injection_point:
                # Generate natural injection text
                injected_text = KeywordInjectorService.inject_keyword_naturally(
                    injection_point['text'], keyword, injection_point['type']
                )
                
                changes.append({
                    'type': 'keyword_injection',
                    'keyword': keyword,
                    'frequency': keyword_freq.get(keyword, 0),
                    'location': injection_point['section'],
                    'field': injection_point['field'],
                    'old_text': injection_point['text'],
                    'new_text': injected_text,
                    'injection_type': injection_point['type']
                })
        
        return changes
    
    @staticmethod
    def find_best_injection_point(resume, keyword: str) -> Optional[Dict]:
        """
        Find the best location to inject a keyword.
        
        Args:
            resume: Resume model instance
            keyword: Keyword to inject
            
        Returns:
            Dictionary with injection point details or None
        """
        # Priority order: Skills > Experience > Projects > Education
        
        # 1. Try Skills section (best for technical keywords)
        if resume.skills.exists():
            # Check if we can add to existing skills or create new skill
            return {
                'section': 'skills',
                'field': 'name',
                'text': '',  # Will create new skill
                'type': 'skill',
                'model': 'Skill'
            }
        
        # 2. Try Experience descriptions
        experiences = resume.experiences.all()
        if experiences:
            # Find experience with shortest description (most room for improvement)
            best_exp = None
            min_length = float('inf')
            
            for exp in experiences:
                if exp.description:
                    desc_length = len(exp.description)
                    if desc_length < min_length:
                        min_length = desc_length
                        best_exp = exp
            
            if best_exp:
                return {
                    'section': 'experience',
                    'field': 'description',
                    'text': best_exp.description or '',
                    'type': KeywordInjectorService._classify_keyword(keyword),
                    'model': 'Experience',
                    'model_id': best_exp.id
                }
        
        # 3. Try Projects
        projects = resume.projects.all()
        if projects:
            # Find project with shortest description
            best_proj = None
            min_length = float('inf')
            
            for proj in projects:
                if proj.description:
                    desc_length = len(proj.description)
                    if desc_length < min_length:
                        min_length = desc_length
                        best_proj = proj
            
            if best_proj:
                return {
                    'section': 'projects',
                    'field': 'description',
                    'text': best_proj.description or '',
                    'type': KeywordInjectorService._classify_keyword(keyword),
                    'model': 'Project',
                    'model_id': best_proj.id
                }
        
        # 4. Last resort: suggest adding to skills
        return {
            'section': 'skills',
            'field': 'name',
            'text': '',
            'type': 'skill',
            'model': 'Skill'
        }
    
    @staticmethod
    def inject_keyword_naturally(text: str, keyword: str, injection_type: str = 'general') -> str:
        """
        Inject keyword naturally into text using templates.
        
        Args:
            text: Original text
            keyword: Keyword to inject
            injection_type: Type of injection (skill, technology, etc.)
            
        Returns:
            Text with keyword injected naturally
        """
        # Get appropriate templates
        templates = KeywordInjectorService.INJECTION_TEMPLATES.get(
            injection_type,
            KeywordInjectorService.INJECTION_TEMPLATES['general']
        )
        
        # Select random template
        template = random.choice(templates)
        injected_phrase = template.format(keyword=keyword)
        
        # If text is empty, just return the injected phrase
        if not text or not text.strip():
            return injected_phrase
        
        # If text exists, append as new bullet point or sentence
        # Check if text has bullet points
        if '•' in text or '\n-' in text or '\n*' in text:
            # Add as new bullet point
            return f"{text}\n• {injected_phrase}"
        else:
            # Add as new sentence
            return f"{text}. {injected_phrase}"
    
    @staticmethod
    def _classify_keyword(keyword: str) -> str:
        """
        Classify keyword type for appropriate template selection.
        
        Args:
            keyword: Keyword to classify
            
        Returns:
            Classification type
        """
        keyword_lower = keyword.lower()
        
        # Technology keywords
        tech_indicators = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue',
            'node', 'django', 'flask', 'spring', 'sql', 'nosql',
            'mongodb', 'postgresql', 'mysql', 'redis', 'aws', 'azure',
            'docker', 'kubernetes', 'git', 'jenkins', 'ci/cd'
        ]
        if any(tech in keyword_lower for tech in tech_indicators):
            return 'technology'
        
        # Methodology keywords
        methodology_indicators = [
            'agile', 'scrum', 'kanban', 'waterfall', 'devops',
            'tdd', 'bdd', 'ci/cd', 'microservices', 'rest', 'api'
        ]
        if any(method in keyword_lower for method in methodology_indicators):
            return 'methodology'
        
        # Tool keywords
        tool_indicators = [
            'jira', 'confluence', 'slack', 'trello', 'asana',
            'github', 'gitlab', 'bitbucket', 'visual studio'
        ]
        if any(tool in keyword_lower for tool in tool_indicators):
            return 'tool'
        
        # Default to skill
        return 'skill'
    
    @staticmethod
    def calculate_keyword_priority(keywords: Set[str], job_description: str) -> List[tuple]:
        """
        Calculate priority scores for keywords based on job description frequency.
        
        Args:
            keywords: Set of keywords to prioritize
            job_description: Job description text
            
        Returns:
            List of (keyword, priority_score) tuples sorted by priority
        """
        keyword_freq = KeywordExtractorService.calculate_keyword_frequency(job_description)
        
        # Calculate priority scores
        priorities = []
        for keyword in keywords:
            freq = keyword_freq.get(keyword, 0)
            # Priority = frequency * keyword_length_factor
            # Longer keywords (more specific) get slight boost
            length_factor = min(len(keyword) / 10, 1.5)
            priority = freq * length_factor
            priorities.append((keyword, priority))
        
        # Sort by priority (descending)
        priorities.sort(key=lambda x: x[1], reverse=True)
        
        return priorities
