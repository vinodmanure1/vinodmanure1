from django.urls import path
from . import student_views, api_views

urlpatterns = [
    # Student views
    path('', student_views.home, name='home'),
    path('assessment/<int:assessment_id>/', student_views.take_assessment, name='take_assessment'),
    path('result/<int:result_id>/', student_views.view_result, name='view_result'),
    path('result/<int:result_id>/pdf/', student_views.download_pdf, name='download_pdf'),
    
    # API views
    path('api/assessments/', api_views.list_assessments, name='api_list_assessments'),
    path('api/assessment/<int:assessment_id>/', api_views.get_assessment, name='api_get_assessment'),
    path('api/submit/', api_views.submit_assessment, name='api_submit_assessment'),
    path('api/results/', api_views.list_results, name='api_list_results'),
]
