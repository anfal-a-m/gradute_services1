from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from core.models import TimeStampedModel


phone_validator = RegexValidator(
    regex=r'^\+?[0-9]{8,15}$',
    message='أدخل رقم هاتف صحيحًا، ويمكن أن يبدأ بعلامة +.',
)


class User(AbstractUser, TimeStampedModel):
    class Role(models.TextChoices):
        GRADUATE = 'graduate', 'خريج'
        EMPLOYER = 'employer', 'ممثل جهة توظيف'
        STAFF = 'staff', 'موظف العمادة'
        COLLEGE_REPRESENTATIVE = 'college_rep', 'ممثل كلية'
        ANALYST = 'analyst', 'محلل بيانات'
        SYSTEM_ADMIN = 'system_admin', 'مدير النظام'

    class PreferredLanguage(models.TextChoices):
        ARABIC = 'ar', 'العربية'
        ENGLISH = 'en', 'الإنجليزية'

    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.GRADUATE,
        db_index=True,
        verbose_name='الدور',
    )
    university_id = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        verbose_name='الرقم الجامعي أو الوظيفي',
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        validators=[phone_validator],
        verbose_name='رقم الجوال',
    )
    preferred_language = models.CharField(
        max_length=2,
        choices=PreferredLanguage.choices,
        default=PreferredLanguage.ARABIC,
        verbose_name='اللغة المفضلة',
    )
    email_verified = models.BooleanField(
        default=False,
        verbose_name='البريد موثق',
    )
    must_change_password = models.BooleanField(
        default=False,
        verbose_name='يجب تغيير كلمة المرور',
    )
    represented_college = models.ForeignKey(
        'academic_data.College',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='representatives',
        verbose_name='الكلية الممثلة',
    )

    class Meta:
        ordering = ['first_name', 'last_name', 'username']
        verbose_name = 'مستخدم'
        verbose_name_plural = 'المستخدمون'

    def __str__(self):
        full_name = self.get_full_name().strip()
        return full_name or self.username


class UserConsent(TimeStampedModel):
    class ConsentType(models.TextChoices):
        PRIVACY = 'privacy', 'سياسة الخصوصية'
        TERMS = 'terms', 'شروط الاستخدام'
        COMMUNICATIONS = 'communications', 'استقبال الرسائل'
        RESEARCH = 'research', 'استخدام البيانات في الدراسات'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='consents',
        verbose_name='المستخدم',
    )
    consent_type = models.CharField(
        max_length=30,
        choices=ConsentType.choices,
        verbose_name='نوع الموافقة',
    )
    document_version = models.CharField(
        max_length=20,
        verbose_name='إصدار الوثيقة',
    )
    is_granted = models.BooleanField(
        default=True,
        verbose_name='تمت الموافقة',
    )
    granted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الموافقة',
    )
    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاريخ سحب الموافقة',
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='عنوان IP',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'consent_type', 'document_version'],
                name='unique_user_consent_version',
            ),
        ]
        verbose_name = 'موافقة مستخدم'
        verbose_name_plural = 'موافقات المستخدمين'

    def __str__(self):
        return f'{self.user} - {self.get_consent_type_display()}'
