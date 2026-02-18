from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import TestViewSet, AttemptViewSet

router = DefaultRouter()
router.register(r'tests', TestViewSet, basename='test')
router.register(r'attempts', AttemptViewSet, basename='attempt')

urlpatterns = [
    path('', include(router.urls)),
]
