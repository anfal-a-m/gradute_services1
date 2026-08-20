from django.contrib import admin

from .models import Employer, EmployerContact, EmployerPartnership


class EmployerContactInline(admin.TabularInline):
    model = EmployerContact
    extra = 0
    fields = (
        'full_name',
        'job_title',
        'email',
        'phone_number',
        'is_primary',
        'is_active',
    )


@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = (
        'name_ar',
        'sector_type',
        'industry',
        'city',
        'is_verified',
        'is_active',
        'created_at',
    )

    list_filter = (
        'sector_type',
        'is_verified',
        'is_active',
        'country',
    )

    search_fields = (
        'name_ar',
        'name_en',
        'registration_number',
        'industry',
        'city',
    )

    readonly_fields = ('created_at', 'updated_at')

    inlines = (EmployerContactInline,)


@admin.register(EmployerContact)
class EmployerContactAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'employer',
        'job_title',
        'email',
        'phone_number',
        'is_primary',
        'is_active',
    )

    list_filter = (
        'is_primary',
        'is_active',
        'employer__sector_type',
    )

    search_fields = (
        'full_name',
        'email',
        'phone_number',
        'employer__name_ar',
        'employer__name_en',
    )

    autocomplete_fields = (
        'employer',
        'user',
    )

    readonly_fields = ('created_at', 'updated_at')


@admin.register(EmployerPartnership)
class EmployerPartnershipAdmin(admin.ModelAdmin):
    list_display = (
        'employer',
        'partnership_type',
        'status',
        'start_date',
        'end_date',
    )

    list_filter = (
        'partnership_type',
        'status',
    )

    search_fields = (
        'employer__name_ar',
        'employer__name_en',
        'notes',
    )

    autocomplete_fields = ('employer',)

    readonly_fields = ('created_at', 'updated_at')