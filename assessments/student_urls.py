"""
Student-facing URL configuration for assessments app.
"""
from django.urls import path
from . import student_views

urlpatterns = [
    path('', student_views.test_list, name='test_list'),
    path('test/<int:test_id>/', student_views.take_test, name='take_test'),
    path('result/<int:attempt_id>/', student_views.test_result, name='test_result'),
]
