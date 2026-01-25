from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.projects import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'regions', views.RegionViewSet, basename='region')
router.register(r'projects', views.ProjectViewSet, basename='project')

app_name = 'projects'

urlpatterns = [
    path('', include(router.urls)),
]
