from django.urls import path
from . import views

app_name = 'assessments'

urlpatterns = [
    # Student views
    path('', views.home, name='home'),
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('test/<int:test_id>/take/', views.take_test, name='take_test'),
    path('attempt/<int:attempt_id>/save/', views.save_progress, name='save_progress'),
    path('attempt/<int:attempt_id>/submit/', views.submit_attempt, name='submit_attempt'),
    path('attempt/<int:attempt_id>/report/', views.view_report, name='view_report'),
    path('attempt/<int:attempt_id>/pdf/', views.download_pdf_report, name='download_pdf'),
    
    # Admin API
    path('api/admin/upload-csv/', views.admin_upload_csv, name='admin_upload_csv'),
]
