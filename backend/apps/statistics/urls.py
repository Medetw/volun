from django.urls import path
from apps.statistics.views_simple import StatisticsSimpleAPIView

urlpatterns = [
    path('statistics/', StatisticsSimpleAPIView.as_view(), name='statistics'),
]
