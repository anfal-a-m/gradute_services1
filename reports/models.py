from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


class SavedReport(TimeStampedModel):
    """
    إعدادات التقارير المحفوظة.
    """

    class ReportType(models.TextChoices):
        GRADUATE_PROFILE = (
            'graduate_profile',
            'بيانات الخريجين',
        )
        EMPLOYMENT = (
            'employment',
            'مؤشرات التوظيف',
        )
        EMPLOYER_FEEDBACK = (
            'employer_feedback',
            'تقييم جهات التوظيف',
        )
        SURVEYS = (
            'surveys',
            'نتائج الاستبانات',
        )
        PROGRAMS = (
            'programs',
            'البرامج التطويرية',
        )
        CUSTOM = (
            'custom',
            'تقرير مخصص',
        )

    name = models.CharField(
        max_length=200,
        verbose_name='اسم التقرير',
    )

    report_type = models.CharField(
        max_length=30,
        choices=ReportType.choices,
        db_index=True,
        verbose_name='نوع التقرير',
    )

    filters = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='مرشحات التقرير',
    )

    selected_columns = models.JSONField(
        default=list,
        blank=True,
        verbose_name='الأعمدة المختارة',
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_reports',
        verbose_name='أنشأه',
    )

    shared_with = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='shared_reports',
        verbose_name='مشارك مع',
    )

    is_public_to_staff = models.BooleanField(
        default=False,
        verbose_name='متاح لموظفي البوابة',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'تقرير محفوظ'
        verbose_name_plural = 'التقارير المحفوظة'

    def __str__(self):
        return self.name


class ReportExport(TimeStampedModel):
    """
    ملفات التقارير التي تم تصديرها.
    """

    class ExportFormat(models.TextChoices):
        XLSX = 'xlsx', 'Excel'
        CSV = 'csv', 'CSV'
        PDF = 'pdf', 'PDF'

    class Status(models.TextChoices):
        PENDING = 'pending', 'بانتظار المعالجة'
        PROCESSING = 'processing', 'قيد المعالجة'
        COMPLETED = 'completed', 'مكتمل'
        FAILED = 'failed', 'فشل'

    report = models.ForeignKey(
        SavedReport,
        on_delete=models.CASCADE,
        related_name='exports',
        verbose_name='التقرير',
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='report_exports',
        verbose_name='طلبه',
    )

    export_format = models.CharField(
        max_length=10,
        choices=ExportFormat.choices,
        verbose_name='صيغة التصدير',
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name='حالة التصدير',
    )

    file = models.FileField(
        upload_to='report_exports/%Y/%m/',
        blank=True,
        verbose_name='ملف التقرير',
    )

    error_message = models.TextField(
        blank=True,
        verbose_name='رسالة الخطأ',
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='انتهاء صلاحية الملف',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'تصدير تقرير'
        verbose_name_plural = 'عمليات تصدير التقارير'

    def __str__(self):
        return f'{self.report} - {self.get_export_format_display()}'


class MetricSnapshot(TimeStampedModel):
    """
    نسخة محفوظة من قيمة مؤشر في وقت محدد.
    """

    metric_code = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name='رمز المؤشر',
    )

    metric_name = models.CharField(
        max_length=200,
        verbose_name='اسم المؤشر',
    )

    scope = models.CharField(
        max_length=100,
        default='university',
        verbose_name='نطاق المؤشر',
    )

    dimensions = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='أبعاد المؤشر',
    )

    value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='قيمة المؤشر',
    )

    calculated_at = models.DateTimeField(
        verbose_name='وقت احتساب المؤشر',
    )

    class Meta:
        ordering = ['-calculated_at']

        indexes = [
            models.Index(
                fields=['metric_code', 'calculated_at'],
                name='metric_code_date_idx',
            ),
        ]

        verbose_name = 'لقطة مؤشر'
        verbose_name_plural = 'لقطات المؤشرات'

    def __str__(self):
        return f'{self.metric_name}: {self.value}'