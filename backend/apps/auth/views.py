from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse
from apps.auth.serializers import (
    VolunteerRegisterSerializer,
    OrganizationRegisterSerializer,
    LoginSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from apps.core.logging import logger, log_authentication_attempt


@extend_schema(
    summary="Register a new volunteer",
    description="Create a new volunteer account with profile information.",
    request=VolunteerRegisterSerializer,
    responses={
        201: OpenApiResponse(description="Volunteer registered successfully"),
        400: OpenApiResponse(description="Validation error"),
    },
)
@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def register_volunteer(request):
    """Register a new volunteer."""
    logger.info(f"New volunteer registration attempt from {request.META.get('REMOTE_ADDR')}")

    serializer = VolunteerRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # Сохраняем аватар если загружен
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
            user.save(update_fields=['avatar'])
        refresh = RefreshToken.for_user(user)
        
        logger.user_action(
            action="VOLUNTEER_REGISTERED",
            user_id=user.id,
            details={'email': user.email, 'username': user.username}
        )
        
        return Response({
            'user': UserSerializer(user, context={'request': request}).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)

    logger.warning(f"Volunteer registration failed: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Register a new organization",
    description="Create a new organization account with profile information.",
    request=OrganizationRegisterSerializer,
    responses={
        201: OpenApiResponse(description="Organization registered successfully"),
        400: OpenApiResponse(description="Validation error"),
    },
)
@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def register_organization(request):
    """Register a new organization."""
    logger.info(f"New organization registration attempt from {request.META.get('REMOTE_ADDR')}")

    serializer = OrganizationRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # Сохраняем аватар если загружен
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
            user.save(update_fields=['avatar'])
        refresh = RefreshToken.for_user(user)

        logger.user_action(
            action="ORGANIZATION_REGISTERED",
            user_id=user.id,
            details={'email': user.email, 'username': user.username}
        )

        return Response({
            'user': UserSerializer(user, context={'request': request}).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)

    logger.warning(f"Organization registration failed: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Login",
    description="Authenticate user and get JWT tokens.",
    request=LoginSerializer,
    responses={
        200: OpenApiResponse(description="Login successful"),
        400: OpenApiResponse(description="Invalid credentials"),
    },
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Login user and return JWT tokens."""
    email = request.data.get('email', '')
    logger.info(f"Login attempt for {email} from {request.META.get('REMOTE_ADDR')}")
    
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        log_authentication_attempt(request, success=True, username=email)
        logger.user_action(
            action="LOGIN_SUCCESS",
            user_id=user.id,
            details={'email': user.email, 'role': user.role}
        )
        
        return Response({
            'user': UserSerializer(user, context={'request': request}).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)

    log_authentication_attempt(request, success=False, username=email)
    logger.warning(f"Login failed for {email}: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


@extend_schema(
    summary="Get current user profile",
    description="Retrieve the authenticated user's profile.",
    responses={
        200: UserSerializer,
        401: OpenApiResponse(description="Unauthorized"),
    },
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """Get current authenticated user profile."""
    serializer = UserSerializer(request.user, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Update current user profile",
    description="Update the authenticated user's profile information.",
    request=UserUpdateSerializer,
    responses={
        200: UserSerializer,
        400: OpenApiResponse(description="Validation error"),
        401: OpenApiResponse(description="Unauthorized"),
    },
)
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def update_current_user(request):
    """Update current authenticated user profile."""
    serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        # Обновляем аватар если загружен
        if 'avatar' in request.FILES:
            request.user.avatar = request.FILES['avatar']
            request.user.save(update_fields=['avatar'])
        logger.user_action(
            action="PROFILE_UPDATED",
            user_id=request.user.id,
            details={'updated_fields': list(request.data.keys())}
        )
        return Response(UserSerializer(request.user, context={'request': request}).data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Logout",
    description="Logout user and blacklist refresh token.",
    responses={
        200: OpenApiResponse(description="Logout successful"),
        401: OpenApiResponse(description="Unauthorized"),
    },
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Logout user and blacklist refresh token."""
    try:
        refresh_token = request.data.get("refresh_token")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        logger.user_action(
            action="LOGOUT",
            user_id=request.user.id,
            details={'email': request.user.email}
        )
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.warning(f"Logout failed for user {request.user.id}: {e}")
        return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
