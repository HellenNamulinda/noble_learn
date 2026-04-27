from django.contrib import admin
from .models import Enrollment, LessonProgress


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'is_paid', 'enrolled_at', 'completed_at')
    list_filter = ('is_paid',)
    search_fields = ('user__email', 'course__title')


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'quiz_score', 'completed_at')
    search_fields = ('user__email', 'lesson__title')
