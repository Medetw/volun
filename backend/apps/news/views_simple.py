from rest_framework import views, permissions, status
from rest_framework.response import Response


class NewsSimpleAPIView(views.APIView):
    """Простой API для тестирования новостей."""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        return Response({
            'message': 'News API is working!',
            'status': 'success'
        })
