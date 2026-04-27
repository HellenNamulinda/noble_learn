import uuid
from django.db import models


class Niche(models.Model):
    """A professional target audience (e.g. Accountants, Nurses, Lawyers)."""
    name = models.CharField(max_length=100)  # e.g. "Accountants"
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=10, default='📚')  # emoji
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    niche = models.ForeignKey(Niche, on_delete=models.SET_NULL, null=True, related_name='courses')
    title = models.CharField(max_length=200)   # e.g. "SQL for Accountants"
    slug = models.SlugField(unique=True)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='course_thumbnails/', null=True, blank=True)
    price = models.PositiveIntegerField(default=999)        # cents — $9.99
    certificate_price = models.PositiveIntegerField(default=499)  # cents — $4.99
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class Module(models.Model):
    """A chapter / section inside a Course."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    is_free = models.BooleanField(default=False)  # True for the first/preview module

    def __str__(self):
        return f'{self.course.title} — {self.title}'

    class Meta:
        ordering = ['order']


class Lesson(models.Model):
    """A single lesson inside a Module. Can be text content or a quiz."""
    TEXT = 'text'
    QUIZ = 'quiz'
    LESSON_TYPE_CHOICES = [(TEXT, 'Text'), (QUIZ, 'Quiz')]

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    lesson_type = models.CharField(max_length=10, choices=LESSON_TYPE_CHOICES, default=TEXT)
    content = models.TextField(blank=True)   # markdown for text lessons
    order = models.PositiveIntegerField(default=0)
    duration_minutes = models.PositiveIntegerField(default=5)

    def __str__(self):
        return f'[{self.lesson_type.upper()}] {self.title}'

    class Meta:
        ordering = ['order']


class Question(models.Model):
    """A multiple-choice question belonging to a quiz Lesson."""
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    OPTION_CHOICES = [(A, 'A'), (B, 'B'), (C, 'C'), (D, 'D')]

    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name='questions',
        limit_choices_to={'lesson_type': Lesson.QUIZ},
    )
    question_text = models.TextField()
    option_a = models.CharField(max_length=300)
    option_b = models.CharField(max_length=300)
    option_c = models.CharField(max_length=300)
    option_d = models.CharField(max_length=300)
    correct_option = models.CharField(max_length=1, choices=OPTION_CHOICES)
    explanation = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.question_text[:60]

    class Meta:
        ordering = ['order']
