from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course, Lesson
from .models import Enrollment, LessonProgress
from .serializers import EnrollmentSerializer, LessonProgressSerializer


class EnrollView(APIView):
    """Auto-enroll a user (free) when they open a course."""

    def post(self, request):
        course_id = request.data.get('course_id')
        try:
            course = Course.objects.get(pk=course_id, is_published=True)
        except Course.DoesNotExist:
            return Response({'detail': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)

        enrollment, _ = Enrollment.objects.get_or_create(
            user=request.user, course=course
        )
        return Response(EnrollmentSerializer(enrollment, context={'request': request}).data)


class MyCoursesView(generics.ListAPIView):
    serializer_class = EnrollmentSerializer

    def get_queryset(self):
        return Enrollment.objects.filter(
            user=self.request.user
        ).select_related('course').prefetch_related('course__modules__lessons')

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


class CompleteLessonView(APIView):
    """Mark a lesson as completed, optionally recording a quiz score."""

    def post(self, request):
        lesson_id = request.data.get('lesson_id')
        quiz_score = request.data.get('quiz_score')

        try:
            lesson = Lesson.objects.select_related('module__course').get(pk=lesson_id)
        except Lesson.DoesNotExist:
            return Response({'detail': 'Lesson not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Verify access through enrollment for non-free modules.
        if not lesson.module.is_free:
            has_access = Enrollment.objects.filter(
                user=request.user, course=lesson.module.course
            ).exists()
            if not has_access:
                return Response({'detail': 'Enroll in the course first.'}, status=status.HTTP_403_FORBIDDEN)

        progress, created = LessonProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson,
            defaults={'quiz_score': quiz_score},
        )
        if not created and quiz_score is not None:
            progress.quiz_score = quiz_score
            progress.save(update_fields=['quiz_score'])

        # Check if entire course is now complete
        course = lesson.module.course
        total = sum(m.lessons.count() for m in course.modules.all())
        completed = LessonProgress.objects.filter(
            user=request.user,
            lesson__module__course=course,
        ).count()
        if total > 0 and completed >= total:
            Enrollment.objects.filter(
                user=request.user, course=course
            ).update(completed_at=timezone.now())

        return Response(LessonProgressSerializer(progress).data)


class ProgressSummaryView(APIView):
    """Return completed lesson IDs for a course (used by the Flutter app to mark checkmarks)."""

    def get(self, request, course_id):
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        lesson_ids = [
            l.id for m in course.modules.all() for l in m.lessons.all()
        ]
        completed_ids = list(
            LessonProgress.objects.filter(
                user=request.user, lesson_id__in=lesson_ids
            ).values_list('lesson_id', flat=True)
        )
        return Response({'completed_lesson_ids': completed_ids})
