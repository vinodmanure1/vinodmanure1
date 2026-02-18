"""
API URL configuration for assessments app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('import-questions/', views.import_questions_csv, name='import_questions_csv'),
    path('submit-attempt/', views.submit_attempt, name='submit_attempt'),
    path('report/<int:attempt_id>/pdf/', views.generate_report_pdf, name='generate_report_pdf'),
]
