from django.db import models
from django.conf import settings


class Enrollment(models.Model):
    """Tracks whether a user has access (free auto-enroll or paid unlock)."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments'
    )
    course = models.ForeignKey(
        'courses.Course', on_delete=models.CASCADE, related_name='enrollments'
    )
    is_paid = models.BooleanField(default=False)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f'{self.user.email} → {self.course.title} (paid={self.is_paid})'


class LessonProgress(models.Model):
    """Records a completed lesson for a user."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lesson_progress'
    )
    lesson = models.ForeignKey(
        'courses.Lesson', on_delete=models.CASCADE, related_name='progress_records'
    )
    completed_at = models.DateTimeField(auto_now_add=True)
    quiz_score = models.PositiveIntegerField(null=True, blank=True)  # 0-100 for quiz lessons

    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        return f'{self.user.email} — {self.lesson.title}'
