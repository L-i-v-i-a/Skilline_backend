# courses/admin.py
from django.contrib import admin
from .models import Course, Enrollment, Assignment, Submission, Payment, Notification


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'price', 'created_at', 'is_active')
    list_filter = ('is_active', 'instructor')
    search_fields = ('title', 'description')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at', 'is_paid')
    list_filter = ('is_paid',)
    search_fields = ('student__username', 'course__title')


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'due_date', 'created_at')
    list_filter = ('course',)
    search_fields = ('title', 'description')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'submitted_at', 'grade')
    list_filter = ('assignment__course',)
    search_fields = ('student__username', 'assignment__title')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'amount', 'status', 'transaction_id', 'paid_at')
    list_filter = ('status',)
    search_fields = ('transaction_id', 'enrollment__student__username')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read',)
    search_fields = ('user__username', 'message')