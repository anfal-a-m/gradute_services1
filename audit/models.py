from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from core.models import TimeStampedModel


class AuditLog(TimeStampedModel):
    class Action(models.TextChoices):
        CREATE = 'create', 'إنشاء'
        UPDATE = 'update', 'تعديل'
        DELETE = 'delete', 'حذف'
        VIEW = 'view', 'عرض'
        LOGIN = 'login', 'تسجيل دخول'
        LOGOUT = 'logout', 'تسجيل خروج'
        EXPORT = 'export', 'تصدير'
        SEND = 'send', 'إرسال'
        APPROVE = 'approve', 'اعتماد'
        REJECT = 'reject', 'رفض'

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name='منفذ العملية',
    )
    action = models.CharField(
        max_length=20,
        choices=Action.choices,
        db_index=True,
        verbose_name='العملية',
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='نوع العنصر',
    )
    object_id = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name='معرف العنصر',
    )
    target = GenericForeignKey(
        'content_type',
        'object_id',
    )
    object_representation = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='وصف العنصر',
    )
    changes = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='التغييرات',
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='بيانات إضافية',
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='عنوان IP',
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name='بيانات المتصفح',
    )
    request_path = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='مسار الطلب',
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(
                fields=['content_type', 'object_id'],
                name='audit_target_idx',
            ),
            models.Index(
                fields=['actor', 'created_at'],
                name='audit_actor_date_idx',
            ),
        ]
        verbose_name = 'سجل تدقيق'
        verbose_name_plural = 'سجلات التدقيق'

    def __str__(self):
        actor = self.actor or 'مستخدم غير معروف'
        return f'{actor} - {self.get_action_display()}'


class DataAccessLog(TimeStampedModel):
    class AccessType(models.TextChoices):
        VIEW_PERSONAL_DATA = 'view_personal', 'عرض بيانات شخصية'
        EXPORT_DATA = 'export', 'تصدير بيانات'
        DOWNLOAD_DOCUMENT = 'download', 'تنزيل مستند'
        PRINT_REPORT = 'print', 'طباعة تقرير'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='data_access_logs',
        verbose_name='المستخدم',
    )
    access_type = models.CharField(
        max_length=30,
        choices=AccessType.choices,
        db_index=True,
        verbose_name='نوع الوصول',
    )
    resource_name = models.CharField(
        max_length=250,
        verbose_name='المورد',
    )
    purpose = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='غرض الوصول',
    )
    records_count = models.PositiveIntegerField(
        default=0,
        verbose_name='عدد السجلات',
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='عنوان IP',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'سجل وصول للبيانات'
        verbose_name_plural = 'سجلات الوصول للبيانات'

    def __str__(self):
        return f'{self.user} - {self.get_access_type_display()}'