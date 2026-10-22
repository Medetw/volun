from django.urls import path
from apps.auth import views
from apps.auth.views_password import (
    request_password_reset,
    confirm_password_reset,
    change_password
)

urlpatterns = [
    path('register/volunteer/', views.register_volunteer, name='register-volunteer'),
    path('register/organization/', views.register_organization, name='register-organization'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('me/', views.get_current_user, name='me'),
    path('me/update/', views.update_current_user, name='me-update'),
    
    # Password reset endpoints
    path('password/reset/', request_password_reset, name='password-reset'),
    path('password/reset/confirm/', confirm_password_reset, name='password-reset-confirm'),
    path('password/change/', change_password, name='password-change'),

    # Aliases for reverse lookups with auth- prefix
    path('register/volunteer/', views.register_volunteer, name='auth-register-volunteer'),
    path('register/organization/', views.register_organization, name='auth-register-organization'),
    path('login/', views.login, name='auth-login'),
    path('logout/', views.logout, name='auth-logout'),
    path('me/', views.get_current_user, name='auth-me'),
    path('me/update/', views.update_current_user, name='auth-me-update'),
    path('password/reset/', request_password_reset, name='auth-password-reset'),
    path('password/reset/confirm/', confirm_password_reset, name='auth-password-reset-confirm'),
    path('password/change/', change_password, name='auth-password-change'),
]
