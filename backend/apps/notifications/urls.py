from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.notifications.views import (
    NotificationViewSet,
    NotificationPreferenceViewSet,
    NotificationAdminViewSet
)

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notifications')
router.register(r'admin/notifications', NotificationAdminViewSet, basename='admin-notifications')

urlpatterns = [
    path('notification-preferences/', NotificationPreferenceViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'update',
    }), name='notification-preferences-list'),
    path('', include(router.urls)),
]
