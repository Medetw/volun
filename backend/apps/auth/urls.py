from django.urls import path
from apps.auth import views

app_name = 'auth'

urlpatterns = [
    path('register/volunteer/', views.register_volunteer, name='register-volunteer'),
    path('register/organization/', views.register_organization, name='register-organization'),
    path('login/', views.login, name='login'),
    path('me/', views.get_current_user, name='me'),
    path('me/update/', views.update_current_user, name='me-update'),
]
