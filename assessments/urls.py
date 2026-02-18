from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('assessment/', views.AssessmentView.as_view(), name='assessment'),
    path('results/<str:email>/', views.ResultsView.as_view(), name='results'),
    path('report/<str:email>/pdf/', views.PDFReportView.as_view(), name='pdf_report'),
]
