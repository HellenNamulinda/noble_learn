from django.contrib import admin
from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_number', 'user', 'course', 'issued_at')
    search_fields = ('certificate_number', 'user__email', 'course__title')
    readonly_fields = ('id', 'certificate_number', 'pdf_file', 'issued_at')
