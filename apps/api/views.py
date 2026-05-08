"""
REST API Views for NextGenCV.

Endpoints:
  /api/v1/resumes/                    — list, create
  /api/v1/resumes/{id}/               — retrieve, update, delete
  /api/v1/resumes/{id}/analyse/       — trigger ATS analysis
  /api/v1/resumes/{id}/optimise/      — trigger AI optimisation
  /api/v1/resumes/{id}/ats-simulate/  — ATS system simulation
  /api/v1/resumes/{id}/versions/      — version history
  /api/v1/resumes/{id}/linkedin-import/ — import from LinkedIn
  /api/v1/applications/               — job applications CRUD
  /api/v1/applications/{id}/cover-letter/ — generate cover letter
  /api/v1/applications/{id}/interview-prep/ — generate interview questions
  /api/v1/applications/{id}/rejection-analysis/ — why was I rejected?
  /api/v1/outcomes/                   — outcome analytics
  /api/v1/me/                         — current user profile
"""
import logging
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle


class AIFeatureThrottle(UserRateThrottle):
    """20 AI calls per hour per user — prevents API key drain attacks."""
    scope = 'ai_features'

from apps.resumes.models import Resume, ResumeAnalysis, ResumeVersion
from apps.tracker.models import JobApplication, CoverLetter, InterviewPrepSession
from .serializers import (
    ResumeListSerializer, ResumeDetailSerializer, ResumeCreateSerializer,
    ResumeAnalysisSerializer, ResumeVersionSerializer,
    JobApplicationSerializer, CoverLetterSerializer, InterviewPrepSerializer,
    UserSerializer,
)

logger = logging.getLogger(__name__)


# ── Current User ──────────────────────────────────────────────────────────────

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def me(request):
    """Get or update the current user's profile."""
    if request.method == 'GET':
        return Response(UserSerializer(request.user).data)
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── Resumes ───────────────────────────────────────────────────────────────────

