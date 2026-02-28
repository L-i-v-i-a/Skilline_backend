from django.shortcuts import render
from django.core.mail import send_mail

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView, settings
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import User
from .serializers import (
    StudentRegisterSerializer, InstructorRegisterSerializer, OTPVerifySerializer,
    ProfileSerializer, ForgotPasswordSerializer, ResetPasswordSerializer,
    ChangePasswordSerializer, CustomTokenObtainPairSerializer
)


class StudentRegisterView(APIView):
    @swagger_auto_schema(
        operation_summary="Register new Student account",
        operation_description="Creates a student account. OTP is sent to email for verification.",
        request_body=StudentRegisterSerializer,
        tags=['Authentication - Registration'],
        consumes=['multipart/form-data'],
    )
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


class InstructorRegisterView(APIView):
    @swagger_auto_schema(
        operation_summary="Register new Instructor account",
        operation_description="Creates an instructor account. OTP is sent to email for verification.",
        request_body=InstructorRegisterSerializer,
        tags=['Authentication - Registration'],
        consumes=['multipart/form-data'],
    )
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


class OTPVerifyView(APIView):
    @swagger_auto_schema(
        operation_summary="Verify email with OTP",
        request_body=OTPVerifySerializer,
        tags=['Authentication'],
    )
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


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary="Get current user profile", tags=['Profile'])
    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)


class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Update profile (including photo & documents)",
        request_body=ProfileSerializer,
        tags=['Profile'],
        consumes=['multipart/form-data'],
    )
    def patch(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class ForgotPasswordView(APIView):
    @swagger_auto_schema(
        operation_summary="Request password reset OTP",
        request_body=ForgotPasswordSerializer,
        tags=['Authentication'],
    )
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


class ResetPasswordView(APIView):
    @swagger_auto_schema(
        operation_summary="Reset password using OTP",
        request_body=ResetPasswordSerializer,
        tags=['Authentication'],
    )
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


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Change password while logged in",
        request_body=ChangePasswordSerializer,
        tags=['Authentication'],
    )
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


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary="Logout and blacklist refresh token", tags=['Authentication'])
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