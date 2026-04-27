import uuid
from django.db import models
from django.conf import settings


class Certificate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificates'
    )
    course = models.ForeignKey(
        'courses.Course', on_delete=models.CASCADE, related_name='certificates'
    )
    order = models.OneToOneField(
        'payments.Order', on_delete=models.CASCADE, related_name='certificate', null=True
    )
    certificate_number = models.CharField(max_length=20, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='certificates/')

    def __str__(self):
        return f'{self.certificate_number} — {self.user.email} — {self.course.title}'
