import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from academic_data.models import AcademicProgram
from core.models import TimeStampedModel
from graduates.models import GraduateProfile


class DevelopmentProgram(TimeStampedModel):
    class ProgramType(models.TextChoices):
        COURSE = 'course', 'دورة'
        WORKSHOP = 'workshop', 'ورشة عمل'
        CAREER_GUIDANCE = 'career_guidance', 'إرشاد مهني'
        CERTIFICATION = 'certification', 'شهادة مهنية'
        MENTORING = 'mentoring', 'إرشاد وتوجيه'
        EVENT = 'event', 'فعالية'

    class DeliveryMode(models.TextChoices):
        IN_PERSON = 'in_person', 'حضوري'
        ONLINE_LIVE = 'online_live', 'عن بعد مباشر'
        ONLINE_RECORDED = 'online_recorded', 'عن بعد مسجل'
        HYBRID = 'hybrid', 'مدمج'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'مسودة'
        OPEN = 'open', 'التسجيل متاح'
        CLOSED = 'closed', 'التسجيل مغلق'
        IN_PROGRESS = 'in_progress', 'قيد التنفيذ'
        COMPLETED = 'completed', 'مكتمل'
        CANCELLED = 'cancelled', 'ملغي'

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='رمز البرنامج',
    )
    title = models.CharField(
        max_length=250,
        verbose_name='عنوان البرنامج',
    )
    description = models.TextField(
        verbose_name='الوصف',
    )
    program_type = models.CharField(
        max_length=30,
        choices=ProgramType.choices,
        verbose_name='نوع البرنامج',
    )
    delivery_mode = models.CharField(
        max_length=30,
        choices=DeliveryMode.choices,
        verbose_name='طريقة التقديم',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name='الحالة',
    )
    capacity = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='السعة',
    )
    registration_starts_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='بداية التسجيل',
    )
    registration_ends_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='نهاية التسجيل',
    )
    starts_at = models.DateTimeField(
        verbose_name='بداية البرنامج',
    )
    ends_at = models.DateTimeField(
        verbose_name='نهاية البرنامج',
    )
    location = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='الموقع',
    )
    meeting_url = models.URLField(
        blank=True,
        verbose_name='رابط الحضور',
    )
    target_academic_programs = models.ManyToManyField(
        AcademicProgram,
        blank=True,
        related_name='development_programs',
        verbose_name='البرامج الأكاديمية المستهدفة',
    )
    eligibility_rules = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='شروط الأهلية',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_development_programs',
        verbose_name='أنشأه',
    )

    class Meta:
        ordering = ['-starts_at']
        verbose_name = 'برنامج تطويري'
        verbose_name_plural = 'البرامج التطويرية'

    def clean(self):
        errors = {}

        if self.ends_at <= self.starts_at:
            errors['ends_at'] = 'نهاية البرنامج يجب أن تلي بدايته.'

        if (
            self.registration_starts_at
            and self.registration_ends_at
            and self.registration_ends_at <= self.registration_starts_at
        ):
            errors['registration_ends_at'] = (
                'نهاية التسجيل يجب أن تلي بدايته.'
            )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return self.title


class ProgramSession(TimeStampedModel):
    program = models.ForeignKey(
        DevelopmentProgram,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name='البرنامج',
    )
    title = models.CharField(
        max_length=250,
        verbose_name='عنوان الجلسة',
    )
    trainer_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='اسم المدرب',
    )
    starts_at = models.DateTimeField(
        verbose_name='بداية الجلسة',
    )
    ends_at = models.DateTimeField(
        verbose_name='نهاية الجلسة',
    )
    location_or_url = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='الموقع أو الرابط',
    )

    class Meta:
        ordering = ['starts_at']
        verbose_name = 'جلسة برنامج'
        verbose_name_plural = 'جلسات البرامج'

    def clean(self):
        if self.ends_at <= self.starts_at:
            raise ValidationError({
                'ends_at': 'نهاية الجلسة يجب أن تلي بدايتها.'
            })

    def __str__(self):
        return f'{self.program} - {self.title}'


class ProgramRegistration(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'قيد المراجعة'
        CONFIRMED = 'confirmed', 'مؤكد'
        WAITLISTED = 'waitlisted', 'قائمة انتظار'
        REJECTED = 'rejected', 'مرفوض'
        CANCELLED = 'cancelled', 'ملغي'
        COMPLETED = 'completed', 'مكتمل'

    program = models.ForeignKey(
        DevelopmentProgram,
        on_delete=models.CASCADE,
        related_name='registrations',
        verbose_name='البرنامج',
    )
    graduate = models.ForeignKey(
        GraduateProfile,
        on_delete=models.CASCADE,
        related_name='program_registrations',
        verbose_name='الخريج',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name='حالة التسجيل',
    )
    registered_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ التسجيل',
    )
    cancellation_reason = models.TextField(
        blank=True,
        verbose_name='سبب الإلغاء',
    )
    completion_percentage = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='نسبة الإنجاز',
    )

    class Meta:
        ordering = ['-registered_at']
        constraints = [
            models.UniqueConstraint(
                fields=['program', 'graduate'],
                name='unique_program_registration_per_graduate',
            ),
        ]
        verbose_name = 'تسجيل في برنامج'
        verbose_name_plural = 'التسجيلات في البرامج'

    def __str__(self):
        return f'{self.graduate} - {self.program}'


class SessionAttendance(TimeStampedModel):
    registration = models.ForeignKey(
        ProgramRegistration,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        verbose_name='التسجيل',
    )
    session = models.ForeignKey(
        ProgramSession,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        verbose_name='الجلسة',
    )
    attended = models.BooleanField(
        default=False,
        verbose_name='حضر',
    )
    checked_in_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='وقت تسجيل الحضور',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['registration', 'session'],
                name='unique_attendance_per_session',
            ),
        ]
        verbose_name = 'حضور جلسة'
        verbose_name_plural = 'سجلات الحضور'

    def __str__(self):
        return f'{self.registration} - {self.session}'


class ProgramCertificate(TimeStampedModel):
    registration = models.OneToOneField(
        ProgramRegistration,
        on_delete=models.CASCADE,
        related_name='certificate',
        verbose_name='التسجيل',
    )
    verification_code = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name='رمز التحقق',
    )
    issued_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإصدار',
    )
    certificate_file = models.FileField(
        upload_to='program_certificates/%Y/%m/',
        blank=True,
        verbose_name='ملف الشهادة',
    )

    class Meta:
        verbose_name = 'شهادة برنامج'
        verbose_name_plural = 'شهادات البرامج'

    def __str__(self):
        return f'شهادة {self.registration}'