from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def health_check(_request):
    return JsonResponse({'status': 'ok'})

urlpatterns = [
    path('healthz/', health_check, name='healthz'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/courses/', include('courses.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/progress/', include('progress.urls')),
    path('api/certificates/', include('certificates.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
