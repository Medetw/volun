from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.notifications.views import (
    NotificationViewSet,
    NotificationPreferenceViewSet,
    NotificationAdminViewSet
)

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notifications')
router.register(r'notification-preferences', NotificationPreferenceViewSet, basename='notification-preferences')
router.register(r'admin/notifications', NotificationAdminViewSet, basename='admin-notifications')

urlpatterns = [
    path('', include(router.urls)),
]
