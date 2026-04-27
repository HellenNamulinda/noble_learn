import uuid
from django.db import models
from django.conf import settings


class Order(models.Model):
    COURSE_UNLOCK = 'course'
    CERTIFICATE = 'certificate'
    ORDER_TYPE_CHOICES = [
        (COURSE_UNLOCK, 'Course Unlock'),
        (CERTIFICATE, 'Certificate'),
    ]

    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders'
    )
    course = models.ForeignKey(
        'courses.Course', on_delete=models.CASCADE, related_name='orders'
    )
    order_type = models.CharField(max_length=15, choices=ORDER_TYPE_CHOICES)
    amount = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} | {self.order_type} | {self.course.title} | {self.status}'
