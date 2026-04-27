from rest_framework import serializers
from .models import Certificate


class CertificateSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = ('id', 'certificate_number', 'course_title', 'issued_at', 'pdf_url')

    def get_pdf_url(self, obj):
        request = self.context.get('request')
        if obj.pdf_file and request:
            return request.build_absolute_uri(obj.pdf_file.url)
        return None
