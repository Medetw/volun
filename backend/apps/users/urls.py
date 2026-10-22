from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.users.views import (
    VolunteerCertificateViewSet,
    VolunteerHoursViewSet,
    VolunteerListView,
    VolunteerOfWeekAPIView,
    ModeratorProfileView,
    ModeratorManagementView,
    ModeratorDetailView,
    BlacklistViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('certificates', VolunteerCertificateViewSet, basename='certificates')
router.register('hours', VolunteerHoursViewSet, basename='volunteer-hours')
router.register('blacklist', BlacklistViewSet, basename='blacklist')

urlpatterns = [
    path('', include(router.urls)),
    path('volunteers/', VolunteerListView.as_view(), name='volunteer-list'),
    path('volunteer-of-week/', VolunteerOfWeekAPIView.as_view(), name='volunteer-of-week'),
    path('moderator/profile/', ModeratorProfileView.as_view(), name='moderator-profile'),
    path('moderators/', ModeratorManagementView.as_view(), name='moderator-management'),
    path('moderators/<int:pk>/', ModeratorDetailView.as_view(), name='moderator-detail'),
]
