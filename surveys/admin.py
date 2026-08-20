from django.contrib import admin

from .models import (
    Answer,
    Question,
    QuestionOption,
    Survey,
    SurveyInvitation,
    SurveyResponse,
    SurveySection,
)


class SurveySectionInline(admin.TabularInline):
    model = SurveySection
    extra = 0
    fields = (
        'title',
        'display_order',
    )


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 0
    fields = (
        'label',
        'value',
        'display_order',
    )


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'audience',
        'category',
        'status',
        'opens_at',
        'closes_at',
        'created_by',
    )

    list_filter = (
        'audience',
        'category',
        'status',
        'is_anonymous',
        'allow_multiple_responses',
    )

    search_fields = (
        'title',
        'description',
        'created_by__username',
        'created_by__first_name',
        'created_by__last_name',
    )

    autocomplete_fields = ('created_by',)

    readonly_fields = ('created_at', 'updated_at')

    inlines = (SurveySectionInline,)


@admin.register(SurveySection)
class SurveySectionAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'survey',
        'display_order',
    )

    list_filter = ('survey',)

    search_fields = (
        'title',
        'survey__title',
    )

    autocomplete_fields = ('survey',)

    readonly_fields = ('created_at', 'updated_at')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        'short_question',
        'section',
        'question_type',
        'is_required',
        'display_order',
    )

    list_filter = (
        'question_type',
        'is_required',
        'section__survey',
    )

    search_fields = (
        'text',
        'section__title',
        'section__survey__title',
    )

    autocomplete_fields = ('section',)

    readonly_fields = ('created_at', 'updated_at')

    inlines = (QuestionOptionInline,)

    @admin.display(description='السؤال')
    def short_question(self, obj):
        return obj.text[:80]


@admin.register(QuestionOption)
class QuestionOptionAdmin(admin.ModelAdmin):
    list_display = (
        'label',
        'question',
        'value',
        'display_order',
    )

    search_fields = (
        'label',
        'value',
        'question__text',
    )

    autocomplete_fields = ('question',)

    readonly_fields = ('created_at', 'updated_at')


@admin.register(SurveyInvitation)
class SurveyInvitationAdmin(admin.ModelAdmin):
    list_display = (
        'survey',
        'recipient_display',
        'status',
        'sent_at',
        'opened_at',
        'expires_at',
    )

    list_filter = (
        'status',
        'survey',
    )

    search_fields = (
        'survey__title',
        'recipient_email',
        'graduate__user__username',
        'graduate__user__first_name',
        'graduate__user__last_name',
        'employer_contact__full_name',
        'employer_contact__email',
        'token',
    )

    autocomplete_fields = (
        'survey',
        'graduate',
        'employer_contact',
    )

    readonly_fields = (
        'token',
        'created_at',
        'updated_at',
    )

    @admin.display(description='المستلم')
    def recipient_display(self, obj):
        return (
            obj.graduate
            or obj.employer_contact
            or obj.recipient_email
            or '—'
        )


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'survey',
        'respondent_display',
        'is_complete',
        'started_at',
        'submitted_at',
    )

    list_filter = (
        'is_complete',
        'survey',
    )

    search_fields = (
        'survey__title',
        'graduate__user__username',
        'graduate__user__first_name',
        'graduate__user__last_name',
        'employer_contact__full_name',
        'invitation__token',
    )

    autocomplete_fields = (
        'survey',
        'invitation',
        'graduate',
        'employer_contact',
    )

    readonly_fields = (
        'started_at',
        'created_at',
        'updated_at',
    )

    @admin.display(description='المجيب')
    def respondent_display(self, obj):
        return obj.graduate or obj.employer_contact or 'مجهول'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'response',
        'question',
        'answer_preview',
    )

    search_fields = (
        'response__survey__title',
        'question__text',
        'text_value',
    )

    autocomplete_fields = (
        'response',
        'question',
    )

    filter_horizontal = ('selected_options',)

    readonly_fields = ('created_at', 'updated_at')

    @admin.display(description='الإجابة')
    def answer_preview(self, obj):
        if obj.text_value:
            return obj.text_value[:80]

        if obj.number_value is not None:
            return obj.number_value

        if obj.boolean_value is not None:
            return 'نعم' if obj.boolean_value else 'لا'

        if obj.date_value:
            return obj.date_value

        return 'اختيارات'

# Register your models here.
