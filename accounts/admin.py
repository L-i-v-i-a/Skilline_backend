# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import User


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'role')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    # List view columns
    list_display = (
        'username',
        'email',
        'role',
        'first_name',
        'last_name',
        'is_verified',
        'is_staff',
        'is_superuser',
        'date_joined',
    )
    list_display_links = ('username', 'email')

    # Filters on the right sidebar
    list_filter = (
        'role',
        'is_verified',
        'is_staff',
        'is_superuser',
        'date_joined',
    )

    # Search fields
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
        'matric_number',
        'department',
    )

    # Default ordering
    ordering = ('username',)

    # Fieldsets when viewing/editing an existing user
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (
            _('Personal Information'),
            {
                'fields': (
                    'first_name',
                    'last_name',
                    'email',
                    'phone_number',
                    'date_of_birth',
                    'address',
                    'bio',
                    'profile_image',
                )
            },
        ),
        (
            _('Role & Account Status'),
            {
                'fields': (
                    'role',
                    'is_verified',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            },
        ),
        (
            _('Student Information'),
            {
                'classes': ('collapse',),
                'fields': ('matric_number', 'major', 'student_id_document'),
            },
        ),
        (
            _('Instructor Information'),
            {
                'classes': ('collapse',),
                'fields': (
                    'department',
                    'expertise',
                    'years_experience',
                    'qualifications',
                    'resume',
                ),
            },
        ),
        (
            _('Permissions'),
            {
                'classes': ('collapse',),
                'fields': ('groups', 'user_permissions'),
            },
        ),
        (
            _('Important dates'),
            {'fields': ('last_login', 'date_joined')},
        ),
    )

    # Fields shown when adding a new user
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'username',
                    'email',
                    'password1',
                    'password2',
                    'role',
                    'first_name',
                    'last_name',
                    'phone_number',
                    'is_staff',
                    'is_superuser',
                ),
            },
        ),
    )

    # Read-only fields
    readonly_fields = ('last_login', 'date_joined', 'is_verified')

    # Custom admin actions
    actions = ['mark_as_verified']

    @admin.action(description="Mark selected users as email-verified")
    def mark_as_verified(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f"{updated} user(s) have been marked as verified.")