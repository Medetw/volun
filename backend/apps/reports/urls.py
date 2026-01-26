from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.reports.views import (
    ProjectReportViewSet,
    VolunteerContributionViewSet
)

router = DefaultRouter()
router.register(r'reports', ProjectReportViewSet, basename='reports')
router.register(r'contributions', VolunteerContributionViewSet, basename='contributions')

urlpatterns = [
    path('', include(router.urls)),
]
