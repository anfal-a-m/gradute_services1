from django.conf import settings
from django.core.validators import FileExtensionValidator, RegexValidator
from django.db import models

from core.models import TimeStampedModel


phone_validator = RegexValidator(
    regex=r'^\+?[0-9]{8,15}$',
    message='أدخل رقم هاتف صحيحًا، ويمكن أن يبدأ بعلامة +.',
)


def graduate_document_path(instance, filename):
    return f'graduates/{instance.graduate.user_id}/documents/{filename}'


class GraduateProfile(TimeStampedModel):
    class Gender(models.TextChoices):
        MALE = 'male', 'ذكر'
        FEMALE = 'female', 'أنثى'
        NOT_SPECIFIED = 'not_specified', 'غير محدد'

    class ProfileStatus(models.TextChoices):
        INCOMPLETE = 'incomplete', 'غير مكتمل'
        COMPLETE = 'complete', 'مكتمل'
        NEEDS_REVIEW = 'needs_review', 'يحتاج مراجعة'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='graduate_profile',
        verbose_name='المستخدم',
    )
    gender = models.CharField(
        max_length=20,
        choices=Gender.choices,
        default=Gender.NOT_SPECIFIED,
        verbose_name='الجنس',
    )
    personal_email = models.EmailField(
        blank=True,
        verbose_name='البريد الشخصي',
    )
    primary_phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[phone_validator],
        verbose_name='رقم الجوال',
    )
    alternative_phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[phone_validator],
        verbose_name='رقم جوال بديل',
    )
    country = models.CharField(
        max_length=100,
        default='المملكة العربية السعودية',
        verbose_name='الدولة',
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='المدينة',
    )
    address = models.TextField(
        blank=True,
        verbose_name='العنوان',
    )
    linkedin_url = models.URLField(
        blank=True,
        verbose_name='حساب LinkedIn',
    )
    portfolio_url = models.URLField(
        blank=True,
        verbose_name='الموقع أو معرض الأعمال',
    )
    profile_status = models.CharField(
        max_length=20,
        choices=ProfileStatus.choices,
        default=ProfileStatus.INCOMPLETE,
        db_index=True,
        verbose_name='حالة الملف',
    )
    completion_percentage = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='نسبة اكتمال الملف',
    )
    allow_email_contact = models.BooleanField(
        default=True,
        verbose_name='السماح بالتواصل عبر البريد',
    )
    allow_sms_contact = models.BooleanField(
        default=False,
        verbose_name='السماح بالتواصل عبر الرسائل',
    )
    last_profile_review_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='آخر مراجعة للملف',
    )

    class Meta:
        ordering = ['user__first_name', 'user__last_name']
        verbose_name = 'ملف خريج'
        verbose_name_plural = 'ملفات الخريجين'

    def __str__(self):
        return str(self.user)


class Skill(TimeStampedModel):
    name_ar = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='اسم المهارة بالعربية',
    )
    name_en = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='اسم المهارة بالإنجليزية',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='نشطة',
    )

    class Meta:
        ordering = ['name_ar']
        verbose_name = 'مهارة'
        verbose_name_plural = 'المهارات'

    def __str__(self):
        return self.name_ar


class GraduateSkill(TimeStampedModel):
    class ProficiencyLevel(models.TextChoices):
        BEGINNER = 'beginner', 'مبتدئ'
        INTERMEDIATE = 'intermediate', 'متوسط'
        ADVANCED = 'advanced', 'متقدم'
        EXPERT = 'expert', 'خبير'

    graduate = models.ForeignKey(
        GraduateProfile,
        on_delete=models.CASCADE,
        related_name='skills',
        verbose_name='الخريج',
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.PROTECT,
        related_name='graduates',
        verbose_name='المهارة',
    )
    proficiency_level = models.CharField(
        max_length=20,
        choices=ProficiencyLevel.choices,
        verbose_name='مستوى الإتقان',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['graduate', 'skill'],
                name='unique_skill_per_graduate',
            ),
        ]
        verbose_name = 'مهارة خريج'
        verbose_name_plural = 'مهارات الخريجين'

    def __str__(self):
        return f'{self.graduate} - {self.skill}'


class GraduateDocument(TimeStampedModel):
    class DocumentType(models.TextChoices):
        CV = 'cv', 'السيرة الذاتية'
        CERTIFICATE = 'certificate', 'شهادة'
        PORTFOLIO = 'portfolio', 'معرض أعمال'
        OTHER = 'other', 'أخرى'

    graduate = models.ForeignKey(
        GraduateProfile,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='الخريج',
    )
    document_type = models.CharField(
        max_length=20,
        choices=DocumentType.choices,
        verbose_name='نوع الملف',
    )
    title = models.CharField(
        max_length=200,
        verbose_name='عنوان الملف',
    )
    file = models.FileField(
        upload_to=graduate_document_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'doc', 'docx'],
            ),
        ],
        verbose_name='الملف',
    )
    is_visible_to_employers = models.BooleanField(
        default=False,
        verbose_name='ظاهر لجهات التوظيف',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'مستند خريج'
        verbose_name_plural = 'مستندات الخريجين'

    def __str__(self):
        return self.title