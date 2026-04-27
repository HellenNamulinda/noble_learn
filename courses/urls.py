from django.urls import path
from .views import NicheListView, CourseListView, CourseDetailView, LessonDetailView, AIHintView

urlpatterns = [
    path('niches/', NicheListView.as_view(), name='niches'),
    path('', CourseListView.as_view(), name='courses'),
    path('<slug:slug>/', CourseDetailView.as_view(), name='course-detail'),
    path('lessons/<int:pk>/', LessonDetailView.as_view(), name='lesson-detail'),
    path('ai/hint/', AIHintView.as_view(), name='ai-hint'),
]
