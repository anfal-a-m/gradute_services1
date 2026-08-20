from django.contrib import admin

from .models import MetricSnapshot, ReportExport, SavedReport


@admin.register(SavedReport)
class SavedReportAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'report_type',
        'created_by',
        'is_public_to_staff',
        'created_at',
    )

    list_filter = (
        'report_type',
        'is_public_to_staff',
    )

    search_fields = (
        'name',
        'created_by__username',
        'created_by__first_name',
        'created_by__last_name',
    )

    autocomplete_fields = ('created_by',)

    filter_horizontal = ('shared_with',)

    readonly_fields = (
        'created_at',
        'updated_at',
    )


@admin.register(ReportExport)
class ReportExportAdmin(admin.ModelAdmin):
    list_display = (
        'report',
        'requested_by',
        'export_format',
        'status',
        'expires_at',
        'created_at',
    )

    list_filter = (
        'export_format',
        'status',
    )

    search_fields = (
        'report__name',
        'requested_by__username',
        'requested_by__first_name',
        'requested_by__last_name',
    )

    autocomplete_fields = (
        'report',
        'requested_by',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )


@admin.register(MetricSnapshot)
class MetricSnapshotAdmin(admin.ModelAdmin):
    list_display = (
        'metric_code',
        'metric_name',
        'scope',
        'value',
        'calculated_at',
    )

    list_filter = (
        'metric_code',
        'scope',
    )

    search_fields = (
        'metric_code',
        'metric_name',
        'scope',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )