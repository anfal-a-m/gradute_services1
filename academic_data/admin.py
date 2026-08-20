from django.contrib import admin

from .models import (
    AcademicProgram,
    College,
    Department,
    GraduateAcademicRecord,
    GraduationCohort,
)


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'name_ar',
        'name_en',
        'is_active',
    )

    list_filter = ('is_active',)

    search_fields = (
        'code',
        'name_ar',
        'name_en',
    )

    list_editable = ('is_active',)

    readonly_fields = ('created_at', 'updated_at')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'name_ar',
        'college',
        'is_active',
    )

    list_filter = (
        'is_active',
        'college',
    )

    search_fields = (
        'code',
        'name_ar',
        'name_en',
        'college__name_ar',
    )

    autocomplete_fields = ('college',)

    readonly_fields = ('created_at', 'updated_at')


@admin.register(AcademicProgram)
class AcademicProgramAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'name_ar',
        'department',
        'degree_level',
        'is_active',
    )

    list_filter = (
        'degree_level',
        'is_active',
        'department__college',
    )

    search_fields = (
        'code',
        'name_ar',
        'name_en',
        'department__name_ar',
    )

    autocomplete_fields = ('department',)

    readonly_fields = ('created_at', 'updated_at')


@admin.register(GraduationCohort)
class GraduationCohortAdmin(admin.ModelAdmin):
    list_display = (
        'academic_year',
        'semester',
        'graduation_date',
    )

    list_filter = (
        'academic_year',
        'semester',
    )

    search_fields = (
        'academic_year',
        'semester',
    )

    readonly_fields = ('created_at', 'updated_at')


@admin.register(GraduateAcademicRecord)
class GraduateAcademicRecordAdmin(admin.ModelAdmin):
    list_display = (
        'student_number',
        'full_name_ar',
        'program',
        'cohort',
        'gpa',
        'graduation_date',
        'is_verified',
    )

    list_filter = (
        'is_verified',
        'program__degree_level',
        'program__department__college',
        'cohort',
    )

    search_fields = (
        'student_number',
        'full_name_ar',
        'full_name_en',
        'user__username',
        'user__email',
        'program__name_ar',
    )

    autocomplete_fields = (
        'user',
        'program',
        'cohort',
    )

    readonly_fields = ('created_at', 'updated_at')