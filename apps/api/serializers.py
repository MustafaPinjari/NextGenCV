"""
DRF Serializers for the NextGenCV REST API.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from apps.resumes.models import (
    Resume, PersonalInfo, Experience, Education, Skill, Project,
    ResumeAnalysis, ResumeVersion, Certification
)
from apps.tracker.models import JobApplication, CoverLetter, InterviewPrepSession


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


# ── Resume Sections ───────────────────────────────────────────────────────────

class PersonalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalInfo
        fields = ['id', 'full_name', 'phone', 'email', 'linkedin', 'github', 'location']


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = [
            'id', 'company', 'role', 'location', 'start_date', 'end_date',
            'description', 'achievements', 'order'
        ]


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = [
            'id', 'institution', 'degree', 'field', 'start_year', 'end_year',
            'gpa', 'honors', 'relevant_coursework', 'order'
        ]


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category', 'proficiency_level', 'years_of_experience']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'technologies', 'impact',
            'url', 'start_date', 'end_date', 'order'
        ]


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = [
            'id', 'name', 'issuer', 'issue_date', 'expiry_date',
            'credential_id', 'credential_url', 'order'
        ]


# ── Resume ────────────────────────────────────────────────────────────────────

class ResumeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    class Meta:
        model = Resume
        fields = [
            'id', 'title', 'template', 'is_draft', 'latest_ats_score',
            'completeness_score', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ResumeDetailSerializer(serializers.ModelSerializer):
    """Full serializer with all nested sections."""
    personal_info = PersonalInfoSerializer(read_only=True)
    experiences = ExperienceSerializer(many=True, read_only=True)
    education = EducationSerializer(many=True, read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)
    certifications = CertificationSerializer(many=True, read_only=True)

    class Meta:
        model = Resume
        fields = [
            'id', 'title', 'template', 'summary', 'is_draft',
            'color_scheme', 'font_family',
            'latest_ats_score', 'completeness_score',
            'last_analyzed_at', 'last_optimized_at',
            'created_at', 'updated_at',
            'personal_info', 'experiences', 'education',
            'skills', 'projects', 'certifications',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'latest_ats_score']


class ResumeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ['title', 'template', 'summary', 'is_draft', 'color_scheme', 'font_family']


# ── Analysis ──────────────────────────────────────────────────────────────────

class ResumeAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeAnalysis
        fields = [
            'id', 'resume', 'job_description', 'analysis_timestamp',
            'keyword_match_score', 'skill_relevance_score', 'section_completeness_score',
            'experience_impact_score', 'quantification_score', 'action_verb_score',
            'final_score', 'matched_keywords', 'missing_keywords',
            'weak_action_verbs', 'missing_quantifications', 'suggestions',
        ]
        read_only_fields = ['id', 'analysis_timestamp']


# ── Version ───────────────────────────────────────────────────────────────────

class ResumeVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeVersion
        fields = [
            'id', 'version_number', 'created_at', 'modification_type',
            'ats_score', 'user_notes'
        ]
        read_only_fields = ['id', 'created_at', 'version_number']


# ── Job Applications ──────────────────────────────────────────────────────────

class JobApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = [
            'id', 'company', 'role', 'job_url', 'job_description',
            'resume', 'status', 'ats_score_at_apply', 'applied_date',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CoverLetterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoverLetter
        fields = ['id', 'company', 'role', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class InterviewPrepSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewPrepSession
        fields = ['id', 'role', 'company', 'questions', 'created_at']
        read_only_fields = ['id', 'created_at']
