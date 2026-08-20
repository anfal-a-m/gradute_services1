from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from core.models import TimeStampedModel


class Announcement(TimeStampedModel):
    """
    الإعلانات التي تظهر داخل بوابة خدمات الخريجين.
    """

    class Audience(models.TextChoices):
        ALL = 'all', 'الجميع'
        GRADUATES = 'graduates', 'الخريجون'
        EMPLOYERS = 'employers', 'جهات التوظيف'
        STAFF = 'staff', 'موظفو البوابة'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'مسودة'
        PUBLISHED = 'published', 'منشور'
        ARCHIVED = 'archived', 'مؤرشف'

    title = models.CharField(
        max_length=250,
        verbose_name='عنوان الإعلان',
    )

    content = models.TextField(
        verbose_name='محتوى الإعلان',
    )

    audience = models.CharField(
        max_length=20,
        choices=Audience.choices,
        default=Audience.ALL,
        db_index=True,
        verbose_name='الفئة المستهدفة',
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name='حالة الإعلان',
    )

    target_filters = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='معايير استهداف الإعلان',
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاريخ النشر',
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاريخ انتهاء الإعلان',
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_announcements',
        verbose_name='أنشأه',
    )

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = 'إعلان'
        verbose_name_plural = 'الإعلانات'

    def clean(self):
        if (
            self.published_at
            and self.expires_at
            and self.expires_at <= self.published_at
        ):
            raise ValidationError({
                'expires_at': (
                    'تاريخ انتهاء الإعلان يجب أن يلي تاريخ نشره.'
                ),
            })

    def __str__(self):
        return self.title


class MessageTemplate(TimeStampedModel):
    """
    قوالب البريد والرسائل النصية وإشعارات البوابة.
    """

    class Channel(models.TextChoices):
        EMAIL = 'email', 'البريد الإلكتروني'
        SMS = 'sms', 'رسالة نصية'
        IN_APP = 'in_app', 'إشعار داخل البوابة'

    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='اسم القالب',
    )

    channel = models.CharField(
        max_length=20,
        choices=Channel.choices,
        db_index=True,
        verbose_name='قناة الإرسال',
    )

    subject = models.CharField(
        max_length=250,
        blank=True,
        verbose_name='عنوان الرسالة',
    )

    body = models.TextField(
        verbose_name='محتوى الرسالة',
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='القالب نشط',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'قالب رسالة'
        verbose_name_plural = 'قوالب الرسائل'

    def __str__(self):
        return self.name


class CommunicationCampaign(TimeStampedModel):
    """
    حملة تواصل موجهة لمجموعة من الخريجين أو جهات التوظيف.
    """

    class Status(models.TextChoices):
        DRAFT = 'draft', 'مسودة'
        SCHEDULED = 'scheduled', 'مجدولة'
        PROCESSING = 'processing', 'قيد الإرسال'
        COMPLETED = 'completed', 'مكتملة'
        CANCELLED = 'cancelled', 'ملغية'
        FAILED = 'failed', 'فشلت'

    name = models.CharField(
        max_length=200,
        verbose_name='اسم الحملة',
    )

    template = models.ForeignKey(
        MessageTemplate,
        on_delete=models.PROTECT,
        related_name='campaigns',
        verbose_name='قالب الرسالة',
    )

    target_filters = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='معايير الاستهداف',
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name='حالة الحملة',
    )

    scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='موعد الإرسال المجدول',
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='وقت بدء الإرسال',
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='وقت اكتمال الإرسال',
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_campaigns',
        verbose_name='أنشأها',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'حملة تواصل'
        verbose_name_plural = 'حملات التواصل'

    def clean(self):
        errors = {}

        if (
            self.started_at
            and self.completed_at
            and self.completed_at < self.started_at
        ):
            errors['completed_at'] = (
                'وقت اكتمال الحملة لا يمكن أن يسبق وقت بدايتها.'
            )

        if self.status == self.Status.SCHEDULED and not self.scheduled_at:
            errors['scheduled_at'] = (
                'يجب تحديد موعد الإرسال للحملة المجدولة.'
            )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return self.name


class CampaignRecipient(TimeStampedModel):
    """
    مستلم واحد ضمن حملة التواصل.
    """

    class DeliveryStatus(models.TextChoices):
        PENDING = 'pending', 'بانتظار الإرسال'
        SENT = 'sent', 'مرسلة'
        DELIVERED = 'delivered', 'مستلمة'
        OPENED = 'opened', 'تم فتحها'
        FAILED = 'failed', 'فشل الإرسال'
        UNSUBSCRIBED = 'unsubscribed', 'ألغى الاشتراك'

    campaign = models.ForeignKey(
        CommunicationCampaign,
        on_delete=models.CASCADE,
        related_name='recipients',
        verbose_name='الحملة',
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='campaign_messages',
        verbose_name='المستخدم',
    )

    # علاقة نصية لمنع أخطاء الاستيراد بين التطبيقات
    employer_contact = models.ForeignKey(
        'employers.EmployerContact',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='campaign_messages',
        verbose_name='مسؤول جهة التوظيف',
    )

    recipient_address = models.CharField(
        max_length=250,
        verbose_name='بريد أو رقم المستلم',
    )

    delivery_status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.PENDING,
        db_index=True,
        verbose_name='حالة التسليم',
    )

    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='وقت الإرسال',
    )

    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='وقت الاستلام',
    )

    opened_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='وقت فتح الرسالة',
    )

    error_message = models.TextField(
        blank=True,
        verbose_name='رسالة الخطأ',
    )

    class Meta:
        ordering = ['-created_at']

        constraints = [
            models.UniqueConstraint(
                fields=['campaign', 'recipient_address'],
                name='unique_recipient_per_campaign',
            ),
        ]

        verbose_name = 'مستلم حملة'
        verbose_name_plural = 'مستلمو الحملات'

    def clean(self):
        if not any([
            self.user,
            self.employer_contact,
            self.recipient_address,
        ]):
            raise ValidationError(
                'يجب تحديد مستخدم أو مسؤول جهة توظيف أو عنوان مستلم.'
            )

    def __str__(self):
        return f'{self.campaign.name} - {self.recipient_address}'


class Notification(TimeStampedModel):
    """
    إشعار يظهر للمستخدم داخل البوابة.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='المستخدم',
    )

    title = models.CharField(
        max_length=250,
        verbose_name='عنوان الإشعار',
    )

    message = models.TextField(
        verbose_name='نص الإشعار',
    )

    action_url = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='رابط الإجراء',
    )

    is_read = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name='تمت القراءة',
    )

    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='وقت القراءة',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'إشعار'
        verbose_name_plural = 'الإشعارات'

    def __str__(self):
        return self.title