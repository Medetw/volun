"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    
    # Auth endpoints
    path("api/auth/", include("apps.auth.urls")),
    
    # JWT token refresh
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    
    # Admin endpoints
    path("api/admin/", include("apps.admin_panel.urls")),
    
    # Projects endpoints
    path("api/projects/", include("apps.projects.urls")),
    
    # Applications endpoints
    path("api/applications/", include("apps.applications.urls")),
    
    # News endpoints
    path("api/news/", include("apps.news.urls")),
    
    # Statistics endpoints
    path("api/statistics/", include("apps.statistics.urls")),
    
    # Notifications endpoints
    path("api/notifications/", include("apps.notifications.urls")),
    
    # Reports endpoints
    path("api/reports/", include("apps.reports.urls")),

    # Users endpoints (certificates, etc.)
    path("api/users/", include("apps.users.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve Vue frontend assets directly (works regardless of collectstatic)
from django.views.static import serve as static_serve
from pathlib import Path as _Path

_frontend_dist = _Path(settings.BASE_DIR) / "frontend_dist"

urlpatterns += [
    # Serve /assets/ files directly from frontend_dist
    re_path(r"^assets/(?P<path>.*)$", static_serve, {"document_root": _frontend_dist / "assets"}),
    # Serve /favicon.ico and other root-level files
    re_path(r"^favicon\.ico$", static_serve, {"document_root": _frontend_dist, "path": "favicon.ico"}),
]

# Serve Vue SPA — catch-all MUST be last (excludes api, admin, static, media, assets)
urlpatterns += [
    re_path(r"^(?!api/|admin/|static/|media/|assets/).*$", TemplateView.as_view(template_name="index.html"), name="spa"),
]
