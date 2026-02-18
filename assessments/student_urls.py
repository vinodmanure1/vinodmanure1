from django.urls import path
from . import student_views

urlpatterns = [
    path('', student_views.index, name='index'),
    path('dashboard/', student_views.student_dashboard, name='student_dashboard'),
    path('test/<int:test_id>/', student_views.take_test, name='take_test'),
    path('report/<int:attempt_id>/', student_views.view_report, name='view_report'),
    path('report/<int:attempt_id>/pdf/', student_views.download_pdf_report, name='download_pdf_report'),
]
