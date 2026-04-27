from django.urls import path
from .views import EnrollView, MyCoursesView, CompleteLessonView, ProgressSummaryView

urlpatterns = [
    path('enroll/', EnrollView.as_view(), name='enroll'),
    path('my-courses/', MyCoursesView.as_view(), name='my-courses'),
    path('complete-lesson/', CompleteLessonView.as_view(), name='complete-lesson'),
    path('<uuid:course_id>/summary/', ProgressSummaryView.as_view(), name='progress-summary'),
]
