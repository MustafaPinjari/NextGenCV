"""
Celery tasks for async processing of heavy operations.

These tasks move blocking operations (PDF parsing, AI optimization, ATS scoring)
off the request thread so users get immediate responses with real-time progress.
"""
import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, name='resumes.parse_pdf', max_retries=2)
def parse_pdf_task(self, upload_id: int):
    """
    Parse an uploaded PDF in the background.
    Updates UploadedResume.status as it progresses.
    """
    from apps.resumes.models import UploadedResume
    from apps.resumes.services.pdf_parser import PDFParserService
    from apps.resumes.services.section_parser import SectionParserService

    try:
        upload = UploadedResume.objects.get(id=upload_id)
        upload.status = 'parsing'
        upload.save(update_fields=['status'])

        # Extract text
        with upload.file_path.open('rb') as f:
            raw_text = PDFParserService.extract_text_from_pdf(f)

        cleaned_text = PDFParserService.clean_extracted_text(raw_text)

        # Parse sections
        parsed_data = SectionParserService.parse_resume_sections(cleaned_text)
        confidence = PDFParserService.calculate_parsing_confidence(cleaned_text, parsed_data)

        upload.extracted_text = cleaned_text
        upload.parsed_data = parsed_data
        upload.parsing_confidence = confidence
        upload.status = 'parsed'
        upload.save(update_fields=['extracted_text', 'parsed_data', 'parsing_confidence', 'status'])

        logger.info(f"PDF parsed successfully: upload_id={upload_id}, confidence={confidence:.2f}")
        return {'status': 'parsed', 'upload_id': upload_id, 'confidence': confidence}

    except UploadedResume.DoesNotExist:
        logger.error(f"UploadedResume {upload_id} not found")
        return {'status': 'error', 'error': 'Upload not found'}
    except Exception as exc:
        logger.error(f"PDF parsing failed for upload {upload_id}: {exc}", exc_info=True)
        try:
            upload = UploadedResume.objects.get(id=upload_id)
            upload.status = 'failed'
            upload.error_message = str(exc)
            upload.save(update_fields=['status', 'error_message'])
        except Exception:
            pass
        raise self.retry(exc=exc, countdown=5)


