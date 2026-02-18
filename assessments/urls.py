from django.urls import path
from . import views

app_name = 'assessments'

urlpatterns = [
    # Student views
    path('', views.student_dashboard, name='student_dashboard'),
    path('test/<int:test_id>/', views.take_test, name='take_test'),
    path('attempt/<int:attempt_id>/autosave/', views.autosave_attempt, name='autosave_attempt'),
    path('report/<int:attempt_id>/', views.view_report, name='view_report'),
    
    # API endpoints
    path('api/submit/', views.submit_attempt, name='submit_attempt'),
    path('api/csv-upload/', views.csv_upload, name='csv_upload'),
    path('api/report/<int:attempt_id>/pdf/', views.generate_pdf_report, name='generate_pdf_report'),
]
