from django.contrib import admin
from django.utils.html import format_html
from .models import Course, Enrollment, Assignment, Submission, Payment, Notification, CourseMaterial


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0
    readonly_fields = ('enrolled_at', 'is_paid')
    fields = ('student', 'enrolled_at', 'is_paid')
    can_delete = False
    show_change_link = True


class SubmissionInline(admin.TabularInline):
    model = Submission
    extra = 0
    readonly_fields = ('submitted_at', 'grade', 'feedback')
    fields = ('student', 'submitted_at', 'grade', 'feedback')
    can_delete = False
    show_change_link = True


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor_link', 'price', 'enrollment_count', 'created_at', 'is_active')
    list_filter = ('is_active', 'instructor', 'created_at')
    search_fields = ('title', 'description', 'instructor__username', 'instructor__first_name', 'instructor__last_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [EnrollmentInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'instructor', 'price', 'is_active')
        }),
        ('Media', {
            'fields': ('cover_image', 'intro_video')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    list_per_page = 20

    def instructor_link(self, obj):
        return format_html('<a href="/admin/accounts/user/{}/change/">{}</a>', obj.instructor.id, obj.instructor.get_full_name())
    instructor_link.short_description = 'Instructor'

    def enrollment_count(self, obj):
        return obj.enrollments.count()
    enrollment_count.short_description = 'Enrollments'


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student_link', 'course_link', 'enrolled_at', 'is_paid')
    list_filter = ('is_paid', 'enrolled_at', 'course')
    search_fields = ('student__username', 'student__first_name', 'student__last_name', 'course__title')
    readonly_fields = ('enrolled_at',)
    list_per_page = 25

    def student_link(self, obj):
        return format_html('<a href="/admin/accounts/user/{}/change/">{}</a>', obj.student.id, obj.student.get_full_name())
    student_link.short_description = 'Student'

    def course_link(self, obj):
        return format_html('<a href="/admin/courses/course/{}/change/">{}</a>', obj.course.id, obj.course.title)
    course_link.short_description = 'Course'


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course_link', 'due_date', 'max_score', 'created_at')
    list_filter = ('course', 'due_date', 'created_at')
    search_fields = ('title', 'description', 'course__title')
    readonly_fields = ('created_at',)
    inlines = [SubmissionInline]
    ordering = ('-created_at',)
    list_per_page = 20

    def course_link(self, obj):
        return format_html('<a href="/admin/courses/course/{}/change/">{}</a>', obj.course.id, obj.course.title)
    course_link.short_description = 'Course'


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment_link', 'student_link', 'submitted_at', 'grade', 'has_feedback')
    list_filter = ('assignment__course', 'submitted_at', 'grade')
    search_fields = ('student__username', 'assignment__title', 'feedback')
    readonly_fields = ('submitted_at',)
    ordering = ('-submitted_at',)
    list_per_page = 25

    def assignment_link(self, obj):
        return format_html('<a href="/admin/courses/assignment/{}/change/">{}</a>', obj.assignment.id, obj.assignment.title)
    assignment_link.short_description = 'Assignment'

    def student_link(self, obj):
        return format_html('<a href="/admin/accounts/user/{}/change/">{}</a>', obj.student.id, obj.student.get_full_name())
    student_link.short_description = 'Student'

    def has_feedback(self, obj):
        return bool(obj.feedback)
    has_feedback.boolean = True
    has_feedback.short_description = 'Has Feedback'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('enrollment_link', 'amount', 'status_colored', 'transaction_id', 'paid_at')
    list_filter = ('status', 'paid_at')
    search_fields = ('transaction_id', 'enrollment__student__username', 'enrollment__course__title')
    readonly_fields = ('paid_at', 'metadata')
    ordering = ('-paid_at',)
    list_per_page = 20

    def enrollment_link(self, obj):
        return format_html('<a href="/admin/courses/enrollment/{}/change/">{} - {}</a>',
                           obj.enrollment.id,
                           obj.enrollment.student.get_full_name(),
                           obj.enrollment.course.title)
    enrollment_link.short_description = 'Enrollment'

    def status_colored(self, obj):
        color_map = {
            'success': 'green',
            'failed': 'red',
            'pending': 'orange',
        }
        color = color_map.get(obj.status, 'gray')
        return format_html('<span style="color: {};">{}</span>', color, obj.get_status_display())
    status_colored.short_description = 'Status'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user_link', 'message_truncated', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'message')
    readonly_fields = ('created_at',)
    actions = ['mark_as_read', 'mark_as_unread']
    ordering = ('-created_at',)
    list_per_page = 25

    def user_link(self, obj):
        return format_html('<a href="/admin/accounts/user/{}/change/">{}</a>',
                           obj.user.id,
                           obj.user.get_full_name() or obj.user.username)
    user_link.short_description = 'User'

    def message_truncated(self, obj):
        return (obj.message[:75] + '...') if len(obj.message) > 75 else obj.message
    message_truncated.short_description = 'Message'

    @admin.action(description="Mark selected notifications as read")
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description="Mark selected notifications as unread")
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        
# Update admin.py to include CourseMaterial
# courses/admin.py (add to existing)

@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'course_link', 'created_at', 'is_public')
    list_filter = ('course', 'is_public', 'created_at')
    search_fields = ('title', 'description', 'course__title')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    def course_link(self, obj):
        return format_html('<a href="/admin/courses/course/{}/change/">{}</a>', obj.course.id, obj.course.title)
    course_link.short_description = 'Course'