from rest_framework import serializers
from .models import Niche, Course, Module, Lesson, Question


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d',
                  'correct_option', 'explanation', 'order')


class LessonSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = ('id', 'title', 'lesson_type', 'content', 'order',
                  'duration_minutes', 'questions')


class LessonListSerializer(serializers.ModelSerializer):
    """Lightweight — no content/questions for list views."""
    class Meta:
        model = Lesson
        fields = ('id', 'title', 'lesson_type', 'order', 'duration_minutes')


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonListSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ('id', 'title', 'order', 'is_free', 'lessons')


class CourseListSerializer(serializers.ModelSerializer):
    niche_name = serializers.CharField(source='niche.name', read_only=True)
    niche_icon = serializers.CharField(source='niche.icon', read_only=True)
    module_count = serializers.SerializerMethodField()
    price_display = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ('id', 'title', 'slug', 'description', 'thumbnail',
                  'price', 'price_display', 'certificate_price',
                  'niche_name', 'niche_icon', 'module_count')

    def get_module_count(self, obj):
        return obj.modules.count()

    def get_price_display(self, obj):
        return f'${obj.price / 100:.2f}'


class CourseDetailSerializer(CourseListSerializer):
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta(CourseListSerializer.Meta):
        fields = CourseListSerializer.Meta.fields + ('modules', 'created_at')


class NicheSerializer(serializers.ModelSerializer):
    course_count = serializers.SerializerMethodField()

    class Meta:
        model = Niche
        fields = ('id', 'name', 'slug', 'icon', 'description', 'course_count')

    def get_course_count(self, obj):
        return obj.courses.filter(is_published=True).count()
