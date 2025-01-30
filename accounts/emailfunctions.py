from django.core.mail import send_mail
from django.conf import settings


def email_verified_email(user):
    send_mail(
        'Email Verified Successfully',
        'Your email has been successfully verified. You can now login.',
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )

def otp_to_reset_password_email(user, OTP):
    send_mail(
        'Password Reset OTP',
        f'Your OTP for password reset is {OTP}',
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )

def password_reset_successfully_email(user):
    send_mail(
        'Password Reset Successfully',
        'Your password has been successfully reset.',
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )

def verify_email_otp_email(user, OTP):
    send_mail(
        'OTP to verify email',
        f'Your OTP to verify your is {OTP}',
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )
