from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, UserConsent


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'full_name_display',
        'email',
        'university_id',
        'role',
        'email_verified',
        'is_active',
        'is_staff',
    )

    list_filter = (
        'role',
        'email_verified',
        'preferred_language',
        'is_active',
        'is_staff',
        'is_superuser',
    )

    search_fields = (
        'username',
        'first_name',
        'last_name',
        'email',
        'university_id',
        'phone_number',
    )

    ordering = (
        'first_name',
        'last_name',
        'username',
    )

    readonly_fields = (
        'last_login',
        'date_joined',
        'created_at',
        'updated_at',
    )

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            'بيانات بوابة الخريجين',
            {
                'fields': (
                    'role',
                    'university_id',
                    'phone_number',
                    'preferred_language',
                    'email_verified',
                    'must_change_password',
                    'created_at',
                    'updated_at',
                ),
            },
        ),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            'بيانات بوابة الخريجين',
            {
                'fields': (
                    'first_name',
                    'last_name',
                    'email',
                    'role',
                    'university_id',
                    'phone_number',
                    'preferred_language',
                    'email_verified',
                    'must_change_password',
                ),
            },
        ),
    )

    @admin.display(description='الاسم الكامل')
    def full_name_display(self, obj):
        return obj.get_full_name() or '—'


@admin.register(UserConsent)
class UserConsentAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'consent_type',
        'document_version',
        'is_granted',
        'granted_at',
        'revoked_at',
    )

    list_filter = (
        'consent_type',
        'is_granted',
        'document_version',
    )

    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__email',
        'user__university_id',
    )

    autocomplete_fields = ('user',)

    readonly_fields = (
        'granted_at',
        'created_at',
        'updated_at',
    )