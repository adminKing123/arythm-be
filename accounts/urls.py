from django.contrib import admin
from django.urls import path, include
from .views import LoginWithUsernameAPIView, LogoutAPIView, ResgisterAPIView, VerifyEmailnActivateAPIAccountView, ResendEmailOTPView, ForgotPasswordRequestAPIView, ResetPasswordRequestAPIView

urlpatterns = [
    path('username/login', LoginWithUsernameAPIView.as_view(), name='username_login'),
    path('register', ResgisterAPIView.as_view(), name='register'),
    path('logout', LogoutAPIView.as_view(), name='login'),
    path('verify-email-and-activate-account', VerifyEmailnActivateAPIAccountView.as_view(), name='verify_email_and_activate_account'),
    path('resend-email-otp', ResendEmailOTPView.as_view(), name='verify_email_and_activate_account'),
    path('request-password-change-email-otp', ForgotPasswordRequestAPIView.as_view(), name="request_password_change_email_otp"),
    path('reset-password-with-email', ResetPasswordRequestAPIView.as_view(), name="reset_password_with_email"),
]
