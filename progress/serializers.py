from rest_framework import serializers
from .models import Enrollment, LessonProgress


class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_slug = serializers.CharField(source='course.slug', read_only=True)
    course_thumbnail = serializers.ImageField(source='course.thumbnail', read_only=True)
    total_lessons = serializers.SerializerMethodField()
    completed_lessons = serializers.SerializerMethodField()
    progress_pct = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = (
            'id', 'course', 'course_title', 'course_slug', 'course_thumbnail',
            'is_paid', 'enrolled_at', 'completed_at',
            'total_lessons', 'completed_lessons', 'progress_pct',
        )

    def get_total_lessons(self, obj):
        return obj.course.modules.prefetch_related('lessons').aggregate(
            total=__import__('django.db.models', fromlist=['Count']).Count('lessons')
        )['total'] if False else sum(m.lessons.count() for m in obj.course.modules.all())

    def get_completed_lessons(self, obj):
        user = self.context['request'].user
        lesson_ids = [
            l.id for m in obj.course.modules.all() for l in m.lessons.all()
        ]
        return LessonProgress.objects.filter(user=user, lesson_id__in=lesson_ids).count()

    def get_progress_pct(self, obj):
        total = self.get_total_lessons(obj)
        if total == 0:
            return 0
        return round(self.get_completed_lessons(obj) / total * 100)


class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = ('id', 'lesson', 'completed_at', 'quiz_score')
        read_only_fields = ('id', 'completed_at')
