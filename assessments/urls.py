"""
URL configuration for assessments app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# DRF router for API endpoints
router = DefaultRouter()
router.register(r'tests', views.TestViewSet, basename='test')
router.register(r'attempts', views.AttemptViewSet, basename='attempt')

app_name = 'assessments'

urlpatterns = [
    # Student views
    path('', views.student_dashboard, name='dashboard'),
    path('take-test/<int:test_id>/', views.take_test, name='take_test'),
    path('report/<int:attempt_id>/pdf/', views.generate_report_pdf, name='report_pdf'),
    
    # API endpoints
    path('api/', include(router.urls)),
    path('api/upload-csv/', views.upload_csv, name='upload_csv'),
]
