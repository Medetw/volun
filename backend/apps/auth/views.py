from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
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
def register_volunteer(request):
    """Register a new volunteer."""
    serializer = VolunteerRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
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
def register_organization(request):
    """Register a new organization."""
    serializer = OrganizationRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
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
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    serializer = UserSerializer(request.user)
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
def update_current_user(request):
    """Update current authenticated user profile."""
    serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
