from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    StudentRegisterView, InstructorRegisterView, OTPVerifyView,
    CustomTokenObtainPairView, ProfileView, UpdateProfileView,
    ForgotPasswordView, ResetPasswordView, ChangePasswordView, LogoutView
)

urlpatterns = [
    # Registration
    path('register/student/',    StudentRegisterView.as_view(),    name='register-student'),
    path('register/instructor/', InstructorRegisterView.as_view(), name='register-instructor'),

    # Verification & Auth
    path('verify-otp/',          OTPVerifyView.as_view(),          name='verify-otp'),
    path('login/',               CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/',       TokenRefreshView.as_view(),      name='token-refresh'),

    # Profile
    path('profile/',             ProfileView.as_view(),            name='profile-detail'),
    path('profile/update/',      UpdateProfileView.as_view(),      name='profile-update'),

    # Password management
    path('forgot-password/',     ForgotPasswordView.as_view(),     name='forgot-password'),
    path('reset-password/',      ResetPasswordView.as_view(),      name='reset-password'),
    path('change-password/',     ChangePasswordView.as_view(),     name='change-password'),

    # Logout
    path('logout/',              LogoutView.as_view(),             name='logout'),
]