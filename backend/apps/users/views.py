"""
Views for users application.
Handles registration, JWT auth, profile, admin user management.
"""
from django.contrib.auth import update_session_auth_hash
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import User, Passenger
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    UserRegistrationSerializer,
    PassengerSerializer,
    ChangePasswordSerializer,
    AdminUserUpdateSerializer,
)
from .permissions import IsAdminUser, IsAdminOrManager


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    UC-002: User Login.
    Returns JWT access + refresh tokens with user info.
    """
    serializer_class = CustomTokenObtainPairSerializer

    @extend_schema(
        summary='Login — obtain JWT tokens',
        tags=['Authentication']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RegisterView(generics.CreateAPIView):
    """
    UC-002: User Registration.
    Creates a new user account with passenger profile.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary='Register new user',
        tags=['Authentication']
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Return tokens immediately after registration
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Registration successful.',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    """Blacklist the refresh token on logout."""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(summary='Logout — blacklist refresh token', tags=['Authentication'])
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully.'})
        except Exception:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Get and update current user profile.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(summary='Get current user profile', tags=['Profile'])
    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(summary='Update current user profile', tags=['Profile'])
    def patch(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PassengerProfileView(generics.RetrieveUpdateAPIView):
    """Get and update passenger travel profile."""
    serializer_class = PassengerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        try:
            return self.request.user.passenger_profile
        except Passenger.DoesNotExist:
            return None

    @extend_schema(summary='Get passenger profile', tags=['Profile'])
    def get(self, request, *args, **kwargs):
        passenger = self.get_object()
        if not passenger:
            return Response({'error': 'Passenger profile not found.'}, status=404)
        return Response(PassengerSerializer(passenger).data)

    @extend_schema(summary='Update passenger profile', tags=['Profile'])
    def patch(self, request, *args, **kwargs):
        passenger = self.get_object()
        if not passenger:
            return Response({'error': 'Passenger profile not found.'}, status=404)
        serializer = PassengerSerializer(passenger, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ChangePasswordView(APIView):
    """Change password for authenticated user."""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(summary='Change password', tags=['Profile'])
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'error': 'Old password is incorrect.'}, status=400)

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Password changed successfully.'})


# ──────────────────────────────────────────
# Admin views
# ──────────────────────────────────────────

class AdminUserListView(generics.ListAPIView):
    """Admin: list all users with filtering."""
    queryset = User.objects.all().select_related('passenger_profile')
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrManager]
    search_fields = ['username', 'email']
    ordering_fields = ['date_joined', 'username']

    @extend_schema(summary='[Admin] List all users', tags=['Admin — Users'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin: get, update or delete a specific user."""
    queryset = User.objects.all()
    serializer_class = AdminUserUpdateSerializer
    permission_classes = [IsAdminUser]

    @extend_schema(summary='[Admin] Get user by ID', tags=['Admin — Users'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(summary='[Admin] Update user', tags=['Admin — Users'])
    def patch(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(summary='[Admin] Delete user', tags=['Admin — Users'])
    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
