from django.contrib import admin

from .models import (
    GraduateDocument,
    GraduateProfile,
    GraduateSkill,
    Skill,
)


class GraduateSkillInline(admin.TabularInline):
    model = GraduateSkill
    extra = 0
    autocomplete_fields = ('skill',)


class GraduateDocumentInline(admin.TabularInline):
    model = GraduateDocument
    extra = 0


@admin.register(GraduateProfile)
class GraduateProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'primary_phone',
        'personal_email',
        'city',
        'profile_status',
        'completion_percentage',
        'updated_at',
    )

    list_filter = (
        'gender',
        'profile_status',
        'country',
        'city',
        'allow_email_contact',
        'allow_sms_contact',
    )

    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__email',
        'user__university_id',
        'personal_email',
        'primary_phone',
    )

    autocomplete_fields = ('user',)

    readonly_fields = ('created_at', 'updated_at')

    inlines = (
        GraduateSkillInline,
        GraduateDocumentInline,
    )


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = (
        'name_ar',
        'name_en',
        'is_active',
    )

    list_filter = ('is_active',)

    search_fields = (
        'name_ar',
        'name_en',
    )

    list_editable = ('is_active',)

    readonly_fields = ('created_at', 'updated_at')


@admin.register(GraduateSkill)
class GraduateSkillAdmin(admin.ModelAdmin):
    list_display = (
        'graduate',
        'skill',
        'proficiency_level',
    )

    list_filter = (
        'proficiency_level',
        'skill',
    )

    search_fields = (
        'graduate__user__username',
        'graduate__user__first_name',
        'graduate__user__last_name',
        'skill__name_ar',
        'skill__name_en',
    )

    autocomplete_fields = (
        'graduate',
        'skill',
    )

    readonly_fields = ('created_at', 'updated_at')


@admin.register(GraduateDocument)
class GraduateDocumentAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'graduate',
        'document_type',
        'is_visible_to_employers',
        'created_at',
    )

    list_filter = (
        'document_type',
        'is_visible_to_employers',
    )

    search_fields = (
        'title',
        'graduate__user__username',
        'graduate__user__first_name',
        'graduate__user__last_name',
    )

    autocomplete_fields = ('graduate',)

    readonly_fields = ('created_at', 'updated_at')