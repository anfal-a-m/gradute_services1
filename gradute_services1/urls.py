"""
URL configuration for the gradute_services1 project.

يربط هذا الملف المسارات الرئيسية بتطبيقات بوابة خدمات الخريجين.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


# تخصيص عناوين لوحة إدارة Django
admin.site.site_header = 'إدارة بوابة خدمات الخريجين'
admin.site.site_title = 'بوابة خدمات الخريجين'
admin.site.index_title = 'لوحة التحكم الرئيسية'


urlpatterns = [
    # لوحة إدارة Django
    path('admin/', admin.site.urls),

    # الصفحة الرئيسية والصفحات العامة
    path('', include('core.urls')),

    # المستخدمون وتسجيل الدخول والصلاحيات
    path('accounts/', include('accounts.urls')),

    # ملفات الخريجين
    path('graduates/', include('graduates.urls')),

    # بيانات التوظيف والمسار المهني
    path('employment/', include('employment.urls')),

    # جهات التوظيف
    path('employers/', include('employers.urls')),

    # الاستبانات والقياس
    path('surveys/', include('surveys.urls')),

    # البرامج والدورات التطويرية
    path('programs/', include('programs.urls')),

    # الإعلانات والتنبيهات والتواصل
    path('communications/', include('communications.urls')),

    # التقارير ومؤشرات الأداء
    path('reports/', include('reports.urls')),

    # البيانات والتكاملات الأكاديمية
    path('academic-data/', include('academic_data.urls')),

    # سجلات العمليات والتدقيق
    path('audit/', include('audit.urls')),
]


# عرض ملفات الميديا أثناء التطوير المحلي فقط
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )