from django.urls import path
from apps.statistics.views import StatisticsAPIView

urlpatterns = [
    path('', StatisticsAPIView.as_view(), name='statistics-root'),
    path('statistics/', StatisticsAPIView.as_view(), name='statistics'),
]
