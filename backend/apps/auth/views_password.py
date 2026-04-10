from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import secrets

from apps.auth.serializers import (
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    PasswordChangeSerializer
)

User = get_user_model()


@extend_schema(
    summary="Request password reset",
    description="Send password reset code to user email",
    request=PasswordResetRequestSerializer,
    responses={
        200: OpenApiResponse(description="Password reset code sent"),
        400: OpenApiResponse(description="Invalid email"),
        404: OpenApiResponse(description="User not found"),
    },
)
@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    """Запрос на сброс пароля."""
    serializer = PasswordResetRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            
            # Генерируем код сброса
            reset_code = str(secrets.randbelow(1000000)).zfill(6)
            reset_code_expiry = timezone.now() + timedelta(hours=1)
            
            # Сохраняем код в user (можно вынести в отдельную модель)
            user.password_reset_code = reset_code
            user.password_reset_expiry = reset_code_expiry
            user.save(update_fields=['password_reset_code', 'password_reset_expiry'])
            
            # TODO: Отправить email с кодом
            # send_password_reset_email.delay(user.email, reset_code)
            
            return Response({
                'message': 'Код для сброса пароля отправлен на вашу почту',
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            # Возвращаем успех даже если пользователь не найден (безопасность)
            return Response({
                'message': 'Если указанный email существует, код для сброса пароля будет отправлен'
            }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Confirm password reset",
    description="Reset password using code from email",
    request=PasswordResetConfirmSerializer,
    responses={
        200: OpenApiResponse(description="Password reset successful"),
        400: OpenApiResponse(description="Invalid code or email"),
        410: OpenApiResponse(description="Reset code expired"),
    },
)
@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_password_reset(request):
    """Подтверждение сброса пароля."""
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        reset_code = serializer.validated_data['reset_code']
        new_password = serializer.validated_data['new_password']
        
        try:
            user = User.objects.get(
                email=email,
                password_reset_code=reset_code,
                password_reset_expiry__gt=timezone.now()
            )
            
            # Устанавливаем новый пароль
            user.set_password(new_password)
            user.password_reset_code = None
            user.password_reset_expiry = None
            user.save(update_fields=['password', 'password_reset_code', 'password_reset_expiry'])
            
            return Response({
                'message': 'Пароль успешно изменен'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'error': 'Неверный email или код сброса пароля'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Change password",
    description="Change user password (requires authentication)",
    request=PasswordChangeSerializer,
    responses={
        200: OpenApiResponse(description="Password changed successfully"),
        400: OpenApiResponse(description="Invalid current password"),
        401: OpenApiResponse(description="Unauthorized"),
    },
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Изменение пароля."""
    
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Пароль успешно изменен'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
