from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.users.views import VolunteerCertificateViewSet

router = DefaultRouter()
router.register('certificates', VolunteerCertificateViewSet, basename='certificates')

urlpatterns = [
    path('', include(router.urls)),
]
