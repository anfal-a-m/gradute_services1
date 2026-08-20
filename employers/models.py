from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

from core.models import TimeStampedModel


phone_validator = RegexValidator(
    regex=r'^\+?[0-9]{8,15}$',
    message='أدخل رقم هاتف صحيحًا، ويمكن أن يبدأ بعلامة +.',
)


class Employer(TimeStampedModel):
    """
    بيانات جهة التوظيف.
    """

    class SectorType(models.TextChoices):
        GOVERNMENT = 'government', 'حكومي'
        PRIVATE = 'private', 'خاص'
        NON_PROFIT = 'non_profit', 'غير ربحي'
        INTERNATIONAL = 'international', 'دولي'
        OTHER = 'other', 'أخرى'

    name_ar = models.CharField(
        max_length=250,
        verbose_name='اسم الجهة بالعربية',
    )

    name_en = models.CharField(
        max_length=250,
        blank=True,
        verbose_name='اسم الجهة بالإنجليزية',
    )

    sector_type = models.CharField(
        max_length=20,
        choices=SectorType.choices,
        db_index=True,
        verbose_name='نوع القطاع',
    )

    industry = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='مجال النشاط',
    )

    registration_number = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        verbose_name='رقم السجل أو التعريف',
    )

    website = models.URLField(
        blank=True,
        verbose_name='الموقع الإلكتروني',
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

    is_verified = models.BooleanField(
        default=False,
        verbose_name='جهة موثقة',
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='نشطة',
    )

    class Meta:
        ordering = ['name_ar']
        verbose_name = 'جهة توظيف'
        verbose_name_plural = 'جهات التوظيف'

    def __str__(self):
        return self.name_ar


class EmployerContact(TimeStampedModel):
    """
    مسؤول التواصل لدى جهة التوظيف.
    يجب أن يوجد هذا النموذج داخل employers فقط.
    """

    employer = models.ForeignKey(
        Employer,
        on_delete=models.CASCADE,
        related_name='contacts',
        verbose_name='جهة التوظيف',
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employer_contact',
        verbose_name='حساب المستخدم',
    )

    full_name = models.CharField(
        max_length=200,
        verbose_name='الاسم',
    )

    job_title = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='المسمى الوظيفي',
    )

    email = models.EmailField(
        verbose_name='البريد الإلكتروني',
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
        validators=[phone_validator],
        verbose_name='رقم التواصل',
    )

    is_primary = models.BooleanField(
        default=False,
        verbose_name='جهة الاتصال الرئيسية',
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='نشط',
    )

    class Meta:
        ordering = ['employer', 'full_name']

        constraints = [
            models.UniqueConstraint(
                fields=['employer', 'email'],
                name='unique_contact_email_per_employer',
            ),
        ]

        verbose_name = 'مسؤول جهة توظيف'
        verbose_name_plural = 'مسؤولو جهات التوظيف'

    def __str__(self):
        return f'{self.full_name} - {self.employer.name_ar}'


class EmployerPartnership(TimeStampedModel):
    """
    الشراكات والتعاون بين الجامعة وجهات التوظيف.
    """

    class PartnershipType(models.TextChoices):
        EMPLOYMENT = 'employment', 'توظيف'
        TRAINING = 'training', 'تدريب'
        SURVEYS = 'surveys', 'استبانات وقياس'
        GENERAL = 'general', 'تعاون عام'

    class Status(models.TextChoices):
        PROPOSED = 'proposed', 'مقترحة'
        ACTIVE = 'active', 'نشطة'
        EXPIRED = 'expired', 'منتهية'
        SUSPENDED = 'suspended', 'موقوفة'

    employer = models.ForeignKey(
        Employer,
        on_delete=models.PROTECT,
        related_name='partnerships',
        verbose_name='جهة التوظيف',
    )

    partnership_type = models.CharField(
        max_length=20,
        choices=PartnershipType.choices,
        verbose_name='نوع الشراكة',
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PROPOSED,
        db_index=True,
        verbose_name='حالة الشراكة',
    )

    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='تاريخ البداية',
    )

    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='تاريخ النهاية',
    )

    notes = models.TextField(
        blank=True,
        verbose_name='ملاحظات',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'شراكة مع جهة توظيف'
        verbose_name_plural = 'شراكات جهات التوظيف'

    def clean(self):
        if (
            self.start_date
            and self.end_date
            and self.end_date < self.start_date
        ):
            raise ValidationError({
                'end_date': 'تاريخ النهاية لا يمكن أن يسبق تاريخ البداية.',
            })

    def __str__(self):
        return (
            f'{self.employer.name_ar} - '
            f'{self.get_partnership_type_display()}'
        )