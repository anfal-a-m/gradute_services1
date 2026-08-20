import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from core.models import TimeStampedModel


class Survey(TimeStampedModel):
    """
    النموذج الرئيسي للاستبانة.
    """

    class Audience(models.TextChoices):
        GRADUATES = 'graduates', 'الخريجون'
        EMPLOYERS = 'employers', 'جهات التوظيف'
        BOTH = 'both', 'الخريجون وجهات التوظيف'

    class Category(models.TextChoices):
        GRADUATE_OUTCOMES = (
            'graduate_outcomes',
            'قياس مخرجات الخريجين',
        )
        EMPLOYER_SATISFACTION = (
            'employer_satisfaction',
            'رضا أصحاب العمل',
        )
        PROGRAM_EVALUATION = (
            'program_evaluation',
            'تقييم البرامج الأكاديمية',
        )
        TRAINING_NEEDS = (
            'training_needs',
            'الاحتياجات التدريبية',
        )
        GENERAL = 'general', 'استبانة عامة'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'مسودة'
        PUBLISHED = 'published', 'منشورة'
        CLOSED = 'closed', 'مغلقة'
        ARCHIVED = 'archived', 'مؤرشفة'

    title = models.CharField(
        max_length=250,
        verbose_name='عنوان الاستبانة',
    )

    description = models.TextField(
        blank=True,
        verbose_name='وصف الاستبانة',
    )

    audience = models.CharField(
        max_length=20,
        choices=Audience.choices,
        verbose_name='الفئة المستهدفة',
    )

    category = models.CharField(
        max_length=30,
        choices=Category.choices,
        default=Category.GENERAL,
        db_index=True,
        verbose_name='تصنيف الاستبانة',
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name='حالة الاستبانة',
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_surveys',
        verbose_name='أنشأها',
    )

    opens_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاريخ فتح الاستبانة',
    )

    closes_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاريخ إغلاق الاستبانة',
    )

    is_anonymous = models.BooleanField(
        default=False,
        verbose_name='استبانة مجهولة الهوية',
    )

    allow_multiple_responses = models.BooleanField(
        default=False,
        verbose_name='السماح بأكثر من استجابة',
    )

    thank_you_message = models.TextField(
        blank=True,
        verbose_name='رسالة الشكر بعد الإرسال',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'استبانة'
        verbose_name_plural = 'الاستبانات'

    def clean(self):
        """
        التحقق من أن تاريخ الإغلاق يأتي بعد تاريخ الفتح.
        """

        if self.opens_at and self.closes_at:
            if self.closes_at <= self.opens_at:
                raise ValidationError({
                    'closes_at': (
                        'تاريخ إغلاق الاستبانة يجب أن يلي تاريخ فتحها.'
                    ),
                })

    def __str__(self):
        return self.title


class SurveySection(TimeStampedModel):
    """
    أقسام الاستبانة؛ مثل البيانات العامة والتوظيف والرضا.
    """

    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='sections',
        verbose_name='الاستبانة',
    )

    title = models.CharField(
        max_length=250,
        verbose_name='عنوان القسم',
    )

    description = models.TextField(
        blank=True,
        verbose_name='وصف القسم',
    )

    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name='ترتيب العرض',
    )

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = 'قسم استبانة'
        verbose_name_plural = 'أقسام الاستبانة'

    def __str__(self):
        return f'{self.survey.title} - {self.title}'


class Question(TimeStampedModel):
    """
    الأسئلة الموجودة داخل أقسام الاستبانة.
    """

    class QuestionType(models.TextChoices):
        SHORT_TEXT = 'short_text', 'نص قصير'
        LONG_TEXT = 'long_text', 'نص طويل'
        SINGLE_CHOICE = 'single_choice', 'اختيار واحد'
        MULTIPLE_CHOICE = 'multiple_choice', 'اختيارات متعددة'
        RATING = 'rating', 'مقياس تقييم'
        NUMBER = 'number', 'رقم'
        DATE = 'date', 'تاريخ'
        BOOLEAN = 'boolean', 'نعم أو لا'

    section = models.ForeignKey(
        SurveySection,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='قسم الاستبانة',
    )

    text = models.TextField(
        verbose_name='نص السؤال',
    )

    question_type = models.CharField(
        max_length=30,
        choices=QuestionType.choices,
        verbose_name='نوع السؤال',
    )

    is_required = models.BooleanField(
        default=False,
        verbose_name='السؤال إجباري',
    )

    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name='ترتيب العرض',
    )

    help_text = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='نص مساعد',
    )

    validation_rules = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='قواعد التحقق',
    )

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = 'سؤال'
        verbose_name_plural = 'الأسئلة'

    def __str__(self):
        return self.text[:100]


class QuestionOption(TimeStampedModel):
    """
    خيارات أسئلة الاختيار الواحد أو المتعدد.
    """

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name='السؤال',
    )

    label = models.CharField(
        max_length=250,
        verbose_name='نص الخيار',
    )

    value = models.CharField(
        max_length=100,
        verbose_name='قيمة الخيار',
    )

    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name='ترتيب العرض',
    )

    class Meta:
        ordering = ['display_order', 'id']

        constraints = [
            models.UniqueConstraint(
                fields=['question', 'value'],
                name='unique_option_value_per_question',
            ),
        ]

        verbose_name = 'خيار سؤال'
        verbose_name_plural = 'خيارات الأسئلة'

    def __str__(self):
        return self.label


