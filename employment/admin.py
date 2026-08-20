from django.contrib import admin

from .models import (
    EmploymentRecord,
    FurtherStudyRecord,
    GraduateCareerStatus,
    JobPreference,
)


@admin.register(GraduateCareerStatus)
class GraduateCareerStatusAdmin(admin.ModelAdmin):
    list_display = (
        'graduate',
        'status',
        'available_for_opportunities',
        'status_since',
        'updated_at',
    )

    list_filter = (
        'status',
        'available_for_opportunities',
    )

    search_fields = (
        'graduate__user__username',
        'graduate__user__first_name',
        'graduate__user__last_name',
        'graduate__user__university_id',
    )

    autocomplete_fields = ('graduate',)

    readonly_fields = ('created_at', 'updated_at')


@admin.register(EmploymentRecord)
class EmploymentRecordAdmin(admin.ModelAdmin):
    list_display = (
        'graduate',
        'job_title',
        'employer_display',
        'employment_type',
        'city',
        'is_current',
        'is_primary',
        'related_to_specialization',
    )

    list_filter = (
        'employment_type',
        'is_current',
        'is_primary',
        'related_to_specialization',
        'country',
        'city',
    )

    search_fields = (
        'graduate__user__username',
        'graduate__user__first_name',
        'graduate__user__last_name',
        'graduate__user__university_id',
        'job_title',
        'employer__name_ar',
        'employer_name',
    )

    autocomplete_fields = (
        'graduate',
        'employer',
    )

    readonly_fields = ('created_at', 'updated_at')

    @admin.display(description='جهة العمل')
    def employer_display(self, obj):
        if obj.employer:
            return obj.employer.name_ar

        return obj.employer_name or '—'


@admin.register(JobPreference)
class JobPreferenceAdmin(admin.ModelAdmin):
    list_display = (
        'graduate',
        'accepts_remote_work',
        'accepts_relocation',
        'expected_salary_range',
        'updated_at',
    )

    list_filter = (
        'accepts_remote_work',
        'accepts_relocation',
    )

    search_fields = (
        'graduate__user__username',
        'graduate__user__first_name',
        'graduate__user__last_name',
        'desired_job_titles',
        'preferred_cities',
        'preferred_sectors',
    )

    autocomplete_fields = ('graduate',)

    readonly_fields = ('created_at', 'updated_at')


@admin.register(FurtherStudyRecord)
class FurtherStudyRecordAdmin(admin.ModelAdmin):
    list_display = (
        'graduate',
        'institution_name',
        'program_name',
        'degree_level',
        'country',
        'status',
        'start_date',
    )

    list_filter = (
        'status',
        'degree_level',
        'country',
    )

    search_fields = (
        'graduate__user__username',
        'graduate__user__first_name',
        'graduate__user__last_name',
        'institution_name',
        'program_name',
    )

    autocomplete_fields = ('graduate',)

    readonly_fields = ('created_at', 'updated_at')