from django.db import models


class TimeStampedModel(models.Model):
    """
    نموذج أساسي مجرد لإضافة تاريخ الإنشاء والتحديث
    إلى بقية نماذج المشروع.
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإنشاء',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاريخ آخر تحديث',
    )

    class Meta:
        abstract = True


class SiteSetting(TimeStampedModel):
    site_name = models.CharField(
        max_length=150,
        default='بوابة خدمات الخريجين',
        verbose_name='اسم البوابة',
    )
    university_name = models.CharField(
        max_length=200,
        verbose_name='اسم الجامعة',
    )
    support_email = models.EmailField(
        blank=True,
        verbose_name='بريد الدعم',
    )
    support_phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name='هاتف الدعم',
    )
    privacy_policy_url = models.URLField(
        blank=True,
        verbose_name='رابط سياسة الخصوصية',
    )
    is_maintenance_mode = models.BooleanField(
        default=False,
        verbose_name='وضع الصيانة',
    )

    class Meta:
        verbose_name = 'إعداد البوابة'
        verbose_name_plural = 'إعدادات البوابة'

    def __str__(self):
        return self.site_name


class StaticPage(TimeStampedModel):
    title = models.CharField(
        max_length=200,
        verbose_name='العنوان',
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='الرابط المختصر',
    )
    content = models.TextField(
        verbose_name='المحتوى',
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name='منشورة',
    )

    class Meta:
        ordering = ['title']
        verbose_name = 'صفحة ثابتة'
        verbose_name_plural = 'الصفحات الثابتة'

    def __str__(self):
        return self.title


class FAQ(TimeStampedModel):
    question = models.CharField(
        max_length=300,
        verbose_name='السؤال',
    )
    answer = models.TextField(
        verbose_name='الإجابة',
    )
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name='ترتيب العرض',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='نشط',
    )

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = 'سؤال شائع'
        verbose_name_plural = 'الأسئلة الشائعة'

    def __str__(self):
        return self.question