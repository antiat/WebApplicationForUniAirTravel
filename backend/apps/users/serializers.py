"""
Serializers for the users application.
Handles validation, registration, profile data.
"""
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, Passenger


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extended JWT serializer — includes user info in token response.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['role'] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Add user info to login response
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'role': self.user.role,
        }
        return data


class PassengerSerializer(serializers.ModelSerializer):
    """Serializer for passenger profile data."""

    class Meta:
        model = Passenger
        fields = [
            'id', 'first_name', 'last_name',
            'passport_number', 'nationality',
            'birth_date', 'phone',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """
    Read serializer for User model.
    Includes nested passenger profile if exists.
    """
    passenger_profile = PassengerSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role',
            'is_active', 'date_joined', 'passenger_profile'
        ]
        read_only_fields = ['id', 'date_joined']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for new user registration (UC-002).
    Validates password match and creates passenger profile.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)

    # Passenger profile fields (required at registration)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    passport_number = serializers.CharField(max_length=50)
    nationality = serializers.CharField(max_length=100)
    birth_date = serializers.DateField()
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'passport_number',
            'nationality', 'birth_date', 'phone'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        if Passenger.objects.filter(passport_number=attrs.get('passport_number')).exists():
            raise serializers.ValidationError({'passport_number': 'This passport number is already registered.'})
        return attrs

    def create(self, validated_data):
        # Extract passenger fields
        passenger_fields = {
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'passport_number': validated_data.pop('passport_number'),
            'nationality': validated_data.pop('nationality'),
            'birth_date': validated_data.pop('birth_date'),
            'phone': validated_data.pop('phone', ''),
        }
        validated_data.pop('password_confirm')

        # Create user
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            role='passenger'
        )

        # Create passenger profile
        Passenger.objects.create(user=user, **passenger_fields)

        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change endpoint."""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password': 'New passwords do not match.'})
        return attrs


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for admin to update user details (role, status).
    """
    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'is_active']