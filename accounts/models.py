from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.cache import cache
import random
import string
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('admin', 'Admin'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    # Student-specific
    matric_number = models.CharField(
        max_length=20, blank=True, null=True, unique=True,
        help_text="Matriculation / Registration number (required for students)"
    )
    major = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Field of study / Major"
    )
    student_id_document = models.FileField(
        upload_to='student_docs/', blank=True, null=True,
        help_text="Student ID card, admission letter or proof of enrollment"
    )

    # Instructor-specific
    department = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Department / Faculty"
    )
    expertise = models.TextField(blank=True, null=True)
    years_experience = models.PositiveIntegerField(default=0, blank=True)
    qualifications = models.TextField(blank=True, null=True)
    resume = models.FileField(
        upload_to='instructor_docs/', blank=True, null=True,
        help_text="CV / Resume / Academic credentials"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        name = self.get_full_name() or self.username
        return f"{name} ({self.role})"

    @property
    def is_student(self):
        return self.role == 'student'

    @property
    def is_instructor(self):
        return self.role == 'instructor'

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    def generate_otp(self):
        otp = ''.join(random.choices(string.digits, k=6))
        cache_key = f"otp_{self.email}_{timezone.now().strftime('%Y%m%d%H')}"
        cache.set(cache_key, otp, timeout=300)  # 5 minutes
        return otp

    def verify_otp(self, otp):
        cache_key = f"otp_{self.email}_{timezone.now().strftime('%Y%m%d%H')}"
        cached_otp = cache.get(cache_key)
        if cached_otp and cached_otp == otp:
            self.is_verified = True
            self.save(update_fields=['is_verified'])
            cache.delete(cache_key)
            return True
        return False