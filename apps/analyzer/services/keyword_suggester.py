"""
Keyword suggestion service for resume optimization.
Provides industry-specific keyword recommendations.
"""
from typing import Dict, List, Set
from .keyword_extractor import KeywordExtractorService


class KeywordSuggesterService:
    """
    Service for suggesting relevant keywords based on industry and role.
    """
    
    # Industry-specific keyword database
    INDUSTRY_KEYWORDS = {
        'software_engineering': {
            'technical': [
                'Python', 'Java', 'JavaScript', 'TypeScript', 'React', 'Angular', 'Vue',
                'Node.js', 'Django', 'Flask', 'Spring Boot', 'Docker', 'Kubernetes',
                'AWS', 'Azure', 'GCP', 'CI/CD', 'Git', 'Agile', 'Scrum', 'REST API',
                'GraphQL', 'SQL', 'NoSQL', 'MongoDB', 'PostgreSQL', 'Redis',
                'Microservices', 'DevOps', 'TDD', 'Unit Testing', 'Integration Testing'
            ],
            'soft_skills': [
                'Problem Solving', 'Team Collaboration', 'Code Review', 'Mentoring',
                'Technical Documentation', 'Cross-functional Communication',
                'Project Planning', 'Debugging', 'Performance Optimization'
            ],
            'certifications': [
                'AWS Certified', 'Azure Certified', 'Google Cloud Certified',
                'Certified Scrum Master', 'PMP'
            ]
        },
        'data_science': {
            'technical': [
                'Python', 'R', 'SQL', 'Machine Learning', 'Deep Learning', 'TensorFlow',
                'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy', 'Data Visualization',
                'Tableau', 'Power BI', 'Statistical Analysis', 'A/B Testing',
                'Natural Language Processing', 'Computer Vision', 'Big Data', 'Spark',
                'Hadoop', 'Data Mining', 'Predictive Modeling', 'Feature Engineering'
            ],
            'soft_skills': [
                'Data Storytelling', 'Business Acumen', 'Stakeholder Communication',
                'Problem Solving', 'Critical Thinking', 'Research', 'Presentation'
            ],
            'certifications': [
                'AWS Machine Learning', 'Google Data Analytics', 'Microsoft Data Scientist',
                'Certified Analytics Professional'
            ]
        },
        'product_management': {
            'technical': [
                'Product Strategy', 'Roadmap Planning', 'User Research', 'A/B Testing',
                'Analytics', 'SQL', 'Jira', 'Confluence', 'Agile', 'Scrum', 'Kanban',
                'Product Metrics', 'KPIs', 'OKRs', 'User Stories', 'Wireframing',
                'Prototyping', 'Market Research', 'Competitive Analysis'
            ],
            'soft_skills': [
                'Stakeholder Management', 'Cross-functional Leadership', 'Communication',
                'Prioritization', 'Decision Making', 'Negotiation', 'Presentation',
                'Strategic Thinking', 'Customer Empathy'
            ],
            'certifications': [
                'Certified Scrum Product Owner', 'Product Management Certificate',
                'Pragmatic Marketing Certified'
            ]
        },
        'marketing': {
            'technical': [
                'SEO', 'SEM', 'Google Analytics', 'Google Ads', 'Facebook Ads',
                'Content Marketing', 'Email Marketing', 'Social Media Marketing',
                'Marketing Automation', 'HubSpot', 'Salesforce', 'CRM', 'A/B Testing',
                'Conversion Optimization', 'Brand Strategy', 'Campaign Management',
                'Market Research', 'Customer Segmentation'
            ],
            'soft_skills': [
                'Creative Thinking', 'Storytelling', 'Communication', 'Project Management',
                'Data Analysis', 'Collaboration', 'Presentation', 'Negotiation'
            ],
            'certifications': [
                'Google Analytics Certified', 'HubSpot Certified', 'Facebook Blueprint',
                'Hootsuite Certified'
            ]
        },
        'general': {
            'technical': [
                'Microsoft Office', 'Excel', 'PowerPoint', 'Project Management',
                'Data Analysis', 'Reporting', 'Documentation', 'Process Improvement',
                'Quality Assurance', 'Customer Service'
            ],
            'soft_skills': [
                'Communication', 'Leadership', 'Team Collaboration', 'Problem Solving',
                'Time Management', 'Adaptability', 'Critical Thinking', 'Attention to Detail',
                'Organization', 'Multitasking', 'Initiative', 'Reliability'
            ],
            'certifications': [
                'PMP', 'Six Sigma', 'Lean Certification', 'ITIL'
            ]
        }
    }
    
    @staticmethod
    def extract_industry_and_role(resume) -> Dict[str, str]:
        """
        Extract industry and role from resume content.
        
        Args:
            resume: Resume model instance
            
        Returns:
            Dict with 'industry' and 'role' keys
        """
        # Get all text from resume
        text_parts = []
        
        # Get experiences
        for exp in resume.experiences.all():
            if exp.role:
                text_parts.append(exp.role.lower())
            if exp.description:
                text_parts.append(exp.description.lower())
        
        # Get skills
        for skill in resume.skills.all():
            text_parts.append(skill.name.lower())
        
        combined_text = ' '.join(text_parts)
        
        # Detect industry based on keywords
        industry = 'general'
        
        # Software Engineering indicators
        if any(keyword in combined_text for keyword in ['software', 'developer', 'engineer', 'programming', 'python', 'java', 'javascript']):
            industry = 'software_engineering'
        # Data Science indicators
        elif any(keyword in combined_text for keyword in ['data scientist', 'machine learning', 'data analyst', 'analytics', 'ml engineer']):
            industry = 'data_science'
        # Product Management indicators
        elif any(keyword in combined_text for keyword in ['product manager', 'product owner', 'product lead', 'roadmap']):
            industry = 'product_management'
        # Marketing indicators
        elif any(keyword in combined_text for keyword in ['marketing', 'seo', 'social media', 'content', 'brand', 'campaign']):
            industry = 'marketing'
        
        # Extract role from most recent experience
        role = 'general'
        if resume.experiences.exists():
            latest_exp = resume.experiences.first()
            role = latest_exp.role if latest_exp.role else 'general'
        
        return {
            'industry': industry,
            'role': role
        }
    
    @staticmethod
    def suggest_keywords(resume, job_description: str, max_suggestions: int = 15) -> List[Dict]:
        """
        Suggest relevant keywords for a resume based on industry and job description.
        
        Args:
            resume: Resume model instance
            job_description: Job description text
            max_suggestions: Maximum number of suggestions to return
            
        Returns:
            List of keyword suggestion dicts with:
                - keyword: The keyword
                - category: technical/soft_skills/certifications
                - relevance_score: 0-100
                - in_job_description: boolean
                - placement_suggestion: where to add it
        """
        # Extract industry and role
        industry_info = KeywordSuggesterService.extract_industry_and_role(resume)
        industry = industry_info['industry']
        
        # Get industry-specific keywords
        industry_keywords = KeywordSuggesterService.INDUSTRY_KEYWORDS.get(
            industry, 
            KeywordSuggesterService.INDUSTRY_KEYWORDS['general']
        )
        
        # Get current resume keywords
        resume_text = KeywordSuggesterService._get_resume_text(resume)
        resume_keywords = KeywordExtractorService.extract_keywords(resume_text)
        resume_keywords_lower = {kw.lower() for kw in resume_keywords}
        
        # Get job description keywords
        jd_keywords = KeywordExtractorService.extract_keywords(job_description)
        jd_keywords_lower = {kw.lower() for kw in jd_keywords}
        
        # Generate suggestions
        suggestions = []
        
        for category, keywords in industry_keywords.items():
            for keyword in keywords:
                keyword_lower = keyword.lower()
                
                # Skip if already in resume
                if keyword_lower in resume_keywords_lower:
                    continue
                
                # Calculate relevance score
                in_jd = keyword_lower in jd_keywords_lower
                relevance_score = 100 if in_jd else 50
                
                # Determine placement
                if category == 'technical':
                    placement = 'skills'
                elif category == 'soft_skills':
                    placement = 'experience'
                else:  # certifications
                    placement = 'education'
                
                suggestions.append({
                    'keyword': keyword,
                    'category': category,
                    'relevance_score': relevance_score,
                    'in_job_description': in_jd,
                    'placement_suggestion': placement,
                    'example_usage': KeywordSuggesterService._generate_example_usage(
                        keyword, category, placement
                    )
                })
        
        # Sort by relevance score (highest first)
        suggestions.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Return top N suggestions
        return suggestions[:max_suggestions]
    
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
    def _generate_example_usage(keyword: str, category: str, placement: str) -> str:
        """Generate example usage for a keyword."""
        if category == 'technical':
            if placement == 'skills':
                return f"Add '{keyword}' to your Skills section"
            else:
                return f"Utilized {keyword} to improve system performance"
        elif category == 'soft_skills':
            return f"Demonstrated {keyword} by leading cross-functional initiatives"
        else:  # certifications
            return f"Add '{keyword}' to your Education or Certifications section"