class ResumeViewSet(viewsets.ModelViewSet):
    """
    CRUD for resumes. All operations are scoped to the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user).prefetch_related(
            'personal_info', 'experiences', 'education', 'skills', 'projects', 'certifications'
        )

    def get_serializer_class(self):
        if self.action == 'list':
            return ResumeListSerializer
        if self.action == 'create':
            return ResumeCreateSerializer
        return ResumeDetailSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # ── ATS Analysis ──────────────────────────────────────────────────────────

    @action(detail=True, methods=['post'], url_path='analyse',
            throttle_classes=[AIFeatureThrottle])
    def analyse(self, request, pk=None):
        """
        Trigger ATS analysis for a resume.
        Runs synchronously if Celery is unavailable, async otherwise.

        Body: {job_description: str}
        """
        resume = self.get_object()
        job_description = request.data.get('job_description', '').strip()
        if not job_description:
            return Response(
                {'error': 'job_description is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from apps.resumes.tasks import analyse_ats_task
            task = analyse_ats_task.delay(resume.id, job_description, request.user.id)
            return Response({
                'task_id': task.id,
                'status': 'queued',
                'message': 'Analysis started. Poll /api/v1/tasks/{task_id}/ for results.',
            }, status=status.HTTP_202_ACCEPTED)
        except Exception:
            # Celery not available — run synchronously
            from apps.analyzer.services.scoring_engine import ScoringEngineService
            from apps.resumes.services.llm_service import LLMService
            from django.utils import timezone

            score_data = ScoringEngineService.calculate_ats_score(resume, job_description)
            explanation = LLMService.explain_ats_score(score_data, resume.title)

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

            return Response(ResumeAnalysisSerializer(analysis).data, status=status.HTTP_201_CREATED)

    # ── AI Optimisation ───────────────────────────────────────────────────────

    @action(detail=True, methods=['post'], url_path='optimise',
            throttle_classes=[AIFeatureThrottle])
    def optimise(self, request, pk=None):
        """
        Trigger AI-powered resume optimisation.

        Body: {job_description: str}
        """
        resume = self.get_object()
        job_description = request.data.get('job_description', '').strip()
        if not job_description:
            return Response(
                {'error': 'job_description is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from apps.resumes.tasks import optimize_resume_task
            task = optimize_resume_task.delay(resume.id, job_description, request.user.id)
            return Response({
                'task_id': task.id,
                'status': 'queued',
                'message': 'Optimisation started.',
            }, status=status.HTTP_202_ACCEPTED)
        except Exception:
            return Response(
                {'error': 'Async processing unavailable. Use the web interface for optimisation.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

    # ── ATS System Simulation ─────────────────────────────────────────────────

    @action(detail=True, methods=['post'], url_path='ats-simulate')
    def ats_simulate(self, request, pk=None):
        """
        Simulate how major ATS systems (Taleo, Workday, Greenhouse, Lever, iCIMS)
        would parse and score this resume.

        Body: {job_description: str}
        """
        resume = self.get_object()
        job_description = request.data.get('job_description', '')

        from apps.analyzer.services.ats_simulator import ATSSystemSimulator
        results = ATSSystemSimulator.simulate_all(resume, job_description)
        return Response(results)

    # ── LinkedIn Import ───────────────────────────────────────────────────────

    @action(detail=False, methods=['post'], url_path='linkedin-import')
    def linkedin_import(self, request):
        """
        Import a LinkedIn profile and return structured resume data.

        Body: {url: str}
        """
        url = request.data.get('url', '').strip()
        if not url:
            return Response({'error': 'url is required'}, status=status.HTTP_400_BAD_REQUEST)

        from apps.resumes.services.linkedin_importer import LinkedInImporter
        result = LinkedInImporter().import_profile(url)
        return Response(result)

    # ── Rejection Analysis ────────────────────────────────────────────────────

    @action(detail=True, methods=['post'], url_path='rejection-analysis',
            throttle_classes=[AIFeatureThrottle])
    def rejection_analysis(self, request, pk=None):
        """
        AI-powered analysis of why a resume may have been rejected.

        Body: {job_description: str, company: str, role: str}
        """
        resume = self.get_object()
        job_description = request.data.get('job_description', '')
        company = request.data.get('company', '')
        role = request.data.get('role', '')

        from apps.resumes.services.llm_service import LLMService
        result = LLMService.analyse_rejection(resume, job_description, company, role)
        return Response(result)

    # ── Version History ───────────────────────────────────────────────────────

    @action(detail=True, methods=['get'], url_path='versions')
    def versions(self, request, pk=None):
        resume = self.get_object()
        versions = resume.versions.all()
        return Response(ResumeVersionSerializer(versions, many=True).data)


# ── Task Status ───────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_status(request, task_id: str):
    """Poll the status of a background Celery task."""
    try:
        from celery.result import AsyncResult
        result = AsyncResult(task_id)
        data = {
            'task_id': task_id,
            'status': result.status,
            'ready': result.ready(),
        }
        if result.ready():
            data['result'] = result.result if not isinstance(result.result, Exception) else str(result.result)
        return Response(data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ── Job Applications ──────────────────────────────────────────────────────────

class JobApplicationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = JobApplicationSerializer

    def get_queryset(self):
        return JobApplication.objects.filter(user=self.request.user).select_related('resume')

    def perform_create(self, serializer):
        app = serializer.save(user=self.request.user)
        # Snapshot ATS score
        if app.resume:
            latest = app.resume.analyses.order_by('-analysis_timestamp').first()
            if latest:
                app.ats_score_at_apply = latest.final_score
                app.save(update_fields=['ats_score_at_apply'])

    @action(detail=True, methods=['post'], url_path='cover-letter',
            throttle_classes=[AIFeatureThrottle])
    def cover_letter(self, request, pk=None):
        """Generate or retrieve a cover letter for this application."""
        app = self.get_object()
        if not app.resume:
            return Response(
                {'error': 'Link a resume to this application first'},
                status=status.HTTP_400_BAD_REQUEST
            )

        existing = getattr(app, 'cover_letter', None)
        if existing and not request.data.get('regenerate'):
            return Response(CoverLetterSerializer(existing).data)

        from apps.resumes.services.llm_service import LLMService
        result = LLMService.generate_cover_letter(
            app.resume, app.company, app.role, app.job_description
        )
        cl, _ = CoverLetter.objects.update_or_create(
            application=app,
            defaults={
                'user': request.user,
                'resume': app.resume,
                'company': app.company,
                'role': app.role,
                'content': result['content'],
            }
        )
        data = CoverLetterSerializer(cl).data
        data['ai_powered'] = result['ai_powered']
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='interview-prep',
            throttle_classes=[AIFeatureThrottle])
    def interview_prep(self, request, pk=None):
        """Generate interview questions for this application."""
        app = self.get_object()
        if not app.resume:
            return Response(
                {'error': 'Link a resume to this application first'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from apps.resumes.services.llm_service import LLMService
        result = LLMService.generate_interview_questions(
            app.resume, app.role, app.job_description, app.company
        )
        session, _ = InterviewPrepSession.objects.update_or_create(
            application=app,
            defaults={
                'user': request.user,
                'resume': app.resume,
                'role': app.role,
                'company': app.company,
                'job_description': app.job_description,
                'questions': result['questions'],
            }
        )
        data = InterviewPrepSerializer(session).data
        data['ai_powered'] = result['ai_powered']
        return Response(data, status=status.HTTP_201_CREATED)


# ── Outcome Analytics ─────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def outcome_analytics(request):
    """Return outcome analytics for the current user."""
    from apps.tracker.outcome_analytics import OutcomeAnalyticsService
    stats = OutcomeAnalyticsService().get_user_stats(request.user)
    return Response(stats)


# ── ATS Simulation (standalone) ───────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ats_simulate_resume(request, resume_id: int):
    """Simulate ATS parsing for a specific resume."""
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    job_description = request.data.get('job_description', '')

    from apps.analyzer.services.ats_simulator import ATSSystemSimulator
    results = ATSSystemSimulator.simulate_all(resume, job_description)
    return Response(results)
