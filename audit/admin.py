from django.contrib import admin

from .models import AuditLog, DataAccessLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        'actor',
        'action',
        'object_representation',
        'ip_address',
        'request_path',
        'created_at',
    )

    list_filter = (
        'action',
        'content_type',
        'created_at',
    )

    search_fields = (
        'actor__username',
        'actor__first_name',
        'actor__last_name',
        'object_id',
        'object_representation',
        'request_path',
        'ip_address',
    )

    autocomplete_fields = ('actor',)

    readonly_fields = (
        'actor',
        'action',
        'content_type',
        'object_id',
        'object_representation',
        'changes',
        'metadata',
        'ip_address',
        'user_agent',
        'request_path',
        'created_at',
        'updated_at',
    )

    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(DataAccessLog)
class DataAccessLogAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'access_type',
        'resource_name',
        'records_count',
        'ip_address',
        'created_at',
    )

    list_filter = (
        'access_type',
        'created_at',
    )

    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'resource_name',
        'purpose',
        'ip_address',
    )

    autocomplete_fields = ('user',)

    readonly_fields = (
        'user',
        'access_type',
        'resource_name',
        'purpose',
        'records_count',
        'ip_address',
        'created_at',
        'updated_at',
    )

    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False