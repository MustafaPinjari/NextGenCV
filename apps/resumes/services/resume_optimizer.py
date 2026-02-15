# Resume optimization orchestrator service
from typing import Dict, List, Set
from .bullet_point_rewriter import BulletPointRewriterService
from .keyword_injector import KeywordInjectorService
from .quantification_suggester import QuantificationSuggesterService
from .formatting_standardizer import FormattingStandardizerService
from apps.analyzer.services.keyword_extractor import KeywordExtractorService
from apps.analyzer.services.scoring_engine import ScoringEngineService


class ResumeOptimizerService:
    """
    Orchestrator service for comprehensive resume optimization.
    Coordinates all optimization sub-services to improve resume ATS compatibility.
    """
    
    @staticmethod
    def optimize_resume(resume, job_description: str, options: Dict = None) -> Dict:
        """
        Run full optimization pipeline on a resume.
        
        Args:
            resume: Resume model instance
            job_description: Job description text for context
            options: Optional configuration for optimization
                - rewrite_bullets: bool (default True)
                - inject_keywords: bool (default True)
                - suggest_quantifications: bool (default True)
                - standardize_formatting: bool (default True)
                - max_keywords: int (default 10)
                
        Returns:
            Dictionary containing:
                - original_score: Original ATS score
                - optimized_score: Projected optimized score
                - improvement_delta: Score improvement
                - detailed_changes: List of all changes by category
                - changes_summary: Summary counts by type
                - optimized_data: Optimized resume data structure
        """
        if options is None:
            options = {}
        
        # Default options
        rewrite_bullets = options.get('rewrite_bullets', True)
        inject_keywords = options.get('inject_keywords', True)
        suggest_quantifications = options.get('suggest_quantifications', True)
        standardize_formatting = options.get('standardize_formatting', True)
        max_keywords = options.get('max_keywords', 10)
        
        # Calculate original score
        original_analysis = ScoringEngineService.calculate_ats_score(resume, job_description)
        original_score = original_analysis['final_score']
        
        # Initialize changes tracking
        detailed_changes = []
        changes_summary = {
            'bullet_rewrites': 0,
            'keyword_injections': 0,
            'quantification_suggestions': 0,
            'formatting_fixes': 0,
            'total_changes': 0
        }
        
        # 1. Rewrite bullet points with strong action verbs
        if rewrite_bullets:
            bullet_changes = ResumeOptimizerService._optimize_bullet_points(
                resume, job_description
            )
            detailed_changes.extend(bullet_changes)
            changes_summary['bullet_rewrites'] = len(bullet_changes)
        
        # 2. Inject missing keywords
        if inject_keywords:
            # Get missing keywords from original analysis
            resume_text = ResumeOptimizerService._get_resume_text(resume)
            resume_keywords = KeywordExtractorService.extract_keywords(resume_text)
            jd_keywords = KeywordExtractorService.extract_keywords(job_description)
            missing_keywords = jd_keywords - resume_keywords
            
            keyword_changes = KeywordInjectorService.inject_keywords(
                resume, missing_keywords, job_description, max_keywords
            )
            detailed_changes.extend(keyword_changes)
            changes_summary['keyword_injections'] = len(keyword_changes)
        
        # 3. Suggest quantifications
        if suggest_quantifications:
            quant_changes = ResumeOptimizerService._suggest_quantifications(resume)
            detailed_changes.extend(quant_changes)
            changes_summary['quantification_suggestions'] = len(quant_changes)
        
        # 4. Standardize formatting
        if standardize_formatting:
            format_changes = ResumeOptimizerService._standardize_formatting(resume)
            detailed_changes.extend(format_changes)
            changes_summary['formatting_fixes'] = len(format_changes)
        
        # Calculate total changes
        changes_summary['total_changes'] = sum([
            changes_summary['bullet_rewrites'],
            changes_summary['keyword_injections'],
            changes_summary['quantification_suggestions'],
            changes_summary['formatting_fixes']
        ])
        
        # Generate optimized data structure
        optimized_data = ResumeOptimizerService._generate_optimized_data(
            resume, detailed_changes
        )
        
        # Estimate optimized score (heuristic-based)
        optimized_score = ResumeOptimizerService._estimate_optimized_score(
            original_score, changes_summary, original_analysis
        )
        
        improvement_delta = optimized_score - original_score
        
        return {
            'original_score': round(original_score, 2),
            'optimized_score': round(optimized_score, 2),
            'improvement_delta': round(improvement_delta, 2),
            'detailed_changes': detailed_changes,
            'changes_summary': changes_summary,
            'optimized_data': optimized_data,
            'original_analysis': original_analysis
        }
    
    @staticmethod
    def _optimize_bullet_points(resume, job_description: str) -> List[Dict]:
        """
        Optimize bullet points in experience descriptions.
        
        Args:
            resume: Resume model instance
            job_description: Job description for context
            
        Returns:
            List of bullet point changes
        """
        changes = []
        
        for experience in resume.experiences.all():
            if not experience.description:
                continue
            
            # Split description into bullet points
            lines = experience.description.split('\n')
            bullets = [line.strip() for line in lines if line.strip()]
            
            # Rewrite each bullet
            for i, bullet in enumerate(bullets):
                result = BulletPointRewriterService.rewrite_bullet_point(
                    bullet, job_description
                )
                
                if result['changed']:
                    changes.append({
                        'type': 'bullet_rewrite',
                        'section': 'experience',
                        'company': experience.company,
                        'role': experience.role,
                        'bullet_index': i,
                        'old_text': result['original'],
                        'new_text': result['rewritten'],
                        'reason': result['reason']
                    })
        
        return changes
    
    @staticmethod
    def _suggest_quantifications(resume) -> List[Dict]:
        """
        Suggest quantifications for achievements lacking metrics.
        
        Args:
            resume: Resume model instance
            
        Returns:
            List of quantification suggestions
        """
        changes = []
        
        for experience in resume.experiences.all():
            if not experience.description:
                continue
            
            # Analyze quantification coverage
            analysis = QuantificationSuggesterService.analyze_experience_quantification(
                experience.description
            )
            
            # Add suggestions for unquantified bullets
            for suggestion in analysis['suggestions']:
                changes.append({
                    'type': 'quantification_suggestion',
                    'section': 'experience',
                    'company': experience.company,
                    'role': experience.role,
                    'old_text': suggestion['original'],
                    'suggested_text': suggestion['example'],
                    'achievement_type': suggestion['achievement_type'],
                    'metric_options': suggestion['suggestions']
                })
        
        return changes
    
    @staticmethod
    def _standardize_formatting(resume) -> List[Dict]:
        """
        Standardize formatting across resume sections.
        
        Args:
            resume: Resume model instance
            
        Returns:
            List of formatting changes
        """
        changes = []
        
        # Standardize experience descriptions
        for experience in resume.experiences.all():
            if experience.description:
                result = FormattingStandardizerService.standardize_all(
                    experience.description
                )
                
                if result['all_changes']:
                    changes.append({
                        'type': 'formatting_standardization',
                        'section': 'experience',
                        'company': experience.company,
                        'role': experience.role,
                        'field': 'description',
                        'old_text': result['original'],
                        'new_text': result['standardized'],
                        'specific_changes': result['all_changes']
                    })
        
        # Standardize project descriptions
        for project in resume.projects.all():
            if project.description:
                result = FormattingStandardizerService.standardize_all(
                    project.description
                )
                
                if result['all_changes']:
                    changes.append({
                        'type': 'formatting_standardization',
                        'section': 'projects',
                        'project_name': project.name,
                        'field': 'description',
                        'old_text': result['original'],
                        'new_text': result['standardized'],
                        'specific_changes': result['all_changes']
                    })
        
        return changes
    
    @staticmethod
    def _generate_optimized_data(resume, detailed_changes: List[Dict]) -> Dict:
        """
        Generate optimized resume data structure with all changes applied.
        
        Args:
            resume: Resume model instance
            detailed_changes: List of all changes to apply
            
        Returns:
            Dictionary with optimized resume data
        """
        # Create a copy of resume data
        optimized = {
            'personal_info': {},
            'experiences': [],
            'education': [],
            'skills': [],
            'projects': []
        }
        
        # Copy personal info
        try:
            pi = resume.personal_info
            if pi:
                optimized['personal_info'] = {
                    'full_name': pi.full_name,
                    'email': pi.email,
                    'phone': pi.phone,
                    'location': pi.location
                }
        except:
            pass
        
        # Copy and apply changes to experiences
        for exp in resume.experiences.all():
            exp_data = {
                'company': exp.company,
                'role': exp.role,
                'start_date': str(exp.start_date) if exp.start_date else None,
                'end_date': str(exp.end_date) if exp.end_date else None,
                'description': exp.description
            }
            
            # Apply changes for this experience
            for change in detailed_changes:
                if (change.get('section') == 'experience' and 
                    change.get('company') == exp.company and
                    change.get('role') == exp.role):
                    
                    if change['type'] == 'bullet_rewrite':
                        # Replace bullet in description
                        if exp_data['description']:
                            exp_data['description'] = exp_data['description'].replace(
                                change['old_text'],
                                change['new_text']
                            )
                    
                    elif change['type'] == 'formatting_standardization':
                        exp_data['description'] = change['new_text']
            
            optimized['experiences'].append(exp_data)
        
        # Copy education
        for edu in resume.education.all():
            optimized['education'].append({
                'institution': edu.institution,
                'degree': edu.degree,
                'field': edu.field,
                'start_year': edu.start_year,
                'end_year': edu.end_year
            })
        
        # Copy and potentially add skills
        for skill in resume.skills.all():
            optimized['skills'].append({
                'name': skill.name,
                'category': skill.category
            })
        
        # Add injected keywords as new skills
        for change in detailed_changes:
            if change['type'] == 'keyword_injection' and change.get('location') == 'skills':
                optimized['skills'].append({
                    'name': change['keyword'],
                    'category': 'Technical'  # Default category
                })
        
        # Copy and apply changes to projects
        for proj in resume.projects.all():
            proj_data = {
                'name': proj.name,
                'description': proj.description,
                'technologies': proj.technologies,
                'url': proj.url
            }
            
            # Apply formatting changes
            for change in detailed_changes:
                if (change.get('section') == 'projects' and 
                    change.get('project_name') == proj.name and
                    change['type'] == 'formatting_standardization'):
                    proj_data['description'] = change['new_text']
            
            optimized['projects'].append(proj_data)
        
        return optimized
    
    @staticmethod
    def _estimate_optimized_score(original_score: float, changes_summary: Dict, 
                                   original_analysis: Dict) -> float:
        """
        Estimate optimized ATS score based on changes made.
        
        Args:
            original_score: Original ATS score
            changes_summary: Summary of changes by type
            original_analysis: Original score analysis
            
        Returns:
            Estimated optimized score
        """
        # Start with original score
        estimated_score = original_score
        
        # Bullet rewrites improve action verb score
        if changes_summary['bullet_rewrites'] > 0:
            # Estimate 5-15 point improvement in action verb component
            verb_improvement = min(changes_summary['bullet_rewrites'] * 3, 15)
            # Action verbs are 10% of total score
            estimated_score += verb_improvement * 0.10
        
        # Keyword injections improve keyword match score
        if changes_summary['keyword_injections'] > 0:
            # Estimate 10-30 point improvement in keyword component
            keyword_improvement = min(changes_summary['keyword_injections'] * 3, 30)
            # Keywords are 30% of total score
            estimated_score += keyword_improvement * 0.30
        
        # Quantification suggestions improve quantification score
        if changes_summary['quantification_suggestions'] > 0:
            # Estimate 10-20 point improvement in quantification component
            quant_improvement = min(changes_summary['quantification_suggestions'] * 2, 20)
            # Quantification is 10% of total score
            estimated_score += quant_improvement * 0.10
        
        # Formatting fixes improve overall score slightly
        if changes_summary['formatting_fixes'] > 0:
            # Small boost for ATS-friendly formatting
            estimated_score += 2
        
        # Cap at 100
        estimated_score = min(estimated_score, 100.0)
        
        return estimated_score
    
    @staticmethod
    def _get_resume_text(resume) -> str:
        """
        Get all text content from resume.
        
        Args:
            resume: Resume model instance
            
        Returns:
            Combined text from all resume sections
        """
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
