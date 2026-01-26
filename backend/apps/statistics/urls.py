from django.urls import path
from apps.statistics.views import StatisticsAPIView

urlpatterns = [
    path('statistics/', StatisticsAPIView.as_view(), name='statistics'),
]
