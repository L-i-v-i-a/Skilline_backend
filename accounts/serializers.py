from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.mail import send_mail
from django.conf import settings
from .models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        if not user.is_verified:
            raise serializers.ValidationError(
                {"detail": "Account email not verified. Please complete OTP verification."}
            )

        # Login notification
        send_mail(
            subject="New Login Detected - Educator Platform",
            message=(
                f"Dear {user.get_full_name() or user.username},\n\n"
                f"We detected a new login to your account on {user.last_login.strftime('%Y-%m-%d %H:%M:%S')}.\n"
                "If this was not you, please change your password immediately.\n\n"
                "Best regards,\nEducator Team"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )

        data['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'profile_image_url': user.profile_image.url if user.profile_image else None,
        }
        return data


class BaseRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, label="Confirm password", style={'input_type': 'password'})
    profile_image = serializers.ImageField(required=False, allow_null=True)
    date_of_birth = serializers.DateField(required=False)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password2', 'first_name', 'last_name',
            'phone_number', 'date_of_birth', 'address', 'bio', 'profile_image'
        ]

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        role = self.context['role']
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data.pop('username'),
            email=validated_data.pop('email'),
            password=validated_data.pop('password'),
            role=role,
            **validated_data
        )

        otp = user.generate_otp()
        send_mail(
            'Your Educator Account Verification OTP',
            f'Welcome to Educator!\n\nYour verification code is: {otp}\nThis code expires in 5 minutes.',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return user


class StudentRegisterSerializer(BaseRegisterSerializer):
    
    matric_number = serializers.CharField(max_length=20, required=True)
    major = serializers.CharField(max_length=100, required=False)
    student_id_document = serializers.FileField(required=False, allow_null=True)

    class Meta(BaseRegisterSerializer.Meta):
        fields = BaseRegisterSerializer.Meta.fields + ['matric_number', 'major', 'student_id_document']


class InstructorRegisterSerializer(BaseRegisterSerializer):
    department = serializers.CharField(max_length=100, required=True)
    expertise = serializers.CharField(required=True)
    years_experience = serializers.IntegerField(min_value=0, required=False)
    qualifications = serializers.CharField(required=False)
    resume = serializers.FileField(required=False, allow_null=True)

    class Meta(BaseRegisterSerializer.Meta):
        fields = BaseRegisterSerializer.Meta.fields + [
            'department', 'expertise', 'years_experience', 'qualifications', 'resume'
        ]


class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(max_length=6, required=True)


class ProfileSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(required=False, allow_null=True)
    student_id_document = serializers.FileField(required=False, allow_null=True)
    resume = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'role',
            'phone_number', 'date_of_birth', 'address', 'bio', 'profile_image',
            'matric_number', 'major', 'student_id_document',
            'department', 'expertise', 'years_experience', 'qualifications', 'resume'
        ]
        read_only_fields = ['email', 'role', 'matric_number', 'department']


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(max_length=6, required=True)
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=8)
    new_password2 = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({"new_password": "New passwords do not match."})
        return data