class SurveyInvitation(TimeStampedModel):
    """
    دعوة خريج أو مسؤول جهة توظيف للمشاركة في الاستبانة.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'بانتظار الإرسال'
        SENT = 'sent', 'مرسلة'
        OPENED = 'opened', 'تم فتحها'
        COMPLETED = 'completed', 'مكتملة'
        EXPIRED = 'expired', 'منتهية'

    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='invitations',
        verbose_name='الاستبانة',
    )

    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name='رمز الدعوة',
    )

    # العلاقة مكتوبة نصيًا لمنع أخطاء الاستيراد بين التطبيقات
    graduate = models.ForeignKey(
        'graduates.GraduateProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='survey_invitations',
        verbose_name='الخريج',
    )

    # العلاقة مكتوبة نصيًا لمنع أخطاء الاستيراد بين التطبيقات
    employer_contact = models.ForeignKey(
        'employers.EmployerContact',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='survey_invitations',
        verbose_name='مسؤول جهة التوظيف',
    )

    recipient_email = models.EmailField(
        blank=True,
        verbose_name='البريد الإلكتروني للمستلم',
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name='حالة الدعوة',
    )

    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاريخ إرسال الدعوة',
    )

    opened_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاريخ فتح الدعوة',
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاريخ انتهاء الدعوة',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'دعوة استبانة'
        verbose_name_plural = 'دعوات الاستبانات'

    def clean(self):
        """
        يجب أن ترتبط الدعوة بخريج أو مسؤول جهة أو بريد.
        """

        if not any([
            self.graduate,
            self.employer_contact,
            self.recipient_email,
        ]):
            raise ValidationError(
                'يجب تحديد خريج أو مسؤول جهة توظيف أو بريد مستلم.'
            )

    def __str__(self):
        return f'{self.survey.title} - {self.token}'


class SurveyResponse(TimeStampedModel):
    """
    استجابة الخريج أو جهة التوظيف للاستبانة.
    """

    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name='الاستبانة',
    )

    invitation = models.OneToOneField(
        SurveyInvitation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='response',
        verbose_name='دعوة الاستبانة',
    )

    graduate = models.ForeignKey(
        'graduates.GraduateProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='survey_responses',
        verbose_name='الخريج',
    )

    employer_contact = models.ForeignKey(
        'employers.EmployerContact',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='survey_responses',
        verbose_name='مسؤول جهة التوظيف',
    )

    is_complete = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name='الاستجابة مكتملة',
    )

    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='وقت بدء الاستجابة',
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='وقت إرسال الاستجابة',
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='عنوان IP',
    )

    class Meta:
        ordering = ['-started_at']
        verbose_name = 'استجابة استبانة'
        verbose_name_plural = 'استجابات الاستبانات'

    def clean(self):
        """
        التحقق من أن الدعوة والاستجابة تتبعان الاستبانة نفسها.
        """

        if self.invitation:
            if self.invitation.survey_id != self.survey_id:
                raise ValidationError({
                    'invitation': (
                        'الدعوة المحددة لا تنتمي إلى هذه الاستبانة.'
                    ),
                })

    def __str__(self):
        return f'{self.survey.title} - استجابة رقم {self.pk}'


class Answer(TimeStampedModel):
    """
    إجابة واحدة عن سؤال داخل استجابة الاستبانة.
    """

    response = models.ForeignKey(
        SurveyResponse,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='استجابة الاستبانة',
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.PROTECT,
        related_name='answers',
        verbose_name='السؤال',
    )

    text_value = models.TextField(
        blank=True,
        verbose_name='الإجابة النصية',
    )

    number_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='الإجابة الرقمية',
    )

    boolean_value = models.BooleanField(
        null=True,
        blank=True,
        verbose_name='إجابة نعم أو لا',
    )

    date_value = models.DateField(
        null=True,
        blank=True,
        verbose_name='إجابة التاريخ',
    )

    selected_options = models.ManyToManyField(
        QuestionOption,
        blank=True,
        related_name='selected_in_answers',
        verbose_name='الخيارات المحددة',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['response', 'question'],
                name='unique_answer_per_response_question',
            ),
        ]

        verbose_name = 'إجابة'
        verbose_name_plural = 'الإجابات'

    def clean(self):
        """
        التحقق من أن السؤال يتبع الاستبانة المرتبطة بالاستجابة.
        """

        if self.response_id and self.question_id:
            question_survey_id = self.question.section.survey_id

            if question_survey_id != self.response.survey_id:
                raise ValidationError({
                    'question': (
                        'السؤال المحدد لا ينتمي إلى استبانة الاستجابة.'
                    ),
                })

    def __str__(self):
        return f'إجابة السؤال رقم {self.question_id}'