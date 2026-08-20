from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from core.models import TimeStampedModel


class GraduateCareerStatus(TimeStampedModel):
    """
    الحالة المهنية الحالية للخريج.
    """

    class Status(models.TextChoices):
        EMPLOYED = 'employed', 'موظف'
        SELF_EMPLOYED = 'self_employed', 'عمل حر أو صاحب عمل'
        JOB_SEEKER = 'job_seeker', 'باحث عن عمل'
        STUDYING = 'studying', 'يواصل الدراسة'
        NOT_SEEKING = 'not_seeking', 'لا يبحث عن عمل'
        UNKNOWN = 'unknown', 'غير محدد'

    graduate = models.OneToOneField(
        'graduates.GraduateProfile',
        on_delete=models.CASCADE,
        related_name='career_status',
        verbose_name='الخريج',
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UNKNOWN,
        db_index=True,
        verbose_name='الحالة المهنية',
    )

    available_for_opportunities = models.BooleanField(
        default=False,
        verbose_name='متاح للفرص الوظيفية',
    )

    status_since = models.DateField(
        null=True,
        blank=True,
        verbose_name='الحالة منذ',
    )

    notes = models.TextField(
        blank=True,
        verbose_name='ملاحظات',
    )

    class Meta:
        verbose_name = 'حالة مهنية'
        verbose_name_plural = 'الحالات المهنية'

    def __str__(self):
        return f'{self.graduate} - {self.get_status_display()}'


class EmploymentRecord(TimeStampedModel):
    """
    الوظائف الحالية والسابقة للخريج.
    """

    class EmploymentType(models.TextChoices):
        FULL_TIME = 'full_time', 'دوام كامل'
        PART_TIME = 'part_time', 'دوام جزئي'
        CONTRACT = 'contract', 'عقد'
        INTERNSHIP = 'internship', 'تدريب'
        FREELANCE = 'freelance', 'عمل حر'
        BUSINESS_OWNER = 'business_owner', 'صاحب عمل'

    graduate = models.ForeignKey(
        'graduates.GraduateProfile',
        on_delete=models.CASCADE,
        related_name='employment_records',
        verbose_name='الخريج',
    )

    employer = models.ForeignKey(
        'employers.Employer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graduate_employment_records',
        verbose_name='جهة التوظيف المسجلة',
    )

    employer_name = models.CharField(
        max_length=250,
        blank=True,
        verbose_name='اسم جهة العمل',
    )

    job_title = models.CharField(
        max_length=200,
        verbose_name='المسمى الوظيفي',
    )

    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        verbose_name='نوع العمل',
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

    start_date = models.DateField(
        verbose_name='تاريخ بداية العمل',
    )

    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='تاريخ نهاية العمل',
    )

    is_current = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name='عمل حالي',
    )

    is_primary = models.BooleanField(
        default=True,
        verbose_name='العمل الأساسي',
    )

    related_to_specialization = models.BooleanField(
        null=True,
        blank=True,
        verbose_name='مرتبط بالتخصص',
    )

    specialization_relevance_percentage = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name='نسبة ارتباط العمل بالتخصص',
    )

    salary_range = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='نطاق الراتب',
    )

    class Meta:
        ordering = ['-is_current', '-start_date']

        constraints = [
            models.UniqueConstraint(
                fields=['graduate'],
                condition=Q(
                    is_current=True,
                    is_primary=True,
                ),
                name='unique_primary_current_job',
            ),
        ]

        verbose_name = 'سجل وظيفي'
        verbose_name_plural = 'السجلات الوظيفية'

    def clean(self):
        errors = {}

        if not self.employer and not self.employer_name.strip():
            errors['employer_name'] = 'يجب تحديد اسم جهة العمل.'

        if self.end_date and self.end_date < self.start_date:
            errors['end_date'] = (
                'تاريخ نهاية العمل لا يمكن أن يسبق تاريخ البداية.'
            )

        if self.is_current and self.end_date:
            errors['end_date'] = (
                'العمل الحالي يجب ألا يحتوي على تاريخ نهاية.'
            )

        percentage = self.specialization_relevance_percentage

        if percentage is not None and percentage > 100:
            errors['specialization_relevance_percentage'] = (
                'النسبة يجب ألا تتجاوز 100.'
            )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        if self.employer:
            employer_name = self.employer.name_ar
        else:
            employer_name = self.employer_name

        return (
            f'{self.graduate} - '
            f'{self.job_title} - '
            f'{employer_name}'
        )


class JobPreference(TimeStampedModel):
    """
    تفضيلات الخريج الباحث عن وظيفة.
    """

    graduate = models.OneToOneField(
        'graduates.GraduateProfile',
        on_delete=models.CASCADE,
        related_name='job_preference',
        verbose_name='الخريج',
    )

    desired_job_titles = models.TextField(
        blank=True,
        verbose_name='المسميات الوظيفية المرغوبة',
    )

    preferred_cities = models.TextField(
        blank=True,
        verbose_name='المدن المفضلة',
    )

    preferred_sectors = models.TextField(
        blank=True,
        verbose_name='القطاعات المفضلة',
    )

    accepts_remote_work = models.BooleanField(
        default=True,
        verbose_name='يقبل العمل عن بعد',
    )

    accepts_relocation = models.BooleanField(
        default=False,
        verbose_name='يقبل الانتقال إلى مدينة أخرى',
    )

    expected_salary_range = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='نطاق الراتب المتوقع',
    )

    class Meta:
        verbose_name = 'تفضيلات وظيفية'
        verbose_name_plural = 'التفضيلات الوظيفية'

    def __str__(self):
        return f'التفضيلات الوظيفية: {self.graduate}'


class FurtherStudyRecord(TimeStampedModel):
    """
    الدراسات التي التحق بها الخريج بعد تخرجه.
    """

    class StudyStatus(models.TextChoices):
        CURRENT = 'current', 'مستمر'
        COMPLETED = 'completed', 'مكتمل'
        SUSPENDED = 'suspended', 'متوقف'

    graduate = models.ForeignKey(
        'graduates.GraduateProfile',
        on_delete=models.CASCADE,
        related_name='further_studies',
        verbose_name='الخريج',
    )

    institution_name = models.CharField(
        max_length=250,
        verbose_name='اسم المؤسسة التعليمية',
    )

    program_name = models.CharField(
        max_length=250,
        verbose_name='اسم البرنامج',
    )

    degree_level = models.CharField(
        max_length=100,
        verbose_name='الدرجة العلمية',
    )

    country = models.CharField(
        max_length=100,
        verbose_name='الدولة',
    )

    start_date = models.DateField(
        verbose_name='تاريخ البداية',
    )

    expected_or_actual_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='تاريخ النهاية المتوقع أو الفعلي',
    )

    status = models.CharField(
        max_length=20,
        choices=StudyStatus.choices,
        default=StudyStatus.CURRENT,
        db_index=True,
        verbose_name='حالة الدراسة',
    )

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'دراسة لاحقة'
        verbose_name_plural = 'الدراسات اللاحقة'

    def clean(self):
        if (
            self.expected_or_actual_end_date
            and self.expected_or_actual_end_date < self.start_date
        ):
            raise ValidationError({
                'expected_or_actual_end_date': (
                    'تاريخ النهاية لا يمكن أن يسبق تاريخ البداية.'
                ),
            })

    def __str__(self):
        return f'{self.graduate} - {self.program_name}'