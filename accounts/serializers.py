from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User
from config import CONFIG

class LoginWithUsernameAPISerializer(serializers.Serializer):
    username = serializers.CharField(required=True)  # Use CharField for username
    password = serializers.CharField(required=True, write_only=True)  # Hide password in responses

class RegisterAPISerializer(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=150, validators=[UniqueValidator(queryset=User.objects.all())])
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    first_name = serializers.CharField(required=True, max_length=30)
    last_name = serializers.CharField(required=True, max_length=30)

class VerifyEmailnActivateAccountAPISerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    OTP = serializers.CharField(required=True, validators=[
            MinLengthValidator(CONFIG["OTP_LENGTH"]),
            MaxLengthValidator(CONFIG["OTP_LENGTH"])
        ])

class ResendEmailOTPAPISerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class ForgotPasswordRequestAPISerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class ResetPasswordRequestAPISerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    OTP = serializers.CharField(required=True, validators=[
            MinLengthValidator(CONFIG["OTP_LENGTH"]),
            MaxLengthValidator(CONFIG["OTP_LENGTH"])
        ])
    
class LogoutAPISerializer(serializers.Serializer):
    logout_all_devices = serializers.BooleanField(default=False, required=False)