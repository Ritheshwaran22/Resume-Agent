import logging
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    ChangePasswordSerializer,
)
from .throttles import PasswordResetRateThrottle

logger = logging.getLogger(__name__)

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens immediately upon registration
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "User registered successfully.",
            "user": UserSerializer(user).data,
            "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }
        }, status=status.HTTP_201_CREATED)

class CustomLoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer

class CurrentUserView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieves, updates (e.g. email), or permanently deletes the authenticated user's account.
    All data deletion is wrapped in a database transaction, and uploaded files are cleaned up.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        user = self.get_object()

        # Collect physical resume files to clean up after database deletion
        resume_files = []
        try:
            for resume in user.resumes.all():
                if resume.file:
                    resume_files.append(resume.file)
        except Exception as e:
            logger.warning(f"Could not enumerate resume files for user {user.pk}: {e}")

        # Execute cascading database deletion in a transaction
        with transaction.atomic():
            user.delete()

        # Clean up physical files from storage after successful database commit
        for rf in resume_files:
            try:
                rf.delete(save=False)
            except Exception as file_err:
                logger.warning(f"Could not remove physical resume file from storage: {file_err}")

        return Response(
            {"message": "Account and all associated data have been permanently deleted."},
            status=status.HTTP_200_OK
        )


class ChangePasswordView(generics.GenericAPIView):
    """
    Authenticated password change endpoint.
    Validates current password, enforces Django password validators,
    and returns fresh JWT tokens so the user remains authenticated.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        new_password = serializer.validated_data['new_password']
        user.set_password(new_password)
        user.save()

        # Generate fresh JWT tokens for continued session security
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Password changed successfully.",
            "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }
        }, status=status.HTTP_200_OK)

class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"message": "Logged out."}, status=status.HTTP_200_OK)

class PasswordResetRequestView(generics.GenericAPIView):
    """
    Initiates password reset by generating a secure token and emailing a reset link.
    Guarantees account enumeration prevention by returning identical safe responses.
    Throttled to protect against abuse and excessive requests.
    """
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer
    throttle_classes = [PasswordResetRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email'].strip().lower()

        safe_message = "If an account exists with this email, you'll receive a password reset link shortly."

        try:
            users = User.objects.filter(email__iexact=email, is_active=True)
            for user in users:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173').rstrip('/')
                if not settings.DEBUG and frontend_url.startswith('http://'):
                    frontend_url = 'https://' + frontend_url[len('http://'):]
                reset_url = f"{frontend_url}/reset-password/{uid}/{token}"

                subject = "Reset your Resume Agent password"
                
                # Plain text version
                text_content = (
                    f"Hello,\n\n"
                    f"We received a request to reset your Resume Agent password.\n\n"
                    f"Click the link below to create a new password:\n"
                    f"{reset_url}\n\n"
                    f"If you did not request this password reset, you can safely ignore this email.\n\n"
                    f"— The Resume Agent Team"
                )

                # Professional HTML version with Resume Agent branding
                html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reset your Resume Agent password</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f9fafb; margin: 0; padding: 40px 16px; color: #0a1b33;">
  <div style="max-width: 560px; margin: 0 auto; background: #ffffff; border-radius: 16px; border: 1px solid #e5e7eb; overflow: hidden; box-shadow: 0 4px 20px -4px rgba(10, 27, 51, 0.05);">
    <div style="background-color: #0a152d; padding: 28px 32px; text-align: left;">
      <h1 style="color: #ffffff; font-size: 20px; font-weight: 700; margin: 0; letter-spacing: -0.02em;">
        Resume Agent
      </h1>
      <p style="color: #94a3b8; font-size: 13px; margin: 4px 0 0 0;">
        Intelligent career & resume analysis
      </p>
    </div>
    <div style="padding: 36px 32px;">
      <h2 style="font-size: 18px; font-weight: 600; color: #0a1b33; margin: 0 0 16px 0;">
        Reset your password
      </h2>
      <p style="font-size: 14px; line-height: 1.6; color: #475569; margin: 0 0 20px 0;">
        Hello,
      </p>
      <p style="font-size: 14px; line-height: 1.6; color: #475569; margin: 0 0 28px 0;">
        We received a request to reset your Resume Agent password. Click the button below to create a new password:
      </p>
      <div style="margin: 0 0 32px 0;">
        <a href="{reset_url}" style="display: inline-block; background-color: #0a152d; color: #ffffff; font-size: 14px; font-weight: 600; text-decoration: none; padding: 12px 28px; border-radius: 9999px; text-align: center;">
          Reset Password
        </a>
      </div>
      <p style="font-size: 13px; line-height: 1.6; color: #64748b; margin: 0 0 12px 0;">
        If the button above does not work, copy and paste this link into your browser:
      </p>
      <p style="font-size: 12px; line-height: 1.5; color: #0284c7; word-break: break-all; margin: 0 0 28px 0;">
        <a href="{reset_url}" style="color: #0284c7; text-decoration: underline;">{reset_url}</a>
      </p>
      <div style="border-top: 1px solid #f1f5f9; padding-top: 20px; margin-top: 20px;">
        <p style="font-size: 12px; line-height: 1.5; color: #94a3b8; margin: 0;">
          If you did not request this password reset, you can safely ignore this email. Your password will remain unchanged.
        </p>
      </div>
    </div>
  </div>
</body>
</html>"""

                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Resume Agent <noreply@resumeagent.ai>')
                msg = EmailMultiAlternatives(subject, text_content, from_email, [user.email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()

        except Exception as e:
            # Safe server logging without exposing credentials or internal traces to user
            logger.error("Error occurred while processing password reset email: %s: %s", type(e).__name__, str(e)[:150])

        # Always return the same safe message
        return Response({"message": safe_message}, status=status.HTTP_200_OK)

class PasswordResetConfirmView(generics.GenericAPIView):
    """
    Validates the password reset token and changes the user's password.
    Enforces Django's built-in password validation.
    """
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uid_b64 = serializer.validated_data['uid']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            uid = force_str(urlsafe_base64_decode(uid_b64))
            user = User.objects.get(pk=uid, is_active=True)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"detail": "This password reset link is invalid or has expired."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"detail": "This password reset link is invalid or has expired."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Enforce authoritative Django password validation
        try:
            validate_password(new_password, user=user)
        except DjangoValidationError as ve:
            return Response(
                {"detail": list(ve.messages)},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Your password has been reset successfully. You can now log in with your new password."},
            status=status.HTTP_200_OK
        )

