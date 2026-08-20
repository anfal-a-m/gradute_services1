from django.contrib import admin

from .models import (
    DevelopmentProgram,
    ProgramCertificate,
    ProgramRegistration,
    ProgramSession,
    SessionAttendance,
)


class ProgramSessionInline(admin.TabularInline):
    model = ProgramSession
    extra = 0


@admin.register(DevelopmentProgram)
class DevelopmentProgramAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'title',
        'program_type',
        'delivery_mode',
        'status',
        'starts_at',
        'capacity',
    )

    list_filter = (
        'program_type',
        'delivery_mode',
        'status',
    )

    search_fields = (
        'code',
        'title',
        'description',
    )

    autocomplete_fields = ('created_by',)

    filter_horizontal = ('target_academic_programs',)

    readonly_fields = ('created_at', 'updated_at')

    inlines = (ProgramSessionInline,)


@admin.register(ProgramSession)
class ProgramSessionAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'program',
        'trainer_name',
        'starts_at',
        'ends_at',
    )

    list_filter = ('program',)

    search_fields = (
        'title',
        'program__title',
        'trainer_name',
    )

    autocomplete_fields = ('program',)

    readonly_fields = ('created_at', 'updated_at')


@admin.register(ProgramRegistration)
class ProgramRegistrationAdmin(admin.ModelAdmin):
    list_display = (
        'graduate',
        'program',
        'status',
        'registered_at',
        'completion_percentage',
    )

    list_filter = (
        'status',
        'program',
    )

    search_fields = (
        'graduate__user__username',
        'graduate__user__first_name',
        'graduate__user__last_name',
        'program__title',
        'program__code',
    )

    autocomplete_fields = (
        'program',
        'graduate',
    )

    readonly_fields = (
        'registered_at',
        'created_at',
        'updated_at',
    )


@admin.register(SessionAttendance)
class SessionAttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'registration',
        'session',
        'attended',
        'checked_in_at',
    )

    list_filter = (
        'attended',
        'session__program',
    )

    search_fields = (
        'registration__graduate__user__username',
        'registration__graduate__user__first_name',
        'registration__graduate__user__last_name',
        'session__title',
    )

    autocomplete_fields = (
        'registration',
        'session',
    )

    readonly_fields = ('created_at', 'updated_at')


@admin.register(ProgramCertificate)
class ProgramCertificateAdmin(admin.ModelAdmin):
    list_display = (
        'registration',
        'verification_code',
        'issued_at',
    )

    search_fields = (
        'verification_code',
        'registration__graduate__user__username',
        'registration__graduate__user__first_name',
        'registration__graduate__user__last_name',
        'registration__program__title',
    )

    autocomplete_fields = ('registration',)

    readonly_fields = (
        'verification_code',
        'issued_at',
        'created_at',
        'updated_at',
    )