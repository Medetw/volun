from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.users.views import (
    VolunteerCertificateViewSet,
    VolunteerHoursViewSet,
    VolunteerListView,
    VolunteerOfWeekAPIView,
)

router = DefaultRouter()
router.register('certificates', VolunteerCertificateViewSet, basename='certificates')
router.register('hours', VolunteerHoursViewSet, basename='volunteer-hours')

urlpatterns = [
    path('', include(router.urls)),
    path('volunteers/', VolunteerListView.as_view(), name='volunteer-list'),
    path('volunteer-of-week/', VolunteerOfWeekAPIView.as_view(), name='volunteer-of-week'),
]