@shared_task(bind=True, name='resumes.optimize_resume', max_retries=1)
def optimize_resume_task(self, resume_id: int, job_description: str, user_id: int):
    """
    Run AI-powered resume optimization in the background.
    Returns optimization changes that the user can accept/reject.
    """
    from apps.resumes.models import Resume, OptimizationHistory, ResumeVersion
    from apps.resumes.services.llm_service import LLMService
    from apps.resumes.services.keyword_injector import KeywordInjectorService
    from apps.analyzer.services.scoring_engine import ScoringEngineService
    from apps.analyzer.services.keyword_extractor import KeywordExtractorService

    try:
        resume = Resume.objects.prefetch_related(
            'personal_info', 'experiences', 'education', 'skills', 'projects'
        ).get(id=resume_id, user_id=user_id)

        # Score before optimization
        score_before = ScoringEngineService.calculate_ats_score(resume, job_description)

        # Get missing keywords
        resume_text = ScoringEngineService._get_resume_text(resume)
        resume_kw = KeywordExtractorService.extract_keywords(resume_text)
        jd_kw = KeywordExtractorService.extract_keywords(job_description)
        missing_kw = jd_kw - resume_kw

        changes = []

        # 1. Rewrite bullet points using LLM
        for exp in resume.experiences.all():
            if not exp.description:
                continue
            bullets = [
                line.strip().lstrip('•-* ')
                for line in exp.description.split('\n')
                if line.strip() and len(line.strip()) > 15
            ]
            if not bullets:
                continue

            rewrites = LLMService.rewrite_bullets_batch(bullets, job_description, exp.role)
            for rewrite in rewrites:
                if rewrite['changed']:
                    changes.append({
                        'type': 'bullet_rewrite',
                        'section': 'experience',
                        'model': 'Experience',
                        'model_id': exp.id,
                        'field': 'description',
                        'old_text': rewrite['original'],
                        'new_text': rewrite['rewritten'],
                        'reason': rewrite['reason'],
                        'ai_powered': rewrite.get('ai_powered', False),
                    })

        # 2. Keyword injection
        kw_changes = KeywordInjectorService.inject_keywords(
            resume, missing_kw, job_description, max_keywords=8
        )
        for kw_change in kw_changes:
            kw_change['ai_powered'] = False
        changes.extend(kw_changes)

        # Save optimization history
        version = resume.versions.order_by('-version_number').first()
        history = OptimizationHistory.objects.create(
            resume=resume,
            original_version=version,
            job_description=job_description,
            original_score=score_before['final_score'],
            changes_summary={
                'bullet_rewrites': sum(1 for c in changes if c['type'] == 'bullet_rewrite'),
                'keyword_injections': sum(1 for c in changes if c['type'] == 'keyword_injection'),
            },
            detailed_changes=changes,
        )

        resume.last_optimized_at = timezone.now()
        resume.save(update_fields=['last_optimized_at'])

        logger.info(f"Optimization complete: resume_id={resume_id}, changes={len(changes)}")
        return {
            'status': 'complete',
            'optimization_id': history.id,
            'changes_count': len(changes),
            'score_before': score_before['final_score'],
        }

    except Resume.DoesNotExist:
        return {'status': 'error', 'error': 'Resume not found'}
    except Exception as exc:
        logger.error(f"Optimization failed for resume {resume_id}: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=10)


@shared_task(bind=True, name='resumes.analyse_ats', max_retries=1)
def analyse_ats_task(self, resume_id: int, job_description: str, user_id: int):
    """
    Run full ATS analysis in the background.
    """
    from apps.resumes.models import Resume, ResumeAnalysis
    from apps.analyzer.services.scoring_engine import ScoringEngineService
    from apps.resumes.services.llm_service import LLMService

    try:
        resume = Resume.objects.prefetch_related(
            'personal_info', 'experiences', 'education', 'skills', 'projects'
        ).get(id=resume_id, user_id=user_id)

        score_data = ScoringEngineService.calculate_ats_score(resume, job_description)

        # Generate AI explanation
        explanation = LLMService.explain_ats_score(score_data, resume.title)

        # Save analysis
        analysis = ResumeAnalysis.objects.create(
            resume=resume,
            job_description=job_description,
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

        logger.info(f"ATS analysis complete: resume_id={resume_id}, score={score_data['final_score']:.1f}")
        return {
            'status': 'complete',
            'analysis_id': analysis.id,
            'score': score_data['final_score'],
        }

    except Resume.DoesNotExist:
        return {'status': 'error', 'error': 'Resume not found'}
    except Exception as exc:
        logger.error(f"ATS analysis failed for resume {resume_id}: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=5)


@shared_task(name='resumes.send_verification_email')
def send_verification_email_task(user_id: int, token: str, base_url: str):
    """Send email verification link to a newly registered user."""
    from django.contrib.auth.models import User
    from django.core.mail import send_mail
    from django.conf import settings

    try:
        user = User.objects.get(id=user_id)
        verify_url = f"{base_url}/auth/verify-email/{token}/"
        send_mail(
            subject='Verify your NextGenCV email address',
            message=(
                f"Hi {user.username},\n\n"
                f"Please verify your email address by clicking the link below:\n\n"
                f"{verify_url}\n\n"
                f"This link expires in 48 hours.\n\n"
                f"If you didn't create an account, you can ignore this email.\n\n"
                f"— The NextGenCV Team"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f"Verification email sent to {user.email}")
    except Exception as e:
        logger.error(f"Failed to send verification email to user {user_id}: {e}")
