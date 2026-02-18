from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'assessments'

# API router
router = DefaultRouter()
router.register(r'questions', views.QuestionViewSet, basename='question')
router.register(r'tests', views.TestViewSet, basename='test')
router.register(r'attempts', views.AttemptViewSet, basename='attempt')

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    path('api/submit-attempt/', views.submit_attempt, name='submit-attempt'),
    path('api/autosave-attempt/<int:attempt_id>/', views.autosave_attempt, name='autosave-attempt'),
    path('api/upload-csv/', views.upload_csv, name='upload-csv'),
    
    # Student views
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('take-test/<int:test_id>/', views.take_test, name='take-test'),
    path('report/<int:attempt_id>/', views.view_report, name='view-report'),
    path('report/<int:attempt_id>/pdf/', views.download_pdf_report, name='download-pdf'),
]
