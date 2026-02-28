# accounts/views.py

from django.core.mail import send_mail
from django.conf import settings

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# drf-spectacular imports
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

from .models import User
from .serializers import (
    StudentRegisterSerializer, InstructorRegisterSerializer, OTPVerifySerializer,
    ProfileSerializer, ForgotPasswordSerializer, ResetPasswordSerializer,
    ChangePasswordSerializer, CustomTokenObtainPairSerializer
)


@extend_schema(
    summary="Register new Student account",
    description="Creates a student account. An OTP is sent to the provided email for verification.",
    request=StudentRegisterSerializer,
    responses={
        201: OpenApiResponse(
            description="Account created – check email for OTP",
            response=StudentRegisterSerializer  # or custom dict serializer if you prefer
        ),
        400: "Validation error"
    },
    tags=['Authentication - Registration'],
    methods=['POST'],
    request_media_type='multipart/form-data',
)
class StudentRegisterView(APIView):
    def post(self, request):
        serializer = StudentRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Student account created successfully. Check your email for OTP.",
                "user_id": user.id,
                "email": user.email
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Register new Instructor account",
    description="Creates an instructor account. An OTP is sent to the provided email for verification.",
    request=InstructorRegisterSerializer,
    responses={
        201: OpenApiResponse(
            description="Account created – check email for OTP",
            response=InstructorRegisterSerializer
        ),
        400: "Validation error"
    },
    tags=['Authentication - Registration'],
    methods=['POST'],
    request_media_type='multipart/form-data',
)
class InstructorRegisterView(APIView):
    def post(self, request):
        serializer = InstructorRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Instructor account created successfully. Check your email for OTP.",
                "user_id": user.id,
                "email": user.email
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Verify email with OTP",
    description="Verifies the 6-digit OTP sent during registration.",
    request=OTPVerifySerializer,
    responses={
        200: OpenApiResponse(description="OTP verified successfully"),
        400: "Invalid/expired OTP or user not found"
    },
    tags=['Authentication'],
    methods=['POST'],
)
class OTPVerifyView(APIView):
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            try:
                user = User.objects.get(email=email)
                if user.verify_otp(otp):
                    return Response({"message": "Email verified successfully. You may now log in."})
                return Response({"error": "Invalid or expired OTP."}, status=400)
            except User.DoesNotExist:
                return Response({"error": "No account found with this email."}, status=400)
        return Response(serializer.errors, status=400)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(
    summary="Get current user profile",
    description="Returns the authenticated user's profile information.",
    responses=ProfileSerializer,
    tags=['Profile'],
    methods=['GET'],
)
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)


@extend_schema(
    summary="Update profile (including photo & documents)",
    description="Partially update the authenticated user's profile. Supports file uploads.",
    request=ProfileSerializer,
    responses=ProfileSerializer,
    tags=['Profile'],
    methods=['PATCH'],
    request_media_type='multipart/form-data',
)
class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


@extend_schema(
    summary="Request password reset OTP",
    description="Sends a password reset OTP to the provided email.",
    request=ForgotPasswordSerializer,
    responses={
        200: OpenApiResponse(description="OTP sent to email"),
        400: "Email not found or invalid"
    },
    tags=['Authentication'],
    methods=['POST'],
)
class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                otp = user.generate_otp()
                send_mail(
                    'Password Reset Request - Educator Platform',
                    f'Use this code to reset your password: {otp}\nValid for 5 minutes.',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                return Response({"message": "Password reset OTP sent to your email."})
            except User.DoesNotExist:
                return Response({"error": "No account found with this email."}, status=400)
        return Response(serializer.errors, status=400)


@extend_schema(
    summary="Reset password using OTP",
    description="Resets the password using a valid OTP.",
    request=ResetPasswordSerializer,
    responses={
        200: OpenApiResponse(description="Password reset successful"),
        400: "Invalid OTP or user not found"
    },
    tags=['Authentication'],
    methods=['POST'],
)
class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            password = serializer.validated_data['password']
            try:
                user = User.objects.get(email=email)
                if user.verify_otp(otp):
                    user.set_password(password)
                    user.save()
                    return Response({"message": "Password has been reset successfully."})
                return Response({"error": "Invalid or expired OTP."}, status=400)
            except User.DoesNotExist:
                return Response({"error": "No account found."}, status=400)
        return Response(serializer.errors, status=400)


@extend_schema(
    summary="Change password while logged in",
    description="Allows the authenticated user to change their password.",
    request=ChangePasswordSerializer,
    responses={
        200: OpenApiResponse(description="Password changed successfully"),
        400: "Invalid old password or mismatch"
    },
    tags=['Authentication'],
    methods=['POST'],
)
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"old_password": "Current password is incorrect."}, status=400)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Password changed successfully."})
        return Response(serializer.errors, status=400)


@extend_schema(
    summary="Logout and blacklist refresh token",
    description="Blacklists the provided refresh token to log the user out.",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'refresh': {'type': 'string', 'description': 'Refresh token to blacklist'}
            },
            'required': ['refresh']
        }
    },
    responses={
        200: OpenApiResponse(description="Logged out successfully"),
        400: "Invalid or missing refresh token"
    },
    tags=['Authentication'],
    methods=['POST'],
)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Refresh token is required."}, status=400)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully."})
        except Exception as e:
            return Response({"error": str(e)}, status=400)