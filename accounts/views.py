from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginWithUsernameAPISerializer, LogoutAPISerializer, RegisterAPISerializer, VerifyEmailnActivateAccountAPISerializer, ResendEmailOTPAPISerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.core.cache import cache
from .helpers import generateOTP
from config import CONFIG

class LoginWithUsernameAPIView(APIView):
    def post(self, request):
        serializer = LoginWithUsernameAPISerializer(data=request.data)
        if (serializer.is_valid()):
            data = serializer.validated_data
            username = data['username']
            password = data['password']

            user = authenticate(request, username=username, password=password)

            if (user):
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                    "token": token.key,
                    "__c__": created,
                }, status=status.HTTP_200_OK)
            return Response({"username": ["Invalid username or password."]}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ResgisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterAPISerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            user = User.objects.create_user(
                username=data['username'], 
                email=data['email'], 
                password=data['password'], 
                first_name=data['first_name'], 
                last_name=data['last_name'], 
                is_active=False
            )
            OTP = generateOTP(6)
            cache.set(user.email, OTP, timeout=120)

            if (CONFIG["DEBUG"]): data["OTP"] = OTP
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailnActivateAPIAccountView(APIView):
    def post(self, request):
        serializer = VerifyEmailnActivateAccountAPISerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            CACHED_OTP = cache.get(data['email'])
            if (CACHED_OTP != data['OTP']): return Response({"OTP": ["Invalid OTP!"]}, status=status.HTTP_400_BAD_REQUEST)
            try:
                user = User.objects.get(email=data['email'])
                user.is_active = True
                user.save()
                cache.delete(data['email'])
                return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"OTP": ["Invalid Request!"]}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResendEmailOTPView(APIView):
    def post(self, request):
        serializer = ResendEmailOTPAPISerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            CACHED_OTP = cache.get(data['email'])
            if (CACHED_OTP): return Response({"OTP": ["OTP Already Sent"]}, status=status.HTTP_400_BAD_REQUEST)
            OTP = generateOTP(6)
            cache.set(data["email"], OTP, timeout=120)
            if (CONFIG["DEBUG"]): data["OTP"] = OTP
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = LogoutAPISerializer(data=request.data)
            if (serializer.is_valid()):
                data = serializer.validated_data
                if (data['logout_all_devices']):
                    token = Token.objects.get(user=request.user)
                    token.delete()
            return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({"logout": ["Invalid token or already logged out."]}, status=status.HTTP_400_BAD_REQUEST)
