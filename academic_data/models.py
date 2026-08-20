from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.models import TimeStampedModel


class College(TimeStampedModel):
    code = models.CharField(
        max_length=30,
        unique=True,
        verbose_name='رمز الكلية',
    )
    name_ar = models.CharField(
        max_length=200,
        verbose_name='اسم الكلية بالعربية',
    )
    name_en = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='اسم الكلية بالإنجليزية',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='نشطة',
    )

    class Meta:
        ordering = ['name_ar']
        verbose_name = 'كلية'
        verbose_name_plural = 'الكليات'

    def __str__(self):
        return self.name_ar


class Department(TimeStampedModel):
    college = models.ForeignKey(
        College,
        on_delete=models.PROTECT,
        related_name='departments',
        verbose_name='الكلية',
    )
    code = models.CharField(
        max_length=30,
        verbose_name='رمز القسم',
    )
    name_ar = models.CharField(
        max_length=200,
        verbose_name='اسم القسم بالعربية',
    )
    name_en = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='اسم القسم بالإنجليزية',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='نشط',
    )

    class Meta:
        ordering = ['college', 'name_ar']
        constraints = [
            models.UniqueConstraint(
                fields=['college', 'code'],
                name='unique_department_code_per_college',
            ),
        ]
        verbose_name = 'قسم أكاديمي'
        verbose_name_plural = 'الأقسام الأكاديمية'

    def __str__(self):
        return f'{self.name_ar} - {self.college.name_ar}'


class AcademicProgram(TimeStampedModel):
    class DegreeLevel(models.TextChoices):
        DIPLOMA = 'diploma', 'دبلوم'
        BACHELOR = 'bachelor', 'بكالوريوس'
        MASTER = 'master', 'ماجستير'
        DOCTORATE = 'doctorate', 'دكتوراه'

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='academic_programs',
        verbose_name='القسم',
    )
    code = models.CharField(
        max_length=30,
        unique=True,
        verbose_name='رمز البرنامج',
    )
    name_ar = models.CharField(
        max_length=200,
        verbose_name='اسم البرنامج بالعربية',
    )
    name_en = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='اسم البرنامج بالإنجليزية',
    )
    degree_level = models.CharField(
        max_length=20,
        choices=DegreeLevel.choices,
        verbose_name='الدرجة العلمية',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='نشط',
    )

    class Meta:
        ordering = ['name_ar']
        verbose_name = 'برنامج أكاديمي'
        verbose_name_plural = 'البرامج الأكاديمية'

    def __str__(self):
        return self.name_ar


class GraduationCohort(TimeStampedModel):
    academic_year = models.CharField(
        max_length=20,
        verbose_name='العام الأكاديمي',
    )
    semester = models.CharField(
        max_length=30,
        verbose_name='الفصل الدراسي',
    )
    graduation_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='تاريخ التخرج',
    )

    class Meta:
        ordering = ['-academic_year', 'semester']
        constraints = [
            models.UniqueConstraint(
                fields=['academic_year', 'semester'],
                name='unique_graduation_cohort',
            ),
        ]
        verbose_name = 'دفعة تخرج'
        verbose_name_plural = 'دفعات التخرج'

    def __str__(self):
        return f'{self.academic_year} - {self.semester}'


class GraduateAcademicRecord(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='academic_record',
        verbose_name='حساب الخريج',
    )
    student_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='الرقم الجامعي',
    )
    full_name_ar = models.CharField(
        max_length=250,
        verbose_name='الاسم بالعربية',
    )
    full_name_en = models.CharField(
        max_length=250,
        blank=True,
        verbose_name='الاسم بالإنجليزية',
    )
    program = models.ForeignKey(
        AcademicProgram,
        on_delete=models.PROTECT,
        related_name='graduate_records',
        verbose_name='البرنامج الأكاديمي',
    )
    cohort = models.ForeignKey(
        GraduationCohort,
        on_delete=models.PROTECT,
        related_name='graduate_records',
        verbose_name='دفعة التخرج',
    )
    gpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5),
        ],
        verbose_name='المعدل التراكمي',
    )
    graduation_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='تاريخ التخرج',
    )
    source_system = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='النظام المصدر',
    )
    source_last_updated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='آخر تحديث من النظام المصدر',
    )
    is_verified = models.BooleanField(
        default=True,
        verbose_name='سجل موثق',
    )

    class Meta:
        ordering = ['-graduation_date', 'student_number']
        verbose_name = 'سجل أكاديمي لخريج'
        verbose_name_plural = 'السجلات الأكاديمية للخريجين'

    def __str__(self):
        return f'{self.full_name_ar} - {self.student_number}'