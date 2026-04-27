from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.shortcuts import get_object_or_404 
import json
from urllib import error as urllib_error
from urllib import request as urllib_request

from .models import Niche, Course, Module, Lesson
from .serializers import (
    NicheSerializer, CourseListSerializer, CourseDetailSerializer,
    ModuleSerializer, LessonSerializer,
)
from progress.models import Enrollment


class IsEnrolledOrFreeModule(permissions.BasePermission):
    """Allow access to a lesson if the parent module is free OR user is enrolled."""
    message = 'Enroll in this course to unlock all lessons.'

    def has_object_permission(self, request, view, obj):
        if obj.module.is_free:
            return True
        return Enrollment.objects.filter(
            user=request.user, course=obj.module.course
        ).exists()


# ── Niches ───────────────────────────────────────────────────────────────────

class NicheListView(generics.ListAPIView):
    queryset = Niche.objects.all()
    serializer_class = NicheSerializer
    permission_classes = [permissions.AllowAny]


# ── Courses ──────────────────────────────────────────────────────────────────

class CourseListView(generics.ListAPIView):
    serializer_class = CourseListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Course.objects.filter(is_published=True).select_related('niche')
        niche_slug = self.request.query_params.get('niche')
        if niche_slug:
            qs = qs.filter(niche__slug=niche_slug)
        return qs


class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.filter(is_published=True)
    serializer_class = CourseDetailSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]


# ── Lessons ──────────────────────────────────────────────────────────────────

class LessonDetailView(generics.RetrieveAPIView):
    queryset = Lesson.objects.select_related('module__course')
    serializer_class = LessonSerializer

    def get_object(self):
        lesson = super().get_object()
        # Enforce enrollment gate: non-free lessons require enrollment.
        if not lesson.module.is_free:
            has_access = Enrollment.objects.filter(
                user=self.request.user,
                course=lesson.module.course,
            ).exists()
            if not has_access:
                self.permission_denied(self.request, message='Enroll to access this lesson.')
        return lesson


# ── AI Hint ──────────────────────────────────────────────────────────────────

class AIHintView(APIView):
    """Return an AI-generated hint for a quiz question (enrolled users only)."""

    def post(self, request):
        question_id = request.data.get('question_id')
        if not question_id:
            return Response({'detail': 'question_id required.'}, status=status.HTTP_400_BAD_REQUEST)

        from .models import Question
        question = get_object_or_404(Question, pk=question_id)

        # Verify user is enrolled in the course
        has_access = Enrollment.objects.filter(
            user=request.user,
            course=question.lesson.module.course,
        ).exists()
        if not has_access:
            return Response({'detail': 'Enroll in the course first.'}, status=status.HTTP_403_FORBIDDEN)

        api_key = settings.GEMINI_API_KEY
        if not api_key:
            return Response({'hint': 'Think carefully about each option before choosing.'})

        try:
            prompt = (
                f"You are a helpful tutor. Give a short, non-revealing hint (2-3 sentences) "
                f"for this multiple-choice question WITHOUT giving away the answer.\n\n"
                f"Question: {question.question_text}\n"
                f"A) {question.option_a}\nB) {question.option_b}\n"
                f"C) {question.option_c}\nD) {question.option_d}"
            )

            model_name = settings.GEMINI_MODEL
            endpoint = (
                f'https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}'
            )
            payload = {
                'contents': [{'parts': [{'text': prompt}]}],
                'generationConfig': {
                    'temperature': 0.6,
                    'maxOutputTokens': 180,
                },
            }

            req = urllib_request.Request(
                endpoint,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST',
            )
            with urllib_request.urlopen(req, timeout=15) as resp:
                body = json.loads(resp.read().decode('utf-8'))

            candidates = body.get('candidates') or []
            parts = (((candidates[0] if candidates else {}).get('content') or {}).get('parts') or [])
            hint = (parts[0].get('text', '').strip() if parts else '')
            if not hint:
                hint = 'Review the relevant concept in the lesson above.'
            return Response({'hint': hint})
        except (urllib_error.URLError, urllib_error.HTTPError, ValueError, KeyError):
            return Response({'hint': 'Review the relevant concept in the lesson above.'})
